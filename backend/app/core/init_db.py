from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.db_models import User, StudentProfile, Subject, Timetable, AttendanceRecord, Notification
from app.core.security import get_password_hash

def init_db_with_seed_data(db: Session):
    # Check if user already exists
    demo_user = db.query(User).filter(User.email == "student@college.edu").first()
    if demo_user:
        return

    # 1. Create demo student user
    user = User(
        id="00000000-0000-0000-0000-000000000001",
        email="student@college.edu",
        full_name="Aarav Sharma",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db.add(user)
    db.flush()

    # 2. Student Profile (Semester 6: Aug 3, 2026 to Dec 11, 2026)
    profile = StudentProfile(
        id="00000000-0000-0000-0000-000000000002",
        user_id=user.id,
        roll_number="23IT4012",
        department="Information Technology",
        semester=6,
        college_name="National Institute of Technology",
        default_attendance_target=75.0,
        semester_start_date=date(2026, 8, 3),
        semester_end_date=date(2026, 12, 11)
    )
    db.add(profile)
    db.flush()

    # 3. Core BTech IT Subjects
    # CS601: Distributed Systems (Lecture, 4 credits, target 75%)
    # CS602: Database Management Systems (Lecture, 4 credits, target 75%) - will have lower attendance to demonstrate risk & recovery!
    # CS603: Machine Learning & Analytics (Lecture, 3 credits, target 75%)
    # CS604: Web Technologies & Cloud (Lecture, 3 credits, target 75%)
    # CS605: Computer Networks Lab (Lab, 2 credits, 2.0 hrs, target 80%)
    # CS606: Full Stack Lab (Lab, 2 credits, 2.0 hrs, target 80%)
    subjects_data = [
        {"id": "11111111-1111-1111-1111-111111110001", "code": "CS601", "name": "Distributed Systems", "subject_type": "lecture", "credits": 4, "duration_hours": 1.0, "target_percentage": 75.0, "color": "#3B82F6"},
        {"id": "11111111-1111-1111-1111-111111110002", "code": "CS602", "name": "Database Management Systems", "subject_type": "lecture", "credits": 4, "duration_hours": 1.0, "target_percentage": 75.0, "color": "#EF4444"},
        {"id": "11111111-1111-1111-1111-111111110003", "code": "CS603", "name": "Machine Learning & Analytics", "subject_type": "lecture", "credits": 3, "duration_hours": 1.0, "target_percentage": 75.0, "color": "#10B981"},
        {"id": "11111111-1111-1111-1111-111111110004", "code": "CS604", "name": "Web Technologies & Cloud", "subject_type": "lecture", "credits": 3, "duration_hours": 1.0, "target_percentage": 75.0, "color": "#F59E0B"},
        {"id": "11111111-1111-1111-1111-111111110005", "code": "CS605", "name": "Computer Networks Lab", "subject_type": "lab", "credits": 2, "duration_hours": 2.0, "target_percentage": 80.0, "color": "#8B5CF6"},
        {"id": "11111111-1111-1111-1111-111111110006", "code": "CS606", "name": "Full Stack Development Lab", "subject_type": "lab", "credits": 2, "duration_hours": 2.0, "target_percentage": 80.0, "color": "#06B6D4"}
    ]

    for sd in subjects_data:
        subj = Subject(user_id=user.id, **sd)
        db.add(subj)
    db.flush()

    # 4. Weekly Timetable Slots
    # Mon: CS601 (9-10), CS602 (10-11), CS603 (11:15-12:15), CS605 (13:30-15:30, 2 periods)
    # Tue: CS604 (9-10), CS601 (10-11), CS602 (11:15-12:15)
    # Wed: CS603 (9-10), CS604 (10-11), CS606 (13:30-15:30, 2 periods)
    # Thu: CS601 (9-10), CS602 (10-11), CS603 (11:15-12:15)
    # Fri: CS604 (9-10), CS601 (10-11), CS602 (11:15-12:15)
    timetable_slots = [
        # Monday (0)
        {"subject_id": "11111111-1111-1111-1111-111111110001", "day_of_week": 0, "start_time": "09:00", "end_time": "10:00", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110002", "day_of_week": 0, "start_time": "10:00", "end_time": "11:00", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110003", "day_of_week": 0, "start_time": "11:15", "end_time": "12:15", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110005", "day_of_week": 0, "start_time": "13:30", "end_time": "15:30", "room": "NET-LAB-1", "periods_count": 2},
        # Tuesday (1)
        {"subject_id": "11111111-1111-1111-1111-111111110004", "day_of_week": 1, "start_time": "09:00", "end_time": "10:00", "room": "LH-202", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110001", "day_of_week": 1, "start_time": "10:00", "end_time": "11:00", "room": "LH-202", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110002", "day_of_week": 1, "start_time": "11:15", "end_time": "12:15", "room": "LH-202", "periods_count": 1},
        # Wednesday (2)
        {"subject_id": "11111111-1111-1111-1111-111111110003", "day_of_week": 2, "start_time": "09:00", "end_time": "10:00", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110004", "day_of_week": 2, "start_time": "10:00", "end_time": "11:00", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110006", "day_of_week": 2, "start_time": "13:30", "end_time": "15:30", "room": "DEV-LAB-2", "periods_count": 2},
        # Thursday (3)
        {"subject_id": "11111111-1111-1111-1111-111111110001", "day_of_week": 3, "start_time": "09:00", "end_time": "10:00", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110002", "day_of_week": 3, "start_time": "10:00", "end_time": "11:00", "room": "LH-201", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110003", "day_of_week": 3, "start_time": "11:15", "end_time": "12:15", "room": "LH-201", "periods_count": 1},
        # Friday (4)
        {"subject_id": "11111111-1111-1111-1111-111111110004", "day_of_week": 4, "start_time": "09:00", "end_time": "10:00", "room": "LH-203", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110001", "day_of_week": 4, "start_time": "10:00", "end_time": "11:00", "room": "LH-203", "periods_count": 1},
        {"subject_id": "11111111-1111-1111-1111-111111110002", "day_of_week": 4, "start_time": "11:15", "end_time": "12:15", "room": "LH-203", "periods_count": 1}
    ]

    for ts in timetable_slots:
        t_entry = Timetable(user_id=user.id, **ts)
        db.add(t_entry)
    db.flush()

    # 5. Seed 8 weeks of historical attendance (from 2026-08-03 to 2026-09-25)
    # Simulates:
    # CS601: 28 conducted, 23 attended (82.14%) -> Low risk, safe bunks available
    # CS602 (DBMS): 28 conducted, 19 attended (67.86%) -> High risk, shortage!
    # CS603: 21 conducted, 18 attended (85.71%) -> Low risk
    # CS604: 21 conducted, 16 attended (76.19%) -> Medium risk, borderline!
    # CS605 (Net Lab): 8 sessions (16 periods), 14 attended (87.5%) -> Low risk
    # CS606 (Dev Lab): 8 sessions (16 periods), 14 attended (87.5%) -> Low risk
    cur_date = date(2026, 8, 3)
    end_history = date(2026, 9, 25)

    # Weekday schedule mapping
    dow_map = {
        0: [("11111111-1111-1111-1111-111111110001", 1), ("11111111-1111-1111-1111-111111110002", 1), ("11111111-1111-1111-1111-111111110003", 1), ("11111111-1111-1111-1111-111111110005", 2)],
        1: [("11111111-1111-1111-1111-111111110004", 1), ("11111111-1111-1111-1111-111111110001", 1), ("11111111-1111-1111-1111-111111110002", 1)],
        2: [("11111111-1111-1111-1111-111111110003", 1), ("11111111-1111-1111-1111-111111110004", 1), ("11111111-1111-1111-1111-111111110006", 2)],
        3: [("11111111-1111-1111-1111-111111110001", 1), ("11111111-1111-1111-1111-111111110002", 1), ("11111111-1111-1111-1111-111111110003", 1)],
        4: [("11111111-1111-1111-1111-111111110004", 1), ("11111111-1111-1111-1111-111111110001", 1), ("11111111-1111-1111-1111-111111110002", 1)]
    }

    # Controlled absence counts to match exact percentages
    absent_targets = {
        "11111111-1111-1111-1111-111111110001": 5, # CS601: 5 absent out of 28 -> 23 attended = 82.14%
        "11111111-1111-1111-1111-111111110002": 9, # CS602: 9 absent out of 28 -> 19 attended = 67.86% (SHORTAGE!)
        "11111111-1111-1111-1111-111111110003": 3, # CS603: 3 absent out of 21 -> 18 attended = 85.71%
        "11111111-1111-1111-1111-111111110004": 5, # CS604: 5 absent out of 21 -> 16 attended = 76.19% (Borderline!)
        "11111111-1111-1111-1111-111111110005": 2, # CS605: 1 session (2 periods) absent out of 16 -> 14 attended = 87.5%
        "11111111-1111-1111-1111-111111110006": 2  # CS606: 1 session (2 periods) absent out of 16 -> 14 attended = 87.5%
    }
    absent_done = {k: 0 for k in absent_targets}

    step_date = cur_date
    while step_date <= end_history:
        dow = step_date.weekday()
        if dow in dow_map:
            for s_id, periods in dow_map[dow]:
                # Determine status
                status = "present"
                reason = "none"
                if absent_done[s_id] < absent_targets[s_id] and (step_date.day % 4 == 0 or step_date.day % 7 == 0):
                    status = "absent"
                    absent_done[s_id] += periods
                    reasons_pool = ["illness", "personal", "college_event"]
                    reason = reasons_pool[step_date.day % len(reasons_pool)]

                rec = AttendanceRecord(
                    user_id=user.id,
                    subject_id=s_id,
                    date=step_date,
                    status=status,
                    periods_count=periods,
                    reason_category=reason,
                    notes=f"Recorded session on {step_date.isoformat()}"
                )
                db.add(rec)
        step_date += timedelta(days=1)

    # 6. Notifications
    n1 = Notification(
        user_id=user.id,
        subject_id="11111111-1111-1111-1111-111111110002",
        title="High Risk Shortage: CS602 (DBMS)",
        message="Your Database Management Systems attendance is currently at 67.86%, which is below your target of 75.00%. You need to attend the next 8 consecutive classes to recover.",
        alert_type="shortage",
        is_read=False
    )
    n2 = Notification(
        user_id=user.id,
        subject_id="11111111-1111-1111-1111-111111110004",
        title="Borderline Alert: CS604",
        message="Your Web Technologies & Cloud attendance is at 76.19% with only 1 safe bunk remaining before slipping below 75%.",
        alert_type="warning",
        is_read=False
    )
    db.add(n1)
    db.add(n2)
    db.commit()
    print("Database successfully seeded with realistic BTech IT curriculum & attendance history.")
