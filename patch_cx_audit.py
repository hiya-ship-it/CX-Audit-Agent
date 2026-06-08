"""
One-off script: run CX evaluation on an existing journey_log.json
and patch the result back in.

Usage:
    python -X utf8 patch_cx_audit.py
    python -X utf8 patch_cx_audit.py --persona karan-bhatia
    python -X utf8 patch_cx_audit.py --slug karan-bhatia-personal-loan-for-home-renovation

Reads from:  reports/{slug}/journey_log.json
Writes to:   reports/{slug}/journey_log.json  (patches cx_audit key in-place)
             reports/{slug}/report.md         (prepends CX sections to existing report)

The existing design_audit and content_analysis in journey_log.json are preserved.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import fields as _dc_fields
from pathlib import Path

_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))

import config
from agents.memory import JourneyMemory, JourneyStep, CXObservation
from agents.controller import JourneyResult
from evaluation.cx_evaluator import CXEvaluator
from parsers.persona_parser import Persona
from rich.console import Console

console = Console()


# ── Reconstruct helpers ────────────────────────────────────────────────────────

def _build_persona(persona_data: dict) -> Persona:
    known = {"name", "age", "gender", "occupation", "location", "device",
             "financial_literacy", "intent", "constraints", "behaviour", "success_criteria"}
    raw = {k: str(v) for k, v in persona_data.items() if k not in known and v}
    try:
        age = int(persona_data.get("age") or 0) or None
    except (ValueError, TypeError):
        age = None
    return Persona(
        name               = persona_data.get("name", ""),
        age                = age,
        gender             = persona_data.get("gender") or None,
        occupation         = persona_data.get("occupation") or None,
        location           = persona_data.get("location") or None,
        device             = persona_data.get("device") or None,
        financial_literacy = persona_data.get("financial_literacy") or None,
        intent             = persona_data.get("intent", ""),
        constraints        = persona_data.get("constraints") or None,
        behaviour          = persona_data.get("behaviour") or None,
        success_criteria   = persona_data.get("success_criteria") or None,
        raw_attributes     = raw,
    )


def _build_memory(journey: dict) -> JourneyMemory:
    memory = JourneyMemory(
        persona_name   = journey.get("persona", ""),
        persona_intent = journey.get("intent", ""),
        persona_data   = journey.get("persona_data", {}),
    )
    memory.started_at            = journey.get("started_at", "")
    memory.terminal_reason       = journey.get("terminal_reason")
    memory.completed             = journey.get("completed", False)
    memory.initial_screenshot    = journey.get("initial_screenshot", "")
    memory.video_path            = journey.get("video_path", "")
    memory.token_usage           = journey.get("token_usage", {"input_tokens": 0, "output_tokens": 0})
    memory.google_entry          = journey.get("google_entry")
    memory.visited_urls          = journey.get("visited_urls", [])
    memory.failed_actions        = journey.get("failed_actions", [])
    memory.login_wall_encounters = journey.get("login_wall_encounters", 0)
    memory.login_wall_decisions  = journey.get("login_wall_decisions", [])

    for obs in journey.get("cx_observations", []):
        memory.cx_observations.append(CXObservation(
            step=obs.get("step", 0), url=obs.get("url", ""),
            kind=obs.get("kind", "neutral"), note=obs.get("note", ""),
            severity=obs.get("severity", "low"),
        ))

    # Filter step dicts to only the fields JourneyStep knows about
    _step_fields = {f.name for f in _dc_fields(JourneyStep)}
    for s in journey.get("steps", []):
        filtered = {k: v for k, v in s.items() if k in _step_fields}
        try:
            memory.steps.append(JourneyStep(**filtered))
        except TypeError as exc:
            console.print(f"[yellow]Skipping malformed step: {exc}[/yellow]")

    return memory


# ── Report patch: prepend CX sections to existing report.md ───────────────────

def _patch_report_md(out_dir: Path, cx_audit, journey_result: JourneyResult, eval_type: str) -> None:
    """
    Prepend CX audit sections to the existing report.md.
    This preserves any already-written design/content sections.
    """
    from reporting.report_generator import (
        _append_cx_audit_section, _outcome_emoji, _outcome_label,
        _score_color_label,
    )
    from datetime import datetime, timezone

    md_path = out_dir / "report.md"
    existing = md_path.read_text(encoding="utf-8") if md_path.exists() else ""

    # Strip the old header from existing content so we don't duplicate it
    # (the header is everything up to the first "---\n" separator)
    if "---\n" in existing:
        existing_body = existing[existing.index("---\n") + 4:]
    else:
        existing_body = existing

    lines: list[str] = []

    # New header with CX score included
    j = journey_result
    lines += [
        f"# CX Audit — {j.persona.name}",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Target** | {config.TARGET_URL} |",
        f"| **Date** | {datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')} |",
        f"| **Outcome** | {_outcome_emoji(j)} {_outcome_label(j)} |",
        f"| **CX Score** | **{cx_audit.overall_score:.1f} / 10** — {_score_color_label(cx_audit.overall_score)} |",
        f"| **Model** | {config.OPENAI_MODEL} |",
        "",
        "---",
        "",
    ]

    _append_cx_audit_section(lines, cx_audit)

    # Re-attach existing body (design/content/step log sections)
    lines.append(existing_body)

    md_path.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]Report updated:[/green] {md_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

async def patch(slug: str, auth_mode: str = "logged_out") -> None:
    log_path = config.REPORTS_DIR / slug / "journey_log.json"
    if not log_path.exists():
        console.print(f"[red]journey_log.json not found: {log_path}[/red]")
        sys.exit(1)

    raw          = json.loads(log_path.read_text(encoding="utf-8"))
    journey_data = raw.get("journey", {})
    eval_type    = raw.get("eval_type", "both")

    if raw.get("cx_audit") is not None:
        console.print(
            f"[yellow]cx_audit already present "
            f"(overall_score={raw['cx_audit'].get('overall_score')}). "
            "Re-running anyway to refresh.[/yellow]"
        )

    persona = _build_persona(journey_data.get("persona_data", {}))
    memory  = _build_memory(journey_data)

    console.print(f"\n[bold cyan]Persona:[/bold cyan] {persona.name}")
    console.print(f"Steps: {memory.step_count}  |  Terminal: {memory.terminal_reason}  |  Auth: {auth_mode}")
    console.print(f"[dim](Screenshots not required — evaluation uses journey text + cx_notes)[/dim]\n")

    evaluator = CXEvaluator()
    try:
        cx_audit = await evaluator.evaluate(persona, memory, auth_mode=auth_mode)
        console.print(
            f"[bold green]CX Score: {cx_audit.overall_score:.1f}/10[/bold green]  "
            f"— {cx_audit.journey_verdict}"
        )
    except Exception as exc:
        import traceback as _tb
        console.print(f"[bold red]CX evaluation failed: {exc}[/bold red]")
        console.print(f"[dim]{_tb.format_exc()}[/dim]")
        sys.exit(1)

    # ── Patch journey_log.json in-place ───────────────────────────────────────
    raw["cx_audit"] = cx_audit.to_dict()
    types_run = raw.get("eval_types_run", [])
    if "cx" not in types_run:
        raw["eval_types_run"] = ["cx"] + types_run

    log_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"[green]Patched journey_log.json:[/green] {log_path}")

    # ── Patch report.md (prepend CX sections, preserve design/content) ────────
    journey_result = JourneyResult(
        persona         = persona,
        memory          = memory,
        duration_secs   = 0.0,
        completed       = memory.completed,
        terminal_reason = memory.terminal_reason or "",
    )
    out_dir = config.REPORTS_DIR / slug
    try:
        _patch_report_md(out_dir, cx_audit, journey_result, eval_type)
    except Exception as exc:
        console.print(
            f"[yellow]report.md update failed ({exc}) — "
            "journey_log.json is patched so the dashboard will show CX results.[/yellow]"
        )

    console.print("\n[bold green]Done. Refresh the dashboard to see the CX score.[/bold green]")


def _find_slug(query: str) -> str:
    from slugify import slugify
    direct = config.REPORTS_DIR / query
    if (direct / "journey_log.json").exists():
        return query
    slg = slugify(query)
    if (config.REPORTS_DIR / slg / "journey_log.json").exists():
        return slg
    matches = [
        d.name for d in config.REPORTS_DIR.iterdir()
        if d.is_dir() and (d / "journey_log.json").exists() and query.lower() in d.name.lower()
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        console.print(f"[yellow]Multiple matches:[/yellow] {matches}\nBe more specific.")
        sys.exit(1)
    console.print(f"[red]No persona folder matched: {query!r}[/red]")
    sys.exit(1)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Patch missing CX audit into an existing journey_log.json")
    p.add_argument("--slug",      default="", help="Exact persona slug (folder name under reports/)")
    p.add_argument("--persona",   default="", help="Partial persona name (fuzzy match)")
    p.add_argument("--auth-mode", default="logged_out", choices=["logged_out", "logged_in"])
    args = p.parse_args()

    if args.slug:
        _slug = args.slug
    elif args.persona:
        _slug = _find_slug(args.persona)
    else:
        _slug = "karan-bhatia-personal-loan-for-home-renovation"
        console.print(f"[dim]No --slug/--persona given; defaulting to: {_slug}[/dim]")

    asyncio.run(patch(_slug, auth_mode=args.auth_mode))
