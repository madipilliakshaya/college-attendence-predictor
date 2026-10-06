import pytest
from app.services.risk_engine import RiskEngine
from app.services.recommendation_engine import RecommendationEngine

def test_risk_classification_high_when_below_target():
    risk = RiskEngine.evaluate_risk(
        current_percentage=68.0,
        target_percentage=75.0,
        safe_bunks=0,
        classes_needed=7,
        remaining_classes=15,
        predicted_percentage=70.0
    )
    assert risk["risk_level"] == "HIGH"
    assert len(risk["factors"]) > 0
    # Factors should mention below target
    assert any("below your required target" in f for f in risk["factors"])

def test_risk_classification_low_when_healthy():
    risk = RiskEngine.evaluate_risk(
        current_percentage=88.0,
        target_percentage=75.0,
        safe_bunks=6,
        classes_needed=0,
        remaining_classes=20,
        predicted_percentage=86.0
    )
    assert risk["risk_level"] == "LOW"
    assert any("Healthy attendance buffer" in f for f in risk["factors"])

def test_recovery_plan_achievable():
    # 18 attended out of 26 = 69.23%. Target = 75%. Classes needed = 6. Remaining = 14.
    plan = RecommendationEngine.generate_recovery_plan(
        subject_id="test-sub-1",
        subject_name="Database Systems",
        attended=18,
        conducted=26,
        target_percentage=75.0,
        remaining_classes=14
    )
    assert plan["is_achievable"] is True
    assert plan["classes_needed"] == 6
    assert len(plan["steps"]) >= 2
    # Last step should achieve target
    assert plan["steps"][-1]["target_achieved"] is True

def test_recovery_plan_unachievable():
    # 10 attended out of 25 = 40.0%. Target = 75%. Remaining = 5.
    # Total final = 30. Max attended = 15. Max % = 50% < 75%.
    plan = RecommendationEngine.generate_recovery_plan(
        subject_id="test-sub-2",
        subject_name="Physics",
        attended=10,
        conducted=25,
        target_percentage=75.0,
        remaining_classes=5
    )
    assert plan["is_achievable"] is False
    assert plan["max_achievable_percentage"] == 50.0
    assert any("impossible" in a.lower() for a in plan["action_items"])
