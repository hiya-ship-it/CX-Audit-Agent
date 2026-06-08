"""
Mobile CX Audit Agent â€” Entry Point (Appium / Android)
=======================================================
Runs a persona-driven CX audit on a native Android app using Appium.
OpenAI observes screenshots and decides actions; results feed the same
report pipeline used by the web audit.

Usage:
    python mobile_main.py                                           # all personas
    python mobile_main.py --debug                                   # 1 persona, 10 steps
    python mobile_main.py --app-package com.example.app
    python mobile_main.py --personas-file personas/bajaj_personas.md

Prerequisites:
    1. Appium server running:   appium
    2. Android emulator/device: adb devices
    3. App installed on device with --app-package / --app-activity set
    4. pip install Appium-Python-Client
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import config
from parsers.persona_parser import PersonaParser, Persona
from agents.memory import JourneyMemory
from evaluation.cx_evaluator import CXEvaluator, CXAuditResult
from reporting.report_generator import generate_persona_report, generate_master_report
from llm.openai_responses import OpenAIResponsesClient

console = Console()

MOBILE_REPORTS_DIR     = config.BASE_DIR / "reports" / "mobile"
MOBILE_SCREENSHOTS_DIR = config.BASE_DIR / "screenshots" / "mobile"
MOBILE_LOGS_DIR        = config.BASE_DIR / "logs" / "mobile"

for _d in (MOBILE_REPORTS_DIR, MOBILE_SCREENSHOTS_DIR, MOBILE_LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

_SYSTEM_PROMPT = """You are an expert mobile UX auditor testing the Bajaj Finserv Android app.
You observe screenshots and decide the next action to take on behalf of a specific user persona.

Respond ONLY with a JSON object â€” no commentary, no markdown fences â€” in one of these schemas:

Tap an element:
  {"action": "tap", "x": <int 0-1080>, "y": <int 0-1920>, "description": "..."}

Type text (tap a field first, then type):
  {"action": "type", "text": "...", "description": "..."}

Swipe / scroll:
  {"action": "swipe", "direction": "up"|"down"|"left"|"right", "description": "..."}

Press Android back:
  {"action": "back", "description": "..."}

Mark goal achieved:
  {"action": "done", "goal_achieved": true|false, "reason": "..."}

Record a CX observation (friction or delight):
  {"action": "observe", "kind": "friction"|"delight", "severity": "high"|"medium"|"low", "note": "..."}

Rules:
- Prefer tapping visible text/buttons directly â€” estimate x/y from screenshot layout
- Record observations frequently; they are the audit output
- Never loop on the same screen more than 3 times

FINTECH APPLICATION FUNNEL â€” CRITICAL:
On Bajaj Finserv, tapping Apply ALWAYS opens a login/OTP â†’ eligibility â†’ KYC funnel.
This is NOT a blocker. Enter it. Your most valuable audit data comes from inside the funnel.
- If a mobile number field appears: tap it and type a number, observe the UX.
- If an OTP screen appears: record it as friction/observation, note the UX quality.
- If an eligibility or personal details form appears: read every field, record CX observations.
- Only call done(goal_achieved=false) when a CAPTCHA or genuine dead-end is reached,
  OR when you have fully documented the application funnel experience.
