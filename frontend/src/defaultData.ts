export const DEFAULT_META = {
  n_deals: 200,
  n_open: 150,
  n_closed: 50,
  quarters: ["2026-Q2", "2026-Q3"],
  holdout: "2026-Q1",
  rag_chunks: 216,
  llm_connected: true,
};

export const DEFAULT_AGENT_STATUS = {
  agent_name: "PipelineForge CRO Orchestrator",
  framework: "LangGraph State Machine",
  nodes: ["forecast", "risk", "backtest", "rag_recommend", "simulate", "narrative"],
  llm_available: true,
  llm_model: "Groq Cloud LLM (openai/gpt-oss-120b)",
  vector_store: "ChromaDB (Local Disk)",
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2 (Local CPU)",
  indexed_chunks: 216,
  tools: [
    { name: "tool_forecast_pipeline", description: "Compute probabilistic revenue forecast (P10/P50/P90) via Monte Carlo." },
    { name: "tool_rank_risk_deals", description: "Rank open deals by 6-signal risk heuristic matrix." },
    { name: "tool_score_deal", description: "Score a single deal's risk with transparent telemetry." },
    { name: "tool_backtest_holdout", description: "Hold out 2026-Q1 and compare APE vs rep estimates and actuals." },
    { name: "tool_retrieve_playbook", description: "ChromaDB RAG retrieve sales playbooks with [C#] citations." },
    { name: "tool_simulate_commit", description: "Simulate executing next-best-actions to compute P50 lift." },
    { name: "tool_rep_calibration", description: "Score sales rep historical optimism bias." },
  ],
};

