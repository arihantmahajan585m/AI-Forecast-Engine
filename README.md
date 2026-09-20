# ⚡ LegitsIQ-AI-Forecast
### Autonomous Pipeline Revenue Forecasting & Deal-Risk Agent
**Track D · D4 — Sales, Growth & Revenue Agents (Advanced)**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/LLM-Groq%20High--Speed-f55036.svg)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_Store-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![React 19](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Executive Summary

B2B sales forecasts are notoriously broken: **over 68% of enterprise sales forecasts are built on rep gut-feeling and optimism rather than empirical signals**. High-value deals slip silently when key stakeholders disengage, champions depart, or legal review stalls — and sales leadership only discovers the shortfall in the final weeks of the quarter.

**LegitsIQ-AI-Forecast** replaces static spreadsheets and subjective estimates with an autonomous revenue intelligence agent. Built on **LangGraph**, **Monte Carlo probabilistic simulations (4,000 runs)**, and **grounded RAG playbooks**, LegitsIQ pinpoints deal risks, predicts empirical revenue confidence intervals (P10/P50/P90), and generates traceable next-best-actions with source citations.

> 🏆 **Compulsory Feature 7 Verified**: On a blind holdout quarter (**2026-Q1**), LegitsIQ’s probabilistic engine achieved **23.56% APE** vs human sales reps' **90.71% APE**, **outperforming rep intuition by +67.15 percentage points**.

---

## 🚀 Key Features (Track D · D4 Requirements)

| # | Feature | Description | Architecture / Engine |
|---|---|---|---|
| **1** | **Structured CRM Ingestion** | Ingestion of deals with stage, amount, close date, recency, stakeholders, and engagement history. Supports one-click CSV uploads. | `pandas`, `validate_deals_frame()`, FastAPI `/api/upload` |
| **2** | **6-Signal Risk Engine** | Quantifiable deal risk scoring (0.00 – 1.00) with transparent evidence tags — eliminates vague *"this deal looks risky"* warnings. | Multi-signal heuristic matrix (`risk.py`): stalled activity, stage overage, missing economic buyer, engagement drop, zero-touch, enterprise exposure. |
| **3** | **Probabilistic Forecasting** | Generates confidence intervals (**P10 Bear, P50 Base, P90 Bull**) rather than a single point guess. | 4,000 Monte Carlo sampling iterations over deal-level win probabilities haircutted by risk scores (`forecast.py`). |
| **4** | **Next-Best-Action RAG** | Prescribes specific salvage actions for at-risk accounts grounded in battle-tested sales playbooks with citation tags like `[C1]`, `[C2]`. | Local ChromaDB vector store (216 indexed chunks) + `sentence-transformers` + Groq LLM reasoning. |
| **5** | **Monday Briefing Dashboard** | Executive leadership view synthesizing forecast bands, at-risk accounts, and action recommendations with a live AI narrative. | React 19 + Recharts + Groq `openai/gpt-oss-120b` CRO synthesizer. |
| **6** | **What-If Commit Simulator** | Interactive slider allowing sales leaders to simulate revenue salvage scenarios before assigning engineering or exec resources. | Re-runs Monte Carlo simulation post-intervention to calculate expected P50 revenue lift (`simulate.py`). |
| **7** | **Compulsory Holdout Backtest** | Proves forecast reasonableness by backtesting against historical ground-truth actuals and sales rep committed forecasts. | `forecast_closed_quarter_as_of()` + rep accuracy calibration ranking optimism bias across sales reps. |

---

## 🧠 System Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          CRM Ingestion & Validation          │
                  │   data/deals.csv  •  /api/upload (CSV)      │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │       LangGraph StateGraph Orchestration     │
                  └──────────────────────┬───────────────────────┘
                                         │
      ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
      ▼                  ▼                               ▼                  ▼
┌─────────────┐   ┌─────────────┐                 ┌─────────────┐   ┌─────────────┐
│ Node 1:     │   │ Node 2:     │                 │ Node 3:     │   │ Node 4:     │
│ Monte Carlo │   │ 6-Signal    │                 │ Holdout     │   │ ChromaDB    │
│ Simulation  │   │ Risk Engine │                 │ Backtest    │   │ Grounded    │
│ (P10/50/90) │   │ (Scoring)   │                 │ (Feature 7) │   │ RAG Citings │
└──────┬──────┘   └──────┬──────┘                 └──────┬──────┘   └──────┬──────┘
       │                 │                               │                 │
       └─────────────────┴───────────────┬───────────────┴─────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ Node 5: Commit Salvage Simulator             │
                  │ Calculates weighted P50 lift on interventions│
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ Node 6: Executive Narrative Synthesizer      │
                  │ Powered by Groq (openai/gpt-oss-120b)        │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ Modern React 19 + Vite Executive Dashboard   │
                  │ Recharts  •  Clean Light Theme  •  7 Panels  │
                  └──────────────────────────────────────────────┘
```

---

## 📊 Feature 7: Holdout Backtest Results (Compulsory Evaluation)

To ensure empirical reasonableness, the model was evaluated against unseen **2026-Q1** closed deals:

| Metric | Sales Reps Intuition | LegitsIQ Monte Carlo Engine | Delta / Improvement |
|---|:---:|:---:|:---:|
| **Committed / Expected** | $15,623,000 | $6,262,052 | Realistic Calibration |
| **Actual Ground Truth** | $8,192,000 | $8,192,000 | Baseline Reality |
| **Absolute % Error (APE)** | **90.71%** | **23.56%** | **-67.15% Error Reduction** |
| **Verification Status** | Optimism Bias | Validated within P10-P90 | 🏆 **Model Beats Reps by +67.2 pp** |

---

## 🛠️ Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python 3.11+)
- **Agent Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) / [LangChain](https://www.langchain.com/)
- **Statistical Engine**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [Scikit-learn](https://scikit-learn.org/)
- **Large Language Model**: [Groq](https://groq.com/) Cloud Inference (`openai/gpt-oss-120b`)
- **RAG & Vector Storage**: [ChromaDB](https://www.trychroma.com/) (Local CPU vector indexing)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Frontend Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Visualizations**: [Recharts](https://recharts.org/) & [Lucide React](https://lucide.dev/)

---

## ⚡ Quickstart & Local Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- A free Groq API key from [console.groq.com](https://console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/arihantmahajan585m/AI-Forecast-Engine.git
cd AI-Forecast-Engine
```

### 2. Set Up the Backend
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create a .env file in root:
echo GROQ_API_KEY=your_groq_api_key_here > .env
echo GROQ_MODEL=openai/gpt-oss-120b >> .env

# Start FastAPI backend server
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be active at: `http://127.0.0.1:8000` (API docs at `/docs`).

### 3. Set Up the Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will launch at: `http://localhost:5173`.

---

## 📁 Repository Structure

```
├── data/
│   ├── deals.csv               # 200 realistic CRM deals (150 open, 50 holdout)
│   ├── meta.json               # CRM metadata and quarter index
│   └── knowledge/              # Battle-tested sales playbooks for RAG
│       ├── sales_playbook.md
│       ├── objection_and_stall_playbook.md
│       ├── win_loss_patterns.md
│       └── leadership_qbr.md
├── pipeline_forge/             # Core AI & Statistical Engine
│   ├── agents/
│   │   ├── graph.py            # LangGraph StateGraph (6-node orchestration)
│   │   └── tools.py            # 8 LangChain @tool wrappers
│   ├── rag/
│   │   ├── ingest.py           # ChromaDB document loader & chunk indexer
│   │   └── retrieve.py         # Multi-hop retriever with [C#] citations
│   └── stats/
│       ├── forecast.py         # 4,000-iteration Monte Carlo engine
│       ├── risk.py             # 6-signal deal risk scoring algorithm
│       └── simulate.py         # What-if commit salvage simulator & rep calibration
├── frontend/                   # Modern React 19 Dashboard
│   ├── src/
│   │   ├── App.tsx             # Main dashboard (7 tabs, modals, Recharts)
│   │   ├── WelcomePage.tsx     # Landing page with T&C gate
│   │   └── App.css             # Light theme styling & CSS variables
│   └── vercel.json             # Vercel deployment configuration
├── Procfile                    # Railway deployment process command
├── render.yaml                 # Render infrastructure configuration
├── server.py                   # FastAPI REST API endpoints
└── requirements.txt            # Python dependencies
```

---

## 💼 Business Model & Go-To-Market

LegitsIQ bridges the gap between low-accuracy spreadsheet forecasting and enterprise platforms like Clari/Gong ($50,000+/year).

- **Phase 1 (Self-Serve Pilot)**: Instant friction-free CSV upload allowing RevOps to test model accuracy against historical closed quarters in 5 minutes.
- **Phase 2 (1-Click OAuth Sync)**: Automated nightly sync with Salesforce AppExchange and HubSpot CRM APIs.
- **Monetization**: Tiered SaaS pricing for mid-market B2B teams ($499 – $1,499/month). 
- **ROI Justification**: Salvaging a single $65,000 stalled enterprise deal pays for the software for 4+ years.

---

## 👥 Authors & Acknowledgments

- **Team**: LegitsIQ Development Team
- **Track**: Track D · D4 (Sales, Growth & Revenue Agents)
- **Built for**: Global AI Hackathon 2026

Licensed under the [MIT License](LICENSE).
