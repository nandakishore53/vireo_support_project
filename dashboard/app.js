/**
 * Vireo Audio Support Analytics — Executive Dashboard Controller
 * Authoritative source: window.VIREO_DATA (from data.js or data.json)
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Ensure Data is Loaded
  const data = window.VIREO_DATA;
  if (!data) {
    console.error("VIREO_DATA not found. Attempting to fetch data.json...");
    fetch("data.json")
      .then(res => res.json())
      .then(jsonData => {
        window.VIREO_DATA = jsonData;
        initDashboard(jsonData);
      })
      .catch(err => {
        document.body.innerHTML = `<div style="padding: 40px; text-align: center; color: red;">
          <h2>Failed to load dashboard data</h2>
          <p>${err.message}</p>
        </div>`;
      });
  } else {
    initDashboard(data);
  }
});

function initDashboard(data) {
  setupNavigation();
  renderExecutiveSummary(data);
  renderRawContractualView(data);
  renderRecommendedShortlist(data);
  setupAgentInspector(data);
  renderWhyNotRawBottom10(data);
  renderBusinessImpact(data);
  renderAIDiagnostics(data);
  renderDataQualityLimitations();
}

/**
 * View Navigation
 */
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetView = tab.getAttribute("data-view");
      switchView(targetView);
    });
  });
}

