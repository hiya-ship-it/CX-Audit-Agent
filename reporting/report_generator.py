"""
Report Generator  (BRD §5.1, §5.5)
------------------------------------
Produces:
  1. Per-persona journey_log.json  →  reports/{slug}/journey_log.json
  2. Per-persona Markdown report   →  reports/{slug}/report.md
  3. Master Markdown report        →  reports/master_report.md
  4. manifest.json                 →  reports/manifest.json
  5. session_index.json            →  reports/session_index.json
  6. Run archive                   →  reports/run_archive/{run_id}/
"""
from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import config

log = logging.getLogger(__name__)
from agents.journey import JourneyResult
from evaluation.cx_evaluator import CXAuditResult
from evaluation.design_evaluator import DesignAuditResult
from evaluation.content_analyzer import ContentAnalysisResult


# ── Helpers ───────────────────────────────────────────────────────────────────

def _score_bar(score: float, width: int = 20) -> str:
    filled = round((score / 10) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar}  {score:.1f}/10"


def _score_label(score: float) -> str:
    if score >= 8.0:   return "Strong"
    elif score >= 6.0: return "Moderate"
    elif score >= 4.0: return "Weak"
    else:              return "Critical"


def _severity_icon(s: str) -> str:
    return {"critical": "🔴", "major": "🟡", "minor": "🟢"}.get(s.lower(), "⚪")


# ── Per-persona report ────────────────────────────────────────────────────────

