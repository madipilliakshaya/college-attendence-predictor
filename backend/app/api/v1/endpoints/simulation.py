from typing import List, Dict, Any, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import User, Subject, AttendanceRecord, Timetable, StudentProfile, PlannedAbsence
from app.models.schemas import (
    WhatIfRequest, WhatIfResult, AbsenceSimulationRequest, AbsenceSimulationResult,
    PlannedAbsenceCreate, PlannedAbsenceOut
)
from app.api.deps import get_current_user
from app.services.attendance_engine import AttendanceEngine
from app.services.simulation_engine import SimulationEngine

router = APIRouter()

@router.post("/what-if", response_model=WhatIfResult)
def run_what_if_scenario(
    req: WhatIfRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    default_target = profile.default_attendance_target if profile else 75.0

    if req.subject_id:
        subj = db.query(Subject).filter(Subject.id == req.subject_id, Subject.user_id == current_user.id).first()
        if not subj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == current_user.id,
            AttendanceRecord.subject_id == req.subject_id
        ).all()

        conducted = sum(r.periods_count for r in records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in records if r.status == "present")
        target = subj.target_percentage
        subj_name = f"{subj.code} - {subj.name}"
    else:
        records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()
        conducted = sum(r.periods_count for r in records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in records if r.status == "present")
        target = default_target
        subj_name = "Overall Semester Attendance"

    calc = AttendanceEngine.calculate_what_if(
        attended=attended,
        conducted=conducted,
        target=target,
        miss_classes=req.miss_classes,
        attend_classes=req.attend_classes
    )

    return WhatIfResult(
        subject_id=req.subject_id,
        subject_name=subj_name,
        current_percentage=calc["current_percentage"],
        simulated_percentage=calc["simulated_percentage"],
        percentage_change=calc["percentage_change"],
        target_percentage=calc["target_percentage"],
        is_target_met=calc["is_target_met"],
        new_safe_bunks=calc["new_safe_bunks"],
        new_classes_needed=calc["new_classes_needed"],
        new_risk_level=calc["new_risk_level"]
    )

@router.post("/absence-simulation", response_model=AbsenceSimulationResult)
def simulate_planned_absences(
    sim_in: AbsenceSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    timetables = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()

    # Build subjects map
    subjects_map = {}
    for s in subjects:
        s_records = [r for r in records if r.subject_id == s.id]
        conducted = sum(r.periods_count for r in s_records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in s_records if r.status == "present")
        subjects_map[s.id] = {
            "code": s.code,
            "name": s.name,
            "attended": attended,
            "conducted": conducted,
            "target": s.target_percentage
        }

    res = SimulationEngine.simulate_planned_dates(
        dates_to_miss=sim_in.dates,
        subjects_map=subjects_map,
        timetables=timetables,
        reason=sim_in.reason or "Planned Leave"
    )
    return AbsenceSimulationResult(**res)

@router.get("/planned-absences", response_model=List[PlannedAbsenceOut])
def list_planned_absences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(PlannedAbsence).filter(PlannedAbsence.user_id == current_user.id).order_by(PlannedAbsence.date).all()

@router.post("/planned-absences", response_model=PlannedAbsenceOut)
def create_planned_absence(
    pa_in: PlannedAbsenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pa = PlannedAbsence(
        user_id=current_user.id,
        **pa_in.model_dump()
    )
    db.add(pa)
    db.commit()
    db.refresh(pa)
    return pa

@router.delete("/planned-absences/{pa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planned_absence(
    pa_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pa = db.query(PlannedAbsence).filter(
        PlannedAbsence.id == pa_id,
        PlannedAbsence.user_id == current_user.id
    ).first()
    if not pa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planned absence not found")
    db.delete(pa)
    db.commit()
    return None
