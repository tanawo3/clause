import { makeReader, write, connectWallet, activeAccount, short, fmtErr } from "./shared/genlayer-lite.js";
import { mountReviewDesk } from "./shared/review-desk.js";
import { CONTRACT, NETWORK, DEMO } from "./config.js";

const { read } = makeReader(CONTRACT);
const VERDICT = ["Pending", "Permitted", "Prohibited", "Unclear"];
const STAMP = ["pending", "permit", "prohibit", "unclear"];
const $ = (id) => document.getElementById(id);
const app = () => $("app");

queueMicrotask(() => mountReviewDesk({
  contract: CONTRACT, read, write, ensureWallet, fmtErr,
  entity: "Policy query", idLabel: "Query ID", countMethod: "get_claim_count", recordMethod: "get_claim_record",
  openWindowMethod: "open_challenge_window", submitChallengeMethod: "submit_challenge", resolveChallengeMethod: "resolve_challenge_with_genlayer",
  submitAppealMethod: "submit_appeal", resolveAppealMethod: "resolve_appeal_with_genlayer", archiveMethod: "archive_claim",
  variant: "docket", kicker: "Policy interpretation review", title: "Clause appeal docket",
  intro: "Read the cited rule beside its ruling, file a source-backed objection, and preserve a complete challenge and appeal trail before archival.",
}));
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const hostOf = (u) => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch (_) { return u; } };

// Demo records are clearly labelled and never claim to be on-chain.
const DEMO_QUERIES = [
  { id: 0, asker: "0xDEMO...", question: "May I use this software for commercial purposes?", policy_url: "https://example.com/mit", status: 1, passage: "Permission is hereby granted, free of charge, to any person...", rationale: "The licence grants unrestricted use including commercial.", archived: 0 },
  { id: 1, asker: "0xDEMO...", question: "Is it permitted to remove the copyright notice?", policy_url: "https://example.com/mit", status: 2, passage: "The above copyright notice...shall be included in all copies.", rationale: "The notice must be retained.", archived: 0 },
];

let account = null, queries = [], stats = null;

function toast(msg, kind = "", title = "clause") {
  const el = document.createElement("div"); el.className = "toast " + kind; el.setAttribute("role", kind === "err" ? "alert" : "status");
  el.innerHTML = `<span class="tt">${title}</span>`; el.appendChild(document.createTextNode(msg));
  $("log").appendChild(el); setTimeout(() => el.remove(), kind === "err" ? 14000 : 5000);
}

$("netLabel").textContent = NETWORK;

async function refreshWallet() {
  if (DEMO) { $("walletslot").innerHTML = `<span class="mono" style="font-size:12px;color:var(--muted)">demo mode</span>`; return; }
  try { account = await activeAccount(); } catch (_) { account = null; }
  const slot = $("walletslot");
  if (account) slot.innerHTML = `<span class="mono" style="font-size:12px;color:var(--muted)">${short(account)}</span>`;
  else { slot.innerHTML = `<button class="btn outline" id="connectBtn">Connect wallet</button>`; $("connectBtn").onclick = doConnect; }
}
async function doConnect() { try { account = await connectWallet(); toast("Wallet connected on " + NETWORK + ".", "ok"); await refreshWallet(); route(); } catch (e) { toast(fmtErr(e), "err"); } }
async function ensureWallet() { if (!account) account = await connectWallet(); await refreshWallet(); }

async function load() {
  if (DEMO) { queries = DEMO_QUERIES.slice(); stats = tally(queries); return; }
  const [statsRaw, countRaw] = await Promise.all([read("get_stats"), read("get_query_count")]);
  stats = statsRaw;
  const n = Number(countRaw);
  const records = await Promise.all(Array.from({ length: n }, (_, i) => read("get_query", [i]).then((q) => ({ id: i, ...q }))));
  const out = records.filter((q) => Number(q.archived) === 0);
  queries = out;
}
function tally(qs) { const s = { total: qs.length, permitted: 0, prohibited: 0, unclear: 0, pending: 0 }; qs.forEach((q) => { s[["pending", "permitted", "prohibited", "unclear"][q.status]]++; }); return s; }

