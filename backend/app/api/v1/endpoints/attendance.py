from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.db_models import User, AttendanceRecord, Subject
from app.models.schemas import (
    AttendanceRecordOut, AttendanceRecordCreate, AttendanceRecordBulkCreate
)
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AttendanceRecordOut])
def list_attendance_records(
    subject_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id)
    if subject_id:
        query = query.filter(AttendanceRecord.subject_id == subject_id)
    if from_date:
        query = query.filter(AttendanceRecord.date >= from_date)
    if to_date:
        query = query.filter(AttendanceRecord.date <= to_date)
    if status:
        query = query.filter(AttendanceRecord.status == status)

    records = query.order_by(AttendanceRecord.date.desc(), AttendanceRecord.created_at.desc()).offset(offset).limit(limit).all()

    # Hydrate subject metadata
    subject_lookup = {s.id: s for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    out = []
    for r in records:
        subj = subject_lookup.get(r.subject_id)
        out.append(AttendanceRecordOut(
            id=r.id,
            user_id=r.user_id,
            subject_id=r.subject_id,
            subject_name=subj.name if subj else "Unknown",
            subject_code=subj.code if subj else "N/A",
            subject_color=subj.color if subj else "#3B82F6",
            date=r.date,
            status=r.status,
            periods_count=r.periods_count,
            reason_category=r.reason_category,
            notes=r.notes,
            created_at=r.created_at,
            updated_at=r.updated_at
        ))
    return out

@router.post("/", response_model=AttendanceRecordOut)
def create_attendance_record(
    record_in: AttendanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify subject exists
    subj = db.query(Subject).filter(Subject.id == record_in.subject_id, Subject.user_id == current_user.id).first()
    if not subj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    rec = AttendanceRecord(
        user_id=current_user.id,
        **record_in.model_dump()
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return AttendanceRecordOut(
        id=rec.id,
        user_id=rec.user_id,
        subject_id=rec.subject_id,
        subject_name=subj.name,
        subject_code=subj.code,
        subject_color=subj.color,
        date=rec.date,
        status=rec.status,
        periods_count=rec.periods_count,
        reason_category=rec.reason_category,
        notes=rec.notes,
        created_at=rec.created_at,
        updated_at=rec.updated_at
    )

@router.post("/bulk", response_model=List[AttendanceRecordOut])
def bulk_create_attendance_records(
    bulk_in: AttendanceRecordBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject_lookup = {s.id: s for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    created = []
    for item in bulk_in.records:
        if item.subject_id not in subject_lookup:
            continue
        rec = AttendanceRecord(
            user_id=current_user.id,
            subject_id=item.subject_id,
            date=bulk_in.date,
            status=item.status,
            periods_count=item.periods_count,
            reason_category=item.reason_category,
            notes=item.notes
        )
        db.add(rec)
        created.append(rec)
    
    db.commit()
    for rec in created:
        db.refresh(rec)

    return [
        AttendanceRecordOut(
            id=r.id,
            user_id=r.user_id,
            subject_id=r.subject_id,
            subject_name=subject_lookup[r.subject_id].name,
            subject_code=subject_lookup[r.subject_id].code,
            subject_color=subject_lookup[r.subject_id].color,
            date=r.date,
            status=r.status,
            periods_count=r.periods_count,
            reason_category=r.reason_category,
            notes=r.notes,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in created
    ]

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(AttendanceRecord).filter(
        AttendanceRecord.id == record_id,
        AttendanceRecord.user_id == current_user.id
    ).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    db.delete(rec)
    db.commit()
    return None

@router.get("/calendar")
def get_attendance_calendar(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns monthly attendance aggregation per calendar date.
    """
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        func.extract("year", AttendanceRecord.date) == year,
        func.extract("month", AttendanceRecord.date) == month
    ).all()

    subject_lookup = {s.id: s for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}

    calendar_map: Dict[str, Dict[str, Any]] = {}
    for r in records:
        d_str = r.date.isoformat()
        if d_str not in calendar_map:
            calendar_map[d_str] = {
                "date": d_str,
                "present_count": 0,
                "absent_count": 0,
                "cancelled_count": 0,
                "total_periods": 0,
                "sessions": []
            }
        
        subj = subject_lookup.get(r.subject_id)
        if r.status == "present":
            calendar_map[d_str]["present_count"] += r.periods_count
        elif r.status == "absent":
            calendar_map[d_str]["absent_count"] += r.periods_count
        elif r.status == "cancelled":
            calendar_map[d_str]["cancelled_count"] += r.periods_count
        calendar_map[d_str]["total_periods"] += r.periods_count

        calendar_map[d_str]["sessions"].append({
            "id": r.id,
            "subject_code": subj.code if subj else "N/A",
            "subject_name": subj.name if subj else "Unknown",
            "subject_color": subj.color if subj else "#3B82F6",
            "status": r.status,
            "periods": r.periods_count,
            "reason": r.reason_category,
            "notes": r.notes
        })

    return list(calendar_map.values())

@router.get("/reasons-summary")
def get_absence_reasons_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggregates absences by categorized reason.
    """
    absent_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.status == "absent"
    ).all()

    summary: Dict[str, int] = {
        "illness": 0,
        "college_event": 0,
        "personal": 0,
        "approved_leave": 0,
        "other": 0,
        "none": 0
    }

    for r in absent_records:
        cat = r.reason_category if r.reason_category in summary else "other"
        summary[cat] += r.periods_count

    return summary
