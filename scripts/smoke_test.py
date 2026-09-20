"""End-to-end smoke test — no Groq key required."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

# Safe encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []
    print("1) Generate CRM...")
    from data.generate_crm import main as gen

    gen()

    print("2) Build RAG index...")
    from pipeline_forge.rag.retrieve import ensure_index, retrieve_with_citations

    meta = ensure_index()
    print("   ", meta)
    cites = retrieve_with_citations("missing economic buyer next action", k=3)
    print(f"   retrieved {len(cites)} citations")
    if not cites:
        errors.append("RAG returned zero citations")

    print("3) Forecast + risk + backtest...")
    import pandas as pd

    from pipeline_forge.config import BACKTEST_HOLDOUT, DEALS_CSV
    from pipeline_forge.stats.forecast import forecast_closed_quarter_as_of, forecast_open_pipeline
    from pipeline_forge.stats.risk import rank_at_risk

    df = pd.read_csv(DEALS_CSV)
    fc = forecast_open_pipeline(df, quarter="2026-Q2")
    risks = rank_at_risk(df, min_score=0.2, top_n=5)
    bt = forecast_closed_quarter_as_of(df, BACKTEST_HOLDOUT)
    print(f"   P50={fc['p50']} rep={fc['rep_roll_up']} n_risk={len(risks)}")
    print(
        f"   backtest APE model={bt.get('model_abs_pct_error')}% "
        f"rep={bt.get('rep_abs_pct_error')}% "
        f"delta_pp=+{bt.get('error_improvement_pp')}pp"
    )
    if bt.get("error"):
        errors.append(bt["error"])
    elif bt.get("error_improvement_pp", 0) <= 0:
        errors.append("Model did not beat reps on holdout quarter")
    if fc["n_deals"] < 10:
        errors.append("Too few open deals")
    if not risks:
        errors.append("No risk deals flagged")

    # Verify signals include variety
    all_signal_codes = {s["code"] for r in risks for s in r.get("signals", [])}
    print(f"   observed risk signals: {all_signal_codes}")

    print("4) LangGraph leadership briefing...")
    from pipeline_forge.agents.graph import run_ask, run_deal_deep_dive, run_leadership_briefing
    from pipeline_forge.agents.tools import refresh_deals

    refresh_deals(df)
    briefing = run_leadership_briefing("2026-Q2")
    trace_str = " -> ".join(briefing.get("trace") or [])[:200]
    print(f"   trace: {trace_str}")
    print(f"   narrative snippet: {(briefing.get('narrative') or '')[:160]}")
    if not briefing.get("forecast"):
        errors.append("Leadership missing forecast")
    if not briefing.get("recommendations"):
        errors.append("Leadership missing recommendations")
    if not briefing.get("citations"):
        errors.append("Leadership missing citations")

    print("5) Deal deep dive + ask...")
    deal_id = risks[0]["deal_id"]
    deep = run_deal_deep_dive(deal_id)
    ask = run_ask("What is our P50 and which deals are most at risk?")
    print(f"   deep errors: {deep.get('errors')}")
    print(f"   ask narrative: {(ask.get('narrative') or '')[:160]}")

    print("6) Tools decorated...")
    from pipeline_forge.agents.tools import ALL_TOOLS

    for t in ALL_TOOLS:
        assert t.name and t.description, t
        print(f"  - {t.name}")

    print("7) Commit simulator...")
    from pipeline_forge.stats.simulate import simulate_salvage

    sim = simulate_salvage(df, [r["deal_id"] for r in risks[:5]], salvage_strength=0.55)
    print(f"   p50_lift={sim.get('p50_lift')} n={sim.get('n_intervened')}")
    if sim.get("n_intervened", 0) < 1:
        errors.append("Simulator touched zero deals")

    if errors:
        print(f"FAIL: {errors}")
        return 1
    print("SMOKE OK")
    print(
        json.dumps(
            {
                "forecast_p50": fc["p50"],
                "backtest_delta_pp": bt.get("error_improvement_pp"),
                "chunks": meta.get("chunks"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
