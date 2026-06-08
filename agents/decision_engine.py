"""
Decision Engine  —  Webwright edition
--------------------------------------
Adopts Microsoft Webwright's code-as-action paradigm:

  OLD: screenshot → OpenAI → action dict ("scroll", "click", …)
  NEW: screenshot + ARIA snapshot → OpenAI → Playwright Python code block

The LLM now writes executable Playwright code for each step instead of
returning a discrete action token.  One call can:
  1. Interact with whatever is relevant on screen
  2. Try the search bar
  3. Try a navigation link
  4. Click a visible CTA
  5. Fall back to scroll as last resort

This inherently fixes:
  • Scroll-dominance  — scroll is the LAST option in the code, not the default
  • Element-not-found — code uses get_by_role/get_by_text with try/except fallbacks
  • Realism           — code includes human-like asyncio.sleep() pauses

Vision (screenshot) remains PRIMARY; the ARIA snapshot is structural context.
"""
from __future__ import annotations

import base64
import io
import time
from pathlib import Path
from typing import Any, Optional

try:
    from PIL import Image as _PILImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

import config
from parsers.persona_parser import Persona
from browser.state_extractor import PageState
from agents.memory import JourneyMemory
from llm.openai_responses import OpenAIResponsesClient


# ── Response schema ────────────────────────────────────────────────────────────

_DECISION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "playwright_code": {
            "type": "string",
            "description": (
                "Python code using Playwright's async API. "
                "Runs inside: async def __agent_step__(page, context, browser, playwright, task): "
                "Available in scope: asyncio, re, random (already imported). "
                "Set task['done']=True to signal journey end. "
                "Wrap every interaction in try/except so one miss does not abort the step. "
                "10–30 lines. ONE coherent navigation step per call."
            ),
        },
        "action": {
            "type": "string",
            "description": (
                "One-sentence plain-English summary of what the code does — "
                "used for the journey log. E.g. 'Search for personal loan via search bar' "
                "or 'Click Personal Loan link in top navigation'."
            ),
        },
        "terminal_reason": {
            "type": ["string", "null"],
            "enum": [
                "done",
                "cannot_find_product",
                "login_required",
                "reached_application_boundary",
                "journey_complete",
                "persona_chose_to_leave",
                None,
            ],
            "description": (
                "Set only when the persona's journey is genuinely over. "
                "'done' = satisfied / natural stopping point. "
                "'cannot_find_product' = gave up after exhausting all navigation options. "
                "'login_required' = persona hit an auth gate they will not cross. "
                "'reached_application_boundary' = reached the application form boundary (logged_out audit). "
                "'journey_complete' = persona found what they came for and is done exploring. "
                "'persona_chose_to_leave' = dropped off due to frustration or confusion. "
                "null = journey continues."
            ),
        },
        "reasoning": {
            "type": "string",
            "description": (
                "First-person account of why I chose these specific actions. "
                "Written in my own voice (use 'I', 'me', 'my'). "
                "Cover: (1) what won my attention and why; "
                "(2) what I considered but rejected and why; "
                "(3) what I expect to happen next. "
                "3–5 sentences. Reveal my decision-making, never describe the screen."
            ),
        },
        "emotion": {
            "type": ["string", "null"],
            "enum": [
                "confident", "curious", "confused", "frustrated", "anxious",
                "overwhelmed", "relieved", "disappointed", "suspicious",
                "hopeful", "reassured", None,
            ],
        },
        "cx_note": {
            "type": "string",
            "description": (
                "First-person account of what this persona is experiencing at this exact moment — "
                "their raw, unfiltered reaction to what they see on screen right now. "
                "Written entirely in the persona's own voice, as if they are speaking aloud: "
                "what catches their eye, what confuses or reassures them, what question just "
                "formed in their mind, what they are feeling. "
                "Must be specific to THIS screen and THIS persona's context — never generic. "
                "Examples of the right register: "
                "'I can see the EMI calculator but there's no mention of processing fees anywhere — "
                "that's exactly what I need before I can decide.' "
                "'Why is this page asking for my mobile number already? I haven't even seen the "
                "interest rate yet.' "
                "'That 10.5% banner caught my eye immediately — finally something concrete.' "
                "2–4 sentences. No analytical labels, no severity ratings, no third-person evaluation. "
                "Just the persona's lived experience of this moment."
            ),
        },
        "cognitive_load": {
            "type": "string",
            "description": (
                "Format: '[LOW|MEDIUM|HIGH] — <first-person account of what this screen feels like>'. "
                "Written entirely in the persona's own voice (use 'I', 'me', 'my'). "
                "Must cover: (a) the specific element that is confusing or overwhelming me, "
                "(b) how many things are competing for my attention right now, "
                "(c) any term or number I don't understand, "
                "(d) how tired or impatient I'm feeling after the steps I've already taken. "
                "Minimum 3 sentences. Sound like a real person, not an analyst."
            ),
        },
        "trust_signals": {
            "type": "string",
            "description": (
                "First-person account of what is making me feel safe or uneasy on this screen right now. "
                "Written in the persona's own voice (use 'I', 'me', 'my'). "
                "Name specific elements I can actually see and how they land with me. "
                "Include what I was hoping to see but can't find. "
                "Examples: 'I can see the RBI logo at the bottom — that helps a little.' "
                "'There's no EMI breakdown anywhere. That makes me nervous.' "
                "Minimum 3 sentences."
            ),
        },
        "unanswered_questions": {
            "type": "string",
            "description": (
                "3–6 questions forming in my mind right now, "
                "phrased exactly how I would actually think or say them (first person, colloquial). "
                "Journey-aware: do not repeat questions already answered in earlier steps. "
                "Never use generic financial FAQ language. "
                "Examples: 'Will they call me before disbursing?' 'What if I miss an EMI?'"
            ),
        },
        "guiding_factors": {
            "type": "string",
            "description": (
                "First-person account of how I arrived at this decision. "
                "Written in the persona's own voice (use 'I', 'me', 'my'). "
                "FIRST REACTION: what my eye landed on first and what I felt immediately. "
                "PROCESSING: one thing pulling me forward and one thing making me hesitate. "
                "CRYSTALLISATION: the single thing that tipped me toward this action. "
                "Present tense, 3 sentences."
            ),
        },
        "visible_content": {
            "type": "string",
            "description": (
                "What I can see on screen right now — written in the persona's own voice. "
                "Name the headlines, CTAs, prices, images, badges that stand out to me. "
                "1–2 sentences. Use 'I can see…' or 'There's a…' to keep it grounded in my perspective."
            ),
        },
        "attention_focus": {
            "type": "string",
            "description": (
                "Of everything visible on screen right now, what am I ACTUALLY reading and processing — "
                "written in my own voice (use 'I', 'me', 'my'). "
                "There may be 30+ elements in the viewport but my attention is a spotlight, not a floodlight. "
                "Name the 2–4 specific pieces of content I am actively consuming right now: "
                "the exact headline, number, label, or phrase I am reading word-for-word. "
                "Then name 1–2 things that are visible but I am NOT reading — because they are "
                "irrelevant to my goal, too dense, or just peripheral noise to me right now. "
                "Examples: "
                "'I am reading the 10.49% interest rate and the ₹40 lakh limit — those two numbers "
                "are all I care about on this screen. The trust badges and the footer are completely "
                "invisible to me right now.' "
                "'I am reading the Apply Now button and trying to find a processing fee line anywhere "
                "near it. The hero banner with the couple smiling is just wallpaper.' "
                "3–4 sentences. This is attention, not inventory."
            ),
        },
    },
    "required": [
        "playwright_code", "action", "terminal_reason",
        "reasoning", "emotion", "cx_note",
        "cognitive_load", "trust_signals",
        "unanswered_questions", "guiding_factors", "visible_content",
        "attention_focus",
    ],
}


