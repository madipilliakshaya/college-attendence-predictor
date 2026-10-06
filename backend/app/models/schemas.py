from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

# ----------------- Auth & User Schemas -----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "student"

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Profile Schemas -----------------
class StudentProfileBase(BaseModel):
    roll_number: str
    department: str = "Information Technology"
    semester: int = 6
    college_name: str = "Engineering College"
    default_attendance_target: float = 75.0
    semester_start_date: date
    semester_end_date: date

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileUpdate(BaseModel):
    roll_number: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    college_name: Optional[str] = None
    default_attendance_target: Optional[float] = None
    semester_start_date: Optional[date] = None
    semester_end_date: Optional[date] = None

class StudentProfileOut(StudentProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ----------------- Subject Schemas -----------------
class SubjectBase(BaseModel):
    code: str
    name: str
    subject_type: str = "lecture" # lecture, lab, tutorial, practical, extra
    credits: int = 3
    duration_hours: float = 1.0
    target_percentage: float = 75.0
    color: str = "#3B82F6"

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    subject_type: Optional[str] = None
    credits: Optional[int] = None
    duration_hours: Optional[float] = None
    target_percentage: Optional[float] = None
    color: Optional[str] = None

class SubjectOut(SubjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ----------------- Timetable Schemas -----------------
class TimetableBase(BaseModel):
    subject_id: str
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    room: Optional[str] = None
    periods_count: int = Field(default=1, ge=1)

class TimetableCreate(TimetableBase):
    pass

class TimetableOut(TimetableBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Attendance Record Schemas -----------------
class AttendanceRecordBase(BaseModel):
    subject_id: str
    date: date
    status: str = Field(..., pattern=r"^(present|absent|cancelled)$")
    periods_count: int = Field(default=1, ge=1)
    reason_category: str = Field(default="none", pattern=r"^(none|illness|college_event|personal|approved_leave|other)$")
    notes: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordBulkCreate(BaseModel):
    date: date
    records: List[AttendanceRecordBase]

class AttendanceRecordOut(AttendanceRecordBase):
    id: str
    user_id: str
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ----------------- Planned Absence Schemas -----------------
class PlannedAbsenceBase(BaseModel):
    subject_id: Optional[str] = None # None means all day
    date: date
    periods_count: int = 1
    reason: Optional[str] = None

class PlannedAbsenceCreate(PlannedAbsenceBase):
    pass

class PlannedAbsenceOut(PlannedAbsenceBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Computation & Analytics Schemas -----------------
class SubjectAttendanceStats(BaseModel):
    subject_id: str
    subject_code: str
    subject_name: str
    subject_type: str
    credits: int
    color: str
    target_percentage: float
    classes_conducted: int
    classes_attended: int
    classes_absent: int
    classes_cancelled: int
    current_percentage: float
    is_shortage: bool
    safe_bunks: int
    classes_needed: int
    remaining_classes_semester: int
    predicted_final_percentage: float
    risk_level: str # LOW, MEDIUM, HIGH
    projected_shortage_date: Optional[date] = None

class OverallAttendanceStats(BaseModel):
    total_conducted: int
    total_attended: int
    total_absent: int
    current_percentage: float
    target_percentage: float
    weighted_percentage: float
    is_shortage: bool
    safe_bunks: int
    classes_needed: int
    total_remaining_classes: int
    predicted_final_percentage: float
    prediction_confidence: float
    confidence_interval_low: float
    confidence_interval_high: float
    overall_risk_level: str # LOW, MEDIUM, HIGH
    projected_shortage_date: Optional[date] = None
    recovery_possible: bool = True
    max_possible_final_percentage: float

class WhatIfRequest(BaseModel):
    subject_id: Optional[str] = None # None for overall
    miss_classes: int = Field(default=0, ge=0)
    attend_classes: int = Field(default=0, ge=0)

class WhatIfResult(BaseModel):
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None
    current_percentage: float
    simulated_percentage: float
    percentage_change: float
    target_percentage: float
    is_target_met: bool
    new_safe_bunks: int
    new_classes_needed: int
    new_risk_level: str

class AbsenceSimulationRequest(BaseModel):
    dates: List[date]
    reason: Optional[str] = "Planned Leave"

class AbsenceSimulationResult(BaseModel):
    dates_simulated: List[date]
    total_periods_missed: int
    impacted_subjects: List[dict]
    overall_current_percentage: float
    overall_projected_percentage: float
    overall_target_percentage: float
    target_breached: bool
    recovery_classes_needed_after_leave: int
    risk_summary: str

class RecoveryPlanStep(BaseModel):
    step_number: int
    milestone_name: str
    consecutive_classes_to_attend: int
    expected_attendance_percentage: float
    target_percentage: float
    target_achieved: bool
    notes: str

class RecoveryPlan(BaseModel):
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None
    current_percentage: float
    target_percentage: float
    classes_needed: int
    remaining_classes_in_semester: int
    is_achievable: bool
    max_achievable_percentage: float
    steps: List[RecoveryPlanStep]
    action_items: List[str]

class NotificationOut(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str] = None
    title: str
    message: str
    alert_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    student_name: str = ""
    student_profile: StudentProfileOut
    overall: OverallAttendanceStats
    subjects: List[SubjectAttendanceStats]
    recent_notifications: List[NotificationOut]
    upcoming_classes_today: List[dict]
    trend_data: List[dict]
    explanation_factors: List[str]