def generate_persona_report(
    journey:      JourneyResult,
    cx_audit:     Optional[CXAuditResult],
    design_audit: Optional[DesignAuditResult],
    content:      Optional[ContentAnalysisResult],
    eval_type:    str = "both",
) -> Path:
    slug    = journey.persona.slug
    out_dir = config.REPORTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write journey_log.json
    log_data = {
        "eval_type": eval_type,
        "journey": {
            **journey.memory.to_dict(),
            "persona_slug":  slug,
            "duration_secs": round(journey.duration_secs, 1),
            "product":       (journey.persona.raw_attributes or {}).get("product", ""),
            "model":         config.OPENAI_MODEL,
        },
        "cx_audit":         cx_audit.to_dict()     if cx_audit     else None,
        "design_audit":     design_audit.to_dict() if design_audit else None,
        "content_analysis": content.to_dict()      if content      else None,
    }
    log_path = out_dir / "journey_log.json"
    log_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Write Markdown report
    lines: list[str] = []
    p = journey.persona

    lines += [
        f"# CX Audit — {p.name}",
        f"> **Intent:** {p.intent}",
        f"> **Terminal:** {journey.terminal_reason}  |  "
        f"**Steps:** {journey.memory.step_count}  |  "
        f"**Duration:** {journey.duration_secs:.0f}s",
        "",
    ]

    # ── CX section ────────────────────────────────────────────────────────────
    if cx_audit:
        lines += [
            "---",
            "## CX Audit",
            f"**Overall CX Score:** {_score_bar(cx_audit.overall_cx_score)}  "
            f"({_score_label(cx_audit.overall_cx_score)})",
            "",
        ]

        # Persona emotional narrative
        if cx_audit.persona_emotional_narrative:
            lines += ["### Persona Emotional Narrative", ""]
            lines.append(cx_audit.persona_emotional_narrative)
            lines.append("")

        # Emotional journey arc
        if cx_audit.emotional_journey:
            lines += ["### Emotional Journey Arc", ""]
            for stage in cx_audit.emotional_journey:
                lines.append(f"- **{stage.stage}** — {stage.emotion} *(trigger: {stage.trigger})*")
            lines.append("")

        # Dimension scores table
        if cx_audit.dimension_scores:
            lines += ["### Dimension Scores", ""]
            lines.append("| Dimension | Score | Status |")
            lines.append("|-----------|-------|--------|")
            for d in cx_audit.dimension_scores:
                status = "N/A" if d.is_na else _score_label(d.score)
                score_str = "—" if d.is_na else f"{d.score:.1f}/10"
                lines.append(f"| {d.dimension_name} | {score_str} | {status} |")
            lines.append("")

        # Objective scores
        if cx_audit.objective_scores:
            lines += ["### Objective Metrics", ""]
            for k, v in cx_audit.objective_scores.items():
                label = k.replace("_", " ").title()
                lines.append(f"- **{label}:** {v}")
            lines.append("")

        # Issues
        if cx_audit.issues:
            lines += ["### Issues", ""]
            for issue in cx_audit.issues:
                sev = issue.get("severity", "minor")
                dim = issue.get("dimension", "")
                desc = issue.get("description", "")
                rec  = issue.get("recommendation", "")
                lines.append(f"{_severity_icon(sev)} **[{sev.upper()}]** *{dim}*")
                lines.append(f"  {desc}")
                if rec:
                    lines.append(f"  → {rec}")
                lines.append("")

        # Delight points
        if cx_audit.delight_points:
            lines += ["### Delight Points", ""]
            for dp in cx_audit.delight_points:
                lines.append(f"✨ {dp}")
            lines.append("")

    # ── Design section ────────────────────────────────────────────────────────
    if design_audit:
        lines += [
            "---",
            "## Design Audit",
            f"**Overall Design Score:** {_score_bar(design_audit.overall_design_score)}  "
            f"({_score_label(design_audit.overall_design_score)})",
            "",
        ]

        if design_audit.brand_alignment:
            lines += ["### Brand Alignment", ""]
            lines.append(design_audit.brand_alignment)
            lines.append("")

        if design_audit.dimension_scores:
            lines += ["### Design Dimension Scores", ""]
            lines.append("| Dimension | Score | Status |")
            lines.append("|-----------|-------|--------|")
            for d in design_audit.dimension_scores:
                status = "N/A" if d.is_na else _score_label(d.score)
                score_str = "—" if d.is_na else f"{d.score:.1f}/10"
                lines.append(f"| {d.dimension_name} | {score_str} | {status} |")
            lines.append("")

        if design_audit.critical_issues:
            lines += ["### Design Issues", ""]
            for issue in design_audit.critical_issues:
                sev = issue.get("severity", "minor")
                desc = issue.get("description", "")
                rec  = issue.get("recommendation", "")
                lines.append(f"{_severity_icon(sev)} **[{sev.upper()}]** {desc}")
                if rec:
                    lines.append(f"  → {rec}")
                lines.append("")

        if design_audit.positive_findings:
            lines += ["### Design Strengths", ""]
            for pos in design_audit.positive_findings:
                lines.append(f"✅ {pos}")
            lines.append("")

    # ── Content section ───────────────────────────────────────────────────────
    if content:
        lines += [
            "---",
            "## Content Analysis",
            f"**Overall Content Score:** {_score_bar(content.overall_content_score)}  "
            f"({_score_label(content.overall_content_score)})",
            "",
        ]

        if content.key_findings:
            lines += ["### Key Findings", ""]
            lines.append(content.key_findings)
            lines.append("")

        if content.dimension_scores:
            lines += ["### Content Dimension Scores", ""]
            lines.append("| Dimension | Score | Status |")
            lines.append("|-----------|-------|--------|")
            for d in content.dimension_scores:
                status = "N/A" if d.is_na else _score_label(d.score)
                score_str = "—" if d.is_na else f"{d.score:.1f}/10"
                lines.append(f"| {d.dimension_name} | {score_str} | {status} |")
            lines.append("")

        if content.content_gaps:
            lines += ["### Content Gaps", ""]
            for gap in content.content_gaps:
                lines.append(f"- {gap}")
            lines.append("")

        if content.content_strengths:
            lines += ["### Content Strengths", ""]
            for s in content.content_strengths:
                lines.append(f"✓ {s}")
            lines.append("")

    # ── Journey log ───────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Journey Log",
        f"**Terminal Reason:** {journey.terminal_reason}",
        "",
    ]
    for s in journey.memory.steps:
        tick        = "✓" if s.success else "✗"
        emotion_tag = f" [{s.emotion}]" if s.emotion else ""
        lines.append(f"\n### Step {s.step_number} {tick}{emotion_tag}")
        lines.append(f"**Action:** `{s.action}` → {s.target}")
        lines.append(f"**URL:** {s.url}")
        if s.inner_monologue:
            lines.append(f"\n💭 *{s.inner_monologue}*")
        if s.state_of_mind:
            lines.append(f"\n🧠 **State of mind:** {s.state_of_mind}")
        if s.cx_note:
            lines.append(f"\n📌 **CX Note:** {s.cx_note}")
        if s.cognitive_load:
            lines.append(f"⚡ **Cognitive Load:** {s.cognitive_load}")
        if s.unanswered_questions:
            lines.append(f"❓ **Questions:** {s.unanswered_questions}")
        if not s.success and s.error:
            lines.append(f"❌ **Error:** {s.error[:200]}")

    md_path = out_dir / "report.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


# ── Master report ─────────────────────────────────────────────────────────────