/* ----------------------------- router ----------------------------- */
function setNav(r) { document.querySelectorAll(".mnl").forEach((a) => a.classList.toggle("on", a.dataset.route === r)); }
function focusMain() { try { app().focus({ preventScroll: true }); } catch (_) {} }
function route() {
  const h = location.hash || "#/";
  window.scrollTo(0, 0);
  if (h.startsWith("#/method")) { setNav("method"); renderMethod(); }
  else if (h.startsWith("#/file")) { setNav(""); renderFile(); }
  else if (h.startsWith("#/ruling/")) { setNav("docket"); renderRecord(Number(h.split("/")[2])); }
  else { setNav("docket"); renderDocket(); }
  focusMain();
}

function demoBanner() {
  return DEMO ? `<div class="banner demo" role="note"><i class="ph-bold ph-warning-octagon"></i><div><b>Demo mode.</b> No contract is configured, so these are sample records - not real on-chain rulings.</div></div>` : "";
}

/* ----------------------------- docket ----------------------------- */
function renderDocket() {
  const s = stats || { total: 0, permitted: 0, prohibited: 0, unclear: 0, pending: 0 };
  const rows = queries.length
    ? queries.slice().reverse().map((q) => `
        <li class="row" tabindex="0" role="link" data-q="${q.id}" aria-label="Ruling ${q.id + 1}: ${esc(q.question)}, ${VERDICT[q.status]}">
          <span class="row-no">${String(q.id + 1).padStart(2, "0")}</span>
          <span><span class="row-q">${esc(q.question)}</span><span class="row-src">${esc(hostOf(q.policy_url))}</span></span>
          <span class="row-verdict"><span class="stamp ${STAMP[q.status]}">${VERDICT[q.status]}</span></span>
        </li>`).join("")
    : `<li class="empty">No queries on the docket yet. <a href="#/file">File the first one&nbsp;&rarr;</a></li>`;

  app().innerHTML = `<div class="sheet">
    ${demoBanner()}
    <p class="kicker">The Docket</p>
    <h1 class="doc-title">Rulings, grounded in the policy itself.</h1>
    <p class="doc-lead">Ask whether something is allowed under a specific written rule. A validator set reads the document and records a verdict &mdash; with the exact passage it rests on.</p>

    <section class="intake" aria-labelledby="intakeH">
      <span class="intake-tab">New matter</span>
      <h2 id="intakeH">Have a policy question?</h2>
      <p>Link the governing document and ask in plain language. You&rsquo;ll get Permitted, Prohibited, or Unclear.</p>
      <div class="intake-actions"><a href="#/file" class="btn ox">File a query</a><a href="#/method" class="btn ghost">How it&rsquo;s decided</a></div>
    </section>

    <div class="tally" aria-label="Docket tally">
      <span><b>${s.total}</b> on the docket</span>
      <span class="permit"><b>${s.permitted}</b> permitted</span>
      <span class="prohibit"><b>${s.prohibited}</b> prohibited</span>
      <span class="unclear"><b>${s.unclear}</b> unclear</span>
      <span><b>${s.pending}</b> pending</span>
    </div>
    <ul class="docket">${rows}</ul>
  </div>`;

  app().querySelectorAll("[data-q]").forEach((r) => {
    const go = () => { location.hash = "#/ruling/" + r.dataset.q; };
    r.addEventListener("click", go);
    r.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
  });
}

