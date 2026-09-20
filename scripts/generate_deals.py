"""
Generate 200 realistic CRM deals for LegitsIQ-AI-Forecast demo.
Run: .venv\Scripts\python.exe scripts/generate_deals.py
"""
import random
import csv
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "data" / "deals.csv"

# ── Realistic data pools ───────────────────────────────────────────────────
ACCOUNTS = [
    # Indian enterprises
    "Tata Consultancy Services", "Infosys Ltd", "Wipro Technologies",
    "HCL Technologies", "Reliance Industries", "HDFC Bank", "ICICI Bank",
    "Bajaj Auto", "Mahindra & Mahindra", "Larsen & Toubro",
    "Adani Enterprises", "Bharti Airtel", "ITC Limited", "Sun Pharma",
    "Dr Reddy's Laboratories", "Zomato India", "Swiggy", "Paytm",
    "Flipkart", "Ola Electric", "Freshworks",
    "Zoho Corporation", "PhonePe", "MakeMyTrip",
    # Global
    "Microsoft Corporation", "Google LLC", "Amazon Web Services",
    "Salesforce Inc", "SAP SE", "Oracle Corporation",
    "Accenture PLC", "IBM Corporation", "Capgemini",
    "Cognizant Technology", "Deloitte LLP", "PwC Advisory",
    "JP Morgan Chase", "Goldman Sachs", "Morgan Stanley",
    "Siemens AG", "Bosch GmbH", "ABB Ltd", "Schneider Electric",
    "Honeywell International", "General Electric", "Caterpillar Inc",
    "Ford Motor Company", "Tesla Inc", "Uber Technologies",
    "Airbnb Inc", "Shopify Inc", "Stripe Inc", "Twilio Inc",
    "Snowflake Inc", "Databricks", "HashiCorp", "Confluent",
    "MongoDB Inc", "Elastic NV", "Cloudflare Inc", "Okta Inc",
    "Workday Inc", "ServiceNow Inc", "Zendesk Inc", "HubSpot Inc",
    "DocuSign Inc", "Box Inc", "Dropbox Inc", "Zoom Video",
    "Slack Technologies", "Atlassian Corp", "JFrog Ltd", "GitLab Inc",
]

REPS = [
    "Rahul Sharma", "Priya Patil", "Amit Kulkarni", "Sneha Joshi",
    "Karan Mehta", "Neha Desai", "Vivek Rao", "Ananya Shah",
    "Rohan Jain", "Meera Nair", "Arjun Verma", "Ishita Rao",
    "Siddharth Pillai", "Pooja Iyer", "Neeraj Gupta",
]

STAGES = ["Prospecting", "Qualification", "Discovery", "Proposal", "Negotiation"]

NOTES_TEMPLATES = [
    "Champion is {rep} but no exec sponsor confirmed yet.",
    "Good engagement from VP of Engineering; legal review pending.",
    "POC completed successfully; procurement involved.",
    "Multi-threaded: 3 stakeholders aligned. Close expected end of quarter.",
    "Stalled after initial demo. Follow-up scheduled for next week.",
    "Competitor PTC is also in evaluation. Need to differentiate on ROI.",
    "Budget approved. Waiting on final sign-off from CFO.",
    "Decision delayed due to internal reorganisation.",
    "Strong champion, but no economic buyer identified.",
    "Fast-track evaluation requested by CTO.",
    "Objection on pricing. Working on custom proposal.",
    "Security review in progress. Legal NDA signed.",
    "Reference customer call scheduled.",
    "Pilot expanded to 3 business units.",
    "Renewal conversation overlapping with new expansion deal.",
    "Executive sponsor changed mid-cycle.",
    "Lost key contact – reconnecting through LinkedIn.",
    "RFP issued. Responding with detailed SOW.",
    "POC approved. Technical win confirmed.",
    "Contract redlines under legal review.",
]

rows = []
deal_counter = 1000

