# College Attendance Predictor: Architecture & System Design

## 1. Architectural Baseline

The system is constructed with strict separation of concerns across three core architectural tiers:

```
[ Next.js 14+ (TypeScript App Router) ]
                ↕  REST JSON API
[ Python FastAPI Backend Engine ]
        ├── Attendance Engine (Deterministic Mathematics)
        ├── Timetable Engine (Schedule Projections)
        ├── Prediction Engine (Baseline & Confidence Interval)
        ├── Machine Learning Pipeline (Scikit-Learn Regression & Classification)
        ├── Risk Engine (Multi-Factor Explainable Scoring)
        ├── Simulation Engine (What-If & Multi-Day Leave Impact)
        └── Recommendation Engine (Actionable Milestones)
                ↕  SQLAlchemy ORM / SQL Migrations
[ PostgreSQL / Supabase Relational Database ]
```

---

## 2. Responsibilities & Boundaries

### Frontend (Next.js 14 + TypeScript)
- **Role**: Presentation, user interaction, client-side validation, routing, responsive UX.
- **Boundaries**: Strictly non-authoritative for business calculations. All safe-bunk, classes-needed, risk scores, forecasts, and recovery milestones are computed authoritatively by the Python backend.

### Backend (Python FastAPI)
- **Role**: Authoritative business logic, mathematical computations, timetable remaining class derivation, ML inference, risk classification, and transactional orchestration.
- **Modules**:
  - `AttendanceEngine`: Pure deterministic attendance percentages, safe bunks, classes needed.
  - `TimetableEngine`: Calendar schedule mapping, clash detection, remaining period calculations.
  - `PredictionEngine`: Trend-aware forecasting, confidence bounds, projected shortage date calculations.
  - `MLModelService`: Scikit-learn model loading, feature vector inference, model comparison.
  - `RiskEngine`: Explainable risk scoring (LOW, MEDIUM, HIGH) with human-readable attribution factors.
  - `RecommendationEngine`: Actionable recovery milestones and personalized directives.
  - `SimulationEngine`: What-If simulator and multi-day leave impact against scheduled timetables.

### Persistence (PostgreSQL / Supabase + SQLite fallback)
- **Role**: Relational integrity, foreign key cascades, check constraints, row-level security (RLS) policies, and performance indexes.
- **Zero-config Dual Mode**: Automatically connects to Supabase/PostgreSQL when credentials are provided in `.env`, or seamlessly initializes local SQLite for instant out-of-the-box local operation and CI testing.

---

## 3. Data Flow Diagram

```
User Action (e.g. Mark Class or Run What-If)
       │
       ▼
Next.js Client (lib/api.ts)
       │
       ▼  HTTP Request (/api/v1/...)
FastAPI Route Controller
       │
       ├── Reads DB Session (SQLAlchemy)
       │
       ├── Evaluates Timetable Schedule (TimetableEngine)
       │
       ├── Computes Attendance Bounds (AttendanceEngine)
       │
       ├── Generates ML Forecast (MLModelService)
       │
       ├── Assesses Multi-Factor Risk (RiskEngine)
       │
       ▼
JSON Response with Explainable Factors & Recommendations
       │
       ▼
Next.js Component Render (Accessible Badges, Alerts, Gauges)
```
