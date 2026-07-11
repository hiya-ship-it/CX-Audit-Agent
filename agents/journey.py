"""
Journey Agent
-------------
Runs one persona's complete browsing journey.

The loop each step:
  1. Take screenshot
  2. Extract visible page state (URL + title + viewport elements)
  3. Call LLM with persona context + journey history + screenshot
  4. LLM returns a structured action dict
  5. Execute the action via BrowserController
  6. Record the step in JourneyMemory
  7. Check terminal conditions
  8. Repeat until done or limit reached
"""
from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.markup import escape as _esc

import config
from parsers.persona_parser import Persona
from agents.memory import JourneyMemory
from browser.controller import BrowserController
from llm.openai_responses import OpenAIResponsesClient

console = Console()


# ── Response schema for the LLM decision ─────────────────────────────────────

_DECISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "inner_monologue": {
            "type": "string",
            "description": (
                "Your unfiltered thought process RIGHT NOW as {persona.name}. "
                "First person, present tense. 2-4 sentences. "
                "Name what you literally see on screen. "
                "If the screen is showing a result from something you just entered (EMI, eligibility, rate, "
                "repayment amount), you MUST state that number and what you think of it relative to your "
                "personal situation — your income, your budget, your specific concerns. "
                "State specifically what you are about to do next and exactly why."
            ),
        },
        "action": {
            "type": "string",
            "enum": ["scroll_down", "scroll_up", "scroll_right", "scroll_left",
                     "click", "type", "search", "drag", "select",
                     "dismiss_overlay", "navigate_back", "done"],
            "description": (
                "drag = move a SLIDER thumb: set x,y to the slider thumb's current "
                "position and x2,y2 to where you want to drag it (e.g. further right "
                "for a higher loan amount). "
                "select = choose an option from a dropdown / picker: set x,y on the "
                "dropdown and value to the exact option label you want (e.g. '24 months')."
            ),
        },
        "target": {
            "type": "string",
            "description": (
                "For click: the EXACT text of the element from the VISIBLE ELEMENTS list above. "
                "For type: description of the input field. "
                "For search: the keyword to search. "
                "For drag: the slider you are moving. "
                "For select: the dropdown you are choosing from. "
                "For scroll/dismiss/back/done: leave empty or 'page'."
            ),
        },
        "value": {
            "type": "string",
            "description": (
                "For type/search: the actual text to enter. "
                "For select: the exact option label to choose (e.g. '24 months', '7.25%'). "
                "Empty for all other actions."
            ),
        },
        "x2": {
            "type": ["number", "null"],
            "description": (
                "ONLY for drag: the destination x-coordinate (0-360) to drag the "
                "slider thumb to. Null for every other action."
            ),
        },
        "y2": {
            "type": ["number", "null"],
            "description": (
                "ONLY for drag: the destination y-coordinate (0-740) to drag the "
                "slider thumb to. Usually the same as y for a horizontal slider. "
                "Null for every other action."
            ),
        },
        "x": {
            "type": ["number", "null"],
            "description": (
                "For click and type: the pixel x-coordinate of the element's centre. "
                "The screenshot is exactly 360 px wide — x=0 is the left edge, x=360 is the right edge. "
                "Set null for scroll, navigate_back, dismiss_overlay, search, done."
            ),
        },
        "y": {
            "type": ["number", "null"],
            "description": (
                "For click and type: the pixel y-coordinate of the element's centre. "
                "The screenshot is exactly 740 px tall — y=0 is the top, y=740 is the bottom. "
                "Set null for scroll, navigate_back, dismiss_overlay, search, done."
            ),
        },
        "marker": {
            "type": ["integer", "null"],
            "description": (
                "The orange numbered circle visible on the screenshot that marks your target element. "
                "PREFER this over estimating x/y when a marker is visible at your target — "
                "the marker centre is pixel-perfect. "
                "Still set x and y as a rough estimate in case marker is unclear. "
                "Set null for elements without a visible marker, or for scroll/back/done."
            ),
        },
        "reasoning": {
            "type": "string",
            "description": (
                "First-person account of why I chose this action right now. "
                "Written in my own voice (use 'I', 'me', 'my'). "
                "What I saw, what I thought, why this felt like the right move. "
                "2-3 sentences. Specific to this screen and my situation."
            ),
        },
        "emotion": {
            "type": "string",
            "enum": ["confident", "curious", "confused", "frustrated", "anxious",
                     "overwhelmed", "relieved", "disappointed", "suspicious", "hopeful", "reassured"],
        },
        "terminal_reason": {
            "type": ["string", "null"],
            "enum": [
                "done",
                "persona_chose_to_leave",
                "cannot_find_product",
                "login_required",
                "reached_application_boundary",
                None,
            ],
            "description": (
                "Set ONLY when the journey is genuinely over. "
                "'done' = found what they came for. "
                "'persona_chose_to_leave' = genuine frustration/confusion caused drop-off. "
                "'cannot_find_product' = exhausted all navigation options. "
                "'login_required' = hit auth gate they won't cross. "
                "'reached_application_boundary' = reached form asking for personal data (logged-out mode). "
                "null = journey continues."
            ),
        },
        "cx_note": {
            "type": "string",
            "description": (
                "First-person account of what I am experiencing at this exact moment — "
                "my raw, unfiltered reaction to what I see on screen right now. "
                "Written entirely in my own voice (use 'I', 'me', 'my'): "
                "what catches my eye, what confuses or reassures me, what question just formed, what I feel. "
                "If I just typed into a calculator or form, I MUST describe what the screen is now showing me "
                "as a result — the specific number, figure, or output — and whether it works for my situation. "
                "Must be specific to THIS screen and MY context — never generic. "
                "2-4 sentences. No analytical labels, no third-person evaluation."
            ),
        },
        "cognitive_load": {
            "type": "string",
            "description": (
                "Format: 'LOW|MEDIUM|HIGH — <first-person account of what this screen feels like>'. "
                "Written in my own voice (use 'I', 'me', 'my'). "
                "Name the exact thing confusing or overwhelming me right now. 2-3 sentences."
            ),
        },
        "trust_signals": {
            "type": "string",
            "description": (
                "First-person account of what is making me feel safe or uneasy right now. "
                "Written in my own voice (use 'I', 'me', 'my'). "
                "Name the specific elements I can see and how they land with me. "
                "Include what I was hoping to see but can't find. 2-3 sentences."
            ),
        },
        "unanswered_questions": {
            "type": "string",
            "description": (
                "3-5 questions forming in my mind RIGHT NOW. "
                "First person, colloquial, specific to my situation. "
                "Example: 'Will they ask for my income proof? How long will this take?'"
            ),
        },
        "guiding_factors": {
            "type": "string",
            "description": (
                "First-person account of how I arrived at this decision. "
                "Written in my own voice (use 'I', 'me', 'my'). "
                "What my eye landed on first, what pulled me forward, what tipped me toward this action. "
                "2-3 sentences."
            ),
        },
        "visible_content": {
            "type": "string",
            "description": (
                "What I can see on screen right now — written in my own voice. "
                "Name the headlines, CTAs, prices, images, badges that stand out to me. "
                "1-2 sentences. Use 'I can see…' or 'There's a…' to keep it grounded."
            ),
        },
        "attention_focus": {
            "type": "string",
            "description": (
                "Of everything visible on screen right now, what am I ACTUALLY reading and processing — "
                "written in my own voice (use 'I', 'me', 'my'). "
                "There may be 30+ elements in the viewport but my attention is a spotlight, not a floodlight. "
                "Name the 2-4 specific pieces of content I am actively consuming right now: "
                "the exact headline, number, label, or phrase I am reading word-for-word. "
                "Then name 1-2 things that are visible but I am NOT reading — because they are "
                "irrelevant to my goal, too dense, or just peripheral noise to me right now. "
                "Examples: "
                "'I am reading the 10.49% interest rate and the ₹40 lakh limit — those two numbers "
                "are all I care about on this screen. The trust badges and the footer are completely "
                "invisible to me right now.' "
                "'I am reading the Apply Now button and trying to find a processing fee line anywhere "
                "near it. The hero banner with the couple smiling is just wallpaper.' "
                "3-4 sentences. This is attention, not inventory."
            ),
        },
        "state_of_mind": {
            "type": "string",
            "description": (
                "My deeper psychological state beyond the surface emotion — written in my own voice. "
                "Use 'I', 'me', 'my' throughout. "
                "Cover: how motivated I am right now, whether I'm still fully in it or starting to doubt, "
                "specific anxieties I have about data, costs, or commitment, "
                "whether my original goal still feels within reach from here, "
                "and what would make me keep going versus give up. "
                "3-4 sentences."
            ),
        },
    },
    "required": [
        "inner_monologue", "action", "target", "value", "x", "y", "x2", "y2", "marker",
        "reasoning", "emotion", "terminal_reason", "cx_note", "cognitive_load",
        "trust_signals", "unanswered_questions", "guiding_factors", "visible_content",
        "attention_focus", "state_of_mind",
    ],
}


