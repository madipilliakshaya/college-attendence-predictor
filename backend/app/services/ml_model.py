import os
import joblib
from typing import Optional, Dict, Any, List
import numpy as np

class MLModelService:
    """
    ML Inference Service for Student Attendance Prediction & Risk Scoring.
    Loads trained scikit-learn models and provides feature attribution.
    """
    _model_bundle = None
    _is_loaded = False

    @classmethod
    def load_model(cls) -> bool:
        if cls._is_loaded and cls._model_bundle is not None:
            return True
        
        bundle_path = os.path.join(os.path.dirname(__file__), "..", "data", "trained_attendance_model.joblib")
        if os.path.exists(bundle_path):
            try:
                cls._model_bundle = joblib.load(bundle_path)
                cls._is_loaded = True
                return True
            except Exception as e:
                print(f"Warning: Could not load ML model bundle: {e}")
                return False
        return False

    @classmethod
    def predict_final_attendance(
        cls,
        current_attendance_pct: float,
        classes_conducted: int,
        classes_attended: int,
        classes_absent: int,
        recent_attendance_pct: float,
        trend_delta: float,
        consecutive_absences: int,
        remaining_classes: int,
        semester_progress: float = 0.5,
        subject_credits: int = 3,
        is_lab: int = 0
    ) -> Optional[float]:
        """
        Runs ML inference to predict final semester attendance.
        Returns None if model is unavailable.
        """
        if not cls.load_model():
            return None

        try:
            import pandas as pd
            regressor = cls._model_bundle["regressor"]
            feature_cols = cls._model_bundle.get("feature_columns", [
                "current_attendance_pct", "classes_conducted", "classes_attended", "classes_absent",
                "recent_attendance_pct", "trend_delta", "consecutive_absences", "remaining_classes",
                "semester_progress", "subject_credits", "is_lab"
            ])
            features_df = pd.DataFrame([[
                current_attendance_pct,
                classes_conducted,
                classes_attended,
                classes_absent,
                recent_attendance_pct,
                trend_delta,
                consecutive_absences,
                remaining_classes,
                semester_progress,
                subject_credits,
                is_lab
            ]], columns=feature_cols)
            pred = float(regressor.predict(features_df)[0])
            return round(min(100.0, max(0.0, pred)), 2)
        except Exception as e:
            print(f"Error during ML inference: {e}")
            return None

    @classmethod
    def get_feature_importances(cls) -> Dict[str, float]:
        if not cls.load_model():
            return {}
        return cls._model_bundle.get("feature_importances", {})
