"""Probabilistic weighted pipeline forecast with confidence bands."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from pipeline_forge.config import STAGE_WIN_RATE
from pipeline_forge.stats.risk import score_deal


def forecast_open_pipeline(
    df: pd.DataFrame,
    n_sims: int = 4000,
    seed: int = 7,
    quarter: str | None = "2026-Q2",
) -> dict[str, Any]:
    open_df = df[df["is_open"] == 1].copy()
    if quarter:
        open_df = open_df[open_df["forecast_quarter"] == quarter]
    if open_df.empty:
        return {
            "quarter": quarter,
            "n_deals": 0,
            "coverage": 0.0,
            "rep_roll_up": 0.0,
            "p10": 0.0,
            "p50": 0.0,
            "p90": 0.0,
            "expected": 0.0,
            "commit": 0.0,
            "best_case": 0.0,
            "deal_contributions": [],
        }

    rng = np.random.default_rng(seed)
    probs = []
    amounts = []
    contrib = []
    commit = 0.0
    best = 0.0
    rep_sum = 0.0

    for _, row in open_df.iterrows():
        s = score_deal(row)
        p = s["adj_win_prob"]
        amt = float(row["amount"])
        probs.append(p)
        amounts.append(amt)
        best += amt * float(STAGE_WIN_RATE.get(str(row["stage"]), 0.2))
        rep_sum += float(row.get("rep_forecast_amount") or 0)
        if (
            str(row["stage"]) == "Negotiation"
            and s["risk_score"] < 0.35
            and int(row.get("has_economic_buyer", 0) or 0) == 1
        ):
            commit += amt * p
        contrib.append(
            {
                "deal_id": row["deal_id"],
                "account": row["account"],
                "amount": amt,
                "stage": row["stage"],
                "win_prob": p,
                "weighted": round(amt * p, 2),
                "risk_score": s["risk_score"],
                "risk_band": s["risk_band"],
            }
        )

    probs_a = np.array(probs)
    amounts_a = np.array(amounts)
    wins = rng.random((n_sims, len(probs_a))) < probs_a
    sim_totals = (wins * amounts_a).sum(axis=1)
    expected = float((probs_a * amounts_a).sum())

    contrib.sort(key=lambda x: x["weighted"], reverse=True)

    return {
        "quarter": quarter,
        "n_deals": int(len(open_df)),
        "coverage": float(amounts_a.sum()),
        "rep_roll_up": round(rep_sum, 2),
        "p10": round(float(np.percentile(sim_totals, 10)), 2),
        "p50": round(float(np.percentile(sim_totals, 50)), 2),
        "p90": round(float(np.percentile(sim_totals, 90)), 2),
        "expected": round(expected, 2),
        "commit": round(commit, 2),
        "best_case": round(best, 2),
        "deal_contributions": contrib[:40],
        "sim_mean": round(float(sim_totals.mean()), 2),
        "sim_std": round(float(sim_totals.std()), 2),
    }


def forecast_closed_quarter_as_of(
    df: pd.DataFrame,
    holdout_quarter: str,
    n_sims: int = 3000,
    seed: int = 11,
) -> dict[str, Any]:
    """
    Hold out a past quarter and reconstruct a mid-quarter snapshot using only
    features knowable before close (engagement, activity, stakeholders).
    Compare model expected revenue vs actuals and vs optimistic rep estimates.
    """
    q = df[df["forecast_quarter"] == holdout_quarter].copy()
    if q.empty:
        return {"error": f"No deals for {holdout_quarter}"}

    closed = q[q["is_open"] == 0].copy()
    if closed.empty:
        return {"error": f"No closed deals for {holdout_quarter}"}

    rows = []
    for _, row in closed.iterrows():
        r = row.copy()
        eng = float(r.get("engagement_score") or 0.4)
        days = int(r.get("days_since_activity") or 20)
        has_eb = int(r.get("has_economic_buyer") or 0)
        # Mid-quarter stage proxy from engagement/activity — not outcome leakage
        if eng >= 0.7 and days <= 10 and has_eb:
            stage = "Negotiation"
        elif eng >= 0.55 and days <= 18:
            stage = "Proposal"
        elif eng >= 0.4:
            stage = "Discovery"
        else:
            stage = "Qualification"
        r["stage"] = stage
        r["is_open"] = 1
        rows.append(r)

    snap = pd.DataFrame(rows)
    snap["forecast_quarter"] = holdout_quarter
    fc = forecast_open_pipeline(snap, n_sims=n_sims, seed=seed, quarter=holdout_quarter)

    if "actual_revenue" in closed.columns:
        actual = float(closed["actual_revenue"].fillna(0).sum())
    else:
        actual = float(closed[closed["stage"] == "Closed Won"]["amount"].fillna(0).sum())
    # Rep roll-up on the same closed set (what they committed mid-quarter)
    rep_sum = float(closed["rep_forecast_amount"].fillna(0).sum())
    model = float(fc["expected"])

    def ape(pred: float, truth: float) -> float:
        if truth == 0:
            return 0.0 if pred == 0 else 100.0
        return abs(pred - truth) / truth * 100.0

    return {
        "holdout_quarter": holdout_quarter,
        "n_deals": int(len(closed)),
        "actual_revenue": round(actual, 2),
        "rep_forecast_total": round(rep_sum, 2),
        "model_expected": round(model, 2),
        "model_p10": fc["p10"],
        "model_p50": fc["p50"],
        "model_p90": fc["p90"],
        "rep_abs_pct_error": round(ape(rep_sum, actual), 2),
        "model_abs_pct_error": round(ape(model, actual), 2),
        "error_improvement_pp": round(ape(rep_sum, actual) - ape(model, actual), 2),
        "within_p10_p90": bool(fc["p10"] <= actual <= fc["p90"]),
        "methodology": (
            "Reconstructed mid-quarter stages from engagement/activity/EB only; "
            "Monte Carlo expected vs actual closed revenue; rep estimates from CRM."
        ),
    }
