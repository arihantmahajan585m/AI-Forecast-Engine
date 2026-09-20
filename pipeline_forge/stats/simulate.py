"""Commit-call simulator and rep calibration — real math, not LLM guesses."""
from __future__ import annotations

from typing import Any

import pandas as pd

from pipeline_forge.stats.forecast import forecast_open_pipeline
from pipeline_forge.stats.risk import score_deal


def simulate_salvage(
    df: pd.DataFrame,
    deal_ids: list[str],
    salvage_strength: float = 0.55,
    quarter: str = "2026-Q2",
) -> dict[str, Any]:
    """
    Model the Monday commit ritual: if RevOps executes the action queue on
    selected at-risk deals, engagement/EB/activity recover by salvage_strength.
    Re-run Monte Carlo and report P50 lift vs baseline.
    """
    baseline = forecast_open_pipeline(df, quarter=quarter)
    work = df.copy()
    touched = []
    ids = set(deal_ids)
    for i, row in work.iterrows():
        if row.get("deal_id") not in ids:
            continue
        days = int(row.get("days_since_activity") or 0)
        eng = float(row.get("engagement_score") or 0.3)
        work.at[i, "days_since_activity"] = max(0, int(days * (1 - salvage_strength)))
        work.at[i, "engagement_score"] = min(0.95, eng + salvage_strength * (0.85 - eng))
        work.at[i, "email_opens_14d"] = max(int(row.get("email_opens_14d") or 0), int(4 + 8 * salvage_strength))
        work.at[i, "meetings_30d"] = max(int(row.get("meetings_30d") or 0), int(1 + 2 * salvage_strength))
        if salvage_strength >= 0.4:
            work.at[i, "has_economic_buyer"] = 1
        before = score_deal(row)
        after = score_deal(work.loc[i])
        touched.append(
            {
                "deal_id": row["deal_id"],
                "account": row["account"],
                "amount": float(row["amount"]),
                "risk_before": before["risk_score"],
                "risk_after": after["risk_score"],
                "p_before": before["adj_win_prob"],
                "p_after": after["adj_win_prob"],
                "weighted_lift": round(float(row["amount"]) * (after["adj_win_prob"] - before["adj_win_prob"]), 2),
            }
        )
    scenario = forecast_open_pipeline(work, quarter=quarter)
    return {
        "quarter": quarter,
        "salvage_strength": salvage_strength,
        "n_intervened": len(touched),
        "baseline_p50": baseline["p50"],
        "scenario_p50": scenario["p50"],
        "p50_lift": round(scenario["p50"] - baseline["p50"], 2),
        "baseline_expected": baseline["expected"],
        "scenario_expected": scenario["expected"],
        "expected_lift": round(scenario["expected"] - baseline["expected"], 2),
        "baseline_p10": baseline["p10"],
        "scenario_p10": scenario["p10"],
        "baseline_p90": baseline["p90"],
        "scenario_p90": scenario["p90"],
        "deals": sorted(touched, key=lambda x: x["weighted_lift"], reverse=True),
        "methodology": (
            "Reduce stall days, restore engagement/touches, map EB if strength≥0.4, "
            "then re-run the same Monte Carlo engine as the live forecast."
        ),
    }


def rep_calibration(df: pd.DataFrame) -> list[dict[str, Any]]:
    closed = df[df["is_open"] == 0].copy()
    if closed.empty:
        return []
    rows = []
    for rep, g in closed.groupby("rep"):
        if "actual_revenue" in g.columns:
            actual = float(g["actual_revenue"].fillna(0).sum())
        else:
            actual = float(g[g["stage"] == "Closed Won"]["amount"].fillna(0).sum())
        predicted = float(g["rep_forecast_amount"].fillna(0).sum())
        ape = 0.0 if actual == 0 and predicted == 0 else (
            100.0 if actual == 0 else abs(predicted - actual) / actual * 100.0
        )
        won = int((g["stage"] == "Closed Won").sum())
        rows.append(
            {
                "rep": str(rep),
                "n_closed": int(len(g)),
                "won": won,
                "win_rate": round(won / len(g), 3) if len(g) else 0.0,
                "actual_revenue": round(actual, 2),
                "rep_forecast": round(predicted, 2),
                "abs_pct_error": round(ape, 2),
                "bias": round(predicted - actual, 2),
            }
        )
    rows.sort(key=lambda x: x["abs_pct_error"], reverse=True)
    return rows