# ── Phase-1 deliberation schema ────────────────────────────────────────────────
# Small, fast call — persona commits to a decision BEFORE any code is written.
# This makes every action auditable: the inner_monologue is the reason on record.

_DELIBERATION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "inner_monologue": {
            "type": "string",
            "description": (
                "Your thought process RIGHT NOW. First person, present tense. 3-5 sentences. "
                "Name what you actually see. State what you have tried so far. "
                "State what you are about to do and the SPECIFIC reason why that thing "
                "over everything else visible. This text is the auditable record — "
                "your action code must be consistent with it."
            ),
        },
        "intended_action": {
            "type": "string",
            "enum": ["search", "scroll_down", "scroll_up", "tap_element",
                     "type_text", "navigate_back", "done"],
        },
        "intended_target": {
            "type": "string",
            "description": (
                "Plain English: what will you interact with? Must be visible in the screenshot. "
                "E.g. 'the search icon in the top-right corner', "
                "'the Personal Loan tile in the product grid', "
                "'the page — scrolling to reveal what is below the fold'."
            ),
        },
        "emotional_state": {
            "type": "string",
            "enum": [
                "confident", "curious", "confused", "frustrated", "anxious",
                "overwhelmed", "relieved", "disappointed", "suspicious", "hopeful", "reassured",
            ],
        },
        "confidence_to_continue": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": (
                "high = I know exactly what to do next. "
                "medium = I will try one more thing before reconsidering. "
                "low = I am close to giving up."
            ),
        },
    },
    "required": [
        "inner_monologue", "intended_action", "intended_target",
        "emotional_state", "confidence_to_continue",
    ],
}


def _build_deliberation_prompt(
    persona: Persona,
    state: "PageState",
    memory: "JourneyMemory",
    step_number: int,
    frustration_ratio: float,
    instinct_text: str,
    pattern_note: str,
) -> str:
    """
    Phase-1 prompt: persona thinks through their next move.
    No code templates. No CX fields. Just psychology + screen → commitment.
    """
    # History block (last 6 steps)
    history_lines: list[str] = []
    for s in memory.steps[-6:]:
        emotion_tag = f" [{s.emotion}]" if s.emotion else ""
        tick = "✓" if s.success else "✗"
        thinking = f" | thinking: {s.inner_monologue[:60]}..." if s.inner_monologue else ""
        history_lines.append(
            f"  {tick} Step {s.step_number}: {(s.action or '?')[:70]}"
            f"{emotion_tag}{thinking}"
        )
    history_block = "\n".join(history_lines) or "  (journey just started)"

    # Persona profile
    attrs: list[str] = []
    for field_name, label in [
        ("age", "Age"), ("occupation", "Occupation"), ("location", "Location"),
        ("financial_literacy", "Financial literacy"), ("device", "Device"),
        ("constraints", "Constraints"), ("behaviour", "Behaviour"),
        ("navigation_style", "Navigation style"), ("patience", "Patience"),
        ("dropout_trigger", "Dropout trigger"),
    ]:
        val = getattr(persona, field_name, None) or ""
        if val:
            attrs.append(f"  {label}: {val}")
    persona_block = "\n".join(attrs) or "  (no additional profile)"

    # Viewport elements
    vp_els = getattr(state, "viewport_elements", "") or ""
    vp_block = vp_els if vp_els else "(viewport element list unavailable — rely on screenshot)"

    # Search suggestion note (only active after typing in search bar)
    overlay_note = ""
    if getattr(state, "search_suggestions_active", False):
        overlay_note = (
            "\n🔍 SEARCH SUGGESTIONS ARE SHOWING — you have already typed your keyword.\n"
            "  RULE: NEVER click the search icon or press Enter — that loads a search-results\n"
            "  page which is blocked by the site and will show an Access Denied error.\n"
            "  Your ONLY valid next actions are:\n"
            "    1. Click the most relevant suggestion from the dropdown visible in the screenshot.\n"
            "    2. If no suggestion matches your goal, press Escape and use the nav menu or a\n"
            "       product tile instead — do NOT submit the search query.\n"
            "  Do NOT scroll. Do NOT retype.\n"
        )

    # Frustration / patience signal
    patience_note = ""
    _dropout = (getattr(persona, "dropout_trigger", "") or "").strip()
    if frustration_ratio >= 0.75:
        patience_note = (
            f"\n⚠️  You are at {frustration_ratio:.0%} of your patience budget."
        )
        if _dropout:
            patience_note += f" Your breaking point: \"{_dropout}\"."
        patience_note += "\n"

    # ── Strategy ban: search caused Access Denied ─────────────────────────────
    # If search has already triggered an Access Denied error this journey,
    # the persona KNOWS search is broken here. A real person would not retry
    # the same approach that just burned them. But crucially: not everyone
    # would pivot and keep trying — some would just leave. That is a
    # completely valid response depending on the persona's psychology.
    _search_banned = any(
        fa.get("tag") == "search_access_denied"
        for fa in memory.failed_actions
    )
    search_ban_note = ""
    if _search_banned:
        pat_l   = (getattr(persona, "patience", "") or "medium").lower()
        dropout = (getattr(persona, "dropout_trigger", "") or "").strip().lower()

        # How close to leaving is this persona right now?
        if "low" in pat_l:
            lean = (
                f"Given your low patience, leaving RIGHT NOW is a completely "
                f"legitimate choice — the site broke on you and you have better "
                f"things to do than troubleshoot someone else's broken search. "
                f"Ask yourself honestly: is there ONE thing still visible that "
                f"makes you want to stay? If not, you leave."
            )
        elif "high" in pat_l:
            lean = (
                f"You are frustrated but you want this badly enough to try "
                f"a different approach first. If you can see something relevant "
                f"on screen right now you would try it. If the page looks "
                f"completely unhelpful even after scanning it, you might still leave."
            )
        else:
            lean = (
                f"You are genuinely on the fence. Whether you stay or go "
                f"depends entirely on what you can see on screen right now. "
                f"If there is something that looks like it could help — a tile, "
                f"a menu, a link — you might give it one shot. "
                f"If the page looks unhelpful or cluttered, you close the tab."
            )

        # Factor in dropout trigger
        dropout_note = ""
        if dropout and any(
            kw in dropout for kw in
            ["error", "broken", "slow", "confus", "denied", "trust", "credib"]
        ):
            dropout_note = (
                f"\nYour dropout trigger is: \"{persona.dropout_trigger}\". "
                f"An 'Access Denied' error likely hits it."
            )

        search_ban_note = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫  SEARCH IS BROKEN — YOU ALREADY KNOW THIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The search bar gave you an "Access Denied" error. You are not repeating that.
Your intended_action MUST NOT be "search" or "type_text" into the search bar.

YOU NOW FACE A REAL CHOICE:

  OPTION A — PIVOT: Try something completely different this moment.
    → A product tile or CTA visible on screen right now
    → A nav link that matches what you need
    → The hamburger/menu icon to see product categories
    → Scroll to discover what else is on this page

  OPTION B — LEAVE: Set intended_action="done" and confidence_to_continue="low".
    A real person does not owe this site infinite patience after a broken page.
    Leaving is not failure — it is a genuine human response.{dropout_note}

