from typing import List, Dict, Any, Optional
import math
from app.services.attendance_engine import AttendanceEngine

class RecommendationEngine:
    """
    Personalized Attendance Recovery & Recommendation Engine.
    Generates actionable, step-by-step milestones to help students regain or protect
    their required attendance percentage.
    """

    @staticmethod
    def generate_recovery_plan(
        subject_id: Optional[str],
        subject_name: Optional[str],
        attended: int,
        conducted: int,
        target_percentage: float,
        remaining_classes: int
    ) -> Dict[str, Any]:
        """
        Builds a structured milestone recovery plan with step-by-step targets.
        """
        current_pct = AttendanceEngine.calculate_percentage(attended, conducted)
        classes_needed = AttendanceEngine.calculate_classes_needed(attended, conducted, target_percentage)
        max_possible = AttendanceEngine.calculate_max_possible_attendance(attended, conducted, remaining_classes)
        
        is_achievable = True
        if remaining_classes > 0 and classes_needed > remaining_classes:
            is_achievable = False

        steps: List[Dict[str, Any]] = []
        action_items: List[str] = []

        if current_pct >= target_percentage:
            safe_bunks = AttendanceEngine.calculate_safe_bunks(attended, conducted, target_percentage)
            action_items.append(f"Your attendance is currently healthy at {current_pct:.1f}%.")
            action_items.append(f"You can safely miss up to {safe_bunks} upcoming classes without falling below {target_percentage:.1f}%.")
            action_items.append("Maintain consistent weekly attendance to preserve your safe bunk buffer for unexpected events.")
            return {
                "subject_id": subject_id,
                "subject_name": subject_name or "Overall Attendance",
                "current_percentage": current_pct,
                "target_percentage": target_percentage,
                "classes_needed": 0,
                "remaining_classes_in_semester": remaining_classes,
                "is_achievable": True,
                "max_achievable_percentage": max_possible,
                "steps": [],
                "action_items": action_items
            }

        if not is_achievable:
            action_items.append(f"CRITICAL: It is mathematically impossible to reach {target_percentage:.1f}% by normal attendance alone.")
            action_items.append(f"Even with 100% attendance in all {remaining_classes} remaining classes, your maximum semester-end percentage will be {max_possible:.1f}%.")
            action_items.append("Immediate Action: Contact your department coordinator or mentor to discuss institutional condonation rules, medical certificate submission, or remedial/extra makeup sessions.")
            
            # Show the maximum effort path
            steps.append({
                "step_number": 1,
                "milestone_name": "Maximum Attendance Effort",
                "consecutive_classes_to_attend": remaining_classes,
                "expected_attendance_percentage": max_possible,
                "target_percentage": target_percentage,
                "target_achieved": False,
                "notes": f"Attending all {remaining_classes} remaining sessions yields {max_possible:.1f}%."
            })

            return {
                "subject_id": subject_id,
                "subject_name": subject_name or "Overall Attendance",
                "current_percentage": current_pct,
                "target_percentage": target_percentage,
                "classes_needed": classes_needed,
                "remaining_classes_in_semester": remaining_classes,
                "is_achievable": False,
                "max_achievable_percentage": max_possible,
                "steps": steps,
                "action_items": action_items
            }

        # Build progressive milestones (e.g. 1/3, 2/3, and 100% of classes needed)
        milestone_points = sorted(list(set([
            max(1, math.ceil(classes_needed * 0.33)),
            max(1, math.ceil(classes_needed * 0.66)),
            classes_needed
        ])))

        for idx, count in enumerate(milestone_points, start=1):
            projected_att = attended + count
            projected_cond = conducted + count
            proj_pct = AttendanceEngine.calculate_percentage(projected_att, projected_cond)
            achieved = proj_pct >= target_percentage
            
            milestone_name = f"Milestone {idx}: Attend next {count} classes"
            if achieved:
                milestone_name = f"Final Goal: Attend {count} classes (Target Restored!)"

            steps.append({
                "step_number": idx,
                "milestone_name": milestone_name,
                "consecutive_classes_to_attend": count,
                "expected_attendance_percentage": proj_pct,
                "target_percentage": target_percentage,
                "target_achieved": achieved,
                "notes": f"Raises attendance from {current_pct:.1f}% to {proj_pct:.1f}%."
            })

        action_items.append(f"Attend the next {classes_needed} consecutive classes without unexcused absence to restore target {target_percentage:.1f}%.")
        action_items.append(f"Prioritize upcoming laboratory and lecture sessions in {subject_name or 'the curriculum'}.")
        action_items.append("Avoid scheduling any personal commitments or bunking during this recovery window.")

        return {
            "subject_id": subject_id,
            "subject_name": subject_name or "Overall Attendance",
            "current_percentage": current_pct,
            "target_percentage": target_percentage,
            "classes_needed": classes_needed,
            "remaining_classes_in_semester": remaining_classes,
            "is_achievable": True,
            "max_achievable_percentage": max_possible,
            "steps": steps,
            "action_items": action_items
        }

    @staticmethod
    def generate_overall_recommendations(
        subjects_data: List[Dict[str, Any]],
        overall_stats: Dict[str, Any]
    ) -> List[str]:
        """
        Synthesizes high-level actionable guidance across all subjects.
        """
        recommendations = []
        high_risk_subjects = [s for s in subjects_data if s.get("risk_level") == "HIGH"]
        zero_bunk_subjects = [s for s in subjects_data if s.get("safe_bunks", 0) == 0 and s.get("current_percentage", 100) >= s.get("target_percentage", 75)]

        if high_risk_subjects:
            names = ", ".join([s["subject_code"] for s in high_risk_subjects])
            recommendations.append(f"Immediate Alert: Attendance in {names} is below required threshold. Prioritize attending these sessions above all others.")

        if zero_bunk_subjects:
            names = ", ".join([s["subject_code"] for s in zero_bunk_subjects])
            recommendations.append(f"Zero Bunk Warning: {names} has 0 safe bunks. Any absence will breach target percentage.")

        if overall_stats.get("is_shortage"):
            needed = overall_stats.get("classes_needed", 0)
            recommendations.append(f"Overall Recovery: You need to attend {needed} consecutive classes across all subjects to lift aggregate attendance above target.")
        else:
            safe = overall_stats.get("safe_bunks", 0)
            if safe > 5:
                recommendations.append(f"Good Standing: Overall attendance is stable with a cushion of {safe} safe bunks. Use absences sparingly for emergencies only.")
            else:
                recommendations.append(f"Caution: Total safe bunk cushion is limited to {safe} classes. Stricter attendance is advised.")

        return recommendations