def generate_master_report(
    results:    list[tuple[JourneyResult, Optional[CXAuditResult], Optional[DesignAuditResult], Optional[ContentAnalysisResult]]],
    target_url: str = "",
    run_id:     str = "",
) -> Path:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [
        "# CX Audit — Master Report",
        "",
        "| **Target** | **Date** | **Model** | **Run** |",
        "|---|---|---|---|",
        f"| {target_url or config.TARGET_URL} | {now_str} | {config.OPENAI_MODEL} | {run_id or 'local'} |",
        "",
        "---",
        "## Executive Summary",
        "",
    ]

    cx_scores      = [(j.persona.name, cx.overall_cx_score)       for j, cx, _, _ in results if cx]
    design_scores  = [(j.persona.name, d.overall_design_score)     for j, _, d, _ in results if d]
    content_scores = [(j.persona.name, c.overall_content_score)    for j, _, _, c in results if c]

    if cx_scores:
        avg_cx = sum(s for _, s in cx_scores) / len(cx_scores)
        lines.append(f"**Average CX Score:** {avg_cx:.1f}/10  ({_score_label(avg_cx)})")
    if design_scores:
        avg_d = sum(s for _, s in design_scores) / len(design_scores)
        lines.append(f"**Average Design Score:** {avg_d:.1f}/10  ({_score_label(avg_d)})")
    if content_scores:
        avg_c = sum(s for _, s in content_scores) / len(content_scores)
        lines.append(f"**Average Content Score:** {avg_c:.1f}/10  ({_score_label(avg_c)})")
    lines.append("")

    # Persona scorecard
    lines += [
        "## Scorecard",
        "",
        "| Persona | Outcome | Steps | CX | Design | Content |",
        "|---------|---------|-------|----|--------|---------|",
    ]
    _TERMINAL_MAP = {
        "done":                         "✅ Completed",
        "persona_chose_to_leave":       "🚪 Dropped off",
        "max_steps":                    "⏱ Max steps",
        "consecutive_failures":         "❌ Failures",
        "loop_detected":                "🔁 Loop",
        "login_required":               "🔒 Login wall",
        "reached_application_boundary": "📋 Form boundary",
        "cannot_find_product":          "🔍 Not found",
        "navigation_failed":            "💥 Nav failed",
        "valid_journey_abandoned":      "🛑 Abandoned",
        "popup_loop":                   "⚠️ Popup loop",
    }
    for journey, cx, design, ct in results:
        terminal  = _TERMINAL_MAP.get(journey.terminal_reason, journey.terminal_reason)
        cx_score  = f"{cx.overall_cx_score:.1f}"      if cx     else "—"
        d_score   = f"{design.overall_design_score:.1f}" if design else "—"
        c_score   = f"{ct.overall_content_score:.1f}" if ct     else "—"
        lines.append(
            f"| {journey.persona.name} | {terminal} | {journey.memory.step_count} "
            f"| {cx_score} | {d_score} | {c_score} |"
        )
    lines.append("")

    # Critical issues across all personas
    critical: list[tuple[str, str]] = []
    for journey, cx, design, _ in results:
        if cx:
            for issue in cx.issues:
                if issue.get("severity") == "critical":
                    critical.append((journey.persona.name, issue.get("description", "")))
        if design:
            for issue in design.critical_issues:
                if issue.get("severity") == "critical":
                    critical.append((journey.persona.name, issue.get("description", "")))

    if critical:
        lines += ["## Critical Issues (Across All Personas)", ""]
        for persona_name, desc in critical:
            lines.append(f"🔴 **{persona_name}:** {desc}")
        lines.append("")

    master_path = config.REPORTS_DIR / "master_report.md"
    master_path.write_text("\n".join(lines), encoding="utf-8")
    return master_path


# ── manifest.json ─────────────────────────────────────────────────────────────

def write_manifest(
    results:    list[tuple[JourneyResult, Optional[CXAuditResult], Optional[DesignAuditResult], Optional[ContentAnalysisResult]]],
    target_url: str,
    auth_mode:  str,
    eval_type:  str,
    run_id:     str = "",
) -> Path:
    slugs     = [j.persona.slug for j, *_ in results]
    cx_scores = [cx.overall_cx_score      for _, cx, *_ in results if cx]
    d_scores  = [d.overall_design_score   for _, _, d, _ in results if d]

    manifest = {
        "slugs":            slugs,
        "target_url":       target_url,
        "auth_mode":        auth_mode,
        "eval_type":        eval_type,
        "run_id":           run_id,
        "generated_at":     datetime.now(timezone.utc).isoformat() + "Z",
        "avg_cx_score":     round(sum(cx_scores) / len(cx_scores), 2) if cx_scores else None,
        "avg_design_score": round(sum(d_scores) / len(d_scores), 2)   if d_scores  else None,
        "persona_count":    len(slugs),
    }
    path = config.REPORTS_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


