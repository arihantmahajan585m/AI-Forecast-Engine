# Sales Methodology Playbook — PipelineForge Knowledge Base
# Used by RAG for grounded next-best-actions and risk explanations.

## Economic Buyer Engagement

Deals without an identified economic buyer (EB) convert at less than half the rate of deals with EB participation by the Proposal stage.
Recommended actions:
1. Ask the champion to map the approval chain and name the budget holder.
2. Request a 20-minute value review with the EB focused on ROI, not product features.
3. If the champion blocks access, treat as a structural risk and lower forecast weight by 25–40%.

Signal thresholds:
- Missing EB after Discovery → high risk
- EB present but silent >14 days → medium risk
- EB attended demo or pricing call in last 10 days → positive signal

## Stalled Pipeline Recovery

A deal is considered stalled when there is no meaningful activity for 14+ days in mid/late stages, or 21+ days in early stages.
Recovery playbook:
1. Send a breakup email that creates a decision deadline within 5 business days.
2. Re-qualify mutual close plan: next meeting, decision criteria, and paper process.
3. If no response in 7 days after breakup, move to Closed Lost or recycle to nurture — do not keep in commit forecast.

Do not recommend "just follow up" without a specific ask and date.

## Engagement Drop Detection

Engagement drop = email opens and meetings falling >40% vs prior 30-day window, or engagement_score < 0.45 with stage ≥ Discovery.
Actions:
1. Change the channel: call instead of email; involve a SE for a technical deep-dive.
2. Multi-thread: introduce a second stakeholder so the deal is not single-threaded on the champion.
3. Surface a business trigger (renewal, compliance deadline, board date) to re-create urgency.

## Negotiation Stage Risks

Late-stage risk patterns that frequently flip Closed Won → Closed Lost:
- Legal/security review started but no owner assigned
- Discount requested without EB on the thread
- Close date slipped more than once
- Champion changed jobs mid-cycle

Next best actions:
1. Joint close plan with dates for redlines, security sign-off, and signature.
2. Escalate internally for executive sponsor alignment if amount > $150k.
3. Cap discount to a documented give-get; never discount to buy a forecast.

## Forecast Hygiene for Leadership

Weighted pipeline should use stage win rates calibrated on trailing four quarters, adjusted for deal-level risk modifiers.
Confidence bands:
- P10 / P50 / P90 from Monte Carlo sampling of deal win probabilities
- Commit layer = Negotiation deals with risk_score < 0.35 and EB present
- Best case = all open deals at stage win rate without risk haircuts

Rep estimates are systematically optimistic by 15–35% on open pipeline; always compare agent forecast vs rep roll-up in leadership reviews.

## Industry Nuances

FinTech / Healthcare: security and compliance reviews add 2–4 weeks — build into close dates.
Manufacturing: procurement cycles are calendar-quarter bound; slipped Q-end deals rarely close in the first two weeks of next quarter.
SaaS mid-market: champion-led deals without EB fail most often at Proposal.
