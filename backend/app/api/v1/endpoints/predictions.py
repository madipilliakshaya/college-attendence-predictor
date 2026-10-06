import os
import json
from typing import List, Dict, Any, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import User, Subject, AttendanceRecord, Timetable, StudentProfile
from app.models.schemas import RecoveryPlan, RecoveryPlanStep
from app.api.deps import get_current_user
from app.services.attendance_engine import AttendanceEngine
from app.services.timetable_engine import TimetableEngine
from app.services.prediction_engine import PredictionEngine
from app.services.risk_engine import RiskEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.ml_model import MLModelService

router = APIRouter()

@router.get("/forecast")
def get_attendance_forecast(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    timetables = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()

    today = date.today()
    sem_end = profile.semester_end_date if profile else today
    remaining_map = TimetableEngine.calculate_remaining_classes_by_subject(timetables, today, sem_end)

    subject_forecasts = []
    total_conducted = 0
    total_attended = 0
    total_remaining = 0

    for s in subjects:
        s_records = [r for r in records if r.subject_id == s.id]
        conducted = sum(r.periods_count for r in s_records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in s_records if r.status == "present")
        remaining = remaining_map.get(s.id, 0)
        
        total_conducted += conducted
        total_attended += attended
        total_remaining += remaining

        trend = AttendanceEngine.calculate_trend(s_records)
        curr_pct = AttendanceEngine.calculate_percentage(attended, conducted)
        
        # Run ML model if available
        ml_pred = MLModelService.predict_final_attendance(
            current_attendance_pct=curr_pct,
            classes_conducted=conducted,
            classes_attended=attended,
            classes_absent=conducted - attended,
            recent_attendance_pct=trend["recent_percentage"],
            trend_delta=trend["delta"],
            consecutive_absences=trend["consecutive_absences"],
            remaining_classes=remaining,
            subject_credits=s.credits,
            is_lab=1 if s.subject_type == "lab" else 0
        )

        forecast = PredictionEngine.forecast_attendance(
            attended=attended,
            conducted=conducted,
            remaining_classes=remaining,
            target_percentage=s.target_percentage,
            recent_percentage=trend["recent_percentage"],
            ml_prediction=ml_pred
        )

        s_timetables = [t for t in timetables if t.subject_id == s.id]
        shortage_date = PredictionEngine.calculate_projected_shortage_date(
            attended=attended,
            conducted=conducted,
            target_percentage=s.target_percentage,
            timetables_for_subject=s_timetables,
            from_date=today,
            semester_end_date=sem_end
        )

        safe_bunks = AttendanceEngine.calculate_safe_bunks(attended, conducted, s.target_percentage)
        classes_needed = AttendanceEngine.calculate_classes_needed(attended, conducted, s.target_percentage)

        risk = RiskEngine.evaluate_risk(
            current_percentage=curr_pct,
            target_percentage=s.target_percentage,
            safe_bunks=safe_bunks,
            classes_needed=classes_needed,
            remaining_classes=remaining,
            predicted_percentage=forecast["predicted_percentage"],
            trend_direction=trend["trend_direction"],
            consecutive_absences=trend["consecutive_absences"],
            projected_shortage_date=shortage_date
        )

        subject_forecasts.append({
            "subject_id": s.id,
            "subject_code": s.code,
            "subject_name": s.name,
            "current_percentage": curr_pct,
            "target_percentage": s.target_percentage,
            "classes_conducted": conducted,
            "classes_attended": attended,
            "remaining_classes": remaining,
            "predicted_percentage": forecast["predicted_percentage"],
            "confidence_score": forecast["confidence_score"],
            "confidence_interval_low": forecast["confidence_interval_low"],
            "confidence_interval_high": forecast["confidence_interval_high"],
            "max_possible_percentage": forecast["max_possible_percentage"],
            "min_possible_percentage": forecast["min_possible_percentage"],
            "prediction_method": forecast["method"],
            "risk_level": risk["risk_level"],
            "risk_score": risk["risk_score"],
            "contributing_factors": risk["factors"],
            "projected_shortage_date": shortage_date
        })

    # Overall forecast
    default_target = profile.default_attendance_target if profile else 75.0
    overall_trend = AttendanceEngine.calculate_trend(records)
    overall_forecast = PredictionEngine.forecast_attendance(
        attended=total_attended,
        conducted=total_conducted,
        remaining_classes=total_remaining,
        target_percentage=default_target,
        recent_percentage=overall_trend["recent_percentage"]
    )
    overall_curr_pct = AttendanceEngine.calculate_percentage(total_attended, total_conducted)
    overall_safe_bunks = AttendanceEngine.calculate_safe_bunks(total_attended, total_conducted, default_target)
    overall_needed = AttendanceEngine.calculate_classes_needed(total_attended, total_conducted, default_target)

    overall_risk = RiskEngine.evaluate_risk(
        current_percentage=overall_curr_pct,
        target_percentage=default_target,
        safe_bunks=overall_safe_bunks,
        classes_needed=overall_needed,
        remaining_classes=total_remaining,
        predicted_percentage=overall_forecast["predicted_percentage"],
        trend_direction=overall_trend["trend_direction"],
        consecutive_absences=overall_trend["consecutive_absences"]
    )

    return {
        "overall": {
            "current_percentage": overall_curr_pct,
            "target_percentage": default_target,
            "total_conducted": total_conducted,
            "total_attended": total_attended,
            "total_remaining": total_remaining,
            "predicted_percentage": overall_forecast["predicted_percentage"],
            "confidence_score": overall_forecast["confidence_score"],
            "confidence_interval_low": overall_forecast["confidence_interval_low"],
            "confidence_interval_high": overall_forecast["confidence_interval_high"],
            "max_possible_percentage": overall_forecast["max_possible_percentage"],
            "min_possible_percentage": overall_forecast["min_possible_percentage"],
            "prediction_method": overall_forecast["method"],
            "risk_level": overall_risk["risk_level"],
            "risk_score": overall_risk["risk_score"],
            "contributing_factors": overall_risk["factors"]
        },
        "subjects": subject_forecasts
    }

@router.get("/metrics")
def get_ml_metrics():
    """
    Returns authentic training and evaluation metrics from the trained ML models.
    """
    report_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "ml_evaluation_report.json")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            return json.load(f)
    return {
        "status": "pending_or_unavailable",
        "message": "Model evaluation report has not yet been generated."
    }

