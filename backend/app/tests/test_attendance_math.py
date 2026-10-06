import pytest
from app.services.attendance_engine import AttendanceEngine

def test_percentage_calculation():
    # 0 conducted
    assert AttendanceEngine.calculate_percentage(0, 0) == 100.0
    # 18 attended out of 24 conducted
    assert AttendanceEngine.calculate_percentage(18, 24) == 75.0
    # 19 attended out of 28 conducted = 67.857... -> 67.86
    assert AttendanceEngine.calculate_percentage(19, 28) == 67.86
    # 100% attendance
    assert AttendanceEngine.calculate_percentage(20, 20) == 100.0

def test_safe_bunks_calculation():
    # Example: 24 attended out of 28 conducted = 85.71%. Target = 75%.
    # B = floor((100 * 24 - 75 * 28) / 75) = floor((2400 - 2100) / 75) = floor(300 / 75) = 4
    # If student bunks 4 classes: 24 / 32 = 75.0%. Exactly target!
    # If student bunks 5 classes: 24 / 33 = 72.72% < 75%.
    assert AttendanceEngine.calculate_safe_bunks(24, 28, 75.0) == 4

    # Current below target: 19 attended out of 28 = 67.86% < 75%
    # Safe bunks must be 0
    assert AttendanceEngine.calculate_safe_bunks(19, 28, 75.0) == 0

    # Exactly at target: 15 attended out of 20 = 75.0%
    # (1500 - 1500) / 75 = 0
    assert AttendanceEngine.calculate_safe_bunks(15, 20, 75.0) == 0

def test_classes_needed_calculation():
    # Current below target: 19 attended out of 28 conducted. Target = 75%.
    # N = ceil((75 * 28 - 100 * 19) / (100 - 75)) = ceil((2100 - 1900) / 25) = ceil(200 / 25) = 8
    # After attending 8 consecutive:
    # Attended = 19 + 8 = 27
    # Conducted = 28 + 8 = 36
    # 27 / 36 = 75.0%. Exactly reaches target!
    assert AttendanceEngine.calculate_classes_needed(19, 28, 75.0) == 8

    # Already above target: 24 attended out of 28 conducted.
    # Needed must be 0
    assert AttendanceEngine.calculate_classes_needed(24, 28, 75.0) == 0

    # Boundary: Target 100% when 1 class already missed
    # Should flag impossible (-1)
    assert AttendanceEngine.calculate_classes_needed(9, 10, 100.0) == -1

def test_max_possible_attendance():
    # 19 attended out of 28 conducted. Remaining = 12.
    # Total final = 40. Max attended = 19 + 12 = 31.
    # 31 / 40 = 77.5%
    assert AttendanceEngine.calculate_max_possible_attendance(19, 28, 12) == 77.5

def test_what_if_scenario():
    # Current: 18 / 20 = 90.0%, Target: 75%
    # What if student misses 3 classes and attends 0?
    # New: 18 / 23 = 78.26%
    res = AttendanceEngine.calculate_what_if(18, 20, 75.0, miss_classes=3, attend_classes=0)
    assert res["current_percentage"] == 90.0
    assert res["simulated_percentage"] == 78.26
    assert res["is_target_met"] is True
    assert res["percentage_change"] == -11.74
