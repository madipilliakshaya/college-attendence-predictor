import pytest
from datetime import date
from app.services.timetable_engine import TimetableEngine

class DummyTimetable:
    def __init__(self, subject_id, day_of_week, periods_count=1, start_time="09:00", end_time="10:00", room="LH-1"):
        self.subject_id = subject_id
        self.day_of_week = day_of_week
        self.periods_count = periods_count
        self.start_time = start_time
        self.end_time = end_time
        self.room = room

def test_timetable_remaining_classes():
    # 2 subjects: S1 (Mon: 1, Wed: 1, Fri: 1 -> 3/week)
    #             S2 (Tue: 2 periods lab)
    timetables = [
        DummyTimetable("S1", 0, 1),
        DummyTimetable("S1", 2, 1),
        DummyTimetable("S1", 4, 1),
        DummyTimetable("S2", 1, 2)
    ]

    # Monday 2026-10-05 to Friday 2026-10-16 (2 full weeks: 12 days total)
    from_date = date(2026, 10, 5) # Monday
    to_date = date(2026, 10, 16)   # Friday of next week

    counts = TimetableEngine.calculate_remaining_classes_by_subject(timetables, from_date, to_date)
    # Remaining starts from from_date + 1 (Tue Oct 6 to Fri Oct 16)
    # In that period:
    # Wed Oct 7 (S1), Fri Oct 9 (S1), Mon Oct 12 (S1), Wed Oct 14 (S1), Fri Oct 16 (S1) -> 5 periods for S1
    # Tue Oct 6 (S2: 2), Tue Oct 13 (S2: 2) -> 4 periods for S2
    assert counts["S1"] == 5
    assert counts["S2"] == 4

def test_classes_for_date():
    timetables = [
        DummyTimetable("S1", 0, 1, start_time="09:00"),
        DummyTimetable("S2", 0, 2, start_time="10:00"),
        DummyTimetable("S3", 1, 1, start_time="09:00")
    ]
    # 2026-10-05 is Monday (day 0)
    mon_classes = TimetableEngine.get_classes_for_date(timetables, date(2026, 10, 5))
    assert len(mon_classes) == 2
    assert mon_classes[0]["subject_id"] == "S1"
    assert mon_classes[1]["subject_id"] == "S2"
