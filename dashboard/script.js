/* ═══════════════════════════════════════════════════════════════════════════
   CX Audit Platform — script.js
   Handles: dashboard, run audit forms, issues log, persona modal.
   Works in two modes:
     API_MODE  — served from Flask (python server.py) — uses /api/ endpoints
     FILE_MODE — opened directly as a file — loads ../reports/ directly
   ═══════════════════════════════════════════════════════════════════════════ */
'use strict';

/* ── Mode detection ────────────────────────────────────────────────────────── */
const API_MODE = window.location.protocol !== 'file:';
const BASE     = API_MODE ? '' : '..';

/* ── Persistent delete (FILE_MODE) ─────────────────────────────────────────── */
// In file:// mode there is no server to call, so deletions are stored in
// localStorage and filtered out on every load.  The key set survives refreshes.
const _LS_DELETED = 'cx-audit-deleted-runs';

function _getDeletedKeys() {
  try { return new Set(JSON.parse(localStorage.getItem(_LS_DELETED) || '[]')); }
  catch { return new Set(); }
}
function _addDeletedKey(key) {
  const s = _getDeletedKeys();
  s.add(key);
  try { localStorage.setItem(_LS_DELETED, JSON.stringify([...s])); } catch {}
}
// Build the same key that personaRunKey() produces, from deletePersonaRun args
function _makeRunKey(slug, auditType, runId) {
  return runId ? `${runId}__${slug}__${auditType}` : `${slug}__${auditType}`;
}

/* ── Config ────────────────────────────────────────────────────────────────── */
const CFG = {
  reportsBase:     `${BASE}/reports`,
  screenshotsBase: `${BASE}/screenshots`,
  videosBase:      `${BASE}/videos`,
  logsBase:        `${BASE}/logs`,
  api:             '/api',
};

/* ── App state ─────────────────────────────────────────────────────────────── */
const STATE = {
  allPersonas:      [],
  filteredPersonas: [],
  activeFilter:     'all',
  activeSort:       'default',
  searchQuery:      '',
  activeProducts:   new Set(),    // empty = all; populated = filter to those products
  activePersona:    null,
  ssIndex:          0,
  lbIndex:          0,
  lbImages:         [],
  activePage:       'dashboard',
  activeRunId:      null,
  pollTimer:        null,
  appRunId:         null,
  webPersonaPath:   '',
  webPersonaOptions: [],
  appPersonaPath:   '',
  appPersonaOptions: [],
};

/* ── Tiny DOM helpers ──────────────────────────────────────────────────────── */
const qs  = (sel, ctx = document) => ctx.querySelector(sel);
const qsa = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* ══════════════════════════════════════════════════════════════════════════════
   DATA LAYER
   ══════════════════════════════════════════════════════════════════════════════ */

async function fetchText(url) {
  try {
    const r = await fetch(url, { cache: 'no-store' });
    if (!r.ok) return null;
    return await r.text();
  } catch { return null; }
}

async function fetchJSON(url) {
  try {
    const r = await fetch(url, { cache: 'no-store' });
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}

function toSlug(name) {
  return name.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').trim();
}

function screenshotRel(absPath, base) {
  if (!absPath) return null;
  const norm = absPath.replace(/\\/g, '/');
  // Already a relative path — serve directly under reportsBase
  if (!norm.match(/^([A-Za-z]:\/|\/)/)) {
    return `${CFG.reportsBase}/${norm}`;
  }
  // Absolute OS path — find the "reports/" anchor and keep everything after it
  // e.g. "C:/…/reports/slug-name/steps/step_003.png" → "slug-name/steps/step_003.png"
  const reportsIdx = norm.toLowerCase().lastIndexOf('/reports/');
  if (reportsIdx !== -1) {
    return `${CFG.reportsBase}/${norm.slice(reportsIdx + '/reports/'.length)}`;
  }
  // Find the "screenshots/" anchor and preserve the subdirectory structure
  // e.g. "C:/…/screenshots/persona-slug/step_000.png" → "persona-slug/step_000.png"
  // Use the supplied base (archived _screenshots dir for archived runs) so an
  // archived tile shows its OWN screenshots, not the overwritten live ones.
  const ssIdx = norm.toLowerCase().lastIndexOf('/screenshots/');
  if (ssIdx !== -1) {
    return `${base || CFG.screenshotsBase}/${norm.slice(ssIdx + '/screenshots/'.length)}`;
  }
  // Fallback: filename only (legacy flat paths)
  const parts = norm.split('/');
  return `${base || CFG.screenshotsBase}/${parts[parts.length - 1]}`;
}

function artifactRel(absPath, base) {
  if (!absPath) return null;
  const parts = absPath.replace(/\\/g, '/').split('/');
  return `${base}/${parts[parts.length - 1]}`;
}

function formatDateTime(value) {
  if (!value) return 'Run time unavailable';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function parseMasterReport(md) {
  if (!md) return null;
  const meta = {};

  // Metadata table. Current reports use a HORIZONTAL table (header row +
  // value row):
  //   | **Target** | **Date** | **Model** | **Run** |
  //   |---|---|---|---|
  //   | https://…  | 2026-… UTC | gpt-4.1 | 203e808f |
  // Older reports used a VERTICAL 2-column table: | **Target** | value |.
  // The old regex grabbed the *next header cell* on a horizontal table
  // (Target→**Date**, Date→**Model**, …), which is what surfaced the literal
  // "**Date** • **Model** • **Run**" in the header. Parse by column instead.
  const mdLines   = md.split('\n');
  const headerRow = mdLines.findIndex(l => /\|\s*\*\*Target\*\*\s*\|/.test(l));
  if (headerRow !== -1) {
    const headerCells = mdLines[headerRow]
      .split('|').map(c => c.replace(/\*\*/g, '').trim().toLowerCase()).filter(Boolean);
    const isHorizontal = headerCells.includes('date') || headerCells.includes('model');
    if (isHorizontal) {
      // First non-separator row after the header carries the values.
      for (let i = headerRow + 1; i < mdLines.length; i++) {
        if (!mdLines[i].trim().startsWith('|')) break;
        const cells = mdLines[i].split('|').map(c => c.trim()).filter(Boolean);
        if (!cells.length || cells.every(c => /^-+$/.test(c))) continue;   // skip separator
        const col = {};
        headerCells.forEach((h, idx) => { if (cells[idx] != null) col[h] = cells[idx]; });
        if (col['target']) meta.target = col['target'];
        if (col['date'])   meta.date   = col['date'];
        if (col['model'])  meta.model  = col['model'];
        break;
      }
    } else {
      const tM = md.match(/\|\s*\*\*Target\*\*\s*\|\s*([^|\n]+?)\s*\|/);
      const dM = md.match(/\|\s*\*\*Date\*\*\s*\|\s*([^|\n]+?)\s*\|/);
      const mM = md.match(/\|\s*\*\*Model\*\*\s*\|\s*([^|\n]+?)\s*\|/);
      if (tM) meta.target = tM[1].trim();
      if (dM) meta.date   = dM[1].trim();
      if (mM) meta.model  = mM[1].trim();
    }
  }

  // Scorecard table has variable columns; parse by header names, not position.
  // The actual report header is: | Persona | Outcome | Steps | CX | Design | Content |
  // (section "## Scorecard", with or without an emoji).
  const scorecardMatch = md.match(/##\s*(?:📊\s*)?Scorecard[\s\S]*?(?=\n##\s|$)/);
  const personas = [];
  if (scorecardMatch) {
    const block = scorecardMatch[0];
    const tableLines = block.split('\n').filter(l => l.trim().startsWith('|'));
    if (tableLines.length >= 2) {
      // Parse header row → column index map
      const headerCells = tableLines[0].split('|').map(c => c.trim()).filter(Boolean);
      const colIdx = {};
      headerCells.forEach((h, i) => { colIdx[h.toLowerCase()] = i; });
      // CX score lives in the column literally headed "CX" (older reports used
      // "CX Score"). Resolve once, tolerating both.
      const cxCol = colIdx['cx'] ?? colIdx['cx score'] ?? colIdx['score'] ?? -1;

      // Parse data rows (skip separator row)
      for (let i = 1; i < tableLines.length; i++) {
        const cells = tableLines[i].split('|').map(c => c.trim()).filter(Boolean);
        if (!cells.length) continue;
        // Skip separator rows (all dashes)
        if (cells.every(c => /^-+$/.test(c))) continue;

        const name = cells[colIdx['persona'] ?? 0] || '';
        if (!name || name === 'Persona') continue;

        const outcome    = cells[colIdx['outcome']   ?? 1] || '';
        const steps      = parseInt(cells[colIdx['steps']    ?? 2]) || 0;
        const cxRaw      = cxCol >= 0 ? (cells[cxCol] || '') : '';
        const score      = parseFloat(cxRaw.match(/([\d.]+)/)?.[1] ?? '0');

        personas.push({
          name,
          outcome: outcome.replace(/[🟢🟡🟠🔴✅❌⚠️🎯⬆️🚪⏱🔁🔒📋🔍💥🛑]/gu, '').trim(),
          score,
          steps,
          topFriction: '',   // master scorecard has no friction column; use journey_log
          slug: toSlug(name),
        });
      }
    }
  }
  return { ...meta, personas };
}

/* ── cx_audit field-name normalisation (handles old + new journey_log formats) ─ */

function _normCxDims(arr) {
  return (arr || []).map(d => ({ ...d, name: d.name || d.dimension_name || '' }));
}

// Backend emits severities from the enum ["critical","major","minor"]
// (evaluation/cx_evaluator.py), but the dashboard buckets friction by
// high/medium/low. Map here — the single choke point — so the tile summary,
// overview "Critical Issues", and friction list all agree, and already-saved
// journey_log.json files render without re-running the audit.
const _SEVERITY_MAP = { critical: 'high', major: 'medium', minor: 'low' };

function _normCxFriction(arr) {
  return (arr || []).map(f => ({
    severity:    _SEVERITY_MAP[f.severity] || f.severity || 'low',
    location:    f.location    || f.dimension      || '',
    description: f.description || '',
    impact:      f.impact      || f.recommendation || '',
  }));
}

function _normCxStepEvals(arr) {
  return (arr || []).map(se => ({
    ...se,
    dimension_scores: (se.dimension_scores || []).map(d => ({
      ...d,
      dimension:   d.dimension   || d.dimension_name || '',
      observation: d.observation || d.rationale      || '',
    })),
  }));
}

/* ── design_audit field-name normalisation ──────────────────────────────────── */

function _normDesignDims(arr) {
  return (arr || []).map(d => ({
    ...d,
    name:        d.name        || d.dimension_name || '',
    observation: d.observation || d.rationale      || '',
  }));
}

function _normDesignIssues(arr) {
  return (arr || []).map(i => ({
    severity:    i.severity    || 'minor',
    location:    i.location    || i.dimension      || '',
    description: i.description || '',
    impact:      i.impact      || i.recommendation || '',
  }));
}

async function loadPersonaData(slug, forceBase, meta = {}) {
  setLoadingStatus(`Loading ${slug}…`);
  // Try the supplied base first, then web path, then mobile path
  const bases = forceBase
    ? [forceBase]
    : [`${CFG.reportsBase}/${slug}`, `${CFG.reportsBase}/mobile/${slug}`];

  let journeyLog = null;
  let reportMd   = null;
  let usedBase   = null;

  for (const base of bases) {
    const jl = await fetchJSON(`${base}/journey_log.json`);
    if (jl) { journeyLog = jl; usedBase = base; reportMd = await fetchText(`${base}/report.md`); break; }
  }
  if (!journeyLog) return null;

  const journey      = journeyLog.journey      || {};
  const cxAudit      = journeyLog.cx_audit     || {};
  const designAudit  = journeyLog.design_audit || {};
  // Maps snake_case objective_scores keys → human-readable dimension names
  const objectiveScoreKeys = journeyLog.objective_score_keys || {};

  // Determine screenshots base: mobile audits store shots under screenshots/mobile/
  const isMobile = usedBase && usedBase.includes('/mobile/');
  const ssBase   = meta.screenshotsBase || (isMobile ? `${CFG.screenshotsBase}/mobile` : CFG.screenshotsBase);
  const videoBase = meta.videosBase || CFG.videosBase;

  const steps = (journey.steps || []).map(s => ({
    ...s, screenshotRel: screenshotRel(s.screenshot, ssBase),
  }));
  const screenshots = steps
    .filter(s => s.screenshotRel)
    .map(s => ({
      src: s.screenshotRel,
      caption: `Step ${s.step_number + 1} — ${(s.action || '').toUpperCase()} ${s.target || s.url || ''}`,
      step: s.step_number,
    }));
  // Final screenshot — resolved from the real path the agent recorded
  // (screenshots/{slug}/final.png). Only pushed when it actually exists.
  const finalRel = screenshotRel(journey.final_screenshot, ssBase);
  if (finalRel) {
    screenshots.push({ src: finalRel, caption: 'Final state', step: 9999 });
  }

  return {
    slug:           meta.slugKey || slug,
    sourceSlug:     slug,
    runId:          meta.runId || journey.run_id || '',
    archived:       !!meta.archived,
    isMobile:       isMobile,
    name:           journey.persona         || cxAudit.persona_name || slug,
    intent:         journey.intent          || '',
    personaData:    journey.persona_data    || {},
    terminalReason: journey.terminal_reason || 'unknown',
    isTechnicalFailure: !!journey.is_technical_failure,
    completed:      !!journey.completed,
    createdAt:      meta.createdAt || journey.started_at || journey.generated_at || cxAudit.generated_at || '',
    stepCount:      journey.step_count      || steps.length,
    failureCount:   journey.failure_count   || 0,
    visitedUrls:    journey.visited_urls    || [],
    failedActions:  journey.failed_actions  || [],
    videoRel:       artifactRel(journey.video_path, videoBase),
    cxObservations: journey.cx_observations || [],
    tokenUsage:  journey.token_usage || { input_tokens: 0, output_tokens: 0 },
    costInr:     typeof journey.cost_inr === 'number' ? journey.cost_inr : null,
    model:       journey.model || '',
    googleEntry: journey.google_entry || null,
    steps, screenshots, reportMd,
    // cx_audit: read new-format fields, fall back to old-format names for existing logs
    overallScore:    parseFloat(cxAudit.overall_score ?? cxAudit.overall_cx_score) || 0,
    journeyVerdict:  cxAudit.journey_verdict  || '',
    tldr:            cxAudit.tldr            || '',
    keyTakeaways:    cxAudit.key_takeaways   || [],
    dimensions:      _normCxDims(cxAudit.dimensions || cxAudit.dimension_scores),
    frictionPoints:  _normCxFriction(cxAudit.friction_points || cxAudit.issues),
    positiveMoments: cxAudit.positive_moments || cxAudit.delight_points || [],
    recommendations: cxAudit.recommendations  || [],
    stepEvaluations: _normCxStepEvals(cxAudit.step_evaluations),
    // Design audit fields
    designAuditScore:   parseFloat(designAudit.overall_score ?? designAudit.overall_design_score) || 0,
    designVerdict:      designAudit.design_verdict   || '',
    designTldr:         designAudit.design_tldr      || '',
    designKeyFindings:  designAudit.key_findings     || [],
    designDimensions:   _normDesignDims(designAudit.dimensions || designAudit.dimension_scores),
    designIssues:       _normDesignIssues(designAudit.issues   || designAudit.critical_issues),
    designPositives:    designAudit.positives        || designAudit.positive_findings || [],
    designBrandAlignment:   designAudit.brand_alignment         || '',
    designWcagLevel:        designAudit.wcag_compliance_level   || '',
    designDsAdherence:      designAudit.ds_adherence_level      || '',
    designStepEvaluations:  designAudit.step_evaluations        || [],
    evalType:           journeyLog.eval_type         || (cxAudit.overall_score ? 'cx' : ''),
    evalTypesRun:       journeyLog.eval_types_run    || [],
    // Content analysis
    contentAnalysis:    journeyLog.content_analysis  || null,
    // Accessibility audit
    accessibilityAudit: journeyLog.accessibility_audit || null,
    // Login wall data
    loginWallEncounters: journey.login_wall_encounters || 0,
    loginWallDecisions:  journey.login_wall_decisions  || [],
  };
}

/* ══════════════════════════════════════════════════════════════════════════════
   PAGE NAVIGATION
   ══════════════════════════════════════════════════════════════════════════════ */

function showPage(pageId) {
  qsa('.page').forEach(p => p.classList.remove('page--active'));
  qsa('.nav-tab').forEach(t => t.classList.remove('nav-tab--active'));

  const page = qs(`#page-${pageId}`);
  const tab  = qs(`.nav-tab[data-page="${pageId}"]`);
  if (page) page.classList.add('page--active');
  if (tab)  tab.classList.add('nav-tab--active');

  STATE.activePage = pageId;

  if (pageId === 'new-audit') loadPersonaFiles('#f-personas-select').then(() => parsePersonaSource('web'));
  if (pageId === 'issues')    loadIssues();
}

function bindNavEvents() {
  qsa('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => showPage(tab.dataset.page));
  });

  qs('#new-audit-btn').addEventListener('click', () => showPage('new-audit'));
}

/* ══════════════════════════════════════════════════════════════════════════════
   INIT — boot sequence
   ══════════════════════════════════════════════════════════════════════════════ */

async function init() {
  setLoadingStatus('Fetching audit data…');

  // Load master report for header metadata
  const masterMd   = await fetchText(`${CFG.reportsBase}/master_report.md`);
  const masterData = parseMasterReport(masterMd);

  if (masterData) {
    const tEl = qs('#header-target');
    const mEl = qs('#header-model');
    if (masterData.target) tEl.textContent = masterData.target.replace(/https?:\/\//, '');
    if (masterData.model)  mEl.textContent = masterData.model;
  }

  // Discover slugs — web manifest
  let slugs = masterData?.personas?.map(p => p.slug).filter(Boolean) || [];
  const manifest = await fetchJSON(`${CFG.reportsBase}/manifest.json`);
  if (manifest?.slugs) {
    const existing = new Set(slugs);
    for (const s of manifest.slugs) if (!existing.has(s)) slugs.push(s);
  }

  // Also pick up mobile manifest (reports/mobile/manifest.json)
  const mobileManifest = await fetchJSON(`${CFG.reportsBase}/mobile/manifest.json`);
  const mobileSlugs = mobileManifest?.slugs || [];

  // Load web personas + mobile personas in parallel (mobile tagged with base)
  const webResults    = await Promise.all(slugs.map(s => loadPersonaData(s, null, {
    runId: manifest?.run_id || '',
  })));
  const mobileResults = await Promise.all(
    mobileSlugs.map(s => loadPersonaData(s, `${CFG.reportsBase}/mobile/${s}`, {
      runId: mobileManifest?.run_id || '',
    }))
  );

  let archivedResults = [];
  if (API_MODE) {
    const runsData = await fetchJSON(`${CFG.api}/runs`);
    const runs = runsData?.runs || [];
    const archiveJobs = [];
    for (const run of runs) {
      if (!run.archived_reports_path) continue;
      const archivedSlugs = run.archived_slugs || run.manifest_slugs || [];
      for (const s of archivedSlugs) {
        archiveJobs.push(loadPersonaData(
          s,
          `${CFG.reportsBase}/run_archive/${run.id}/${s}`,
          {
            runId: run.id,
            createdAt: run.created_at,
            archived: true,
            slugKey: `${run.id}__${s}`,
            screenshotsBase: run.archived_screenshots_path ? `${BASE}/${run.archived_screenshots_path}` : undefined,
            videosBase: run.archived_videos_path ? `${BASE}/${run.archived_videos_path}` : undefined,
          }
        ));
      }
    }
    archivedResults = await Promise.all(archiveJobs);
  } else {
    // FILE_MODE: enumerate archived runs via archive_index.json written by archive_run()
    const archiveIndex = await fetchJSON(`${CFG.reportsBase}/run_archive/archive_index.json`);
    if (Array.isArray(archiveIndex)) {
      const archiveJobs = [];
      for (const run of archiveIndex) {
        if (!run.run_id || !Array.isArray(run.slugs)) continue;
        for (const s of run.slugs) {
          archiveJobs.push(loadPersonaData(
            s,
            `${CFG.reportsBase}/run_archive/${run.run_id}/${s}`,
            {
              runId: run.run_id,
              createdAt: run.generated_at,
              archived: true,
              slugKey: `${run.run_id}__${s}`,
              // Point at this run's archived media so a later same-persona run
              // can't overwrite what this tile shows.
              screenshotsBase: `${CFG.reportsBase}/run_archive/${run.run_id}/_screenshots`,
              videosBase: `${CFG.reportsBase}/run_archive/${run.run_id}/_videos`,
            }
          ));
        }
      }
      archivedResults = (await Promise.all(archiveJobs)).filter(Boolean);
    }
  }

  // Merge by run+persona so repeated runs of the same persona remain visible.
  const bySlug = new Map();
  for (const p of [...webResults, ...mobileResults, ...archivedResults]) {
    if (p) bySlug.set(personaRunKey(p), p);
  }
  STATE.allPersonas = [...bySlug.values()];

  // Remove any personas the user has deleted (FILE_MODE persists deletions
  // in localStorage; API_MODE deletions are already gone from the server).
  const _deleted = _getDeletedKeys();
  if (_deleted.size > 0) {
    STATE.allPersonas = STATE.allPersonas.filter(p => !_deleted.has(personaRunKey(p)));
  }

  if (STATE.allPersonas.length === 0) {
    showToast('No audit data found — run an audit first or start one from New Audit tab.', 'info');
  }

  updateStats();
  renderProductDropdown();
  applyFilterSort();
  updateRunBadge();
  bindNavEvents();
  bindDashboardEvents();
  bindModalEvents();
  bindAuditFormEvents();
  bindIssuesEvents();
  hideLoading();

  if (STATE.allPersonas.length > 0) {
    showToast(`Loaded ${STATE.allPersonas.length} persona audit${STATE.allPersonas.length > 1 ? 's' : ''}`, 'success');
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   STATS BAR
   ══════════════════════════════════════════════════════════════════════════════ */

function updateStats(personas = STATE.allPersonas) {
  const ps = personas || [];
  const total       = ps.length;
  const avgScore    = total ? (ps.reduce((a, p) => a + p.overallScore, 0) / total) : 0;
  const highFriction= ps.reduce((a, p) => a + p.frictionPoints.filter(f => f.severity === 'high').length, 0);

  qs('#stat-total').textContent     = total;
  qs('#stat-avg-score').textContent = avgScore.toFixed(1) + '/10';
  qs('#stat-friction').textContent  = highFriction;

  const fill = qs('#stat-score-fill');
  if (fill) {
    fill.style.width      = `${(avgScore / 10) * 100}%`;
    fill.style.background = scoreGradient(avgScore);
  }

  // Design score card — show only when at least one persona has design audit data
  const designPs = ps.filter(p => p.designAuditScore > 0);
  const designCard = qs('#stat-card-design');
  if (designCard) {
    if (designPs.length > 0) {
      const avgDesign = designPs.reduce((a, p) => a + p.designAuditScore, 0) / designPs.length;
      qs('#stat-avg-design-score').textContent = avgDesign.toFixed(1) + '/10';
      const df = qs('#stat-design-score-fill');
      if (df) { df.style.width = `${(avgDesign / 10) * 100}%`; df.style.background = scoreGradient(avgDesign); }
      designCard.style.display = '';
    } else {
      designCard.style.display = 'none';
    }
  }

  updateExecutiveSummary(ps);
}

function updateExecutiveSummary(personas) {
  const el = qs('#executive-summary-body');
  if (!el) return;
  const ps = personas || [];
  if (!ps.length) {
    el.textContent = 'No persona runs match the current filters.';
    return;
  }
  const avg = ps.reduce((a, p) => a + p.overallScore, 0) / ps.length;
  const products = [...new Set(ps.map(p => p.personaData?.product || 'General'))];
  const highFriction = ps.flatMap(p => p.frictionPoints || []).filter(f => f.severity === 'high').length;
  const weakest = [...ps].sort((a, b) => a.overallScore - b.overallScore)[0];
  const productText = products.length === 1 ? products[0] : `${products.length} product groups`;
  el.textContent = `${ps.length} persona run(s) across ${productText}: average CX score is ${avg.toFixed(1)}/10, with ${highFriction} high-severity friction point(s). Lowest scoring journey: ${weakest?.name || 'n/a'} (${(weakest?.overallScore || 0).toFixed(1)}/10).`;
}

function updateRunBadge() {
  // Badge removed from UI — no-op
}

/* ══════════════════════════════════════════════════════════════════════════════
   FILTER + SORT + CARDS
   ══════════════════════════════════════════════════════════════════════════════ */

function applyFilterSort() {
  let ps = [...STATE.allPersonas];
  if (STATE.searchQuery) {
    const q = STATE.searchQuery.toLowerCase();
    // Search by business (product line), not persona name.
    ps = ps.filter(p => (p.personaData?.product || '').toLowerCase().includes(q));
  }
  if (STATE.activeFilter === 'failed')  ps = ps.filter(p => isTechnicalFailure(p));
  if (STATE.activeProducts.size > 0) {
    ps = ps.filter(p => STATE.activeProducts.has(p.personaData?.product || 'General'));
  }
  if (STATE.activeSort === 'score-asc')  ps.sort((a, b) => a.overallScore - b.overallScore);
  if (STATE.activeSort === 'score-desc') ps.sort((a, b) => b.overallScore - a.overallScore);
  if (STATE.activeSort === 'name')       ps.sort((a, b) => a.name.localeCompare(b.name));
  STATE.filteredPersonas = ps;
  updateStats(ps);
  renderCards(ps);
}

function renderProductDropdown() {
  const wrap = qs('#product-filter-wrap');
  const btn  = qs('#product-dropdown-btn');
  const menu = qs('#product-dropdown-menu');
  if (!wrap || !btn || !menu) return;

  const products = [...new Set(STATE.allPersonas.map(p => p.personaData?.product || 'General'))].sort();
  if (products.length <= 1) { wrap.style.display = 'none'; return; }

  wrap.style.display = 'flex';

  function _renderItems() {
    menu.innerHTML = products.map(prod => `
      <label class="pd-item">
        <input type="checkbox" class="pd-check" value="${esc(prod)}"
          ${STATE.activeProducts.has(prod) ? 'checked' : ''} />
        <span class="pd-label">${esc(prod)}</span>
      </label>`).join('');
    menu.querySelectorAll('.pd-check').forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked) STATE.activeProducts.add(cb.value);
        else            STATE.activeProducts.delete(cb.value);
        _updateBtnLabel();
        applyFilterSort();
      });
    });
  }

  function _updateBtnLabel() {
    const sel = [...STATE.activeProducts];
    btn.innerHTML = sel.length === 0
      ? 'All Products <span class="dropdown-caret">▾</span>'
      : `${sel.length} Product${sel.length > 1 ? 's' : ''} <span class="dropdown-caret">▾</span>`;
  }

  _renderItems();
  _updateBtnLabel();

  btn.onclick = (e) => {
    e.stopPropagation();
    const open = menu.style.display !== 'none';
    menu.style.display = open ? 'none' : 'block';
    btn.classList.toggle('product-dropdown-btn--open', !open);
  };

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!wrap.contains(e.target)) {
      menu.style.display = 'none';
      btn.classList.remove('product-dropdown-btn--open');
    }
  }, { capture: false });
}

