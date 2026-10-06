from typing import List, Dict, Any, Optional
from datetime import date
from app.services.attendance_engine import AttendanceEngine
from app.services.timetable_engine import TimetableEngine

class SimulationEngine:
    """
    Simulation & What-If Engine.
    Handles:
    1. Single subject or overall class what-if scenarios (miss N, attend M).
    2. Planned absence simulation across specific future calendar dates using timetable mappings.
    """

    @staticmethod
    def simulate_planned_dates(
        dates_to_miss: List[date],
        subjects_map: Dict[str, Dict[str, Any]], # subject_id -> {code, name, attended, conducted, target}
        timetables: List[Any],
        reason: str = "Planned Absence"
    ) -> Dict[str, Any]:
        """
        Simulates the exact impact of taking leave on specified calendar dates.
        """
        # Count periods missed per subject based on timetable
        missed_by_subject: Dict[str, int] = {s_id: 0 for s_id in subjects_map}
        total_missed_periods = 0

        for d in dates_to_miss:
            scheduled_classes = TimetableEngine.get_classes_for_date(timetables, d)
            for item in scheduled_classes:
                s_id = item["subject_id"]
                periods = item["periods_count"]
                if s_id in missed_by_subject:
                    missed_by_subject[s_id] += periods
                    total_missed_periods += periods

        # Evaluate impact per subject
        impacted_subjects = []
        overall_attended_before = 0
        overall_conducted_before = 0
        overall_attended_after = 0
        overall_conducted_after = 0
        target_breached_any = False

        for s_id, s_data in subjects_map.items():
            att = s_data["attended"]
            cond = s_data["conducted"]
            tgt = s_data["target"]
            missed = missed_by_subject.get(s_id, 0)

            curr_pct = AttendanceEngine.calculate_percentage(att, cond)
            sim_cond = cond + missed
            sim_att = att # no new attendance
            sim_pct = AttendanceEngine.calculate_percentage(sim_att, sim_cond)
            pct_drop = round(curr_pct - sim_pct, 2)
            breaches = sim_pct < tgt

            if breaches and curr_pct >= tgt:
                target_breached_any = True

            new_needed = AttendanceEngine.calculate_classes_needed(sim_att, sim_cond, tgt)

            impacted_subjects.append({
                "subject_id": s_id,
                "subject_code": s_data["code"],
                "subject_name": s_data["name"],
                "periods_missed": missed,
                "current_percentage": curr_pct,
                "projected_percentage": sim_pct,
                "percentage_drop": pct_drop,
                "target_percentage": tgt,
                "target_breached": breaches,
                "classes_needed_to_recover": new_needed
            })

            overall_attended_before += att
            overall_conducted_before += cond
            overall_attended_after += sim_att
            overall_conducted_after += sim_cond

        overall_curr_pct = AttendanceEngine.calculate_percentage(overall_attended_before, overall_conducted_before)
        overall_sim_pct = AttendanceEngine.calculate_percentage(overall_attended_after, overall_conducted_after)
        default_target = 75.0
        overall_target_breached = overall_sim_pct < default_target
        recovery_needed = AttendanceEngine.calculate_classes_needed(overall_attended_after, overall_conducted_after, default_target)

        risk_summary = ""
        if overall_target_breached and overall_curr_pct >= default_target:
            risk_summary = f"CRITICAL: Taking leave on these dates will drop your overall attendance from {overall_curr_pct:.1f}% to {overall_sim_pct:.1f}%, causing an attendance shortage below {default_target:.1f}%!"
        elif target_breached_any:
            risk_summary = f"WARNING: Taking this leave will cause one or more specific subjects to drop below their required target percentage."
        else:
            risk_summary = f"SAFE: You have adequate safe bunks. Overall attendance will drop by {round(overall_curr_pct - overall_sim_pct, 2):.1f}% but remain above target."

        return {
            "dates_simulated": dates_to_miss,
            "total_periods_missed": total_missed_periods,
            "impacted_subjects": impacted_subjects,
            "overall_current_percentage": overall_curr_pct,
            "overall_projected_percentage": overall_sim_pct,
            "overall_target_percentage": default_target,
            "target_breached": overall_target_breached or target_breached_any,
            "recovery_classes_needed_after_leave": recovery_needed,
            "risk_summary": risk_summary
        }
