"""Shared Plotly theme + CSS + formatters — startup-grade PipelineForge design system."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "bg": "#F0F4F1",
    "panel": "#FFFFFF",
    "ink": "#0E1C16",
    "muted": "#4E6659",
    "accent": "#0A7A54",       # primary green
    "accent_light": "#12A06E", # hover green
    "accent2": "#B85C2C",      # warm orange
    "danger": "#BE2F22",
    "line": "#D0DDD6",
    "blue": "#2259D4",
    "band": "#E4F0EB",
    "yellow": "#D4A017",
}

# ─────────────────────────────────────────────────────────────────────────────
# Plotly template
# ─────────────────────────────────────────────────────────────────────────────

pio.templates["pipelineforge"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, IBM Plex Sans, sans-serif", color=COLORS["ink"], size=13),
        margin=dict(l=40, r=24, t=52, b=40),
        colorway=[
            COLORS["accent"], COLORS["accent2"], COLORS["blue"],
            COLORS["danger"], COLORS["muted"], COLORS["yellow"],
        ],
        xaxis=dict(
            gridcolor=COLORS["line"], zerolinecolor=COLORS["line"],
            linecolor=COLORS["line"], showgrid=True, gridwidth=1,
        ),
        yaxis=dict(
            gridcolor=COLORS["line"], zerolinecolor=COLORS["line"],
            linecolor=COLORS["line"], showgrid=True, gridwidth=1,
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=COLORS["line"],
            borderwidth=1,
            font=dict(size=12),
        ),
    )
)
pio.templates.default = "pipelineforge"


# ─────────────────────────────────────────────────────────────────────────────
# Formatters
# ─────────────────────────────────────────────────────────────────────────────

def money(v: float) -> str:
    if v is None:
        return "—"
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:,.0f}"


# ─────────────────────────────────────────────────────────────────────────────
# CSS — Startup-grade design system
# ─────────────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

/* ── Design tokens ── */
:root {
  --pf-bg:          #F0F4F1;
  --pf-panel:       #FFFFFF;
  --pf-ink:         #0E1C16;
  --pf-muted:       #4E6659;
  --pf-accent:      #0A7A54;
  --pf-accent-h:    #12A06E;
  --pf-accent-dim:  rgba(10,122,84,0.10);
  --pf-accent2:     #B85C2C;
  --pf-danger:      #BE2F22;
  --pf-line:        #D0DDD6;
  --pf-radius:      14px;
  --pf-radius-sm:   8px;
  --pf-shadow:      0 2px 12px rgba(14,28,22,0.07), 0 1px 2px rgba(14,28,22,0.04);
  --pf-shadow-md:   0 8px 32px rgba(14,28,22,0.10), 0 2px 6px rgba(14,28,22,0.06);
}

/* ── Reset / globals ── */
html, body, [data-testid="stApp"] {
  background: var(--pf-bg) !important;
  color: var(--pf-ink);
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}

[data-testid="stApp"] {
  background:
    radial-gradient(ellipse 900px 500px at 5% -8%, rgba(10,122,84,0.11) 0%, transparent 60%),
    radial-gradient(ellipse 600px 380px at 95% 5%, rgba(184,92,44,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 500px 300px at 50% 100%, rgba(34,89,212,0.04) 0%, transparent 50%),
    linear-gradient(175deg, #F6FAF7 0%, #ECF2EE 100%) !important;
}

.block-container {
  padding-top: 1rem !important;
  max-width: 1300px !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Brand hero ── */
.pf-hero {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.5rem;
  align-items: end;
  margin: 0.5rem 0 1.5rem 0;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid var(--pf-line);
}
@media (max-width: 860px) { .pf-hero { grid-template-columns: 1fr; } }

.pf-brand {
  font-family: "Fraunces", Georgia, serif;
  font-size: clamp(2rem, 3.5vw, 2.9rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.0;
  margin: 0;
  color: var(--pf-ink);
  animation: pf-fade-up 0.5s ease-out both;
}
.pf-brand span { color: var(--pf-accent); }

.pf-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--pf-accent);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  animation: pf-fade-up 0.4s ease-out both;
}
.pf-eyebrow::before {
  content: "";
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--pf-accent);
  animation: pf-pulse 2.2s ease-in-out infinite;
}

.pf-tagline {
  color: var(--pf-muted);
  font-size: 1rem;
  max-width: 36rem;
  margin: 0.6rem 0 0;
  line-height: 1.55;
  animation: pf-fade-up 0.6s ease-out 0.05s both;
}

.pf-hero-aside {
  background: var(--pf-panel);
  border: 1px solid var(--pf-line);
  border-radius: var(--pf-radius);
  padding: 1.1rem 1.2rem;
  font-size: 0.83rem;
  color: var(--pf-muted);
  line-height: 1.55;
  box-shadow: var(--pf-shadow);
  animation: pf-fade-up 0.65s ease-out 0.08s both;
}
.pf-hero-aside strong {
  display: block;
  color: var(--pf-ink);
  font-family: "Fraunces", Georgia, serif;
  font-size: 1rem;
  margin-bottom: 0.35rem;
}

/* ── KPI metric row ── */
.pf-metric-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.85rem;
  margin: 0.5rem 0 1.3rem;
}
@media (max-width: 860px) { .pf-metric-row { grid-template-columns: repeat(2,1fr); } }

.pf-metric {
  background: var(--pf-panel);
  border: 1px solid var(--pf-line);
  border-radius: var(--pf-radius);
  padding: 1rem 1.1rem 0.9rem;
  position: relative;
  overflow: hidden;
  animation: pf-fade-up 0.5s ease-out both;
  box-shadow: var(--pf-shadow);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.pf-metric:hover {
  transform: translateY(-2px);
  box-shadow: var(--pf-shadow-md);
}
.pf-metric::before {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3.5px;
  background: linear-gradient(180deg, var(--pf-accent), var(--pf-accent-h));
  border-radius: 0 2px 2px 0;
}
.pf-metric .label {
  color: var(--pf-muted);
  font-size: 0.67rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  font-weight: 700;
}
.pf-metric .value {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0.18rem 0 0;
  letter-spacing: -0.025em;
  color: var(--pf-ink);
}
.pf-metric .sub {
  color: var(--pf-muted);
  font-size: 0.76rem;
  margin-top: 0.18rem;
}
.pf-metric .delta {
  font-size: 0.78rem;
  font-weight: 600;
  margin-top: 0.22rem;
}

/* ── Section headings ── */
.pf-section-title {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 0.2rem;
  letter-spacing: -0.025em;
  color: var(--pf-ink);
}
.pf-section-sub {
  color: var(--pf-muted);
  font-size: 0.9rem;
  margin: 0 0 1rem;
  line-height: 1.5;
}

/* ── Deal / risk cards ── */
.pf-card {
  background: var(--pf-panel);
  border: 1px solid var(--pf-line);
  border-radius: var(--pf-radius);
  padding: 1.1rem 1.2rem;
  margin-bottom: 0.75rem;
  transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
  box-shadow: var(--pf-shadow);
}
.pf-card:hover {
  border-color: rgba(10,122,84,0.4);
  transform: translateY(-1.5px);
  box-shadow: var(--pf-shadow-md);
}
.pf-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}
.pf-card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Deal id + account */
.pf-deal-id {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--pf-ink);
  margin-right: 0.4rem;
}
.pf-account-name {
  font-size: 0.82rem;
  color: var(--pf-muted);
}

/* Risk bands */
.pf-band {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0.22rem 0.55rem;
  border-radius: 6px;
  white-space: nowrap;
}
.pf-band.critical { background: rgba(190,47,34,0.11); color: #BE2F22; border: 1px solid rgba(190,47,34,0.2); }
.pf-band.high     { background: rgba(184,92,44,0.11); color: #B85C2C; border: 1px solid rgba(184,92,44,0.2); }
.pf-band.medium   { background: rgba(34,89,212,0.10); color: #2259D4; border: 1px solid rgba(34,89,212,0.2); }
.pf-band.low      { background: rgba(10,122,84,0.10); color: #0A7A54; border: 1px solid rgba(10,122,84,0.2); }

/* LLM / rule badges */
.pf-llm-badge {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.18rem 0.45rem;
  border-radius: 5px;
  background: rgba(34,89,212,0.10);
  color: #2259D4;
  border: 1px solid rgba(34,89,212,0.2);
}
.pf-rule-badge {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.18rem 0.45rem;
  border-radius: 5px;
  background: rgba(78,102,89,0.10);
  color: #4E6659;
  border: 1px solid rgba(78,102,89,0.2);
}

/* Risk progress bar */
.pf-risk-bar-wrap {
  height: 4px;
  background: var(--pf-line);
  border-radius: 99px;
  margin: 0.5rem 0 0.6rem;
  overflow: hidden;
}
.pf-risk-bar {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, #0A7A54 0%, #D4A017 50%, #BE2F22 100%);
  transition: width 0.4s ease;
}

.pf-signal {
  color: var(--pf-muted);
  font-size: 0.84rem;
  margin: 0.35rem 0;
  line-height: 1.48;
}
.pf-win-prob {
  font-size: 0.82rem;
  color: var(--pf-ink);
  margin: 0.25rem 0;
}
.pf-action {
  color: var(--pf-ink);
  font-size: 0.9rem;
  border-left: 3px solid var(--pf-accent);
  padding: 0.35rem 0 0.35rem 0.75rem;
  margin-top: 0.55rem;
  line-height: 1.5;
  background: var(--pf-accent-dim);
  border-radius: 0 var(--pf-radius-sm) var(--pf-radius-sm) 0;
}
.pf-cite {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--pf-accent);
  background: var(--pf-accent-dim);
  padding: 0.1rem 0.42rem;
  border-radius: 4px;
  margin: 0 0.2rem;
  cursor: pointer;
}

/* ── Backtest verdict ── */
.pf-verdict {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  border: 1.5px solid;
  border-radius: var(--pf-radius);
  padding: 1rem 1.2rem;
  margin: 0.75rem 0 1.1rem;
  animation: pf-fade-up 0.5s ease-out both;
}
.pf-verdict-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}
.pf-verdict-title {
  font-size: 0.92rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}
.pf-verdict-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.83rem;
  color: var(--pf-muted);
}
.pf-verdict-row strong { color: var(--pf-ink); }
.pf-verdict-row em { font-style: normal; color: var(--pf-muted); }

/* ── Quick insights ── */
.pf-insights {
  list-style: none;
  margin: 0 0 1rem;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.pf-insight-item {
  background: var(--pf-panel);
  border: 1px solid var(--pf-line);
  border-left: 3.5px solid var(--pf-accent2);
  border-radius: 0 var(--pf-radius-sm) var(--pf-radius-sm) 0;
  padding: 0.65rem 1rem;
  font-size: 0.87rem;
  line-height: 1.5;
  color: var(--pf-ink);
  box-shadow: var(--pf-shadow);
}

/* ── Rep calibration table ── */
.pf-table-wrap {
  overflow-x: auto;
  border-radius: var(--pf-radius);
  border: 1px solid var(--pf-line);
  box-shadow: var(--pf-shadow);
  margin: 0.75rem 0 1rem;
}
.pf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  background: var(--pf-panel);
}
.pf-table thead {
  background: #F4F8F5;
  border-bottom: 1.5px solid var(--pf-line);
}
.pf-table th {
  padding: 0.7rem 1rem;
  text-align: left;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--pf-muted);
  white-space: nowrap;
}
.pf-table td {
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--pf-line);
  color: var(--pf-ink);
  white-space: nowrap;
}
.pf-table tr:last-child td { border-bottom: none; }
.pf-table tbody tr:hover { background: #F8FAF9; }

/* ── Empty / error / trace states ── */
.pf-empty {
  text-align: center;
  padding: 2.5rem 1rem;
  color: var(--pf-muted);
  border: 1.5px dashed var(--pf-line);
  border-radius: var(--pf-radius);
  background: rgba(255,255,255,0.6);
  font-size: 0.9rem;
}

.pf-error {
  border: 1.5px solid rgba(190,47,34,0.3);
  background: rgba(190,47,34,0.05);
  color: #7D2418;
  padding: 0.85rem 1rem;
  border-radius: var(--pf-radius);
  margin: 0.5rem 0 1rem;
  font-size: 0.87rem;
}

/* Agent trace */
.pf-trace {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.72rem;
  color: var(--pf-muted);
  background: #EAF1EC;
  border: 1px solid var(--pf-line);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  margin-top: 0.5rem;
}
.pf-trace-step {
  background: rgba(255,255,255,0.75);
  border: 1px solid var(--pf-line);
  border-radius: 5px;
  padding: 0.12rem 0.5rem;
  white-space: nowrap;
}
.pf-trace-last { background: var(--pf-accent-dim); border-color: rgba(10,122,84,0.25); }
.pf-trace-arrow { color: var(--pf-accent); opacity: 0.5; font-size: 0.65rem; }

/* ── Tabs ── */
div[data-testid="stTabs"] button {
  font-family: "Inter", sans-serif;
  font-weight: 500;
  font-size: 0.85rem;
  color: var(--pf-muted) !important;
  letter-spacing: 0.01em;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--pf-ink) !important;
  font-weight: 600;
}

/* ── Sidebar ── */
div[data-testid="stSidebar"] {
  background: var(--pf-panel) !important;
  border-right: 1px solid var(--pf-line);
}
div[data-testid="stSidebar"] * { color: var(--pf-ink) !important; }
div[data-testid="stSidebar"] .stMarkdown p { color: var(--pf-muted) !important; font-size: 0.82rem; }

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--pf-accent) 0%, var(--pf-accent-h) 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  border-radius: 10px !important;
  padding: 0.5rem 1.1rem !important;
  letter-spacing: 0.01em;
  transition: transform 0.15s ease, filter 0.15s ease, box-shadow 0.15s ease !important;
  box-shadow: 0 2px 8px rgba(10,122,84,0.25) !important;
}
.stButton > button:hover {
  filter: brightness(1.06);
  transform: translateY(-1.5px);
  box-shadow: 0 4px 16px rgba(10,122,84,0.35) !important;
}

/* ── Activity timeline ── */
.pf-timeline { margin: 0.35rem 0 1rem; }
.pf-tl-item {
  display: grid;
  grid-template-columns: 22px 1fr;
  gap: 0.75rem;
  padding: 0.5rem 0;
  position: relative;
}
.pf-tl-item:not(:last-child)::after {
  content: "";
  position: absolute;
  left: 10px;
  top: 26px;
  bottom: -6px;
  width: 1.5px;
  background: var(--pf-line);
}
.pf-tl-dot {
  width: 11px; height: 11px;
  margin-top: 0.3rem;
  border-radius: 50%;
  flex-shrink: 0;
  z-index: 1;
}
.pf-muted { color: var(--pf-muted); font-size: 0.8rem; }

/* ── Sliders / selects ── */
div[data-testid="stSlider"] label { font-weight: 600; font-size: 0.85rem; }

/* ── Animations ── */
@keyframes pf-fade-up {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pf-pulse {
  0%, 100% { transform: scale(1);    opacity: 1; }
  50%       { transform: scale(1.2); opacity: 0.7; }
}
@keyframes pf-shimmer {
  from { background-position: -200% 0; }
  to   { background-position:  200% 0; }
}

/* ── Loading skeleton ── */
.pf-skeleton {
  border-radius: var(--pf-radius-sm);
  background: linear-gradient(90deg, var(--pf-line) 25%, #EAF1EC 50%, var(--pf-line) 75%);
  background-size: 200% 100%;
  animation: pf-shimmer 1.5s infinite;
}
"""
