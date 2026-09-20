"""FastAPI backend for PipelineForge Vite React frontend with CSV upload & Agent Status API."""
from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from pipeline_forge.agents.graph import run_ask, run_deal_deep_dive, run_leadership_briefing
from pipeline_forge.agents.tools import ALL_TOOLS, refresh_deals, validate_deals_frame
from pipeline_forge.config import BACKTEST_HOLDOUT, DEALS_CSV, GROQ_API_KEY
from pipeline_forge.rag.retrieve import ensure_index
from pipeline_forge.stats.forecast import forecast_closed_quarter_as_of, forecast_open_pipeline
from pipeline_forge.stats.risk import compute_stage_avg_days, rank_at_risk, score_deal
from pipeline_forge.stats.simulate import rep_calibration, simulate_salvage

app = FastAPI(title="PipelineForge API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_df() -> pd.DataFrame:
    df = pd.read_csv(DEALS_CSV)
    refresh_deals(df)
    return df


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "PipelineForge"}


@app.get("/api/meta")
def get_meta():
    df = get_df()
    rag_meta = ensure_index()
    open_df = df[df["is_open"] == 1]
    quarters = sorted(open_df["forecast_quarter"].dropna().unique().tolist(), reverse=True)
    return {
        "n_deals": len(df),
        "n_open": int(df["is_open"].sum()),
        "n_closed": int((1 - df["is_open"]).sum()),
        "quarters": quarters or ["2026-Q2"],
        "holdout": BACKTEST_HOLDOUT,
        "rag_chunks": rag_meta.get("chunks", 0),
        "llm_connected": bool(GROQ_API_KEY),
    }


@app.get("/api/agent-status")
def get_agent_status():
    rag_meta = ensure_index()
    tools_list = [{"name": t.name, "description": t.description} for t in ALL_TOOLS]
    return {
        "agent_name": "PipelineForge CRO Orchestrator",
        "framework": "LangGraph State Machine",
        "nodes": ["forecast", "risk", "backtest", "rag_recommend", "simulate", "narrative"],
        "llm_available": bool(GROQ_API_KEY),
        "llm_model": "Groq Llama 3.3 70B Versatile (Free Tier)" if GROQ_API_KEY else "Local Rule Engine (Offline)",
        "vector_store": "ChromaDB (Local Disk)",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2 (Local CPU)",
        "indexed_chunks": rag_meta.get("chunks", 0),
        "tools": tools_list,
    }


@app.get("/api/forecast")
def get_forecast(quarter: str = "2026-Q2"):
    df = get_df()
    res = forecast_open_pipeline(df, quarter=quarter)
    return res


@app.get("/api/risks")
def get_risks(min_score: float = 0.2, top_n: int = 15):
    df = get_df()
    stage_avg = compute_stage_avg_days(df)
    ranked = rank_at_risk(df, min_score=min_score, top_n=top_n, stage_avg_days=stage_avg)
    return {"risks": ranked, "stage_avg_days": stage_avg}


@app.get("/api/backtest")
def get_backtest(quarter: str = BACKTEST_HOLDOUT):
    df = get_df()
    bt = forecast_closed_quarter_as_of(df, holdout_quarter=quarter)
    reps = rep_calibration(df)
    return {"backtest": bt, "rep_calibration": reps}


@app.get("/api/briefing")
def get_briefing(quarter: str = "2026-Q2"):
    return run_leadership_briefing(quarter)


@app.get("/api/deal/{deal_id}")
def get_deal_deep_dive(deal_id: str):
    return run_deal_deep_dive(deal_id)


class SimulateRequest(BaseModel):
    deal_ids: List[str]
    salvage_strength: float = 0.55
    quarter: str = "2026-Q2"


@app.post("/api/simulate")
def post_simulate(req: SimulateRequest):
    df = get_df()
    return simulate_salvage(
        df,
        req.deal_ids,
        salvage_strength=req.salvage_strength,
        quarter=req.quarter,
    )


class AskRequest(BaseModel):
    question: str
    quarter: str = "2026-Q2"


@app.post("/api/ask")
def post_ask(req: AskRequest):
    return run_ask(req.question, quarter=req.quarter)


@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    contents = await file.read()
    try:
        custom_df = pd.read_csv(io.BytesIO(contents))
        errs = validate_deals_frame(custom_df)
        if errs:
            raise HTTPException(status_code=400, detail=errs[0])
        custom_df.to_csv(DEALS_CSV, index=False)
        refresh_deals(custom_df)
        # Re-index vector store with new CRM notes
        from pipeline_forge.rag.ingest import reset_store
        reset_store()
        rag_meta = ensure_index()
        return {
            "status": "success",
            "message": f"Successfully loaded {len(custom_df)} deals from {file.filename}",
            "n_deals": len(custom_df),
            "n_open": int(custom_df["is_open"].sum()),
            "rag_chunks": rag_meta.get("chunks", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")
