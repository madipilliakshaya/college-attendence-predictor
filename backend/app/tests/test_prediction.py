import pytest
from datetime import date
from app.services.prediction_engine import PredictionEngine

def test_forecast_attendance_bounds():
    # 20 attended out of 25 conducted. 15 remaining classes. Target = 75%.
    # Current = 80.0%
    res = PredictionEngine.forecast_attendance(
        attended=20,
        conducted=25,
        remaining_classes=15,
        target_percentage=75.0,
        recent_percentage=85.0
    )

    assert "predicted_percentage" in res
    assert "confidence_score" in res
    assert "confidence_interval_low" in res
    assert "confidence_interval_high" in res
    assert res["min_possible_percentage"] <= res["predicted_percentage"] <= res["max_possible_percentage"]
    assert res["confidence_interval_low"] <= res["predicted_percentage"] <= res["confidence_interval_high"]
    assert res["max_possible_percentage"] == round(((20 + 15) / (25 + 15)) * 100.0, 2) # 35 / 40 = 87.5%

def test_shortage_date_detection():
    # Student has 15 attended out of 19 conducted = 78.95%. Target = 75%.
    # If student continues missing 50% of classes, will attendance breach 75%?
    class DummyTimetable:
        def __init__(self, day_of_week, periods_count=1):
            self.day_of_week = day_of_week
            self.periods_count = periods_count

    timetables = [
        DummyTimetable(0, 1), # Mon
        DummyTimetable(1, 1), # Tue
        DummyTimetable(2, 1), # Wed
        DummyTimetable(3, 1), # Thu
        DummyTimetable(4, 1)  # Fri
    ]

    shortage_date = PredictionEngine.calculate_projected_shortage_date(
        attended=15,
        conducted=19,
        target_percentage=75.0,
        timetables_for_subject=timetables,
        from_date=date(2026, 10, 5),
        semester_end_date=date(2026, 11, 30),
        recent_absence_rate=0.5 # missing half of upcoming classes
    )

    assert shortage_date is not None
    assert shortage_date > date(2026, 10, 5)
