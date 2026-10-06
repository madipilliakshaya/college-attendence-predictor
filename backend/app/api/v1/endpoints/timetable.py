from typing import List, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import User, Timetable, Subject
from app.models.schemas import TimetableOut, TimetableCreate
from app.api.deps import get_current_user
from app.services.timetable_engine import TimetableEngine

router = APIRouter()

@router.get("/", response_model=List[TimetableOut])
def list_timetables(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.query(Timetable).filter(Timetable.user_id == current_user.id).order_by(Timetable.day_of_week, Timetable.start_time).all()
    subject_lookup = {s.id: s for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    
    out = []
    for e in entries:
        subj = subject_lookup.get(e.subject_id)
        out.append(TimetableOut(
            id=e.id,
            user_id=e.user_id,
            subject_id=e.subject_id,
            day_of_week=e.day_of_week,
            start_time=e.start_time,
            end_time=e.end_time,
            room=e.room,
            periods_count=e.periods_count,
            subject_name=subj.name if subj else "Unknown",
            subject_code=subj.code if subj else "N/A",
            subject_color=subj.color if subj else "#3B82F6",
            created_at=e.created_at
        ))
    return out

@router.get("/today")
def get_today_schedule(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    entries = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    subject_lookup = {s.id: s for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    
    classes_today = TimetableEngine.get_classes_for_date(entries, today)
    for c in classes_today:
        subj = subject_lookup.get(c["subject_id"])
        c["subject_name"] = subj.name if subj else "Unknown"
        c["subject_code"] = subj.code if subj else "N/A"
        c["subject_color"] = subj.color if subj else "#3B82F6"
        c["subject_type"] = subj.subject_type if subj else "lecture"
    
    return {
        "date": today.isoformat(),
        "day_of_week": today.weekday(),
        "classes": classes_today
    }

@router.post("/", response_model=TimetableOut)
def create_timetable_entry(
    entry_in: TimetableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subj = db.query(Subject).filter(Subject.id == entry_in.subject_id, Subject.user_id == current_user.id).first()
    if not subj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    entry = Timetable(
        user_id=current_user.id,
        **entry_in.model_dump()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return TimetableOut(
        id=entry.id,
        user_id=entry.user_id,
        subject_id=entry.subject_id,
        day_of_week=entry.day_of_week,
        start_time=entry.start_time,
        end_time=entry.end_time,
        room=entry.room,
        periods_count=entry.periods_count,
        subject_name=subj.name,
        subject_code=subj.code,
        subject_color=subj.color,
        created_at=entry.created_at
    )

@router.delete("/{timetable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timetable_entry(
    timetable_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(Timetable).filter(
        Timetable.id == timetable_id,
        Timetable.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timetable slot not found")
    db.delete(entry)
    db.commit()
    return None

@router.post("/ocr-import")
def simulate_timetable_ocr_import(
    raw_text: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Intelligent Timetable Parser / OCR processor.
    Parses pasted schedule text lines into timetable entries.
    Format example: "Mon 09:00-10:00 CS601 LH-201"
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    subjects = {s.code.upper(): s for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    
    created_count = 0
    errors = []

    for line in lines:
        parts = line.split()
        if len(parts) < 3:
            continue
        
        day_str = parts[0][:3].lower()
        if day_str not in day_map:
            errors.append(f"Invalid day in line: {line}")
            continue
        dow = day_map[day_str]

        time_part = parts[1]
        if "-" not in time_part:
            errors.append(f"Missing '-' in time slot: {line}")
            continue
        st, et = time_part.split("-")

        code_part = parts[2].upper()
        if code_part not in subjects:
            errors.append(f"Unknown subject code '{code_part}' in line: {line}")
            continue
        subj = subjects[code_part]
        room = parts[3] if len(parts) > 3 else "LH-1"

        entry = Timetable(
            user_id=current_user.id,
            subject_id=subj.id,
            day_of_week=dow,
            start_time=st,
            end_time=et,
            room=room,
            periods_count=1
        )
        db.add(entry)
        created_count += 1

    db.commit()
    return {
        "status": "success",
        "imported_entries": created_count,
        "warnings": errors
    }