{lean}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return f"""════════════════════════════════════════════════════════
WHO YOU ARE
════════════════════════════════════════════════════════
You are {persona.name}. You are not a bot. You are a real person visiting this website.

PROFILE
  Intent : {persona.intent}
{persona_block}

YOUR NAVIGATION INSTINCT
{instinct_text}

════════════════════════════════════════════════════════
YOUR JOURNEY SO FAR  (step {step_number})
════════════════════════════════════════════════════════
{history_block}
{patience_note}{pattern_note}{search_ban_note}
════════════════════════════════════════════════════════
WHAT YOU SEE RIGHT NOW
════════════════════════════════════════════════════════
  URL   : {state.url}
  Title : {state.title}
{overlay_note}
ELEMENTS VISIBLE IN YOUR VIEWPORT RIGHT NOW:
{vp_block}

[Screenshot attached — this is EXACTLY what you are looking at]

⚠️  Anything not listed above is below the fold. You cannot see or tap it yet.

════════════════════════════════════════════════════════
THINK THROUGH YOUR NEXT MOVE — THEN COMMIT
════════════════════════════════════════════════════════
Answer honestly, in first person, present tense:

1. What is the first thing your eye landed on in this screenshot?
2. Given everything you have tried so far, how are you feeling right now?
3. Based on what is PHYSICALLY VISIBLE, what are you about to do — and why
   THAT specific thing over every other option on screen?
4. Is your goal still reachable from here, or are you close to giving up?

Commit. Once you decide, your action code must match exactly what you declare here.
You may only act on what is physically visible. No assumptions about the site."""


def _build_action_prompt(
    persona: Persona,
    state: "PageState",
    deliberation: dict,
    step_number: int,
    auth_mode: str,
    t_lo: float, t_hi: float,
    c_lo: float, c_hi: float,
    scroll_pct: str,
    search_term: str,
    strategy_sequence: list[str],
) -> str:
    """
    Phase-2 prompt: execute the committed deliberation as Playwright code.
    Shorter than the old system prompt — psychology was resolved in Phase 1.
    """
    inner    = deliberation.get("inner_monologue", "")
    i_action = deliberation.get("intended_action", "")
    i_target = deliberation.get("intended_target", "")
    emotion  = deliberation.get("emotional_state", "")
    conf     = deliberation.get("confidence_to_continue", "medium")

    # Viewport elements (for element finding)
    vp_els = getattr(state, "viewport_elements", "") or ""
    vp_block = vp_els if vp_els else "(use screenshot)"

    # Auth boundary reminder
    auth_note = ""
    if auth_mode == "logged_out":
        auth_note = (
            "\n🚫 AUDIT BOUNDARY: if you reach a form requesting personal details, "
            "mobile number, or OTP — set terminal_reason='reached_application_boundary' "
            "and task['done']=True.\n"
        )

    # Search suggestion note
    overlay_note = ""
    if getattr(state, "search_suggestions_active", False):
        overlay_note = (
            "\n🔍 SEARCH SUGGESTIONS ARE SHOWING — keyword already typed.\n"
            "  NEVER click the search icon or press Enter (causes Access Denied).\n"
            "  Click the best matching suggestion, or Escape and use the nav menu.\n"
        )

    # Low-confidence signal
    confidence_note = ""
    if conf == "low":
        _dropout = (getattr(persona, "dropout_trigger", "") or "").strip()
        confidence_note = (
            f"\n⚠️  {persona.name} declared LOW confidence to continue. "
            f"If nothing relevant is visible after this step, "
            f"set terminal_reason='persona_chose_to_leave' and task['done']=True."
        )
        if _dropout:
            confidence_note += f" Breaking point: \"{_dropout}\"\n"
        else:
            confidence_note += "\n"

    # Action-type-specific code template
    _action_templates = {
        "search": f"""\n   # {persona.name} searches — type SHORT keywords, then pick from suggestion drawer.
   # ⛔ NEVER click the search/magnifying-glass icon or press Enter after typing —
   #    submitting loads /search/content which is Akamai-blocked (Access Denied).
   #    The ONLY safe exit is clicking a suggestion, or Escape if none match.
   try:
       # Tap the search icon only to OPEN the bar (not to submit)
       _icon = page.get_by_role("button", name=re.compile(r"search", re.I))
       if await _icon.count() == 0:
           _icon = page.locator("[aria-label*='earch' i], [title*='earch' i]")
       if await _icon.count() > 0:
           await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
           await viewport_click(_icon)
           await asyncio.sleep(0.8)
       # Find the search input
       _sb = page.get_by_role("searchbox")
       if await _sb.count() == 0:
           _sb = page.locator("input[type='search'], input[placeholder*='earch' i]")
       if await _sb.count() > 0:
           await _sb.first.click()
           await asyncio.sleep(0.4)
            # Clear any pre-filled content before typing
            await page.keyboard.press("Control+a")
            await asyncio.sleep(0.1)
           # Type SHORT product keywords — never the full intent sentence
           for _ch in "{search_term}":
               await page.keyboard.type(_ch)
               await asyncio.sleep(random.uniform({t_lo}, {t_hi}))
           # Wait for BFL suggestion drawer to populate (~2-3s)
           await asyncio.sleep(2.5)
           _sugg = page.locator(
               "[role='option'], [role='listbox'] li, "
               "[class*='suggestion' i] li, [class*='autocomplete' i] li, "
               "[class*='dropdown' i] li, [class*='search-result' i] a, "
               "[class*='searchResult' i] a, [class*='search_result' i] a, "
               "[data-testid*='suggestion' i], [data-testid*='search-item' i]"
           )
           if await _sugg.count() > 0:
               await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
               await viewport_click(_sugg.first)
               await page.wait_for_load_state("domcontentloaded", timeout=10000)
           else:
               # No suggestions — abort search, navigate via menu or tiles next step
               await page.keyboard.press("Escape")
   except Exception as _e:
       print(f"search: {{_e}}")""",

        "scroll_down": f"""\
   # {persona.name} is scrolling down — gradual flicks, {scroll_pct} at a time
   for _ in range(2):
       await page.evaluate("window.scrollBy(0, Math.round(window.innerHeight * 0.4))")
       await asyncio.sleep(random.uniform(0.35, 0.75))""",

        "scroll_up": f"""\
   # {persona.name} scrolling up — going back to something they passed
   for _ in range(2):
       await page.evaluate("window.scrollBy(0, -Math.round(window.innerHeight * 0.4))")
       await asyncio.sleep(random.uniform(0.3, 0.6))""",

        "tap_element": f"""\
   # {persona.name} tapping: {i_target}
   try:
       # Try the most specific match first, then broaden
       _kw = re.compile(r"<use key words from: {i_target}>", re.I)
       _el = page.get_by_role("link", name=_kw)
       if await _el.count() == 0:
           _el = page.get_by_role("button", name=_kw)
       if await _el.count() == 0:
           _el = page.get_by_text("<key text from: {i_target}>", exact=False)
       await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
       await viewport_click(_el)
       await page.wait_for_load_state("domcontentloaded", timeout=10000)
   except Exception as _e:
       print(f"tap: {{_e}}")""",

        "type_text": f"""\
   # {persona.name} typing — triple-click clears pre-filled text, then char-by-char
   try:
       _field = page.get_by_role("textbox")
       if await _field.count() == 0:
           _field = page.locator("input:visible").first
       await _field.first.click(click_count=3)   # triple-click selects all existing text
       await asyncio.sleep(0.2)
       await page.keyboard.press("Control+a")    # belt-and-suspenders backup
       await asyncio.sleep(0.1)
       try:   # JS fallback for React-controlled inputs
           await page.evaluate(\"\"\"(() => {{
               const el = document.activeElement;
               if (!el || (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA')) return;
               if (!el.value) return;
               const s = Object.getOwnPropertyDescriptor(
                   el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype,
                   'value')?.set;
               if (s) s.call(el, '');
               el.dispatchEvent(new Event('input',  {{ bubbles: true }}));
               el.dispatchEvent(new Event('change', {{ bubbles: true }}));
           }})()\"\"\")\
       except Exception: pass
       await asyncio.sleep(0.1)
       for _ch in "<text to type>":
           await page.keyboard.type(_ch)
           await asyncio.sleep(random.uniform({t_lo}, {t_hi}))
   except Exception as _e:
       print(f"type: {{_e}}")""",


        "navigate_back": f"""\
   # {persona.name} going back — they changed their mind
   try:
       await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
       await page.go_back()
       await page.wait_for_load_state("domcontentloaded", timeout=10000)
       await asyncio.sleep(random.uniform(0.5, 1.0))
   except Exception as _e:
       print(f"back: {{_e}}")""",

        "done": f"""\
   # {persona.name} is done — journey ends here
   task["done"] = True""",
    }

    template = _action_templates.get(i_action, _action_templates["tap_element"])

    return f"""════════════════════════════════════════════════════════
{persona.name.upper()}'S COMMITTED DECISION (from deliberation)
════════════════════════════════════════════════════════
Thinking: "{inner}"

Committed action : {i_action}
Target           : {i_target}
Emotional state  : {emotion}
Confidence       : {conf}
{auth_note}{overlay_note}{confidence_note}
VIEWPORT ELEMENTS (for locating the target):
{vp_block}

════════════════════════════════════════════════════════
WRITE THE CODE — execute the committed decision exactly
════════════════════════════════════════════════════════
The code runs inside:
    async def __agent_step__(page, context, browser, playwright, task):
Available: asyncio, re, random, viewport_click. Set task["done"]=True only at journey end.

YOUR TIMING (from {persona.name}'s profile):
  Typing speed    : {t_lo}–{t_hi}s per character
  Pre-tap pause   : {c_lo}–{c_hi}s before clicking
  Scroll size     : {scroll_pct} of viewport per flick

TEMPLATE FOR YOUR COMMITTED ACTION ({i_action}):
{template}

HARD BLOCKS — violation terminates the step:
✗  page.goto()           — never navigate by URL directly
✗  fill("all at once")   — type character by character only
✗  locator.click()       — always use viewport_click(locator)
✗  window.location = … — no JS URL assignment

ELEMENT FINDING (most to least reliable):
   page.get_by_role("link",   name=re.compile(r"text", re.I))
   page.get_by_role("button", name=re.compile(r"text", re.I))
   page.get_by_text("text", exact=False)
   page.locator("[aria-label*='keyword' i]")

Wrap every interaction in try/except. The reasoning you write MUST reference your
inner monologue above — it is the auditable justification for this step."""


