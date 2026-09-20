import traceback
try:
    import pipeline_forge
    print("pipeline_forge OK", getattr(pipeline_forge, "__file__", None))
    from pipeline_forge.rag.ingest import build_vector_store
    print("Building vector store (force_rebuild=True)...")
    build_vector_store(force_rebuild=True)
    print("Vector store OK")
    from pipeline_forge.agents.graph import run_leadership_briefing
    print("Running leadership briefing...")
    result = run_leadership_briefing()
    fc = result.get("forecast") or {}
    risks = result.get("risks") or []
    bt = result.get("backtest") or {}
    recs = result.get("recommendations") or []
    print("=== METRICS ===")
    print("p50:", fc.get("p50"))
    print("risk_count:", len(risks))
    print("backtest_model_APE:", bt.get("model_abs_pct_error"))
    print("backtest_rep_APE:", bt.get("rep_abs_pct_error"))
    print("first_action:", (recs[0].get("action") if recs else None))
    print("holdout:", bt.get("holdout_quarter"))
    print("=== DONE ===")
except Exception:
    traceback.print_exc()
    raise
