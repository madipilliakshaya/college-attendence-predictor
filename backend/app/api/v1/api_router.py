from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, profile, subjects, attendance, timetable, predictions, simulation, notifications, analytics
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["Student Profile"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance Records"])
api_router.include_router(timetable.router, prefix="/timetable", tags=["Timetable"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions & Forecasting"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["What-If & Simulation"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications & Alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Dashboard"])