function switchView(viewId) {
  document.querySelectorAll(".nav-tab").forEach(t => {
    t.classList.toggle("active", t.getAttribute("data-view") === viewId);
  });
  document.querySelectorAll(".view-section").forEach(s => {
    s.classList.toggle("active", s.id === viewId);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Format Currency (INR)
 */
function formatINR(val) {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return "₹" + Math.round(val).toLocaleString("en-IN");
}

/**
 * Format Percent
 */
function formatPercent(val) {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return (val * 100).toFixed(1) + "%";
}

/**
 * VIEW 1 — EXECUTIVE SUMMARY
 */
function renderExecutiveSummary(data) {
  const sla = data.kpis.sla;
  const dd = data.kpis.double_dipping;

  // KPI 1: Baseline Breaches
  document.getElementById("exec-baseline-breaches").innerText = `${sla.historical_breaches_18m} Breaches`;
  document.getElementById("exec-baseline-cost").innerText = formatINR(sla.historical_cost_18m_inr);
  
  // Scenario Cards
  const sc25 = sla.scenarios["25%"];
  const sc50 = sla.scenarios["50%"];
  const sc75 = sla.scenarios["75%"];

  document.getElementById("exec-sc-25-val").innerText = formatINR(sc25.annualized_savings_inr) + " / yr";
  document.getElementById("exec-sc-25-breaches").innerText = `${sc25.breaches_avoided_annual} breaches avoided / yr`;

  document.getElementById("exec-sc-50-val").innerText = formatINR(sc50.annualized_savings_inr) + " / yr";
  document.getElementById("exec-sc-50-breaches").innerText = `${sc50.breaches_avoided_annual} breaches avoided / yr`;

  document.getElementById("exec-sc-75-val").innerText = formatINR(sc75.annualized_savings_inr) + " / yr";
  document.getElementById("exec-sc-75-breaches").innerText = `${sc75.breaches_avoided_annual} breaches avoided / yr`;

  // Process Control
  document.getElementById("exec-dd-exposure").innerText = formatINR(dd.historical_combined_exposure_inr);
  document.getElementById("exec-dd-orders").innerText = `${dd.affected_orders_count} confirmed orders`;
}

/**
 * VIEW 2 — PRIYA'S REQUESTED RAW VIEW
 */
function renderRawContractualView(data) {
  const rawList = data.raw_bottom10;
  const csatTableBody = document.querySelector("#table-raw-csat tbody");
  const htTableBody = document.querySelector("#table-raw-ht tbody");

  const csatItems = rawList.filter(r => r.metric_basis === "Lowest Raw Mean CSAT");
  const htItems = rawList.filter(r => r.metric_basis === "Highest Audited Median Handle Time");

  csatTableBody.innerHTML = csatItems.map(item => `
    <tr onclick="inspectAgent('${item.agent_id}')">
      <td><strong>#${item.raw_rank}</strong></td>
      <td><strong>${item.agent_name}</strong></td>
      <td><code>${item.agent_id}</code></td>
      <td>${item.team}</td>
      <td><span class="badge-tag badge-tier-${item.tier}">Tier ${item.tier}</span></td>
      <td><strong style="color: var(--danger);">${item.raw_mean_csat ? item.raw_mean_csat.toFixed(2) : "—"}</strong></td>
      <td>${item.median_audited_handle_time_hours ? item.median_audited_handle_time_hours.toFixed(1) + "h" : "—"}</td>
      <td>${formatPercent(item.sla_breach_rate)}</td>
      <td><span class="badge-tag badge-warning">${item.queue_bias_explanation}</span></td>
    </tr>
  `).join("");

  htTableBody.innerHTML = htItems.map(item => `
    <tr onclick="inspectAgent('${item.agent_id}')">
      <td><strong>#${item.raw_rank}</strong></td>
      <td><strong>${item.agent_name}</strong></td>
      <td><code>${item.agent_id}</code></td>
      <td>${item.team}</td>
      <td><span class="badge-tag badge-tier-${item.tier}">Tier ${item.tier}</span></td>
      <td>${item.raw_mean_csat ? item.raw_mean_csat.toFixed(2) : "—"}</td>
      <td><strong style="color: var(--danger);">${item.median_audited_handle_time_hours ? item.median_audited_handle_time_hours.toFixed(1) + "h" : "—"}</strong></td>
      <td>${formatPercent(item.sla_breach_rate)}</td>
      <td><span class="badge-tag badge-warning">${item.queue_bias_explanation}</span></td>
    </tr>
  `).join("");
}

/**
 * VIEW 3 — FAIR RECOMMENDED SHORTLIST
 */
function renderRecommendedShortlist(data) {
  const candidates = data.training_candidates;
  const tbody = document.querySelector("#table-training-candidates tbody");

  tbody.innerHTML = candidates.map((c, idx) => {
    let trackClass = "badge-track-1";
    if (c.track.includes("Track 2")) trackClass = "badge-track-2";
    if (c.track.includes("Track 3")) trackClass = "badge-track-3";

    return `
      <tr onclick="inspectAgent('${c.agent_id}')">
        <td><strong>#${idx + 1}</strong></td>
        <td><strong>${c.name}</strong></td>
        <td><code>${c.agent_id}</code></td>
        <td>${c.team}</td>
        <td><span class="badge-tag ${trackClass}">${c.track.split(":")[0]}</span></td>
        <td><strong>${c.key_metric}</strong>: ${c.metric_value}</td>
        <td><small style="color: var(--text-subtle);">${c.peer_value}</small></td>
        <td>${c.reason}</td>
        <td><span class="badge-tag" style="background-color: var(--primary-light); color: var(--primary-dark); font-size: 11px;">${c.recommended_action}</span></td>
      </tr>
    `;
  }).join("");
}

/**
 * VIEW 4 — AGENT INSPECTOR
 */
let currentAgentData = null;

function setupAgentInspector(data) {
  const select = document.getElementById("inspector-agent-select");
  select.innerHTML = data.agent_metrics
    .slice()
    .sort((a, b) => a.agent_id.localeCompare(b.agent_id))
    .map(a => `<option value="${a.agent_id}">${a.agent_id} — ${a.agent_name} (${a.team})</option>`)
    .join("");

  select.addEventListener("change", (e) => {
    renderAgentDetail(e.target.value, data);
  });

  // Default to first training candidate (A3003)
  renderAgentDetail("A3003", data);
}

function inspectAgent(agentId) {
  switchView("view-inspector");
  const select = document.getElementById("inspector-agent-select");
  if (select) {
    select.value = agentId;
  }
  renderAgentDetail(agentId, window.VIREO_DATA);
}

function renderAgentDetail(agentId, data) {
  const agent = data.agent_metrics.find(a => a.agent_id === agentId);
  if (!agent) return;

  currentAgentData = agent;
  const isCandidate = data.training_candidates.find(c => c.agent_id === agentId);

  document.getElementById("insp-agent-title").innerText = `${agent.agent_name} (${agent.agent_id})`;
  document.getElementById("insp-agent-meta").innerHTML = `
    <strong>Team:</strong> ${agent.team} | 
    <strong>Site:</strong> ${agent.site} | 
    <strong>Shift:</strong> ${agent.shift} | 
    <strong>Tier:</strong> ${agent.tier} | 
    <strong>Peer Group:</strong> ${agent.peer_group}
    ${isCandidate ? ` | <span class="badge-tag badge-track-1" style="margin-left: 8px;">Recommended for ${isCandidate.track}</span>` : ""}
  `;

  // Metric Boxes
  document.getElementById("insp-tickets").innerText = agent.ticket_count;
  document.getElementById("insp-csat-raw").innerText = agent.raw_mean_csat ? agent.raw_mean_csat.toFixed(3) : "—";
  document.getElementById("insp-csat-count").innerText = `${agent.csat_response_count} responses (${formatPercent(agent.csat_response_rate)})`;
  
  document.getElementById("insp-csat-peer").innerText = agent.peer_mean_csat ? agent.peer_mean_csat.toFixed(3) : "—";
  document.getElementById("insp-csat-shrunk").innerText = agent.empirical_bayes_shrunk_csat ? agent.empirical_bayes_shrunk_csat.toFixed(3) : "—";

  document.getElementById("insp-ht-raw").innerText = agent.mean_raw_handle_time_hours ? agent.mean_raw_handle_time_hours.toFixed(2) + "h" : "—";
  document.getElementById("insp-ht-audited").innerText = agent.mean_audited_handle_time_hours ? agent.mean_audited_handle_time_hours.toFixed(2) + "h" : "—";
  document.getElementById("insp-ht-median").innerText = agent.median_audited_handle_time_hours ? agent.median_audited_handle_time_hours.toFixed(2) + "h" : "—";

  document.getElementById("insp-sla-breaches").innerText = agent.sla_breach_count;
  document.getElementById("insp-sla-rate").innerText = formatPercent(agent.sla_breach_rate);
  document.getElementById("insp-sla-penalty").innerText = formatINR(agent.sla_penalty_liability_inr);

  document.getElementById("insp-transfers").innerText = `${agent.transfers_count} (${formatPercent(agent.transfers_rate)})`;
  document.getElementById("insp-replacements").innerText = `${agent.replacements_count} (${formatPercent(agent.replacements_rate)})`;
  document.getElementById("insp-refunds").innerText = `${agent.refunds_count} (${formatINR(agent.refunds_total_inr)})`;
  document.getElementById("insp-double-dipping").innerText = agent.double_dipped_tickets_count;

  // Legacy Note
  const legacyBox = document.getElementById("insp-legacy-note");
  if (agent.negative_raw_handle_time_count > 0) {
    legacyBox.style.display = "block";
    legacyBox.innerHTML = `<strong>Legacy Timestamp Offset Applied:</strong> This agent had ${agent.negative_raw_handle_time_count} legacy tickets migrated from Freshdesk prior to the 14 September 2025 cutover with negative raw handle times caused by the UTC/IST mismatch. A deterministic +05:30 (+330 min) correction was applied.`;
  } else {
    legacyBox.style.display = "none";
  }
}

/**
 * VIEW 5 — WHY NOT THE RAW BOTTOM 10?
 */
function renderWhyNotRawBottom10(data) {
  const kavyaList = ["A3004", "A3005", "A3006", "A3007"];
  const kavyaAgents = data.agent_metrics.filter(a => kavyaList.includes(a.agent_id));
  const tbody = document.querySelector("#table-kavya-explanation tbody");

  tbody.innerHTML = kavyaAgents.map(a => `
    <tr onclick="inspectAgent('${a.agent_id}')">
      <td><strong>${a.agent_name}</strong></td>
      <td><code>${a.agent_id}</code></td>
      <td>${a.team}</td>
      <td><strong>${a.raw_mean_csat ? a.raw_mean_csat.toFixed(2) : "—"}</strong></td>
      <td>${a.empirical_bayes_shrunk_csat ? a.empirical_bayes_shrunk_csat.toFixed(2) : "—"}</td>
      <td>${formatPercent(a.sla_breach_rate)}</td>
      <td>${a.median_audited_handle_time_hours ? a.median_audited_handle_time_hours.toFixed(1) + "h" : "—"}</td>
      <td><span class="badge-tag badge-warning">Assigned to Hardware Triage rota during Pulse 2 battery defect surge (2x company defect baseline). Not recommended for punitive training.</span></td>
    </tr>
  `).join("");
}

/**
 * VIEW 6 — BUSINESS IMPACT & SENSITIVITY
 */
function renderBusinessImpact(data) {
  const sla = data.kpis.sla;
  const dd = data.kpis.double_dipping;

  // Double Dipping Summary (with null checks)
  const ddOrders = document.getElementById("biz-dd-orders");
  if (ddOrders) ddOrders.innerText = dd.affected_orders_count;
  const ddRefunds = document.getElementById("biz-dd-refunds");
  if (ddRefunds) ddRefunds.innerText = formatINR(dd.historical_refunds_inr);
  const ddReplacements = document.getElementById("biz-dd-replacements");
  if (ddReplacements) ddReplacements.innerText = formatINR(dd.historical_replacement_cost_inr);
  const ddCombined = document.getElementById("biz-dd-combined");
  if (ddCombined) ddCombined.innerText = formatINR(dd.historical_combined_exposure_inr);
  const ddAnnualized = document.getElementById("biz-dd-annualized");
  if (ddAnnualized) ddAnnualized.innerText = formatINR(dd.annualized_exposure_inr) + " / year";

  // Interactive Scenario Selector
  const buttons = document.querySelectorAll(".btn-scenario-select");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const pct = btn.getAttribute("data-pct") || "50%";
      updateScenarioDisplay(pct, sla);
    });
  });

  // Default to 50%
  updateScenarioDisplay("50%", sla);
}