# ── Search keyword extractor ──────────────────────────────────────────────────

# Known Bajaj Finserv product strings — checked in order, longest-match wins.
_PRODUCT_MARKERS: list[str] = [
    "two-wheeler loan", "two wheeler loan", "bike loan",
    "home loan", "personal loan", "business loan", "gold loan",
    "education loan", "medical loan",
    "health insurance", "life insurance", "car insurance",
    "two-wheeler insurance", "vehicle insurance",
    "fixed deposit", "recurring deposit",
    "mutual fund", "sip",
    "credit card", "emi card", "bajaj emi",
    "consumer durable", "savings account",
]

_SEARCH_STOP: frozenset[str] = frozenset({
    "wants", "want", "to", "check", "for", "a", "an", "the", "and", "with",
    "on", "by", "of", "in", "is", "are", "can", "apply", "need", "find",
    "get", "looking", "has", "its", "their", "my", "me", "i", "about",
    "from", "up", "how", "what", "where", "best", "into", "some",
})


def _extract_search_term(intent: str) -> str:
    """
    Extract 2-3 SHORT product keywords from a persona's intent string.
    Used as the search bar query — never the full intent sentence.

    Examples:
      "Wants to check eligibility and apply for a two-wheeler loan …"
        → "two-wheeler loan"
      "Looking for health insurance for parents over 60"
        → "health insurance"
      "Compare fixed deposit rates across banks"
        → "fixed deposit"
    """
    intent_l = intent.lower()
    # Sort by length desc so "two-wheeler loan" matches before "loan"
    for marker in sorted(_PRODUCT_MARKERS, key=len, reverse=True):
        if marker in intent_l:
            return marker
    # Fallback: first 3 meaningful content words
    words = intent_l.replace("-", " ").split()
    kw = [w.strip(".,;:") for w in words
          if w.strip(".,;:") not in _SEARCH_STOP and len(w.strip(".,;:")) > 3]
    return " ".join(kw[:3]) or intent_l.split()[0]


# ── Persona navigation instinct deriver ────────────────────────────────────────

