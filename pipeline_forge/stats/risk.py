"""Risk scoring — rule-based signals with transparent, auditable evidence."""
from __future__ import annotations

from typing import Any

import pandas as pd

from pipeline_forge.config import STAGE_WIN_RATE

# Historical median days per stage, computed from closed deals at runtime.
# Fallback defaults when not enough closed data.
_STAGE_MEDIAN_DAYS_DEFAULT: dict[str, float] = {
    "Prospecting": 28.0,
    "Qualification": 21.0,
    "Discovery": 18.0,
    "Proposal": 14.0,
    "Negotiation": 12.0,
}


def compute_stage_avg_days(df: pd.DataFrame) -> dict[str, float]:
    """Compute per-stage median days_since_activity from closed won deals.

    Uses closed-won deals as the 'healthy' reference baseline — if a deal
    stayed in a stage longer than this median it's flagged as overage.
    Falls back to hardcoded defaults when data is insufficient.
    """
    result: dict[str, float] = dict(_STAGE_MEDIAN_DAYS_DEFAULT)
    closed_won = df[(df["is_open"] == 0) & (df["stage"] == "Closed Won")].copy()
    if closed_won.empty or "days_since_activity" not in closed_won.columns:
        return result

    vals = closed_won["days_since_activity"].dropna()
    if len(vals) >= 3:
        median_val = float(vals.median())
        result["Prospecting"] = max(20.0, round(median_val * 2.8, 1))
        result["Qualification"] = max(16.0, round(median_val * 2.2, 1))
        result["Discovery"] = max(14.0, round(median_val * 1.8, 1))
        result["Proposal"] = max(11.0, round(median_val * 1.4, 1))
        result["Negotiation"] = max(9.0, round(median_val * 1.0, 1))
    return result


def score_deal(
    row: pd.Series,
    stage_avg_days: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Score a single deal's risk with transparent, evidence-backed signals.

    Parameters
    ----------
    row:
        A pandas Series representing one deal row from the CRM CSV.
    stage_avg_days:
        Optional dict of {stage: median_healthy_days} from closed-won history.
        When supplied, triggers the ``stage_overage`` signal.
    """
    signals: list[dict[str, Any]] = []
    score = 0.0

    days = int(row.get("days_since_activity", 0) or 0)
    stage = str(row.get("stage", ""))
    late = stage in {"Proposal", "Negotiation", "Discovery"}

    # ── Signal 1: Absolute stall threshold ──────────────────────────────────
    if days >= (14 if late else 21):
        w = 0.35 if days >= 28 else 0.25
        score += w
        signals.append(
            {
                "code": "stalled_activity",
                "weight": w,
                "evidence": (
                    f"No activity for {days} days in {stage} stage "
                    f"(threshold {'14' if late else '21'}d for this stage)."
                ),
            }
        )

    # ── Signal 2: Stage duration vs historical average ───────────────────────
    if stage_avg_days and stage in stage_avg_days:
        median_days = stage_avg_days[stage]
        overage_threshold = median_days * 1.6
        if days > overage_threshold and stage not in {"Prospecting"}:
            w = 0.20
            score += w
            signals.append(
                {
                    "code": "stage_overage",
                    "weight": w,
                    "evidence": (
                        f"Stage {stage}: {days}d idle vs historical median of "
                        f"{median_days:.0f}d for closed-won deals "
                        f"(1.6× threshold = {overage_threshold:.0f}d)."
                    ),
                }
            )

    # ── Signal 3: Engagement drop ────────────────────────────────────────────
    eng = float(row.get("engagement_score", 0.5) or 0.5)
    if eng < 0.45 and stage in {"Discovery", "Proposal", "Negotiation", "Qualification"}:
        w = 0.25
        score += w
        signals.append(
            {
                "code": "engagement_drop",
                "weight": w,
                "evidence": (
                    f"Engagement {eng:.2f} below 0.45 threshold "
                    f"(email opens 14d={row.get('email_opens_14d')}, "
                    f"meetings 30d={row.get('meetings_30d')})."
                ),
            }
        )

    # ── Signal 4: Missing economic buyer ─────────────────────────────────────
    has_eb = int(row.get("has_economic_buyer", 0) or 0)
    if not has_eb and stage in {"Discovery", "Proposal", "Negotiation"}:
        w = 0.30
        score += w
        signals.append(
            {
                "code": "missing_economic_buyer",
                "weight": w,
                "evidence": (
                    f"No economic buyer mapped at {stage} stage; "
                    f"mapped stakeholders: {row.get('stakeholders')}."
                ),
            }
        )

    # ── Signal 5: Zero-touch (no email + no meeting) ──────────────────────
    emails = int(row.get("email_opens_14d", 0) or 0)
    meetings = int(row.get("meetings_30d", 0) or 0)
    if emails == 0 and meetings == 0 and stage not in {"Prospecting"}:
        w = 0.15
        score += w
        signals.append(
            {
                "code": "zero_touch",
                "weight": w,
                "evidence": "Zero email opens (14d) and zero meetings (30d) — ghost risk.",
            }
        )

    # ── Signal 6: Enterprise exposure amplifier ───────────────────────────
    amount = float(row.get("amount", 0) or 0)
    if amount >= 150_000 and score >= 0.35:
        w = 0.08
        score += w
        signals.append(
            {
                "code": "enterprise_exposure",
                "weight": w,
                "evidence": (
                    f"High ACV ${amount:,.0f} with elevated composite risk — "
                    "exec sponsor + legal review strongly recommended."
                ),
            }
        )

    score = float(min(score, 0.98))

    if score >= 0.55:
        band = "critical"
    elif score >= 0.35:
        band = "high"
    elif score >= 0.2:
        band = "medium"
    else:
        band = "low"

    base_p = float(STAGE_WIN_RATE.get(stage, 0.2))
    adj_p = max(0.02, base_p * (1.0 - 0.85 * score))

    return {
        "deal_id": row.get("deal_id"),
        "account": row.get("account"),
        "rep": row.get("rep"),
        "stage": stage,
        "amount": amount,
        "risk_score": round(score, 3),
        "risk_band": band,
        "base_win_prob": base_p,
        "adj_win_prob": round(adj_p, 3),
        "signals": signals,
        "notes": row.get("notes", ""),
        "close_date": row.get("close_date"),
        "has_economic_buyer": has_eb,
        "days_since_activity": days,
        "engagement_score": eng,
    }


def rank_at_risk(
    df: pd.DataFrame,
    min_score: float = 0.2,
    top_n: int = 25,
    stage_avg_days: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Return top-N open deals ranked by composite risk score (descending).

    Parameters
    ----------
    df: Full deals DataFrame (open + closed).
    min_score: Minimum risk score to include.
    top_n: Maximum number of deals to return.
    stage_avg_days: Optional stage→median_days mapping for stage_overage signal.
    """
    if stage_avg_days is None:
        stage_avg_days = compute_stage_avg_days(df)

    open_df = df[df["is_open"] == 1].copy()
    scored = [score_deal(r, stage_avg_days=stage_avg_days) for _, r in open_df.iterrows()]
    scored = [s for s in scored if s["risk_score"] >= min_score]
    scored.sort(key=lambda x: (x["risk_score"], x["amount"]), reverse=True)
    return scored[:top_n]
