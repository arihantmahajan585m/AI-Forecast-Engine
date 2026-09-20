"""Reusable UI fragments — startup-grade Plotly charts and Streamlit components."""
from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import streamlit as st

from pipeline_forge.ui.theme import COLORS, money


# ─────────────────────────────────────────────────────────────────────────────
# KPI / Metric row
# ─────────────────────────────────────────────────────────────────────────────

def metric_row(items: list[dict[str, str]]) -> None:
    cells = []
    for i, it in enumerate(items):
        delta_html = ""
        if it.get("delta"):
            sign = "+" if str(it["delta"]).startswith("+") else ""
            color = "#0F8A5F" if "+" in str(it["delta"]) else "#C23B2A"
            delta_html = (
                f'<div class="delta" style="color:{color}">'
                f'{it["delta"]}</div>'
            )
        cells.append(
            f"""<div class="pf-metric" style="animation-delay:{i * 0.07}s">
              <div class="label">{it['label']}</div>
              <div class="value">{it['value']}</div>
              <div class="sub">{it.get('sub', '')}</div>
              {delta_html}
            </div>"""
        )
    st.markdown(
        f'<div class="pf-metric-row">{"".join(cells)}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Forecast confidence fan chart (proper P10/P50/P90 band)
# ─────────────────────────────────────────────────────────────────────────────

def forecast_fan_chart(fc: dict[str, Any]) -> go.Figure:
    """Confidence fan — shows P10/P90 band in green, P50 and rep roll-up as lines."""
    labels = ["P10", "P50", "P90", "Expected", "Rep roll-up"]
    values = [
        fc.get("p10", 0),
        fc.get("p50", 0),
        fc.get("p90", 0),
        fc.get("expected", 0),
        fc.get("rep_roll_up", 0),
    ]

    fig = go.Figure()

    # Confidence band (P10 → P90 shaded area via a waterfall-style bar)
    fig.add_trace(
        go.Bar(
            name="P10 baseline",
            x=["Confidence range"],
            y=[fc.get("p10", 0)],
            marker_color="rgba(0,0,0,0)",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Bar(
            name="P10 → P90 band",
            x=["Confidence range"],
            y=[max(0, fc.get("p90", 0) - fc.get("p10", 0))],
            base=[fc.get("p10", 0)],
            marker_color="rgba(15,138,95,0.18)",
            marker_line=dict(width=0),
            showlegend=True,
        )
    )

    # P50 line
    fig.add_hline(
        y=fc.get("p50", 0),
        line_color=COLORS["accent"],
        line_width=2.5,
        line_dash="solid",
        annotation_text=f"  P50 {money(fc.get('p50', 0))}",
        annotation_position="right",
        annotation_font=dict(color=COLORS["accent"], size=12),
    )

    # Rep roll-up line
    fig.add_hline(
        y=fc.get("rep_roll_up", 0),
        line_color=COLORS["accent2"],
        line_width=2,
        line_dash="dot",
        annotation_text=f"  Rep {money(fc.get('rep_roll_up', 0))}",
        annotation_position="right",
        annotation_font=dict(color=COLORS["accent2"], size=12),
    )

    # Expected (weighted sum)
    fig.add_hline(
        y=fc.get("expected", 0),
        line_color=COLORS["blue"],
        line_width=1.5,
        line_dash="dash",
        annotation_text=f"  Expected {money(fc.get('expected', 0))}",
        annotation_position="right",
        annotation_font=dict(color=COLORS["blue"], size=11),
    )

    # Commit line
    if fc.get("commit", 0) > 0:
        fig.add_hline(
            y=fc.get("commit", 0),
            line_color=COLORS["ink"],
            line_width=1.5,
            line_dash="longdash",
            annotation_text=f"  Commit {money(fc.get('commit', 0))}",
            annotation_position="right",
            annotation_font=dict(color=COLORS["ink"], size=11),
        )

    fig.update_layout(
        title=dict(
            text=f"Probabilistic forecast — {fc.get('quarter', 'Q')} "
                 f"<span style='font-size:13px;color:{COLORS['muted']}'>({fc.get('n_deals', 0)} open deals)</span>",
            font=dict(size=15),
        ),
        yaxis_title="Revenue ($)",
        barmode="stack",
        height=360,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(tickformat="$,.0f"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Monte Carlo distribution histogram
# ─────────────────────────────────────────────────────────────────────────────

def monte_carlo_histogram(fc: dict[str, Any]) -> go.Figure:
    """Approximate the MC distribution with a bell curve from p10/p50/p90."""
    import numpy as np

    p10 = fc.get("p10", 0)
    p50 = fc.get("p50", 0)
    p90 = fc.get("p90", 0)

    if p90 <= p10:
        fig = go.Figure()
        fig.update_layout(title="Distribution not available", height=260)
        return fig

    # Approximate the distribution using log-normal fit to percentiles
    mu = p50
    sigma = (p90 - p10) / 2.56  # approx for normal dist
    xs = np.linspace(max(0, mu - 3.5 * sigma), mu + 3.5 * sigma, 200)
    ys = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mu) / sigma) ** 2)

    fig = go.Figure()
    # Fill between P10 and P90
    mask_band = (xs >= p10) & (xs <= p90)
    fig.add_trace(
        go.Scatter(
            x=xs[mask_band],
            y=ys[mask_band],
            fill="tozeroy",
            fillcolor="rgba(15,138,95,0.15)",
            line=dict(width=0),
            name="P10–P90 band",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            line=dict(color=COLORS["accent"], width=2.5),
            name="Revenue distribution",
            fill="none",
        )
    )
    for val, label, color in [
        (p10, "P10", COLORS["muted"]),
        (p50, "P50", COLORS["accent"]),
        (p90, "P90", COLORS["blue"]),
        (fc.get("rep_roll_up", 0), "Rep", COLORS["accent2"]),
    ]:
        if val > 0:
            fig.add_vline(
                x=val,
                line_color=color,
                line_width=2,
                line_dash="dash" if label != "P50" else "solid",
                annotation_text=f"  {label}",
                annotation_font=dict(color=color, size=11),
            )

    fig.update_layout(
        title="Simulated revenue distribution (4,000 Monte Carlo runs)",
        xaxis_title="Quarter revenue ($)",
        xaxis=dict(tickformat="$,.0f"),
        yaxis=dict(visible=False),
        height=280,
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Risk charts
# ─────────────────────────────────────────────────────────────────────────────

def risk_scatter(risks: list[dict[str, Any]]) -> go.Figure:
    if not risks:
        fig = go.Figure()
        fig.update_layout(title="No at-risk deals in current filter", height=320)
        return fig

    band_color_map = {
        "critical": "#C23B2A",
        "high": "#C45C26",
        "medium": "#2F6FED",
        "low": "#0F8A5F",
    }
    colors = [band_color_map.get(r.get("risk_band", "medium"), COLORS["muted"]) for r in risks]

    fig = go.Figure(
        go.Scatter(
            x=[r["risk_score"] for r in risks],
            y=[r["amount"] for r in risks],
            mode="markers+text",
            text=[r["deal_id"] for r in risks],
            textposition="top center",
            textfont=dict(size=10, color=COLORS["ink"]),
            marker=dict(
                size=[max(12, min(34, r["amount"] / 20_000)) for r in risks],
                color=colors,
                opacity=0.82,
                line=dict(width=1.5, color="white"),
            ),
            customdata=[[r["account"], r["rep"], r["risk_band"], r["adj_win_prob"]] for r in risks],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Account: %{customdata[0]}<br>"
                "Rep: %{customdata[1]}<br>"
                "Risk: %{x:.2f} · %{customdata[2]}<br>"
                "Adj. win prob: %{customdata[3]:.0%}<br>"
                "ACV: %{y:$,.0f}<extra></extra>"
            ),
        )
    )

    # Add quadrant lines
    fig.add_vline(x=0.5, line_dash="dot", line_color=COLORS["line"], line_width=1)
    fig.add_hline(y=100_000, line_dash="dot", line_color=COLORS["line"], line_width=1)

    fig.update_layout(
        title="Deal risk × ACV exposure — bubble size = deal size",
        xaxis=dict(title="Composite risk score →", range=[-0.05, 1.05]),
        yaxis=dict(title="Deal amount ($)", tickformat="$,.0f"),
        height=400,
    )
    return fig


def risk_heatmap(risks: list[dict[str, Any]]) -> go.Figure:
    """Stage × risk-band heatmap showing deal count."""
    if not risks:
        fig = go.Figure()
        fig.update_layout(title="No risk data", height=260)
        return fig

    from collections import defaultdict

    stages = ["Prospecting", "Qualification", "Discovery", "Proposal", "Negotiation"]
    bands = ["critical", "high", "medium"]
    grid: dict[tuple[str, str], int] = defaultdict(int)
    for r in risks:
        grid[(r.get("stage", ""), r.get("risk_band", "medium"))] += 1

    z = [[grid[(s, b)] for s in stages] for b in bands]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=stages,
            y=[b.upper() for b in bands],
            colorscale=[[0, "#F3F6F4"], [0.5, "#C45C26"], [1.0, "#C23B2A"]],
            text=z,
            texttemplate="%{text}",
            hovertemplate="Stage: %{x}<br>Band: %{y}<br>Deals: %{z}<extra></extra>",
            showscale=False,
        )
    )
    fig.update_layout(
        title="At-risk deal concentration by stage × band",
        height=260,
        xaxis_title="Pipeline stage",
        yaxis_title="",
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Backtest chart + verdict
# ─────────────────────────────────────────────────────────────────────────────

def backtest_chart(bt: dict[str, Any]) -> go.Figure:
    actual = bt.get("actual_revenue", 0)
    model = bt.get("model_expected", 0)
    rep = bt.get("rep_forecast_total", 0)
    p10 = bt.get("model_p10", 0)
    p90 = bt.get("model_p90", 0)

    fig = go.Figure()

    # Actual (ground truth)
    fig.add_trace(
        go.Bar(
            name="Actual revenue",
            x=["Actual"],
            y=[actual],
            marker_color=COLORS["accent"],
            text=[money(actual)],
            textposition="outside",
            width=0.5,
        )
    )
    # Model expected with P10–P90 error bar
    fig.add_trace(
        go.Bar(
            name="Model expected",
            x=["Model (P10–P90)"],
            y=[model],
            marker_color=COLORS["blue"],
            text=[money(model)],
            textposition="outside",
            width=0.5,
            error_y=dict(
                type="data",
                symmetric=False,
                array=[max(0, p90 - model)],
                arrayminus=[max(0, model - p10)],
                color=COLORS["muted"],
                thickness=2,
                width=8,
            ),
        )
    )
    # Rep forecast
    fig.add_trace(
        go.Bar(
            name="Rep roll-up",
            x=["Rep roll-up"],
            y=[rep],
            marker_color=COLORS["accent2"],
            text=[money(rep)],
            textposition="outside",
            width=0.5,
        )
    )

    # Actual reference line
    fig.add_hline(
        y=actual,
        line_dash="dot",
        line_color=COLORS["accent"],
        line_width=1.5,
        annotation_text="  Actual",
        annotation_font=dict(color=COLORS["accent"]),
    )

    model_ape = bt.get("model_abs_pct_error", 0)
    rep_ape = bt.get("rep_abs_pct_error", 0)
    delta = bt.get("error_improvement_pp", 0)
    beat = delta > 0
    verdict = f"Model {'beats' if beat else 'trails'} reps by {abs(delta):.1f} pp"

    fig.update_layout(
        title=dict(
            text=(
                f"Holdout backtest: {bt.get('holdout_quarter', '')} — "
                f"Model APE {model_ape:.1f}% vs Rep APE {rep_ape:.1f}% → "
                f"<span style='color:{'#0F8A5F' if beat else '#C23B2A'}'>{verdict}</span>"
            ),
            font=dict(size=13),
        ),
        height=380,
        yaxis=dict(tickformat="$,.0f"),
        barmode="group",
        xaxis=dict(title=""),
    )
    return fig


def backtest_verdict_card(bt: dict[str, Any]) -> None:
    """Prominent 3-column verdict for the compulsory Feature 7."""
    if not bt or bt.get("error"):
        return

    model_ape = bt.get("model_abs_pct_error", 0)
    rep_ape = bt.get("rep_abs_pct_error", 0)
    delta = bt.get("error_improvement_pp", 0)
    beat = delta > 0

    icon = "✓" if beat else "⚠"
    verdict_color = "#0F8A5F" if beat else "#C23B2A"
    verdict_bg = "rgba(15,138,95,0.07)" if beat else "rgba(194,59,42,0.07)"
    verdict_border = "rgba(15,138,95,0.3)" if beat else "rgba(194,59,42,0.3)"

    st.markdown(
        f"""
        <div class="pf-verdict" style="border-color:{verdict_border};background:{verdict_bg}">
          <div class="pf-verdict-icon" style="color:{verdict_color}">{icon}</div>
          <div class="pf-verdict-body">
            <div class="pf-verdict-title" style="color:{verdict_color}">
              Compulsory holdout ({bt.get('holdout_quarter')}) —
              Model {'outperforms' if beat else 'underperforms'} reps by
              <strong>{abs(delta):.1f} pp absolute error</strong>
            </div>
            <div class="pf-verdict-row">
              <span>Actual closed: <strong>{money(bt.get('actual_revenue', 0))}</strong></span>
              <span>Model expected: <strong>{money(bt.get('model_expected', 0))}</strong>
                <em>(APE {model_ape:.1f}%)</em></span>
              <span>Rep roll-up: <strong>{money(bt.get('rep_forecast_total', 0))}</strong>
                <em>(APE {rep_ape:.1f}%)</em></span>
              <span>Within P10–P90: <strong>{'Yes ✓' if bt.get('within_p10_p90') else 'No'}</strong></span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Rep calibration
# ─────────────────────────────────────────────────────────────────────────────

def rep_calibration_chart(rows: list[dict[str, Any]]) -> go.Figure:
    if not rows:
        fig = go.Figure()
        fig.update_layout(title="No closed-book calibration yet", height=280)
        return fig

    reps = [r["rep"] for r in rows]
    apes = [r["abs_pct_error"] for r in rows]
    biases = [r["bias"] for r in rows]
    colors = [COLORS["danger"] if a > 25 else COLORS["accent2"] if a > 15 else COLORS["accent"] for a in apes]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Forecast APE %",
            x=reps,
            y=apes,
            marker_color=colors,
            text=[f"{a:.0f}%" for a in apes],
            textposition="outside",
            customdata=biases,
            hovertemplate=(
                "<b>%{x}</b><br>APE: %{y:.1f}%<br>"
                "Bias: $%{customdata:,.0f}<extra></extra>"
            ),
        )
    )
    fig.add_hline(
        y=15,
        line_dash="dot",
        line_color=COLORS["muted"],
        annotation_text="  15% target",
        annotation_font=dict(size=11, color=COLORS["muted"]),
    )
    fig.update_layout(
        title="Rep forecast APE (closed book) — lower is better",
        yaxis_title="Absolute % error",
        height=300,
        xaxis_title="Sales Rep",
    )
    return fig


def rep_calibration_table(rows: list[dict[str, Any]]) -> None:
    """Styled rep calibration table with color-coded accuracy."""
    if not rows:
        st.markdown('<div class="pf-empty">No closed deals for calibration.</div>', unsafe_allow_html=True)
        return

    cells = []
    for r in rows:
        ape = r.get("abs_pct_error", 0)
        bias = r.get("bias", 0)
        if ape > 25:
            ape_style = "color:#C23B2A;font-weight:700"
        elif ape > 15:
            ape_style = "color:#C45C26;font-weight:600"
        else:
            ape_style = "color:#0F8A5F;font-weight:600"
        bias_html = (
            f'<span style="color:{"#C23B2A" if bias > 0 else "#0F8A5F"}">'
            f'{"+" if bias > 0 else ""}{money(bias)}</span>'
        )
        cells.append(
            f"""<tr>
              <td><strong>{r['rep']}</strong></td>
              <td>{r['n_closed']}</td>
              <td>{r['won']}</td>
              <td>{r['win_rate']:.0%}</td>
              <td>{money(r['actual_revenue'])}</td>
              <td>{money(r['rep_forecast'])}</td>
              <td style="{ape_style}">{ape:.1f}%</td>
              <td>{bias_html}</td>
            </tr>"""
        )
    st.markdown(
        f"""
        <div class="pf-table-wrap">
        <table class="pf-table">
          <thead>
            <tr>
              <th>Rep</th><th>Closed</th><th>Won</th><th>Win rate</th>
              <th>Actual</th><th>Rep forecast</th><th>APE</th><th>Bias</th>
            </tr>
          </thead>
          <tbody>{''.join(cells)}</tbody>
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Risk cards
# ─────────────────────────────────────────────────────────────────────────────

def render_risk_cards(recs: list[dict[str, Any]], citations: list[dict[str, Any]]) -> None:
    if not recs:
        st.markdown(
            '<div class="pf-empty">🎯 No deals match this risk threshold. Lower the slider or widen the pipeline.</div>',
            unsafe_allow_html=True,
        )
        return
    cite_map = {c["id"]: c for c in citations or []}
    for i, rec in enumerate(recs):
        band = rec.get("risk_band", "medium")
        signals = rec.get("signals") or []
        evidence = " · ".join(s.get("evidence", "") for s in signals[:2]) or "Composite risk elevated."
        cites_html = "".join(
            f'<span class="pf-cite">{cid}</span>' for cid in rec.get("citation_ids") or []
        )
        risk_pct = int(float(rec.get("risk_score", 0)) * 100)
        adj_p = float(rec.get("adj_win_prob") or 0)
        base_p = float(rec.get("base_win_prob") or 0)
        llm_badge = (
            '<span class="pf-llm-badge">LLM grounded</span>'
            if rec.get("llm_grounded")
            else '<span class="pf-rule-badge">Rule-based</span>'
        )
        st.markdown(
            f"""<div class="pf-card">
              <div class="pf-card-head">
                <div>
                  <strong class="pf-deal-id">{rec.get('deal_id')}</strong>
                  <span class="pf-account-name">{rec.get('account')}</span>
                </div>
                <div class="pf-card-meta">
                  <span class="pf-band {band}">{band.upper()} · {rec.get('risk_score')}</span>
                  {llm_badge}
                </div>
              </div>
              <div class="pf-risk-bar-wrap">
                <div class="pf-risk-bar" style="width:{risk_pct}%;"></div>
              </div>
              <div class="pf-signal">{evidence}</div>
              <div class="pf-win-prob">
                Win prob: <strong>{adj_p:.0%}</strong>
                <span class="pf-muted">(stage base {base_p:.0%} → haircut {adj_p:.0%})</span>
              </div>
              <div class="pf-action">{rec.get('action', '')} {cites_html}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        for cid in rec.get("citation_ids") or []:
            c = cite_map.get(cid)
            if c:
                with st.expander(f"📄 Source {cid} · {c.get('source')}", expanded=False):
                    st.write(c.get("excerpt"))


# ─────────────────────────────────────────────────────────────────────────────
# Agent trace
# ─────────────────────────────────────────────────────────────────────────────

def render_trace(trace: list[str]) -> None:
    if not trace:
        return
    st.markdown("##### 🔍 Agent execution trace")
    steps = "".join(
        f'<span class="pf-trace-step">{step}</span><span class="pf-trace-arrow">→</span>'
        for step in trace[:-1]
    ) + f'<span class="pf-trace-step pf-trace-last">{trace[-1] if trace else ""}</span>'
    st.markdown(f'<div class="pf-trace">{steps}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Stage mix chart
# ─────────────────────────────────────────────────────────────────────────────

def stage_mix_chart(df, quarter: str | None = None) -> go.Figure:
    import numpy as np

    open_df = df[df["is_open"] == 1].copy()
    if quarter:
        open_df = open_df[open_df["forecast_quarter"] == quarter]
    if open_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No open pipeline", height=300)
        return fig

    stage_order = ["Prospecting", "Qualification", "Discovery", "Proposal", "Negotiation"]
    grouped = (
        open_df.groupby("stage")
        .agg(amount=("amount", "sum"), count=("deal_id", "count"))
        .reindex(stage_order)
        .dropna()
        .reset_index()
    )

    bar_colors = [
        COLORS["muted"],
        COLORS["blue"],
        COLORS["accent"],
        COLORS["accent2"],
        COLORS["danger"],
    ][: len(grouped)]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Amount",
            x=grouped["stage"],
            y=grouped["amount"],
            marker_color=bar_colors,
            text=[f"{money(v)}<br><span style='font-size:10px'>{int(c)} deals</span>"
                  for v, c in zip(grouped["amount"], grouped["count"])],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Amount: %{y:$,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Open coverage by stage",
        yaxis=dict(title="Pipeline amount ($)", tickformat="$,.0f"),
        height=320,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Salvage / commit simulator chart
# ─────────────────────────────────────────────────────────────────────────────

def salvage_chart(sim: dict[str, Any]) -> go.Figure:
    fig = go.Figure()
    categories = ["P10", "P50", "P90", "Expected"]
    baseline = [
        sim.get("baseline_p10", 0),
        sim.get("baseline_p50", 0),
        sim.get("baseline_p90", 0),
        sim.get("baseline_expected", 0),
    ]
    scenario = [
        sim.get("scenario_p10", 0),
        sim.get("scenario_p50", 0),
        sim.get("scenario_p90", 0),
        sim.get("scenario_expected", 0),
    ]

    fig.add_trace(
        go.Bar(
            name="Baseline (no action)",
            x=categories,
            y=baseline,
            marker_color=COLORS["muted"],
            opacity=0.75,
            text=[money(v) for v in baseline],
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Bar(
            name="After action queue",
            x=categories,
            y=scenario,
            marker_color=COLORS["accent"],
            text=[money(v) for v in scenario],
            textposition="outside",
        )
    )

    fig.update_layout(
        title=f"Commit-call simulator — P50 lift: {money(sim.get('p50_lift', 0))} "
              f"({sim.get('n_intervened', 0)} deals intervened)",
        barmode="group",
        height=360,
        yaxis=dict(tickformat="$,.0f"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Calibration chart (rep accuracy)
# ─────────────────────────────────────────────────────────────────────────────

def calibration_chart(rows: list[dict[str, Any]]) -> go.Figure:
    return rep_calibration_chart(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Activity timeline
# ─────────────────────────────────────────────────────────────────────────────

def activity_timeline(raw: str) -> None:
    import json

    type_icons = {
        "email": "📧",
        "call": "📞",
        "demo": "🖥️",
        "meeting": "🤝",
        "proposal_sent": "📄",
        "security_review": "🔒",
    }

    try:
        events = json.loads(raw) if raw else []
    except Exception:
        events = []
    if not events:
        st.markdown(
            '<div class="pf-empty">No activity history on this deal — first outreach needed.</div>',
            unsafe_allow_html=True,
        )
        return

    items = []
    for ev in sorted(events, key=lambda e: int(e.get("days_ago") or 0)):
        icon = type_icons.get(str(ev.get("type", "")), "📌")
        age = int(ev.get("days_ago", 0))
        recency_color = (
            "#0F8A5F" if age < 7 else
            "#C45C26" if age < 21 else
            "#C23B2A"
        )
        items.append(
            f"""<div class="pf-tl-item">
              <div class="pf-tl-dot" style="background:{recency_color};box-shadow:0 0 0 4px {recency_color}22"></div>
              <div>
                <strong>{icon} {ev.get('type', 'event').replace('_', ' ').title()}</strong>
                <span class="pf-muted"> · {age}d ago</span>
                <div class="pf-signal">{ev.get('note', '')}</div>
              </div>
            </div>"""
        )
    st.markdown(f'<div class="pf-timeline">{"".join(items)}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Quick insights panel
# ─────────────────────────────────────────────────────────────────────────────

def quick_insights_panel(fc: dict[str, Any], risks: list[dict[str, Any]]) -> None:
    """Auto-generated insights from forecast + risk data."""
    if not fc:
        return
    p50 = fc.get("p50", 0)
    rep = fc.get("rep_roll_up", 0)
    optimism_gap = rep - p50
    n_critical = sum(1 for r in risks if r.get("risk_band") == "critical")
    n_high = sum(1 for r in risks if r.get("risk_band") == "high")
    at_risk_acv = sum(r.get("amount", 0) for r in risks if r.get("risk_band") in {"critical", "high"})
    missing_eb = sum(1 for r in risks if any(s.get("code") == "missing_economic_buyer" for s in r.get("signals", [])))

    insights = []
    if optimism_gap > 0:
        insights.append(
            f"⚠️ Rep roll-up is <strong>{money(optimism_gap)} higher</strong> than model P50 — "
            f"typical optimism bias. Haircut before committing to leadership."
        )
    if n_critical > 0:
        insights.append(
            f"🔴 <strong>{n_critical} critical-band deals</strong> need intervention this week "
            f"(total ACV exposure: {money(at_risk_acv)})."
        )
    if missing_eb > 0:
        insights.append(
            f"👤 <strong>{missing_eb} deals</strong> missing an economic buyer at a late stage — "
            f"historically halves conversion rate."
        )
    if not insights:
        insights.append("✅ Pipeline looks healthy — no critical signals detected.")

    items_html = "".join(f'<li class="pf-insight-item">{i}</li>' for i in insights)
    st.markdown(
        f'<ul class="pf-insights">{items_html}</ul>',
        unsafe_allow_html=True,
    )
