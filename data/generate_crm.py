"""Generate a realistic synthetic CRM pipeline for PipelineForge demos & backtests."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parent
STAGES = ["Prospecting", "Qualification", "Discovery", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
OPEN_STAGES = STAGES[:-2]
INDUSTRIES = ["FinTech", "Healthcare", "SaaS", "Manufacturing", "Retail", "EdTech", "Logistics"]
REPS = ["A. Mehta", "J. Park", "S. Rivera", "M. Okonkwo", "L. Chen", "R. Iyer"]
PERSONAS = ["economic_buyer", "champion", "technical_buyer", "user_buyer", "legal", "security"]

# Historical stage→win probability (used by forecast agent)
STAGE_WIN_RATE = {
    "Prospecting": 0.12,
    "Qualification": 0.22,
    "Discovery": 0.38,
    "Proposal": 0.52,
    "Negotiation": 0.68,
    "Closed Won": 1.0,
    "Closed Lost": 0.0,
}


def _stakeholders(missing_key: bool = False) -> str:
    base = ["champion", "technical_buyer"]
    if not missing_key and RNG.random() > 0.25:
        base.append("economic_buyer")
    if RNG.random() > 0.5:
        base.append("security" if RNG.random() > 0.5 else "legal")
    return ",".join(sorted(set(base)))


def _activity_history(days_since: int, intensity: str) -> str:
    events = []
    cursor = days_since
    n = {"hot": 8, "warm": 5, "cold": 2}[intensity]
    kinds = ["email", "call", "demo", "meeting", "proposal_sent", "security_review"]
    for i in range(n):
        cursor += int(RNG.integers(3, 18 if intensity != "hot" else 10))
        events.append(
            {
                "days_ago": int(max(0, days_since - i * (days_since // max(n, 1)))),
                "type": str(RNG.choice(kinds)),
                "note": _note_snippet(intensity),
            }
        )
    # ensure last activity aligns
    if events:
        events[0]["days_ago"] = days_since
    return json.dumps(events)


def _note_snippet(intensity: str) -> str:
    hot = [
        "Champion confirmed budget cycle Q-end.",
        "Economic buyer joined demo; positive signal.",
        "Security questionnaire returned 80% complete.",
    ]
    warm = [
        "Follow-up scheduled; waiting on technical evaluation.",
        "Pricing discussion started; no objection yet.",
        "Champion active; EB not yet engaged.",
    ]
    cold = [
        "No reply to last three emails.",
        "Champion went quiet after proposal.",
        "Stakeholder changed; restart needed.",
    ]
    pool = {"hot": hot, "warm": warm, "cold": cold}[intensity]
    return str(RNG.choice(pool))


def generate(n_open: int = 140, n_closed: int = 60) -> pd.DataFrame:
    rows = []
    deal_id = 1000
    as_of = pd.Timestamp("2026-03-31")

    # Closed deals spanning Q3'25 – Q1'26 for backtest
    quarters = [
        ("2025-Q3", "2025-07-01", "2025-09-30"),
        ("2025-Q4", "2025-10-01", "2025-12-31"),
        ("2026-Q1", "2026-01-01", "2026-03-31"),
    ]
    per_q = n_closed // len(quarters)
    for q_name, start, end in quarters:
        for _ in range(per_q):
            won = RNG.random() < 0.55
            stage = "Closed Won" if won else "Closed Lost"
            amount = float(RNG.choice([25, 40, 60, 85, 120, 180, 250, 400]) * 1000)
            close = pd.Timestamp(start) + pd.Timedelta(days=int(RNG.integers(0, 89)))
            # Rep estimate bias: strongly optimistic on losses (classic sandbagging failure)
            if won:
                rep_est = amount * float(RNG.uniform(0.90, 1.08))
            else:
                # Reps still carried most of the amount in their forecast
                rep_est = amount * float(RNG.uniform(0.65, 0.98))
            intensity = "hot" if won else "cold"
            days_since = int(RNG.integers(0, 8) if won else RNG.integers(22, 55))
            has_eb = 1 if won else (1 if RNG.random() > 0.65 else 0)
            rows.append(
                {
                    "deal_id": f"D-{deal_id}",
                    "account": f"{RNG.choice(INDUSTRIES)} Corp {deal_id % 97}",
                    "rep": str(RNG.choice(REPS)),
                    "industry": str(RNG.choice(INDUSTRIES)),
                    "stage": stage,
                    "amount": amount,
                    "created_date": (close - pd.Timedelta(days=int(RNG.integers(40, 160)))).strftime("%Y-%m-%d"),
                    "close_date": close.strftime("%Y-%m-%d"),
                    "forecast_quarter": q_name,
                    "days_since_activity": days_since,
                    "email_opens_14d": int(RNG.integers(0, 2) if not won else RNG.integers(5, 18)),
                    "meetings_30d": int(RNG.integers(0, 1) if not won else RNG.integers(2, 6)),
                    "stakeholders": _stakeholders(missing_key=not bool(has_eb)),
                    "has_economic_buyer": has_eb,
                    "engagement_score": float(RNG.uniform(0.62, 0.95) if won else RNG.uniform(0.12, 0.42)),
                    "rep_forecast_amount": round(rep_est, 2),
                    "actual_revenue": amount if won else 0.0,
                    "is_open": 0,
                    "activity_history": _activity_history(days_since, intensity),
                    "notes": _note_snippet(intensity),
                }
            )
            deal_id += 1

    # Open pipeline (as of end of Q1 2026 looking into Q2)
    for _ in range(n_open):
        stage = str(RNG.choice(OPEN_STAGES, p=[0.18, 0.22, 0.22, 0.2, 0.18]))
        amount = float(RNG.choice([30, 45, 70, 95, 140, 200, 320, 500]) * 1000)
        # Inject risk patterns intentionally
        risk_bucket = str(RNG.choice(["healthy", "stalled", "engagement_drop", "missing_eb"], p=[0.4, 0.22, 0.2, 0.18]))
        if risk_bucket == "stalled":
            days_since = int(RNG.integers(21, 55))
            eng = float(RNG.uniform(0.15, 0.4))
            emails, meetings = int(RNG.integers(0, 2)), int(RNG.integers(0, 1))
            missing_eb = RNG.random() > 0.4
            intensity = "cold"
        elif risk_bucket == "engagement_drop":
            days_since = int(RNG.integers(10, 25))
            eng = float(RNG.uniform(0.2, 0.45))
            emails, meetings = int(RNG.integers(0, 3)), int(RNG.integers(0, 2))
            missing_eb = RNG.random() > 0.5
            intensity = "cold"
        elif risk_bucket == "missing_eb":
            days_since = int(RNG.integers(5, 18))
            eng = float(RNG.uniform(0.4, 0.7))
            emails, meetings = int(RNG.integers(2, 8)), int(RNG.integers(1, 3))
            missing_eb = True
            intensity = "warm"
        else:
            days_since = int(RNG.integers(0, 10))
            eng = float(RNG.uniform(0.6, 0.95))
            emails, meetings = int(RNG.integers(4, 16)), int(RNG.integers(2, 6))
            missing_eb = False
            intensity = "hot"

        close = as_of + pd.Timedelta(days=int(RNG.integers(10, 90)))
        # Optimistic rep estimates on open deals
        rep_est = amount * float(RNG.uniform(0.7, 1.0)) * STAGE_WIN_RATE[stage] * float(RNG.uniform(1.05, 1.35))

        rows.append(
            {
                "deal_id": f"D-{deal_id}",
                "account": f"{RNG.choice(INDUSTRIES)} Corp {deal_id % 97}",
                "rep": str(RNG.choice(REPS)),
                "industry": str(RNG.choice(INDUSTRIES)),
                "stage": stage,
                "amount": amount,
                "created_date": (as_of - pd.Timedelta(days=int(RNG.integers(20, 140)))).strftime("%Y-%m-%d"),
                "close_date": close.strftime("%Y-%m-%d"),
                "forecast_quarter": "2026-Q2",
                "days_since_activity": days_since,
                "email_opens_14d": emails,
                "meetings_30d": meetings,
                "stakeholders": _stakeholders(missing_key=missing_eb),
                "has_economic_buyer": 0 if missing_eb else 1,
                "engagement_score": eng,
                "rep_forecast_amount": round(rep_est, 2),
                "actual_revenue": np.nan,
                "is_open": 1,
                "activity_history": _activity_history(days_since, intensity),
                "notes": _note_snippet(intensity),
                "risk_seed": risk_bucket,
            }
        )
        deal_id += 1

    df = pd.DataFrame(rows)
    if "risk_seed" not in df.columns:
        df["risk_seed"] = ""
    df["risk_seed"] = df["risk_seed"].fillna("")
    return df


def main() -> None:
    df = generate()
    out = ROOT / "deals.csv"
    df.to_csv(out, index=False)
    meta = {
        "n_deals": len(df),
        "n_open": int(df["is_open"].sum()),
        "n_closed": int((1 - df["is_open"]).sum()),
        "stage_win_rates": STAGE_WIN_RATE,
        "as_of": "2026-03-31",
        "backtest_holdout_quarter": "2026-Q1",
    }
    (ROOT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote {len(df)} deals -> {out}")


if __name__ == "__main__":
    main()
