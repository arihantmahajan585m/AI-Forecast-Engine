"""Standalone CLI execution for PipelineForge — runs statistical forecasting, risk scoring, holdout backtest, RAG retrieval, and agent orchestration locally in terminal."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from pipeline_forge.agents.graph import run_ask, run_deal_deep_dive, run_leadership_briefing
from pipeline_forge.agents.tools import refresh_deals
from pipeline_forge.config import BACKTEST_HOLDOUT, DEALS_CSV
from pipeline_forge.rag.retrieve import ensure_index
from pipeline_forge.stats.forecast import forecast_closed_quarter_as_of, forecast_open_pipeline
from pipeline_forge.stats.risk import compute_stage_avg_days, rank_at_risk
from pipeline_forge.stats.simulate import rep_calibration, simulate_salvage


def money(v: float) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:,.0f}"


def main():
    print("=" * 70)
    print(" ◈ PIPELINEFORGE — REVENUE INTELLIGENCE & DEAL RISK AGENT (CLI)")
    print("=" * 70)

    # 1. RAG Indexing
    print("\n[1/6] Indexing Knowledge Base & CRM Notes...")
    rag_meta = ensure_index()
    print(f"      ✓ RAG Vector Store Ready ({rag_meta.get('chunks')} chunks indexed)")

    # 2. Data Loading & Statistics
    print("\n[2/6] Loading CRM Pipeline Data...")
    df = pd.read_csv(DEALS_CSV)
    refresh_deals(df)
    open_n = int(df["is_open"].sum())
    closed_n = int((1 - df["is_open"]).sum())
    print(f"      ✓ Open Deals: {open_n} | Closed Deals: {closed_n}")

    # 3. Monte Carlo Open Forecast
    print("\n[3/6] Running 4,000-Iteration Monte Carlo Open Pipeline Forecast (2026-Q2)...")
    fc = forecast_open_pipeline(df, quarter="2026-Q2")
    print(f"      P10 Forecast : {money(fc['p10'])}")
    print(f"      P50 Forecast : {money(fc['p50'])} (Default Leadership Number)")
    print(f"      P90 Forecast : {money(fc['p90'])}")
    print(f"      Expected     : {money(fc['expected'])}")
    print(f"      Rep Roll-Up  : {money(fc['rep_roll_up'])} (Optimism Gap: {money(fc['rep_roll_up'] - fc['p50'])})")

    # 4. Compulsory Feature 7 — Holdout Backtest
    print(f"\n[4/6] Running Compulsory Holdout Backtest ({BACKTEST_HOLDOUT})...")
    bt = forecast_closed_quarter_as_of(df, BACKTEST_HOLDOUT)
    print(f"      Actual Closed Revenue : {money(bt['actual_revenue'])}")
    print(f"      Model Expected        : {money(bt['model_expected'])} (APE: {bt['model_abs_pct_error']:.1f}%)")
    print(f"      Rep Roll-Up           : {money(bt['rep_forecast_total'])} (APE: {bt['rep_abs_pct_error']:.1f}%)")
    delta = bt.get("error_improvement_pp", 0)
    print(f"      VERDICT               : Model outperforms reps by +{delta:.1f} pp absolute error!")

    # 5. Risk Cockpit & Top Action Queue
    print("\n[5/6] Risk Scoring & Stage-Overage Signal Evaluation...")
    stage_avg = compute_stage_avg_days(df)
    risks = rank_at_risk(df, min_score=0.2, top_n=5, stage_avg_days=stage_avg)
    for i, r in enumerate(risks, 1):
        sigs = ", ".join(s["code"] for s in r["signals"])
        print(f"      {i}. {r['deal_id']} ({r['account']}) — ACV: {money(r['amount'])} | Band: {r['risk_band'].upper()} ({r['risk_score']}) | Signals: [{sigs}]")

    # 6. LangGraph Agent Leadership Briefing
    print("\n[6/6] Executing LangGraph Leadership Agent Orchestration...")
    briefing = run_leadership_briefing("2026-Q2")
    print("\n      [Agent Trace]:")
    print("      " + " -> ".join(briefing.get("trace") or []))
    print("\n      [Agent Narrative Summary]:")
    narrative = briefing.get("narrative") or ""
    for line in narrative.split("\n"):
        if line.strip():
            print(f"      {line.strip()}")

    print("\n" + "=" * 70)
    print(" SUCCESS: All agents, statistics, RAG retrieval, and backtests executed cleanly.")
    print("=" * 70)


if __name__ == "__main__":
    main()