/* ----------------------------- record ----------------------------- */
function renderRecord(id) {
  const q = queries.find((x) => x.id === id);
  if (!q) { app().innerHTML = `<div class="sheet"><button class="back" onclick="location.hash='#/'">&larr; The Docket</button><p class="empty">No such ruling on the docket.</p></div>`; return; }
  const sc = STAMP[q.status];
  const ruled = q.status !== 0;
  const passage = ruled && q.passage
    ? `<div class="rec-section"><div class="rec-h">Governing passage</div><blockquote class="passage">&ldquo;${esc(q.passage)}&rdquo;</blockquote></div>` : "";
  const rationale = ruled && q.rationale
    ? `<div class="rec-section"><div class="rec-h">Reasoning</div><p class="rationale">${esc(q.rationale)}</p></div>` : "";
  const pendingBlock = !ruled ? `
    <div class="rec-section">
      <p class="rationale">This query has been filed but not yet ruled. Request a ruling and a validator set will read the policy and decide.</p>
      <div class="rec-actions">${DEMO ? "" : `<button class="btn ox lg" id="ruleBtn">Request a ruling</button>`}</div>
      <div class="processing" id="proc" hidden><span class="spin"></span> Validators are reading the policy and forming consensus&hellip; this can take a moment.</div>
    </div>` : "";

  app().innerHTML = `<div class="sheet">
    <button class="back" id="backBtn">&larr; The Docket</button>
    <article class="record">
      <div>
        <p class="kicker">Ruling No. ${String(q.id + 1).padStart(2, "0")}</p>
        <h1 class="rec-q">${esc(q.question)}</h1>
        ${passage}${rationale}${pendingBlock}
      </div>
      <aside class="rec-aside" aria-label="Record details">
        <div class="stamp-wrap"><span class="stamp ${sc} stamp-lg">${VERDICT[q.status]}</span></div>
        <div class="kv">
          <div><div class="k">Policy source</div><div class="v"><a href="${esc(q.policy_url)}" target="_blank" rel="noopener">${esc(hostOf(q.policy_url))} &#8599;</a></div></div>
          <div><div class="k">Filed by</div><div class="v mono">${esc(short(q.asker))}</div></div>
          <div><div class="k">Record</div><div class="v mono">#${q.id} <button class="copy" id="copyId">copy</button></div></div>
        </div>
      </aside>
    </article>
  </div>`;

  $("backBtn").onclick = () => { location.hash = "#/"; };
  $("copyId").onclick = () => { navigator.clipboard?.writeText(String(q.id)); toast("Record id copied.", "ok"); };
  if ($("ruleBtn")) $("ruleBtn").onclick = () => doRule(q.id);
}

/* ----------------------------- file ----------------------------- */
function renderFile() {
  app().innerHTML = `<div class="sheet"><div class="form">
    <button class="back" id="backBtn">&larr; The Docket</button>
    <p class="kicker">File a query</p>
    <h1 class="doc-title">State the matter.</h1>
    <p class="doc-lead">Ask one clear question and link the policy that governs it. The cited document is the only thing the validators may use.</p>
    ${demoBanner()}
    <form id="fileForm" novalidate>
      <div class="field">
        <label for="fQ">Your question <span class="count" id="qCount">0 / 240</span></label>
        <textarea id="fQ" maxlength="240" aria-describedby="qErr" placeholder="e.g. May I use this software for commercial purposes?"></textarea>
        <div class="err" id="qErr" hidden></div>
      </div>
      <div class="field">
        <label for="fU">Policy document URL</label>
        <input id="fU" type="url" maxlength="300" aria-describedby="uErr" placeholder="https://... the governing terms, licence or policy" />
        <div class="err" id="uErr" hidden></div>
      </div>
      <button class="btn ink lg" type="submit" id="fileBtn">File for ruling</button>
    </form>
  </div></div>`;
  $("backBtn").onclick = () => { location.hash = "#/"; };
  const q = $("fQ"); q.addEventListener("input", () => { $("qCount").textContent = `${q.value.length} / 240`; });
  $("fileForm").addEventListener("submit", onFile);
}

function fieldErr(id, errId, msg) { const f = $(id), e = $(errId); if (msg) { f.setAttribute("aria-invalid", "true"); e.textContent = msg; e.hidden = false; } else { f.removeAttribute("aria-invalid"); e.hidden = true; } }