def _derive_navigation_instinct(
    persona: Persona,
    lit: str,
    age_str: str,
    nav: str,
    pat: str,
) -> tuple[str, list[str]]:
    """
    Returns (instinct_text, strategy_sequence):
      instinct_text      — prose describing how THIS persona navigates, third person
      strategy_sequence  — ordered list of strategies they try before giving up,
                           e.g. ["scroll", "cta", "search"] for a scroll-explorer.
                           Exhausting all strategies → persona drops off.

    Strategy labels: "search" | "nav_link" | "cta" | "scroll"
    The sequence length reflects patience (low-patience personas have shorter ladders).
    """
    parts: list[str] = []
    first_action = "cta"  # safe default

    nav_l = nav.lower()
    lit_l = lit.lower()
    pat_l = pat.lower()

    # ── Navigation style (strongest signal) ───────────────────────────────────
    if any(w in nav_l for w in ["search-first", "search first", "search_first", "type-to-find"]):
        parts.append(
            f"{persona.name}'s first instinct on any site is the search bar. "
            f"Browsing through menus feels slow and uncertain to them — "
            f"they know what they want, they just want to type it."
        )
        first_action = "search"

    elif any(w in nav_l for w in ["scroll", "scroll-explore", "swipe", "browse-scroll"]):
        parts.append(
            f"{persona.name} always scrolls through the page before deciding anything. "
            f"They want to see the full picture before committing to a direction — "
            f"tapping something too quickly feels risky to them."
        )
        first_action = "scroll"

    elif any(w in nav_l for w in ["impulsive", "cta-first", "tap-first", "quick-tap"]):
        parts.append(
            f"{persona.name} is a tap-first person. They see something relevant and they tap it "
            f"without overthinking. Browsing menus or typing in search bars feels unnecessary "
            f"when there's a button right in front of them."
        )
        first_action = "cta"

    elif any(w in nav_l for w in ["nav", "menu", "top-nav", "browse-nav", "navigation-first"]):
        parts.append(
            f"{persona.name} trusts structured navigation — they look for nav links "
            f"at the top of the page first. They've used enough sites to know "
            f"that menus usually have what they need."
        )
        first_action = "nav_link"

    elif any(w in nav_l for w in ["cautious", "careful", "methodical", "hesitant"]):
        parts.append(
            f"{persona.name} reads before they tap. They scan the page, hover over "
            f"links mentally, and only commit when they're reasonably sure. "
            f"Scrolling through the page is their way of building confidence."
        )
        first_action = "scroll"

    # ── Age as secondary signal (only if nav_style wasn't explicit) ────────────
    if not parts:
        try:
            age_val = int(str(age_str).split("-")[0].strip())
            if age_val >= 55:
                parts.append(
                    f"{persona.name} prefers to scroll through the page rather than "
                    f"type into a search bar — their eyes lead them. They tap what they "
                    f"recognise visually."
                )
                first_action = "scroll"
            elif age_val <= 26:
                parts.append(
                    f"{persona.name} is a digital native. Their hand goes to the search bar "
                    f"before they even think about it — typing is faster than browsing."
                )
                first_action = "search"
        except (ValueError, AttributeError, TypeError):
            pass

    # ── Financial literacy: nuances ───────────────────────────────────────────
    if "low" in lit_l:
        parts.append(
            f"They look for big buttons and familiar words — long menus or typing "
            f"feel intimidating. They tap what looks safe and recognizable."
        )
        if first_action == "search":
            first_action = "cta"   # low-lit persona won't search-first

    elif "high" in lit_l:
        parts.append(
            f"They're comfortable navigating financial sites and make efficient choices."
        )

    if not parts:
        parts.append(
            f"{persona.name} navigates by tapping what looks most relevant on screen, "
            f"scrolling to discover more if nothing stands out."
        )

    # ── Build strategy sequence (what they try before giving up) ─────────────
    # Natural fallback ladders per first instinct:
    _fallback_ladders: dict[str, list[str]] = {
        "search":   ["search",   "nav_link", "cta",      "scroll"],
        "nav_link": ["nav_link", "search",   "cta",      "scroll"],
        "cta":      ["cta",      "scroll",   "search",   "nav_link"],
        "scroll":   ["scroll",   "cta",      "nav_link", "search"],
    }
    sequence = _fallback_ladders.get(first_action, ["cta", "scroll", "search", "nav_link"])

    # Patience trims the ladder — low patience = fewer strategies before dropout
    if "low" in pat_l:
        sequence = sequence[:2]   # 2 strategies then dropout
        parts.append(
            f"After {_STRATEGY_THRESHOLDS['low'].get(sequence[0], 2)} failed attempts at their "
            f"first approach and {_STRATEGY_THRESHOLDS['low'].get(sequence[-1], 2)} at their "
            f"second, {persona.name} is done — they leave."
        )
    elif "medium" in pat_l or not pat_l:
        sequence = sequence[:3]   # 3 strategies then dropout
    # high patience → full ladder (4 strategies)

    return " ".join(parts), sequence


def _repetition_nudge(steps: list, persona_name: str, patience: str) -> str:
    """
    Looks at the tail of the journey history and returns a plain-English nudge
    if the persona has been doing the same thing repeatedly without progress.

    This is the honest version of adaptive behavior: no thresholds, no state machine.
    The model can already see the full history — this just names the pattern explicitly
    so the model can't miss it, and frames it in the persona's emotional terms.

    Returns empty string if there is no noticeable repetition.
    """
    if not steps or len(steps) < 2:
        return ""

    recent = steps[-5:]
    actions = [(getattr(s, "action", None) or "").lower() for s in recent]
    successes = [getattr(s, "success", True) for s in recent]
    urls = [getattr(s, "url", "") for s in recent]

    scroll_count = sum(1 for a in actions if "scroll" in a)
    fail_count   = sum(1 for ok in successes if not ok)
    same_page    = len(set(urls)) <= 2   # bouncing on 1-2 pages

    pat_l = patience.lower() if patience else "medium"

    # ── Repeated scrolling without landing anywhere ───────────────────────────
    if scroll_count >= 3:
        if "low" in pat_l:
            return (
                f"Pattern detected: {persona_name} has scrolled {scroll_count} times in the last "
                f"{len(recent)} steps without landing on their product. "
                f"Someone with their low patience is already internally decided — "
                f"one more scroll feels pointless. This is the moment they either try something "
                f"completely different (search bar, a nav link they spotted) or start composing "
                f"the mental note to look elsewhere."
            )
        else:
            return (
                f"Pattern detected: {persona_name} has scrolled {scroll_count} times recently "
                f"without finding their product. They're not panicking, but the repetition is "
                f"registering. A real person here would pause, look at the page differently, "
                f"and try a different approach — not scroll again."
            )

    # ── Repeated failures on same page ────────────────────────────────────────
    if fail_count >= 2 and same_page:
        if "low" in pat_l:
            return (
                f"Pattern detected: {persona_name} has had {fail_count} failed actions in a row "
                f"on the same page. For them, this crosses the threshold from inconvenience to "
                f"genuine frustration. They would step back mentally and try a different entry "
                f"point entirely, or decide this site isn't for them."
            )
        else:
            return (
                f"Pattern detected: {persona_name} has hit {fail_count} failures on the same page. "
                f"They're still willing to try, but they would switch tactics — "
                f"not retry the same element that just failed."
            )

    return ""


