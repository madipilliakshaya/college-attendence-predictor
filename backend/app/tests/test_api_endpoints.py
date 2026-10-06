import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.core.init_db import init_db_with_seed_data

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        init_db_with_seed_data(db)
    yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_dashboard_endpoint(client):
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "student_profile" in data
    assert "overall" in data
    assert "subjects" in data
    assert len(data["subjects"]) > 0
    assert "current_percentage" in data["overall"]
    assert "predicted_final_percentage" in data["overall"]
    assert "overall_risk_level" in data["overall"]

def test_subjects_stats_endpoint(client):
    response = client.get("/api/v1/subjects/stats")
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) >= 6
    # Look for DBMS subject
    dbms = next((s for s in subjects if s["subject_code"] == "CS602"), None)
    assert dbms is not None
    assert dbms["current_percentage"] < 75.0
    assert dbms["risk_level"] == "HIGH"
    assert dbms["classes_needed"] > 0

def test_what_if_simulation_api(client):
    payload = {
        "miss_classes": 2,
        "attend_classes": 1
    }
    response = client.post("/api/v1/simulation/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "simulated_percentage" in data
    assert "percentage_change" in data
    assert "new_safe_bunks" in data

def test_absence_simulation_api(client):
    payload = {
        "dates": ["2026-10-12", "2026-10-13"],
        "reason": "Family Function"
    }
    response = client.post("/api/v1/simulation/absence-simulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_periods_missed" in data
    assert "impacted_subjects" in data
    assert len(data["impacted_subjects"]) > 0

def test_predictions_forecast_api(client):
    response = client.get("/api/v1/predictions/forecast")
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert "confidence_score" in data["overall"]
    assert "confidence_interval_low" in data["overall"]
    assert "confidence_interval_high" in data["overall"]

def test_ml_metrics_api(client):
    response = client.get("/api/v1/predictions/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "regression_model_comparison" in data
    assert "risk_classification_metrics" in data
