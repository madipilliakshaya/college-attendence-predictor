-- ====================================================================
-- College Attendance Predictor: Authoritative Relational Database Schema
-- Compatible with Supabase / PostgreSQL 14+
-- ====================================================================

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Clean existing schema if re-running
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS prediction_snapshots CASCADE;
DROP TABLE IF EXISTS planned_absences CASCADE;
DROP TABLE IF EXISTS attendance_records CASCADE;
DROP TABLE IF EXISTS timetables CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS student_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Users Table (Aligned with Supabase Auth or standalone user storage)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'faculty', 'admin')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Student Profiles
CREATE TABLE student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    roll_number VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL DEFAULT 'Information Technology',
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 10),
    college_name VARCHAR(255) NOT NULL DEFAULT 'Engineering College',
    default_attendance_target NUMERIC(5, 2) NOT NULL DEFAULT 75.00 CHECK (default_attendance_target >= 0.00 AND default_attendance_target <= 100.00),
    semester_start_date DATE NOT NULL,
    semester_end_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_semester_dates CHECK (semester_end_date > semester_start_date),
    CONSTRAINT uq_student_user UNIQUE (user_id)
);

-- 3. Subjects Table
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    subject_type VARCHAR(50) NOT NULL DEFAULT 'lecture' CHECK (subject_type IN ('lecture', 'lab', 'tutorial', 'practical', 'extra')),
    credits INTEGER NOT NULL DEFAULT 3 CHECK (credits > 0),
    duration_hours NUMERIC(4, 2) NOT NULL DEFAULT 1.00 CHECK (duration_hours > 0),
    target_percentage NUMERIC(5, 2) NOT NULL DEFAULT 75.00 CHECK (target_percentage >= 0.00 AND target_percentage <= 100.00),
    color VARCHAR(20) DEFAULT '#3B82F6',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_subject_code UNIQUE (user_id, code)
);

-- 4. Timetables (Weekly Recurring Schedule)
CREATE TABLE timetables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Monday, 6=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room VARCHAR(50),
    periods_count INTEGER NOT NULL DEFAULT 1 CHECK (periods_count > 0),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_timetable_time CHECK (end_time > start_time)
);

-- 5. Attendance Records (Actual historical tracking per session/day)
CREATE TABLE attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'cancelled')),
    periods_count INTEGER NOT NULL DEFAULT 1 CHECK (periods_count > 0),
    reason_category VARCHAR(50) DEFAULT 'none' CHECK (reason_category IN ('none', 'illness', 'college_event', 'personal', 'approved_leave', 'other')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Planned Absences (For forward-looking what-if scenarios and calendar planning)
CREATE TABLE planned_absences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE, -- NULL indicates whole day absence
    date DATE NOT NULL,
    periods_count INTEGER NOT NULL DEFAULT 1 CHECK (periods_count > 0),
    reason VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Prediction & Risk Snapshots (Periodic or on-demand cached forecasts)
CREATE TABLE prediction_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE, -- NULL for overall aggregate
    calculation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    current_percentage NUMERIC(5, 2) NOT NULL,
    predicted_percentage NUMERIC(5, 2) NOT NULL,
    confidence_score NUMERIC(5, 2) NOT NULL,
    confidence_interval_low NUMERIC(5, 2) NOT NULL,
    confidence_interval_high NUMERIC(5, 2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    projected_shortage_date DATE,
    recommendation_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. Notifications & Alerts
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('shortage', 'projected_shortage', 'high_risk', 'recovery_needed', 'warning', 'info')),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- INDEXES FOR HIGH-PERFORMANCE QUERIES
-- ====================================================================
CREATE INDEX idx_student_profiles_user ON student_profiles(user_id);
CREATE INDEX idx_subjects_user ON subjects(user_id);
CREATE INDEX idx_timetables_user_day ON timetables(user_id, day_of_week);
CREATE INDEX idx_attendance_records_user_date ON attendance_records(user_id, date);
CREATE INDEX idx_attendance_records_subject ON attendance_records(subject_id);
CREATE INDEX idx_attendance_records_user_subject_date ON attendance_records(user_id, subject_id, date);
CREATE INDEX idx_planned_absences_user_date ON planned_absences(user_id, date);
CREATE INDEX idx_prediction_snapshots_user ON prediction_snapshots(user_id, calculation_date);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- ====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ====================================================================
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetables ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE planned_absences ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Dynamic RLS policies for Supabase auth: auth.uid() = user_id
CREATE POLICY "Users can manage own student profile" ON student_profiles FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own subjects" ON subjects FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own timetables" ON timetables FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own attendance records" ON attendance_records FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own planned absences" ON planned_absences FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own prediction snapshots" ON prediction_snapshots FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own notifications" ON notifications FOR ALL USING (auth.uid() = user_id);