export const DEFAULT_RISKS = [
  {
    deal_id: "D-2052",
    account: "Amazon Web Services Migration",
    rep: "Rahul Sharma",
    stage: "Proposal",
    amount: 1200000,
    risk_score: 0.74,
    risk_band: "high",
    signals: [
      { code: "stalled_activity", label: "Stalled Activity", detail: "21 days since last recorded interaction (threshold: 14d)" },
      { code: "stage_overage", label: "Stage Overage", detail: "44 days in Proposal vs historical median of 18 days" },
      { code: "missing_economic_buyer", label: "Missing Economic Buyer", detail: "No VP/C-suite decision maker mapped in opportunity" },
    ],
    days_since_activity: 21,
    engagement_score: 0.38,
    has_economic_buyer: 0,
    notes: "Champion is enthusiastic, but procurement review has been delayed twice. Legal redlines pending.",
  },
  {
    deal_id: "D-2054",
    account: "Reliance Digital Infrastructure",
    rep: "Priya Patil",
    stage: "Negotiation",
    amount: 920000,
    risk_score: 0.68,
    risk_band: "high",
    signals: [
      { code: "stalled_activity", label: "Stalled Activity", detail: "19 days since last touchpoint" },
      { code: "engagement_drop", label: "Engagement Drop", detail: "Zero email opens or portal logins in past 14 days" },
    ],
    days_since_activity: 19,
    engagement_score: 0.42,
    has_economic_buyer: 1,
    notes: "Security clearance granted. Commercial terms agreed verbally but signature delayed.",
  },
  {
    deal_id: "D-2056",
    account: "HDFC Bank Core Banking Sync",
    rep: "Amit Kulkarni",
    stage: "Discovery",
    amount: 750000,
    risk_score: 0.65,
    risk_band: "high",
    signals: [
      { code: "missing_economic_buyer", label: "Missing Economic Buyer", detail: "Only tech lead engaged; CISO and Head of Retail unmapped" },
      { code: "zero_touch", label: "Low Meeting Velocity", detail: "Zero meetings booked in past 30 days" },
    ],
    days_since_activity: 18,
    engagement_score: 0.35,
    has_economic_buyer: 0,
    notes: "POC successful in sandbox. Awaiting executive budget committee presentation date.",
  },
  {
    deal_id: "D-2069",
    account: "Bharti Airtel 5G Core OSS",
    rep: "Sneha Iyer",
    stage: "Negotiation",
    amount: 780000,
    risk_score: 0.58,
    risk_band: "medium",
    signals: [
      { code: "stage_overage", label: "Stage Overage", detail: "36 days in Negotiation vs median of 15 days" },
    ],
    days_since_activity: 12,
    engagement_score: 0.55,
    has_economic_buyer: 1,
    notes: "Vendor consolidation review underway. Competing against incumbent legacy renewal.",
  },
  {
    deal_id: "D-2070",
    account: "Larsen & Toubro Smart Site",
    rep: "Vikram Malhotra",
    stage: "Proposal",
    amount: 610000,
    risk_score: 0.52,
    risk_band: "medium",
    signals: [
      { code: "stalled_activity", label: "Stalled Activity", detail: "16 days since last customer touchpoint" },
    ],
    days_since_activity: 16,
    engagement_score: 0.60,
    has_economic_buyer: 1,
    notes: "Awaiting CFO capex approval for Q2 rollout across 14 infrastructure project locations.",
  },
  {
    deal_id: "D-2066",
    account: "Cisco Unified Comms Modernize",
    rep: "Rahul Sharma",
    stage: "Negotiation",
    amount: 640000,
    risk_score: 0.48,
    risk_band: "medium",
    signals: [
      { code: "engagement_drop", label: "Engagement Drop", detail: "Champion communication slowed following org restructuring" },
    ],
    days_since_activity: 14,
    engagement_score: 0.58,
    has_economic_buyer: 1,
    notes: "Internal re-org created new budget holder. Re-qualifying champion authority.",
  },
  {
    deal_id: "D-2067",
    account: "Oracle Cloud Database Engine",
    rep: "Priya Patil",
    stage: "Proposal",
    amount: 590000,
    risk_score: 0.45,
    risk_band: "medium",
    signals: [
      { code: "stage_overage", label: "Stage Overage", detail: "28 days in Proposal vs median of 18 days" },
    ],
    days_since_activity: 10,
    engagement_score: 0.65,
    has_economic_buyer: 1,
    notes: "Enterprise agreement draft with legal team. Expected signature within 2 weeks.",
  },
  {
    deal_id: "D-2059",
    account: "Salesforce CRM Data Pipeline",
    rep: "Amit Kulkarni",
    stage: "Discovery",
    amount: 550000,
    risk_score: 0.42,
    risk_band: "medium",
    signals: [
      { code: "missing_economic_buyer", label: "Missing Economic Buyer", detail: "Director of RevOps engaged; VP Sales not yet introduced" },
    ],
    days_since_activity: 8,
    engagement_score: 0.70,
    has_economic_buyer: 0,
    notes: "Discovery completed. Preparing custom ROI business case for VP Sales review.",
  },
];

export const DEFAULT_BACKTEST = {
  backtest: {
    holdout_quarter: "2026-Q1",
    n_deals: 50,
    actual_revenue: 8192000,
    model_expected: 6262052,
    rep_forecast_total: 15623000,
    model_abs_pct_error: 23.56,
    rep_abs_pct_error: 90.71,
    error_improvement_pp: 67.15,
    p10: 4980000,
    p50: 6310000,
    p90: 7820000,
  },
  rep_calibration: [
    { rep: "Rahul Sharma", deals: 8, closed_won_acv: 1820000, rep_forecast_total: 3450000, actual_revenue: 1820000, abs_pct_error: 89.56, win_rate: 0.62, optimism_bias: "Extreme Over-Forecast" },
    { rep: "Priya Patil", deals: 7, closed_won_acv: 1450000, rep_forecast_total: 2900000, actual_revenue: 1450000, abs_pct_error: 100.0, win_rate: 0.57, optimism_bias: "Extreme Over-Forecast" },
    { rep: "Amit Kulkarni", deals: 9, closed_won_acv: 1940000, rep_forecast_total: 3100000, actual_revenue: 1940000, abs_pct_error: 59.79, win_rate: 0.67, optimism_bias: "Moderate Over-Forecast" },
    { rep: "Sneha Iyer", deals: 6, closed_won_acv: 1180000, rep_forecast_total: 2200000, actual_revenue: 1180000, abs_pct_error: 86.44, win_rate: 0.50, optimism_bias: "Extreme Over-Forecast" },
    { rep: "Vikram Malhotra", deals: 8, closed_won_acv: 1802000, rep_forecast_total: 3973000, actual_revenue: 1802000, abs_pct_error: 120.48, win_rate: 0.50, optimism_bias: "Extreme Over-Forecast" },
  ],
};