@router.get("/recovery/{subject_id}", response_model=RecoveryPlan)
def get_recovery_plan(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    timetables = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    today = date.today()
    sem_end = profile.semester_end_date if profile else today

    if subject_id == "overall":
        records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()
        conducted = sum(r.periods_count for r in records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in records if r.status == "present")
        target = profile.default_attendance_target if profile else 75.0
        
        remaining_map = TimetableEngine.calculate_remaining_classes_by_subject(timetables, today, sem_end)
        remaining = sum(remaining_map.values())
        
        plan = RecommendationEngine.generate_recovery_plan(
            subject_id=None,
            subject_name="Overall Semester Attendance",
            attended=attended,
            conducted=conducted,
            target_percentage=target,
            remaining_classes=remaining
        )
        return RecoveryPlan(**plan)
    
    subj = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == current_user.id).first()
    if not subj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    s_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.subject_id == subject_id
    ).all()
    conducted = sum(r.periods_count for r in s_records if r.status in ("present", "absent"))
    attended = sum(r.periods_count for r in s_records if r.status == "present")
    
    remaining_map = TimetableEngine.calculate_remaining_classes_by_subject(timetables, today, sem_end)
    remaining = remaining_map.get(subj.id, 0)

    plan = RecommendationEngine.generate_recovery_plan(
        subject_id=subj.id,
        subject_name=f"{subj.code} - {subj.name}",
        attended=attended,
        conducted=conducted,
        target_percentage=subj.target_percentage,
        remaining_classes=remaining
    )
    return RecoveryPlan(**plan)