# ── Prompt builders ───────────────────────────────────────────────────────────

def _derive_navigation_instinct(persona: Persona) -> str:
    """Return 2-3 sentences describing how this persona naturally navigates."""
    nav = (getattr(persona, "navigation_style", "") or "").lower()
    lit = (getattr(persona, "financial_literacy", "") or "medium").lower()
    age = str(getattr(persona, "age", "") or "")
    pat = (getattr(persona, "patience", "") or "medium").lower()

    parts: list[str] = []

    if any(w in nav for w in ["search-first", "search first", "type-to-find"]):
        parts.append(
            f"{persona.name}'s first instinct is the search bar — they know what they want "
            f"and typing is faster than browsing."
        )
    elif any(w in nav for w in ["scroll", "browse-scroll", "swipe"]):
        parts.append(
            f"{persona.name} always scrolls first to get the full picture before deciding anything."
        )
    elif any(w in nav for w in ["impulsive", "cta-first", "quick-tap"]):
        parts.append(
            f"{persona.name} taps what looks relevant immediately — buttons and CTAs catch their eye."
        )
    elif any(w in nav for w in ["nav", "menu", "browse-nav", "navigation-first"]):
        parts.append(
            f"{persona.name} looks for structured navigation first — menu links and nav categories."
        )
    elif any(w in nav for w in ["cautious", "careful", "methodical"]):
        parts.append(
            f"{persona.name} reads carefully before acting — they scan, hover mentally, then decide."
        )
    else:
        # Infer from age
        try:
            age_val = int(str(age).split("-")[0].strip())
            if age_val >= 55:
                parts.append(f"{persona.name} scrolls through the page to find familiar words and images.")
            elif age_val <= 26:
                parts.append(f"{persona.name} goes straight for the search bar — typing is instinctive.")
        except Exception:
            pass

    if "low" in lit:
        parts.append(
            "They look for big, clear buttons with simple words — menus and fine print intimidate them."
        )
    elif "high" in lit:
        parts.append("They navigate financial sites efficiently and make direct, informed choices.")

    if "low" in pat:
        parts.append(
            f"They lose patience quickly. After 2-3 failed attempts they seriously consider leaving."
        )

    if not parts:
        parts.append(f"{persona.name} navigates by tapping what looks most relevant, then scrolling if needed.")

    return " ".join(parts)