- Do NOT call done(goal_achieved=true) just because you found and tapped the Apply button."""

_MOBILE_ACTION_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "action": {
            "type": "string",
            "enum": ["tap", "type", "swipe", "back", "done", "observe"],
        },
        "x": {"type": "integer", "minimum": 0, "maximum": 2000},
        "y": {"type": "integer", "minimum": 0, "maximum": 4000},
        "text": {"type": "string"},
        "direction": {"type": "string", "enum": ["up", "down", "left", "right", ""]},
        "description": {"type": "string"},
        "goal_achieved": {"type": "boolean"},
        "reason": {"type": "string"},
        "kind": {"type": "string", "enum": ["friction", "delight", ""]},
        "severity": {"type": "string", "enum": ["high", "medium", "low", ""]},
        "note": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "action", "x", "y", "text", "direction", "description", "goal_achieved",
        "reason", "kind", "severity", "note", "confidence",
    ],
}


@dataclass
class MobileJourneyResult:
    persona: Persona
    memory: JourneyMemory
    success: bool
    terminal_reason: str
    step_count: int
    failure_count: int
    duration_secs: float = 0.0


def _persona_to_dict(persona: Persona) -> dict:
    return {
        "name":               persona.name,
        "age":                str(persona.age) if persona.age else "",
        "gender":             persona.gender or "",
        "occupation":         persona.occupation or "",
        "location":           persona.location or "",
        "device":             persona.device or "Android smartphone",
        "financial_literacy": persona.financial_literacy or "",
        "intent":             persona.intent,
        "constraints":        persona.constraints or "",
        "behaviour":          persona.behaviour or "",
        "success_criteria":   persona.success_criteria or "",
    }


def _screenshot_b64(driver) -> str:
    """Return base64-encoded PNG screenshot."""
    return driver.get_screenshot_as_base64()


def _execute_action(driver, action: dict) -> str:
    """Execute a parsed action dict on the Appium driver. Returns status string."""
    act = action.get("action", "")

    if act == "tap":
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        x = max(1, min(int(action.get("x", w // 2)), w - 1))
        y = max(1, min(int(action.get("y", h // 2)), h - 1))
        driver.tap([(x, y)])
        return f"tapped ({x}, {y})"

    elif act == "type":
        text = action.get("text", "")
        active = driver.switch_to.active_element
        active.send_keys(text)
        return f"typed: {text!r}"

    elif act == "swipe":
        direction = action.get("direction", "up")
        w, h = driver.get_window_size()["width"], driver.get_window_size()["height"]
        cx = w // 2
        if direction == "up":
            driver.swipe(cx, int(h * 0.7), cx, int(h * 0.3), 600)
        elif direction == "down":
            driver.swipe(cx, int(h * 0.3), cx, int(h * 0.7), 600)
        elif direction == "left":
            driver.swipe(int(w * 0.8), h // 2, int(w * 0.2), h // 2, 600)
        elif direction == "right":
            driver.swipe(int(w * 0.2), h // 2, int(w * 0.8), h // 2, 600)
        return f"swiped {direction}"

    elif act == "back":
        driver.back()
        return "pressed back"

    elif act in ("done", "observe"):
        return f"no-op ({act})"

    return f"unknown action: {act}"


async def run_mobile_journey(
    persona: Persona,
    args: argparse.Namespace,
) -> MobileJourneyResult:
    """Run one persona's journey through the app. Returns a MobileJourneyResult."""

    from mobile.drivers.appium_driver import AppiumDriverFactory, DriverInitError

    slug     = persona.slug
    log_path = MOBILE_LOGS_DIR / f"{slug}.jsonl"
    ss_dir   = MOBILE_SCREENSHOTS_DIR / slug
    ss_dir.mkdir(parents=True, exist_ok=True)

    memory = JourneyMemory(
        persona.name,
        persona.intent,
        persona_data=_persona_to_dict(persona),
    )

    client = OpenAIResponsesClient()
    max_steps  = args.max_steps
    _start_ts  = time.time()

    console.print(Panel(
        f"[bold yellow]{persona.name}[/bold yellow]\n{persona.intent}",
        title="ðŸ“± Mobile Persona",
        border_style="yellow",
    ))

    # â”€â”€ Connect Appium â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    try:
        driver = AppiumDriverFactory.create(
            device_name=args.device_name,
        )
    except DriverInitError as exc:
        console.print(f"[red]Appium connection failed: {exc}[/red]")
        memory.terminal_reason = "driver_init_error"
        return MobileJourneyResult(
            persona=persona,
            memory=memory,
            success=False,
            terminal_reason="driver_init_error",
            step_count=0,
            failure_count=1,
            duration_secs=time.time() - _start_ts,
        )

    # Launch: navigate Chrome to target URL, or activate native app
    target_url   = getattr(args, "target_url", "https://www.bajajfinserv.in")
    _cfg_path    = Path(__file__).parent / "config" / "app_config.yaml"
    _caps        = AppiumDriverFactory._load_config(_cfg_path).get("capabilities", {})
    browser_mode = bool(_caps.get("browserName", ""))

    if browser_mode:
        console.print(f"[cyan]Browser mode: opening {target_url} in Chrome[/cyan]")
        driver.get(target_url)
        memory.visited_urls.append(target_url)
    elif args.app_package:
        try:
            driver.activate_app(args.app_package)
        except Exception:
            pass
    time.sleep(3)

    action_history: list[str] = []
    step = 0
    failure_count = 0
    consecutive_loops = 0          # consecutive steps where OpenAI repeated the same action
    _last_action_sig: str = ""     # fingerprint of last executed action
    terminal_reason = "max_steps"
    goal_achieved = False

    persona_context = (
        f"Persona: {persona.name}\n"
        f"Goal: {persona.intent}\n"
        f"Constraints: {persona.constraints or 'None'}\n"
        f"Device: Android smartphone (Pixel 6, Chrome mobile browser)\n"
        f"Auth mode: {args.auth_mode}\n"
        f"Login mobile number: {args.login_username or 'not provided'}"
    )

    try:
        while step < max_steps:
            step += 1
            console.print(f"[cyan]Step {step}/{max_steps}[/cyan]")

            # Screenshot
            ss_b64 = _screenshot_b64(driver)
            ss_path = ss_dir / f"step_{step:03d}.png"
            ss_path.write_bytes(base64.b64decode(ss_b64))

            # Build message for OpenAI
            user_msg: dict = {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": ss_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"{persona_context}\n\n"
                            "Recent actions:\n"
                            + ("\n".join(action_history[-8:]) or "None yet.")
                            + "\n\n"
                            f"Step {step} of {max_steps}. "
                            "What is the next action? Respond with JSON only."
                        ),
                    },
                ],
            }
            # Ask OpenAI with strict structured output
            action = await client.create_json(
                system_prompt=_SYSTEM_PROMPT,
                input_content=user_msg["content"],
                schema_name="mobile_cx_action",
                schema=_MOBILE_ACTION_SCHEMA,
                max_output_tokens=700,
                max_retries=4,
            )
            raw = json.dumps(action, ensure_ascii=False)

            # Log
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "step": step,
                    "screenshot": str(ss_path),
                    "raw_response": raw,
                }) + "\n")

            action_history.append(raw)

            act_type = action.get("action", "")
            desc     = action.get("description") or action.get("reason") or action.get("note", "")

            console.print(f"  â†’ [bold]{act_type}[/bold] {desc[:80]}")

            # â”€â”€ Loop / stuck detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            # Build a fingerprint from action type + key coordinates/text
            _sig = f"{act_type}:{action.get('x','')}:{action.get('y','')}:{action.get('text','')}"
            if act_type not in ("observe", "done", "swipe", "back") and _sig == _last_action_sig:
                consecutive_loops += 1
                console.print(
                    f"  [bold red]âŸ³ Repeated action (streak {consecutive_loops}): {_sig[:60]}[/bold red]"
                )
                if consecutive_loops >= 3:
                    console.print(
                        "[bold red]3 identical actions in a row â€” agent is stuck. Terminating.[/bold red]"
                    )
                    terminal_reason = "loop_detected"
                    memory.terminal_reason = terminal_reason
                    break
            else:
                consecutive_loops = 0
            _last_action_sig = _sig

            # â”€â”€ Handle terminal / observation actions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if act_type == "done":
                goal_achieved  = bool(action.get("goal_achieved", False))
                terminal_reason = "goal_achieved" if goal_achieved else "agent_gave_up"
                memory.terminal_reason = terminal_reason
                memory.goal_achieved   = goal_achieved
                break

            if act_type == "observe":
                memory.add_cx_observation(
                    step=step,
                    url=f"app://{args.app_package}",
                    kind=action.get("kind", "friction"),
                    note=action.get("note", ""),
                    severity=action.get("severity", "medium"),
                )
                # Don't consume a step for pure observations â€” allow another action
                step -= 1
                continue

            # Execute
            try:
                result_msg = _execute_action(driver, action)
                console.print(f"     [dim]{result_msg}[/dim]")
                time.sleep(1.0)
                # Track URL in browser mode
                try:
                    current_url = driver.current_url
                    if current_url and current_url not in ("about:blank", "data:,") \
                            and current_url not in memory.visited_urls:
                        memory.visited_urls.append(current_url)
                except Exception:
                    pass
            except Exception as exc:
                console.print(f"     [red]Action failed: {exc}[/red]")
                failure_count += 1
                memory.failed_actions.append({"step": step, "action": act_type, "error": str(exc)})

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    memory.terminal_reason = terminal_reason
    memory.goal_achieved   = goal_achieved

    return MobileJourneyResult(
        persona=persona,
        memory=memory,
        success=goal_achieved,
        terminal_reason=terminal_reason,
        step_count=step,
        failure_count=failure_count,
        duration_secs=time.time() - _start_ts,
    )


