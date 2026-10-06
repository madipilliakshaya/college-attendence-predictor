from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import User, Subject, AttendanceRecord, Timetable, StudentProfile
from app.models.schemas import SubjectOut, SubjectCreate, SubjectUpdate, SubjectAttendanceStats
from app.api.deps import get_current_user
from app.services.attendance_engine import AttendanceEngine
from app.services.timetable_engine import TimetableEngine
from app.services.prediction_engine import PredictionEngine
from app.services.risk_engine import RiskEngine

router = APIRouter()

@router.get("/", response_model=List[SubjectOut])
def list_subjects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Subject).filter(Subject.user_id == current_user.id).order_by(Subject.code).all()

@router.get("/stats", response_model=List[SubjectAttendanceStats])
def get_subjects_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).order_by(Subject.code).all()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    timetables = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()

    today = date.today()
    sem_end = profile.semester_end_date if profile else today

    remaining_map = TimetableEngine.calculate_remaining_classes_by_subject(timetables, today, sem_end)

    results = []
    for s in subjects:
        s_records = [r for r in records if r.subject_id == s.id]
        
        conducted = sum(r.periods_count for r in s_records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in s_records if r.status == "present")
        absent = sum(r.periods_count for r in s_records if r.status == "absent")
        cancelled = sum(r.periods_count for r in s_records if r.status == "cancelled")

        pct = AttendanceEngine.calculate_percentage(attended, conducted)
        tgt = s.target_percentage
        safe_bunks = AttendanceEngine.calculate_safe_bunks(attended, conducted, tgt)
        classes_needed = AttendanceEngine.calculate_classes_needed(attended, conducted, tgt)
        remaining = remaining_map.get(s.id, 0)

        # Trend & forecast
        trend = AttendanceEngine.calculate_trend(s_records)
        forecast = PredictionEngine.forecast_attendance(
            attended=attended,
            conducted=conducted,
            remaining_classes=remaining,
            target_percentage=tgt,
            recent_percentage=trend["recent_percentage"]
        )

        s_timetables = [t for t in timetables if t.subject_id == s.id]
        shortage_date = PredictionEngine.calculate_projected_shortage_date(
            attended=attended,
            conducted=conducted,
            target_percentage=tgt,
            timetables_for_subject=s_timetables,
            from_date=today,
            semester_end_date=sem_end
        )

        risk_eval = RiskEngine.evaluate_risk(
            current_percentage=pct,
            target_percentage=tgt,
            safe_bunks=safe_bunks,
            classes_needed=classes_needed,
            remaining_classes=remaining,
            predicted_percentage=forecast["predicted_percentage"],
            trend_direction=trend["trend_direction"],
            consecutive_absences=trend["consecutive_absences"],
            projected_shortage_date=shortage_date
        )

        results.append(SubjectAttendanceStats(
            subject_id=s.id,
            subject_code=s.code,
            subject_name=s.name,
            subject_type=s.subject_type,
            credits=s.credits,
            color=s.color,
            target_percentage=tgt,
            classes_conducted=conducted,
            classes_attended=attended,
            classes_absent=absent,
            classes_cancelled=cancelled,
            current_percentage=pct,
            is_shortage=pct < tgt,
            safe_bunks=safe_bunks,
            classes_needed=classes_needed,
            remaining_classes_semester=remaining,
            predicted_final_percentage=forecast["predicted_percentage"],
            risk_level=risk_eval["risk_level"],
            projected_shortage_date=shortage_date
        ))

    return results

@router.post("/", response_model=SubjectOut)
def create_subject(
    subject_in: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Subject).filter(
        Subject.user_id == current_user.id,
        Subject.code == subject_in.code
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Subject with code {subject_in.code} already exists")

    subject = Subject(
        user_id=current_user.id,
        **subject_in.model_dump()
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: str,
    subject_in: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    db.delete(subject)
    db.commit()
    return None
