from typing import List, Dict, Any
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import User, Subject, AttendanceRecord, Timetable, StudentProfile, Notification
from app.models.schemas import DashboardResponse, StudentProfileOut, OverallAttendanceStats, SubjectAttendanceStats, NotificationOut
from app.api.deps import get_current_user
from app.services.attendance_engine import AttendanceEngine
from app.services.timetable_engine import TimetableEngine
from app.services.prediction_engine import PredictionEngine
from app.services.risk_engine import RiskEngine
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).order_by(Subject.code).all()
    timetables = db.query(Timetable).filter(Timetable.user_id == current_user.id).all()
    records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(10).all()

    today = date.today()
    sem_end = profile.semester_end_date
    default_target = profile.default_attendance_target

    remaining_map = TimetableEngine.calculate_remaining_classes_by_subject(timetables, today, sem_end)
    total_remaining = sum(remaining_map.values())

    subject_stats: List[SubjectAttendanceStats] = []
    total_conducted = 0
    total_attended = 0
    total_absent = 0
    total_weighted_att = 0.0
    total_weighted_cond = 0.0

    for s in subjects:
        s_records = [r for r in records if r.subject_id == s.id]
        conducted = sum(r.periods_count for r in s_records if r.status in ("present", "absent"))
        attended = sum(r.periods_count for r in s_records if r.status == "present")
        absent = sum(r.periods_count for r in s_records if r.status == "absent")
        cancelled = sum(r.periods_count for r in s_records if r.status == "cancelled")

        total_conducted += conducted
        total_attended += attended
        total_absent += absent
        
        # Credit / duration weighting
        weight = float(s.credits) * float(s.duration_hours)
        total_weighted_cond += (conducted * weight)
        total_weighted_att += (attended * weight)

        pct = AttendanceEngine.calculate_percentage(attended, conducted)
        tgt = s.target_percentage
        safe_bunks = AttendanceEngine.calculate_safe_bunks(attended, conducted, tgt)
        classes_needed = AttendanceEngine.calculate_classes_needed(attended, conducted, tgt)
        remaining = remaining_map.get(s.id, 0)

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

        risk = RiskEngine.evaluate_risk(
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

        subject_stats.append(SubjectAttendanceStats(
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
            risk_level=risk["risk_level"],
            projected_shortage_date=shortage_date
        ))

    # Sort subject_stats by risk priority (HIGH first, then MEDIUM, then LOW)
    priority_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    subject_stats.sort(key=lambda x: (priority_map.get(x.risk_level, 3), x.current_percentage))

    overall_pct = AttendanceEngine.calculate_percentage(total_attended, total_conducted)
    weighted_pct = AttendanceEngine.calculate_percentage(total_weighted_att, total_weighted_cond)
    overall_safe = AttendanceEngine.calculate_safe_bunks(total_attended, total_conducted, default_target)
    overall_needed = AttendanceEngine.calculate_classes_needed(total_attended, total_conducted, default_target)
    max_possible = AttendanceEngine.calculate_max_possible_attendance(total_attended, total_conducted, total_remaining)

    overall_trend = AttendanceEngine.calculate_trend(records)
    overall_forecast = PredictionEngine.forecast_attendance(
        attended=total_attended,
        conducted=total_conducted,
        remaining_classes=total_remaining,
        target_percentage=default_target,
        recent_percentage=overall_trend["recent_percentage"]
    )

    overall_risk = RiskEngine.evaluate_risk(
        current_percentage=overall_pct,
        target_percentage=default_target,
        safe_bunks=overall_safe,
        classes_needed=overall_needed,
        remaining_classes=total_remaining,
        predicted_percentage=overall_forecast["predicted_percentage"],
        trend_direction=overall_trend["trend_direction"],
        consecutive_absences=overall_trend["consecutive_absences"]
    )

    overall_stats = OverallAttendanceStats(
        total_conducted=total_conducted,
        total_attended=total_attended,
        total_absent=total_absent,
        current_percentage=overall_pct,
        target_percentage=default_target,
        weighted_percentage=weighted_pct,
        is_shortage=overall_pct < default_target,
        safe_bunks=overall_safe,
        classes_needed=overall_needed,
        total_remaining_classes=total_remaining,
        predicted_final_percentage=overall_forecast["predicted_percentage"],
        prediction_confidence=overall_forecast["confidence_score"],
        confidence_interval_low=overall_forecast["confidence_interval_low"],
        confidence_interval_high=overall_forecast["confidence_interval_high"],
        overall_risk_level=overall_risk["risk_level"],
        projected_shortage_date=None,
        recovery_possible=overall_needed <= total_remaining if total_remaining > 0 else True,
        max_possible_final_percentage=max_possible
    )

    # Classes for today
    classes_today = TimetableEngine.get_classes_for_date(timetables, today)
    subj_lookup = {s.id: s for s in subjects}
    for c in classes_today:
        s = subj_lookup.get(c["subject_id"])
        c["subject_name"] = s.name if s else "Unknown"
        c["subject_code"] = s.code if s else "N/A"
        c["subject_color"] = s.color if s else "#3B82F6"

    # Daily trend points (cumulative percentage progression across recorded dates)
    records_sorted = sorted([r for r in records if r.status in ("present", "absent")], key=lambda r: r.date)
    trend_data = []
    cum_att = 0
    cum_cond = 0
    date_points: Dict[str, Dict[str, int]] = {}
    for r in records_sorted:
        d_str = r.date.isoformat()
        if d_str not in date_points:
            date_points[d_str] = {"attended": 0, "conducted": 0}
        date_points[d_str]["conducted"] += r.periods_count
        if r.status == "present":
            date_points[d_str]["attended"] += r.periods_count

    running_a = 0
    running_c = 0
    for d_str, counts in sorted(date_points.items()):
        running_a += counts["attended"]
        running_c += counts["conducted"]
        trend_data.append({
            "date": d_str,
            "percentage": AttendanceEngine.calculate_percentage(running_a, running_c),
            "target": default_target
        })

    return DashboardResponse(
        student_name=current_user.full_name or "",
        student_profile=StudentProfileOut.model_validate(profile),
        overall=overall_stats,
        subjects=subject_stats,
        recent_notifications=[NotificationOut.model_validate(n) for n in notifications],
        upcoming_classes_today=classes_today,
        trend_data=trend_data,
        explanation_factors=overall_risk["factors"]
    )