def build_system_prompt(persona: Persona, auth_mode: str, target_url: str) -> str:
    """Static per-journey system prompt: who the persona is and how they navigate."""
    attrs: list[str] = []
    for field_name, label in [
        ("age",               "Age"),
        ("gender",            "Gender"),
        ("occupation",        "Occupation"),
        ("location",          "Location"),
        ("financial_literacy","Financial literacy"),
        ("device",            "Device"),
        ("constraints",       "Constraints"),
        ("behaviour",         "Typical behaviour"),
        ("success_criteria",  "Success criteria"),
        ("patience",          "Patience level"),
        ("navigation_style",  "Navigation style"),
        ("dropout_trigger",   "Dropout trigger"),
    ]:
        val = getattr(persona, field_name, None) or ""
        if not val:
            # also check raw_attributes
            val = (persona.raw_attributes or {}).get(field_name.replace("_", " "), "") or ""
        if val:
            attrs.append(f"  {label}: {val}")

    # Include background from raw_attributes if present
    bg = (persona.raw_attributes or {}).get("background", "")
    if bg:
        attrs.append(f"  Background: {bg}")

    persona_block = "\n".join(attrs) or "  (no additional profile details)"
    nav_instinct  = _derive_navigation_instinct(persona)

    auth_instruction = ""
    if auth_mode == "logged_out":
        auth_instruction = """
AUDIT BOUNDARY (logged-out mode):
You are browsing as an anonymous visitor. Reaching a form that asks for your mobile
number, Aadhar, PAN, date of birth, or OTP is NOT automatically the end — it is your
decision, as this person, what to do there. You may keep exploring, look elsewhere, or
leave. ONLY if you genuinely decide that you want to give your mobile number and proceed
to log in / apply should you type it in. Doing so ends this audit (logging in is out of
scope for a logged-out audit) — so only type your mobile number if that is truly what
this person would choose to do at this moment.
"""
    else:
        auth_instruction = """
LOGGED-IN MODE: You are browsing as an authenticated user. You may enter your
mobile number at login prompts. If you reach an application form mid-journey,
you may proceed to explore it (but do not submit).
"""

    dropout = getattr(persona, "dropout_trigger", "") or (persona.raw_attributes or {}).get("dropout trigger", "")
    patience = getattr(persona, "patience", "") or "medium"
    dropout_block = ""
    if dropout:
        dropout_block = f"\n  Your breaking point: \"{dropout}\""

    return f"""You are {persona.name}. You are NOT an AI assistant, NOT a QA bot, NOT a tester.
You are a real person visiting {target_url} on your mobile phone to accomplish a personal goal.
Every decision you make reflects your psychology, your literacy level, your patience, and your emotions.

═══════════════════════════════════════════
WHO YOU ARE
═══════════════════════════════════════════
Goal: {persona.intent}
{persona_block}

═══════════════════════════════════════════
HOW YOU NAVIGATE
═══════════════════════════════════════════
{nav_instinct}

═══════════════════════════════════════════
YOUR PATIENCE AND DROP-OFF INSTINCT
═══════════════════════════════════════════
Patience: {patience}{dropout_block}

You are a real person on a mobile phone. Real people leave. Often. Quickly.
The DEFAULT human response to friction is to leave — not to keep trying.
Persisting through confusion is the exception, not the rule.

You will feel the pull to leave when:
• You have scrolled past the same content twice without finding what you need
• An action failed and you are not sure why
• The page feels cluttered, slow, or irrelevant to your specific goal
• You hit an unexpected form, gate, or step you weren't prepared for
• The information you needed to make a decision is missing or buried
• You feel you have already spent more effort than this should take

When that feeling arises, ask yourself honestly: would you ACTUALLY keep going?
Most of the time, the honest answer is no.

set terminal_reason = "persona_chose_to_leave" the moment the experience stops
feeling worth your effort. Do not wait for a "natural ending". Drop-off mid-journey
IS the natural ending for most real users.

Patience calibration:
  Low    → You leave after 2-3 steps with no clear progress. One bad screen is enough.
  Medium → You give it 4-6 steps. After that, continued friction makes you leave.
  High   → You are unusually persistent, but even you have a limit around 8-10 steps.

If you FIND what you came for, set terminal_reason = "done". That is the rarer outcome.
{auth_instruction}
═══════════════════════════════════════════
HOW TO NAVIGATE THIS WEBSITE
═══════════════════════════════════════════
bajajfinserv.in has many paths to any product. What you try is entirely YOUR call —
based on your instinct, patience, and confidence with apps. Possibilities include:

• The CTA you need may be VISIBLE IN THE FIRST FOLD — just tap it directly.
• More content lives BELOW THE FOLD — scroll down through multiple sections.
• Some product strips are HORIZONTAL CAROUSELS — if a row of tiles seems cut off
  on the right, use scroll_right to see more items in that strip.
• There is an IN-SITE SEARCH BAR — tap it and type a relevant keyword naturally
  (character by character, exactly like a real person would). Pick from suggestions.
• A static NAVIGATION BAR sits at the bottom of the screen with a ☰ Menu icon —
  tap it to browse categories if you can't find your target anywhere else.
• You may DROP OFF at any point for any reason that feels real to you:
  confusion, frustration, cognitive overload, distrust, boredom, or
  simply having found (or decided you won't find) what you came for.

None of these are obligations. Use whichever path YOUR character would take.

═══════════════════════════════════════════
HOW TO INTERACT — VISION + MARKERS + COORDINATES
═══════════════════════════════════════════
You receive a screenshot of the mobile screen (360 px wide × 740 px tall).
Look at it exactly as you would look at a real phone screen.

ORANGE NUMBERED CIRCLES ON THE SCREENSHOT
  Every interactive element in the current viewport has a small orange numbered
  circle drawn at its exact pixel centre. These numbers are your primary way to
  interact precisely:
    → Set "marker" to the circle number you want to tap (e.g. marker=7)
    → Also set x and y as a rough estimate (fallback if marker is ambiguous)
    → Set marker=null only when targeting something with no visible orange circle

COORDINATES (x, y) — use when no marker is visible at your target:
  x = 0  →  left edge     x = 360  →  right edge
  y = 0  →  top            y = 740  →  bottom
  Aim for the centre of the element.

For scroll_down, scroll_up, navigate_back, dismiss_overlay, done → set x=null, y=null, marker=null.

CALCULATORS — MAKE THEM SHOW *YOUR* NUMBERS:
When you reach a loan / EMI / eligibility calculator that relates to what you came for,
a real person with a specific need does NOT just glance at the default figures and move
on. The numbers shown by default (e.g. ₹2,00,000 over 60 months) are generic — they are
NOT your situation. Someone who came wanting a specific amount will set the calculator to
THEIR amount and tenure, then read what EMI / interest / total it produces and judge
whether that actually works for them. Do the same:
  1. CHANGE the loan amount to the amount YOU actually want (from your goal above).
  2. CHANGE the tenure/duration to what suits you, if it is shown.
  3. READ the recalculated EMI / interest / total, and react to it as this person would —
     is it affordable? acceptable? Does it answer what you came to find out?
How to operate the controls (use whichever the calculator actually gives you):
  • NUMERIC FIELD — an editable amount box: action=type your amount.
  • DROPDOWN / TENURE PICKER — action=select (set value to e.g. "24 months"); or click it
    and pick the option on the next step.
  • SLIDER — action=drag: x,y on the thumb, x2,y2 where you want it (further right = higher).
  • STEPPER / PRESET CHIPS — tap the +/- buttons or the preset closest to your amount.
Skipping the calculator, or leaving its default numbers untouched, is exactly the kind of
shallow interaction a real person with a real need would NOT do.

SCROLL RULE: only scroll when the thing you want is NOT visible in the current screenshot.
If you can see it — use its marker number (or coordinates) directly. Do NOT scroll past visible content.

"""


def _extract_target_amount(intent: str) -> str:
    """Pull the persona's target money figure out of their goal text, e.g.
    'gold loan of ₹50,000' → '₹50,000', '2 lakh personal loan' → '2 lakh'.
    Returns '' when no clear amount is stated."""
    if not intent:
        return ""
    m = re.search(
        r'(₹\s?[\d,]+(?:\.\d+)?\s?(?:lakh|crore|thousand|k)?'
        r'|\b\d[\d,]*\s?(?:lakh|crore|thousand)\b)',
        intent, re.I,
    )
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ""


