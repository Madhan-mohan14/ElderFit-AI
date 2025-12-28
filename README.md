# 👵 ElderFit AI  
### *Agentic Wellness Assistant for the Elderly*  
**Innov-AI-tion Problem Statement: Agentic Systems for Healthcare & Fitness**

A **nutrition-first, mood-aware, elder-focused** wellness assistant built using a **multi-agent neuro-symbolic system** that autonomously **plans, reasons, acts, and adapts** using free-tier APIs and lightweight ML.

> ⚠ **Safety scope:** Wellness and habit coaching only — **No medical diagnosis, no treatment, no prescriptions**.  
> All outputs are **constraint-aware, transparent, and auditable**.

---

## ❗ Problem We Solve (Challenge Alignment)

Elderly users (45–90) struggle with:
- generic diet plans that ignore **appetite, mood, and fatigue**
- exercise suggestions that are **not elder-safe**
- lack of personalization based on **past feedback**
- no transparency on **why a plan was selected**
- API quota bias in free-tier wellness tools

**ElderFit AI addresses this** by demonstrating true **agentic behavior**:
✔ Sets long-term wellness goals  
✔ Generates multi-step nutrition + exercise plans  
✔ Makes autonomous decisions under constraints (sleep, mood, appetite, ingredients, dislikes)  
✔ Interacts meaningfully with free-tier tools (nutrients + videos)  
✔ Learns using **memory-driven adaptation** (associative recall)  
✔ Shows every decision transparently via **trace logs**  

:contentReference[oaicite:0]{index=0}

---

## 🧠 Agent Architecture (ML + Symbolic Core)

| Agent | Role |
|---|---|
| **Observe Agent** | Collects & validates check-in data (sleep, mood, appetite, ingredients, adherence, quiz) |
| **Reasoner Agent (NSMR Core)** | Applies symbolic wellness rules + constraints, queries memory, integrates ML signals |
| **ML Predictor** | Classifies **fatigue & appetite** into Low / Normal / High to guide plan intensity |
| **Nutrition Agent** | Nutrient lookup (USDA), generates Sattvic + elder-friendly recipes, swaps meals based on dislikes |
| **Yoga/Exercise Agent** | Creates **gentle daily & weekly yoga/exercise plans**, fetches YouTube video suggestions |
| **Fairness Agent** | Prevents quota bias, ensures balanced API usage for fair recommendations |
| **Report Agent** | Weekly & monthly **progress summaries**, barrier tracking, next-week strategy |

> The system **reasons and acts**, not just predicts. Model performance is secondary to agent autonomy.

---

## 🚀 Features

- **Agentic System Loop**: Observe → Reason → Plan → Act → Reflect → Replan
- **Nutrition-First Planning**: Age-aware meals, Sattvic-aligned, caregiver-friendly
- **Elder-Safe Exercise Recommendations**: Short or gentle yoga sessions when fatigue is high
- **Associative Memory**: Recalls likes/dislikes and successful past plans
- **Decision Transparency Viewer**: Shows triggered rules, memory hits, and API/tool usage
- **Multilingual Support**: English • Hindi • Telugu
- **Professional UI**: Responsive SaaS-style dashboard with progress analytics

---

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- **Free-Tier API Keys Provided by Team**:
  - OpenAI (LLM reasoning + recipe generation)
  - USDA FoodData Central (nutrient lookup)
  - YouTube Data API (exercise & meditation videos)
  - Google Calendar (optional scheduling, already supported but not required)

---

## 🛠️ Installation & Run

### Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run backend server
# ⚠️ IMPORTANT: Make sure you're in the project root directory (not in frontend/ or backend/)

# Manual start (must be in project root)
# Make sure you're in the project root: D:\STUDY\Projects\IITH ELDERAI\
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Verify it's working:
# Open http://localhost:8000/docs in your browser
# You should see the FastAPI documentation page
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend
npm install
npm start
# or
npm run dev
```

### Access URLs
Frontend: http://localhost:3000

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
.
├── backend/
│   ├── agents/       # Observe, Reasoner, Nutrition, Exercise, Fairness, Report, ML Predictor
│   ├── models/       # ORM Data Models & Pydantic Schemas
│   ├── services/     # External Free-Tier API Connectors (USDA, YouTube, OpenAI, GCal)
│   └── main.py       # FastAPI Application Entry Point
├── frontend/         # Vite + React UI
│   ├── src/
│   │   ├── components/  # React Components
│   │   ├── utils/       # API utilities
│   │   └── App.jsx      # Main App Component
├── logs/             # Decision Trace Logs (Audit-Friendly)
└── requirements.txt  # Python dependencies
```
## ⚠️ Important Notes
This is a wellness system, not a medical system

No diagnosis or treatment is provided

Designed for elders (45–90) and caregivers

All APIs used are free-tier and team-provided

Personalization relies on daily check-in honesty

Decision trace logs ensure audit-friendly evaluation

Avoids quota bias using a fairness agent

## 🔮 Future Scope
Wearable data input integration (HR, steps, sleep)

Calendar scheduling + reminders (already supported optionally)

Larger ML training for cross-dataset generalization

Recipe image generation and simplicity scoring

Group wellness challenges with shared-tool fairness

More UI language personalization for elder comfort