# 1. 50 CLOSED DEALS FOR 2026-Q1 HOLDOUT BACKTEST (COMPULSORY FEATURE 7)
for i in range(50):
    deal_id = f"D-{deal_counter + i + 1}"
    account = random.choice(ACCOUNTS)
    rep = random.choice(REPS)
    is_won = random.random() < 0.46
    stage = "Closed Won" if is_won else "Closed Lost"
    
    base = random.choice([
        random.randint(25_000, 95_000),
        random.randint(95_000, 320_000),
        random.randint(320_000, 1_200_000)
    ])
    amount = round(base / 1000) * 1000
    actual_rev = amount if is_won else 0

    # Sales rep optimism: reps forecast they would win most deals
    if is_won:
        rep_forecast = amount
    else:
        # Rep was overly optimistic and committed 85-115% of the deal
        rep_forecast = round(amount * random.uniform(0.85, 1.15) / 1000) * 1000

    # Reconstructed mid-quarter signals before close
    if is_won:
        eng = round(random.uniform(0.68, 0.95), 2)
        days = random.randint(1, 9)
        eb = 1
        opens = random.randint(8, 18)
        meets = random.randint(3, 7)
    else:
        eng = round(random.uniform(0.12, 0.48), 2)
        days = random.randint(15, 65)
        eb = random.choice([0, 0, 1])
        opens = random.randint(0, 5)
        meets = random.randint(0, 2)

    close_month = random.choice(["01", "02", "03"])
    close_day = random.randint(10, 28)
    close_date = f"2026-{close_month}-{close_day:02d}"

    notes = random.choice(NOTES_TEMPLATES).replace("{rep}", rep.split()[0])

    rows.append({
        "deal_id": deal_id,
        "account": account,
        "rep": rep,
        "stage": stage,
        "amount": amount,
        "actual_revenue": actual_rev,
        "close_date": close_date,
        "forecast_quarter": "2026-Q1",
        "days_since_activity": days,
        "engagement_score": eng,
        "has_economic_buyer": eb,
        "email_opens_14d": opens,
        "meetings_30d": meets,
        "stakeholders": random.randint(1, 5),
        "notes": notes,
        "rep_forecast_amount": rep_forecast,
        "is_open": 0,
    })

# 2. 150 OPEN DEALS FOR 2026-Q2 & 2026-Q3 ACTIVE PIPELINE
for i in range(150):
    idx = 50 + i
    deal_id = f"D-{deal_counter + idx + 1}"
    account = random.choice(ACCOUNTS)
    rep = random.choice(REPS)
    stage = random.choices(STAGES, weights=[8, 15, 25, 30, 22])[0]

    base = random.choice([
        random.randint(20_000, 85_000),
        random.randint(85_000, 350_000),
        random.randint(350_000, 1_450_000)
    ])
    amount = round(base / 1000) * 1000
    rep_forecast = round(amount * random.uniform(1.05, 1.30) / 1000) * 1000

    days_since_activity = random.choices(
        [random.randint(1, 6), random.randint(7, 18), random.randint(19, 45), random.randint(46, 110)],
        weights=[35, 35, 20, 10]
    )[0]
    engagement_score = round(max(0.08, min(0.98, random.gauss(0.58, 0.22))), 2)
    has_economic_buyer = random.choices([0, 1], weights=[40, 60])[0]
    email_opens = random.randint(0, 16)
    meetings = random.randint(0, 6)
    stakeholders = random.randint(1, 6)

    # 100 deals in 2026-Q2, 50 in 2026-Q3
    fq = "2026-Q2" if i < 100 else "2026-Q3"
    m_range = (4, 6) if fq == "2026-Q2" else (7, 9)
    close_m = random.randint(m_range[0], m_range[1])
    close_d = random.randint(1, 28)
    close_date = f"2026-{close_m:02d}-{close_d:02d}"

    notes = random.choice(NOTES_TEMPLATES).replace("{rep}", rep.split()[0])

    rows.append({
        "deal_id": deal_id,
        "account": account,
        "rep": rep,
        "stage": stage,
        "amount": amount,
        "actual_revenue": 0,
        "close_date": close_date,
        "forecast_quarter": fq,
        "days_since_activity": days_since_activity,
        "engagement_score": engagement_score,
        "has_economic_buyer": has_economic_buyer,
        "email_opens_14d": email_opens,
        "meetings_30d": meetings,
        "stakeholders": stakeholders,
        "notes": notes,
        "rep_forecast_amount": rep_forecast,
        "is_open": 1,
    })

fieldnames = [
    "deal_id", "account", "rep", "stage", "amount", "actual_revenue",
    "close_date", "forecast_quarter", "days_since_activity", "engagement_score",
    "has_economic_buyer", "email_opens_14d", "meetings_30d", "stakeholders",
    "notes", "rep_forecast_amount", "is_open",
]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"[SUCCESS] Written {len(rows)} deals to {OUT}")
print(f"   Open deals in 2026-Q2/Q3 : {sum(1 for r in rows if r['is_open'] == 1)}")
print(f"   Closed deals in 2026-Q1  : {sum(1 for r in rows if r['is_open'] == 0)}")
print(f"   Total pipeline value     : ${sum(r['amount'] for r in rows if r['is_open'] == 1):,.0f}")