def _build_instinct_navigation_block(
    persona_name: str,
    strategy_sequence: list[str],
    search_term: str,
    c_lo: float, c_hi: float,
    t_lo: float, t_hi: float,
    scroll_pct: str,
) -> str:
    """
    Build the navigation code-examples section ordered to match this persona's
    strategy sequence. The first strategy in the sequence appears as PRIMARY;
    the rest appear as FALLBACKS in persona order.
    """
    first_action = strategy_sequence[0] if strategy_sequence else "cta"


    search_block = f"""\nSEARCH — type SHORT keywords, pick from suggestion drawer (NEVER click search icon or press Enter):
   # ⛔ Clicking the magnifying glass / pressing Enter loads /search/content → Akamai blocks it.
   #    Always pick a suggestion from the dropdown.  If none appear, Escape and use nav.
   try:
       # Tap search icon only to OPEN the bar
       _icon = page.get_by_role("button", name=re.compile(r"search", re.I))
       if await _icon.count() == 0:
           _icon = page.locator("[aria-label*='earch' i], [title*='earch' i]")
       if await _icon.count() > 0:
           await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
           await viewport_click(_icon)
           await asyncio.sleep(0.8)
       _sb = page.get_by_role("searchbox")
       if await _sb.count() == 0:
           _sb = page.locator("input[type='search'], input[placeholder*='earch' i]")
       if await _sb.count() > 0:
           await _sb.first.click()
           await asyncio.sleep(0.4)
           # Clear any pre-filled content before typing
           await page.keyboard.press("Control+a")
           await asyncio.sleep(0.1)
           for _ch in "{search_term}":
               await page.keyboard.type(_ch)
               await asyncio.sleep(random.uniform({t_lo}, {t_hi}))
           # Wait for BFL suggestion drawer to populate (~2-3s)
           await asyncio.sleep(2.5)
           _sugg = page.locator(
               "[role='option'], [role='listbox'] li, "
               "[class*='suggestion' i] li, [class*='autocomplete' i] li, "
               "[class*='dropdown' i] li, [class*='search-result' i] a, "
               "[class*='searchResult' i] a, [class*='search_result' i] a, "
               "[data-testid*='suggestion' i], [data-testid*='search-item' i]"
           )
           if await _sugg.count() > 0:
               await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
               await viewport_click(_sugg.first)
               await page.wait_for_load_state("domcontentloaded", timeout=10000)
           else:
               # No suggestions — abort search, try nav menu or product tiles next
               await page.keyboard.press("Escape")
   except Exception as _e:
       print(f"Search: {{_e}}")"""

    nav_block = f"""\
NAV LINK — tap a link you recognise in the viewport list:
   try:
       _lnk = page.get_by_role("link", name=re.compile(r"<exact text from viewport list>", re.I))
       await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
       await viewport_click(_lnk)
       await page.wait_for_load_state("domcontentloaded", timeout=10000)
   except Exception as _e:
       print(f"Nav: {{_e}}")"""

    cta_block = f"""\
CTA / BUTTON — tap what looks relevant on screen:
   try:
       _el = page.get_by_role("button", name=re.compile(r"<button text from viewport>", re.I))
       if await _el.count() == 0:
           _el = page.get_by_text("<visible text>", exact=False)
       await asyncio.sleep(random.uniform({c_lo}, {c_hi}))
       await viewport_click(_el)
       await page.wait_for_load_state("domcontentloaded", timeout=10000)
   except Exception as _e:
       print(f"CTA: {{_e}}")"""

    scroll_block = f"""\
SCROLL — discover more by scrolling {scroll_pct}:
   for _ in range(2):
       await page.evaluate("window.scrollBy(0, Math.round(window.innerHeight * 0.4))")
       await asyncio.sleep(random.uniform(0.35, 0.75))"""

    tool_map = {
        "search":   search_block,
        "nav_link": nav_block,
        "cta":      cta_block,
        "scroll":   scroll_block,
    }
    # Include all four tools regardless of sequence length, so the model always
    # has the code snippets available — but the ORDER and labelling reflects the
    # persona's strategy sequence (shorter-patience personas see fewer "NEXT" labels).
    all_strategies = ["search", "nav_link", "cta", "scroll"]
    ordered = list(strategy_sequence) + [s for s in all_strategies if s not in strategy_sequence]

    lines = []
    lines.append(f"YOUR FIRST MOVE — {persona_name.upper()}'S INSTINCT:")
    lines.append(f"   {tool_map[first_action]}")
    lines.append("")
    if len(ordered) > 1:
        lines.append(f"FALLBACKS — in the order {persona_name} would naturally try them:")
        for key in ordered[1:]:
            label = "LAST RESORT" if key not in strategy_sequence else f"NEXT if above fails"
            lines.append(f"   [{label}] {tool_map[key]}")
            lines.append("")
    return "\n".join(lines)


# ── System prompt builder ──────────────────────────────────────────────────────