async def run_persona_mobile(
    persona: Persona,
    evaluator: CXEvaluator | None,
    args: argparse.Namespace,
) -> tuple[MobileJourneyResult, CXAuditResult | None]:

    journey = await run_mobile_journey(persona, args)

    audit: CXAuditResult | None = None
    if evaluator and not args.skip_eval:
        console.print(f"\n[cyan]ðŸ” Evaluating {persona.name}â€¦[/cyan]")
        try:
            audit = await evaluator.evaluate(persona, journey.memory, auth_mode=args.auth_mode)
            console.print(f"[green]CX Score: {audit.overall_score:.1f}/10[/green]")
        except Exception as exc:
            console.print(f"[red]Evaluation failed: {exc}[/red]")

    # Reports â€” always write to reports/mobile/ to avoid overwriting web reports
    slug     = persona.slug
    mob_dir  = MOBILE_REPORTS_DIR / slug
    mob_dir.mkdir(parents=True, exist_ok=True)
    if audit:
        generate_persona_report(journey, audit, out_dir=MOBILE_REPORTS_DIR)
    else:
        (mob_dir / "journey_log.json").write_text(
            journey.memory.to_json(), encoding="utf-8"
        )

    return journey, audit


# â”€â”€ CLI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Mobile CX Audit Agent (Appium)")
    p.add_argument("--personas-file", default="personas/bajaj_personas.md")
    p.add_argument("--persona",       default=None)
    p.add_argument("--personas",      default="",
                   help="Comma-separated persona names or slugs to run. Used by the dashboard selector.")
    p.add_argument("--app-package",   default="",
                   help="Android app package name. Leave empty to use Chrome browser mode.")
    p.add_argument("--app-activity",  default="",
                   help="Main activity to launch (native app mode only)")
    p.add_argument("--target-url",    default="https://www.bajajfinserv.in",
                   help="URL to open in Chrome (browser mode) or starting URL context.")
    p.add_argument("--device-name",   default="emulator-5554",
                   help="Appium deviceName capability â€” match `adb devices` output")
    p.add_argument("--auth-mode",     default="logged_out",
                   choices=["logged_out", "logged_in"])
    p.add_argument("--login-username", default="",
                   help="Mobile number to use when a login wall asks for it.")
    p.add_argument("--max-steps",     type=int, default=25)
    p.add_argument("--skip-eval",     action="store_true", default=False)
    p.add_argument("--debug",         action="store_true", default=False,
                   help="1 persona, 10 steps max")
    p.add_argument("--run-id",        default="")
    return p.parse_args()