// Keep old name as alias so nothing else breaks
const renderProductPills = renderProductDropdown;

function renderCards(personas) {
  const grid  = qs('#cards-grid');
  const empty = qs('#empty-state');
  grid.innerHTML = '';

  if (personas.length === 0) {
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  personas.forEach(p => {
    const card = document.createElement('div');
    card.className = `persona-card ${journeyOutcome(p).cardCls}`;
    card.dataset.slug = p.slug;
    card.innerHTML = buildCardHTML(p);
    card.addEventListener('click', () => openModal(p.slug));
    const del = card.querySelector('[data-delete-persona]');
    if (del) del.addEventListener('click', e => {
      e.stopPropagation();
      deletePersonaRun(p.sourceSlug || p.slug, p.isMobile ? 'app' : 'web', p.runId || '');
    });
    grid.appendChild(card);
  });
}

function failureReasonLabel(p) {
  const reason = (p.terminalReason || '').toLowerCase();
  if (reason === 'login_wall_mobile_entry') return 'The persona chose to enter their mobile number — the pre-login audit boundary was reached. Everything before this point is captured.';
  if (reason === 'done')                    return 'The persona decided to end their journey. The evaluation layer determines the nature of this ending from the full journey context.';
  if (/loop|popup_loop/.test(reason))       return 'The journey encountered a repeating navigation pattern that prevented further progress.';
  if (/consecutive_failures/.test(reason))  return 'The journey ended after multiple unsuccessful interactions in sequence.';
  if (/max_steps|timeout/.test(reason))     return 'The full available journey was captured — the audit covers the complete browsing experience up to this point.';
  if (/navigation_failed/.test(reason))     return 'The site could not be reached. No journey data was captured for this run.';
  if (isTechnicalFailure(p))                return 'This run encountered a technical issue before completing. See developer notes for details.';
  return 'The journey ended — see the evaluation tabs for the full picture.';
}

function isTechnicalFailure(p) {
  if (p.isTechnicalFailure) return true;
  const reason = (p.terminalReason || '').toLowerCase();
  return /navigation_failed|decision_engine|browser|playwright/.test(reason);
}

function journeyOutcome(p) {
  const reason = (p.terminalReason || '').toLowerCase();
  if (reason === 'login_wall_mobile_entry')  return { cls: 'continuation', text: 'Login Boundary',   icon: '→',  cardCls: 'persona-card--continuation' };
  if (reason === 'done')                     return { cls: 'neutral',      text: 'Journey Ended',    icon: '●',  cardCls: 'persona-card--partial' };
  if (/loop|popup_loop/.test(reason))        return { cls: 'dropoff',      text: 'Loop Detected',    icon: '↺',  cardCls: 'persona-card--partial' };
  if (/consecutive_failures/.test(reason))   return { cls: 'dropoff',      text: 'Dropped: Failures',icon: '✕',  cardCls: 'persona-card--partial' };
  if (/max_steps|timeout/.test(reason))      return { cls: 'neutral',      text: 'Full Journey',     icon: '◉',  cardCls: 'persona-card--partial' };
  if (isTechnicalFailure(p))                 return { cls: 'failed',       text: 'Tech Failed',      icon: '⚠',  cardCls: 'persona-card--failed' };
  return { cls: 'neutral', text: 'Journey Ended', icon: '●', cardCls: 'persona-card--partial' };
}

/* Returns a richer drop-off object for the modal badge:
   { icon, label, sub, cls, isDropOff }
   - label: concise primary text
   - sub:   one-line context (step number + page, or why audit ended)
   - cls:   matches outcome-- colour token
   - isDropOff: true = persona truly abandoned; false = audit boundary or success
*/
function urlToLabel(url) {
  if (!url) return '';
  try {
    const path = new URL(url).pathname;
    const parts = path.split('/').filter(Boolean);
    if (!parts.length) return 'Homepage';
    const raw = parts[parts.length - 1]
      .replace(/[-_]/g, ' ')
      .replace(/\.[^/.]+$/, '')
      .trim();
    return raw
      ? raw.replace(/\b\w/g, c => c.toUpperCase())
      : (parts.length > 1
          ? parts[parts.length - 2].replace(/[-_]/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
          : 'Homepage');
  } catch { return ''; }
}

function buildDropOffInfo(p) {
  const reason   = (p.terminalReason || '').toLowerCase();
  const lastStep = p.steps && p.steps.length > 0 ? p.steps[p.steps.length - 1] : null;
  const lastNum  = lastStep ? (lastStep.step_number >= 0 ? lastStep.step_number + 1 : 1) : null;
  const lastPage = lastStep
    ? (lastStep.page_title || urlToLabel(lastStep.url) || null)
    : null;
  // Build "Step N · Page name" context string
  const atStr = lastNum && lastPage ? `Step ${lastNum} · ${lastPage}`
              : lastNum             ? `Step ${lastNum}`
              : lastPage            ? lastPage
              : '';

  if (reason === 'login_wall_mobile_entry') return {
    icon: '→', label: 'Login Boundary Reached',
    sub: atStr
      ? `${atStr} · Persona chose to enter their mobile number — pre-login audit boundary.`
      : 'Persona entered mobile number — pre-login audit ends here.',
    cls: 'continuation', isDropOff: false,
  };

  if (reason === 'done') return {
    icon: '●', label: 'Persona Ended Journey',
    sub: atStr
      ? `${atStr} · The persona decided to stop. See evaluation tabs for context.`
      : 'The persona decided to end their journey. See evaluation tabs for context.',
    cls: 'neutral', isDropOff: false,
  };

  if (/loop|popup_loop/.test(reason)) return {
    icon: '↺', label: 'Stuck in Navigation Loop',
    sub: atStr
      ? `${atStr} · A recurring navigation pattern prevented progress.`
      : 'A recurring navigation pattern prevented further progress.',
    cls: 'dropoff', isDropOff: true,
  };

  if (/consecutive_failures/.test(reason)) return {
    icon: '✕', label: 'Dropped: Repeated Failures',
    sub: atStr
      ? `${atStr} · Multiple consecutive interaction failures ended the journey.`
      : 'Multiple consecutive interaction failures ended the journey.',
    cls: 'dropoff', isDropOff: true,
  };

  if (/max_steps|timeout/.test(reason)) return {
    icon: '◉', label: 'Full Journey Captured',
    sub: atStr
      ? `Covered ${atStr} — no drop-off detected within the audit window.`
      : 'Complete available browsing journey was recorded — no drop-off detected.',
    cls: 'neutral', isDropOff: false,
  };

  if (isTechnicalFailure(p)) return {
    icon: '⚠', label: 'Technical Failure',
    sub: atStr
      ? `${atStr} · Journey ended due to a technical issue.`
      : 'Journey ended due to a technical issue before reaching a natural endpoint.',
    cls: 'failed', isDropOff: false,
  };

  return {
    icon: '•', label: 'Partial Journey',
    sub: atStr
      ? `${atStr} · Journey did not reach a clear endpoint.`
      : 'Journey did not reach a clear endpoint.',
    cls: 'neutral', isDropOff: false,
  };
}

function personaRunKey(p) {
  if (!p) return '';
  const slug = p.sourceSlug || p.slug || '';
  return p.runId ? `${p.runId}__${slug}__${p.isMobile ? 'app' : 'web'}` : `${slug}__${p.isMobile ? 'app' : 'web'}`;
}

// Short labels for the card dimension bars. Defaults to the dimension's first
// word; override here where the first word alone is ambiguous.
const CARD_DIM_LABELS = {
  'Financial Clarity and Disclosure': 'Financial Clarity',
};

function buildCardHTML(p) {
  const scoreClass = p.overallScore >= 7 ? 'high' : p.overallScore >= 4 ? 'mid' : 'low';
  const outcomeState = journeyOutcome(p);
  const topFriction = p.frictionPoints.length > 0
    ? p.frictionPoints.filter(f => f.severity === 'high')[0] || p.frictionPoints[0]
    : null;

  const dims = p.dimensions.slice(0, 5).map(d => `
    <div class="card-dim">
      <span class="card-dim-name">${CARD_DIM_LABELS[d.name] || d.name?.split(' ')[0] || '—'}</span>
      <div class="card-dim-bar">
        <div class="card-dim-fill" style="width:${(d.score/10)*100}%;background:${scoreGradient(d.score)}"></div>
      </div>
      <span class="card-dim-score">${d.score?.toFixed(1)}</span>
    </div>`).join('');

  // Persona key attributes
  const pd = p.personaData || {};
  const attrs = [pd.occupation, pd.age ? `Age ${pd.age}` : '', pd.location].filter(Boolean).slice(0, 2);
  const auditTypeBadge = p.isMobile ? '<span class="card-type-badge">📱 App</span>' : '<span class="card-type-badge">🌐 Web</span>';
  const evalTypeLabel = p.evalType === 'both' ? 'CX + Design'
    : p.evalType === 'design' ? 'Design' : p.evalType === 'cx' ? 'CX' : '';
  const evalChipCls = p.evalType === 'both' ? 'both' : p.evalType === 'design' ? 'design' : 'cx';
  const evalTypeBadge = evalTypeLabel
    ? `<span class="card-eval-chip card-eval-chip--${evalChipCls}">${evalTypeLabel}</span>` : '';
  const productTag = pd.product && pd.product !== 'General'
    ? `<span class="card-product-badge">${esc(pd.product)}</span>` : '';
  const runTime = formatDateTime(p.createdAt);

  const designScoreBadge = p.designAuditScore > 0
    ? `<div class="card-design-score" title="Design Score">${p.designAuditScore.toFixed(1)}<span class="card-design-score-label">Design</span></div>` : '';

  return `
    <div class="card-header">
      <div class="card-avatar">${(p.name[0] || '?').toUpperCase()}</div>
      <div class="card-info">
        <h3 class="card-name">${esc(p.name)} ${auditTypeBadge}${evalTypeBadge}</h3>
        <p class="card-run-time">Run: ${esc(runTime)}</p>
        ${attrs.length ? `<p class="card-attrs">${attrs.map(esc).join(' · ')}</p>` : ''}

      </div>
      <div class="card-scores">
        <div class="card-score-badge card-score-badge--${scoreClass}" title="CX Score">${p.overallScore.toFixed(1)}</div>
        ${designScoreBadge}
      </div>
    </div>
    <p class="card-intent">${esc(p.intent)}</p>
    <div class="card-dims">${dims}</div>
    ${p.tldr ? `<div class="card-tldr"><span class="card-tldr-label">TL;DR</span>${esc(p.tldr)}</div>` : ''}
    ${p.costInr !== null ? `<div class="card-cost-badge">₹${p.costInr.toFixed(2)}</div>` : ''}
    <div class="card-foot">
      <span class="card-stat">${p.stepCount} steps</span>
      <span class="card-stat">${p.failureCount} failures</span>
      <span class="card-stat">${p.frictionPoints.length} friction pts</span>
      ${productTag}
      <button type="button" class="btn btn--danger btn--xs card-delete-btn" data-delete-persona>Delete</button>
    </div>`;
}

window.resetFilters = function() {
  STATE.activeFilter = 'all';
  STATE.activeSort   = 'default';
  STATE.searchQuery  = '';
  STATE.activeProducts.clear();
  qs('#search-input').value = '';
  qsa('.filter-pill').forEach(p => p.classList.toggle('filter-pill--active', p.dataset.filter === 'all'));
  qsa('.sort-pill').forEach(p => p.classList.toggle('sort-pill--active', p.dataset.sort === 'default'));
  // Reset the product dropdown checkboxes and label
  const menu = qs('#product-dropdown-menu');
  const btn  = qs('#product-dropdown-btn');
  if (menu) qsa('.pd-check', menu).forEach(cb => { cb.checked = false; });
  if (btn)  btn.innerHTML = 'All Products <span class="dropdown-caret">▾</span>';
  applyFilterSort();
};

function bindDashboardEvents() {
  qs('#search-input').addEventListener('input', e => {
    STATE.searchQuery = e.target.value.trim();
    applyFilterSort();
  });
  qs('#search-clear').addEventListener('click', () => {
    qs('#search-input').value = '';
    STATE.searchQuery = '';
    applyFilterSort();
  });
  qsa('.sort-pill').forEach(btn => btn.addEventListener('click', () => {
    STATE.activeSort = btn.dataset.sort;
    qsa('.sort-pill').forEach(p => p.classList.remove('sort-pill--active'));
    btn.classList.add('sort-pill--active');
    applyFilterSort();
  }));
  qsa('.filter-pill').forEach(btn => btn.addEventListener('click', () => {
    STATE.activeFilter = btn.dataset.filter;
    qsa('.filter-pill').forEach(p => p.classList.remove('filter-pill--active'));
    btn.classList.add('filter-pill--active');
    applyFilterSort();
  }));
  qs('#refresh-btn').addEventListener('click', async () => {
    showLoading();
    await init();
  });
}

/* ══════════════════════════════════════════════════════════════════════════════
   MODAL — open / close / tabs
   ══════════════════════════════════════════════════════════════════════════════ */

async function openModal(slug) {
  const p = STATE.allPersonas.find(x => x.slug === slug)
         || await loadPersonaData(slug);
  if (!p) return;
  STATE.activePersona = p;

  qs('#modal-avatar').textContent       = (p.name[0] || '?').toUpperCase();
  qs('#modal-persona-name').textContent = p.name;
  qs('#modal-intent').textContent       = p.intent;

  const scoreClass = p.overallScore >= 7 ? 'high' : p.overallScore >= 4 ? 'mid' : 'low';
  qs('#modal-score-badge').textContent = p.overallScore.toFixed(1) + '/10';
  qs('#modal-score-badge').className   = `modal-score-badge score--${scoreClass}`;

  // Rich drop-off badge
  const dropOff = buildDropOffInfo(p);
  const doBadge = qs('#modal-dropoff-badge');
  if (doBadge) {
    doBadge.className = `modal-dropoff-badge outcome--${dropOff.cls}`;
    const iconEl  = qs('#modal-dropoff-icon',  doBadge);
    const labelEl = qs('#modal-dropoff-label', doBadge);
    const subEl   = qs('#modal-dropoff-sub',   doBadge);
    if (iconEl)  iconEl.textContent  = dropOff.icon;
    if (labelEl) labelEl.textContent = dropOff.label;
    if (subEl) {
      subEl.textContent    = dropOff.sub || '';
      subEl.style.display  = dropOff.sub ? '' : 'none';
    }
  }

  renderPersonaPanel(p);
  renderOverview(p);
  renderJourney(p);
  renderFailureNotes(p);
  renderFriction(p);
  renderScreenshots(p);
  renderGoogleEntry(p);
  renderReport(p);

  // Show Google Entry tab only when data exists
  const geTab = qs('#modal-tab-google-entry');
  if (geTab) geTab.style.display = p.googleEntry ? '' : 'none';

  // Show Design Audit tab only when design data exists
  const daTab = qs('#modal-tab-design-audit');
  if (daTab) daTab.style.display = p.designAuditScore > 0 || p.designIssues?.length ? '' : 'none';

  // Show Content Analysis tab only when data exists
  const caTab = qs('#modal-tab-content-analysis');
  if (caTab) caTab.style.display = p.contentAnalysis ? '' : 'none';

  // Show Accessibility tab only when data exists
  const a11yTab = qs('#modal-tab-accessibility');
  if (a11yTab) a11yTab.style.display = p.accessibilityAudit ? '' : 'none';

  renderDesignAudit(p);
  renderContentAnalysis(p);
  renderAccessibility(p);

  switchModalTab('overview');

  qs('#modal-backdrop').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  qs('#modal-backdrop').classList.remove('open');
  document.body.style.overflow = '';
  STATE.activePersona = null;
}

function switchModalTab(tabName) {
  qsa('.modal-tab').forEach(t => t.classList.toggle('modal-tab--active', t.dataset.tab === tabName));
  qsa('.tab-panel').forEach(p => p.classList.toggle('tab-panel--active', p.id === `panel-${tabName}`));
}

function bindModalEvents() {
  qs('#modal-close').addEventListener('click', closeModal);
  qs('#modal-backdrop').addEventListener('click', e => {
    if (e.target === qs('#modal-backdrop')) closeModal();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });
  qsa('.modal-tab').forEach(tab => {
    tab.addEventListener('click', () => switchModalTab(tab.dataset.tab));
  });
  qs('#ss-prev').addEventListener('click', () => stepScreenshot(-1));
  qs('#ss-next').addEventListener('click', () => stepScreenshot(+1));
  qs('#lightbox-close').addEventListener('click', closeLightbox);
  qs('#lightbox-prev').addEventListener('click', () => stepLightbox(-1));
  qs('#lightbox-next').addEventListener('click', () => stepLightbox(+1));
  qs('#lightbox').addEventListener('click', e => {
    if (e.target === qs('#lightbox')) closeLightbox();
  });
}

/* ── Persona details panel ──────────────────────────────────────────────── */

function renderPersonaPanel(p) {
  const grid = qs('#persona-details-grid');
  const pd   = p.personaData || {};

  const LABELS = {
    name: 'Name', age: 'Age', gender: 'Gender',
    occupation: 'Occupation', location: 'Location', device: 'Device',
    financial_literacy: 'Financial Literacy', intent: 'Goal / Intent',
    constraints: 'Constraints', behaviour: 'Typical Behaviour',
    success_criteria: 'Success Criteria',
  };

  const known = ['name','age','gender','occupation','location','device',
                 'financial_literacy','intent','constraints','behaviour','success_criteria'];

  let html = '<div class="persona-profile-card">';
  html += `<div class="pp-avatar">${(p.name[0] || '?').toUpperCase()}</div>`;
  html += `<div class="pp-name">${esc(p.name)}</div>`;
  if (pd.occupation) html += `<div class="pp-role">${esc(pd.occupation)}</div>`;
  if (pd.age || pd.location) {
    html += `<div class="pp-meta">`;
    if (pd.age)      html += `<span>${esc(pd.age)} yrs</span>`;
    if (pd.location) html += `<span>${esc(pd.location)}</span>`;
    html += `</div>`;
  }
  html += '</div>';

  html += '<div class="persona-attrs">';
  for (const key of known) {
    const val = pd[key];
    if (!val || key === 'name') continue;
    html += `
      <div class="pa-item">
        <span class="pa-label">${LABELS[key] || key}</span>
        <span class="pa-value">${esc(String(val))}</span>
      </div>`;
  }
  // Extra attributes not in known list
  for (const [key, val] of Object.entries(pd)) {
    if (known.includes(key) || !val) continue;
    html += `
      <div class="pa-item">
        <span class="pa-label">${esc(key.replace(/_/g,' '))}</span>
        <span class="pa-value">${esc(String(val))}</span>
      </div>`;
  }
  html += '</div>';

  grid.innerHTML = html;
}

/* ── Overview panel ─────────────────────────────────────────────────────── */

function renderOverview(p) {
  const highFriction = p.frictionPoints.filter(f => f.severity === 'high');
  const p1Recs = p.recommendations.filter(r => r.priority === 'P1');
  const PRIO = { P1: 0, P2: 1, P3: 2 };
  const allRecs = [...p.recommendations].sort((a, b) => (PRIO[a.priority]??3) - (PRIO[b.priority]??3));

  // ── TL;DR box ──
  const tldrText = p.tldr || p.journeyVerdict || '';
  qs('#overview-verdict').innerHTML = tldrText ? `
    <div class="tldr-label">TL;DR</div>
    <div class="tldr-text">${esc(tldrText)}</div>` : '';

  // ── Key takeaways ──
  const ktEl = qs('#overview-key-takeaways');
  if (ktEl) {
    if (p.keyTakeaways && p.keyTakeaways.length) {
      ktEl.innerHTML = `
        <div class="section-title">Key Takeaways</div>
        <ol class="key-takeaways-list">
          ${p.keyTakeaways.map(kt => `<li class="kt-item">${esc(kt)}</li>`).join('')}
        </ol>`;
      ktEl.style.display = 'block';
    } else {
      ktEl.style.display = 'none';
    }
  }

  // ── Quick stat strip ──
  const statStrip = qs('#overview-stat-strip');
  if (statStrip) {
    const outcomeState = journeyOutcome(p);
    const outcomeClass = outcomeState.cls === 'success' ? 'success' : outcomeState.cls === 'failed' ? 'fail' : 'warn';
    statStrip.innerHTML = `
      <div class="qs-item qs-item--${outcomeClass}">
        <span class="qs-val">${outcomeState.icon}</span>
        <span class="qs-lbl">${esc(outcomeState.text)}</span>
      </div>
      <div class="qs-item">
        <span class="qs-val">${p.stepCount}</span>
        <span class="qs-lbl">Steps</span>
      </div>
      <div class="qs-item qs-item--${highFriction.length > 0 ? 'warn' : 'ok'}">
        <span class="qs-val">${highFriction.length}</span>
        <span class="qs-lbl">Critical Issues</span>
      </div>
      <div class="qs-item">
        <span class="qs-val">${p.failureCount}</span>
        <span class="qs-lbl">Failed Actions</span>
      </div>
      <div class="qs-item">
        <span class="qs-val">${p.visitedUrls.length}</span>
        <span class="qs-lbl">Pages Visited</span>
      </div>`;
  }

  // ── CX Dimensions ──
  // Build a map: dimension name → [{step_number, action, score, observation, url}]
  const dimStepMap = {};
  (p.stepEvaluations || []).forEach(se => {
    (se.dimension_scores || []).forEach(ds => {
      if (!ds.dimension || ds.is_na) return;
      const key = ds.dimension;
      if (!dimStepMap[key]) dimStepMap[key] = [];
      dimStepMap[key].push({
        step_number: se.step_number,
        action:      se.action || '',
        url:         se.url    || '',
        score:       ds.score,
        observation: ds.observation || '',
      });
    });
  });

  const dimsList = qs('#dimensions-list');
  dimsList.innerHTML = p.dimensions.map((d, idx) => {
    const steps   = dimStepMap[d.name] || [];
    const hasSteps = steps.length > 0;
    const stepsHtml = steps.map(s => `
      <div class="dim-step-row">
        <div class="dim-step-meta">
          <span class="dim-step-num">Step ${s.step_number >= 0 ? s.step_number + 1 : 'Home'}</span>
          ${s.action ? `<span class="dim-step-action">${esc(s.action)}</span>` : ''}
          <span class="dim-step-score" style="color:${scoreColor(s.score)}">${s.score?.toFixed(1)}/10</span>
          <div class="dim-step-bar-track">
            <div class="dim-step-bar-fill" style="width:${(s.score/10)*100}%;background:${scoreGradient(s.score)}"></div>
          </div>
        </div>
        ${s.observation ? `<p class="dim-step-obs">${esc(s.observation)}</p>` : ''}
        ${s.url ? `<p class="dim-step-url">${esc(s.url.replace(/^https?:\/\//, '').substring(0, 60))}${s.url.length > 60 ? '…' : ''}</p>` : ''}
      </div>`).join('');

    return `
    <div class="ov-dim-row${hasSteps ? ' ov-dim-row--expandable' : ''}" id="ov-dim-${idx}">
      <div class="ov-dim-header" ${hasSteps ? `onclick="toggleDimExpand('ov-dim-${idx}')" style="cursor:pointer"` : ''}>
        <span class="ov-dim-name">${esc(d.name)}</span>
        <div class="ov-dim-header-right">
          <span class="ov-dim-score" style="color:${scoreColor(d.score)}">${d.score?.toFixed(1)}/10</span>
          ${hasSteps ? `<span class="ov-dim-chevron">▶</span>` : ''}
        </div>
      </div>
      <div class="ov-dim-bar-track">
        <div class="ov-dim-bar-fill" style="width:${(d.score/10)*100}%;background:${scoreGradient(d.score)}"></div>
      </div>
      ${d.rationale ? `<p class="ov-dim-rationale">${esc(d.rationale)}</p>` : ''}
      ${hasSteps ? `
      <div class="ov-dim-steps" id="ov-dim-steps-${idx}">
        <div class="ov-dim-steps-header">Step-by-step evidence (${steps.length} step${steps.length > 1 ? 's' : ''})</div>
        ${stepsHtml}
      </div>` : ''}
    </div>`;
  }).join('') || '<p class="muted">No dimension scores available.</p>';

  // ── Critical Issues (high severity only in overview) ──
  const critEl = qs('#overview-critical');
  if (critEl) {
    if (highFriction.length) {
      critEl.innerHTML = `
        <div class="section-title">🔴 Critical Issues</div>
        ${highFriction.map(fp => `
          <div class="ov-critical-item">
            <div class="ov-critical-loc">${esc(fp.location || '')}</div>
            <div class="ov-critical-desc">${esc(fp.description || '')}</div>
            <div class="ov-critical-impact">Impact: ${esc(fp.impact || '')}</div>
          </div>`).join('')}`;
    } else {
      critEl.innerHTML = `<div class="section-title">Critical Issues</div><p class="muted">No critical issues identified.</p>`;
    }
  }

  // ── Top Recommendations ──
  qs('#recs-list').innerHTML = allRecs.slice(0, 5).map(r => {
    const pCls = (r.priority || 'P3').toLowerCase();
    return `
      <div class="ov-rec-item ov-rec-item--${pCls}">
        <span class="ov-rec-badge ov-rec-badge--${pCls}">${r.priority}</span>
        <div class="ov-rec-body">
          <div class="ov-rec-area">${esc(r.area || '')}</div>
          <div class="ov-rec-action">${esc(r.action || '')}</div>
        </div>
      </div>`;
  }).join('') || '<p class="muted">No recommendations.</p>';

  // ── What Worked ──
  qs('#positives-list').innerHTML = p.positiveMoments.map(pm =>
    `<li>${esc(pm)}</li>`
  ).join('') || '<li class="muted">None identified.</li>';

}

/* ── Journey timeline ────────────────────────────────────────────────────── */

function renderJourney(p) {
  const outcomeState = journeyOutcome(p);
  const dropOff     = buildDropOffInfo(p);
  qs('#journey-meta').innerHTML = `
    <span class="jm-pill">${p.stepCount} steps</span>
    <span class="jm-pill">${p.visitedUrls.length} pages</span>
    <button type="button" class="jm-toggle" id="journey-expand-toggle" data-state="closed" onclick="toggleAllSteps()">Expand all</button>`;

  const EMOTION_EMOJI = {
    confident:'😊', curious:'🤔', confused:'😕', frustrated:'😤',
    anxious:'😰', overwhelmed:'😵', relieved:'😌', disappointed:'😞',
    suspicious:'🤨', hopeful:'🙂', reassured:'✅', excited:'🎉',
    neutral:'😐', delighted:'😄', unsure:'🤔',
    focused:'🎯', engaged:'💡', determined:'💪', cautious:'🧐',
  };
  const COGNITIVE_COLOR = { low:'#22c55e', medium:'#f59e0b', high:'#ef4444' };

  qs('#journey-timeline').innerHTML = p.steps.map((s, i) => {
    const status   = s.success ? 'success' : 'fail';
    const emotion  = (s.emotion || '').toLowerCase();
    const emojiStr = EMOTION_EMOJI[emotion] ? `${EMOTION_EMOJI[emotion]} ${s.emotion}` : (s.emotion || '');
    const cogLevel = (s.cognitive_load || '').toLowerCase().match(/\b(low|medium|high)\b/)?.[1] || '';
    const cogColor = COGNITIVE_COLOR[cogLevel] || '#94a3b8';
    const stepId   = `jstep-${i}`;
    const ss = s.screenshotRel
      ? `<button class="step-ss-btn" onclick="openLightbox('${esc(s.screenshotRel)}','Step ${s.step_number+1}')">📸</button>`
      : '';

    // Everything past the header + the single "why" lead lives in a collapsed
    // detail drawer, so the timeline stays scannable by default. Nothing is
    // dropped — the full prose (visible content, mindset, trust, questions,
    // CX note …) is one click away. The action/emotion/cognitive-load chips in
    // the header carry the at-a-glance signal.
    const detail = [];
    const add = (label, text, cls) => { if (text) detail.push(
      `<div class="step-field step-field--${cls}"><span class="sf-label">${label}</span><p class="sf-text">${esc(text)}</p></div>`); };
    add("What's on Screen",             s.visible_content,      'visible');
    add('Attention Focus',              s.attention_focus,      'attention');
    add('Cognitive Load',               s.cognitive_load,       'cognitive');
    add('State of Mind',                s.state_of_mind,        'mind');
    add('Trust Signals',                s.trust_signals,        'trust');
    add("What's Guiding Next Decision", s.guiding_factors,      'guiding');
    add('Unanswered Questions',         s.unanswered_questions, 'questions');
    add('CX Insight',                   s.cx_note,              'cx');

    if (s.login_wall_decision) {
      const lwDecision = s.login_wall_decision;
      const lwColor = lwDecision === 'entered_mobile' ? '#6366f1' : lwDecision === 'dismissed' ? '#f59e0b' : '#94a3b8';
      const lwLabel = { entered_mobile: 'Entered Dummy Mobile', dismissed: 'Dismissed Popup', ignored: 'Ignored' }[lwDecision] || lwDecision;
      detail.push(`
        <div class="step-field step-field--loginwall">
          <span class="sf-label">Login Wall Decision</span>
          <span class="lw-badge" style="background:${lwColor}">${esc(lwLabel)}</span>
          ${s.login_wall_reasoning ? `<p class="sf-text">${esc(s.login_wall_reasoning)}</p>` : ''}
        </div>`);
    }

    const detailHtml = detail.join('');
    const hasDetail  = detailHtml.length > 0;
    const cogChip    = cogLevel
      ? `<span class="cog-badge tl-cog" style="background:${cogColor}" title="Cognitive load">${cogLevel.toUpperCase()}</span>` : '';

    return `
      <div class="timeline-item timeline-item--${status}" id="${stepId}">
        <div class="tl-dot tl-dot--${status}"></div>
        <div class="tl-content">
          <div class="tl-header">
            <span class="tl-step">#${s.step_number + 1}</span>
            <span class="tl-action tl-action--${s.action}">${s.action?.toUpperCase() || '?'}</span>
            ${s.target ? `<span class="tl-target">${esc(s.target)}</span>` : ''}
            ${emojiStr ? `<span class="tl-emotion">${esc(emojiStr)}</span>` : ''}
            ${cogChip}
            ${s.duration_ms ? `<span class="tl-duration">${s.duration_ms}ms</span>` : ''}
            ${ss}
          </div>
          ${s.reasoning ? `<p class="tl-lead${hasDetail ? ' tl-lead--clamp' : ''}">${esc(s.reasoning)}</p>` : ''}
          ${hasDetail ? `<button type="button" class="tl-detail-toggle" onclick="toggleStepDetail('${stepId}')"><span class="tdt-label">Details</span><span class="tl-chev">▾</span></button>` : ''}
          ${hasDetail ? `<div class="tl-detail" id="${stepId}-detail" hidden>${detailHtml}</div>` : ''}
          ${s.error ? `<p class="tl-error">⚠ ${esc(s.error)}</p>` : ''}
        </div>
      </div>`;
  }).join('') || '<p class="muted">No steps recorded.</p>';
}

// Expand/collapse a single journey step's detail drawer (also un-clamps its
// "why" lead so nothing stays hidden once opened).
window.toggleStepDetail = function(id) {
  const item = document.getElementById(id);
  if (!item) return;
  const open   = item.classList.toggle('tl-item--open');
  const detail = document.getElementById(`${id}-detail`);
  if (detail) detail.hidden = !open;
  const chev = item.querySelector('.tl-chev');   if (chev) chev.textContent = open ? '▴' : '▾';
  const lbl  = item.querySelector('.tdt-label'); if (lbl)  lbl.textContent  = open ? 'Hide details' : 'Details';
};

// Expand/collapse every step at once (button in the journey meta bar).
window.toggleAllSteps = function() {
  const btn    = document.getElementById('journey-expand-toggle');
  const expand = !btn || btn.dataset.state !== 'open';
  qsa('#journey-timeline .timeline-item').forEach(item => {
    if (!document.getElementById(`${item.id}-detail`)) return;         // no drawer → skip
    if (item.classList.contains('tl-item--open') !== expand) toggleStepDetail(item.id);
  });
  if (btn) { btn.dataset.state = expand ? 'open' : 'closed'; btn.textContent = expand ? 'Collapse all' : 'Expand all'; }
};

/* ── Friction & Delight panel ────────────────────────────────────────────── */

function renderFriction(p) {
  const high   = p.frictionPoints.filter(f => f.severity === 'high').length;
  const medium = p.frictionPoints.filter(f => f.severity === 'medium').length;
  const low    = p.frictionPoints.filter(f => f.severity === 'low').length;
  const delights = p.positiveMoments || [];

  qs('#friction-summary').innerHTML = `
    <div class="fs-row">
      <div class="fs-pill fs-pill--high">🔴 Critical: ${high}</div>
      <div class="fs-pill fs-pill--mid">🟡 Medium: ${medium}</div>
      <div class="fs-pill fs-pill--low">⚠ Low: ${low}</div>
      <div class="fs-pill fs-pill--delight">✨ Delight: ${delights.length}</div>
    </div>`;

  const sorted = [...p.frictionPoints].sort((a, b) =>
    ({high:0,medium:1,low:2}[a.severity]??3) - ({high:0,medium:1,low:2}[b.severity]??3));

  let html = '';

  // ── Delight section ──
  if (delights.length) {
    html += `<div class="fad-section-title fad-section-title--delight">✨ What Worked Well</div>`;
    html += delights.map(pm => `
      <div class="fad-card fad-card--delight">
        <div class="fad-icon">✓</div>
        <p class="fad-text">${esc(pm)}</p>
      </div>`).join('');
  }

  // ── Friction section — grouped by severity ──
  // Build the friction cards first, then only emit the section header when at
  // least one card actually rendered. Guarding on `sorted.length` alone would
  // print a bare "⚠ Friction Points" heading with nothing under it whenever a
  // severity value falls outside the known groups (see severity-map above).
  const SEVERITY_GROUPS = [
    { key: 'high',   label: '🔴 Critical', cls: 'high'   },
    { key: 'medium', label: '🟡 Medium',   cls: 'medium' },
    { key: 'low',    label: '⚠ Low',       cls: 'low'    },
  ];

  let frictionHtml = '';
  for (const grp of SEVERITY_GROUPS) {
    const items = sorted.filter(fp => fp.severity === grp.key);
    if (!items.length) continue;
    frictionHtml += `<div class="fad-severity-group">
      <div class="fad-severity-header fad-severity-header--${grp.cls}">
        <span class="fad-severity-label">${grp.label}</span>
        <span class="fad-severity-count">${items.length} issue${items.length > 1 ? 's' : ''}</span>
      </div>`;
    frictionHtml += items.map(fp => `
      <div class="fad-card fad-card--${fp.severity}">
        <div class="fad-left-bar"></div>
        <div class="fad-body">
          <div class="fad-header">
            ${fp.location ? `<span class="fad-loc">${esc(fp.location)}</span>` : ''}
          </div>
          <p class="fad-text">${esc(fp.description || '')}</p>
          ${fp.impact ? `<p class="fad-impact">Impact: ${esc(fp.impact)}</p>` : ''}
        </div>
      </div>`).join('');
    frictionHtml += `</div>`;
  }

  if (frictionHtml) {
    html += `<div class="fad-section-title fad-section-title--friction" style="margin-top:${delights.length ? 24 : 0}px">⚠ Friction Points</div>`;
    html += frictionHtml;
  }

  if (!html) {
    html = '<p class="muted">No friction or delight moments recorded.</p>';
  }

  qs('#friction-list').innerHTML = html;
}

/* ── Screenshots panel ───────────────────────────────────────────────────── */

function renderScreenshots(p) {
  const shots = p.screenshots || [];
  STATE.ssIndex = 0;
  STATE.lbImages = shots;

  qs('#ss-count').textContent = `${shots.length} screenshots`;

  // Video lives in its own dedicated container — never inside screenshots-stage.
  // Keeping it separate means the screenshot viewer and video player don't interfere,
  // and navigating thumbnails doesn't reset video playback.
  const videoEl = qs('#screenshots-video');
  if (p.videoRel) {
    videoEl.innerHTML = `
      <div class="journey-video-wrap" id="journey-video-wrap">
        <video class="journey-video" controls src="${esc(p.videoRel)}"
          onerror="document.getElementById('journey-video-wrap').style.display='none'"></video>
        <p class="ss-caption">Full journey screen recording</p>
      </div>`;
  } else {
    videoEl.innerHTML = '';
  }

  if (!shots.length) {
    qs('#screenshots-stage').innerHTML = '';
    qs('#screenshots-strip').innerHTML = '';
    return;
  }

  updateScreenshotDisplay();

  qs('#screenshots-strip').innerHTML = shots.map((s, i) => `
    <div class="ss-thumb" data-idx="${i}" onclick="STATE.ssIndex=${i};updateScreenshotDisplay()">
      <img src="${esc(s.src)}" alt="${esc(s.caption)}"
        onerror="this.parentElement.classList.add('ss-thumb--error');this.remove()" />
    </div>`).join('');
}

function stepScreenshot(dir) {
  const shots = STATE.activePersona?.screenshots || [];
  STATE.ssIndex = Math.max(0, Math.min(shots.length - 1, STATE.ssIndex + dir));
  updateScreenshotDisplay();
}

window.updateScreenshotDisplay = function() {
  const shots = STATE.activePersona?.screenshots || [];
  if (!shots.length) return;
  const s = shots[STATE.ssIndex];
  // Video is in #screenshots-video — don't touch it here so playback isn't reset
  // every time the user navigates to a different screenshot.
  qs('#screenshots-stage').innerHTML = `
    <img class="ss-main" src="${esc(s.src)}" alt="${esc(s.caption)}"
      onerror="this.parentElement.classList.add('ss-stage--error');this.parentElement.innerHTML='<div class=ss-not-found><span>📷</span><p>Screenshot not available</p><small>${esc(s.src)}</small></div>'"
      onclick="openLightbox('${esc(s.src)}','${esc(s.caption)}')" />
    <p class="ss-caption">${esc(s.caption)}</p>`;
  qs('#ss-progress').textContent = `${STATE.ssIndex + 1} / ${shots.length}`;
};

/* ── Content Analysis panel ──────────────────────────────────────────────── */

function renderContentAnalysis(p) {
  const el = qs('#content-analysis-content');
  if (!el) return;
  const ca = p.contentAnalysis;
  if (!ca) { el.innerHTML = '<p class="muted">Content analysis not available for this run.</p>'; return; }

  const scoreColor = score => score >= 7 ? '#22c55e' : score >= 5 ? '#f59e0b' : '#ef4444';

  let html = `
    <div class="ca-header">
      <div class="ca-score-ring" style="--ring-color:${scoreColor(ca.overall_content_score)}">
        <span class="ca-score-val">${(+ca.overall_content_score).toFixed(1)}</span>
        <span class="ca-score-label">/10</span>
      </div>
      <div class="ca-summary-block">
        <div class="ca-summary-title">Content Quality Summary</div>
        <p class="ca-summary-text">${esc(ca.content_summary || '')}</p>
      </div>
    </div>`;

  // Strengths & Gaps
  if (ca.content_strengths?.length || ca.content_gaps?.length) {
    html += '<div class="ca-two-col">';
    if (ca.content_strengths?.length) {
      html += `<div class="ca-col ca-col--strengths">
        <div class="ca-col-title">✓ Strengths</div>
        ${ca.content_strengths.map(s => `<div class="ca-item ca-item--strength">${esc(s)}</div>`).join('')}
      </div>`;
    }
    if (ca.content_gaps?.length) {
      html += `<div class="ca-col ca-col--gaps">
        <div class="ca-col-title">✗ Content Gaps</div>
        ${ca.content_gaps.map(g => `<div class="ca-item ca-item--gap">${esc(g)}</div>`).join('')}
      </div>`;
    }
    html += '</div>';
  }

  // Recommendations
  if (ca.content_recommendations?.length) {
    html += `<div class="ca-section-title">Content Recommendations</div>
    <div class="ca-recs">`;
    html += ca.content_recommendations.map(r => `
      <div class="ca-rec ca-rec--${(r.priority||'P3').toLowerCase()}">
        <span class="ca-rec-priority">${esc(r.priority || 'P3')}</span>
        <span class="ca-rec-area">${esc(r.area || '')}</span>
        <p class="ca-rec-text">${esc(r.recommendation || '')}</p>
        ${r.expected_impact ? `<p class="ca-rec-impact">${esc(r.expected_impact)}</p>` : ''}
      </div>`).join('');
    html += '</div>';
  }

  // Content dimensions with expandable per-step evidence (from step_evaluations)
  const contentDims = ca.dimensions || ca.dimension_scores || [];
  if (contentDims.length) {
    // Build map: dimension name → [{step_number, action, url, score, observation}]
    const contentDimStepMap = {};
    (ca.step_evaluations || []).forEach(se => {
      (se.dimension_scores || []).forEach(ds => {
        if (!ds.dimension || ds.is_na) return;
        if (!contentDimStepMap[ds.dimension]) contentDimStepMap[ds.dimension] = [];
        contentDimStepMap[ds.dimension].push({
          step_number: se.step_number,
          action:      se.action || '',
          url:         se.url   || '',
          score:       ds.score,
          observation: ds.observation || '',
        });
      });
    });

    html += `<div class="ca-section-title">Content Dimensions</div><div class="ca-dims-list">`;
    html += contentDims.map((d, idx) => {
      const dimName  = d.name || d.dimension_name || '';
      const dimScore = +(d.score ?? 0);
      const steps    = contentDimStepMap[dimName] || [];
      const hasSteps = steps.length > 0;
      const rowId    = `ca-dim-${idx}`;
      const stepsHtml = steps.map(s => `
        <div class="dim-step-row">
          <div class="dim-step-meta">
            <span class="dim-step-num">Step ${s.step_number >= 0 ? s.step_number + 1 : 'Home'}</span>
            ${s.action ? `<span class="dim-step-action">${esc(s.action)}</span>` : ''}
            <span class="dim-step-score" style="color:${scoreColor(s.score)}">${(+s.score).toFixed(1)}/10</span>
            <div class="dim-step-bar-track">
              <div class="dim-step-bar-fill" style="width:${(s.score/10)*100}%;background:${scoreGradient(s.score)}"></div>
            </div>
          </div>
          ${s.observation ? `<p class="dim-step-obs">${esc(s.observation)}</p>` : ''}
          ${s.url ? `<p class="dim-step-url">${esc(s.url.replace(/^https?:\/\//, '').substring(0,60))}${s.url.length > 60 ? '…' : ''}</p>` : ''}
        </div>`).join('');

      return `
        <div class="ov-dim-row${hasSteps ? ' ov-dim-row--expandable' : ''}" id="${rowId}">
          <div class="ov-dim-header" ${hasSteps ? `onclick="toggleDimExpand('${rowId}')" style="cursor:pointer"` : ''}>
            <span class="ov-dim-name">${esc(dimName)}</span>
            <div class="ov-dim-header-right">
              <span class="ov-dim-score" style="color:${scoreColor(dimScore)}">${dimScore.toFixed(1)}/10</span>
              ${hasSteps ? `<span class="ov-dim-chevron">▶</span>` : ''}
            </div>
          </div>
          <div class="ov-dim-bar-track">
            <div class="ov-dim-bar-fill" style="width:${(dimScore/10)*100}%;background:${scoreGradient(dimScore)}"></div>
          </div>
          ${d.rationale ? `<p class="ov-dim-rationale">${esc(d.rationale)}</p>` : ''}
          ${hasSteps ? `
          <div class="ov-dim-steps" id="ov-dim-steps-${rowId}">
            <div class="ov-dim-steps-header">Step-by-step evidence (${steps.length} step${steps.length !== 1 ? 's' : ''})</div>
            ${stepsHtml}
          </div>` : ''}
        </div>`;
    }).join('');
    html += `</div>`;
  }

  el.innerHTML = html;
}

/* ── Accessibility panel ─────────────────────────────────────────────────── */

function renderAccessibility(p) {
  const el = qs('#accessibility-content');
  if (!el) return;
  const aa = p.accessibilityAudit;
  if (!aa) { el.innerHTML = '<p class="muted">Accessibility audit not available for this run.</p>'; return; }

  const scoreColor   = s => s >= 7 ? '#22c55e' : s >= 5 ? '#f59e0b' : '#ef4444';
  const severityColor = { critical:'#ef4444', serious:'#f97316', moderate:'#f59e0b', minor:'#94a3b8' };
  const conformanceClass = {
    'Fails A':'a11y-conf--fail', 'Partial A':'a11y-conf--partial',
    'Meets A':'a11y-conf--meets-a', 'Partial AA':'a11y-conf--partial-aa',
    'Meets AA':'a11y-conf--meets-aa',
  };

  const conformance = aa.wcag_conformance_level || '';
  let html = `
    <div class="a11y-header">
      <div class="a11y-score-ring" style="--ring-color:${scoreColor(aa.overall_accessibility_score||0)}">
        <span class="a11y-score-val">${(+(aa.overall_accessibility_score||0)).toFixed(1)}</span>
        <span class="a11y-score-label">/10</span>
      </div>
      <div class="a11y-header-right">
        <span class="a11y-conformance ${conformanceClass[conformance]||''}">${esc(conformance)}</span>
        <div class="a11y-scope">Scope: WCAG 2.2 Level A &amp; AA (visual assessment)</div>
        <p class="a11y-summary">${esc(aa.accessibility_summary || '')}</p>
      </div>
    </div>`;

  // Critical barriers
  if (aa.critical_barriers?.length) {
    html += `<div class="a11y-section-title a11y-section-title--critical">Critical Barriers</div>
    <div class="a11y-barriers">
      ${aa.critical_barriers.map(b => `<div class="a11y-barrier">${esc(b)}</div>`).join('')}
    </div>`;
  }

  // ── WCAG Principle Dimensions (overall + per-step breakdown) ──────────────
  const a11yDims = aa.dimensions || [];
  const a11yStepAudits = aa.step_audits || [];

  // Map principle name → flat per-step score field
  const a11yPrincipleKey = {
    'Perceivable':    'perceivable_score',
    'Operable':       'operable_score',
    'Understandable': 'understandable_score',
    'Robust':         'robust_score',
  };

  if (a11yDims.length) {
    html += `<div class="a11y-section-title">WCAG Principle Scores</div>
    <div class="ov-dim-grid">`;

    a11yDims.forEach((dim, idx) => {
      const dimScore  = dim.score != null ? (+dim.score).toFixed(1) : '—';
      const scoreClr  = dim.score != null ? scoreColor(+dim.score) : '#94a3b8';
      const stepKey   = a11yPrincipleKey[dim.name] || null;

      // Build per-step evidence for this principle
      const stepPanels = a11yStepAudits.map(sa => {
        const raw  = stepKey ? sa[stepKey] : null;
        const ps   = raw != null ? (+raw).toFixed(1) : '—';
        const psClr = raw != null ? scoreColor(+raw) : '#94a3b8';
        const stepLabel = `Step ${(sa.step_number ?? 0) + 1}`;
        const finding   = sa.key_accessibility_finding || '';

        // For Perceivable/Operable/Understandable, pull relevant issues from wcag_issues
        const relevant = (sa.wcag_issues || []).filter(i => {
          const c = (i.criterion || '').toLowerCase();
          if (dim.name === 'Perceivable')    return /^1\./.test(i.criterion || '');
          if (dim.name === 'Operable')       return /^2\./.test(i.criterion || '');
          if (dim.name === 'Understandable') return /^3\./.test(i.criterion || '');
          if (dim.name === 'Robust')         return /^4\./.test(i.criterion || '');
          return false;
        });

        const issueChips = relevant.length
          ? relevant.map(i => `<span class="dsgn-step-issue-chip a11y-chip--${i.severity}">${esc(i.criterion)}</span>`).join('')
          : `<span class="dsgn-step-na">No ${esc(dim.name)} issues observed</span>`;

        return `
          <div class="dsgn-dim-step-panel">
            <div class="dsgn-dim-step-header">
              <span class="dsgn-dim-step-label">${esc(stepLabel)}</span>
              <span class="dsgn-dim-step-action">${esc(sa.action || '')}</span>
              <span class="dsgn-dim-step-score" style="color:${psClr}">${ps}/10</span>
            </div>
            <div class="dsgn-dim-step-chips">${issueChips}</div>
            ${finding ? `<p class="dsgn-dim-step-obs">${esc(finding)}</p>` : ''}
          </div>`;
      }).join('');

      const domId = `a11y-dim-${idx}`;
      html += `
        <div class="ov-dim-row ov-dim-row--expandable" id="${domId}">
          <div class="ov-dim-header" onclick="toggleDimExpand('${domId}')">
            <span class="ov-dim-name">${esc(dim.name || '')}</span>
            <span class="ov-dim-score" style="color:${scoreClr}">${dimScore}/10</span>
            <span class="ov-dim-chevron">▸</span>
          </div>
          <p class="ov-dim-rationale">${esc(dim.rationale || '')}</p>
          <div class="ov-dim-steps-panel" style="display:none">
            ${stepPanels || '<p class="dsgn-step-empty">No per-step principle data available.</p>'}
          </div>
        </div>`;
    });

    html += '</div>'; // .ov-dim-grid
  }

  // Journey-level WCAG failures (deduplicated)
  if (aa.journey_wcag_failures?.length) {
    html += `<div class="a11y-section-title">WCAG Failures Across Journey</div>
    <div class="a11y-failures">`;
    html += aa.journey_wcag_failures.map(f => `
      <div class="a11y-failure a11y-failure--${f.severity}">
        <div class="a11y-failure-header">
          <span class="a11y-criterion">${esc(f.criterion)}</span>
          <span class="a11y-level-badge">Level ${esc(f.level)}</span>
          <span class="a11y-sev-badge" style="background:${severityColor[f.severity]||'#94a3b8'}">${esc(f.severity)}</span>
          ${f.affected_steps?.length ? `<span class="a11y-steps-badge">Steps: ${f.affected_steps.join(', ')}</span>` : ''}
        </div>
        <p class="a11y-fail-desc">${esc(f.description || '')}</p>
        ${f.recommendation ? `<p class="a11y-fail-rec">Fix: ${esc(f.recommendation)}</p>` : ''}
      </div>`).join('');
    html += '</div>';
  }

  // Recommendations
  if (aa.accessibility_recommendations?.length) {
    html += `<div class="a11y-section-title">Accessibility Recommendations</div>
    <div class="a11y-recs">`;
    html += aa.accessibility_recommendations.map(r => `
      <div class="a11y-rec a11y-rec--${(r.priority||'P3').toLowerCase()}">
        <span class="a11y-rec-priority">${esc(r.priority||'')}</span>
        <span class="a11y-rec-criterion">${esc(r.criterion||'')}</span>
        <span class="a11y-rec-area">${esc(r.area||'')}</span>
        <p class="a11y-rec-text">${esc(r.recommendation||'')}</p>
        ${r.expected_impact ? `<p class="a11y-rec-impact">${esc(r.expected_impact)}</p>` : ''}
      </div>`).join('');
    html += '</div>';
  }

  // Per-step audits
  if (aa.step_audits?.length) {
    html += `<div class="a11y-section-title">Per-Step Accessibility Audit</div>`;
    html += aa.step_audits.map(sa => {
      const stepScore = sa.step_accessibility_score != null ? (+sa.step_accessibility_score).toFixed(1) : '—';
      const issueRows = (sa.wcag_issues || []).map(i => `
        <div class="a11y-step-issue">
          <div class="a11y-step-issue-header">
            <span class="a11y-criterion">${esc(i.criterion)}</span>
            <span class="a11y-level-badge">Level ${esc(i.level)}</span>
            <span class="a11y-sev-badge" style="background:${severityColor[i.severity]||'#94a3b8'}">${esc(i.severity)}</span>
          </div>
          <p class="a11y-issue-desc">${esc(i.description||'')}</p>
          ${i.recommendation ? `<p class="a11y-issue-rec">Fix: ${esc(i.recommendation)}</p>` : ''}
        </div>`).join('');
      const passRows = (sa.wcag_passes || []).map(pass => `
        <div class="a11y-step-pass">
          <span class="a11y-pass-criterion">${esc(pass.criterion)}</span>
          <span class="a11y-pass-obs">${esc(pass.observation||'')}</span>
        </div>`).join('');

      // Per-step principle score pills
      const principleBar = ['Perceivable','Operable','Understandable','Robust'].map(p => {
        const key = a11yPrincipleKey[p];
        const v   = sa[key] != null ? (+sa[key]).toFixed(1) : '—';
        const clr = sa[key] != null ? scoreColor(+sa[key]) : '#94a3b8';
        return `<span class="a11y-principle-pill"><span class="a11y-principle-name">${p[0]}</span><span class="a11y-principle-val" style="color:${clr}">${v}</span></span>`;
      }).join('');

      return `
        <div class="a11y-step-card ${sa.wcag_issues?.length ? '' : 'a11y-step-card--clean'}">
          <div class="a11y-step-header">
            <span class="a11y-step-num">Step ${(sa.step_number??0)+1}</span>
            <span class="a11y-step-action">${esc(sa.action||'')}</span>
            <span class="a11y-step-score" style="color:${scoreColor(+stepScore||0)}">${stepScore}/10</span>
            ${sa.wcag_issues?.length ? `<span class="a11y-issue-count">${sa.wcag_issues.length} issue${sa.wcag_issues.length>1?'s':''}</span>` : '<span class="a11y-issue-count a11y-issue-count--clean">No issues</span>'}
          </div>
          <div class="a11y-principle-bar">${principleBar}</div>
          ${sa.key_accessibility_finding ? `<p class="a11y-step-finding">${esc(sa.key_accessibility_finding)}</p>` : ''}
          ${issueRows}
          ${passRows ? `<details class="a11y-passes-details"><summary>Passes (${sa.wcag_passes?.length||0})</summary>${passRows}</details>` : ''}
        </div>`;
    }).join('');
  }

  el.innerHTML = html;
}

/* ── Google Entry panel ──────────────────────────────────────────────────── */

function renderGoogleEntry(p) {
  const el = qs('#google-entry-content');
  if (!el) return;
  const ge = p.googleEntry;
  if (!ge) { el.innerHTML = '<p class="dim-note">No Google Search entry data for this run.</p>'; return; }

  const scrollLabel = { above_fold: 'Visible on load (no scroll needed)', below_fold: 'Required scrolling to find' };

  // rank = SERP position of the URL the persona actually clicked
  const rankBadge = ge.rank
    ? `<span class="ge-rank-badge ge-rank-badge--${ge.rank <= 3 ? 'good' : ge.rank <= 7 ? 'mid' : 'bad'}" title="Position ${ge.rank} in organic Google results">#${ge.rank}</span>`
    : '<span class="ge-rank-badge ge-rank-badge--bad">Not found</span>';

  // When the persona skipped the top Bajaj result, show both ranks side-by-side
  const skipNote = ge.relevance_skip
    ? `<div class="ge-skip-note" title="Top Bajaj result was less relevant to this persona's intent">
         ⚠ Persona skipped #${ge.first_bajaj_rank} → chose #${ge.clicked_bajaj_rank}
       </div>`
    : '';

  const urlsHtml = (ge.urls_found || []).map((u, i) =>
    `<div class="ge-url-row ${i === 0 ? 'ge-url-row--clicked' : ''}">
      <span class="ge-url-pos">${i + 1}</span>
      <span class="ge-url-text" title="${esc(u)}">${esc(u.replace(/^https?:\/\//, '').slice(0, 80))}${u.length > 80 ? '…' : ''}</span>
      ${i === 0 ? '<span class="ge-url-clicked-badge">clicked</span>' : ''}
    </div>`
  ).join('') || '<p class="dim-note">No Bajaj URLs found in results.</p>';

  el.innerHTML = `
    <div class="ge-section">
      <div class="ge-stat-row">
        <div class="ge-stat">
          <div class="ge-stat-label">Search Query</div>
          <div class="ge-stat-value ge-query">"${esc(ge.query || '—')}"</div>
        </div>
        <div class="ge-stat">
          <div class="ge-stat-label">SERP Position (clicked)</div>
          <div class="ge-stat-value">${rankBadge}${skipNote}</div>
        </div>
        <div class="ge-stat">
          <div class="ge-stat-label">Visibility on Load</div>
          <div class="ge-stat-value">${esc(scrollLabel[ge.scroll_depth] || ge.scroll_depth || '—')}</div>
        </div>
        <div class="ge-stat">
          <div class="ge-stat-label">URL Clicked</div>
          <div class="ge-stat-value ge-query">${ge.landed_url ? esc(ge.landed_url.replace(/^https?:\/\//, '').slice(0, 60)) : '—'}</div>
        </div>
      </div>
      <div class="ge-urls-title">Bajaj URLs found in results</div>
      <div class="ge-urls-list">${urlsHtml}</div>
    </div>`;
}

/* ── Report panel ────────────────────────────────────────────────────────── */

function renderReport(p) {
  const el = qs('#report-render');

  // Prepend Google Entry section if data exists
  let googleHtml = '';
  if (p.googleEntry) {
    const ge = p.googleEntry;
    const rankLabel = ge.rank ? `#${ge.rank} (organic SERP position)` : 'Not found in results';
    const skipLabel = ge.relevance_skip
      ? `⚠ Relevance skip: persona chose #${ge.clicked_bajaj_rank} over top result #${ge.first_bajaj_rank}`
      : '';
    googleHtml = `
      <div class="ge-report-section">
        <h2>🔍 Google Search Entry</h2>
        <table><tbody>
          <tr><td><strong>Query</strong></td><td>"${esc(ge.query || '—')}"</td></tr>
          <tr><td><strong>SERP position (clicked)</strong></td><td>${esc(rankLabel)}</td></tr>
          ${ge.first_bajaj_rank && ge.first_bajaj_rank !== ge.clicked_bajaj_rank ? `<tr><td><strong>Top Bajaj result</strong></td><td>#${ge.first_bajaj_rank} — ${esc((ge.first_bajaj_url||'').replace(/^https?:\/\//,'').slice(0,60))}</td></tr>` : ''}
          ${skipLabel ? `<tr><td><strong>Relevance insight</strong></td><td>${esc(skipLabel)}</td></tr>` : ''}
          <tr><td><strong>Scroll depth</strong></td><td>${esc(ge.scroll_depth || '—')}</td></tr>
          <tr><td><strong>URL clicked</strong></td><td>${esc(ge.landed_url || '—')}</td></tr>
        </tbody></table>
        ${(ge.urls_found || []).length ? `<p><strong>All Bajaj URLs found:</strong> ${ge.urls_found.map(u => esc(u)).join(', ')}</p>` : ''}
      </div>
      <hr>`;
  }

  if (!p.reportMd) {
    el.innerHTML = googleHtml || '<p class="muted">Report not available.</p>';
    return;
  }
  if (window.marked) {
    el.innerHTML = googleHtml + marked.parse(p.reportMd);
  } else {
    el.innerHTML = googleHtml + `<pre>${esc(p.reportMd)}</pre>`;
  }
}

/* ── Design Audit panel ──────────────────────────────────────────────────── */

function renderDesignAudit(p) {
  const el = qs('#design-audit-content');
  if (!el) return;

  if (!p.designAuditScore && !p.designIssues?.length) {
    el.innerHTML = '<p class="muted">No design audit data for this run. Re-run with Evaluation Type set to "Design" or "Both".</p>';
    return;
  }

  const scoreClass = p.designAuditScore >= 7 ? 'high' : p.designAuditScore >= 4 ? 'mid' : 'low';
  const wcagBadge = p.designWcagLevel
    ? `<span class="design-compliance-badge design-compliance-badge--wcag">${esc(p.designWcagLevel)}</span>` : '';
  const dsBadge = p.designDsAdherence
    ? `<span class="design-compliance-badge design-compliance-badge--ds">${esc(p.designDsAdherence)}</span>` : '';

  // TL;DR
  let html = '';
  if (p.designTldr || p.designVerdict) {
    html += `
      <div class="design-tldr">
        <div class="tldr-label">Design TL;DR</div>
        <div class="tldr-text">${esc(p.designTldr || p.designVerdict)}</div>
      </div>`;
  }

  // Score + compliance strip
  html += `
    <div class="design-score-strip">
      <div class="design-score-main score--${scoreClass}">${p.designAuditScore.toFixed(1)}<span>/10</span></div>
      <div class="design-compliance-badges">${wcagBadge}${dsBadge}</div>
    </div>`;

  // Key findings
  if (p.designKeyFindings?.length) {
    html += `
      <div class="design-section">
        <div class="section-title">Key Findings</div>
        <ol class="key-takeaways-list">
          ${p.designKeyFindings.map(f => `<li class="kt-item">${esc(f)}</li>`).join('')}
        </ol>
      </div>`;
  }

  // Dimensions — with expandable per-step panels (mirrors CX dimension pattern)
  if (p.designDimensions?.length) {
    // Build map: dimension name → [{step_number, action, url, score, observation}]
    const designDimStepMap = {};
    (p.designStepEvaluations || []).forEach(se => {
      (se.dimension_scores || []).forEach(ds => {
        if (!ds.dimension || ds.is_na) return;
        const key = ds.dimension;
        if (!designDimStepMap[key]) designDimStepMap[key] = [];
        designDimStepMap[key].push({
          step_number: se.step_number,
          action:      se.action || '',
          url:         se.url   || '',
          score:       ds.score,
          observation: ds.observation || '',
        });
      });
    });

    html += `
      <div class="design-section">
        <div class="section-title">Design Dimensions</div>
        <div class="design-dims-list">
          ${p.designDimensions.map((d, idx) => {
            const steps    = designDimStepMap[d.name] || [];
            const hasSteps = steps.length > 0;
            const rowId    = `dsgn-dim-${idx}`;
            const stepsHtml = steps.map(s => `
              <div class="dim-step-row">
                <div class="dim-step-meta">
                  <span class="dim-step-num">Step ${s.step_number >= 0 ? s.step_number + 1 : 'Home'}</span>
                  ${s.action ? `<span class="dim-step-action">${esc(s.action)}</span>` : ''}
                  <span class="dim-step-score" style="color:${scoreColor(s.score)}">${s.score?.toFixed(1)}/10</span>
                  <div class="dim-step-bar-track">
                    <div class="dim-step-bar-fill" style="width:${(s.score/10)*100}%;background:${scoreGradient(s.score)}"></div>
                  </div>
                </div>
                ${s.observation ? `<p class="dim-step-obs">${esc(s.observation)}</p>` : ''}
                ${s.url ? `<p class="dim-step-url">${esc(s.url.replace(/^https?:\/\//, '').substring(0, 60))}${s.url.length > 60 ? '…' : ''}</p>` : ''}
              </div>`).join('');
            return `
            <div class="ov-dim-row${hasSteps ? ' ov-dim-row--expandable' : ''}" id="${rowId}">
              <div class="ov-dim-header" ${hasSteps ? `onclick="toggleDimExpand('${rowId}')" style="cursor:pointer"` : ''}>
                <span class="ov-dim-name">${esc(d.name)}</span>
                <div class="ov-dim-header-right">
                  <span class="ov-dim-score" style="color:${scoreColor(d.score)}">${d.score?.toFixed(1)}/10</span>
                  ${hasSteps ? `<span class="ov-dim-chevron">▶</span>` : ''}
                </div>
              </div>
              <div class="ov-dim-bar-track">
                <div class="ov-dim-bar-fill" style="width:${(d.score/10)*100}%;background:${scoreGradient(d.score)}"></div>
              </div>
              ${d.rationale ? `<p class="ov-dim-rationale">${esc(d.rationale)}</p>` : ''}
              ${d.violations?.length ? `<p class="design-violations">⚠ ${esc(d.violations.slice(0,2).join(' · '))}</p>` : ''}
              ${hasSteps ? `
              <div class="ov-dim-steps" id="ov-dim-steps-${rowId}">
                <div class="ov-dim-steps-header">Step-by-step evidence (${steps.length} step${steps.length > 1 ? 's' : ''})</div>
                ${stepsHtml}
              </div>` : ''}
            </div>`;
          }).join('')}
        </div>
      </div>`;
  }

  // Issues
  const critIssues = (p.designIssues || []).filter(i => i.severity === 'high');
  const otherIssues = (p.designIssues || []).filter(i => i.severity !== 'high');
  if (critIssues.length) {
    html += `
      <div class="design-section">
        <div class="section-title">🔴 Critical Design Issues</div>
        ${critIssues.map(i => `
          <div class="design-issue-card design-issue-card--high">
            <div class="design-issue-header">
              <span class="fad-sev fad-sev--high">HIGH</span>
              ${i.dimension ? `<span class="design-issue-dim">${esc(i.dimension)}</span>` : ''}
              ${i.wcag_criterion ? `<span class="design-wcag-tag">${esc(i.wcag_criterion)}</span>` : ''}
            </div>
            <p class="design-issue-title">${esc(i.title || i.description || '')}</p>
            ${i.description && i.description !== i.title ? `<p class="design-issue-desc">${esc(i.description)}</p>` : ''}
            ${i.recommendation ? `<p class="design-issue-rec">Fix: ${esc(i.recommendation)}</p>` : ''}
          </div>`).join('')}
      </div>`;
  }
  if (otherIssues.length) {
    html += `
      <div class="design-section">
        <div class="section-title">Medium &amp; Low Design Issues</div>
        ${otherIssues.map(i => `
          <div class="design-issue-card design-issue-card--${i.severity || 'medium'}">
            <div class="design-issue-header">
              <span class="fad-sev fad-sev--${i.severity || 'medium'}">${(i.severity||'MEDIUM').toUpperCase()}</span>
              ${i.dimension ? `<span class="design-issue-dim">${esc(i.dimension)}</span>` : ''}
              ${i.wcag_criterion ? `<span class="design-wcag-tag">${esc(i.wcag_criterion)}</span>` : ''}
            </div>
            <p class="design-issue-title">${esc(i.title || i.description || '')}</p>
            ${i.recommendation ? `<p class="design-issue-rec">Fix: ${esc(i.recommendation)}</p>` : ''}
          </div>`).join('')}
      </div>`;
  }

  // Positives
  if (p.designPositives?.length) {
    html += `
      <div class="design-section">
        <div class="section-title">✨ Design Strengths</div>
        <ul class="positives-list">
          ${p.designPositives.map(pos => `<li>${esc(pos)}</li>`).join('')}
        </ul>
      </div>`;
  }

  el.innerHTML = html || '<p class="muted">No design audit details available.</p>';
}

/* ── Lightbox ────────────────────────────────────────────────────────────── */

window.toggleDimExpand = function(rowId) {
  const row   = document.getElementById(rowId);
  if (!row) return;
  const isOpen = row.classList.toggle('ov-dim-row--open');
  const chevron = row.querySelector('.ov-dim-chevron');
  if (chevron) chevron.style.transform = isOpen ? 'rotate(90deg)' : 'rotate(0deg)';
};

window.openLightbox = function(src, caption) {
  STATE.lbImages = STATE.activePersona?.screenshots || [{ src, caption }];
  STATE.lbIndex  = STATE.lbImages.findIndex(x => x.src === src) ?? 0;
  if (STATE.lbIndex < 0) STATE.lbIndex = 0;
  updateLightbox();
  qs('#lightbox').classList.add('open');
};

function closeLightbox() {
  qs('#lightbox').classList.remove('open');
}

function stepLightbox(dir) {
  STATE.lbIndex = Math.max(0, Math.min(STATE.lbImages.length - 1, STATE.lbIndex + dir));
  updateLightbox();
}

function updateLightbox() {
  const s = STATE.lbImages[STATE.lbIndex] || {};
  qs('#lightbox-img').src           = s.src || '';
  qs('#lightbox-caption').textContent = s.caption || '';
}

/* ══════════════════════════════════════════════════════════════════════════════
   NEW AUDIT FORM
   ══════════════════════════════════════════════════════════════════════════════ */

async function loadPersonaFiles(selectSel) {
  const sel = qs(selectSel);
  if (!sel) return;

  if (API_MODE) {
    const data = await fetchJSON(`${CFG.api}/personas`);
    const files = data?.files || [];
    sel.innerHTML = files.map(f =>
      `<option value="${esc(f.path)}">${esc(f.name)} (${f.size_kb}kb)</option>`
    ).join('');
    if (!files.length) sel.innerHTML = '<option value="">No persona files found</option>';
  } else {
    sel.innerHTML = '<option value="personas/bajaj_personas.md">bajaj_personas.md (default)</option>';
  }
}

async function parsePersonaSource(kind) {
  if (!API_MODE) return;
  const isApp = kind === 'app';
  const fileInput = qs(isApp ? '#af-personas-file' : '#f-personas-file');
  const selInput = qs(isApp ? '#af-personas-select' : '#f-personas-select');
  const picker = qs(isApp ? '#app-persona-picker' : '#persona-picker');
  const list = qs(isApp ? '#app-persona-option-list' : '#persona-option-list');
  const count = qs(isApp ? '#app-persona-picker-count' : '#persona-picker-count');
  if (!picker || !list) return;

  const fd = new FormData();
  if (fileInput?.files?.[0]) {
    fd.append('personas_file', fileInput.files[0]);
  } else if (selInput?.value) {
    fd.append('personas_path', selInput.value);
  } else {
    picker.style.display = 'none';
    return;
  }

  list.innerHTML = '<div class="persona-option-muted">Parsing personas...</div>';
  picker.style.display = 'block';
  const res = await fetch(`${CFG.api}/personas/parse`, { method: 'POST', body: fd });
  const data = await res.json();
  if (!res.ok) {
    list.innerHTML = `<div class="persona-option-muted">${esc(data.error || 'Could not parse persona file')}</div>`;
    return;
  }

  const personas = data.personas || [];
  if (isApp) {
    STATE.appPersonaPath = data.path || '';
    STATE.appPersonaOptions = personas;
  } else {
    STATE.webPersonaPath = data.path || '';
    STATE.webPersonaOptions = personas;
  }
  list.innerHTML = personas.map(p => `
    <label class="persona-option">
      <input type="checkbox" value="${esc(p.slug)}" checked />
      <span>
        <strong>${esc(p.name)}</strong>
        <small>${esc(p.product_tag || 'General')} · ${esc((p.intent || '').slice(0, 120))}</small>
      </span>
    </label>
  `).join('');
  bindPersonaPicker(kind);
  updatePersonaPickerCount(kind);
  if (count) count.textContent = `${personas.length} selected`;
}

function bindPersonaPicker(kind) {
  const isApp = kind === 'app';
  const all = qs(isApp ? '#app-persona-select-all' : '#persona-select-all');
  const list = qs(isApp ? '#app-persona-option-list' : '#persona-option-list');
  if (!all || !list) return;
  all.checked = true;
  all.onchange = () => {
    qsa('input[type="checkbox"]', list).forEach(cb => { cb.checked = all.checked; });
    updatePersonaPickerCount(kind);
  };
  qsa('input[type="checkbox"]', list).forEach(cb => {
    cb.onchange = () => updatePersonaPickerCount(kind);
  });
}

function getSelectedPersonas(kind) {
  const isApp = kind === 'app';
  const list = qs(isApp ? '#app-persona-option-list' : '#persona-option-list');
  if (!list) return [];
  return qsa('input[type="checkbox"]:checked', list).map(cb => cb.value);
}

function updatePersonaPickerCount(kind) {
  const isApp = kind === 'app';
  const list = qs(isApp ? '#app-persona-option-list' : '#persona-option-list');
  const count = qs(isApp ? '#app-persona-picker-count' : '#persona-picker-count');
  const all = qs(isApp ? '#app-persona-select-all' : '#persona-select-all');
  if (!list || !count) return;
  const boxes = qsa('input[type="checkbox"]', list);
  const selected = boxes.filter(cb => cb.checked).length;
  count.textContent = `${selected}/${boxes.length} selected`;
  if (all) all.checked = boxes.length > 0 && selected === boxes.length;
}

/* ══════════════════════════════════════════════════════════════════════════════
   INLINE PERSONA BUILDER
   ══════════════════════════════════════════════════════════════════════════════ */

let _inlinePersonaCount = 0;

function _buildPersonaCardHTML(idx) {
  return `
    <div class="inline-persona-card" id="ipc-${idx}">
      <div class="ipc-header">
        <span class="ipc-number">Persona ${idx + 1}</span>
        ${idx > 0 ? `<button type="button" class="btn btn--danger btn--xs ipc-remove-btn" onclick="removeInlinePersona(${idx})">Remove</button>` : ''}
      </div>
      <div class="form-row form-row--2">
        <div class="form-group">
          <label class="form-label">Name <span class="form-required">*</span></label>
          <input type="text" class="form-input ipc-name" placeholder="e.g. Priya Sharma" />
        </div>
        <div class="form-group">
          <label class="form-label">Occupation / Role</label>
          <input type="text" class="form-input ipc-occupation" placeholder="e.g. Salaried IT professional" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Goal / Intent <span class="form-required">*</span></label>
        <input type="text" class="form-input ipc-intent" placeholder="e.g. Looking for a personal loan to fund home renovation" />
      </div>
      <div class="form-row form-row--3">
        <div class="form-group">
          <label class="form-label">Age</label>
          <input type="number" class="form-input ipc-age" placeholder="32" min="18" max="75" />
        </div>
        <div class="form-group">
          <label class="form-label">Location</label>
          <input type="text" class="form-input ipc-location" placeholder="e.g. Mumbai" />
        </div>
        <div class="form-group">
          <label class="form-label">Financial Literacy</label>
          <select class="form-input ipc-literacy">
            <option value="">Select…</option>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
          </select>
        </div>
      </div>
      <div class="form-row form-row--2">
        <div class="form-group">
          <label class="form-label">Digital Comfort</label>
          <select class="form-input ipc-digital">
            <option value="">Select…</option>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Urgency / Need State</label>
          <input type="text" class="form-input ipc-urgency" placeholder="e.g. Needs funds within 2 weeks" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Behavioural Notes / Context</label>
        <input type="text" class="form-input ipc-behaviour" placeholder="e.g. Compares options carefully, reads fine print" />
      </div>
    </div>`;
}

function addInlinePersona() {
  const list = qs('#inline-personas-list');
  if (!list) return;
  const idx = _inlinePersonaCount++;
  const div = document.createElement('div');
  div.innerHTML = _buildPersonaCardHTML(idx);
  list.appendChild(div.firstElementChild);
}

window.removeInlinePersona = function(idx) {
  const card = qs(`#ipc-${idx}`);
  if (card) card.remove();
};

function getInlinePersonas() {
  return qsa('.inline-persona-card').map(card => ({
    name:               (card.querySelector('.ipc-name')?.value       || '').trim(),
    intent:             (card.querySelector('.ipc-intent')?.value     || '').trim(),
    occupation:         (card.querySelector('.ipc-occupation')?.value || '').trim(),
    age:                (card.querySelector('.ipc-age')?.value        || '').trim(),
    location:           (card.querySelector('.ipc-location')?.value   || '').trim(),
    financial_literacy: (card.querySelector('.ipc-literacy')?.value   || '').trim(),
    digital_proficiency:(card.querySelector('.ipc-digital')?.value    || '').trim(),
    behaviour:          (card.querySelector('.ipc-behaviour')?.value  || '').trim() ||
                        (card.querySelector('.ipc-urgency')?.value    || '').trim(),
  })).filter(p => p.name && p.intent);
}

function isInlineMode() {
  return qs('#web-inline-panel')?.style.display !== 'none';
}

function bindAuditFormEvents() {
  // Auth mode toggle
  qsa('input[name="auth_mode"]', qs('#audit-form')).forEach(radio => {
    radio.addEventListener('change', () => {
      const loggedIn = radio.value === 'logged_in' && radio.checked;
      qs('#login-fields').style.display = loggedIn ? 'block' : 'none';
      qs('#auth-card-out').classList.toggle('auth-card--active', !loggedIn);
      qs('#auth-card-in').classList.toggle('auth-card--active',   loggedIn);
    });
  });

  // Evaluation type toggle
  qsa('input[name="eval_type"]', qs('#audit-form')).forEach(radio => {
    radio.addEventListener('change', () => {
      qs('#eval-card-both').classList.toggle('auth-card--active', radio.value === 'both' && radio.checked);
      qs('#eval-card-cx').classList.toggle('auth-card--active',   radio.value === 'cx'   && radio.checked);
      qs('#eval-card-design').classList.toggle('auth-card--active', radio.value === 'design' && radio.checked);
    });
  });

  // Starting point toggle
  qsa('input[name="start_from"]', qs('#audit-form')).forEach(radio => {
    radio.addEventListener('change', () => {
      const isGoogle = radio.value === 'google' && radio.checked;
      qs('#start-card-homepage').classList.toggle('auth-card--active', !isGoogle);
      qs('#start-card-google').classList.toggle('auth-card--active',    isGoogle);
    });
  });

  // Advanced toggle
  qs('#toggle-advanced').addEventListener('click', () => {
    const fields = qs('#advanced-fields');
    const hidden = fields.style.display === 'none';
    fields.style.display = hidden ? 'block' : 'none';
    qs('#toggle-advanced').textContent = hidden ? 'Hide' : 'Show';
  });

  // Persona mode toggle (file vs inline)
  qs('#web-mode-btn-file')?.addEventListener('click', () => {
    qs('#web-file-panel').style.display   = 'block';
    qs('#web-inline-panel').style.display = 'none';
    qs('#web-mode-btn-file').classList.add('persona-mode-btn--active');
    qs('#web-mode-btn-inline').classList.remove('persona-mode-btn--active');
  });
  qs('#web-mode-btn-inline')?.addEventListener('click', () => {
    qs('#web-file-panel').style.display   = 'none';
    qs('#web-inline-panel').style.display = 'block';
    qs('#web-mode-btn-inline').classList.add('persona-mode-btn--active');
    qs('#web-mode-btn-file').classList.remove('persona-mode-btn--active');
    // Seed one empty card if none exist yet
    if (qsa('.inline-persona-card').length === 0) addInlinePersona();
  });

  // Add another persona button
  qs('#inline-add-persona-btn')?.addEventListener('click', addInlinePersona);

  // File upload label
  qs('#f-personas-file').addEventListener('change', e => {
    const file = e.target.files?.[0];
    qs('#file-upload-label').querySelector('span').textContent =
      file ? file.name : 'Drop file or click to browse';
    if (file) qs('#f-personas-select').selectedIndex = -1;
    parsePersonaSource('web');
  });

  qs('#f-personas-select').addEventListener('change', () => parsePersonaSource('web'));

  // Form submit
  qs('#audit-form').addEventListener('submit', async e => {
    e.preventDefault();
    await submitAudit();
  });

  qs('#cancel-run-btn').addEventListener('click', async () => {
    if (!STATE.activeRunId) return;
    if (!API_MODE) return;
    await fetch(`${CFG.api}/runs/${STATE.activeRunId}/cancel`, { method: 'POST' });
    stopPolling();
    qs('#audit-running-panel').style.display = 'none';
    qs('#audit-form').style.display = 'block';
    showToast('Audit cancelled', 'info');
  });
}

async function submitAudit() {
  if (!API_MODE) {
    showToast('Start the Flask server (python server.py) to launch audits from the web UI.', 'error');
    return;
  }

  const form     = qs('#audit-form');
  const formData = new FormData(form);
  if (formData.get('auth_mode') === 'logged_in' && !String(formData.get('login_username') || '').trim()) {
    showToast('Enter a mobile number for logged-in audits.', 'error');
    return;
  }

  // ── Inline persona mode: validate & convert to temp .md file ────────────────
  if (isInlineMode()) {
    const inlinePersonas = getInlinePersonas();
    if (!inlinePersonas.length) {
      showToast('Add at least one persona with a Name and Goal/Intent.', 'error');
      return;
    }
    qs('#submit-audit-btn').disabled = true;
    qs('#submit-audit-btn').textContent = 'Saving personas…';
    try {
      const cr = await fetch(`${CFG.api}/personas/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ personas: inlinePersonas }),
      });
      const cd = await cr.json();
      if (!cr.ok) throw new Error(cd.error || 'Could not save persona data');
      formData.set('personas_path', cd.path);
      formData.delete('personas_file');
    } catch (err) {
      showToast(`Persona save failed: ${err.message}`, 'error');
      qs('#submit-audit-btn').disabled = false;
      qs('#submit-audit-btn').innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg> Launch Audit`;
      return;
    }
  } else {
    // ── File mode: validate persona selection ──────────────────────────────────
    const fileInput = qs('#f-personas-file');
    const selInput  = qs('#f-personas-select');
    if (!fileInput.files?.[0] && !selInput?.value && !STATE.webPersonaPath) {
      showToast('Select or upload a persona file, or switch to "Type Persona Details".', 'error');
      return;
    }
    const selected = getSelectedPersonas('web');
    if (qs('#persona-picker')?.style.display !== 'none' && !selected.length) {
      showToast('Select at least one persona to run.', 'error');
      return;
    }
    if (selected.length) formData.set('selected_personas', JSON.stringify(selected));
    if (STATE.webPersonaPath) {
      formData.set('personas_path', STATE.webPersonaPath);
      formData.delete('personas_file');
    } else if (!fileInput.files?.[0] && selInput?.value) {
      formData.set('personas_path', selInput.value);
      formData.delete('personas_file');
    }
  }

  qs('#submit-audit-btn').disabled = true;
  qs('#submit-audit-btn').textContent = 'Launching…';

  try {
    const res  = await fetch(`${CFG.api}/audit/start`, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to start audit');

    STATE.activeRunId = data.run_id;
    form.style.display = 'none';
    qs('#audit-running-panel').style.display = 'flex';
    qs('#running-meta').textContent = `Run ID: ${data.run_id}`;
    qs('#running-log').textContent = 'Audit engine starting... Chrome should open shortly.';
    showToast('Audit started!', 'success');
    startPolling(data.run_id);
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    qs('#submit-audit-btn').disabled = false;
    qs('#submit-audit-btn').innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg> Launch Audit`;
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   POLLING — live status during a running audit
   ══════════════════════════════════════════════════════════════════════════════ */

function startPolling(runId) {
  stopPolling();
  STATE.pollTimer = setInterval(() => pollRunStatus(runId), 5000);
}

function stopPolling() {
  if (STATE.pollTimer) {
    clearInterval(STATE.pollTimer);
    STATE.pollTimer = null;
  }
}

async function pollRunStatus(runId) {
  const data = await fetchJSON(`${CFG.api}/runs/${runId}/status`);
  if (!data) {
    // 404 or network error — run no longer exists, stop polling
    stopPolling();
    qs('#audit-running-panel').style.display = 'none';
    qs('#audit-form').style.display = 'block';
    return;
  }

  const slugs = data.manifest_slugs || [];
  if (data.log_tail) {
    const logEl = qs('#running-log');
    if (logEl) {
      logEl.textContent = data.log_tail;
      logEl.scrollTop = logEl.scrollHeight;
    }
  }
  if (data.error) {
    const logEl = qs('#running-log');
    if (logEl && !data.log_tail) logEl.textContent = data.error;
  }
  if (slugs.length) {
    qs('#running-desc').textContent = `${slugs.length} persona(s) audited so far…`;
  } else if (data.status === 'running') {
    qs('#running-desc').textContent = 'Audit engine is running. Watch Chrome and the log below.';
  }

  if (data.status === 'complete' || data.status === 'failed') {
    stopPolling();
    const success = data.status === 'complete';
    showToast(
      success ? 'Audit complete! Loading results…' : 'Audit finished with errors.',
      success ? 'success' : 'error'
    );

    if (success && slugs.length) {
      const archivedSlugs = data.archived_slugs?.length ? data.archived_slugs : [];
      const useArchive = !!data.archived_reports_path && archivedSlugs.length > 0;
      const loadSlugs = useArchive ? archivedSlugs : slugs;
      const results = await Promise.all(loadSlugs.map(s => {
        if (useArchive) {
          return loadPersonaData(
            s,
            `${BASE}/${data.archived_reports_path}/${s}`,
            {
              runId: data.run_id,
              createdAt: data.created_at,
              archived: true,
              slugKey: `${data.run_id}__${s}`,
              screenshotsBase: data.archived_screenshots_path ? `${BASE}/${data.archived_screenshots_path}` : undefined,
              videosBase: data.archived_videos_path ? `${BASE}/${data.archived_videos_path}` : undefined,
            }
          );
        }
        return data.audit_type === 'app'
          ? loadPersonaData(s, `${CFG.reportsBase}/mobile/${s}`, { runId: data.run_id, createdAt: data.created_at })
          : loadPersonaData(s, null, { runId: data.run_id, createdAt: data.created_at });
      }));
      const newPersonas = results.filter(Boolean);
      for (const p of newPersonas) {
        const key = personaRunKey(p);
        const idx = STATE.allPersonas.findIndex(x => personaRunKey(x) === key);
        if (idx >= 0) STATE.allPersonas[idx] = p;
        else STATE.allPersonas.unshift(p);
      }
      updateStats();
      applyFilterSort();
      updateRunBadge();
    }

    // Show dashboard after short delay — hide the running panel
    setTimeout(() => {
      qs('#audit-running-panel').style.display     = 'none';
      qs('#audit-form').style.display              = 'block';
      showPage('dashboard');
    }, 1500);
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   FAILURE NOTES
   ══════════════════════════════════════════════════════════════════════════════ */

function renderFailureNotes(p) {
  const el = qs('#failure-notes');
  if (!el) return;
  const failedSteps = (p.steps || []).filter(s => !s.success);
  const recentFailures = failedSteps.slice(-5);
  const failedTargets = (p.failedActions || []).slice(-5);
  const technicalFailure = isTechnicalFailure(p);
  el.innerHTML = `
    <div class="failure-note-card">
      <div class="section-title">${technicalFailure ? 'Why This Run Failed' : 'Journey Outcome'}</div>
      <p>${esc(failureReasonLabel(p))}</p>
    </div>
    <div class="failure-note-card">
      <div class="section-title">${technicalFailure ? 'Developer Feedback' : 'CX Interpretation'}</div>
      <p>${esc(buildDeveloperFailureNote(p, recentFailures, failedTargets))}</p>
    </div>
    ${technicalFailure ? `<div class="failure-note-card">
      <div class="section-title">Recent Failed Actions</div>
      ${recentFailures.length ? recentFailures.map(s => `
        <div class="failure-action-row">
          <strong>Step ${s.step_number + 1}: ${esc(s.action || 'action')}</strong>
          <span>${esc(s.target || s.error || 'No target recorded')}</span>
        </div>`).join('') : '<p class="muted">No failed action rows were recorded.</p>'}
    </div>` : ''}
  `;
}

function buildDeveloperFailureNote(p, failedSteps, failedTargets) {
  const reason = (p.terminalReason || '').toLowerCase();
  if (!isTechnicalFailure(p)) {
    if (reason.includes('valid_journey_abandoned') || reason.includes('same_page_scrolling')) {
      return 'Treat this as a valid customer experience signal: the journey reached relevant content, but the visible path did not give enough clarity or confidence for the customer to continue.';
    }
    if (reason.includes('max')) {
      return 'Treat this as a valid incomplete journey unless the screenshots show browser or Playwright malfunction. Review the detailed timeline for CX friction, not just action failure.';
    }
    return 'The goal was not completed, but the run is still useful CX evidence. Use the journey timeline, screenshots, and friction points to understand what blocked progress.';
  }
  if (reason.includes('loop')) {
    return 'The agent could not progress after repeated action or navigation cycles. Review the last repeated target/URL and add a more specific escape strategy, selector, or prompt rule for this page pattern.';
  }
  if (reason.includes('max')) {
    return 'The run used all available steps before reaching the goal. Consider increasing max steps for this persona or improving navigation strategy for the product journey.';
  }
  if (failedSteps.length || failedTargets.length) {
    const last = failedSteps[failedSteps.length - 1] || {};
    return `The latest failure was around "${last.target || last.error || 'an unidentified element'}". Review selector coverage and whether the page displayed overlays, bot blocks, or delayed UI.`;
  }
  return 'The run ended unsuccessfully without a specific failed action. Review the journey timeline and screenshots for the last stable page state.';
}

async function deletePersonaRun(slug, auditType, runId = '') {
  if (!slug) return;
  if (!confirm('Permanently delete this persona run?')) return;

  // Helper: remove exactly THIS run tile from state and re-render.
  // Uses the same key as personaRunKey() so the match is unambiguous —
  // deleting run-003 of Vikram never touches run-001…run-005 of the same persona.
  const _runKeyToDelete = _makeRunKey(slug, auditType, runId);
  function _removeFromState() {
    STATE.allPersonas = STATE.allPersonas.filter(
      p => personaRunKey(p) !== _runKeyToDelete
    );
    renderProductDropdown?.();
    applyFilterSort();
    updateRunBadge?.();
  }

  if (!API_MODE) {
    // FILE_MODE — no server. Persist the deletion in localStorage so it
    // survives page refreshes. The key matches what personaRunKey() produces.
    _addDeletedKey(_makeRunKey(slug, auditType, runId));
    _removeFromState();
    showToast('Persona run deleted', 'success');
    return;
  }

  // API_MODE — call the server
  const params = new URLSearchParams({ audit_type: auditType });
  if (runId) params.set('run_id', runId);
  const res = await fetch(`${CFG.api}/persona-runs/${encodeURIComponent(slug)}?${params}`, { method: 'DELETE' });
  if (res.ok) {
    // Belt-and-suspenders: mirror into localStorage so the tile stays gone on
    // refresh even if the server hasn't fully updated manifest.json yet.
    _addDeletedKey(_makeRunKey(slug, auditType, runId));
    _removeFromState();
    showToast('Persona run deleted', 'success');
  } else {
    showToast('Could not delete persona run', 'error');
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   ISSUES LOG PAGE
   ══════════════════════════════════════════════════════════════════════════════ */

function bindIssuesEvents() {
  const applyBtn = qs('#if-apply-btn');
  const resetBtn = qs('#if-reset-btn');
  const sortSel  = qs('#if-sort');
  if (applyBtn) applyBtn.addEventListener('click', loadIssues);
  if (sortSel)  sortSel.addEventListener('change', loadIssues);
  if (resetBtn) resetBtn.addEventListener('click', () => {
    ['#if-sort','#if-product','#if-priority','#if-category','#if-status'].forEach(s => {
      const el = qs(s);
      if (el) el.value = s === '#if-sort' ? 'priority' : '';
    });
    loadIssues();
  });
}

async function loadIssues() {
  const listEl    = qs('#issues-list');
  const summaryEl = qs('#issues-summary');
  if (!listEl) return;
  listEl.innerHTML = '<p class="muted" style="padding:20px 0">Loading…</p>';

  if (!API_MODE) {
    listEl.innerHTML = '<p class="muted" style="padding:20px 0">Issues log requires the Flask server (python server.py)</p>';
    return;
  }

  const params = new URLSearchParams();
  const sort   = (qs('#if-sort')      || {}).value || 'priority';
  const prod   = (qs('#if-product')   || {}).value || '';
  const pri    = (qs('#if-priority')  || {}).value || '';
  const cat    = (qs('#if-category')  || {}).value || '';
  const stat   = (qs('#if-status')    || {}).value || '';
  params.set('sort', sort);
  if (prod) params.set('product',  prod);
  if (pri)  params.set('priority', pri);
  if (stat) params.set('status',   stat);

  const data   = await fetchJSON(`${CFG.api}/issues?${params}`);
  let issues = data?.issues || [];
  if (cat) issues = issues.filter(i => (i.issue_category || 'cx') === cat);

  // Populate product dropdown
  const prodSel = qs('#if-product');
  if (prodSel && data?.products) {
    const cur = prodSel.value;
    prodSel.innerHTML = '<option value="">All Products</option>' +
      (data.products).map(p => `<option value="${esc(p)}" ${p===cur?'selected':''}>${esc(p)}</option>`).join('');
  }

  // Summary strip
  if (summaryEl) {
    const open     = issues.filter(i => i.status === 'open').length;
    const resolved = issues.filter(i => i.status === 'resolved').length;
    const p1 = issues.filter(i => i.priority === 'P1' && i.status === 'open').length;
    summaryEl.innerHTML = `
      <div class="issues-stats">
        <div class="istat istat--open"><span class="istat-val">${open}</span><span class="istat-lbl">Open</span></div>
        <div class="istat istat--p1"><span class="istat-val">${p1}</span><span class="istat-lbl">Critical (P1)</span></div>
        <div class="istat istat--resolved"><span class="istat-val">${resolved}</span><span class="istat-lbl">Resolved</span></div>
        <div class="istat"><span class="istat-val">${issues.length}</span><span class="istat-lbl">Total Shown</span></div>
      </div>`;
  }

  if (!issues.length) {
    listEl.innerHTML = '<p class="muted" style="padding:20px 0">No issues found. Run an audit to auto-generate issues from friction points.</p>';
    return;
  }

  listEl.innerHTML = issues.map(buildIssueCardHTML).join('');
}

function buildIssueCardHTML(iss) {
  const priCls  = (iss.priority || 'p3').toLowerCase();
  const statCls = iss.status === 'resolved' ? 'resolved' : 'open';
  const date    = iss.created_at ? formatDateTime(iss.created_at) : '—';

  // Subtitle: concise summary of issue + recommendation, no persona names
  const subtitleParts = [];
  if (iss.description && iss.description !== iss.title) subtitleParts.push(iss.description);
  if (iss.recommendation) subtitleParts.push(`Recommendation: ${iss.recommendation}`);
  const subtitle = subtitleParts.join(' · ');

  const resolvedBtn = iss.status === 'open'
    ? `<button class="btn btn--xs issue-resolve-btn" onclick="resolveIssue('${esc(iss.id)}')">Mark Resolved</button>`
    : `<button class="btn btn--xs issue-reopen-btn" onclick="reopenIssue('${esc(iss.id)}')">Re-open</button>`;
  const personaLink = iss.persona_slug
    ? `<button class="issue-persona-link" onclick="openModal('${esc(iss.persona_slug)}')">${esc(iss.persona_name || iss.persona_slug)}</button>`
    : '';

  return `
    <div class="issue-card issue-card--${priCls} issue-card--${statCls}" id="issue-${esc(iss.id)}">
      <div class="issue-left-bar"></div>
      <div class="issue-body">
        <div class="issue-header">
          <span class="issue-pri issue-pri--${priCls}">${esc(iss.priority || 'P3')}</span>
          <span class="issue-product">${esc(iss.product_tag || 'General')}</span>
          <span class="issue-category-badge issue-category-badge--${esc(iss.issue_category || 'cx')}">${{cx:'CX',design:'Design',accessibility:'A11y',content:'Content'}[iss.issue_category] || 'CX'}</span>
          <span class="issue-status issue-status--${statCls}">${iss.status === 'resolved' ? '✓ Resolved' : '● Open'}</span>
          <span class="issue-date">${date}</span>
        </div>
        <p class="issue-title">${esc(iss.title || '')}</p>
        ${subtitle ? `<p class="issue-subtitle">${esc(subtitle)}</p>` : ''}
        ${iss.location ? `<p class="issue-location">Location: ${esc(iss.location)}</p>` : ''}
        ${iss.impact   ? `<p class="issue-impact">Impact: ${esc(iss.impact)}</p>` : ''}
        <div class="issue-footer">
          ${personaLink}
          ${resolvedBtn}
          <button class="btn btn--danger btn--xs" onclick="deleteIssue('${esc(iss.id)}')">Delete</button>
        </div>
      </div>
    </div>`;
}

window.resolveIssue = async function(id) {
  if (!API_MODE) return;
  const res = await fetch(`${CFG.api}/issues/${id}`, {
    method: 'PATCH',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({status: 'resolved'}),
  });
  if (res.ok) { showToast('Issue marked resolved', 'success'); loadIssues(); }
};

window.reopenIssue = async function(id) {
  if (!API_MODE) return;
  const res = await fetch(`${CFG.api}/issues/${id}`, {
    method: 'PATCH',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({status: 'open'}),
  });
  if (res.ok) { showToast('Issue re-opened', 'info'); loadIssues(); }
};

window.deleteIssue = async function(id) {
  if (!API_MODE) return;
  if (!confirm('Permanently delete this issue tile? This cannot be undone.')) return;
  const res = await fetch(`${CFG.api}/issues/${id}`, { method: 'DELETE' });
  if (res.ok) {
    // Animate out then reload
    const card = qs(`#issue-${id}`);
    if (card) { card.style.opacity = '0'; card.style.transform = 'translateX(20px)'; card.style.transition = 'opacity .25s, transform .25s'; }
    setTimeout(loadIssues, 280);
    showToast('Issue deleted', 'info');
  } else {
    showToast('Could not delete issue', 'error');
  }
};

/* ══════════════════════════════════════════════════════════════════════════════
   UTILITIES
   ══════════════════════════════════════════════════════════════════════════════ */

function scoreColor(s) {
  if (s >= 7) return 'var(--score-high)';
  if (s >= 4) return 'var(--score-mid)';
  return 'var(--score-low)';
}

function scoreGradient(s) {
  if (s >= 7) return 'linear-gradient(90deg,#10B981,#34D399)';
  if (s >= 4) return 'linear-gradient(90deg,#F59E0B,#FBBF24)';
  return 'linear-gradient(90deg,#EF4444,#F87171)';
}

function esc(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

function showLoading() {
  qs('#loading-overlay').style.display = 'flex';
}
function hideLoading() {
  qs('#loading-overlay').style.display = 'none';
}
function setLoadingStatus(msg) {
  qs('#loading-status').textContent = msg;
}

function showToast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast toast--${type}`;
  el.textContent = msg;
  qs('#toast-container').appendChild(el);
  setTimeout(() => el.classList.add('toast--visible'), 10);
  setTimeout(() => {
    el.classList.remove('toast--visible');
    setTimeout(() => el.remove(), 400);
  }, 4000);
}

/* ══════════════════════════════════════════════════════════════════════════════
   BOOT
   ══════════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', init);
