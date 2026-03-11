# FairFlow 🚚⚖️

### AI-Powered Fair Dispatch System for Logistics

FairFlow is a fairness-aware route assignment system designed to ensure
**balanced workload distribution among delivery drivers**. Instead of
optimizing only distance and delivery speed, FairFlow focuses on
**long-term fairness**, preventing driver burnout and improving
workforce sustainability using effort scoring, fairness ledger tracking,
drift detection AI, and ML-based route recommendations.

---

# Problem

Modern logistics routing systems optimize:

- Distance
- Fuel consumption
- Delivery time

However, they ignore **human fairness**.

This leads to:

- Some drivers repeatedly receiving harder routes
- Driver fatigue and burnout
- Reduced morale
- High driver attrition costs for companies

FairFlow solves this by introducing **fairness intelligence into dispatch systems**.

---

# Solution

FairFlow introduces a **three-layer fairness architecture**.

## 1️⃣ Fairness Ledger

Tracks driver workload history and assigns fairness credits based on effort.

## 2️⃣ Fairness Drift AI

Monitors workload distribution over time using a **7-day sliding window** and detects imbalance.

## 3️⃣ ML Recommendation Engine

Suggests route difficulty assignments while ensuring fairness constraints.

Together, these layers ensure **fair, transparent, and sustainable route assignments**.

---

# System Architecture

```
Route Data
↓
Effort Score Calculation
↓
Team Average Calculation
↓
Fairness Ledger (Credits System)
↓
Fairness Drift Detection AI
↓
ML Recommendation Engine
↓
Final Route Assignment
```

---

# Key Features

- Effort-based route difficulty scoring
- Fairness credit ledger system
- Sliding-window fairness drift detection
- AI-based route recommendation
- Explainable route assignment decisions
- Driver feedback integration
- Real-time fairness monitoring

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- JWT Authentication

## Frontend

- React
- Vite
- JavaScript
- CSS

## AI / ML

- Rule-based explainable ML
- Effort scoring model
- Fairness drift detection algorithm

## Database

- SQLite (Development)
- PostgreSQL (Production Ready)

---

# Running the Project

## Backend

```bash
cd backend
dir main.py
uvicorn main:app --reload --port 8000
```

Backend will run at:

```
http://localhost:8000
```

API documentation available at:

```
http://localhost:8000/docs
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at:

```
http://localhost:5173
```

---

# Example Scenario

## Without FairFlow

Driver A repeatedly receives apartment-heavy routes while Driver B receives easier suburban routes.

Result:

- Driver A becomes overloaded
- Burnout occurs
- Driver resigns

## With FairFlow

- System tracks workload history
- Detects fairness drift
- Redistributes routes fairly

Result:

- Balanced workload
- Reduced burnout
- Higher driver retention

---

# Business Impact

Using FairFlow, logistics companies can achieve:

- Reduced driver attrition
- Improved driver morale
- Transparent route assignments
- Lower recruitment and training costs
- Sustainable workforce management

---

# Project Structure

```
fairflow
│
├── backend
│   ├── main.py
│   ├── models.py
│   ├── logic.py
│   ├── fairness_drift.py
│   ├── ml_recommendation.py
│   └── database.py
│
├── frontend
│   ├── src
│   ├── components
│   └── pages
│
├── assets
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Innovation

FairFlow introduces **fairness memory** into logistics dispatch systems.

Traditional systems ask:

> "What is the fastest route?"

FairFlow asks:

> **"What is the fairest workload over time?"**

---

# License

MIT License