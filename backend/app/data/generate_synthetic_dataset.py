"""
Synthetic Student Attendance Trajectory Dataset Generator.
Explicitly labeled: SYNTHETIC DATASET FOR RESEARCH & PROTOTYPE VALIDATION.
Simulates realistic student attendance trajectories across a standard 15-week college semester.
"""

import numpy as np
import pandas as pd
import random
import os

def generate_synthetic_attendance_dataset(num_samples: int = 1200, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)

    records = []
    for i in range(num_samples):
        # 1. Total semester classes for this subject (e.g. 40 to 60 lectures, or 25 to 35 labs)
        is_lab = np.random.choice([0, 1], p=[0.75, 0.25])
        total_semester_classes = np.random.randint(25, 36) if is_lab else np.random.randint(40, 62)
        credits = 2 if is_lab else np.random.choice([3, 4], p=[0.6, 0.4])

        # 2. Semester progress checkpoint (between 40% and 80% through semester)
        progress = np.random.uniform(0.35, 0.80)
        conducted_so_far = max(8, int(total_semester_classes * progress))
        remaining_classes = total_semester_classes - conducted_so_far

        # 3. Base student attendance archetype:
        # A: Consistent high attender (85-98%)
        # B: Safe borderliner (74-82%)
        # C: Chronic bunk/struggling (55-73%)
        # D: Recovering student (improving after poor start)
        # E: Slipping student (declining after strong start)
        archetype = np.random.choice(["high", "borderline", "struggling", "recovering", "declining"], p=[0.40, 0.25, 0.15, 0.10, 0.10])

        if archetype == "high":
            base_p = np.random.uniform(0.85, 0.98)
            future_p = np.random.uniform(0.82, 0.98)
            recent_p = np.random.uniform(0.85, 1.0)
        elif archetype == "borderline":
            base_p = np.random.uniform(0.72, 0.80)
            future_p = np.random.uniform(0.70, 0.82)
            recent_p = np.random.uniform(0.65, 0.85)
        elif archetype == "struggling":
            base_p = np.random.uniform(0.50, 0.72)
            future_p = np.random.uniform(0.50, 0.73)
            recent_p = np.random.uniform(0.40, 0.70)
        elif archetype == "recovering":
            base_p = np.random.uniform(0.60, 0.73)
            future_p = np.random.uniform(0.80, 0.95)
            recent_p = np.random.uniform(0.80, 0.95)
        else: # declining
            base_p = np.random.uniform(0.80, 0.92)
            future_p = np.random.uniform(0.55, 0.72)
            recent_p = np.random.uniform(0.50, 0.68)

        # Attended so far
        attended_so_far = min(conducted_so_far, np.random.binomial(conducted_so_far, base_p))
        absent_so_far = conducted_so_far - attended_so_far
        current_pct = round((attended_so_far / conducted_so_far) * 100.0, 2)

        # Recent 2-week attendance
        recent_conducted = min(conducted_so_far, max(4, int(conducted_so_far * 0.3)))
        recent_attended = min(recent_conducted, np.random.binomial(recent_conducted, recent_p))
        recent_pct = round((recent_attended / recent_conducted) * 100.0, 2)
        trend_delta = round(recent_pct - current_pct, 2)

        # Consecutive absences in recent window
        if recent_pct < 60:
            consecutive_abs = np.random.randint(2, 6)
        else:
            consecutive_abs = np.random.choice([0, 1], p=[0.7, 0.3])

        # Actual future classes attended in remainder of semester
        future_attended = np.random.binomial(remaining_classes, future_p)
        final_attended = attended_so_far + future_attended
        final_pct = round((final_attended / total_semester_classes) * 100.0, 2)
        shortage_risk = 1 if final_pct < 75.0 else 0

        records.append({
            "sample_id": f"SYN_{i+1:04d}",
            "is_lab": is_lab,
            "subject_credits": credits,
            "total_semester_classes": total_semester_classes,
            "classes_conducted": conducted_so_far,
            "classes_attended": attended_so_far,
            "classes_absent": absent_so_far,
            "remaining_classes": remaining_classes,
            "semester_progress": round(progress, 3),
            "current_attendance_pct": current_pct,
            "recent_attendance_pct": recent_pct,
            "trend_delta": trend_delta,
            "consecutive_absences": consecutive_absences if 'consecutive_absences' in locals() else consecutive_abs,
            "final_semester_attendance_pct": final_pct,
            "shortage_risk_label": shortage_risk,
            "dataset_origin": "synthetic_research_model"
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_synthetic_attendance_dataset()
    output_path = os.path.join(os.path.dirname(__file__), "synthetic_attendance_dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic records saved to {output_path}")
    print(df.head())
