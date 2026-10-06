import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "College Attendance Predictor"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # Defaults to SQLite local file for zero-config out-of-the-box operation and testing,
    # or overrides via DATABASE_URL or SUPABASE_DB_URL with PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./attendance_predictor.db")
    
    # Supabase optional direct client configs
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "btech_attendance_predictor_secret_key_2026_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000"
    ]
    
    # Default College Attendance Rules
    DEFAULT_ATTENDANCE_TARGET: float = 75.0
    HIGH_RISK_THRESHOLD: float = 75.0
    MEDIUM_RISK_BUFFER: float = 5.0 # within 5% of target or <= 2 safe bunks
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