function updateScenarioDisplay(pct, sla) {
  const cleanPct = pct && pct.includes("%") ? pct : (pct ? pct + "%" : "50%");
  const sc = sla.scenarios[cleanPct] || sla.scenarios["50%"];
  if (!sc) return;

  const pctEl = document.getElementById("biz-sc-pct");
  if (pctEl) pctEl.innerText = cleanPct;

  const savingsAnnualEl = document.getElementById("biz-sc-savings-annual");
  if (savingsAnnualEl) savingsAnnualEl.innerText = formatINR(sc.annualized_savings_inr) + " / year";

  const savings18mEl = document.getElementById("biz-sc-savings-18m");
  if (savings18mEl) savings18mEl.innerText = formatINR(sc.baseline_18m_savings_inr) + " (over 18m baseline)";

  const breachesAvoidedEl = document.getElementById("biz-sc-breaches-avoided");
  if (breachesAvoidedEl) breachesAvoidedEl.innerText = `${sc.breaches_avoided_annual.toFixed(1)} breaches avoided / year`;
}

/**
 * VIEW 7 — AI QUALITATIVE DIAGNOSTICS
 */
function renderAIDiagnostics(data) {
  const ai = data.ai_audit;
  const halTable = document.querySelector("#table-ai-hallucinations tbody");

  halTable.innerHTML = ai.hallucination_review.map(h => `
    <tr>
      <td><code>${h.ticket_id}</code></td>
      <td><span class="badge-tag ${h.severity === 'high' ? 'badge-track-1' : h.severity === 'medium' ? 'badge-track-2' : 'badge-warning'}">${h.severity.toUpperCase()}</span></td>
      <td><strong>${h.issue_type}</strong></td>
      <td><small style="color: var(--danger);">${h.claim}</small></td>
      <td><small style="color: var(--text-muted);">${h.supporting_evidence}</small></td>
      <td><span class="badge-tag" style="background-color: var(--primary-light); color: var(--primary-dark); font-size: 11px;">${h.action}</span></td>
    </tr>
  `).join("");
}

/**
 * VIEW 8 — DATA QUALITY LIMITATIONS
 */
function renderDataQualityLimitations() {
  const headers = document.querySelectorAll(".accordion-header");
  headers.forEach(h => {
    h.addEventListener("click", () => {
      const parent = h.parentElement;
      parent.classList.toggle("open");
    });
  });
}
