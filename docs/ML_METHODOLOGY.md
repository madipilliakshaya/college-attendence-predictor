# College Attendance Predictor: Machine Learning Methodology & Evaluation

## 1. Ethical & Academic Integrity Statement

In strict accordance with academic integrity requirements:
- **Dataset Disclosure**: The ML pipeline is trained and evaluated on a documented, reproducible synthetic dataset simulating realistic student attendance trajectories across a standard 15-week college semester ($N = 1,200$ student-subject trajectories).
- **No Fabricated Performance**: All reported metrics (MAE, RMSE, $R^2$, Accuracy, Precision, Recall, F1) are genuinely computed on a 20% held-out test set ($N_{\text{test}} = 240$) using `scikit-learn`.
- **Deterministic Separation**: Mathematical operations (current %, safe-bunk count, classes-needed count, and absolute physical boundaries) are strictly deterministic and never masked as "AI".

---

## 2. Feature Engineering

| Feature | Type | Description |
|---|---|---|
| `current_attendance_pct` | Float ($0-100$) | Current percentage at checkpoint |
| `classes_conducted` | Integer | Total classes conducted to date |
| `classes_attended` | Integer | Total classes attended to date |
| `classes_absent` | Integer | Total classes missed to date |
| `recent_attendance_pct` | Float ($0-100$) | Attendance rate over recent 14-day window |
| `trend_delta` | Float | Momentum indicator ($\text{recent} - \text{current}$) |
| `consecutive_absences` | Integer | Maximum run of consecutive recent absences |
| `remaining_classes` | Integer | Future scheduled classes derived from weekly timetable |
| `semester_progress` | Float ($0-1$) | Fraction of total semester completed |
| `subject_credits` | Integer | Academic weight of course (2, 3, or 4) |
| `is_lab` | Binary ($0/1$) | Class type indicator (lecture vs laboratory) |

---

## 3. Regression Model Comparison (Test Set Evaluation)

| Candidate Model | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Score | Evaluation Result |
|---|---|---|---|---|
| **Ridge Regression (Baseline)** | **4.254%** | **5.471%** | **0.7871** | **Best Generalization** |
| Random Forest Regressor | 4.643% | 6.374% | 0.7110 | Benchmark |
| Gradient Boosting Regressor | 4.681% | 6.301% | 0.7176 | Benchmark |

---

## 4. Shortage Risk Classification Metrics (Held-Out Test Set)

Target: Binary Shortage Risk ($\text{final} < 75.0\%$):
- **Accuracy**: $87.08\%$
- **Precision**: $88.24\%$
- **Recall**: $72.29\%$
- **F1-Score**: $79.47\%$
- **Confusion Matrix**:
  - True Negatives (Safe): 149
  - False Positives: 8
  - False Negatives: 23
  - True Positives (Shortage Detected): 60

---

## 5. Uncertainty & Confidence Bounds

Predictions are never communicated as absolute certainties. The system calculates a 95% confidence interval using the standard error of binomial proportion of future sessions:

$$\text{Margin of Error} = 1.96 \cdot \sqrt{\frac{p(1-p)}{\max(1, R)}} \cdot \left(\frac{R}{C + R}\right) \times 100$$

Confidence score increases as semester progress ratio $\frac{C}{C + R}$ approaches 1.0.