export const DEFAULT_BRIEFING = {
  quarter: "2026-Q2",
  forecast: {
    quarter: "2026-Q2",
    n_deals: 110,
    coverage: 31879000,
    rep_roll_up: 36056000,
    p10: 7702500,
    p50: 9692000,
    p90: 11685100,
    expected: 9738724,
    commit: 2689160,
    best_case: 14873360,
    deal_contributions: [
      { deal_id: "D-2054", account: "Reliance Digital Infrastructure", amount: 920000, stage: "Negotiation", win_prob: 0.68, weighted: 625600, risk_score: 0.68, risk_band: "high" },
      { deal_id: "D-2052", account: "Amazon Web Services Migration", amount: 1200000, stage: "Proposal", win_prob: 0.52, weighted: 624000, risk_score: 0.74, risk_band: "high" },
      { deal_id: "D-2069", account: "Bharti Airtel 5G Core OSS", amount: 780000, stage: "Negotiation", win_prob: 0.68, weighted: 530400, risk_score: 0.58, risk_band: "medium" },
      { deal_id: "D-2066", account: "Cisco Unified Comms Modernize", amount: 640000, stage: "Negotiation", win_prob: 0.68, weighted: 435200, risk_score: 0.48, risk_band: "medium" },
      { deal_id: "D-2070", account: "Larsen & Toubro Smart Site", amount: 610000, stage: "Proposal", win_prob: 0.52, weighted: 317200, risk_score: 0.52, risk_band: "medium" },
      { deal_id: "D-2067", account: "Oracle Cloud Database Engine", amount: 590000, stage: "Proposal", win_prob: 0.52, weighted: 306800, risk_score: 0.45, risk_band: "medium" },
      { deal_id: "D-2056", account: "HDFC Bank Core Banking Sync", amount: 750000, stage: "Discovery", win_prob: 0.38, weighted: 285000, risk_score: 0.65, risk_band: "high" },
      { deal_id: "D-2057", account: "Snowflake Analytics Integration", amount: 380000, stage: "Negotiation", win_prob: 0.68, weighted: 258400, risk_score: 0.28, risk_band: "low" },
      { deal_id: "D-2064", account: "Uber Enterprise Mobility API", amount: 460000, stage: "Proposal", win_prob: 0.52, weighted: 239200, risk_score: 0.32, risk_band: "low" },
      { deal_id: "D-2058", account: "Stripe Payments API Gateway", amount: 420000, stage: "Proposal", win_prob: 0.52, weighted: 218400, risk_score: 0.35, risk_band: "medium" },
      { deal_id: "D-2060", account: "Wipro Cybersecurity Upgrade", amount: 320000, stage: "Negotiation", win_prob: 0.68, weighted: 217600, risk_score: 0.22, risk_band: "low" },
      { deal_id: "D-2059", account: "Salesforce CRM Data Pipeline", amount: 550000, stage: "Discovery", win_prob: 0.38, weighted: 209000, risk_score: 0.42, risk_band: "medium" },
    ],
  },
  risks: DEFAULT_RISKS,
  backtest: DEFAULT_BACKTEST.backtest,
  recommendations: [
    {
      deal_id: "D-2052",
      account: "Amazon Web Services Migration",
      risk_band: "high",
      action: "Issue a 5-business-day mutual close plan with milestone deliverables [C1]. Schedule executive sponsor alignment with VP Cloud Infrastructure [C2].",
      rationale: "Stalled 21 days with no EB mapped; conversion falls 48% without multi-threading.",
      citation_ids: ["C1", "C2"],
    },
    {
      deal_id: "D-2054",
      account: "Reliance Digital Infrastructure",
      risk_band: "high",
      action: "Execute VP Sales intervention to unblock commercial signature bottleneck [C1] [C3].",
      rationale: "Contract agreed verbally; inactivity signals buyer freeze.",
      citation_ids: ["C1", "C3"],
    },
    {
      deal_id: "D-2056",
      account: "HDFC Bank Core Banking Sync",
      risk_band: "high",
      action: "Request Economic Buyer introduction this week; present 20-minute ROI review before security review concludes [C2].",
      rationale: "Discovery stage without EB reduces pipeline velocity by 60%.",
      citation_ids: ["C2"],
    },
  ],
  simulation: {
    p50_lift: 840000,
    scenario_p50: 10532000,
    n_intervened: 3,
  },
  narrative: `Executive Pipeline Briefing for 2026-Q2:
• Revenue Outlook: Our 4,000-run Monte Carlo simulation establishes an expected P50 revenue of $9.69M, framed by a robust confidence interval of $7.70M (P10 Bear) to $11.69M (P90 Bull).
• The Optimism Gap: Sales reps have rolled up an unweighted commit of $36.06M, exposing an acute $26.36M optimism bias. A significant portion of this pipeline is tied up in stalled late-stage evaluations.
• Risk Concentration & Action Queue: We have flagged 8 high-exposure enterprise accounts totaling $5.7M at risk. Executing immediate executive sponsor alignments and dated mutual close plans on AWS ($1.2M) and Reliance ($920K) is projected to lift P50 revenue by +$840K this quarter.
• Backtest Validation (Feature 7): Model validation against 2026-Q1 holdout data confirms a 23.56% APE compared to human reps' 90.71% error rate (+67.15 pp accuracy lift).`,
  citations: [
    { id: "C1", source: "sales_playbook.md", excerpt: "When deal inactivity exceeds 14 days in Proposal/Negotiation, mandate executive sponsor outreach within 48 hours." },
    { id: "C2", source: "objection_and_stall_playbook.md", excerpt: "Deals lacking mapped Economic Buyers suffer a 48% lower win rate and 2.4x longer sales cycle length." },
    { id: "C3", source: "win_loss_patterns.md", excerpt: "Late-stage verbal commitments with stalled signature queues require CEO/CRO intervention before week 10." },
  ],
  trace: ["node_forecast", "node_risk", "node_backtest", "node_rag_recommend", "node_simulate", "node_narrative"],
};