def build_step_prompt(state, memory: JourneyMemory, step_num: int) -> str:
    """Dynamic per-step user prompt: current page state + journey history."""
    history = memory.recent_history(6)

    overlay_warning = ""
    if state.has_overlay:
        _ot = state.overlay_text.lower()
        if "search bar active" in _ot:
            overlay_warning = (
                f"\n⚠️  SEARCH BAR IS ACTIVE — you have tapped the search input.\n"
                f"  You MUST now do one of two things:\n"
                f"  A) Type your search keyword: action=type, value='your keyword'\n"
                f"  B) Cancel and return to the page: action=dismiss_overlay\n"
                f"  You CANNOT scroll while the search overlay is open.\n"
            )
        else:
            overlay_warning = (
                f"\n⚠️  SOMETHING HAS APPEARED ON SCREEN.\n"
                f"  It says: {state.overlay_text[:200]}\n"
                f"\n"
                f"  Look at the screenshot and deal with it exactly as a human would:\n"
                f"  — If it shows options to select (tenure, amount, type) — tap the one you want.\n"
                f"  — If it is a form — fill it in or dismiss it.\n"
                f"  — If it has a close button — tap it.\n"
                f"  — If you want to dismiss it without a close button — use dismiss_overlay.\n"
            )

    bottom_warning = ""
    if state.at_bottom:
        bottom_warning = (
            "\n⚠️  You are at the BOTTOM of this page — nothing more below. "
            "Go back, use search, or decide to leave.\n"
        )

    # Drop-off pressure is keyed ONLY to being CURRENTLY stuck (consecutive
    # failures), never to raw step count. Steady forward progress — even over many
    # steps — must never trigger a "are you giving up?" nudge. (issues 7 & 8)
    _patience = (getattr(memory, "persona_data", {}) or {}).get("patience", "medium")
    _pat_l = str(_patience).lower()
    _is_low_pat    = "low"    in _pat_l
    _is_high_pat   = "high"   in _pat_l
    # How many failures IN A ROW (currently stuck) before the reality-check fires.
    _fail_thresh   = 2 if _is_low_pat else (4 if _is_high_pat else 3)
    _consec_fails  = memory.consecutive_failures

    frustration_note = ""
    if _consec_fails >= _fail_thresh:
        if _is_low_pat:
            frustration_note = (
                f"\n⚠️  REALITY CHECK — {_consec_fails} actions in a row just failed.\n"
                f"Your patience is low. You have already given this more effort than you normally would.\n"
                f"Would you ACTUALLY still be on this site right now?\n"
            )
        elif _is_high_pat:
            frustration_note = (
                f"\n⚠️  REALITY CHECK — {_consec_fails} actions in a row just failed.\n"
                f"Even patient users have limits. Is the effort still worth it to you?\n"
            )
        else:
            frustration_note = (
                f"\n⚠️  REALITY CHECK — {_consec_fails} actions in a row just failed.\n"
                f"A typical person would be questioning whether to continue at this point.\n"
                f"Are you making real progress, or just hitting dead ends? Be honest.\n"
            )

    scroll_ctx = state.scroll_context()

    prev_step = memory.steps[-1] if memory.steps else None

    # Detect within-page stagnation and surface it to the model for self-judgment.
    # This is not a hard termination — the model decides whether it's genuinely
    # reading or just going in circles.
    stagnation_note = ""
    if len(memory.steps) >= 4:
        recent4 = memory.steps[-4:]
        same_url = len(set(s.url for s in recent4)) == 1
        same_action = len(set(s.action for s in recent4)) == 1
        if same_url and same_action:
            _repeated_action = recent4[-1].action.replace("_", " ")
            stagnation_note = (
                f"\n🔁 HONEST SELF-CHECK: Your last 4 steps have all been '{_repeated_action}' "
                f"on the same page.\n"
                f"Ask yourself: am I actually finding and absorbing new content with each scroll, "
                f"or am I going through the same motions without progress?\n"
                f"If there is genuinely new content appearing — keep going.\n"
                f"If the page is giving you nothing new — try something different or accept that "
                f"this page does not have what you need.\n"
            )

    visible_text_block = ""  # Removed — model reads the screenshot directly, same as a human

    # Detect if the previous step CHANGED a calculator value (typed an amount,
    # dragged a slider, or picked a tenure) — if so, the screen likely shows an
    # updated result (EMI, eligibility, premium, etc.) that the persona should
    # read and process against their specific situation before acting.
    calculator_read_note = ""
    if prev_step and prev_step.action in ("type", "drag", "select"):
        # Pull persona-specific context to make the processing prompt concrete
        _pd = memory.persona_data or {}
        _constraints = _pd.get("constraints", "") or getattr(memory, "constraints", "") or ""
        _income_hint = ""
        for _k in ("income", "monthly_income", "salary", "earnings"):
            if _pd.get(_k):
                _income_hint = f"Your income context: {_pd[_k]}. "
                break
        _constraint_hint = f"Your specific constraints: {_constraints[:200]}. " if _constraints else ""

        calculator_read_note = (
            f"\n📊 YOU JUST CHANGED A CALCULATOR VALUE — THE SCREEN HAS UPDATED.\n"
            f"Before doing ANYTHING else, read what the screen is now showing you.\n"
            f"{_income_hint}{_constraint_hint}\n"
            f"Ask yourself these questions RIGHT NOW against YOUR specific situation:\n"
            f"  • What exact number is shown — EMI, interest amount, total repayment, eligibility result?\n"
            f"  • Read it out loud in your head. Is this affordable / acceptable for you personally?\n"
            f"  • Does this result answer what you came here to find out?\n"
            f"  • Is there anything on this screen you haven't read yet — charges, conditions, fine print?\n"
            f"  • Would you try a different value (change tenure, adjust amount) before deciding?\n"
            f"Only move to your next action after genuinely sitting with the result.\n"
        )

    # Proactive calculator engagement: when a calculator is on screen and the
    # persona is NOT already mid-interaction with it, prompt the realistic instinct
    # to set it to their own numbers and read the output. Fires once — it goes quiet
    # as soon as the persona changes a value (type/drag/select), handing off to the
    # calculator_read_note above.
    calculator_engage_note = ""
    _prev_action = prev_step.action if prev_step else ""
    if getattr(state, "has_calculator", False) and _prev_action not in ("type", "drag", "select"):
        _target = _extract_target_amount(memory.persona_intent)
        _target_line = (
            f"You came here wanting {_target}. " if _target
            else "You came here with a specific amount and timeline in mind. "
        )
        calculator_engage_note = (
            f"\n🧮 THERE IS A CALCULATOR ON THIS SCREEN.\n"
            f"{_target_line}The figures on it right now are generic defaults — NOT your situation.\n"
            f"A real person with your specific need would not just look at it and scroll past. They\n"
            f"would set it to THEIR numbers and see what it means for them. Change the loan amount\n"
            f"(and tenure, if shown) to match what YOU actually want, then read the EMI / interest /\n"
            f"total it produces and react to whether that works for you. Use the amount box (type),\n"
            f"the tenure dropdown (select), the +/- steppers or preset chips, or the slider (drag) —\n"
            f"whichever this calculator gives you. Do this BEFORE deciding to move on or leave.\n"
        )

    return f"""YOUR JOURNEY SO FAR — Step {step_num + 1}
{history}

════════════════════════════════
WHAT YOU SEE RIGHT NOW
════════════════════════════════
URL: {state.url}
Title: {state.title}
{scroll_ctx}
{overlay_warning}{bottom_warning}{frustration_note}{stagnation_note}{calculator_engage_note}{calculator_read_note}{visible_text_block}
[Screenshot attached — orange numbered circles mark every interactive element]

To tap a marked element: set "marker" to its number AND set x,y as a rough estimate.
To tap an unmarked element: set marker=null and use x,y coordinates.
Only scroll if what you want is NOT visible in the screenshot above.

────────────────────────────────
What do you do next? Think like {memory.persona_name} — not like a tester trying to complete a task.
If this screen isn't giving you what you came for, leaving is the most realistic choice.
Only continue if you genuinely believe the next step will get you closer."""


# ── Journey result ────────────────────────────────────────────────────────────

@dataclass
class JourneyResult:
    persona:         Persona
    memory:          JourneyMemory
    duration_secs:   float
    completed:       bool
    terminal_reason: str


# ── Agent ─────────────────────────────────────────────────────────────────────

