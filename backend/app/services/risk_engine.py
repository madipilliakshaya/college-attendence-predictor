from typing import List, Dict, Any, Optional
from datetime import date

class RiskEngine:
    """
    Transparent & Explainable Attendance Risk Engine.
    Evaluates attendance health across multiple dimensions and outputs
    both a risk classification (LOW / MEDIUM / HIGH) and transparent
    contributing factors.
    """

    @staticmethod
    def evaluate_risk(
        current_percentage: float,
        target_percentage: float,
        safe_bunks: int,
        classes_needed: int,
        remaining_classes: int,
        predicted_percentage: float,
        trend_direction: str = "STABLE",
        consecutive_absences: int = 0,
        projected_shortage_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Assesses risk and returns level, risk score (0-100), and explainable contributing factors.
        """
        factors: List[str] = []
        risk_score = 0.0 # 0 is safest, 100 is maximum danger

        # 1. Current Percentage vs Target
        pct_diff = current_percentage - target_percentage
        if pct_diff < 0:
            # Below target: automatically high risk baseline
            deficit = abs(pct_diff)
            risk_score += min(50.0, 30.0 + (deficit * 2.0))
            factors.append(f"Current attendance ({current_percentage:.1f}%) is {deficit:.1f}% below your required target of {target_percentage:.1f}%.")
        elif pct_diff < 3.0:
            risk_score += 25.0
            factors.append(f"Current attendance ({current_percentage:.1f}%) is dangerously close to your {target_percentage:.1f}% target margin.")
        elif pct_diff < 7.0:
            risk_score += 10.0
            factors.append(f"Current attendance is maintaining a moderate buffer ({pct_diff:.1f}%) above target.")
        else:
            factors.append(f"Healthy attendance buffer ({pct_diff:.1f}%) above the {target_percentage:.1f}% target.")

        # 2. Safe Bunks Evaluation
        if safe_bunks == 0 and current_percentage >= target_percentage:
            risk_score += 20.0
            factors.append("Zero safe bunks available: any absence will immediately trigger an attendance shortage.")
        elif safe_bunks == 1:
            risk_score += 15.0
            factors.append("Extremely tight buffer: only 1 safe bunk remaining before falling below target.")
        elif safe_bunks >= 4:
            factors.append(f"Comfortable margin: {safe_bunks} safe bunks available without falling below target.")

        # 3. Recovery Feasibility (Classes Needed vs Remaining Classes)
        if classes_needed > 0:
            if remaining_classes > 0 and classes_needed > remaining_classes:
                risk_score += 40.0
                factors.append(f"CRITICAL: Recovery required ({classes_needed} classes) exceeds total remaining semester classes ({remaining_classes}). Target is unachievable without official condonation or extra sessions.")
            elif remaining_classes > 0 and classes_needed > (0.5 * remaining_classes):
                risk_score += 25.0
                factors.append(f"High recovery burden: You must attend {classes_needed} consecutive classes, which represents more than 50% of your remaining semester classes ({remaining_classes}).")
            else:
                risk_score += 15.0
                factors.append(f"Recovery active: You need {classes_needed} consecutive attendances to regain target.")

        # 4. Predicted Final Attendance vs Target
        pred_diff = predicted_percentage - target_percentage
        if pred_diff < 0:
            risk_score += 20.0
            factors.append(f"Predicted semester-end attendance ({predicted_percentage:.1f}%) falls short of the {target_percentage:.1f}% requirement.")
        elif pred_diff < 2.0:
            risk_score += 10.0
            factors.append(f"Predicted final attendance ({predicted_percentage:.1f}%) provides very little room for error.")

        # 5. Trend & Momentum
        if trend_direction == "DECLINING":
            risk_score += 15.0
            factors.append("Recent 14-day attendance rate shows a negative downward trend.")
        elif trend_direction == "IMPROVING":
            risk_score = max(0.0, risk_score - 10.0)
            factors.append("Recent attendance shows positive upward recovery momentum.")

        # 6. Consecutive Absences
        if consecutive_absences >= 3:
            risk_score += 10.0
            factors.append(f"Warning: {consecutive_absences} consecutive absences recorded recently.")

        # 7. Projected Shortage Date
        if projected_shortage_date is not None:
            factors.append(f"Projected shortage warning: Anticipated to breach target threshold around {projected_shortage_date.strftime('%d %B %Y')} at current absence frequency.")

        # Categorize
        risk_score = round(min(100.0, max(0.0, risk_score)), 1)
        if risk_score >= 50.0 or current_percentage < target_percentage or (remaining_classes > 0 and classes_needed > remaining_classes):
            level = "HIGH"
        elif risk_score >= 25.0 or safe_bunks <= 2:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "risk_level": level,
            "risk_score": risk_score,
            "factors": factors
        }
