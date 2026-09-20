"""LangChain tools — real Python logic, not LLM guessing."""
from __future__ import annotations

import json
from typing import Any

import pandas as pd
from langchain_core.tools import tool

from pipeline_forge.config import BACKTEST_HOLDOUT, DEALS_CSV, REQUIRED_DEAL_COLUMNS
from pipeline_forge.rag.retrieve import format_citations_block, retrieve_with_citations
from pipeline_forge.stats.forecast import forecast_closed_quarter_as_of, forecast_open_pipeline
from pipeline_forge.stats.risk import compute_stage_avg_days, rank_at_risk, score_deal
from pipeline_forge.stats.simulate import rep_calibration, simulate_salvage

_DF_CACHE: pd.DataFrame | None = None


def load_deals(path: str | None = None) -> pd.DataFrame:
    global _DF_CACHE
    if _DF_CACHE is None or path:
        _DF_CACHE = pd.read_csv(path or DEALS_CSV)
    return _DF_CACHE


def validate_deals_frame(df: pd.DataFrame) -> list[str]:
    missing = [c for c in REQUIRED_DEAL_COLUMNS if c not in df.columns]
    if missing:
        return [f"CSV missing required columns: {', '.join(missing)}"]
    if df.empty:
        return ["CSV has no rows."]
    return []


def refresh_deals(df: pd.DataFrame) -> None:
    global _DF_CACHE
    _DF_CACHE = df


def _json_safe(obj: Any) -> Any:
    if hasattr(obj, "item"):
        return obj.item()
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    return obj


@tool
def tool_forecast_pipeline(quarter: str = "2026-Q2") -> str:
    """Compute probabilistic revenue forecast (P10/P50/P90, expected, commit) for an open pipeline quarter.

    Uses Monte Carlo simulation over deal-level win probabilities (stage base rate
    × risk haircut). Returns confidence bands, rep roll-up, and top deal contributions.

    Args:
        quarter: Forecast quarter label, e.g. '2026-Q2'.
    """
    df = load_deals()
    result = forecast_open_pipeline(df, quarter=quarter)
    slim = dict(result)
    slim["deal_contributions"] = result.get("deal_contributions", [])[:12]
    return json.dumps(slim)


@tool
def tool_rank_risk_deals(top_n: int = 10, min_score: float = 0.2) -> str:
    """Rank open deals by multi-signal risk score with transparent evidence strings.

    Signals: stalled_activity, stage_overage (vs historical median), engagement_drop,
    missing_economic_buyer, zero_touch, enterprise_exposure.

    Args:
        top_n: Number of deals to return.
        min_score: Minimum risk score threshold (0-1).
    """
    df = load_deals()
    stage_avg = compute_stage_avg_days(df)
    ranked = rank_at_risk(df, min_score=min_score, top_n=top_n, stage_avg_days=stage_avg)
    return json.dumps(ranked)


@tool
def tool_score_deal(deal_id: str) -> str:
    """Score a single deal's risk with transparent signal evidence.

    Checks stall days vs stage historical average, engagement score, economic
    buyer presence, and zero-touch patterns.

    Args:
        deal_id: Deal identifier like 'D-1042'.
    """
    df = load_deals()
    hit = df[df["deal_id"] == deal_id]
    if hit.empty:
        return json.dumps({"error": f"Deal {deal_id} not found"})
    stage_avg = compute_stage_avg_days(df)
    return json.dumps(score_deal(hit.iloc[0], stage_avg_days=stage_avg), default=str)


@tool
def tool_backtest_holdout(quarter: str = BACKTEST_HOLDOUT) -> str:
    """Hold out a past quarter, run the model forecast, and compare APE vs rep estimates and actuals.

    This is the compulsory Feature 7: demonstrates the model beats optimistic rep
    roll-ups on an unseen held-out quarter. Returns actual revenue, model expected,
    rep forecast total, and absolute percentage errors for both.

    Args:
        quarter: Holdout quarter, default '2026-Q1'.
    """
    df = load_deals()
    return json.dumps(forecast_closed_quarter_as_of(df, holdout_quarter=quarter))


@tool
def tool_retrieve_playbook(query: str, k: int = 4) -> str:
    """RAG retrieve sales playbook, win-loss patterns, and CRM note chunks with citation IDs.

    Chunks are grounded — answers cite [C#] IDs traceable to specific playbook sections
    or CRM deal notes.

    Args:
        query: Natural language query about risk pattern, a deal, or next action.
        k: Number of chunks to retrieve.
    """
    cites = retrieve_with_citations(query, k=k)
    return json.dumps({"citations": cites, "formatted": format_citations_block(cites)})


@tool
def tool_deal_context(deal_id: str) -> str:
    """Fetch raw CRM fields and full activity history for a specific deal.

    Args:
        deal_id: Deal identifier like 'D-1042'.
    """
    df = load_deals()
    hit = df[df["deal_id"] == deal_id]
    if hit.empty:
        return json.dumps({"error": f"Deal {deal_id} not found"})
    row = hit.iloc[0].to_dict()
    clean = {k: _json_safe(v) for k, v in row.items()}
    return json.dumps(clean, default=str)


@tool
def tool_simulate_commit(deal_ids: str, salvage_strength: float = 0.55, quarter: str = "2026-Q2") -> str:
    """Simulate executing next-best-actions on at-risk deals and report P50 lift.

    Re-runs the same Monte Carlo engine after synthetically improving engagement,
    activity recency, and EB mapping for the targeted deals. Returns before/after
    P10/P50/P90 and per-deal weighted lift.

    Args:
        deal_ids: Comma-separated deal IDs, e.g. 'D-1113,D-1105'.
        salvage_strength: 0-1 intensity of intervention (0.55 = moderate action queue).
        quarter: Forecast quarter.
    """
    df = load_deals()
    ids = [x.strip() for x in (deal_ids or "").split(",") if x.strip()]
    if not ids:
        return json.dumps({"error": "Provide at least one deal_id"})
    strength = min(1.0, max(0.0, float(salvage_strength)))
    return json.dumps(simulate_salvage(df, ids, salvage_strength=strength, quarter=quarter))


@tool
def tool_rep_calibration() -> str:
    """Score each sales rep's historical forecast accuracy vs actual closed revenue.

    Returns per-rep absolute percentage error (APE), win rate, and optimism bias.
    Sorted by noisiest forecasters first.
    """
    df = load_deals()
    return json.dumps(rep_calibration(df))


ALL_TOOLS = [
    tool_forecast_pipeline,
    tool_rank_risk_deals,
    tool_score_deal,
    tool_backtest_holdout,
    tool_retrieve_playbook,
    tool_deal_context,
    tool_simulate_commit,
    tool_rep_calibration,
]
