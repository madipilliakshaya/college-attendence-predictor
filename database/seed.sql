-- ====================================================================
-- College Attendance Predictor: Seed Data for BTech IT (Semester 6)
-- Provides realistic subjects, attendance history, timetable, targets
-- ====================================================================

-- 1. Demo Student User
-- Password is 'Password123!' (hashed with bcrypt: $2b$12$K1H1a9mZ9r8zFqg1gD9VquZq6S0fJk9Jq5w7Fp8rQ7hY1vX6s2Yeq)
INSERT INTO users (id, email, full_name, hashed_password, role)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'student@college.edu',
    'Aarav Sharma',
    '$2b$12$e/9VfX0H5GzC9W8Z8w7H7uC0l5TfX4X0e8Y3O9M4a8q1Q3k9Q7m4m',
    'student'
) ON CONFLICT (id) DO NOTHING;

-- 2. Student Profile (Semester 6, IT department, 75% college target)
-- Semester runs from 2026-08-01 to 2026-12-15
INSERT INTO student_profiles (
    id, user_id, roll_number, department, semester, college_name,
    default_attendance_target, semester_start_date, semester_end_date
) VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '23IT4012',
    'Information Technology',
    6,
    'National Institute of Technology',
    75.00,
    '2026-08-03',
    '2026-12-11'
) ON CONFLICT (user_id) DO NOTHING;

-- 3. Core BTech IT Subjects
-- CS601: Distributed Systems (Lecture, 4 credits, target 75%)
-- CS602: Database Management Systems (Lecture, 4 credits, target 75%)
-- CS603: Machine Learning & Predictive Analytics (Lecture, 3 credits, target 75%)
-- CS604: Web Technologies & Cloud Computing (Lecture, 3 credits, target 75%)
-- CS605: Computer Networks Lab (Lab, 2 credits, 2 hours per session, target 80%)
-- CS606: Full Stack Web Lab (Lab, 2 credits, 2 hours per session, target 80%)
INSERT INTO subjects (id, user_id, code, name, subject_type, credits, duration_hours, target_percentage, color) VALUES
('11111111-1111-1111-1111-111111110001', '00000000-0000-0000-0000-000000000001', 'CS601', 'Distributed Systems', 'lecture', 4, 1.00, 75.00, '#3B82F6'),
('11111111-1111-1111-1111-111111110002', '00000000-0000-0000-0000-000000000001', 'CS602', 'Database Management Systems', 'lecture', 4, 1.00, 75.00, '#EF4444'),
('11111111-1111-1111-1111-111111110003', '00000000-0000-0000-0000-000000000001', 'CS603', 'Machine Learning & Analytics', 'lecture', 3, 1.00, 75.00, '#10B981'),
('11111111-1111-1111-1111-111111110004', '00000000-0000-0000-0000-000000000001', 'CS604', 'Web Technologies & Cloud', 'lecture', 3, 1.00, 75.00, '#F59E0B'),
('11111111-1111-1111-1111-111111110005', '00000000-0000-0000-0000-000000000001', 'CS605', 'Computer Networks Lab', 'lab', 2, 2.00, 80.00, '#8B5CF6'),
('11111111-1111-1111-1111-111111110006', '00000000-0000-0000-0000-000000000001', 'CS606', 'Full Stack Development Lab', 'lab', 2, 2.00, 80.00, '#06B6D4')
ON CONFLICT DO NOTHING;

-- 4. Weekly Timetable (Monday to Friday)
-- Monday (0)
INSERT INTO timetables (user_id, subject_id, day_of_week, start_time, end_time, room, periods_count) VALUES
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110001', 0, '09:00', '10:00', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110002', 0, '10:00', '11:00', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110003', 0, '11:15', '12:15', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110005', 0, '13:30', '15:30', 'NET-LAB-1', 2);

-- Tuesday (1)
INSERT INTO timetables (user_id, subject_id, day_of_week, start_time, end_time, room, periods_count) VALUES
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110004', 1, '09:00', '10:00', 'LH-202', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110001', 1, '10:00', '11:00', 'LH-202', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110002', 1, '11:15', '12:15', 'LH-202', 1);

-- Wednesday (2)
INSERT INTO timetables (user_id, subject_id, day_of_week, start_time, end_time, room, periods_count) VALUES
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110003', 2, '09:00', '10:00', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110004', 2, '10:00', '11:00', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110006', 2, '13:30', '15:30', 'DEV-LAB-2', 2);

-- Thursday (3)
INSERT INTO timetables (user_id, subject_id, day_of_week, start_time, end_time, room, periods_count) VALUES
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110001', 3, '09:00', '10:00', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110002', 3, '10:00', '11:00', 'LH-201', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110003', 3, '11:15', '12:15', 'LH-201', 1);

-- Friday (4)
INSERT INTO timetables (user_id, subject_id, day_of_week, start_time, end_time, room, periods_count) VALUES
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110004', 4, '09:00', '10:00', 'LH-203', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110001', 4, '10:00', '11:00', 'LH-203', 1),
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110002', 4, '11:15', '12:15', 'LH-203', 1);

-- 5. Notifications
INSERT INTO notifications (user_id, subject_id, title, message, alert_type) VALUES
('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111110002', 'High Risk: DBMS Attendance Below Target', 'Your Database Management Systems attendance is currently at 69.23%, which is below your target of 75.00%. You need to attend the next 3 consecutive classes to recover.', 'shortage'),
('00000000-0000-0000-0000-000000000001', NULL, 'Recovery Milestone: 2 Weeks Goal', 'Attending all classes this upcoming week will increase your aggregate semester attendance from 76.5% to 79.1%.', 'recovery_needed');
