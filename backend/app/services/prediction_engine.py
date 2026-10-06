import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from app.services.attendance_engine import AttendanceEngine

class PredictionEngine:
    """
    Attendance Prediction & Forecasting Engine.
    Combines:
    1. Deterministic bounds (Max achievable %, Worst case if missing all remaining)
    2. Behavioral Bayesian / Rolling-trend Baseline projection
    3. Confidence Intervals (Uncertainty estimation)
    4. Projected Shortage Date Calculation
    5. Integration with Trained ML models
    """

    @staticmethod
    def forecast_attendance(
        attended: int,
        conducted: int,
        remaining_classes: int,
        target_percentage: float,
        recent_percentage: Optional[float] = None,
        ml_prediction: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Computes realistic final semester attendance forecast with uncertainty bounds.
        """
        if conducted <= 0:
            return {
                "predicted_percentage": 100.0,
                "confidence_score": 50.0,
                "confidence_interval_low": 75.0,
                "confidence_interval_high": 100.0,
                "max_possible_percentage": 100.0,
                "min_possible_percentage": 0.0,
                "method": "zero_history_baseline"
            }

        current_pct = (attended / conducted) * 100.0
        total_final_conducted = conducted + remaining_classes

        # Deterministic bounds
        max_possible = AttendanceEngine.calculate_max_possible_attendance(attended, conducted, remaining_classes)
        min_possible = round((attended / total_final_conducted) * 100.0, 2) if total_final_conducted > 0 else 0.0

        if remaining_classes <= 0:
            return {
                "predicted_percentage": current_pct,
                "confidence_score": 100.0,
                "confidence_interval_low": current_pct,
                "confidence_interval_high": current_pct,
                "max_possible_percentage": current_pct,
                "min_possible_percentage": current_pct,
                "method": "semester_completed"
            }

        # Behavioral Attendance Probability Estimation:
        # Weight recent trend (60%) and overall history (40%) to capture momentum
        hist_prob = attended / conducted
        recent_prob = (recent_percentage / 100.0) if recent_percentage is not None else hist_prob
        
        # Weighted behavioral probability
        est_prob = (0.6 * recent_prob) + (0.4 * hist_prob)
        est_prob = min(1.0, max(0.0, est_prob))

        # Baseline projection
        projected_future_attended = est_prob * remaining_classes
        projected_final_pct = ((attended + projected_future_attended) / total_final_conducted) * 100.0

        # If an ML prediction is available and reasonable, blend it
        if ml_prediction is not None and min_possible <= ml_prediction <= max_possible:
            final_pred_pct = round((0.7 * ml_prediction) + (0.3 * projected_final_pct), 2)
            method = "blended_ml_baseline"
        else:
            final_pred_pct = round(projected_final_pct, 2)
            method = "behavioral_momentum_baseline"

        # Ensure within physical bounds
        final_pred_pct = max(min_possible, min(max_possible, final_pred_pct))

        # Confidence Estimation:
        # Progress factor: as conducted / total increases, confidence rises
        progress_ratio = conducted / total_final_conducted
        base_confidence = 50.0 + (progress_ratio * 45.0) # 50% to 95%
        
        # Volatility penalty if recent deviates heavily from historical
        volatility = abs(hist_prob - recent_prob)
        confidence_score = round(max(30.0, min(98.0, base_confidence - (volatility * 20.0))), 1)

        # Standard Error of future proportion
        # SE = sqrt(p * (1-p) / max(1, R)) * (R / total_final) * 100
        p = min(0.99, max(0.01, est_prob))
        future_std_err = math.sqrt((p * (1.0 - p)) / max(1, remaining_classes))
        percentage_margin = round(1.96 * future_std_err * (remaining_classes / total_final_conducted) * 100.0, 2)
        percentage_margin = max(1.5, min(15.0, percentage_margin)) # sensible clamp

        ci_low = round(max(min_possible, final_pred_pct - percentage_margin), 2)
        ci_high = round(min(max_possible, final_pred_pct + percentage_margin), 2)

        return {
            "predicted_percentage": final_pred_pct,
            "confidence_score": confidence_score,
            "confidence_interval_low": ci_low,
            "confidence_interval_high": ci_high,
            "max_possible_percentage": max_possible,
            "min_possible_percentage": min_possible,
            "method": method
        }

    @staticmethod
    def calculate_projected_shortage_date(
        attended: int,
        conducted: int,
        target_percentage: float,
        timetables_for_subject: List[Any],
        from_date: date,
        semester_end_date: date,
        recent_absence_rate: float = 0.25 # e.g. student misses 25% of classes
    ) -> Optional[date]:
        """
        Simulates future day-by-day progression under student's recent absence rate.
        Returns the exact future calendar date when attendance first drops below target,
        or None if it stays above target.
        """
        current_pct = (attended / conducted) * 100.0 if conducted > 0 else 100.0
        if current_pct < target_percentage:
            # Already below target
            return from_date

        if from_date >= semester_end_date or not timetables_for_subject:
            return None

        # Map day of week to periods
        dow_periods = {d: 0 for d in range(7)}
        for entry in timetables_for_subject:
            dow = entry.day_of_week if hasattr(entry, "day_of_week") else entry["day_of_week"]
            periods = entry.periods_count if hasattr(entry, "periods_count") else entry.get("periods_count", 1)
            dow_periods[dow] += periods

        curr_att = float(attended)
        curr_cond = float(conducted)
        p_att = max(0.0, min(1.0, 1.0 - recent_absence_rate))

        cursor = from_date + timedelta(days=1)
        while cursor <= semester_end_date:
            dow = cursor.weekday()
            classes_today = dow_periods[dow]
            if classes_today > 0:
                curr_cond += classes_today
                curr_att += (classes_today * p_att)
                running_pct = (curr_att / curr_cond) * 100.0
                if running_pct < target_percentage:
                    return cursor
            cursor += timedelta(days=1)

        return None
