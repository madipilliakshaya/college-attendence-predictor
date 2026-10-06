import math
from typing import List, Dict, Any, Optional
from datetime import date, timedelta

class AttendanceEngine:
    """
    Deterministic Attendance Calculation Engine.
    All calculations are pure, mathematically verified, and deterministic.
    """

    @staticmethod
    def calculate_percentage(attended: float, conducted: float) -> float:
        """
        Calculate attendance percentage P = (A / C) * 100.
        Returns 100.0 if no classes have been conducted yet.
        """
        if conducted <= 0:
            return 100.0
        pct = (attended / conducted) * 100.0
        return round(min(100.0, max(0.0, pct)), 2)

    @staticmethod
    def calculate_safe_bunks(attended: int, conducted: int, target: float) -> int:
        """
        Calculates maximum upcoming classes that can be missed while maintaining >= target%.
        B = floor((100 * A - T * C) / T)
        If current percentage is already below target, safe bunks = 0.
        """
        if target <= 0:
            return 999
        if conducted <= 0:
            return 0
        
        current_pct = (attended / conducted) * 100.0
        if current_pct < target:
            return 0
        
        numerator = (100.0 * attended) - (target * conducted)
        bunks = math.floor(numerator / target)
        return max(0, int(bunks))

    @staticmethod
    def calculate_classes_needed(attended: int, conducted: int, target: float) -> int:
        """
        Calculates minimum consecutive upcoming classes that must be attended to reach target%.
        N = ceil((T * C - 100 * A) / (100 - T))
        If current percentage is already >= target, classes needed = 0.
        If target is 100% and student missed any class, it is impossible (returns -1).
        """
        if conducted <= 0:
            return 0
        
        current_pct = (attended / conducted) * 100.0
        if current_pct >= target:
            return 0
        
        if target >= 100.0:
            if conducted > attended:
                return -1 # Mathematically impossible
            return 0

        numerator = (target * conducted) - (100.0 * attended)
        denominator = 100.0 - target
        
        needed = math.ceil(numerator / denominator)
        return max(0, int(needed))

    @staticmethod
    def calculate_max_possible_attendance(attended: int, conducted: int, remaining: int) -> float:
        """
        Calculates maximum attainable percentage if student attends 100% of remaining classes.
        P_max = (A + R) / (C + R) * 100
        """
        total_future_conducted = conducted + remaining
        if total_future_conducted <= 0:
            return 100.0
        max_pct = ((attended + remaining) / total_future_conducted) * 100.0
        return round(min(100.0, max(0.0, max_pct)), 2)

    @staticmethod
    def calculate_what_if(
        attended: int,
        conducted: int,
        target: float,
        miss_classes: int = 0,
        attend_classes: int = 0
    ) -> Dict[str, Any]:
        """
        Simulate outcome of attending `attend_classes` and missing `miss_classes`.
        """
        sim_attended = attended + attend_classes
        sim_conducted = conducted + attend_classes + miss_classes
        sim_pct = AttendanceEngine.calculate_percentage(sim_attended, sim_conducted)
        current_pct = AttendanceEngine.calculate_percentage(attended, conducted)
        
        new_safe_bunks = AttendanceEngine.calculate_safe_bunks(sim_attended, sim_conducted, target)
        new_classes_needed = AttendanceEngine.calculate_classes_needed(sim_attended, sim_conducted, target)
        
        # Risk classification
        if sim_pct < target:
            risk = "HIGH"
        elif sim_pct < target + 5.0 or new_safe_bunks <= 2:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "current_percentage": current_pct,
            "simulated_percentage": sim_pct,
            "percentage_change": round(sim_pct - current_pct, 2),
            "target_percentage": target,
            "is_target_met": sim_pct >= target,
            "new_safe_bunks": new_safe_bunks,
            "new_classes_needed": new_classes_needed,
            "new_risk_level": risk
        }

    @staticmethod
    def calculate_trend(records: List[Any], days_window: int = 14) -> Dict[str, Any]:
        """
        Computes rolling attendance rate for recent `days_window` days vs historical,
        and provides momentum indicator.
        records: list of objects or dicts with .date, .status, .periods_count
        """
        if not records:
            return {
                "recent_percentage": 100.0,
                "overall_percentage": 100.0,
                "delta": 0.0,
                "trend_direction": "STABLE",
                "consecutive_absences": 0
            }

        sorted_records = sorted(
            records,
            key=lambda r: r.date if hasattr(r, "date") else r["date"]
        )

        latest_date = sorted_records[-1].date if hasattr(sorted_records[-1], "date") else sorted_records[-1]["date"]
        cutoff_date = latest_date - timedelta(days=days_window)

        recent_conducted = 0
        recent_attended = 0
        overall_conducted = 0
        overall_attended = 0

        # Check consecutive absences backwards from latest
        consecutive_absences = 0
        checking_consecutive = True

        for rec in reversed(sorted_records):
            status = rec.status if hasattr(rec, "status") else rec["status"]
            periods = rec.periods_count if hasattr(rec, "periods_count") else rec["periods_count"]
            r_date = rec.date if hasattr(rec, "date") else rec["date"]

            if status == "cancelled":
                continue

            overall_conducted += periods
            if status == "present":
                overall_attended += periods
                checking_consecutive = False
            elif status == "absent":
                if checking_consecutive:
                    consecutive_absences += periods

            if r_date >= cutoff_date:
                recent_conducted += periods
                if status == "present":
                    recent_attended += periods

        recent_pct = AttendanceEngine.calculate_percentage(recent_attended, recent_conducted)
        overall_pct = AttendanceEngine.calculate_percentage(overall_attended, overall_conducted)
        delta = round(recent_pct - overall_pct, 2)

        if delta > 2.0:
            trend_dir = "IMPROVING"
        elif delta < -2.0:
            trend_dir = "DECLINING"
        else:
            trend_dir = "STABLE"

        return {
            "recent_percentage": recent_pct,
            "overall_percentage": overall_pct,
            "delta": delta,
            "trend_direction": trend_dir,
            "consecutive_absences": consecutive_absences
        }
