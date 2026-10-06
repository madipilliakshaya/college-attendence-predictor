import uuid
from datetime import datetime, date, time
from sqlalchemy import (
    Column, String, Integer, Float, Date, Time, DateTime,
    Boolean, ForeignKey, Text, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(String(50), default="student", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="user", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="user", cascade="all, delete-orphan")
    planned_absences = relationship("PlannedAbsence", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("PredictionSnapshot", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    roll_number = Column(String(100), nullable=False)
    department = Column(String(100), default="Information Technology", nullable=False)
    semester = Column(Integer, default=6, nullable=False)
    college_name = Column(String(255), default="Engineering College", nullable=False)
    default_attendance_target = Column(Float, default=75.0, nullable=False)
    semester_start_date = Column(Date, nullable=False)
    semester_end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    subject_type = Column(String(50), default="lecture", nullable=False) # lecture, lab, tutorial, practical, extra
    credits = Column(Integer, default=3, nullable=False)
    duration_hours = Column(Float, default=1.0, nullable=False)
    target_percentage = Column(Float, default=75.0, nullable=False)
    color = Column(String(20), default="#3B82F6", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "code", name="uq_user_subject_code"),
    )

    user = relationship("User", back_populates="subjects")
    timetables = relationship("Timetable", back_populates="subject", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")


class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False) # 0=Monday, 6=Sunday
    start_time = Column(String(10), nullable=False) # "09:00"
    end_time = Column(String(10), nullable=False)   # "10:00"
    room = Column(String(50), nullable=True)
    periods_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="timetables")
    subject = relationship("Subject", back_populates="timetables")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False) # present, absent, cancelled
    periods_count = Column(Integer, default=1, nullable=False)
    reason_category = Column(String(50), default="none", nullable=False) # none, illness, college_event, personal, approved_leave, other
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")


class PlannedAbsence(Base):
    __tablename__ = "planned_absences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    periods_count = Column(Integer, default=1, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="planned_absences")


class PredictionSnapshot(Base):
    __tablename__ = "prediction_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)
    calculation_date = Column(Date, default=date.today, nullable=False)
    current_percentage = Column(Float, nullable=False)
    predicted_percentage = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    confidence_interval_low = Column(Float, nullable=False)
    confidence_interval_high = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False) # LOW, MEDIUM, HIGH
    projected_shortage_date = Column(Date, nullable=True)
    recommendation_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String(50), nullable=False) # shortage, projected_shortage, high_risk, recovery_needed, warning, info
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
