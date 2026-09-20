import csv
import random
from pathlib import Path

random.seed(101)

OUT = Path("c:/Users/Arihant M/projects/pipeline-forge/demo_enterprise_pipeline.csv")

# Recognizable top-tier accounts
TIER_1_ACCOUNTS = [
    ("Microsoft Cloud Expansion", 850000, "Enterprise"),
    ("Amazon Web Services Migration", 1200000, "Enterprise"),
    ("Tata Consultancy Global IT", 650000, "Enterprise"),
    ("Reliance Digital Infrastructure", 920000, "Enterprise"),
    ("Infosys AI Workstation Pilot", 480000, "Mid-Market"),
    ("HDFC Bank Core Banking Sync", 750000, "Enterprise"),
    ("Snowflake Analytics Integration", 380000, "Mid-Market"),
    ("Stripe Payments API Gateway", 420000, "Mid-Market"),
    ("Salesforce CRM Data Pipeline", 550000, "Enterprise"),
    ("Wipro Cybersecurity Upgrade", 320000, "Mid-Market"),
    ("Zomato Fleet Dispatch Optim", 220000, "Mid-Market"),
    ("Swiggy Delivery Routing Engine", 280000, "Mid-Market"),
    ("Flipkart Q4 Big Billion Cloud", 890000, "Enterprise"),
    ("Uber Enterprise Mobility API", 460000, "Mid-Market"),
    ("Databricks Lakehouse Analytics", 510000, "Enterprise"),
    ("Cisco Unified Comms Modernize", 640000, "Enterprise"),
    ("Oracle Cloud Database Engine", 590000, "Enterprise"),
    ("Paytm Merchant Gateway Sync", 260000, "Mid-Market"),
    ("Bharti Airtel 5G Core OSS", 780000, "Enterprise"),
    ("Larsen & Toubro Smart Site", 610000, "Enterprise"),
]

OTHER_ACCOUNTS = [
    "Adani Green Energy", "Sun Pharma R&D", "Mahindra Auto Telematics",
    "Bajaj Finserv Lending Core", "ICICI Securities Wealth", "DocuSign India",
    "Zoom Video Enterprise", "HubSpot RevOps Upgrade", "Twilio SMS Trunking",
    "MongoDB Atlas Migration", "Cloudflare Zero Trust SASE", "Okta Identity Cloud",
    "Workday Global HRIS", "ServiceNow ITOM Suite", "Atlassian Jira Enterprise",
    "Shopify Plus Scale Engine", "Box Content Cloud", "GitLab DevSecOps",
    "Siemens Industrial IoT", "Bosch Smart Mobility", "Schneider Electric Grid",
    "ABB Robotics Automation", "Honeywell Aerospace Avionics", "Deloitte Advisory Tech",
    "PwC Enterprise Assurance", "KPMG Global Consulting", "Accenture Cloud First",
    "Capgemini Engineering Labs", "Cognizant Digital Core", "IBM RedHat Openshift"
]

REPS = [
    "Rahul Sharma", "Priya Patil", "Amit Kulkarni", "Sneha Joshi",
    "Karan Mehta", "Neha Desai", "Vivek Rao", "Ananya Shah",
    "Rohan Jain", "Meera Nair", "Arjun Verma", "Ishita Rao"
]

STAGES = ["Prospecting", "Qualification", "Discovery", "Proposal", "Negotiation"]

DRAMATIC_NOTES = [
    "Economic buyer (CIO) skipped last 2 review calls. Champion is VP Engineering. Legal review pending.",
    "Competitive bake-off against Clari. High stakeholder engagement across 4 departments. Proposal in final approval.",
    "Contract sent for signature, but procurement has paused new software onboarding pending quarterly budget freeze.",
    "POC validated with 99.8% SLA. Technical win confirmed. Waiting on CFO sign-off.",
    "Stalled in legal for 32 days over data residency indemnification clause. Needs executive sponsor escalation.",
    "Executive champion resigned last week. Need urgent re-threading to new VP Product.",
    "Multi-threaded across 5 stakeholders. Security review signed off. High confidence close.",
    "Budget approved in FY26 OPEX. Contract redlines with outside counsel."
]

rows = []
counter = 2000

