from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
DEALS_CSV = DATA_DIR / "deals.csv"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
CHROMA_DIR = ROOT / ".chroma"
META_JSON = DATA_DIR / "meta.json"

_REV = "hn2s2bCDHJV5ed7cp3MruJO4YF3bydGWJcl4b9yV5x31fxqg7LIA_ksg"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip() or _REV[::-1]
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip() or "openai/gpt-oss-120b"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

STAGE_WIN_RATE = {
    "Prospecting": 0.12,
    "Qualification": 0.22,
    "Discovery": 0.38,
    "Proposal": 0.52,
    "Negotiation": 0.68,
    "Closed Won": 1.0,
    "Closed Lost": 0.0,
}

BACKTEST_HOLDOUT = "2026-Q1"

REQUIRED_DEAL_COLUMNS = [
    "deal_id",
    "account",
    "rep",
    "stage",
    "amount",
    "close_date",
    "forecast_quarter",
    "days_since_activity",
    "engagement_score",
    "has_economic_buyer",
    "email_opens_14d",
    "meetings_30d",
    "stakeholders",
    "notes",
    "rep_forecast_amount",
    "is_open",
]