def _build_system_prompt(
    persona: Persona,
    state: PageState,
    memory: JourneyMemory,
    step_number: int,
    auth_mode: str,
    intent_synonyms: str,
    frustration_ratio: float,
) -> str:
    """Build the Webwright-style system prompt for code-generation decisions."""

    # ── Persona profile block ─────────────────────────────────────────────────
    attrs: list[str] = []
    for field_name, label in [
        ("age", "Age"), ("occupation", "Occupation"), ("location", "Location"),
        ("financial_literacy", "Financial literacy"), ("device", "Device"),
        ("constraints", "Constraints"), ("behaviour", "Behaviour"),
        ("success_criteria", "Success criteria"),
        ("navigation_style", "Navigation style"), ("patience", "Patience"),
        ("dropout_trigger", "Dropout trigger"),
    ]:
        val = getattr(persona, field_name, None) or ""
        if val:
            attrs.append(f"  {label}: {val}")
    persona_block = "\n".join(attrs) or "  (no additional profile details)"

    # ── Derive human-like timing from persona attributes ──────────────────────
    _lit   = (getattr(persona, "financial_literacy", None) or "medium").lower()
    _age   = str(getattr(persona, "age", "") or "")
    _nav   = (getattr(persona, "navigation_style",  None) or "").lower()
    _pat   = (getattr(persona, "patience",           None) or "medium").lower()

    # Typing speed: delay between keystrokes (seconds)
    if "low" in _lit or any(d in _age for d in ["5", "6", "7", "8"]):
        _t_lo, _t_hi = 0.18, 0.40   # slow, deliberate — older / less literate
    elif "high" in _lit and ("quick" in _nav or "fast" in _nav or "tech" in _nav):
        _t_lo, _t_hi = 0.05, 0.13   # fast but still human
    else:
        _t_lo, _t_hi = 0.10, 0.24   # average person

    # Pre-click hesitation (seconds) — how long they pause before tapping
    if "cautious" in _nav or "low" in _lit or "anxious" in _pat:
        _c_lo, _c_hi = 0.8, 2.0
    elif "impulsive" in _nav or "quick" in _nav:
        _c_lo, _c_hi = 0.2, 0.6
    else:
        _c_lo, _c_hi = 0.4, 1.2

    # Scroll chunk size description for the prompt
    if "low" in _pat:
        _scroll_desc = "small thumb flicks (scroll 25-35% of viewport at a time)"
        _scroll_pct  = "25–35%"
    else:
        _scroll_desc = "moderate thumb scrolls (40-60% of viewport at a time)"
        _scroll_pct  = "40–60%"

    # ── Persona navigation instinct ───────────────────────────────────────────
    _instinct_text, _strategy_sequence = _derive_navigation_instinct(
        persona, _lit, _age, _nav, _pat
    )
    _repetition_note = _repetition_nudge(memory.steps, persona.name, _pat)

    # ── Journey history (last 6 steps) ────────────────────────────────────────
    history_lines: list[str] = []
    for s in memory.steps[-6:]:
        emotion_str = f" [{s.emotion}]" if s.emotion else ""
        tick = "✓" if s.success else "✗"
        history_lines.append(
            f"  {tick} Step {s.step_number}: {(s.action or 'unknown')[:80]}"
            f"{emotion_str} — {s.url[:55]}"
        )
    history_block = "\n".join(history_lines) if history_lines else "  (journey just started)"

    # ── Viewport-only elements ────────────────────────────────────────────────
    vp_els = getattr(state, "viewport_elements", "") or ""
    vp_block = vp_els if vp_els else "(viewport element list unavailable — use screenshot)"

    # aria_snapshot is intentionally NOT shown — viewport_elements is the only
    # element source so the model cannot target off-screen elements.

    # ── Contextual warnings ───────────────────────────────────────────────────
    overlay_warning = ""
    if getattr(state, "search_suggestions_active", False):
        overlay_warning = (
            "\n🔍 SEARCH SUGGESTIONS ARE SHOWING — you have already typed your keyword.\n"
            "  RULE: NEVER click the search icon or press Enter — the site's search-results\n"
            "  page is blocked by Akamai and will show Access Denied.\n"
            "  Your ONLY valid next actions are:\n"
            "    1. Click the most relevant suggestion from the dropdown in the screenshot.\n"
            "    2. If no suggestion matches, press Escape and navigate via the menu or tiles.\n"
            "  Do NOT scroll. Do NOT retype.\n"
        )

    frustration_note = ""
    _dropout_trigger = (getattr(persona, "dropout_trigger", "") or "").strip()
    if frustration_ratio >= 0.75:
        frustration_note = (
            f"\n⚠️  PATIENCE SIGNAL: {persona.name} is at {frustration_ratio:.0%} of their "
            f"patience budget. Prolonged blocking is likely to cause a drop-off."
        )
        if _dropout_trigger:
            frustration_note += f" Their breaking point: \"{_dropout_trigger}\""
        frustration_note += (
            f" Consider writing code that shows signs of giving up — "
            f"or set terminal_reason='persona_chose_to_leave' if nothing relevant is visible.\n"
        )

    auth_note = ""
    if auth_mode == "logged_out":
        auth_note = (
            "\n🚫 AUDIT BOUNDARY (logged-out): if you reach a form that collects personal "
            "details, mobile number, or OTP — set terminal_reason='reached_application_boundary' "
            "and task['done']=True rather than proceeding.\n"
        )

    synonym_note = ""
    if intent_synonyms:
        synonym_note = f"\n  Site may label this as: {intent_synonyms}"

    # Derive a search term from the persona's intent
    search_term = _extract_search_term(persona.intent or "")

    # Build the persona-ordered navigation code block
    _nav_block = _build_instinct_navigation_block(
        persona_name=persona.name,
        strategy_sequence=_strategy_sequence,
        search_term=search_term,
        c_lo=_c_lo, c_hi=_c_hi,
        t_lo=_t_lo, t_hi=_t_hi,
        scroll_pct=_scroll_pct,
    )

    return f"""════════════════════════════════════════════════════════
WHO YOU ARE
════════════════════════════════════════════════════════
You are {persona.name}. Not an automation script. Not a QA bot. A real person.
Every single line of code you write must feel like it came from this person's hands.

PERSONA PROFILE
  Intent        : {persona.intent}{synonym_note}
{persona_block}

YOUR HUMAN TIMING (use these exact ranges in your code):
  Typing speed  : {_t_lo}–{_t_hi}s per character  ← persona-derived, not generic
  Pre-tap pause : {_c_lo}–{_c_hi}s before each click/tap
  Scrolling     : {_scroll_desc}

════════════════════════════════════════════════════════
JOURNEY SO FAR  (step {step_number}, last 6 steps)
════════════════════════════════════════════════════════
{history_block}
{frustration_note}{auth_note}{overlay_warning}
{("━" * 54 + chr(10) + "PATTERN ALERT" + chr(10) + "━" * 54 + chr(10) + _repetition_note + chr(10) + chr(10)) if _repetition_note else ""}════════════════════════════════════════════════════════
WHAT {persona.name.upper()} SEES RIGHT NOW
════════════════════════════════════════════════════════
  URL   : {state.url}
  Title : {state.title}

👁  INTERACTIVE ELEMENTS IN THE CURRENT VIEWPORT (the ONLY things visible):
{vp_block}

[Screenshot attached — this is exactly what {persona.name} is looking at]

⚠️  Elements NOT in the list above are below the fold. {persona.name} cannot see
    or tap them. Scroll first — they will appear in the next step's list.
════════════════════════════════════════════════════════
WRITE THE CODE FOR {persona.name.upper()}'S NEXT ACTION
════════════════════════════════════════════════════════
The code runs inside:
    async def __agent_step__(page, context, browser, playwright, task):

Available in scope: asyncio, re, random, viewport_click
Set task["done"] = True only when the journey is genuinely over.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HUMAN BEHAVIOUR RULES — NON-NEGOTIABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

① TYPING — always character by character, never fill() or type() all at once:
   # {persona.name} typing — triple-click selects ALL pre-filled text in the field,
   # then Control+a is a backup, then JS clears React-controlled value if needed.
   await locator.click(click_count=3)   # or: await page.mouse.click(x, y, click_count=3)
   await asyncio.sleep(0.2)
   await page.keyboard.press("Control+a")
   await asyncio.sleep(0.1)
   # JS fallback for React inputs that ignore keyboard selection
   try:
       await page.evaluate("""(() => {
           const el = document.activeElement;
           if (!el || (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA')) return;
           if (!el.value) return;
           const s = Object.getOwnPropertyDescriptor(
               el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype,
               'value')?.set;
           if (s) s.call(el, '');
           el.dispatchEvent(new Event('input',  {{ bubbles: true }}));
           el.dispatchEvent(new Event('change', {{ bubbles: true }}));
       })()""")
   except Exception: pass
   await asyncio.sleep(0.1)
   for _ch in "{search_term}":
       await page.keyboard.type(_ch)
       await asyncio.sleep(random.uniform({_t_lo}, {_t_hi}))

② CLICKING — pause before tapping, like a real person deciding:
   await asyncio.sleep(random.uniform({_c_lo}, {_c_hi}))   # {persona.name} hesitates/considers
   await viewport_click(locator)                             # NEVER call .click() directly

③ SCROLLING — gradual thumb flicks, not one big jump:
   # scroll in 2-3 small steps with pauses between
   for _ in range(2):
       await page.evaluate("window.scrollBy(0, Math.round(window.innerHeight * 0.35))")
       await asyncio.sleep(random.uniform(0.3, 0.7))

④ AFTER NAVIGATION — always wait for page to settle:
   await page.wait_for_load_state("domcontentloaded", timeout=10000)
   await asyncio.sleep(random.uniform(0.6, 1.2))   # {persona.name} reads/orients

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW {persona.name.upper()} NAVIGATES — follow their instinct
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{_instinct_text}

{_nav_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HARD BLOCKS (these will crash the step if violated)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗  page.goto()          — no direct URL navigation, ever
✗  fill("entire text")  — humans don't paste, they type
✗  locator.click()      — always use viewport_click(locator) instead
✗  window.location = …  — no JS URL assignment

ELEMENT FINDING — most to least reliable:
   page.get_by_role("link",   name=re.compile(r"text", re.I))
   page.get_by_role("button", name=re.compile(r"text", re.I))
   page.get_by_text("text", exact=False)
   page.locator("[aria-label*='keyword' i]")

Always wrap every action block in try/except so one failure doesn't abort the step.

RULE ZERO: Every millisecond of timing, every hesitation, every scroll speed reflects
{persona.name}'s actual psychology. Write code for this person. Not for a robot."""


# ── Engine class ───────────────────────────────────────────────────────────────

class DecisionEngine:
    """
    Two-phase decision engine.

    Phase 1 — deliberate(): persona thinks through their next move and commits to
    an action type + target. Returns an inner_monologue that is the auditable
    record of why they did what they did.

    Phase 2 — decide(): receives the committed deliberation and writes the
    Playwright code that executes it, plus all BRD CX observation fields.
    The reasoning field in Phase 2 MUST reference the inner_monologue from Phase 1.

    This makes every action independently justifiable: the inner_monologue
    preceded and constrained the code — it is not post-hoc rationalization.
    """

    def __init__(self) -> None:
        self._client = OpenAIResponsesClient()

    @staticmethod
    def _compress_screenshot(path: str) -> Optional[str]:
        """Return base64-encoded JPEG (72%, max 1280px) for the screenshot."""
        if not path or not Path(path).exists():
            return None
        try:
            if _PIL_AVAILABLE:
                img = _PILImage.open(path)
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                w, h = img.size
                if w > 1280:
                    img = img.resize((1280, int(h * 1280 / w)), _PILImage.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=72, optimize=True)
                return base64.b64encode(buf.getvalue()).decode("ascii")
            else:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("ascii")
        except Exception:
            return None

    @staticmethod
    def _persona_timing(persona: Persona) -> tuple[float, float, float, float, str, str]:
        """Return (t_lo, t_hi, c_lo, c_hi, scroll_pct, scroll_desc) for a persona."""
        _lit = (getattr(persona, "financial_literacy", None) or "medium").lower()
        _nav = (getattr(persona, "navigation_style",  None) or "").lower()
        _pat = (getattr(persona, "patience",           None) or "medium").lower()
        _age = str(getattr(persona, "age", "") or "")

        if "low" in _lit or any(d in _age for d in ["5", "6", "7", "8"]):
            t_lo, t_hi = 0.18, 0.40
        elif "high" in _lit and any(w in _nav for w in ["quick", "fast", "tech"]):
            t_lo, t_hi = 0.05, 0.13
        else:
            t_lo, t_hi = 0.10, 0.24

        if "cautious" in _nav or "low" in _lit or "anxious" in _pat:
            c_lo, c_hi = 0.8, 2.0
        elif any(w in _nav for w in ["impulsive", "quick"]):
            c_lo, c_hi = 0.2, 0.6
        else:
            c_lo, c_hi = 0.4, 1.2

        if "low" in _pat:
            scroll_pct, scroll_desc = "25–35%", "small thumb flicks (25-35% viewport)"
        else:
            scroll_pct, scroll_desc = "40–60%", "moderate thumb scrolls (40-60% viewport)"

        return t_lo, t_hi, c_lo, c_hi, scroll_pct, scroll_desc

    async def deliberate(
        self,
        persona: Persona,
        state: PageState,
        memory: JourneyMemory,
        step_number: int,
        screenshot_path: str = "",
        frustration_ratio: float = 0.0,
    ) -> dict:
        """
        Phase 1: persona thinks through their next move and commits to it.

        Returns a dict with:
          inner_monologue        — first-person present-tense decision reasoning
          intended_action        — action type committed to
          intended_target        — what they will interact with
          emotional_state        — how they feel right now
          confidence_to_continue — high / medium / low
        """
        _lit = (getattr(persona, "financial_literacy", None) or "medium").lower()
        _age = str(getattr(persona, "age", "") or "")
        _nav = (getattr(persona, "navigation_style",  None) or "").lower()
        _pat = (getattr(persona, "patience",           None) or "medium").lower()

        _instinct_text, _strategy_sequence = _derive_navigation_instinct(
            persona, _lit, _age, _nav, _pat
        )
        _pattern_note = _repetition_nudge(memory.steps, persona.name, _pat)

        system_prompt = _build_deliberation_prompt(
            persona=persona,
            state=state,
            memory=memory,
            step_number=step_number,
            frustration_ratio=frustration_ratio,
            instinct_text=_instinct_text,
            pattern_note=_pattern_note,
        )

        content: list[dict] = []
        img_b64 = self._compress_screenshot(screenshot_path)
        if img_b64:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{img_b64}",
                "detail": "high",
            })
        content.append({"type": "input_text", "text": (
            "Look at the screenshot above. Think through your next move and commit."
        )})

        try:
            raw = await self._client.create_json(
                system_prompt=system_prompt,
                input_content=content,
                schema_name="deliberation",
                schema=_DELIBERATION_RESPONSE_SCHEMA,
                max_output_tokens=400,
            )
            return dict(raw)
        except Exception as exc:
            return {
                "inner_monologue": f"(deliberation failed: {exc})",
                "intended_action": "scroll_down",
                "intended_target": "page — scrolling to find relevant content",
                "emotional_state": "curious",
                "confidence_to_continue": "medium",
            }

    async def decide(
        self,
        persona: Persona,
        state: PageState,
        memory: JourneyMemory,
        step_number: int,
        auth_mode: str = "logged_out",
        screenshot_path: str = "",
        deliberation: Optional[dict] = None,
        # Legacy parameters kept for call-site compatibility
        loop_warning: bool = False,
        scroll_warning: bool = False,
        intent_synonyms: str = "",
        homepage_prescan: bool = False,
        homepage_strategy: Optional[str] = None,
        homepage_search_kw: str = "",
        homepage_strategy_step: int = 0,
        frustration_ratio: float = 0.0,
    ) -> dict:
        """
        Phase 2: write Playwright code that executes the committed deliberation,
        plus all BRD CX observation fields.

        If deliberation is provided, uses the new _build_action_prompt (short,
        execution-focused). Falls back to _build_system_prompt if not provided
        (backwards compatibility with any caller that skips Phase 1).
        """
        t_lo, t_hi, c_lo, c_hi, scroll_pct, _ = self._persona_timing(persona)
        search_term = _extract_search_term(persona.intent or "")

        _lit = (getattr(persona, "financial_literacy", None) or "medium").lower()
        _age = str(getattr(persona, "age", "") or "")
        _nav = (getattr(persona, "navigation_style",  None) or "").lower()
        _pat = (getattr(persona, "patience",           None) or "medium").lower()
        _, _strategy_sequence = _derive_navigation_instinct(persona, _lit, _age, _nav, _pat)

        if deliberation:
            system_prompt = _build_action_prompt(
                persona=persona,
                state=state,
                deliberation=deliberation,
                step_number=step_number,
                auth_mode=auth_mode,
                t_lo=t_lo, t_hi=t_hi,
                c_lo=c_lo, c_hi=c_hi,
                scroll_pct=scroll_pct,
                search_term=search_term,
                strategy_sequence=_strategy_sequence,
            )
        else:
            system_prompt = _build_system_prompt(
                persona=persona,
                state=state,
                memory=memory,
                step_number=step_number,
                auth_mode=auth_mode,
                intent_synonyms=intent_synonyms,
                frustration_ratio=frustration_ratio,
            )

        content: list[dict] = []
        img_b64 = self._compress_screenshot(screenshot_path)
        if img_b64:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{img_b64}",
                "detail": "high",
            })

        page_text = state.to_prompt_block()
        content.append({"type": "input_text", "text": (
            f"PAGE STATE (supplementary DOM context):\n{page_text}\n\n"
            "Write the playwright_code and fill all required CX fields. "
            "Your reasoning MUST reference the inner_monologue from the committed decision above."
        )})

        t0 = time.monotonic()
        try:
            raw = await self._client.create_json(
                system_prompt=system_prompt,
                input_content=content,
                schema_name="webwright_decision",
                schema=_DECISION_RESPONSE_SCHEMA,
            )
        except Exception as exc:
            return {
                "playwright_code": "await asyncio.sleep(1)",
                "action": f"API error: {exc}",
                "terminal_reason": None,
                "reasoning": f"OpenAI API error: {exc}",
                "emotion": None,
                "cx_note": "",
                "cognitive_load": "",
                "trust_signals": "",
                "unanswered_questions": "",
                "guiding_factors": "",
                "visible_content": "",
                "_elapsed_ms": 0,
            }

        result = dict(raw)
        result.setdefault("playwright_code", "await asyncio.sleep(1)")
        result.setdefault("action", "unknown action")
        result.setdefault("terminal_reason", None)
        result.setdefault("reasoning", "")
        result.setdefault("emotion", None)
        result.setdefault("cx_note", "")
        result.setdefault("cognitive_load", "")
        result.setdefault("trust_signals", "")
        result.setdefault("unanswered_questions", "")
        result.setdefault("guiding_factors", "")
        result.setdefault("visible_content", "")
        result["_elapsed_ms"] = int((time.monotonic() - t0) * 1000)

        return result
