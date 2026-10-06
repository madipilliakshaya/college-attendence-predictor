"""
ML Training, Comparison & Evaluation Pipeline.
Trains and compares:
1. Baseline Linear/Ridge Regression
2. Random Forest Regressor
3. Gradient Boosting Regressor

Computes verified test metrics (MAE, RMSE, R2, Accuracy, Precision, Recall, F1)
and saves the trained model bundle and evaluation report.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)
from generate_synthetic_dataset import generate_synthetic_attendance_dataset

FEATURE_COLUMNS = [
    "current_attendance_pct",
    "classes_conducted",
    "classes_attended",
    "classes_absent",
    "recent_attendance_pct",
    "trend_delta",
    "consecutive_absences",
    "remaining_classes",
    "semester_progress",
    "subject_credits",
    "is_lab"
]

def train_and_evaluate():
    data_dir = os.path.dirname(__file__)
    csv_path = os.path.join(data_dir, "synthetic_attendance_dataset.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = generate_synthetic_attendance_dataset()
        df.to_csv(csv_path, index=False)

    X = df[FEATURE_COLUMNS]
    y_reg = df["final_semester_attendance_pct"]
    y_clf = df["shortage_risk_label"]

    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, random_state=42
    )

    models_reg = {
        "Ridge_Regression_Baseline": Ridge(alpha=1.0),
        "Random_Forest_Regressor": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
        "Gradient_Boosting_Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
    }

    results = {}
    best_model_name = None
    best_mae = float("inf")

    for name, model in models_reg.items():
        model.fit(X_train, y_reg_train)
        preds = model.predict(X_test)
        
        mae = float(mean_absolute_error(y_reg_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_reg_test, preds)))
        r2 = float(r2_score(y_reg_test, preds))
        
        results[name] = {
            "MAE": round(mae, 3),
            "RMSE": round(rmse, 3),
            "R2": round(r2, 4)
        }
        
        if mae < best_mae:
            best_mae = mae
            best_model_name = name

    # Train risk classifier
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_clf_train)
    clf_preds = clf.predict(X_test)

    clf_metrics = {
        "Accuracy": round(float(accuracy_score(y_clf_test, clf_preds)), 4),
        "Precision": round(float(precision_score(y_clf_test, clf_preds)), 4),
        "Recall": round(float(recall_score(y_clf_test, clf_preds)), 4),
        "F1_Score": round(float(f1_score(y_clf_test, clf_preds)), 4),
        "Confusion_Matrix": confusion_matrix(y_clf_test, clf_preds).tolist()
    }

    best_reg_model = models_reg[best_model_name]
    
    # Feature importances
    feature_importances = {}
    if hasattr(best_reg_model, "feature_importances_"):
        for col, imp in zip(FEATURE_COLUMNS, best_reg_model.feature_importances_):
            feature_importances[col] = round(float(imp), 4)

    # Save artifact bundle
    bundle = {
        "regressor": best_reg_model,
        "classifier": clf,
        "best_model_name": best_model_name,
        "feature_columns": FEATURE_COLUMNS,
        "feature_importances": feature_importances,
        "trained_date": "2026-10-05"
    }
    model_bundle_path = os.path.join(data_dir, "trained_attendance_model.joblib")
    joblib.dump(bundle, model_bundle_path)

    # Evaluation report
    report = {
        "dataset_info": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "origin": "Synthetic Dataset (Explicitly Labeled) simulating 15-week college semester",
            "features": FEATURE_COLUMNS
        },
        "regression_model_comparison": results,
        "best_regression_model": best_model_name,
        "risk_classification_metrics": clf_metrics,
        "feature_importances": feature_importances
    }

    report_path = os.path.join(data_dir, "ml_evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("=== Model Training & Evaluation Complete ===")
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    train_and_evaluate()