class JourneyAgent:

    def __init__(self) -> None:
        self._llm = OpenAIResponsesClient()

    async def run_journey(
        self,
        persona:        Persona,
        target_url:     str   = config.TARGET_URL,
        max_steps:      int   = config.MAX_STEPS,
        auth_mode:      str   = "logged_out",
        start_from:     str   = "homepage",
        login_username: str   = "",
        run_id:         str   = "",
    ) -> JourneyResult:

        if config.DEBUG_MODE:
            max_steps = min(max_steps, 10)

        raw_attrs = persona.raw_attributes or {}
        memory   = JourneyMemory(
            persona.name, persona.intent,
            persona_data={
                "name":               persona.name,
                "slug":               persona.slug,
                "age":                str(persona.age or ""),
                "gender":             getattr(persona, "gender", "") or raw_attrs.get("gender", ""),
                "occupation":         persona.occupation or "",
                "location":           persona.location or "",
                "device":             getattr(persona, "device", "") or raw_attrs.get("device", "Mobile"),
                "financial_literacy": getattr(persona, "financial_literacy", "") or raw_attrs.get("financial literacy", ""),
                "intent":             persona.intent,
                "constraints":        getattr(persona, "constraints", "") or raw_attrs.get("constraints", ""),
                "behaviour":          getattr(persona, "behaviour", "") or raw_attrs.get("behaviour", ""),
                "success_criteria":   getattr(persona, "success_criteria", "") or raw_attrs.get("success criteria", ""),
                "product":            raw_attrs.get("product", ""),
                "patience":           getattr(persona, "patience", "") or raw_attrs.get("patience", ""),
                "navigation_style":   getattr(persona, "navigation_style", "") or raw_attrs.get("navigation style", ""),
                "dropout_trigger":    getattr(persona, "dropout_trigger", "") or raw_attrs.get("dropout trigger", ""),
                "background":         raw_attrs.get("background", ""),
            }
        )
        memory.run_id = run_id
        memory.model  = config.OPENAI_MODEL
        log_path = config.LOGS_DIR / f"{persona.slug}.jsonl"
        memory._jsonl_path = log_path

        t_start = time.monotonic()
        system_prompt = build_system_prompt(persona, auth_mode, target_url)

        console.print(Panel(
            f"[bold cyan]{_esc(persona.name)}[/bold cyan]\n"
            f"[dim]{_esc(persona.intent[:100])}[/dim]\n"
            f"Auth: {auth_mode}  |  Start: {start_from}  |  Max steps: {max_steps}",
            title="Journey Start",
            border_style="cyan",
        ))

        async with BrowserController(persona_slug=persona.slug, persona=persona) as browser:

            # ── Initial navigation ────────────────────────────────────────────
            if start_from == "google":
                console.print(f"[cyan]Google entry — searching for: {persona.intent[:60]}[/cyan]")
                landed_url = await self._run_google_entry(browser, persona, target_url)
                if landed_url:
                    # Record minimal Google-entry data so the dashboard tab shows.
                    _words = persona.intent.lower().split()
                    _stops = {"wants", "to", "a", "an", "the", "and", "or", "for", "with",
                              "on", "apply", "find", "get", "check", "looking", "need"}
                    _kws = [w.strip(".,;:") for w in _words if w.strip(".,;:") not in _stops][:5]
                    memory.google_entry = {
                        "query":       " ".join(_kws) + " bajaj finserv",
                        "landed_url":  landed_url,
                        "scroll_depth": "",
                    }
                if not landed_url:
                    console.print("[yellow]Google entry failed — falling back to homepage[/yellow]")
                    nav_result = await browser.navigate(target_url)
                    if not nav_result.success:
                        memory.mark_terminal("navigation_failed")
                        return JourneyResult(
                            persona=persona, memory=memory,
                            duration_secs=time.monotonic() - t_start,
                            completed=False, terminal_reason="navigation_failed",
                        )
            else:
                nav_result = await browser.navigate(target_url)
                if not nav_result.success:
                    console.print(f"[red]Navigation failed: {nav_result.error}[/red]")
                    memory.mark_terminal("navigation_failed")
                    return JourneyResult(
                        persona=persona, memory=memory,
                        duration_secs=time.monotonic() - t_start,
                        completed=False, terminal_reason="navigation_failed",
                    )

            # ── Initial screenshot (step -1) ──────────────────────────────────
            init_ss = await browser.screenshot("step_-01_initial")
            if init_ss:
                init_state = await browser.get_state()
                memory.add_step(
                    step_number=-1,
                    url=init_state.url, page_title=init_state.title,
                    decision={
                        "action": "navigate", "target": target_url,
                        "inner_monologue": "Landing on the website for the first time.",
                        "reasoning": "Journey start — initial page load.",
                        "emotion": "hopeful", "terminal_reason": None,
                        "cx_note": "First impression of the landing page.",
                        "cognitive_load": "LOW — just arrived",
                        "trust_signals": "", "unanswered_questions": "",
                        "guiding_factors": "", "visible_content": "",
                        "attention_focus": "", "state_of_mind": "",
                    },
                    success=True, error="", screenshot=init_ss, duration_ms=0,
                )

            # ── Main agent loop ───────────────────────────────────────────────
            terminal_reason = "max_steps"
            _consecutive_overlay_dismissals = 0

            for step_num in range(max_steps):
                console.rule(f"[dim]Step {step_num + 1}/{max_steps} — {_esc(persona.name[:25])}[/dim]")

                # 1. Capture state
                try:
                    state = await browser.get_state()
                except Exception as e:
                    console.print(f"[red]State capture failed: {e}[/red]")
                    terminal_reason = "fatal_error"
                    break

                console.print(
                    f"  [dim]URL: {state.url[:70]}  |  "
                    f"Elements: {len(state.viewport_elements)}  |  "
                    f"Overlay: {state.has_overlay}[/dim]"
                )

                # 1b. Access Denied auto-recovery ─────────────────────────────
                _BROKEN_PATHS = ["/myaccount/search/content", "/search/content"]
                if (any(p in state.url for p in _BROKEN_PATHS)
                        or "access denied" in (state.title or "").lower()):
                    console.print("  [red]Access Denied — auto-recovering[/red]")
                    memory.failed_actions.append({
                        "step": step_num, "action": "search",
                        "target": "search bar",
                        "error": "Access Denied — broken search endpoint",
                    })
                    try:
                        await browser.page.go_back()
                        await browser.page.wait_for_load_state("domcontentloaded", timeout=8000)
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass
                    continue

                # 1d. URL rut detection ────────────────────────────────────────
                if _is_url_rut(memory, state.url):
                    console.print(f"  [yellow]URL rut detected: {state.url[:60]}[/yellow]")
                    terminal_reason = "loop_detected"
                    break

                # 2. Take screenshot with numbered marker overlay
                # marked_ss → LLM sees numbered circles (decision only)
                # ss_path   → clean screenshot recorded in memory + used by evaluators
                marked_ss, ss_path, marker_map = await browser.screenshot_with_markers(f"step_{step_num:03d}")

                # 3. Build prompts
                user_prompt = build_step_prompt(state, memory, step_num)

                # 4. Call LLM (pass annotated screenshot so it can read numbered markers)
                console.print("  [dim]Calling LLM…[/dim]")
                try:
                    decision = await asyncio.wait_for(
                        self._decide(system_prompt, user_prompt, marked_ss, browser),
                        timeout=150,
                    )
                except asyncio.TimeoutError:
                    console.print("[yellow]LLM call timed out (150s) — using scroll fallback[/yellow]")
                    decision = _fallback_decision()
                except Exception as e:
                    console.print(f"[yellow]LLM call failed: {e} — using scroll fallback[/yellow]")
                    decision = _fallback_decision()

                # Log the decision
                action     = decision.get("action", "scroll_down")
                emotion    = decision.get("emotion", "")
                monologue  = decision.get("inner_monologue", "")[:80]
                console.print(
                    f"  [{emotion.upper() if emotion else 'NEUTRAL'}] "
                    f"{action.upper()} → {_esc(decision.get('target', '')[:50])}\n"
                    f"  💭 {_esc(monologue)}"
                )

                # 5. Check if LLM decided to end the journey
                terminal_reason_from_llm = decision.get("terminal_reason")
                if terminal_reason_from_llm:
                    terminal_reason = terminal_reason_from_llm
                    # Still record the final step
                    memory.add_step(
                        step_number=step_num,
                        url=state.url, page_title=state.title,
                        decision=decision,
                        success=True, error="", screenshot=ss_path, duration_ms=0,
                    )
                    console.print(f"  [yellow]Terminal: {terminal_reason}[/yellow]")
                    break

                # 5b. Guard: if an overlay is active, the ONLY valid action is
                # dismiss_overlay. Intercept navigate_back (URL-hopping to escape
                # a popup) and any click on navigation links, and redirect to
                # dismiss_overlay instead.
                if state.has_overlay and action == "navigate_back":
                    console.print(
                        "  [yellow]Intercepted navigate_back while overlay active "
                        "— redirecting to dismiss_overlay[/yellow]"
                    )
                    action = "dismiss_overlay"
                    decision["action"] = "dismiss_overlay"

                # 5c. Overlay-loop guard: if the persona has tried to dismiss 3 times
                # and is still stuck, treat it as a genuine drop-off — a real person
                # would give up at this point. No JS forcing.
                if action == "dismiss_overlay":
                    _consecutive_overlay_dismissals += 1
                    if _consecutive_overlay_dismissals >= 3:
                        console.print(
                            "  [yellow]Overlay stuck after 3 dismissals — persona giving up[/yellow]"
                        )
                        terminal_reason = "persona_chose_to_leave"
                        break
                else:
                    _consecutive_overlay_dismissals = 0

                # 6. Execute the action
                # Resolve click target: prefer JS-computed marker centre over LLM-estimated coords
                t_exec = time.monotonic()
                _marker = decision.get("marker")
                if _marker and isinstance(_marker, int) and _marker in marker_map:
                    click_x, click_y = marker_map[_marker]
                    console.print(f"  [dim]Marker {_marker} → ({click_x:.0f}, {click_y:.0f})[/dim]")
                else:
                    _raw_x = decision.get("x")
                    _raw_y = decision.get("y")
                    click_x = float(_raw_x) if _raw_x is not None else 0.0
                    click_y = float(_raw_y) if _raw_y is not None else 0.0
                # Drag destination (for slider drags only)
                _raw_x2 = decision.get("x2")
                _raw_y2 = decision.get("y2")
                drag_x2 = float(_raw_x2) if _raw_x2 is not None else 0.0
                drag_y2 = float(_raw_y2) if _raw_y2 is not None else 0.0
                result = await browser.execute(
                    action=action,
                    target=decision.get("target", ""),
                    value=decision.get("value", ""),
                    x=click_x,
                    y=click_y,
                    x2=drag_x2,
                    y2=drag_y2,
                )
                exec_ms = int((time.monotonic() - t_exec) * 1000)

                if not result.success:
                    console.print(f"  [red]Action failed: {result.error[:80]}[/red]")

                # ── Post-action auth handling ─────────────────────────────────
                _typed_val = decision.get("value", "").strip()
                _typed_tgt = decision.get("target", "").lower()
                _digits = "".join(ch for ch in _typed_val if ch.isdigit())
                _is_mobile_field = any(w in _typed_tgt for w in ("mobile", "phone", "number", "tel", "otp"))

                # LOGGED-OUT audit: merely REACHING the mobile/personal-data boundary
                # is NOT a terminator — the persona decides freely what to do. But if
                # the persona actually COMMITS by typing its mobile number, logging in
                # is out of scope for a logged-out audit, so the journey ends here.
                if (auth_mode == "logged_out"
                        and action == "type"
                        and result.success
                        and (len(_digits) == 10 or (_is_mobile_field and len(_digits) >= 10))):
                    console.print(
                        "  [yellow]Mobile number entered in logged-out audit — "
                        "boundary reached, ending journey[/yellow]"
                    )
                    memory.add_step(
                        step_number=step_num,
                        url=state.url, page_title=state.title,
                        decision=decision,
                        success=result.success, error=result.error,
                        screenshot=ss_path, duration_ms=exec_ms,
                    )
                    terminal_reason = "reached_application_boundary"
                    break

                # LOGGED-IN audit: if click/type caused an OTP page → show banner,
                # wait for the human to enter the OTP, then continue.
                if (auth_mode == "logged_in"
                        and action in ("click", "type")
                        and result.success):
                    try:
                        _peek = await browser.get_state()
                        if _is_otp_page(_peek):
                            console.print(Panel(
                                "[bold yellow]YOUR ACTION REQUIRED — ENTER OTP IN THE BROWSER[/bold yellow]\n\n"
                                "  1. Switch to the Playwright browser window\n"
                                "  2. Enter the OTP sent to your mobile\n"
                                "  3. Click Verify / Submit\n\n"
                                "Waiting up to [cyan]120 seconds[/cyan]...",
                                title="Complete OTP in Browser",
                                border_style="yellow",
                            ))
                            await self._wait_for_post_auth(browser, timeout_secs=120)
                    except Exception:
                        pass

                # 7. Record step with the PRE-action screenshot (ss_path) — the
                # evidence must show exactly what the persona saw when they made this
                # decision, NOT the result of the action. The result of this action
                # (e.g. a recalculated EMI) is seen and reacted to on the NEXT step,
                # where calculator_read_note prompts the persona to read it.
                memory.add_step(
                    step_number=step_num,
                    url=state.url, page_title=state.title,
                    decision=decision,
                    success=result.success, error=result.error,
                    screenshot=ss_path, duration_ms=exec_ms,
                )

                # 8. Controller-level terminal checks
                if memory.consecutive_failures >= config.CONSECUTIVE_FAIL_LIMIT:
                    console.print(f"  [red]{config.CONSECUTIVE_FAIL_LIMIT} consecutive failures — stopping[/red]")
                    terminal_reason = "consecutive_failures"
                    break

                if memory.is_looping():
                    console.print("  [yellow]Loop detected — stopping[/yellow]")
                    terminal_reason = "loop_detected"
                    break

                if state.at_bottom and action == "scroll_down":
                    # Already at bottom and still trying to scroll — force escalation
                    # by noting this in the next step's context (already handled via state.at_bottom)
                    pass

            else:
                terminal_reason = "max_steps"

            # Final screenshot
            final_ss = await browser.screenshot("final")
            if final_ss:
                memory.final_screenshot = final_ss

        # Store the journey video path AFTER the browser context has closed
        # (i.e. OUTSIDE the `async with browser` block above), so Playwright has
        # finalised the recording. BrowserController.__aexit__ writes the
        # consolidated videos/<slug>.webm; fall back to the newest raw Playwright
        # recording under videos/<slug>/ if the consolidated file isn't present.
        _vid = config.VIDEOS_DIR / f"{persona.slug}.webm"
        if _vid.exists():
            memory.video_path = str(_vid)
        else:
            _vsub = config.VIDEOS_DIR / persona.slug
            _webms = (sorted(_vsub.glob("*.webm"), key=lambda f: f.stat().st_mtime, reverse=True)
                      if _vsub.is_dir() else [])
            if _webms:
                memory.video_path = str(_webms[0])

        # Update token usage + derived dashboard metadata
        memory.token_usage = self._llm.pop_usage()
        try:
            from llm.openai_responses import compute_cost_inr
            memory.cost_inr = compute_cost_inr(
                memory.token_usage.get("input_tokens", 0),
                memory.token_usage.get("output_tokens", 0),
                config.OPENAI_MODEL,
            )
        except Exception:
            memory.cost_inr = None
        memory.is_technical_failure = terminal_reason in {"navigation_failed", "fatal_error"}
        memory.mark_terminal(terminal_reason)

        console.print(
            f"\n[bold green]Journey complete[/bold green] — "
            f"{terminal_reason}  |  {memory.step_count} steps  |  "
            f"{int(time.monotonic() - t_start)}s"
        )

        return JourneyResult(
            persona=persona, memory=memory,
            duration_secs=time.monotonic() - t_start,
            completed=memory.completed,
            terminal_reason=terminal_reason,
        )

    # ── Login flow (ported from agents/controller.py) ─────────────────────────

    async def _perform_login(
        self,
        browser: BrowserController,
        username: str,
        otp_wait_secs: int = 120,
    ) -> bool:
        """
        OTP-aware login for Bajaj Finserv.
        1. Enter mobile number via CSS selectors (then natural-language fallback).
        2. Click "Get OTP" / "Send OTP" / "Continue".
        3. Pause — print banner asking the human to enter OTP in the browser window.
        4. Poll URL every 2s for up to otp_wait_secs.
        5. Return True when the URL leaves the login/auth area.
        """
        console.print(Panel(
            f"[bold cyan]Performing login[/bold cyan]\n"
            f"Mobile: {username[:3]}{'*' * max(0, len(username) - 3)}",
            title="Login",
            border_style="cyan",
        ))
        await asyncio.sleep(2)

        # Step 1: Enter mobile number
        typed = False
        css_selectors = [
            'input[type="tel"]',
            'input[type="number"][maxlength="10"]',
            'input[name*="mobile" i]',
            'input[name*="phone" i]',
            'input[id*="mobile" i]',
            'input[id*="phone" i]',
            'input[placeholder*="mobile" i]',
            'input[placeholder*="phone" i]',
            'input[placeholder*="number" i]',
        ]
        for sel in css_selectors:
            try:
                loc = browser.page.locator(sel).first
                await loc.wait_for(state="visible", timeout=2000)
                await loc.click()
                await loc.fill(username)
                typed = True
                console.print(f"  [green]Entered mobile number (selector: {sel})[/green]")
                break
            except Exception:
                continue

        if not typed:
            for target in ["mobile number field", "mobile number or email field", "username field"]:
                result = await browser.execute(action="type", target=target, value=username)
                if result.success:
                    typed = True
                    console.print(f"  [green]Entered mobile number (target: {target})[/green]")
                    break

        if not typed:
            console.print("[yellow]Could not find mobile/username field — enter it manually[/yellow]")

        await asyncio.sleep(0.8)

        # Step 2: Click "Get OTP" or equivalent
        for target in ["Get OTP", "Send OTP", "Request OTP", "LOGIN", "Log In", "Continue", "Proceed"]:
            result = await browser.execute(action="click", target=target)
            if result.success:
                console.print(f"  [green]Clicked '{target}'[/green]")
                break

        await asyncio.sleep(3)
        state = await browser.get_state()
        url_before = state.url

        # Step 3: Hand over to human for OTP entry
        console.print(Panel(
            "[bold yellow]YOUR ACTION REQUIRED — COMPLETE LOGIN IN THE BROWSER[/bold yellow]\n\n"
            "  1. Switch to the browser window\n"
            "  2. Enter the OTP sent to your phone and click Verify\n"
            "  3. Complete any CAPTCHA if shown\n"
            "  4. Once on the post-login page, come back here\n\n"
            f"Waiting up to [cyan]{otp_wait_secs} seconds[/cyan]...",
            title="Complete Login in Browser",
            border_style="yellow",
        ))

        # Step 4: Poll until URL leaves the login area
        _auth_keywords = ("login", "signin", "sign-in", "/auth", "otp", "verify", "password")
        elapsed = 0
        while elapsed < otp_wait_secs:
            await asyncio.sleep(2)
            elapsed += 2
            state = await browser.get_state()
            url_changed   = state.url != url_before
            still_in_auth = any(k in state.url.lower() for k in _auth_keywords)
            if url_changed and not still_in_auth:
                console.print(f"[bold green]Login complete! Now at: {state.url[:100]}[/bold green]")
                return True
            if elapsed % 30 == 0:
                console.print(f"  [dim]Waiting for login... {otp_wait_secs - elapsed}s remaining[/dim]")

        console.print(Panel(
            "[bold red]Login timeout[/bold red]\n"
            f"No login detected after {otp_wait_secs}s.\n"
            "Continuing as logged-out session.",
            title="Login Timeout",
            border_style="red",
        ))
        return False

    # ── Google SERP entry flow ─────────────────────────────────────────────────

    async def _run_google_entry(
        self,
        browser: BrowserController,
        persona,
        target_url: str,
    ) -> str:
        """
        Navigate Google, search for persona's intent + 'bajaj finserv', click the
        first bajaj.com result.  Returns the landed URL, or "" on failure.
        """
        from urllib.parse import quote_plus, urlparse

        try:
            page = browser.page

            # 1. Navigate to Google
            await browser.navigate("https://www.google.com")
            await asyncio.sleep(1.5)

            # 2. Handle consent / cookie popup
            for sel in [
                'button[aria-label="Accept all"]',
                'button:has-text("Accept all")',
                'button:has-text("I agree")',
                '#L2AGLb',
                'form[action*="consent"] button[type="submit"]',
            ]:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=1500):
                        await btn.click()
                        await asyncio.sleep(0.8)
                        break
                except Exception:
                    pass

            # 3. Build query
            words  = persona.intent.lower().split()
            stops  = {"wants", "to", "a", "an", "the", "and", "or", "for", "with",
                      "on", "apply", "find", "get", "check", "looking", "need"}
            kws    = [w.strip(".,;:") for w in words if w.strip(".,;:") not in stops][:5]
            query  = " ".join(kws) + " bajaj finserv"
            console.print(f"[cyan]Google query: \"{query}\"[/cyan]")

            # 4. Type query into Google search box
            typed = False
            for sel in ['textarea[name="q"]', 'input[name="q"]', '[role="combobox"]']:
                try:
                    inp = page.locator(sel).first
                    if await inp.is_visible(timeout=2000):
                        await inp.click()
                        await asyncio.sleep(0.3)
                        await inp.fill(query)
                        await asyncio.sleep(0.3)
                        await inp.press("Enter")
                        typed = True
                        break
                except Exception:
                    continue

            # 5. Fallback: navigate directly to SERP URL
            if not typed:
                serp_url = f"https://www.google.com/search?q={quote_plus(query)}"
                console.print(f"[yellow]Search box unavailable — navigating to SERP URL[/yellow]")
                await page.goto(serp_url, wait_until="domcontentloaded", timeout=config.PAGE_TIMEOUT)

            await asyncio.sleep(3.0)
            await browser.screenshot("step_google_serp")

            # 6. Find first bajaj.com result and click it
            target_domain = urlparse(target_url).netloc.replace("www.", "")
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.startsWith('http'))
            """)

            bajaj_links = [
                h for h in links
                if target_domain in h
                and not any(x in h.lower() for x in ["login", "signin", "/auth", "myaccount/login"])
            ]

            if bajaj_links:
                best = bajaj_links[0]
                console.print(f"[green]Google entry: clicking {best[:80]}[/green]")
                await page.goto(best, wait_until="domcontentloaded", timeout=config.PAGE_TIMEOUT)
                await asyncio.sleep(1.5)
                return page.url

            console.print("[yellow]No bajaj.com results found on SERP[/yellow]")
            return ""

        except Exception as exc:
            console.print(f"[red]Google entry failed: {exc}[/red]")
            return ""

    # ── Post-auth wait (OTP / login completion) ───────────────────────────────

    async def _wait_for_post_auth(
        self,
        browser: BrowserController,
        timeout_secs: int = 120,
    ) -> bool:
        """Poll URL until it leaves the auth/OTP area, or timeout expires."""
        _auth_kw = ("login", "signin", "sign-in", "/auth", "otp", "verify")
        try:
            url_before = (await browser.get_state()).url
        except Exception:
            return False

        elapsed = 0
        while elapsed < timeout_secs:
            await asyncio.sleep(2)
            elapsed += 2
            try:
                st = await browser.get_state()
                if st.url != url_before and not any(k in st.url.lower() for k in _auth_kw):
                    console.print(f"[bold green]Auth complete — now at: {st.url[:80]}[/bold green]")
                    return True
            except Exception:
                pass
            if elapsed % 30 == 0:
                console.print(f"  [dim]Waiting for OTP completion... {timeout_secs - elapsed}s left[/dim]")

        console.print("[yellow]OTP wait timed out — continuing journey[/yellow]")
        return False

    # ── LLM decision ──────────────────────────────────────────────────────────

    async def _decide(
        self,
        system_prompt: str,
        user_prompt: str,
        screenshot_path: str,
        browser: BrowserController,
    ) -> dict:
        """Call LLM and return a validated decision dict."""
        content: list[dict] = []

        img_b64 = browser.compress_screenshot(screenshot_path)
        if img_b64:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{img_b64}",
                "detail": "high",
            })

        content.append({"type": "input_text", "text": user_prompt})

        raw = await self._llm.create_json(
            system_prompt=system_prompt,
            input_content=content,
            schema_name="journey_decision",
            schema=_DECISION_SCHEMA,
        )

        result = dict(raw)
        result.setdefault("action", "scroll_down")
        result.setdefault("target", "")
        result.setdefault("value", "")
        result.setdefault("x", None)
        result.setdefault("y", None)
        result.setdefault("x2", None)
        result.setdefault("y2", None)
        result.setdefault("marker", None)
        result.setdefault("inner_monologue", "")
        result.setdefault("reasoning", "")
        result.setdefault("emotion", "curious")
        result.setdefault("terminal_reason", None)
        result.setdefault("cx_note", "")
        result.setdefault("cognitive_load", "")
        result.setdefault("trust_signals", "")
        result.setdefault("unanswered_questions", "")
        result.setdefault("guiding_factors", "")
        result.setdefault("visible_content", "")
        result.setdefault("attention_focus", "")
        result.setdefault("state_of_mind", "")
        return result


def _fallback_decision() -> dict:
    return {
        "action": "scroll_down", "target": "page", "value": "",
        "inner_monologue": "Something went wrong. I'll keep scrolling.",
        "reasoning": "LLM API error — fallback scroll.",
        "emotion": "confused", "terminal_reason": None,
        "cx_note": "", "cognitive_load": "", "trust_signals": "",
        "unanswered_questions": "", "guiding_factors": "", "visible_content": "",
        "attention_focus": "", "state_of_mind": "",
    }


def _google_query(intent: str) -> str:
    """Build a Google search query from a persona's intent."""
    import urllib.parse
    words = intent.lower().split()
    stops = {"wants", "to", "a", "an", "the", "and", "or", "for", "with", "on",
             "apply", "find", "get", "check", "looking", "need"}
    kws = [w.strip(".,;:") for w in words if w.strip(".,;:") not in stops][:5]
    query = " ".join(kws) + " bajaj finserv"
    return urllib.parse.quote(query)


