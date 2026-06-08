"""
CX Audit Agent — Entry Point
==============================
Usage:
    python -X utf8 main.py                              # all personas
    python -X utf8 main.py --persona "Manoj"            # single persona
    python -X utf8 main.py --debug                      # 1 persona, 10 steps, verbose
    python -X utf8 main.py --eval-type cx               # CX only
    python -X utf8 main.py --start-from google          # start from Google
    python -X utf8 main.py --no-headed                  # headless
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

import config
from parsers.persona_parser import PersonaParser, Persona
from agents.journey import JourneyAgent, JourneyResult
from evaluation.cx_evaluator import CXEvaluator, CXAuditResult
from evaluation.design_evaluator import DesignEvaluator, DesignAuditResult
from evaluation.content_analyzer import ContentAnalyzer, ContentAnalysisResult
from reporting.report_generator import (
    generate_persona_report,
    generate_master_report,
    write_manifest,
    write_session_index,
    archive_run,
)

console = Console()


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Autonomous CX Audit Agent — powered by OpenAI + Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--personas-file", default="personas/bajaj_personas.md")
    p.add_argument("--persona", default=None, help="Run persona whose name contains this string")
    p.add_argument("--target-url", default=config.TARGET_URL)
    p.add_argument("--max-steps", type=int, default=config.MAX_STEPS)
    p.add_argument("--no-headed", action="store_true")
    p.add_argument("--debug", action="store_true", help="1 persona, 10 steps, verbose")
    p.add_argument("--auth-mode", default="logged_out", choices=["logged_out", "logged_in"])
    p.add_argument("--login-username", default="")
    p.add_argument("--start-from", default="homepage", choices=["homepage", "google"])
    p.add_argument("--eval-type", default="both", choices=["cx", "design", "content", "both", "all", "none"])
    p.add_argument("--run-id", default="")
    return p.parse_args()


# ── Single persona run ────────────────────────────────────────────────────────

async def run_one_persona(
    persona:   Persona,
    agent:     JourneyAgent,
    eval_type: str,
    args:      argparse.Namespace,
    run_id:    str = "",
) -> tuple[JourneyResult | None, CXAuditResult | None, DesignAuditResult | None, ContentAnalysisResult | None]:

    crash_log = Path("CRASH_LOG.txt")

    # ── Journey ───────────────────────────────────────────────────────────────
    try:
        journey = await agent.run_journey(
            persona        = persona,
            target_url     = args.target_url,
            max_steps      = args.max_steps,
            auth_mode      = args.auth_mode,
            start_from     = args.start_from,
            login_username = getattr(args, "login_username", ""),
            run_id         = run_id,
        )
    except Exception as exc:
        import traceback
        msg = traceback.format_exc()
        console.print(f"[bold red]Journey crashed for {persona.name}:[/bold red] {exc}")
        try:
            with open(crash_log, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n{datetime.now().isoformat()} [journey]\n{msg}\n")
        except Exception:
            pass
        return None, None, None, None

    real_steps = [s for s in journey.memory.steps if s.step_number >= 0]
    if not real_steps:
        console.print(f"[yellow]No real steps for {persona.name} — skipping evaluations[/yellow]")
        _save_minimal_log(journey, eval_type)
        return journey, None, None, None

    run_cx      = eval_type in ("cx", "both", "all")
    run_design  = eval_type in ("design", "both", "all")
    run_content = eval_type in ("content", "cx", "both", "all")

    cx_audit:       CXAuditResult | None       = None
    design_audit:   DesignAuditResult | None   = None
    content_result: ContentAnalysisResult | None = None

    # ── CX Evaluation ─────────────────────────────────────────────────────────
    if run_cx:
        console.print(f"\n[cyan]Running CX evaluation for {persona.name}…[/cyan]")
        try:
            cx_audit = await CXEvaluator().evaluate(journey.memory, persona)
            console.print(f"[green]CX Score: {cx_audit.overall_cx_score:.1f}/10[/green]")
        except Exception as exc:
            import traceback
            msg = f"CX eval failed for {persona.name}: {exc}\n{traceback.format_exc()}"
            console.print(f"[red]CX evaluation failed: {exc}[/red]")
            try:
                with open(crash_log, "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*60}\n{datetime.now().isoformat()} [cx_eval]\n{msg}\n")
            except Exception:
                pass

    # ── Design Evaluation ─────────────────────────────────────────────────────
    if run_design:
        console.print(f"\n[cyan]Running Design evaluation for {persona.name}…[/cyan]")
        try:
            design_audit = await DesignEvaluator().evaluate(journey.memory, persona)
            console.print(f"[blue]Design Score: {design_audit.overall_design_score:.1f}/10[/blue]")
        except Exception as exc:
            console.print(f"[red]Design evaluation failed: {exc}[/red]")

    # ── Content Analysis ──────────────────────────────────────────────────────
    if run_content:
        console.print(f"\n[cyan]Running Content analysis for {persona.name}…[/cyan]")
        try:
            content_result = await ContentAnalyzer().analyze(journey.memory, persona)
            console.print(f"[green]Content Score: {content_result.overall_content_score:.1f}/10[/green]")
        except Exception as exc:
            console.print(f"[red]Content analysis failed: {exc}[/red]")

    # ── Report ────────────────────────────────────────────────────────────────
    try:
        report_path = generate_persona_report(
            journey, cx_audit, design_audit, content_result, eval_type
        )
        console.print(f"[dim]Report: {report_path}[/dim]")
    except Exception as exc:
        import traceback
        console.print(f"[red]Report generation failed: {exc}[/red]")
        console.print(traceback.format_exc())
        _save_minimal_log(journey, eval_type, cx_audit, design_audit, content_result)

    return journey, cx_audit, design_audit, content_result


def _save_minimal_log(
    journey,
    eval_type: str,
    cx=None, design=None, content=None,
) -> None:
    slug    = journey.persona.slug
    out_dir = config.REPORTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "journey_log.json").write_text(
        json.dumps({
            "eval_type":        eval_type,
            "journey":          journey.memory.to_dict(),
            "cx_audit":         cx.to_dict()      if cx      else None,
            "design_audit":     design.to_dict()  if design  else None,
            "content_analysis": content.to_dict() if content else None,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    args = _parse_args()

    # If --start-from was not explicitly supplied on the CLI, ask the user now.
    if "--start-from" not in sys.argv:
        args.start_from = Prompt.ask(
            "\n[bold cyan]Where should the audit start?[/bold cyan]",
            choices=["homepage", "google"],
            default="homepage",
        )

    if args.no_headed:
        config.HEADED = False
    if args.debug:
        config.DEBUG_MODE = True
        config.SLOW_MO    = 1200
        args.max_steps    = min(args.max_steps, 10)
        console.print("[bold yellow]DEBUG MODE[/bold yellow] — max 10 steps, slow browser")
    config.MAX_STEPS = args.max_steps

    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    # Archive the PREVIOUS run's reports before this run overwrites them.
    # This ensures every completed run gets its own tile in the dashboard
    # regardless of whether the current run's archive step succeeds.
    _prev_manifest = config.REPORTS_DIR / "manifest.json"
    if _prev_manifest.exists():
        try:
            import json as _json
            _prev = _json.loads(_prev_manifest.read_text(encoding="utf-8"))
            _prev_run_id = _prev.get("run_id", "")
            _prev_archive = config.REPORTS_DIR / "run_archive" / _prev_run_id
            if _prev_run_id and _prev_run_id != run_id:
                console.print(f"[dim]Archiving previous run {_prev_run_id} before starting…[/dim]")
                archive_run(_prev_run_id)
        except Exception as _ae:
            console.print(f"[yellow]Pre-run archive warning: {_ae}[/yellow]")

    console.print(Panel(
        f"[bold cyan]CX Audit Agent[/bold cyan]\n"
        f"Target     : {args.target_url}\n"
        f"Max steps  : {args.max_steps}\n"
        f"Eval type  : {args.eval_type}\n"
        f"Start from : {args.start_from}\n"
        f"Headed     : {config.HEADED}\n"
        f"Model      : {config.OPENAI_MODEL}\n"
        f"Run ID     : {run_id}",
        title="Initialising",
        border_style="cyan",
    ))

    if not config.OPENAI_API_KEY:
        console.print("[bold red]ERROR: OPENAI_API_KEY not set. Add it to .env[/bold red]")
        sys.exit(1)

    personas_path = Path(args.personas_file)
    if not personas_path.exists():
        console.print(f"[red]Personas file not found: {personas_path}[/red]")
        sys.exit(1)

    all_personas = PersonaParser.parse(personas_path)
    console.print(f"[green]Loaded {len(all_personas)} personas[/green]")

    if args.debug and not args.persona:
        all_personas = all_personas[:1]
        console.print(f"[yellow]Debug: running first persona only: {all_personas[0].name}[/yellow]")

    if args.persona:
        all_personas = [p for p in all_personas if args.persona.lower() in p.name.lower()]
        if not all_personas:
            console.print(f"[red]No persona matched: {args.persona!r}[/red]")
            sys.exit(1)

    if args.auth_mode == "logged_in" and not args.login_username:
        console.print(
            "[bold yellow]Warning: --login-username not provided. "
            "The agent will browse in logged-in mode but OTP login requires a mobile number.[/bold yellow]"
        )

    agent   = JourneyAgent()
    results = []

    for i, persona in enumerate(all_personas, 1):
        console.print(f"\n[bold]━━━ Persona {i}/{len(all_personas)}: {persona.name} ━━━[/bold]")
        result = await run_one_persona(persona, agent, args.eval_type, args, run_id=run_id)
        if result[0] is not None:
            results.append(result)

    if not results:
        console.print("[bold red]No journeys completed.[/bold red]")
        return

    # Master report + manifest + session index + archive
    complete = [(j, cx, d, c) for j, cx, d, c in results if any((cx, d, c))]
    if complete:
        master = generate_master_report(complete, target_url=args.target_url, run_id=run_id)
        console.print(f"\n[bold green]Master report: {master}[/bold green]")

    write_manifest(
        results,
        target_url=args.target_url,
        auth_mode=args.auth_mode,
        eval_type=args.eval_type,
        run_id=run_id,
    )

    write_session_index(
        results,
        target_url=args.target_url,
        auth_mode=args.auth_mode,
        eval_type=args.eval_type,
        run_id=run_id,
    )

    archive_path = archive_run(run_id)
    console.print(f"[dim]Archive: {archive_path}[/dim]")

    _print_summary(results, args.eval_type)
    console.print("\n[bold green]✅ CX Audit complete.[/bold green]")


def _print_summary(results: list[tuple], eval_type: str) -> None:
    table = Table(title="Audit Summary", border_style="cyan", show_lines=True)
    table.add_column("Persona",  style="bold")
    table.add_column("Outcome",  justify="center")
    table.add_column("Steps",    justify="right")
    if eval_type in ("cx", "both", "all"):
        table.add_column("CX",     justify="center")
    if eval_type in ("design", "both", "all"):
        table.add_column("Design", justify="center")
    if eval_type in ("content", "cx", "both", "all"):
        table.add_column("Content", justify="center")

    _labels = {
        "done":                         "[cyan]✅ Done[/cyan]",
        "persona_chose_to_leave":       "[red]🚪 Left[/red]",
        "max_steps":                    "[yellow]⏱ Max steps[/yellow]",
        "consecutive_failures":         "[red]❌ Failures[/red]",
        "loop_detected":                "[yellow]🔁 Loop[/yellow]",
        "login_required":               "[blue]🔒 Login[/blue]",
        "reached_application_boundary": "[green]📋 Form[/green]",
        "cannot_find_product":          "[red]🔍 Not found[/red]",
        "navigation_failed":            "[red]💥 Nav failed[/red]",
        "valid_journey_abandoned":      "[yellow]🛑 Abandoned[/yellow]",
        "popup_loop":                   "[yellow]⚠️ Popup loop[/yellow]",
    }

    for journey, cx, design, ct in results:
        if journey is None:
            continue
        outcome = _labels.get(journey.terminal_reason, f"[dim]{journey.terminal_reason}[/dim]")
        row = [journey.persona.name, outcome, str(journey.memory.step_count)]
        if eval_type in ("cx", "both", "all"):
            row.append(f"{cx.overall_cx_score:.1f}" if cx else "—")
        if eval_type in ("design", "both", "all"):
            row.append(f"{design.overall_design_score:.1f}" if design else "—")
        if eval_type in ("content", "cx", "both", "all"):
            row.append(f"{ct.overall_content_score:.1f}" if ct else "—")
        table.add_row(*row)

    console.print("\n", table)


if __name__ == "__main__":
    asyncio.run(main())
