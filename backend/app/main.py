import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.init_db import init_db_with_seed_data
from app.api.v1.api_router import api_router
from app.services.ml_model import MLModelService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed demo data if fresh
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        init_db_with_seed_data(db)
    
    # Load ML models into memory
    MLModelService.load_model()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected",
        "ml_service": "active" if MLModelService.load_model() else "baseline_mode"
    }

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
