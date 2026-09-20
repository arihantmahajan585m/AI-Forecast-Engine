# QBR Leadership Operating Notes — PipelineForge KB

## Monday Commit Ritual

1. Start from agent P50, not rep roll-up.
2. Review P10–P90 band; if commit sits above P50, require named risk mitigations.
3. Walk the top-10 risk queue; each deal needs one owner and one dated action.
4. Compare last quarter holdout: if model APE beat reps, keep the haircut policy.

## Commit vs Best Case vs Pipeline Coverage

- Coverage = sum of open amounts in the forecast quarter.
- Best case = stage win rates without risk haircuts (usually too high).
- Commit = Negotiation + low risk + economic buyer present.
- P50 is the default leadership number for board updates.

## What Not To Say in Forecast Calls

Avoid vague language: "needs attention", "following up", "looking good".
Require evidence: days since activity, engagement score, EB present/absent, and a concrete next step with a date.

## Edge Cases

- Empty open pipeline for a quarter → forecast returns zeros; surface empty state, do not invent.
- Uploaded CSV missing columns → reject with a clear schema error.
- Deal ID not found → return an explicit error; do not hallucinate accounts.
