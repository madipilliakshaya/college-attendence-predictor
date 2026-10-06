# 🎓 College Attendance Predictor

> **BTech IT, Semester 6 — Production-quality attendance intelligence system**  
> Built with Next.js 14, FastAPI, SQLite/PostgreSQL, scikit-learn ML pipeline.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Dashboard** | Live KPI cards — current %, predicted %, safe bunks, classes needed |
| **Subject Analytics** | Per-subject breakdown with risk classification (LOW / MEDIUM / HIGH) |
| **Attendance Tracking** | Mark present/absent, bulk import, monthly calendar view |
| **Timetable Management** | Weekly grid editor + OCR text importer |
| **ML Prediction Engine** | Semester-end forecast with 95% confidence interval, Ridge/RF/GBM comparison |
| **Recovery Planner** | Step-by-step milestone plan to recover from low attendance |
| **Leave Simulator** | What-If slider + multi-day absence impact simulation |
| **Risk Engine** | Transparent multi-factor explainable risk scoring |
| **Notifications** | Auto-generated shortage alerts and recovery reminders |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**

---

### 1. Backend Setup

```powershell
# From project root
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment (optional — SQLite works with no changes)
copy .env.example .env

# Start the API server (from project root)
cd ..
.\backend\venv\Scripts\uvicorn.exe backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The server auto-creates the SQLite database and seeds demo data on first launch.

**Verify**: http://127.0.0.1:8000/health → `{"status": "healthy", ...}`  
**API docs**: http://127.0.0.1:8000/docs

---

### 2. Frontend Setup

```powershell
# In a new terminal, from project root
cd frontend

npm install
npm run dev
```

**App**: http://localhost:3000

---

### 3. Demo Credentials

The backend seeds a demo student automatically. The app works **without login** in demo mode.

| Field | Value |
|---|---|
| Email | `student@college.edu` |
| Password | `student123` |
| Role | BTech IT, Semester 6 |

---

## 🧪 Running Tests

```powershell
# From project root — all 20 tests
.\backend\venv\Scripts\pytest.exe -v

# Quick summary
.\backend\venv\Scripts\pytest.exe -q
```

Expected: **20 passed** ✅

---

## 🤖 ML Pipeline

Pre-trained models are included in `backend/app/data/`. To retrain:

```powershell
# Generate synthetic dataset (1,200 student trajectories)
.\backend\venv\Scripts\python.exe backend\app\data\generate_synthetic_dataset.py

# Train and evaluate models
.\backend\venv\Scripts\python.exe backend\app\data\train_ml_models.py
```

### Model Performance (on held-out test set)

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Ridge Regression | 4.25% | 5.47% | 0.787 |
| Random Forest | — | — | — |
| Gradient Boosting | — | — | — |
| **Risk Classifier (RF)** | Acc: 87.08% | F1: 79.47% | — |

*Full report in `backend/app/data/ml_evaluation_report.json`*

---

## 🏗️ Architecture

```
college-attendance-predictor/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # FastAPI route handlers
│   │   ├── core/               # Config, security, DB, seeding
│   │   ├── models/             # SQLAlchemy ORM + Pydantic schemas
│   │   ├── services/           # Business logic engines
│   │   │   ├── attendance_engine.py
│   │   │   ├── prediction_engine.py
│   │   │   ├── risk_engine.py
│   │   │   ├── recommendation_engine.py
│   │   │   └── simulation_engine.py
│   │   ├── data/               # ML training scripts + artifacts
│   │   └── tests/              # 20 pytest tests (unit + integration)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/app/                # Next.js 14 App Router pages
│       ├── page.tsx            # Dashboard
│       ├── attendance/         # History + Calendar
│       ├── subjects/           # Subject CRUD
│       ├── timetable/          # Weekly grid
│       ├── predict/            # ML forecast
│       ├── simulator/          # What-If + leave planner
│       ├── recovery/           # Recovery milestones
│       ├── analytics/          # Leaderboard + reasons
│       └── settings/           # Profile config
├── database/
│   ├── schema.sql              # PostgreSQL/Supabase DDL with RLS
│   └── seed.sql                # Initial seed data
└── docs/
    ├── ARCHITECTURE.md
    ├── MATHEMATICAL_FORMULATION.md
    └── ML_METHODOLOGY.md
```

---

## 📐 Mathematical Formulation

Core attendance math used throughout the system:

- **Attendance %** = `(classes_attended / total_classes) × 100`
- **Safe bunks** = `floor(total × (current% − target%) / 100)`
- **Classes needed** = `ceil((target% × total − 100 × attended) / (100 − target%))`
- **Max possible %** = `(attended + remaining) / (total + remaining) × 100`
- **Forecast** = behavioral momentum (EMA) blended with ML regression output

Full formulation: [`docs/MATHEMATICAL_FORMULATION.md`](docs/MATHEMATICAL_FORMULATION.md)

---

## 🔒 Security Notes

- JWT RS256 tokens with configurable expiry
- bcrypt password hashing (direct, 72-byte safe truncation)
- CORS restricted to configured origins
- Change `SECRET_KEY` in `.env` before any deployment
- Database RLS policies in `database/schema.sql` for Supabase production

---

## 📚 Documentation

| Document | Description |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design, data flow, component diagram |
| [`docs/MATHEMATICAL_FORMULATION.md`](docs/MATHEMATICAL_FORMULATION.md) | All attendance formulas with derivations |
| [`docs/ML_METHODOLOGY.md`](docs/ML_METHODOLOGY.md) | Feature engineering, model training, evaluation |
| [`database/schema.sql`](database/schema.sql) | PostgreSQL schema with RLS policies |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS 3, lucide-react |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2 |
| Database | SQLite (dev) / PostgreSQL + Supabase (production) |
| ML | scikit-learn (Ridge, Random Forest, Gradient Boosting), pandas, numpy, joblib |
| Auth | JWT (python-jose), bcrypt |
| Testing | pytest, httpx, FastAPI TestClient |

---

*College Attendance Predictor — BTech IT Final Year Project*
