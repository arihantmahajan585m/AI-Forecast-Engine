"""PipelineForge Interactive Terminal & CLI Agent Application (No Streamlit required)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
from pipeline_forge.rag.retrieve import ensure_index, retrieve_with_citations
from pipeline_forge.stats.forecast import forecast_closed_quarter_as_of, forecast_open_pipeline
from pipeline_forge.stats.risk import compute_stage_avg_days, rank_at_risk, score_deal
from pipeline_forge.stats.simulate import rep_calibration, simulate_salvage


def money(v: float) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:,.0f}"


def print_banner():
    print("\n" + "═" * 74)
    print(" ◈ PIPELINEFORGE — REVENUE INTELLIGENCE & DEAL RISK AGENT (TERMINAL CLI)")
    print(" 100% Offline / Free Stack · LangGraph Orchestration · Monte Carlo Forecast")
    print("═" * 74 + "\n")


def action_briefing(quarter: str = "2026-Q2"):
    print(f"\n▶ RUNNING MONDAY COMMIT BRIEFING AGENT ({quarter})...")
    print("   Orchestrating: forecast -> risk -> backtest -> RAG -> simulate -> narrative")
    res = run_leadership_briefing(quarter)

    fc = res.get("forecast") or {}
    bt = res.get("backtest") or {}
    recs = res.get("recommendations") or []
    sim = res.get("simulation") or {}

    print("\n" + "─" * 60)
    print(f"📊 FORECAST SUMMARY ({quarter})")
    print("─" * 60)
    print(f"  • P10 Forecast     : {money(fc.get('p10'))}")
    print(f"  • P50 Forecast     : {money(fc.get('p50'))}  <-- Executive Baseline")
    print(f"  • P90 Forecast     : {money(fc.get('p90'))}")
    print(f"  • Expected Revenue : {money(fc.get('expected'))}")
    print(f"  • Rep Roll-up      : {money(fc.get('rep_roll_up'))}  (Optimism gap: {money(fc.get('rep_roll_up',0) - fc.get('p50',0))})")

    if bt:
        print("\n" + "─" * 60)
        print(f"🧪 COMPULSORY HOLDOUT VERDICT ({bt.get('holdout_quarter')})")
        print("─" * 60)
        print(f"  • Actual Closed    : {money(bt.get('actual_revenue'))}")
        print(f"  • Model Expected   : {money(bt.get('model_expected'))} (APE: {bt.get('model_abs_pct_error'):.1f}%)")
        print(f"  • Rep Roll-Up      : {money(bt.get('rep_forecast_total'))} (APE: {bt.get('rep_abs_pct_error'):.1f}%)")
        delta = bt.get('error_improvement_pp', 0)
        print(f"  • VERDICT          : Model outperforms reps by +{delta:.1f} pp absolute error!")

    print("\n" + "─" * 60)
    print("📋 TOP ACTION QUEUE (GROUNDED IN PLAYBOOKS)")
    print("─" * 60)
    for i, r in enumerate(recs[:5], 1):
        cites = ", ".join(r.get("citation_ids") or [])
        print(f"  {i}. Deal {r.get('deal_id')} ({r.get('account')}) — Band: {r.get('risk_band', '').upper()} ({r.get('risk_score')})")
        print(f"     Action   : {r.get('action')}")
        print(f"     Citations: [{cites}]")
        print()

    print("─" * 60)
    print("📝 AGENT NARRATIVE SUMMARY")
    print("─" * 60)
    print(res.get("narrative") or "No narrative.")

    print("\n🔍 Execution Trace:", " -> ".join(res.get("trace") or []))


def action_risk_cockpit(min_risk: float = 0.2, top_n: int = 10):
    df = pd.read_csv(DEALS_CSV)
    stage_avg = compute_stage_avg_days(df)
    risks = rank_at_risk(df, min_score=min_risk, top_n=top_n, stage_avg_days=stage_avg)

    print(f"\n🔴 RISK COCKPIT — TOP {len(risks)} DEALS (Min score >= {min_risk})")
    print("─" * 74)
    print(f"{'DEAL ID':<8} {'ACCOUNT':<22} {'STAGE':<14} {'ACV':<10} {'RISK':<6} {'BAND':<9} {'SIGNALS'}")
    print("─" * 74)
    for r in risks:
        sigs = ",".join(s["code"] for s in r["signals"])
        print(f"{r['deal_id']:<8} {r['account'][:21]:<22} {r['stage']:<14} {money(r['amount']):<10} {r['risk_score']:<6.2f} {r['risk_band'].upper():<9} {sigs}")
    print("─" * 74)


def action_deal_deep_dive(deal_id: str):
    print(f"\n🔬 DEEP DIVE ON DEAL: {deal_id}")
    df = pd.read_csv(DEALS_CSV)
    refresh_deals(df)

    res = run_deal_deep_dive(deal_id)
    if res.get("errors"):
        print("❌ Error:", ", ".join(res["errors"]))
        return

    scored = (res.get("risks") or [{}])[0]
    rec = (res.get("recommendations") or [{}])[0]
    cites = res.get("citations") or []

    print("─" * 60)
    print(f"Account    : {scored.get('account')}")
    print(f"Stage      : {scored.get('stage')}")
    print(f"Amount     : {money(scored.get('amount'))}")
    print(f"Days Silent: {scored.get('days_since_activity')}d")
    print(f"EB Mapped  : {'Yes ✓' if scored.get('has_economic_buyer') else 'No ✗'}")
    print(f"Risk Score : {scored.get('risk_score')} ({scored.get('risk_band', '').upper()})")
    print("─" * 60)

    print("\n⚡ Signal Breakdown:")
    for s in scored.get("signals", []):
        print(f"  • {s['code']} (weight {s['weight']:.0%}): {s['evidence']}")

    print("\n🎯 Recommended Action:")
    print(f"  {rec.get('action')}")

    if cites:
        print("\n📚 Grounded Citations:")
        for c in cites[:3]:
            print(f"  [{c['id']}] ({c['source']}) {c['excerpt'][:120]}...")


def action_commit_simulator(deal_ids_str: str, strength: float = 0.55):
    df = pd.read_csv(DEALS_CSV)
    ids = [x.strip() for x in deal_ids_str.split(",") if x.strip()]
    print(f"\n🚀 COMMIT SIMULATOR — Intervening on {len(ids)} deals with strength {strength:.0%}")

    sim = simulate_salvage(df, ids, salvage_strength=strength, quarter="2026-Q2")
    if sim.get("error"):
        print("❌ Error:", sim["error"])
        return

    print("─" * 60)
    print(f"Baseline P50  : {money(sim.get('baseline_p50'))}")
    print(f"Scenario P50  : {money(sim.get('scenario_p50'))}")
    print(f"P50 Lift      : +{money(sim.get('p50_lift'))}")
    print(f"Deals Touched : {sim.get('n_intervened')}")
    print("─" * 60)

    print("\nPer-Deal Impact:")
    for d in sim.get("deals", []):
        print(f"  • {d['deal_id']} ({d['account']}): Risk {d['risk_before']:.2f} -> {d['risk_after']:.2f} | Win Prob {d['p_before']:.0%} -> {d['p_after']:.0%} | Lift: +{money(d['weighted_lift'])}")


def action_backtest_lab():
    df = pd.read_csv(DEALS_CSV)
    print(f"\n🧪 COMPULSORY HOLDOUT BACKTEST ({BACKTEST_HOLDOUT})")
    bt = forecast_closed_quarter_as_of(df, BACKTEST_HOLDOUT)

    print("─" * 60)
    print(f"Holdout Quarter   : {bt['holdout_quarter']}")
    print(f"Closed Deals      : {bt['n_deals']}")
    print(f"Actual Revenue    : {money(bt['actual_revenue'])}")
    print(f"Model Expected    : {money(bt['model_expected'])} (APE: {bt['model_abs_pct_error']:.1f}%)")
    print(f"Rep Forecast      : {money(bt['rep_forecast_total'])} (APE: {bt['rep_abs_pct_error']:.1f}%)")
    print(f"Error Improvement : +{bt['error_improvement_pp']:.1f} pp model superiority")
    print(f"Inside P10-P90    : {'Yes ✓' if bt['within_p10_p90'] else 'No ✗'}")
    print("─" * 60)

    print("\n👤 Sales Rep Calibration Breakdown:")
    reps = rep_calibration(df)
    print(f"{'REP':<15} {'CLOSED':<8} {'WON':<6} {'WIN RATE':<10} {'ACTUAL':<12} {'REP FORECAST':<14} {'APE %':<8}")
    print("─" * 74)
    for r in reps:
        print(f"{r['rep']:<15} {r['n_closed']:<8} {r['won']:<6} {r['win_rate']:<10.0%} {money(r['actual_revenue']):<12} {money(r['rep_forecast']):<14} {r['abs_pct_error']:<8.1f}%")


def action_ask(query: str):
    print(f"\n💬 ASK THE AGENT: \"{query}\"")
    df = pd.read_csv(DEALS_CSV)
    refresh_deals(df)

    res = run_ask(query)
    print("\n💡 Answer:")
    print(res.get("narrative"))

    if res.get("citations"):
        print("\n📚 Grounded Citations:")
        for c in res["citations"][:4]:
            print(f"  [{c['id']}] ({c['source']}) {c['excerpt'][:140]}...")

    print("\n🔍 Agent Execution Trace:", " -> ".join(res.get("trace") or []))


def interactive_menu():
    print_banner()
    while True:
        print("\nMAIN MENU:")
        print("  [1] Run Monday Commit Briefing (LangGraph Agent)")
        print("  [2] Inspect Deal Risk Cockpit")
        print("  [3] Deep Dive on a Specific Deal")
        print("  [4] Run Commit Simulator (Monte Carlo Salvage Scenario)")
        print("  [5] Run Compulsory Holdout Backtest (Feature 7 vs Reps)")
        print("  [6] Ask the Agent (Natural Language ReAct Routing)")
        print("  [0] Exit")

        try:
            choice = input("\nSelect an option [0-6]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            action_briefing()
        elif choice == "2":
            action_risk_cockpit()
        elif choice == "3":
            did = input("Enter Deal ID (e.g. D-1113): ").strip() or "D-1113"
            action_deal_deep_dive(did)
        elif choice == "4":
            dids = input("Enter comma-separated Deal IDs (e.g. D-1113,D-1140): ").strip() or "D-1113,D-1140,D-1147"
            action_commit_simulator(dids)
        elif choice == "5":
            action_backtest_lab()
        elif choice == "6":
            q = input("Enter your question: ").strip() or "What is our P50 forecast and which deals are most at risk?"
            action_ask(q)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


def main():
    parser = argparse.ArgumentParser(description="PipelineForge Terminal CLI Agent Application")
    parser.add_argument("--briefing", action="store_true", help="Run Monday Leadership Briefing")
    parser.add_argument("--risk", action="store_true", help="Inspect Risk Cockpit")
    parser.add_argument("--deep-dive", type=str, help="Deep dive on a specific deal ID")
    parser.add_argument("--simulate", type=str, help="Simulate salvage on comma-separated deal IDs")
    parser.add_argument("--backtest", action="store_true", help="Run compulsory holdout backtest")
    parser.add_argument("--ask", type=str, help="Ask the agent a natural language question")

    args = parser.parse_args()

    if args.briefing:
        print_banner()
        action_briefing()
    elif args.risk:
        print_banner()
        action_risk_cockpit()
    elif args.deep_dive:
        print_banner()
        action_deal_deep_dive(args.deep_dive)
    elif args.simulate:
        print_banner()
        action_commit_simulator(args.simulate)
    elif args.backtest:
        print_banner()
        action_backtest_lab()
    elif args.ask:
        print_banner()
        action_ask(args.ask)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