async function onFile(ev) {
  ev.preventDefault();
  const q = $("fQ").value.trim(), u = $("fU").value.trim();
  let bad = false;
  if (!q) { fieldErr("fQ", "qErr", "A question is required."); bad = true; } else if (q.length > 240) { fieldErr("fQ", "qErr", "Keep it under 240 characters."); bad = true; } else fieldErr("fQ", "qErr", "");
  if (!u) { fieldErr("fU", "uErr", "A policy URL is required."); bad = true; }
  else if (!/^https?:\/\//.test(u)) { fieldErr("fU", "uErr", "Must start with http:// or https://"); bad = true; }
  else if (u.length > 300) { fieldErr("fU", "uErr", "URL is too long (max 300)."); bad = true; } else fieldErr("fU", "uErr", "");
  if (bad) return;
  if (DEMO) { toast("Demo mode: filing is disabled.", "err"); return; }

  const btn = $("fileBtn"); btn.disabled = true; btn.innerHTML = '<span class="spin"></span> filing';
  try {
    await ensureWallet();
    await write(CONTRACT, "file_query", [q, u]);
    toast("Filed on the docket.", "ok");
    await load();
    const newId = Math.max(...queries.map((x) => x.id));
    location.hash = "#/ruling/" + newId;
  } catch (e) { toast(fmtErr(e), "err"); btn.disabled = false; btn.textContent = "File for ruling"; }
}

/* ----------------------------- actions ----------------------------- */
async function doRule(id) {
  if (!confirm("Request a ruling? A validator set will read the cited policy and decide. This calls a real LLM consensus and cannot be undone.")) return;
  const btn = $("ruleBtn"), proc = $("proc");
  if (btn) btn.disabled = true; if (proc) proc.hidden = false;
  try {
    await ensureWallet();
    await write(CONTRACT, "rule", [id]);
    toast("Ruling recorded on-chain.", "ok");
    await load(); renderRecord(id);
  } catch (e) {
    // Consensus failure / undetermined leaves the query PENDING (state unchanged).
    toast(fmtErr(e) + " - the query stays pending; you can retry.", "err");
    if (btn) btn.disabled = false; if (proc) proc.hidden = true;
  }
}

/* ----------------------------- method ----------------------------- */
function renderMethod() {
  app().innerHTML = `<div class="sheet">
    <p class="kicker">How it&rsquo;s decided</p>
    <h1 class="doc-title">Read the policy. Agree. Record it.</h1>
    <p class="doc-lead">Clause is a GenLayer Intelligent Contract. Interpreting a rule against a real document needs reading external text <em>and</em> protection from any one party spinning the result. Here is the process.</p>
    <div class="steps">
      <div class="mstep"><span class="n"></span><div><h3>You file the matter</h3><p>A question and the URL of the governing policy are stored on-chain. Inputs are validated and length-limited; you can&rsquo;t file the same matter twice.</p></div></div>
      <div class="mstep"><span class="n"></span><div><h3>Validators read the same source</h3><p>When a ruling is requested, the contract fetches the policy. A leader proposes a verdict; every validator independently reads the document and derives its own verdict.</p></div></div>
      <div class="mstep"><span class="n"></span><div><h3>Consensus on the substance</h3><p>The ruling is accepted only if the validators agree on the <em>outcome</em> &mdash; not merely the formatting. If they can&rsquo;t agree, nothing is recorded and the matter stays pending.</p></div></div>
      <div class="mstep"><span class="n"></span><div><h3>Grounded &amp; permanent</h3><p>The verdict is stored with the single governing passage it rests on &mdash; Permitted, Prohibited, or Unclear &mdash; so every ruling is citable and tamper-proof.</p></div></div>
    </div>
    <div class="banner" role="note" style="margin-top:26px"><i class="ph-bold ph-info"></i><div>The contract reads only the document you cite and answers strictly from it. If the source can&rsquo;t be read or doesn&rsquo;t address the question, the verdict is <b>Unclear</b> rather than a guess.</div></div>
    <div class="rec-actions" style="margin-top:22px"><a href="#/file" class="btn ox lg">File a query</a></div>
  </div>`;
  $("backBtn") && ($("backBtn").onclick = () => location.hash = "#/");
}

/* ----------------------------- boot ----------------------------- */
window.addEventListener("hashchange", route);
if (!DEMO && window.ethereum) window.ethereum.on?.("accountsChanged", refreshWallet);

(async () => {
  await refreshWallet();
  try { await load(); }
  catch (e) {
    app().innerHTML = `<div class="sheet"><div class="banner warn" role="alert"><i class="ph-bold ph-warning"></i><div><b>Couldn&rsquo;t reach the contract.</b> ${esc(fmtErr(e))} <button class="copy" onclick="location.reload()">retry</button></div></div></div>`;
    return;
  }
  route();
})();
