# Win / Loss Pattern Library — historical CRM patterns for RAG grounding

## Pattern: Champion-Only Deals

When the only active contact is a champion and the economic buyer never joins a call by Proposal:
- Historical win rate drops from ~52% to ~22% at Proposal.
- Typical loss reason: "lost to no decision" or competitor with CFO access.
- Next action: require an EB meeting as a stage-exit criterion; otherwise reduce weighted forecast by 35%.

## Pattern: Silent After Proposal

Deals with >14 days of silence after proposal_sent:
- 61% of such deals in trailing four quarters ended Closed Lost.
- Recovery that works: breakup email + decision deadline; recovery that fails: weekly "just checking in".
- If engagement_score < 0.35 and meetings_30d = 0, prefer recycle over commit.

## Pattern: Security Review Without Owner

Enterprise deals ($150k+) entering security/legal without a named owner:
- Average slip: 18 days; 28% slip out of quarter.
- Next action: assign security owner + weekly redline cadence; exec sponsor if ACV > $150k.

## Pattern: Engagement Cliff Mid-Discovery

Engagement_score falling below 0.45 while still in Discovery/Qualification:
- Often precedes champion job change or budget freeze.
- Multi-thread within 5 days; introduce SE for a technical win to re-activate.

## Pattern: Rep Forecast Optimism

Across holdout quarters, sum of rep_forecast_amount exceeded actual closed revenue by 18–40%.
Causes: carrying zombie deals, missing EB risk, ignoring stall thresholds.
Mitigation: apply risk haircuts before leadership commit calls.

## Positive Pattern: Mutual Close Plan

Deals with a dated mutual close plan (security, legal, signature owners) in Negotiation:
- Win rate +19 pp vs Negotiation deals without a plan.
- Next action for healthy late-stage deals: lock the plan this week; do not discount without give-get.