async def main() -> None:
    args = _parse_args()

    if args.debug:
        args.max_steps = min(args.max_steps, 10)
        console.print("[bold yellow]DEBUG MODE[/bold yellow] â€” 1 persona, 10 steps")

    if not config.OPENAI_API_KEY:
        console.print("[red]OPENAI_API_KEY not set.[/red]")
        sys.exit(1)

    personas_path = Path(args.personas_file)
    if not personas_path.exists():
        console.print(f"[red]Personas file not found: {personas_path}[/red]")
        sys.exit(1)

    all_personas = PersonaParser.parse(personas_path)
    if args.debug:
        all_personas = all_personas[:1]
    if args.persona:
        all_personas = [p for p in all_personas if args.persona.lower() in p.name.lower()]
    if args.personas:
        selected = {item.strip().lower() for item in args.personas.split(",") if item.strip()}
        all_personas = [
            p for p in all_personas
            if p.slug.lower() in selected or p.name.lower() in selected
        ]

    console.print(Panel(
        f"[bold cyan]Mobile CX Audit Agent[/bold cyan]\n"
        f"App     : {args.app_package}\n"
        f"Device  : {args.device_name}\n"
        f"Personas: {len(all_personas)}\n"
        f"Auth    : {args.auth_mode}",
        title="ðŸ“± Initialising",
        border_style="cyan",
    ))

    evaluator = CXEvaluator() if not args.skip_eval else None
    all_results: list[tuple[MobileJourneyResult, CXAuditResult | None]] = []

    for i, persona in enumerate(all_personas, 1):
        console.print(f"\n[cyan]{'â”€'*60}\nPersona {i}/{len(all_personas)}[/cyan]")
        result = await run_persona_mobile(persona, evaluator, args)
        all_results.append(result)

    # Master report â€” written to reports/mobile/
    complete = [(j, a) for j, a in all_results if a is not None]
    if complete:
        generate_master_report(complete, out_dir=MOBILE_REPORTS_DIR)

    # Manifest
    slugs = [j.persona.slug for j, _ in all_results]
    manifest = {
        "slugs":        slugs,
        "app_package":  args.app_package,
        "auth_mode":    args.auth_mode,
        "run_id":       args.run_id,
        "audit_type":   "app",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (MOBILE_REPORTS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    # Run summary for web server
    if args.run_id:
        runs_dir = config.BASE_DIR / "runs"
        runs_dir.mkdir(exist_ok=True)
        scores  = [a.overall_score for _, a in all_results if a]
        summary = {
            "run_id":         args.run_id,
            "manifest_slugs": slugs,
            "persona_count":  len(slugs),
            "avg_cx_score":   round(sum(scores) / len(scores), 2) if scores else None,
            "auth_mode":      args.auth_mode,
            "app_package":    args.app_package,
        }
        (runs_dir / f"{args.run_id}.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )

    # Summary table
    table = Table(title="Mobile Audit Summary", border_style="cyan", show_lines=True)
    table.add_column("Persona",  style="bold")
    table.add_column("Outcome",  justify="center")
    table.add_column("Steps",    justify="right")
    table.add_column("CX Score", justify="center")
    for journey, audit in all_results:
        outcome = "[green]âœ… Achieved[/green]" if journey.success else f"[red]ðŸš« {journey.terminal_reason}[/red]"
        table.add_row(
            journey.persona.name,
            outcome,
            str(journey.step_count),
            f"{audit.overall_score:.1f}/10" if audit else "â€”",
        )
    console.print("\n", table)
    console.print("\n[bold green]âœ… Mobile CX Audit complete.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())

