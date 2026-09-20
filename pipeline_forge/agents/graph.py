"""LangGraph orchestration: multi-step forecast → risk → RAG → recommendations + ReAct ask."""
from __future__ import annotations

import json
import re
from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from pipeline_forge.agents.tools import (
    ALL_TOOLS,
    load_deals,
    tool_backtest_holdout,
    tool_forecast_pipeline,
    tool_rank_risk_deals,
    tool_rep_calibration,
    tool_retrieve_playbook,
    tool_score_deal,
    tool_simulate_commit,
)
from pipeline_forge.config import BACKTEST_HOLDOUT, GROQ_API_KEY, GROQ_MODEL
from pipeline_forge.rag.retrieve import retrieve_with_citations


class AgentState(TypedDict, total=False):
    mode: str
    quarter: str
    deal_id: str
    question: str
    forecast: dict[str, Any]
    risks: list[dict[str, Any]]
    backtest: dict[str, Any]
    simulation: dict[str, Any]
    calibration: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    narrative: str
    trace: list[str]
    errors: list[str]
    messages: list[Any]


def _llm_available() -> bool:
    return bool(GROQ_API_KEY)


def _chat(system: str, user: str) -> str:
    if not _llm_available():
        return ""
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_groq import ChatGroq

        llm = ChatGroq(model=GROQ_MODEL, temperature=0.2, api_key=GROQ_API_KEY)
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        return str(resp.content)
    except Exception as e:
        return f"[LLM unavailable: {e}]"