# ── Login wall helpers (ported from agents/controller.py) ─────────────────────

_LOGIN_URL_KEYWORDS = (
    "login", "signin", "sign-in", "/auth", "otp", "verify",
    "myaccount/login", "account/login", "user/login",
    "register", "signup", "sign-up",
)


def _is_login_url(url: str) -> bool:
    lower = url.lower()
    return any(k in lower for k in _LOGIN_URL_KEYWORDS)


def _is_login_wall(state) -> bool:
    """Return True when the current page appears to be a login / OTP gate."""
    if _is_login_url(state.url):
        return True
    text = f"{state.title} {getattr(state, 'visible_text', '')}".lower()
    signals = (
        "get otp", "send otp", "verify otp",
        "login to continue", "log in to continue",
        "sign in to continue", "registered mobile",
    )
    return any(s in text for s in signals)


def _is_otp_page(state) -> bool:
    """Return True when the visible page is asking the user to enter an OTP."""
    text = f"{state.title} {getattr(state, 'visible_text', '')}".lower()
    signals = (
        "enter otp", "enter the otp", "verify otp",
        "otp sent", "otp has been sent", "enter your otp",
        "otp verification", "6-digit otp", "4-digit otp",
    )
    return any(s in text for s in signals)


def _normalize_url(url: str) -> str:
    """
    Strip query string and hash fragment so SPA calculators that mutate the URL
    on every slider/input change (?amount=…, #emi) are treated as the SAME page.
    Without this, interacting with a calculator looks like bouncing between URLs
    and falsely trips loop detection. (issue 9)
    """
    if not url:
        return ""
    u = url.split("#", 1)[0].split("?", 1)[0]
    return u.rstrip("/")


def _is_url_rut(memory: JourneyMemory, current_url: str, rut_threshold: int = 3) -> bool:
    """
    Arrival-based URL rut: counts how many times we *returned* to current_url
    from a different URL in the last 14 steps.  More accurate than raw counts
    because it ignores legitimate multi-step interactions on a single page.
    URLs are normalised (query/hash stripped) so SPA calculator state changes
    don't count as navigation.
    """
    window = memory.steps[-14:]
    if len(window) < 3:
        return False
    cur = _normalize_url(current_url)
    norm = [_normalize_url(s.url) for s in window]
    arrivals = sum(
        1 for i in range(1, len(norm))
        if norm[i] == cur and norm[i - 1] != cur
    )
    return arrivals >= rut_threshold
