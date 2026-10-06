from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import User, Notification, Subject, AttendanceRecord, Timetable, StudentProfile
from app.models.schemas import NotificationOut
from app.api.deps import get_current_user
from app.services.attendance_engine import AttendanceEngine
from app.services.timetable_engine import TimetableEngine
from app.services.prediction_engine import PredictionEngine

router = APIRouter()

@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(50).all()

@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif

@router.post("/refresh-alerts", response_model=List[NotificationOut])
def refresh_alerts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Evaluates current attendance and schedule to generate fresh notifications.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    timetables = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()

    today = date.today()
    sem_end = profile.semester_end_date if profile else today

    created_notifs = []

    for s in subjects:
        s_records = [r for r in records if r.subject_id == s.id]
        conducted = sum(r.periods_count for r in s_records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in s_records if r.status == "present")
        pct = AttendanceEngine.calculate_percentage(attended, conducted)
        tgt = s.target_percentage

        if pct < tgt and conducted > 0:
            needed = AttendanceEngine.calculate_classes_needed(attended, conducted, tgt)
            msg = f"Your {s.name} ({s.code}) attendance is {pct:.1f}%, which is below target {tgt:.1f}%. Attend the next {needed} classes to recover."
            # Check if identical unread notification exists
            exists = db.query(Notification).filter(
                Notification.user_id == current_user.id,
                Notification.subject_id == s.id,
                Notification.alert_type == "shortage",
                Notification.is_read == False
            ).first()
            if not exists:
                n = Notification(
                    user_id=current_user.id,
                    subject_id=s.id,
                    title=f"Shortage Alert: {s.code}",
                    message=msg,
                    alert_type="shortage"
                )
                db.add(n)
                created_notifs.append(n)
        else:
            safe = AttendanceEngine.calculate_safe_bunks(attended, conducted, tgt)
            if safe == 0 and conducted > 0:
                msg = f"Zero safe bunks in {s.code}. Missing your next class will immediately result in an attendance shortage!"
                exists = db.query(Notification).filter(
                    Notification.user_id == current_user.id,
                    Notification.subject_id == s.id,
                    Notification.alert_type == "warning",
                    Notification.is_read == False
                ).first()
                if not exists:
                    n = Notification(
                        user_id=current_user.id,
                        subject_id=s.id,
                        title=f"Zero Bunk Warning: {s.code}",
                        message=msg,
                        alert_type="warning"
                    )
                    db.add(n)
                    created_notifs.append(n)

    db.commit()
    for n in created_notifs:
        db.refresh(n)

    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