def node_forecast(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    quarter = state.get("quarter") or "2026-Q2"
    trace.append(f"tool_forecast_pipeline(quarter={quarter})")
    raw = tool_forecast_pipeline.invoke({"quarter": quarter})
    forecast = json.loads(raw)
    return {**state, "forecast": forecast, "trace": trace}


def node_risk(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    trace.append("tool_rank_risk_deals(top_n=12)")
    raw = tool_rank_risk_deals.invoke({"top_n": 12, "min_score": 0.2})
    risks = json.loads(raw)
    return {**state, "risks": risks, "trace": trace}


def node_backtest(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    holdout = BACKTEST_HOLDOUT
    trace.append(f"tool_backtest_holdout(quarter={holdout})")
    raw = tool_backtest_holdout.invoke({"quarter": holdout})
    return {**state, "backtest": json.loads(raw), "trace": trace}


def _rule_recommendation(deal: dict[str, Any], citations: list[dict[str, Any]]) -> dict[str, Any]:
    codes = {s["code"] for s in deal.get("signals", [])}
    cite_ids = [c["id"] for c in citations[:3]]
    if "missing_economic_buyer" in codes:
        action = (
            "Request economic-buyer intro this week; run a 20-min ROI review — "
            "or haircut forecast 30–40%."
        )
        why = "No EB mapped at late stage; playbook: EB absence halves conversion."
    elif "stalled_activity" in codes:
        action = (
            "Send a breakup email with a 5-business-day decision deadline; "
            "re-qualify mutual close plan."
        )
        why = f"Stalled {deal.get('days_since_activity')} days — recovery playbook applies."
    elif "engagement_drop" in codes:
        action = (
            "Switch channel to call + multi-thread a second stakeholder; "
            "surface a business trigger date."
        )
        why = "Engagement below threshold; velocity pattern predicts loss without intervention."
    else:
        action = "Lock a dated mutual close plan (security/legal/signature owners)."
        why = "Elevated composite risk; tighten decision process."
    return {
        "deal_id": deal.get("deal_id"),
        "account": deal.get("account"),
        "risk_band": deal.get("risk_band"),
        "risk_score": deal.get("risk_score"),
        "action": action,
        "rationale": why,
        "citation_ids": cite_ids,
        "signals": deal.get("signals", []),
    }


def node_rag_and_recommend(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    risks = state.get("risks") or []
    recommendations = []
    all_cites: list[dict[str, Any]] = []

    themes = []
    for d in risks[:8]:
        for s in d.get("signals", []):
            themes.append(s.get("code", ""))
    query = " ".join(themes) or "stalled deal economic buyer engagement drop next best action"
    query = f"playbook actions for: {query}"
    trace.append(f"tool_retrieve_playbook(query={query[:80]}...)")
    raw = tool_retrieve_playbook.invoke({"query": query, "k": 5})
    payload = json.loads(raw)
    cites = payload.get("citations") or []
    all_cites.extend(cites)

    for deal in risks[:8]:
        dq = (
            f"{deal.get('stage')} risk {' '.join(s['code'] for s in deal.get('signals', []))} "
            f"next best action economic buyer stalled engagement"
        )
        trace.append(f"retrieve_with_citations(deal={deal.get('deal_id')})")
        deal_cites = retrieve_with_citations(dq, k=3)
        for c in deal_cites:
            if c["excerpt"] not in {x["excerpt"] for x in all_cites}:
                all_cites.append(c)
        rec = _rule_recommendation(deal, deal_cites)
        rec["llm_grounded"] = True
        if rec.get("citation_ids"):
            rec["action"] = rec["action"] + " " + " ".join(f"[{i}]" for i in rec["citation_ids"])
        recommendations.append(rec)

    return {
        **state,
        "recommendations": recommendations,
        "citations": all_cites[:12],
        "trace": trace,
    }


def node_simulate(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    recs = state.get("recommendations") or []
    ids = ",".join(str(r.get("deal_id")) for r in recs[:8] if r.get("deal_id"))
    quarter = state.get("quarter") or "2026-Q2"
    if not ids:
        return {**state, "simulation": {}, "calibration": [], "trace": trace}
    trace.append(f"tool_simulate_commit(deals={ids[:60]})")
    sim = json.loads(
        tool_simulate_commit.invoke({"deal_ids": ids, "salvage_strength": 0.55, "quarter": quarter})
    )
    trace.append("tool_rep_calibration()")
    cal = json.loads(tool_rep_calibration.invoke({}))
    return {**state, "simulation": sim, "calibration": cal, "trace": trace}


def node_narrative(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    fc = state.get("forecast") or {}
    bt = state.get("backtest") or {}
    risks = state.get("risks") or []
    recs = state.get("recommendations") or []
    sim = state.get("simulation") or {}

    lift = sim.get("p50_lift")
    lift_txt = (
        f" If the action queue lands this week, simulated P50 lifts by ${lift:,.0f} "
        f"to ${sim.get('scenario_p50', 0):,.0f}."
        if lift is not None
        else ""
    )
    fallback = (
        f"Forecast for {fc.get('quarter', 'open pipeline')}: "
        f"P50 ${fc.get('p50', 0):,.0f} (P10–P90 ${fc.get('p10', 0):,.0f}–${fc.get('p90', 0):,.0f}). "
        f"Rep roll-up ${fc.get('rep_roll_up', 0):,.0f} sits above the model — typical optimism bias. "
        f"{len(risks)} deals flagged; top action queue prepared. "
        f"Holdout {bt.get('holdout_quarter')}: model APE {bt.get('model_abs_pct_error')}% vs rep "
        f"{bt.get('rep_abs_pct_error')}% (improvement {bt.get('error_improvement_pp')} pp)."
        + lift_txt
    )

    if _llm_available():
        sys = (
            "You are PipelineForge, a revenue intelligence briefing for a CRO. "
            "Be specific with numbers. 3 short paragraphs max. No fluff."
        )
        user = json.dumps(
            {
                "forecast": {
                    k: fc.get(k)
                    for k in [
                        "quarter",
                        "p10",
                        "p50",
                        "p90",
                        "expected",
                        "commit",
                        "rep_roll_up",
                        "n_deals",
                    ]
                },
                "backtest": bt,
                "top_risks": [
                    {
                        "deal_id": r.get("deal_id"),
                        "band": r.get("risk_band"),
                        "score": r.get("risk_score"),
                        "signals": r.get("signals"),
                    }
                    for r in risks[:5]
                ],
                "actions": [{"deal_id": r.get("deal_id"), "action": r.get("action")} for r in recs[:5]],
                "simulation": {
                    "p50_lift": sim.get("p50_lift"),
                    "scenario_p50": sim.get("scenario_p50"),
                    "n_intervened": sim.get("n_intervened"),
                },
            }
        )
        text = _chat(sys, user)
        narrative = text.strip() if text and not text.startswith("[LLM unavailable") else fallback
    else:
        narrative = fallback

    trace.append("narrative_synthesis")
    return {**state, "narrative": narrative, "trace": trace}


def node_deal_deep_dive(state: AgentState) -> AgentState:
    trace = list(state.get("trace") or [])
    deal_id = state.get("deal_id") or ""
    errors = list(state.get("errors") or [])
    if not deal_id:
        errors.append("No deal_id provided for deep dive.")
        return {**state, "errors": errors, "trace": trace}

    trace.append(f"tool_score_deal({deal_id})")
    scored = json.loads(tool_score_deal.invoke({"deal_id": deal_id}))
    if scored.get("error"):
        errors.append(scored["error"])
        return {**state, "errors": errors, "trace": trace}

    q = (
        f"next best action for {scored.get('stage')} deal with signals "
        + ",".join(s["code"] for s in scored.get("signals", []))
    )
    trace.append("tool_retrieve_playbook")
    cites = json.loads(tool_retrieve_playbook.invoke({"query": q, "k": 4})).get("citations", [])
    rec = _rule_recommendation(scored, cites)
    if _llm_available():
        sys = (
            "You are a sales risk coach. Use ONLY CRM evidence and cited passages. "
            "One concrete next action, max 2 sentences, cite [C1] style IDs. No vague advice."
        )
        text = _chat(sys, json.dumps({"deal": scored, "citations": cites}))
        if text and not text.startswith("[LLM unavailable"):
            rec["action"] = text.strip()
            rec["llm_grounded"] = True
    return {
        **state,
        "risks": [scored],
        "recommendations": [rec],
        "citations": cites,
        "trace": trace,
        "errors": errors,
        "narrative": rec.get("action"),
    }


def node_ask_router(state: AgentState) -> AgentState:
    """Deterministic multi-tool routing when no LLM, or first pass before ReAct."""
    trace = list(state.get("trace") or [])
    q = (state.get("question") or "").strip()
    errors = list(state.get("errors") or [])
    if not q:
        errors.append("Empty question.")
        return {**state, "errors": errors}

    ql = q.lower()
    forecast = state.get("forecast")
    risks = state.get("risks")
    backtest = state.get("backtest")
    citations = list(state.get("citations") or [])
    recs = list(state.get("recommendations") or [])

    # Always retrieve playbook for grounding
    need_forecast = any(w in ql for w in ["forecast", "p50", "pipeline", "revenue", "commit", "p10", "p90"])
    need_risk = any(w in ql for w in ["risk", "at-risk", "stalled", "danger", "slip", "engagement", "buyer"])
    need_backtest = any(w in ql for w in ["backtest", "accuracy", "rep estimate", "holdout", "error", "actual"])
    need_sim = any(w in ql for w in ["simulat", "lift", "what if", "what-if", "salvage", "intervene"])
    need_cal = any(w in ql for w in ["calibration", "sandbag", "rep accuracy", "which rep"])
    m = re.search(r"D-\d+", q, re.I)

    # Broad questions → run the core stack
    if not (need_forecast or need_risk or need_backtest or need_sim or need_cal or m):
        need_forecast = True
        need_risk = True

    if need_sim:
        need_risk = True

    if need_forecast:
        trace.append("ask→forecast")
        forecast = json.loads(tool_forecast_pipeline.invoke({"quarter": state.get("quarter") or "2026-Q2"}))
    if need_risk:
        trace.append("ask→risk")
        risks = json.loads(tool_rank_risk_deals.invoke({"top_n": 8, "min_score": 0.2}))
    if need_backtest:
        trace.append("ask→backtest")
        backtest = json.loads(tool_backtest_holdout.invoke({"quarter": BACKTEST_HOLDOUT}))
    simulation = state.get("simulation")
    calibration = state.get("calibration")
    if need_sim:
        trace.append("ask→simulate")
        ids = ",".join(str(r.get("deal_id")) for r in (risks or [])[:6] if r.get("deal_id"))
        if ids:
            simulation = json.loads(
                tool_simulate_commit.invoke(
                    {"deal_ids": ids, "salvage_strength": 0.55, "quarter": state.get("quarter") or "2026-Q2"}
                )
            )
    if need_cal:
        trace.append("ask→calibration")
        calibration = json.loads(tool_rep_calibration.invoke({}))

    if m:
        did = m.group(0).upper()
        trace.append(f"ask→deal {did}")
        scored = json.loads(tool_score_deal.invoke({"deal_id": did}))
        cites = retrieve_with_citations(q, k=4)
        citations.extend(cites)
        if not scored.get("error"):
            risks = [scored] + (risks or [])
            recs = [_rule_recommendation(scored, cites)]

    trace.append("ask→rag")
    rag = json.loads(tool_retrieve_playbook.invoke({"query": q, "k": 4}))
    citations = (rag.get("citations") or []) + citations

    if _llm_available():
        sys = (
            "Answer as PipelineForge using tool results and citations. "
            "Cite sources as [C1]. If data missing, say what tool would be needed. Be specific."
        )
        user = json.dumps(
            {
                "question": q,
                "forecast": forecast,
                "risks": (risks or [])[:5],
                "backtest": backtest,
                "recommendations": recs[:3],
                "simulation": simulation,
                "calibration": (calibration or [])[:4],
                "citations": citations[:6],
            }
        )
        narrative = _chat(sys, user) or "Unable to synthesize."
    else:
        parts = [f"**Q:** {q}"]
        if forecast:
            parts.append(
                f"Forecast P50 ${forecast.get('p50', 0):,.0f} "
                f"(band ${forecast.get('p10', 0):,.0f}–${forecast.get('p90', 0):,.0f}). "
                f"Rep roll-up ${forecast.get('rep_roll_up', 0):,.0f}."
            )
        if risks:
            parts.append(
                "Top risks: "
                + "; ".join(
                    f"{r.get('deal_id')} ({r.get('risk_band')}: "
                    + ", ".join(s.get("evidence", "")[:60] for s in (r.get("signals") or [])[:1])
                    + ")"
                    for r in risks[:5]
                )
            )
        if backtest:
            parts.append(
                f"Backtest {backtest.get('holdout_quarter')}: model APE "
                f"{backtest.get('model_abs_pct_error')}% vs rep {backtest.get('rep_abs_pct_error')}% "
                f"(Δ {backtest.get('error_improvement_pp')} pp)."
            )
        if simulation:
            parts.append(
                f"Commit simulator: intervening on {simulation.get('n_intervened')} deals lifts P50 by "
                f"${simulation.get('p50_lift', 0):,.0f} to ${simulation.get('scenario_p50', 0):,.0f}."
            )
        if calibration:
            worst = calibration[0]
            parts.append(
                f"Noisiest forecast: {worst.get('rep')} (APE {worst.get('abs_pct_error')}%)."
            )
        if citations:
            parts.append(
                "Grounded on: " + ", ".join(f"[{c['id']}] {c['source']}" for c in citations[:4])
            )
        narrative = "\n\n".join(parts)

    return {
        **state,
        "forecast": forecast or state.get("forecast"),
        "risks": risks or state.get("risks"),
        "backtest": backtest or state.get("backtest"),
        "simulation": simulation or state.get("simulation"),
        "calibration": calibration or state.get("calibration"),
        "citations": citations[:12],
        "recommendations": recs or state.get("recommendations"),
        "narrative": narrative,
        "trace": trace,
        "errors": errors,
    }


def node_ask_react(state: AgentState) -> AgentState:
    """True tool-calling ReAct loop with Groq when API key is present."""
    if not _llm_available():
        return node_ask_router(state)

    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
    from langchain_groq import ChatGroq

    q = (state.get("question") or "").strip()
    trace = list(state.get("trace") or [])
    errors = list(state.get("errors") or [])
    if not q:
        errors.append("Empty question.")
        return {**state, "errors": errors}

    llm = ChatGroq(model=GROQ_MODEL, temperature=0.1, api_key=GROQ_API_KEY)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    messages: list[Any] = [
        SystemMessage(
            content=(
                "You are PipelineForge. Use tools for numbers and retrieval — never invent forecasts. "
                "Call tools as needed (forecast, risk, backtest, retrieve_playbook, score_deal, simulate_commit, rep_calibration). "
                "Cite playbook IDs from tool_retrieve_playbook. Be concise and specific for a CRO."
            )
        ),
        HumanMessage(content=q),
    ]
    tool_map = {t.name: t for t in ALL_TOOLS}
    max_steps = 6
    for step in range(max_steps):
        trace.append(f"react_step_{step+1}")
        ai: AIMessage = llm_with_tools.invoke(messages)
        messages.append(ai)
        if not getattr(ai, "tool_calls", None):
            narrative = str(ai.content)
            return {**state, "narrative": narrative, "trace": trace, "messages": messages, "errors": errors}
        for tc in ai.tool_calls:
            name = tc["name"]
            args = tc.get("args") or {}
            trace.append(f"tool_call:{name}({json.dumps(args)[:80]})")
            tool = tool_map.get(name)
            if not tool:
                result = json.dumps({"error": f"Unknown tool {name}"})
            else:
                try:
                    result = tool.invoke(args)
                except Exception as e:
                    result = json.dumps({"error": str(e)})
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    # Final forced answer
    messages.append(HumanMessage(content="Synthesize a final answer now using tool results. Cite [C#] if available."))
    final = llm.invoke(messages)
    return {
        **state,
        "narrative": str(final.content),
        "trace": trace,
        "messages": messages,
        "errors": errors,
    }


def route_entry(state: AgentState) -> Literal["leadership", "deal", "ask"]:
    mode = state.get("mode") or "leadership"
    if mode == "deal":
        return "deal"
    if mode == "ask":
        return "ask"
    return "leadership"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("forecast", node_forecast)
    g.add_node("risk", node_risk)
    g.add_node("backtest", node_backtest)
    g.add_node("rag_recommend", node_rag_and_recommend)
    g.add_node("simulate", node_simulate)
    g.add_node("narrative", node_narrative)
    g.add_node("deal_deep_dive", node_deal_deep_dive)
    g.add_node("ask", node_ask_react)

    g.set_conditional_entry_point(
        route_entry,
        {"leadership": "forecast", "deal": "deal_deep_dive", "ask": "ask"},
    )
    g.add_edge("forecast", "risk")
    g.add_edge("risk", "backtest")
    g.add_edge("backtest", "rag_recommend")
    g.add_edge("rag_recommend", "simulate")
    g.add_edge("simulate", "narrative")
    g.add_edge("narrative", END)
    g.add_edge("deal_deep_dive", END)
    g.add_edge("ask", END)
    return g.compile()


_GRAPH = None


def get_graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


def run_leadership_briefing(quarter: str = "2026-Q2") -> dict[str, Any]:
    load_deals()
    graph = get_graph()
    return graph.invoke(
        {"mode": "leadership", "quarter": quarter, "trace": [], "errors": []},
        config={"recursion_limit": 25},
    )


def run_deal_deep_dive(deal_id: str) -> dict[str, Any]:
    load_deals()
    graph = get_graph()
    return graph.invoke(
        {"mode": "deal", "deal_id": deal_id, "trace": [], "errors": []},
        config={"recursion_limit": 15},
    )


def run_ask(question: str, quarter: str = "2026-Q2") -> dict[str, Any]:
    load_deals()
    graph = get_graph()
    return graph.invoke(
        {"mode": "ask", "question": question, "quarter": quarter, "trace": [], "errors": []},
        config={"recursion_limit": 20},
    )