export function parseCsvDeals(csvText: string): { deals: any[]; message: string } {
  const lines = csvText.trim().split("\n");
  if (lines.length < 2) return { deals: [], message: "CSV file is empty or has no header." };

  const headers = lines[0].split(",").map(h => h.trim().toLowerCase().replace(/['"]/g, ""));
  const deals: any[] = [];

  for (let i = 1; i < lines.length; i++) {
    const row = lines[i].split(",").map(v => v.trim().replace(/['"]/g, ""));
    if (row.length < headers.length) continue;
    const item: any = {};
    headers.forEach((h, idx) => {
      item[h] = row[idx];
    });

    const amount = parseFloat(item.amount || item.value || item.deal_size || "75000") || 75000;
    const stage = item.stage || "Proposal";
    const deal_id = item.deal_id || item.id || `D-${2000 + i}`;
    const account = item.account || item.company || item.name || `Enterprise Account ${i}`;
    const rep = item.rep || item.owner || item.sales_rep || "Account Rep";

    deals.push({
      deal_id,
      account,
      rep,
      stage,
      amount,
      risk_score: Math.min(0.85, Math.max(0.15, (parseFloat(item.days_since_activity || "12") / 30) * 0.7)),
      risk_band: stage === "Negotiation" ? "medium" : "high",
      signals: [
        { code: "stalled_activity", label: "Uploaded Account", detail: `Imported from custom CRM CSV (${stage})` }
      ],
      days_since_activity: parseInt(item.days_since_activity || "14"),
      engagement_score: parseFloat(item.engagement_score || "0.6"),
      has_economic_buyer: parseInt(item.has_economic_buyer || "1"),
      notes: item.notes || "Imported custom CRM deal",
    });
  }

  return { deals, message: `Successfully loaded ${deals.length} deals from CSV file` };
}
