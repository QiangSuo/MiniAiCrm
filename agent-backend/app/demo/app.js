const customerId = "CUST-DEMO-001";
const byId = (id) => document.getElementById(id);
let activeProposal = null;
let refreshGeneration = 0;
let identityGeneration = 0;

const context = () => ({ customer_id: customerId, user_id: byId("user-id").value });

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || `请求失败 (${response.status})`);
  return payload;
}

function toast(message, error = false) {
  const el = byId("toast");
  el.textContent = message;
  el.className = `toast show${error ? " error" : ""}`;
  window.clearTimeout(el.hideTimer);
  el.hideTimer = window.setTimeout(() => { el.className = "toast"; }, 3200);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[char]);
}

function formatAmount(value) {
  if (!value) return "¥0";
  return `¥${(value / 100000000).toFixed(1)}亿`;
}

function renderProposal(proposal) {
  activeProposal = proposal;
  byId("result-state").textContent = `${proposal.proposal_type} · ${proposal.status}`;
  const changes = proposal.changes.map((change) => `
    <article class="result-card">
      <strong>${escapeHtml(change.entity_type)} · ${escapeHtml(change.operation)}</strong>
      ${Object.entries(change.data).map(([key, value]) => `<p><span class="tag">${escapeHtml(key)}</span> ${escapeHtml(value)}</p>`).join("")}
    </article>`).join("");
  const conflicts = proposal.conflicts.length ? proposal.conflicts.map((item) => `
    <article class="result-card conflict-card"><strong>${escapeHtml(item.message)}</strong>
      <p>${escapeHtml(item.field)}：${escapeHtml(item.current)} → ${escapeHtml(item.proposed)}</p></article>`).join("") : "<p>未发现与已确认事实的冲突。</p>";
  const missing = proposal.missing_fields.length ? `<ul>${proposal.missing_fields.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : "<p>当前提案无必填缺失。</p>";
  byId("result-view").className = "result-view";
  byId("result-view").innerHTML = `
    <section class="result-section"><h3>拟议变更</h3>${changes}</section>
    <section class="result-section"><h3>冲突检查</h3>${conflicts}</section>
    <section class="result-section"><h3>缺失信息</h3>${missing}</section>
    <div class="confirm-bar"><span>确认后才会事务性写入正式事实，并记录审计轨迹。</span>
      <button id="confirm-proposal" class="button button-primary" type="button">确认并写入</button></div>`;
  byId("confirm-proposal").addEventListener("click", confirmProposal);
}

function renderAnswer(answer) {
  activeProposal = null;
  byId("result-state").textContent = `数据截止 ${new Date(answer.data_cutoff).toLocaleString("zh-CN")}`;
  const list = (title, values) => `<section class="result-section"><h3>${title}</h3>${values.map((value) => typeof value === "string" ? `<article class="result-card"><p>${escapeHtml(value)}</p></article>` : `<article class="result-card"><p>${escapeHtml(value.statement)}</p><span class="tag">${escapeHtml(value.confidence)}</span> <small>${escapeHtml(value.source_id)}</small></article>`).join("")}</section>`;
  byId("result-view").className = "result-view";
  byId("result-view").innerHTML = `
    <p class="answer-summary">${escapeHtml(answer.summary)}</p>
    ${list("已确认事实 / 单一来源线索", answer.facts)}
    ${list("Agent 推断", answer.inferences)}
    ${list("建议动作", answer.recommendations)}
    ${list("缺失信息", answer.missing_information)}
    <section class="result-section"><h3>来源</h3>${answer.sources.map((source) => `<article class="result-card"><strong>${escapeHtml(source.label)}</strong><p>${escapeHtml(source.type)} · ${escapeHtml(source.source_id)}</p></article>`).join("")}</section>`;
}

async function confirmProposal() {
  if (!activeProposal) return;
  const proposalId = activeProposal.proposal_id;
  const requestContext = context();
  const generation = identityGeneration;
  try {
    const confirmed = await api(`/api/proposals/${proposalId}/confirm`, {
      method: "POST", body: JSON.stringify(requestContext),
    });
    if (generation !== identityGeneration || context().user_id !== requestContext.user_id) return;
    renderProposal(confirmed);
    const button = byId("confirm-proposal");
    button.textContent = "已确认写入";
    button.disabled = true;
    toast("提案已确认，正式事实与审计记录已更新");
    await refreshAll();
  } catch (error) { toast(error.message, true); }
}


function clearSensitiveView(message = "切换身份后需重新授权访问") {
  activeProposal = null;
  ["kpi-opportunities", "kpi-amount", "kpi-actions", "kpi-risks", "kpi-pending"].forEach((id) => { byId(id).textContent = "—"; });
  byId("kpi-overdue").textContent = "逾期 —";
  byId("result-state").textContent = "访问上下文已清除";
  byId("result-view").className = "result-view empty-state";
  byId("result-view").innerHTML = `<div><h3>客户数据未显示</h3><p>${escapeHtml(message)}</p></div>`;
  byId("weekly-summary").textContent = message;
  byId("pending-list").innerHTML = '<div class="record">未返回任何待确认提案。</div>';
  byId("snapshot-view").innerHTML = `<section class="snapshot-group"><h3>客户数据未显示</h3><p>${escapeHtml(message)}</p></section>`;
  byId("audit-view").innerHTML = '<div class="record">未返回任何客户数据。</div>';
}

function renderDashboard(data) {
  byId("kpi-opportunities").textContent = data.active_opportunities;
  byId("kpi-amount").textContent = formatAmount(data.total_amount_cny);
  byId("kpi-actions").textContent = data.open_actions;
  byId("kpi-overdue").textContent = `逾期 ${data.overdue_actions}`;
  byId("kpi-risks").textContent = data.high_risks;
  byId("kpi-pending").textContent = data.pending_proposals;
  byId("weekly-summary").textContent = data.weekly_summary;
  byId("pending-list").innerHTML = data.pending_proposal_items.length
    ? data.pending_proposal_items.map((item) => `<div class="record"><strong>${escapeHtml(item.proposal_type)}</strong> · ${escapeHtml(item.proposal_id)}<time>${new Date(item.created_at).toLocaleString("zh-CN")} · 冲突 ${item.conflict_count}</time></div>`).join("")
    : '<div class="record">当前没有待确认提案。</div>';
}

function renderSnapshot(data) {
  const group = (title, items, render) => `<section class="snapshot-group"><h3>${title} · ${items.length}</h3>${items.length ? items.map(render).join("") : "<p>暂无已确认记录</p>"}</section>`;
  byId("snapshot-view").innerHTML = [
    group("关键人", data.contacts, (item) => `<p><strong>${escapeHtml(item.name)}</strong><br>${escapeHtml(item.role)}</p>`),
    group("商机", data.opportunities, (item) => `<p><strong>${escapeHtml(item.name)}</strong><br>${formatAmount(item.amount_cny)} · ${escapeHtml(item.stage)}<br><span class="tag">${escapeHtml(item.confidence)}</span></p>`),
    group("行动", data.actions, (item) => `<p><strong>${escapeHtml(item.description)}</strong><br>截止 ${escapeHtml(item.due_date || "待确认")}</p>`),
    group("资料证据", data.materials, (item) => `<p><strong>${escapeHtml(item.filename)}</strong><br>${escapeHtml(item.processing_status)}</p>`),
    group("风险", data.risks, (item) => `<p><strong>${escapeHtml(item.title)}</strong><br>${escapeHtml(item.level)} · ${escapeHtml(item.status)}</p>`),
    group("提案", data.proposals, (item) => `<p><strong>${escapeHtml(item.proposal_type)}</strong><br>${escapeHtml(item.status)} · ${escapeHtml(item.proposal_id)}</p>`),
  ].join("");
  byId("audit-view").innerHTML = data.audit_logs.slice(0, 8).map((item) => `<div class="record"><strong>${escapeHtml(item.action)}</strong><br>${escapeHtml(item.entity_type)} · ${escapeHtml(item.entity_id)}<time>${new Date(item.created_at).toLocaleString("zh-CN")} · ${escapeHtml(item.user_id)}</time></div>`).join("");
}

async function refreshAll() {
  const generation = ++refreshGeneration;
  const requestContext = context();
  const query = new URLSearchParams(requestContext);
  try {
    const [dashboard, snapshot] = await Promise.all([
      api(`/api/dashboard?${query}`),
      api(`/api/customers/${customerId}/snapshot?user_id=${encodeURIComponent(requestContext.user_id)}`),
    ]);
    if (generation !== refreshGeneration || context().user_id !== requestContext.user_id) return;
    renderDashboard(dashboard);
    renderSnapshot(snapshot);
  } catch (error) {
    if (generation !== refreshGeneration || context().user_id !== requestContext.user_id) return;
    clearSensitiveView(error.message);
    byId("snapshot-view").innerHTML = `<section class="snapshot-group"><h3>访问被拒绝</h3><p>${escapeHtml(error.message)}</p></section>`;
    toast(error.message, true);
  }
}

byId("progress-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const requestContext = context();
  const generation = identityGeneration;
  try {
    const proposal = await api("/api/intake/progress", { method: "POST", body: JSON.stringify({ ...requestContext, text: byId("progress-text").value }) });
    if (generation !== identityGeneration || context().user_id !== requestContext.user_id) return;
    renderProposal(proposal); toast("商务进展提案已生成，尚未写入正式事实"); await refreshAll();
  } catch (error) {
    if (generation === identityGeneration && context().user_id === requestContext.user_id) toast(error.message, true);
  }
});
byId("material-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const requestContext = context();
  const generation = identityGeneration;
  try {
    const proposal = await api("/api/intake/material", { method: "POST", body: JSON.stringify({ ...requestContext, filename: byId("material-filename").value, description: byId("material-description").value }) });
    if (generation !== identityGeneration || context().user_id !== requestContext.user_id) return;
    renderProposal(proposal); toast("资料归档提案已生成，尚未写入资料证据"); await refreshAll();
  } catch (error) {
    if (generation === identityGeneration && context().user_id === requestContext.user_id) toast(error.message, true);
  }
});
byId("question-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const requestContext = context();
  const generation = identityGeneration;
  try {
    const answer = await api("/api/questions", { method: "POST", body: JSON.stringify({ ...requestContext, question: byId("question-text").value }) });
    if (generation !== identityGeneration || context().user_id !== requestContext.user_id) return;
    renderAnswer(answer);
    toast("已基于当前已确认事实生成回答");
  } catch (error) {
    if (generation === identityGeneration && context().user_id === requestContext.user_id) toast(error.message, true);
  }
});
byId("reset-demo").addEventListener("click", async () => {
  try { await api("/api/demo/reset", { method: "POST" }); activeProposal = null; toast("Demo 数据已恢复到固定初始状态"); await refreshAll(); }
  catch (error) { toast(error.message, true); }
});
byId("refresh-all").addEventListener("click", refreshAll);
byId("user-id").addEventListener("change", async () => {
  identityGeneration += 1;
  clearSensitiveView();
  await refreshAll();
});
refreshAll();