# ── session_index.json ────────────────────────────────────────────────────────

def write_session_index(
    results:    list[tuple[JourneyResult, Optional[CXAuditResult], Optional[DesignAuditResult], Optional[ContentAnalysisResult]]],
    target_url: str,
    auth_mode:  str,
    eval_type:  str,
    run_id:     str = "",
) -> Path:
    sessions = []
    for journey, cx, design, ct in results:
        sessions.append({
            "persona_name":   journey.persona.name,
            "persona_slug":   journey.persona.slug,
            "terminal_reason": journey.terminal_reason,
            "steps":          journey.memory.step_count,
            "duration_secs":  round(journey.duration_secs, 1),
            "cx_score":       cx.overall_cx_score      if cx     else None,
            "design_score":   design.overall_design_score if design else None,
            "content_score":  ct.overall_content_score if ct     else None,
            "report_path":    f"{journey.persona.slug}/report.md",
            "log_path":       f"{journey.persona.slug}/journey_log.json",
        })

    index = {
        "run_id":       run_id,
        "target_url":   target_url,
        "auth_mode":    auth_mode,
        "eval_type":    eval_type,
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "sessions":     sessions,
    }
    path = config.REPORTS_DIR / "session_index.json"
    path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return path


# ── Run archive  (BRD §5.5) ───────────────────────────────────────────────────

def archive_run(run_id: str) -> Path:
    """Copy the current reports/ contents to reports/run_archive/{run_id}/."""
    archive_root = config.REPORTS_DIR / "run_archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    dest = archive_root / run_id
    if dest.exists():
        shutil.rmtree(dest)

    # Copy everything under reports/ except the run_archive/ subdirectory itself
    dest.mkdir(parents=True, exist_ok=True)
    for item in config.REPORTS_DIR.iterdir():
        if item.name == "run_archive":
            continue
        target = dest / item.name
        try:
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True,
                                ignore_dangling_symlinks=True)
            else:
                shutil.copy2(item, target)
        except Exception as _copy_err:
            log.warning("archive_run: skipping %s — %s", item, _copy_err)

    # Load this run's manifest (copied into dest) to know its slugs + metadata.
    manifest_path = dest / "manifest.json"
    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    except Exception:
        manifest_data = {}
    slugs = manifest_data.get("slugs", [])

    # Copy THIS run's screenshots + videos into the archive so the tile keeps its
    # own media even after a later run overwrites the live screenshots/ & videos/.
    # Stored under _screenshots/{slug}/ and _videos/ so the dashboard can point at
    # them via archived_screenshots_path / archived_videos_path.
    arch_ss_dir = dest / "_screenshots"
    arch_vid_dir = dest / "_videos"
    for slug in slugs:
        try:
            src_ss = config.SCREENSHOTS_DIR / slug
            if src_ss.is_dir():
                shutil.copytree(src_ss, arch_ss_dir / slug, dirs_exist_ok=True,
                                ignore_dangling_symlinks=True)
        except Exception as _e:
            log.warning("archive_run: screenshots skip %s — %s", slug, _e)
        try:
            src_vid = config.VIDEOS_DIR / f"{slug}.webm"
            if src_vid.exists():
                arch_vid_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_vid, arch_vid_dir / f"{slug}.webm")
        except Exception as _e:
            log.warning("archive_run: video skip %s — %s", slug, _e)

    # Update archive_index.json so FILE_MODE dashboard can enumerate all past runs
    # without needing a server to list directories.
    index_path = archive_root / "archive_index.json"
    try:
        index: list = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    except Exception:
        index = []

    entry = {
        "run_id":          run_id,
        "slugs":           slugs,
        # Use the run's OWN generated_at (not the archive moment) so tiles show
        # the real run time. (issue 20)
        "generated_at":    manifest_data.get("generated_at") or (datetime.now(timezone.utc).isoformat() + "Z"),
        "target_url":      manifest_data.get("target_url", ""),
        "eval_type":       manifest_data.get("eval_type", ""),
        "auth_mode":       manifest_data.get("auth_mode", ""),
        "avg_cx_score":    manifest_data.get("avg_cx_score"),
        "avg_design_score": manifest_data.get("avg_design_score"),
        "persona_count":   manifest_data.get("persona_count", 0),
    }
    index = [e for e in index if e.get("run_id") != run_id]  # remove stale duplicate
    index.insert(0, entry)  # newest first
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    return dest