# 1. 50 CLOSED DEALS FOR 2026-Q1 (FEATURE 7 HOLDOUT BACKTEST)
for i in range(50):
    deal_id = f"D-{counter + i + 1}"
    rep = random.choice(REPS)
    account = random.choice(OTHER_ACCOUNTS if i >= 20 else [a[0] for a in TIER_1_ACCOUNTS])
    is_won = random.random() < 0.44
    stage = "Closed Won" if is_won else "Closed Lost"
    
    amount = random.randint(35, 450) * 1000
    actual_rev = amount if is_won else 0
    
    # Reps were overly optimistic on lost deals
    rep_forecast = amount if is_won else round(amount * random.uniform(0.9, 1.25) / 1000) * 1000
    
    if is_won:
        eng = round(random.uniform(0.72, 0.95), 2)
        days = random.randint(2, 8)
        eb = 1
        opens = random.randint(8, 16)
        meets = random.randint(3, 6)
    else:
        eng = round(random.uniform(0.15, 0.45), 2)
        days = random.randint(18, 55)
        eb = random.choice([0, 0, 1])
        opens = random.randint(0, 4)
        meets = random.randint(0, 2)
        
    rows.append({
        "deal_id": deal_id,
        "account": account,
        "rep": rep,
        "stage": stage,
        "amount": amount,
        "actual_revenue": actual_rev,
        "close_date": f"2026-0{random.randint(1, 3)}-{random.randint(10, 28):02d}",
        "forecast_quarter": "2026-Q1",
        "days_since_activity": days,
        "engagement_score": eng,
        "has_economic_buyer": eb,
        "email_opens_14d": opens,
        "meetings_30d": meets,
        "stakeholders": random.randint(1, 5),
        "notes": random.choice(DRAMATIC_NOTES),
        "rep_forecast_amount": rep_forecast,
        "is_open": 0,
    })

# 2. 150 OPEN ACTIVE DEALS FOR 2026-Q2 & 2026-Q3
# Include all 20 Tier 1 flagship accounts with dramatic stories
for i, (name, amt, tier) in enumerate(TIER_1_ACCOUNTS):
    idx = 50 + i
    deal_id = f"D-{counter + idx + 1}"
    rep = REPS[i % len(REPS)]
    stage = "Negotiation" if i % 3 == 0 else ("Proposal" if i % 3 == 1 else "Discovery")
    
    # Make some dramatic high-risk deals for the video demo
    if i in [0, 2, 4, 12]:  # Microsoft, Tata, Infosys, Flipkart
        days = random.randint(28, 52)
        eng = round(random.uniform(0.22, 0.38), 2)
        eb = 0
        note = "Economic buyer (CIO) skipped last 2 review calls. Stalled in legal for 32 days. Needs immediate executive sponsor escalation."
    else:
        days = random.randint(3, 12)
        eng = round(random.uniform(0.68, 0.94), 2)
        eb = 1
        note = "Multi-threaded across 4 departments. Security review passed. Target close end of month."
        
    rows.append({
        "deal_id": deal_id,
        "account": name,
        "rep": rep,
        "stage": stage,
        "amount": amt,
        "actual_revenue": 0,
        "close_date": f"2026-0{random.randint(4, 6)}-{random.randint(10, 28):02d}",
        "forecast_quarter": "2026-Q2",
        "days_since_activity": days,
        "engagement_score": eng,
        "has_economic_buyer": eb,
        "email_opens_14d": random.randint(1, 14),
        "meetings_30d": random.randint(1, 6),
        "stakeholders": random.randint(2, 6),
        "notes": note,
        "rep_forecast_amount": round(amt * 1.15 / 1000) * 1000,
        "is_open": 1,
    })

# Fill remaining open deals to reach 200 total
for i in range(130):
    idx = 70 + i
    deal_id = f"D-{counter + idx + 1}"
    account = random.choice(OTHER_ACCOUNTS)
    rep = random.choice(REPS)
    stage = random.choices(STAGES, weights=[10, 15, 25, 30, 20])[0]
    amt = random.randint(25, 380) * 1000
    
    fq = "2026-Q2" if i < 90 else "2026-Q3"
    m_val = random.randint(4, 6) if fq == "2026-Q2" else random.randint(7, 9)
    
    rows.append({
        "deal_id": deal_id,
        "account": account,
        "rep": rep,
        "stage": stage,
        "amount": amt,
        "actual_revenue": 0,
        "close_date": f"2026-0{m_val}-{random.randint(1, 28):02d}",
        "forecast_quarter": fq,
        "days_since_activity": random.randint(1, 45),
        "engagement_score": round(random.uniform(0.20, 0.90), 2),
        "has_economic_buyer": random.choice([0, 1]),
        "email_opens_14d": random.randint(0, 12),
        "meetings_30d": random.randint(0, 5),
        "stakeholders": random.randint(1, 5),
        "notes": random.choice(DRAMATIC_NOTES),
        "rep_forecast_amount": round(amt * 1.12 / 1000) * 1000,
        "is_open": 1,
    })

fields = [
    "deal_id", "account", "rep", "stage", "amount", "actual_revenue",
    "close_date", "forecast_quarter", "days_since_activity", "engagement_score",
    "has_economic_buyer", "email_opens_14d", "meetings_30d", "stakeholders",
    "notes", "rep_forecast_amount", "is_open"
]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Created: {OUT} with {len(rows)} deals")
