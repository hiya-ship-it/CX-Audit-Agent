"""
Agent Controller   --  THE CORE AGENT LOOP
-----------------------------------------
Orchestrates the full OpenAI + Playwright cycle for one persona journey.

Design principle: the controller is a neutral executor. It does NOT judge
whether the persona succeeded or failed — that is the evaluators' job.
The controller's only responsibilities are:
   -- Drive the step loop: capture state → ask model → execute action → repeat.
   -- Enforce purely mechanical terminal conditions:
        max_steps, consecutive_failures, loop_detected, login_wall_mobile_entry.
   -- The ONE content-aware rule: for logged_out audits, end the journey the
        moment the persona types a mobile number — that is the authentication
        boundary beyond which a logged-out audit cannot go.
   -- Pre-execution action validation (validate_action) — fails fast.
   -- Loop detection — records (action, target, url) fingerprints in memory;
        aborts if the same state recurs 2+ times in 6 steps.
   -- Per-step JSONL file logging to logs/{persona_slug}.jsonl for debugging.
   -- DEBUG_MODE: slower execution, extra console output, 10-step cap.
"""
from __future__ import annotations

import asyncio
import json
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Patterns that indicate the agent is about to click a FINAL submission button.
# We stop BEFORE the click executes so no real application is submitted.
# Terminal reason: "done" (the agent's journey ends naturally at this boundary).
_GENERIC_CTA_RE = re.compile(
    r'\b('
    r'apply\s+now|apply\s+here|apply\s+online'
    r'|get\s+started|start\s+now|start\s+here'
    r'|check\s+eligibility|check\s+now|check\s+offer'
    r'|know\s+more|learn\s+more|read\s+more|view\s+more|see\s+more|explore\s+more'
    r'|click\s+here|tap\s+here|proceed|continue'
    r'|explore|discover|find\s+out|get\s+offer'
    r'|book\s+now|register\s+now|enquire\s+now'
    r')\b',
    re.I,
)

_FINAL_SUBMIT_RE = re.compile(
    r'\b('
    r'submit\s+(?:application|form|loan|request|now)'
    r'|confirm\s+(?:&|and)\s+(?:submit|apply|proceed)'
    r'|final\s+(?:submit|confirm|review\s+&\s+submit)'
    r'|complete\s+(?:application|your\s+application)'
    r'|i\s+agree\s+(?:&|and)\s+(?:submit|apply|proceed)'
    r'|proceed\s+to\s+(?:submit|disbursal|disbursement)'
    r'|confirm\s+(?:application|loan|submission)'
    r')\b',
    re.I,
)

from rich.console import Console
from rich.markup import escape as _markup_escape
from rich.panel import Panel
from rich.text import Text

import config
from parsers.persona_parser import Persona
from browser.controller import BrowserController, ActionResult
from agents.decision_engine import DecisionEngine
from agents.memory import JourneyMemory, _normalise_fp_target

console = Console()


# "" Helpers """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def _persona_to_dict(persona: "Persona") -> dict:
    """Serialize a Persona to a plain dict for storage in JourneyMemory."""
    return {
        "name":               persona.name,
        "age":                str(persona.age) if persona.age else "",
        "gender":             persona.gender or "",
        "occupation":         persona.occupation or "",
        "location":           persona.location or "",
        "device":             persona.device or "",
        "financial_literacy": persona.financial_literacy or "",
        "intent":             persona.intent,
        "constraints":        persona.constraints or "",
        "behaviour":          persona.behaviour or "",
        "success_criteria":   persona.success_criteria or "",
        **{k: v for k, v in (persona.raw_attributes or {}).items()
           if k not in ("name", "age", "gender", "occupation", "location",
                        "device", "financial literacy", "intent", "constraints",
                        "behaviour", "behavior", "success criteria")},
    }




_INTENT_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "credit",
    "need", "needs", "want", "wants", "find", "apply", "application",
    "eligibility", "startup", "expansion", "facility", "product", "finance",
    "financing", "pre", "approval", "about", "looking", "look", "buy",
    "purchase", "open", "start",
}


_PRODUCT_TERMS = (
    "loan", "loans", "insurance", "card", "cards", "emi", "fd", "deposit",
    "deposits", "mutual fund", "mutual funds", "sip", "investment",
    "investments", "wallet", "account", "accounts", "recharge", "bill",
    "bills", "payment", "payments", "health", "life", "motor", "car",
    "bike", "two wheeler", "two-wheeler", "property", "gold", "business",
    "personal", "home", "travel", "device", "electronics", "shopping",
)

_KNOWN_PRODUCT_PHRASES = (
    "business loan", "working capital", "personal loan", "home loan", "gold loan",
    "loan against property", "loan against mutual fund", "two wheeler loan",
    "two-wheeler loan", "health insurance", "life insurance", "car insurance",
    "motor insurance", "emi card", "bajaj emi card", "fixed deposit",
    "mutual fund", "investment", "sip",
)

# ── Semantic synonym groups ───────────────────────────────────────────────────
# Each frozenset is a cluster of terms that mean the same product category.
# Any intent keyword that belongs to the same group as a tile label is a match,
# regardless of the exact words used. This handles abbreviations, synonyms,
# Indian English variants, and any user phrasing for the same product.
_SEMANTIC_GROUPS: list[frozenset[str]] = [
    # ── Consumer electronics ──────────────────────────────────────────────────
    frozenset([
        "smartphone", "smartphones", "mobile", "mobiles", "mobilephone",
        "mobilephones", "phone", "phones", "cellphone", "cellphones",
        "handset", "handsets", "android", "iphone", "smart phone",
        "smart phones", "mobile phone", "mobile phones",
    ]),
    frozenset([
        "laptop", "laptops", "notebook", "notebooks", "computer", "computers",
        "pc", "macbook", "chromebook", "ultrabook", "netbook",
    ]),
    frozenset([
        "tv", "tvs", "television", "televisions", "smart tv", "smart tvs",
        "led tv", "oled", "qled", "monitor", "display", "screen",
        "smart television",
    ]),
    frozenset([
        "refrigerator", "refrigerators", "fridge", "fridges", "freezer",
        "freezers", "double door", "single door", "side by side fridge",
    ]),
    frozenset([
        "ac", "acs", "air conditioner", "air conditioners", "airconditioner",
        "airconditioners", "air-conditioner", "split ac", "window ac",
        "cooling", "inverter ac", "air conditioning",
    ]),
    frozenset([
        "washing machine", "washing machines", "washer", "washers",
        "dryer", "dryers", "clothes washer", "front load", "top load",
        "laundry machine",
    ]),
    frozenset([
        "camera", "cameras", "dslr", "mirrorless", "digital camera",
        "action camera", "gopro", "webcam", "dashcam", "security camera",
    ]),
    frozenset([
        "tablet", "tablets", "ipad", "android tablet", "tab",
    ]),
    frozenset([
        "headphone", "headphones", "earphone", "earphones", "earbuds",
        "earbud", "neckband", "neckbands", "tws", "wireless earbuds",
        "bluetooth earphones", "audio", "speaker", "speakers",
        "soundbar", "headset",
    ]),
    frozenset([
        "smartwatch", "smartwatches", "watch", "watches", "fitness band",
        "fitness tracker", "wearable", "wristband",
    ]),
    frozenset([
        "printer", "printers", "scanner", "scanners", "projector",
        "projectors", "gaming console", "console", "xbox", "playstation",
        "nintendo",
    ]),
    frozenset([
        "personal care", "grooming", "trimmer", "trimmers", "shaver",
        "shavers", "epilator", "hair dryer", "straightener", "iron",
        "electric toothbrush",
    ]),
    frozenset([
        "kitchen appliance", "kitchen appliances", "mixer", "grinder",
        "blender", "juicer", "microwave", "oven", "toaster", "chimney",
        "dishwasher", "induction", "pressure cooker", "rice cooker",
        "water purifier", "ro", "roti maker",
    ]),
    frozenset([
        "furniture", "sofa", "couch", "bed", "mattress", "wardrobe",
        "almirah", "chair", "table", "desk", "dining", "bookshelf",
        "cabinet", "shoe rack",
    ]),
    frozenset([
        "fitness equipment", "gym equipment", "treadmill", "cycle",
        "exercise bike", "dumbbells", "gym", "elliptical",
    ]),
    # ── Financial loans ───────────────────────────────────────────────────────
    frozenset([
        "personal loan", "personal loans", "pl", "instant loan",
        "salary loan", "cash loan", "quick loan", "unsecured loan",
    ]),
    frozenset([
        "home loan", "home loans", "housing loan", "housing loans",
        "mortgage", "property loan", "house loan",
    ]),
    frozenset([
        "business loan", "business loans", "msme loan", "sme loan",
        "working capital", "enterprise loan", "merchant loan",
        "shop loan", "commercial loan",
    ]),
    frozenset([
        "gold loan", "gold loans", "loan against gold", "jewel loan",
        "jewellery loan",
    ]),
    frozenset([
        "two wheeler loan", "two-wheeler loan", "two wheeler loans",
        "bike loan", "scooter loan", "motorcycle loan", "two wheeler",
        "two-wheeler", "bike", "scooter", "motorcycle", "moped",
    ]),
    frozenset([
        "car loan", "car loans", "vehicle loan", "auto loan",
        "four wheeler loan", "automobile loan",
    ]),
    frozenset([
        "education loan", "education loans", "student loan",
        "study loan", "college loan",
    ]),
    frozenset([
        "loan against property", "lap", "property loan",
        "mortgage loan", "loan against securities",
    ]),
    # ── Insurance ─────────────────────────────────────────────────────────────
    frozenset([
        "health insurance", "medical insurance", "mediclaim",
        "health cover", "health plan", "family health",
        "critical illness", "hospital cover",
    ]),
    frozenset([
        "life insurance", "term insurance", "term plan", "term life",
        "life cover", "endowment plan", "ulip",
    ]),
    frozenset([
        "car insurance", "motor insurance", "vehicle insurance",
        "auto insurance", "four wheeler insurance", "comprehensive insurance",
        "third party insurance",
    ]),
    frozenset([
        "bike insurance", "two wheeler insurance", "two-wheeler insurance",
        "scooter insurance", "motorcycle insurance",
    ]),
    frozenset([
        "travel insurance", "trip insurance", "travel cover",
    ]),
    frozenset([
        "home insurance", "property insurance", "house insurance",
    ]),
    # ── Investment / savings ──────────────────────────────────────────────────
    frozenset([
        "fixed deposit", "fd", "fixed deposits", "fds", "term deposit",
        "recurring deposit", "rd",
    ]),
    frozenset([
        "mutual fund", "mutual funds", "mf", "sip", "equity fund",
        "debt fund", "elss", "index fund",
    ]),
    # ── EMI / payments ────────────────────────────────────────────────────────
    frozenset([
        "emi", "emis", "emi card", "insta emi", "bajaj emi",
        "no cost emi", "zero cost emi", "easy emi", "buy now pay later",
        "bnpl", "pay later",
    ]),
    frozenset([
        "credit card", "credit cards", "card", "bajaj card", "co-brand card",
    ]),
]

# Precompute a fast lookup: normalized_term → frozenset of all normalized synonyms
def _build_semantic_index(
    groups: list[frozenset[str]],
) -> dict[str, frozenset[str]]:
    """Build O(1) lookup table: compact-normalized term → its full synonym set."""
    idx: dict[str, frozenset[str]] = {}
    for group in groups:
        normed = frozenset(re.sub(r"\s+", "", t.lower()).rstrip("s") for t in group)
        for t in group:
            key = re.sub(r"\s+", "", t.lower()).rstrip("s")
            if key not in idx:
                idx[key] = normed
    return idx

_SEMANTIC_INDEX: dict[str, frozenset[str]] = _build_semantic_index(_SEMANTIC_GROUPS)


def _semantic_match(a: str, b: str) -> bool:
    """
    Return True if a and b belong to the same semantic product group.
    Handles: synonyms, abbreviations, compound words, plurals, spacing variants.
    Examples:
      "mobile"     ↔ "Smart Phones"   → True
      "fridge"     ↔ "Refrigerator"   → True
      "AC"         ↔ "Air Conditioner" → True
      "bike loan"  ↔ "Two Wheeler Loan" → True
    """
    def norm(s: str) -> str:
        return re.sub(r"\s+", "", s.lower()).rstrip("s")

    a_n = norm(a)
    b_n = norm(b)

    # Try exact lookup of a_n → check if b_n is in the same group
    synonyms_of_a = _SEMANTIC_INDEX.get(a_n)
    if synonyms_of_a and b_n in synonyms_of_a:
        return True

    # Try reverse: lookup b_n → check if a_n is in the same group
    synonyms_of_b = _SEMANTIC_INDEX.get(b_n)
    if synonyms_of_b and a_n in synonyms_of_b:
        return True

    # Substring fallback: handle partial matches like "phone" → "smartphon"
    # Only apply when both stems are reasonably long (avoid false positives with short strings)
    if len(a_n) >= 4 and len(b_n) >= 4:
        if synonyms_of_a and any(a_n in m or m in a_n for m in synonyms_of_a if len(m) >= 4):
            if synonyms_of_b and any(b_n in m or m in b_n for m in synonyms_of_b if len(m) >= 4):
                # Both terms are substring-related to their respective group members
                # — check if any group member from a's set overlaps b's set
                return bool(synonyms_of_a & synonyms_of_b)

    return False


def _intent_product_phrases(intent: str) -> list[str]:
    low = re.sub(r"[^a-z0-9\s-]+", " ", (intent or "").lower())
    low = re.sub(r"\s+", " ", low).strip()
    tokens = low.split()
    phrases: list[str] = []

    def add(phrase: str) -> None:
        phrase = re.sub(r"\s+", " ", phrase.strip().lower())
        if phrase and phrase not in phrases:
            phrases.append(phrase)

    for known in _KNOWN_PRODUCT_PHRASES:
        if known in low:
            add(known)

    for i in range(len(tokens)):
        for n in range(1, min(5, len(tokens) - i) + 1):
            phrase = " ".join(tokens[i:i+n])
            if not any(term in phrase for term in _PRODUCT_TERMS):
                continue
            if not any(w not in _INTENT_STOPWORDS for w in phrase.split()):
                continue
            add(phrase)

    return phrases


def _intent_keywords(intent: str) -> list[str]:
    words = [
        w for w in re.split(r"[^a-z0-9]+", (intent or "").lower())
        if len(w) > 2 and w not in _INTENT_STOPWORDS
    ]
    phrases = []
    for phrase in _intent_product_phrases(intent):
        phrases.extend(phrase.split())
    return list(dict.fromkeys([*phrases, *words]))


def _sanitize_search_query(value: str, intent: str, persona) -> str:
    """
    Reduce a verbose search query to 1-3 product-relevant keywords.
    Only acts when the value looks like a full sentence (> 3 words).
    Adapts specificity to persona financial literacy.
    """
    words = value.strip().split()
    if len(words) <= 3:
        return value  # already concise  leave it

    # Try to extract the best product phrase from the typed value first,
    # then fall back to the persona's intent if that yields nothing.
    phrases = _intent_product_phrases(value) or _intent_product_phrases(intent)
    if phrases:
        best = sorted(phrases, key=len)[0]
        literacy = (getattr(persona, "financial_literacy", "") or "").lower()
        # Low-literacy personas use the simplest term (e.g. "personal loan"  "loan")
        if "low" in literacy and " " in best:
            return best.split()[-1]
        return best

    # Fallback: top 2 non-stopword keywords
    kws = [
        w for w in re.split(r"[^a-z0-9]+", value.lower())
        if len(w) > 2 and w not in _INTENT_STOPWORDS
    ]
    return " ".join(kws[:2]) if kws else " ".join(words[:2])


def _get_intent_synonyms(intent: str) -> str:
    """
    Return up to 5 readable site-navigation labels that could represent the same
    product as the persona's intent, drawn from _SEMANTIC_GROUPS.
    Injected into the decision prompt so the model recognises alternate labels
    for the same product without needing to guess from training data.
    """
    for kw in _intent_keywords(intent):
        kw_norm = re.sub(r"\s+", "", kw.lower()).rstrip("s")
        group_normed = _SEMANTIC_INDEX.get(kw_norm)
        if not group_normed:
            continue
        for group in _SEMANTIC_GROUPS:
            if frozenset(re.sub(r"\s+", "", t.lower()).rstrip("s") for t in group) == group_normed:
                # Prefer multi-word readable forms; sort by descending word count then length
                candidates = [
                    t.title()
                    for t in sorted(group, key=lambda s: (-len(s.split()), len(s)))
                    if len(t) >= 4
                ]
                return ", ".join(candidates[:5])
    return ""


def _tile_haystack(tile: dict) -> tuple[str, str]:
    """
    Return (spaced, compact) versions of a tile's label + ctaLabel for matching.
    spaced  = normal lowercased string, e.g. "smart phones"
    compact = spaces removed,           e.g. "smartphones"
    Both forms are needed because intent keywords are compacted ("smartphone")
    while tile labels may be spaced ("Smart Phones").
    """
    label   = (tile.get("label") or "").lower()
    cta_lbl = (tile.get("ctaLabel") or "").lower()
    spaced  = f"{label} {cta_lbl}".strip()
    compact = spaced.replace(" ", "")
    return spaced, compact


def _kw_in_tile(kw: str, spaced: str, compact: str) -> bool:
    """
    True if keyword semantically matches anything in the tile text.

    Checks in order (cheapest → most expensive):
      1. Direct substring (e.g. "emi" in "emi card")
      2. Space-normalized (e.g. "smartphone" in "smartphones" compact form)
      3. Stem (e.g. "phones" → "phone" matches "phone")
      4. Semantic group (e.g. "mobile" → same group as "smart phones")
    """
    kw_compact = kw.replace(" ", "")

    # 1. Direct substring in both spaced and compact forms
    if kw in spaced or kw_compact in compact:
        return True

    # 2. Stem: strip trailing 's' from both sides
    if len(kw_compact) > 4:
        kw_stem = kw_compact.rstrip("s")
        compact_stem = compact.rstrip("s")
        if kw_stem in compact or kw_stem in compact_stem:
            return True

    # 3. Semantic group: "mobile" ↔ "smart phones", "fridge" ↔ "refrigerator", etc.
    #    Check each individual word in the tile label against the keyword.
    for tile_word in spaced.split():
        if _semantic_match(kw, tile_word):
            return True
    # Also check the full compact tile label as a single token
    if _semantic_match(kw, spaced):
        return True

    return False







def _find_intent_in_elements(elements: list, intent: str) -> Optional[dict]:
    """
    Scan visible interactive_elements for an intent-matched link/button.
    Used as a fallback when viewport_tiles is empty (e.g. non-standard tile HTML).
    Only considers elements that are visible in the viewport AND have short labels
    (long labels are likely paragraph text, not product tiles).
    """
    if not elements or not intent:
        return None
    keywords = _intent_keywords(intent)
    phrases  = _intent_product_phrases(intent)
    SKIP_TYPES = {"input", "textarea", "select"}

    for el in elements:
        if not getattr(el, "visible", False):
            continue
        el_type = getattr(el, "el_type", "")
        if el_type in SKIP_TYPES:
            continue
        label = (getattr(el, "label", "") or getattr(el, "text", "") or "").strip()
        if not label or len(label) > 70:
            continue

        spaced  = label.lower()
        compact = spaced.replace(" ", "")

        for phrase in phrases:
            if phrase in spaced or phrase.replace(" ", "") in compact:
                return {"label": label, "ctaLabel": label, "ctaHref": ""}

        for kw in keywords:
            if _kw_in_tile(kw, spaced, compact):
                return {"label": label, "ctaLabel": label, "ctaHref": ""}

    return None


def _find_intent_tile(tiles: list[dict], intent: str) -> Optional[dict]:
    """
    Return the best intent-matched tile from viewport_tiles, or None.
    Used to intercept scroll actions when a relevant tile is already visible.

    Handles space-split mismatches:
      intent keyword "smartphone" matches tile label "Smart Phones"
      because "smartphones" (compact keyword) is found in "smartphones" (compact tile).
    """
    if not tiles or not intent:
        return None
    keywords = _intent_keywords(intent)
    phrases  = _intent_product_phrases(intent)
    best       = None
    best_score = 0

    for tile in tiles:
        spaced, compact = _tile_haystack(tile)

        # Multi-word phrase match — highest confidence
        for phrase in phrases:
            phrase_compact = phrase.replace(" ", "")
            if phrase in spaced or phrase_compact in compact:
                score = len(phrase.split()) * 10
                if score > best_score:
                    best_score = score
                    best = tile
                break

        # Single-keyword match — require at least 1 strong hit
        # (tiles are product-specific, so 1 keyword match is usually enough)
        if best is not tile:
            kw_hits = sum(1 for kw in keywords if _kw_in_tile(kw, spaced, compact))
            if kw_hits >= 1:
                score = kw_hits * 2
                if score > best_score:
                    best_score = score
                    best = tile

    return best


# "" Journey result """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

@dataclass
class JourneyResult:
    persona:         Persona
    memory:          JourneyMemory
    duration_secs:   float
    completed:       bool          # True = simulation ran; False = technical crash only
    terminal_reason: str


# "" Agent controller """"""""""""""""""""""""""""""""""""""""""""""""""""""""""

class AgentController:
    """
    Runs one persona's complete journey from start to terminal state.

    Usage:
        engine = DecisionEngine()
        ctrl   = AgentController(engine)
        result = await ctrl.run_journey(persona, target_url)
    """

    def __init__(self, decision_engine: DecisionEngine) -> None:
        self._engine = decision_engine

    async def run_journey(
        self,
        persona:        Persona,
        target_url:     str = config.TARGET_URL,
        max_steps:      int = config.MAX_STEPS,
        auth_mode:      str = "logged_out",
        start_from:     str = "homepage",
        login_url:      str = "",
        login_username: str = "",
        login_password: str = "",
    ) -> JourneyResult:

        # Debug mode: cap steps and slow everything down
        if config.DEBUG_MODE:
            max_steps = min(max_steps, 10)
            console.print(
                "[bold yellow]DEBUG MODE ON[/bold yellow] -- "
                f"max_steps capped at {max_steps}, SLOW_MO={config.SLOW_MO}"
            )

        memory  = JourneyMemory(persona.name, persona.intent, persona_data=_persona_to_dict(persona))
        log_path = config.LOGS_DIR / f"{persona.slug}.jsonl"
        memory._jsonl_path = log_path
        t_start  = time.monotonic()

        _patience_map = {"low": 3, "medium": 8, "high": 15}
        _patience_level = (getattr(persona, "patience", None) or "medium").strip().lower()
        _patience_threshold = _patience_map.get(_patience_level, 8)

        console.print(Panel(
            f"[bold cyan]Starting journey[/bold cyan]\n"
            f"Persona       : [yellow]{persona.name}[/yellow]\n"
            f"Intent        : {persona.intent}\n"
            f"Patience      : [magenta]{_patience_level}[/magenta]\n"
            f"Nav style     : [cyan]{getattr(persona, 'navigation_style', 'default') or 'default'}[/cyan]\n"
            f"Dropout signal: [dim]{(getattr(persona, 'dropout_trigger', '') or '')[:100]}[/dim]\n"
            f"Target        : {target_url}",
            title=" Agent Loop",
            border_style="cyan",
        ))

        async with BrowserController() as browser:
            browser.set_artifact_prefix(persona.slug)

            # "" Navigate to start URL (or run Google entry flow) """""""""""""
            if start_from == "google":
                console.print(f"[cyan]Starting from Google Search for: {persona.intent}[/cyan]")
                google_entry = await self._run_google_entry(browser, persona, target_url, log_path)
                memory.google_entry = google_entry
                landed = google_entry.get("landed_url", "")
                # If Google result landed on a login/webform/auth URL, that's a
                # friction point worth noting but we shouldn't start the journey there.
                # Navigate to BFL homepage so the agent can explore normally.
                _is_auth_landing = landed and any(
                    tok in landed for tok in ["/login", "/myaccount", "/webform", "/auth", "sign-in", "signin"]
                )
                if _is_auth_landing:
                    console.print(
                        f"[yellow]Google landed on auth/login URL: {landed[:80]} "
                        f"-- navigating to BFL homepage to start journey.[/yellow]"
                    )
                    landed = ""  # reset so fallback navigation fires
                if not landed:
                    console.print("[yellow]Google entry found no usable Bajaj result -- falling back to direct navigation.[/yellow]")
                    nav_result = await browser.navigate(target_url)
                    if not nav_result.success:
                        memory.mark_terminal("navigation_failed")
                        return JourneyResult(
                            persona=persona, memory=memory,
                            duration_secs=time.monotonic() - t_start,
                            completed=False, terminal_reason="navigation_failed",
                        )
            else:
                console.print(f"[cyan]Opening target URL in Chrome: {target_url}[/cyan]")
                nav_result = await browser.navigate(target_url)
                _append_log(log_path, {
                    "step": -1, "event": "initial_navigate",
                    "url": target_url, "success": nav_result.success,
                    "error": nav_result.error,
                })
                try:
                    console.print(f"[dim]Chrome current URL: {browser.page.url}[/dim]")
                except Exception:
                    pass
                if not nav_result.success:
                    console.print(
                        f"[red]Initial navigation failed: {nav_result.error}[/red]"
                    )
                    memory.mark_terminal("navigation_failed")
                    return JourneyResult(
                        persona=persona, memory=memory,
                        duration_secs=time.monotonic() - t_start,
                        completed=False, terminal_reason="navigation_failed",
                    )

            if auth_mode == "logged_in" and not login_username:
                console.print(
                    "[bold red]Logged-in audit requested but mobile number is missing "
                    "- running as logged_out.[/bold red]"
                )
                auth_mode = "logged_out"

            # "" Main agent loop """""""""""""""""""""""""""""""""""""""""""""""
            terminal_reason = "max_steps"
            consecutive_loops = 0   # tracks back-to-back loop detections
            # Set to True once the persona types a mobile number into any field.
            # For logged_out audits this is the authentication boundary —
            # the journey ends immediately when the type action is executed.
            _entered_login_mobile: bool = False

            # Per-persona steps dir: reports/{slug}/steps/ — BRD Section 13
            steps_dir = config.REPORTS_DIR / persona.slug / "steps"

            # Take an initial screenshot before step 0 so OpenAI can see the
            # landing page visually on the very first decision.
            prev_screenshot = await browser.screenshot(
                f"{persona.slug}_step-1_initial",
                steps_dir=steps_dir,
            )
            if prev_screenshot:
                memory.initial_screenshot = prev_screenshot
                # Capture page state and record the homepage as step -1 so it
                # appears as the first entry in the journey timeline everywhere
                # (JSONL, journey_log.json, dashboard) — not just the evaluator.
                _home_state = await browser.get_state()
                memory.add_step(
                    step_number=-1,
                    url=_home_state.url,
                    page_title=_home_state.title or "Homepage",
                    decision={
                        "action":      "navigate",
                        "target":      target_url,
                        "reasoning":   "Journey start — initial homepage load",
                        "observation": "Landing page captured before any persona action.",
                        "emotion":     "hopeful",
                        "cx_note":     "First impression of the homepage.",
                    },
                    result=ActionResult(
                        success=True,
                        action="navigate",
                        target=target_url,
                        notes="Initial homepage load",
                    ),
                    screenshot=prev_screenshot,
                )
                _append_log(log_path, {
                    "step": -1, "event": "homepage_captured",
                    "url": _home_state.url, "screenshot": prev_screenshot,
                })

            # Synonym labels for this persona's intent — computed once, injected
            # into every decide() call so the model can match site terminology.
            _intent_synonyms = _get_intent_synonyms(persona.intent)

            for step_num in range(max_steps):
              try:
                console.rule(
                    f"[dim]Step {step_num + 1}/{max_steps}  "
                    f"{_markup_escape(persona.name[:20])}[/dim]"
                )

                # 1. STATE CAPTURE ----------------------------------------
                try:
                    state = await browser.get_state()
                except Exception as _state_exc:
                    console.print(
                        f"[bold red]Step {step_num}: state capture failed "
                        f"({_state_exc}) -- stopping.[/bold red]"
                    )
                    _append_log(log_path, {
                        "step": step_num, "event": "state_capture_failed",
                        "error": str(_state_exc),
                    })
                    terminal_reason = "fatal_error"
                    break
                _log_state(step_num, state)

                # 2. LOGGED-IN: handle login wall -------------------------
                if auth_mode == "logged_in" and _is_login_wall(state):
                    console.print(
                        f"  [bold cyan]Login wall reached ({state.url[:70]}) "
                        f"-- entering credentials.[/bold cyan]"
                    )
                    _append_log(log_path, {"step": step_num,
                                            "event": "login_wall_detected",
                                            "url": state.url})
                    login_ok = await self._perform_login(
                        browser, "", login_username, login_password, log_path
                    )
                    if login_ok:
                        prev_screenshot = await browser.screenshot(
                            f"{persona.slug}_step{step_num}_post_login",
                            steps_dir=steps_dir,
                        )
                        continue
                    console.print("[bold yellow]Login failed -- continuing as logged_out.[/bold yellow]")
                    auth_mode = "logged_out"
                    continue

                # 2b. ACCESS DENIED AUTO-RECOVERY ----------------------
                # The site's search endpoint returns a broken "Access Denied"
                # page for certain queries.  Detect it before deliberation,
                # go back automatically, and permanently ban search for the
                # rest of this journey so the persona doesn't repeat the same
                # mistake — a real user would pivot, not retry what just failed.
                _BROKEN_SEARCH_PATHS = [
                    "/myaccount/search/content",
                    "/search/content",
                ]
                _is_access_denied = (
                    any(p in state.url for p in _BROKEN_SEARCH_PATHS)
                    or "access denied" in (state.title or "").lower()
                )
                if _is_access_denied:
                    console.print(
                        "  [bold red]Access Denied page detected — "
                        "auto-recovering, banning search for this journey.[/bold red]"
                    )
                    # Record the failure so deliberation can see it
                    memory.failed_actions.append({
                        "step":   step_num,
                        "action": "search",
                        "target": "search bar",
                        "error":  "Access Denied — site's search navigation is broken",
                        "tag":    "search_access_denied",
                    })
                    _append_log(log_path, {
                        "step": step_num, "event": "access_denied_auto_recovery",
                        "url": state.url,
                    })
                    # Go back without counting this as a step
                    try:
                        await browser.page.go_back()
                        await browser.page.wait_for_load_state(
                            "domcontentloaded", timeout=8000
                        )
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass
                    continue   # do not deliberate, do not add_step

                # 3. URL-RUT DETECTION -----------------------------------
                if _is_url_rut(memory, state.url, rut_threshold=3):
                    console.print(
                        f"[bold red]URL rut: '{state.url[:70]}' seen 3+ times.[/bold red]"
                    )
                    _append_log(log_path, {"step": step_num,
                                            "event": "url_rut_detected",
                                            "url": state.url})
                    terminal_reason = "loop_detected"
                    break

                # 4. SCREENSHOT (before decision) -------------------------
                prev_screenshot = await browser.screenshot(
                    f"{persona.slug}_step{step_num:02d}",
                    steps_dir=steps_dir,
                    step_num=step_num,
                )

                # 5. PHASE 1 — DELIBERATION: persona thinks, then commits ----
                _frustration_ratio = step_num / max(_patience_threshold, 1)
                try:
                    _deliberation = await asyncio.wait_for(
                        self._engine.deliberate(
                            persona=persona,
                            state=state,
                            memory=memory,
                            step_number=step_num,
                            screenshot_path=prev_screenshot,
                            frustration_ratio=_frustration_ratio,
                        ),
                        timeout=45,
                    )
                except (asyncio.TimeoutError, Exception) as _delib_exc:
                    _deliberation = {
                        "inner_monologue": f"(deliberation unavailable: {_delib_exc})",
                        "intended_action": "scroll_down",
                        "intended_target": "page — scrolling to find content",
                        "emotional_state": "curious",
                        "confidence_to_continue": "medium",
                    }

                _monologue = _deliberation.get("inner_monologue", "")
                _intended  = _deliberation.get("intended_action", "?")
                _target    = _deliberation.get("intended_target", "")
                _emotion   = _deliberation.get("emotional_state", "")
                _conf      = _deliberation.get("confidence_to_continue", "medium")
                console.print(
                    f"  [bold magenta]Thinking ({_emotion}, {_conf}):[/bold magenta] "
                    f"[italic]{_monologue[:180]}[/italic]"
                )
                console.print(
                    f"  [magenta]Committed:[/magenta] {_intended} → {_target[:80]}"
                )
                _append_log(log_path, {
                    "step": step_num, "event": "deliberation",
                    "inner_monologue": _monologue,
                    "intended_action": _intended,
                    "intended_target": _target,
                    "emotional_state": _emotion,
                    "confidence": _conf,
                })

                # 5b. PHASE 2 — ACTION: write code for the committed decision --
                try:
                    decision = await asyncio.wait_for(
                        self._engine.decide(
                            persona=persona,
                            state=state,
                            memory=memory,
                            step_number=step_num,
                            auth_mode=auth_mode,
                            screenshot_path=prev_screenshot,
                            deliberation=_deliberation,
                            intent_synonyms=_intent_synonyms,
                            frustration_ratio=_frustration_ratio,
                        ),
                        timeout=120,
                    )
                except asyncio.TimeoutError:
                    console.print("[red]OpenAI timed out (120s) -- inserting wait[/red]")
                    decision = {
                        "playwright_code": "await asyncio.sleep(1)",
                        "action": "wait (API timeout)",
                        "terminal_reason": None,
                        "reasoning": "API timeout",
                        "emotion": None, "cx_note": "",
                        "cognitive_load": "", "trust_signals": "",
                        "unanswered_questions": "", "guiding_factors": "",
                        "visible_content": "",
                    }
                except Exception as _api_exc:
                    console.print(f"[red]Decision engine error: {_api_exc}[/red]")
                    decision = {
                        "playwright_code": "await asyncio.sleep(1)",
                        "action": f"error: {_api_exc}",
                        "terminal_reason": None,
                        "reasoning": str(_api_exc),
                        "emotion": None, "cx_note": "",
                        "cognitive_load": "", "trust_signals": "",
                        "unanswered_questions": "", "guiding_factors": "",
                        "visible_content": "",
                    }

                # Merge inner_monologue into decision so it reaches add_step()
                decision["inner_monologue"] = _monologue

                _action_summary = decision.get("action", "")
                _elapsed_ms     = decision.get("_elapsed_ms", 0)
                console.print(
                    f"  [cyan]Decision ({_elapsed_ms}ms):[/cyan] {_action_summary[:100]}"
                )
                _append_log(log_path, {
                    "step": step_num, "event": "decision",
                    "action": _action_summary,
                    "terminal_reason": decision.get("terminal_reason"),
                    "url": state.url, "elapsed_ms": _elapsed_ms,
                })

                # 6. PAGE CHANGE DURING API CALL? -------------------------
                try:
                    _url_now = browser.page.url
                except Exception:
                    _url_now = state.url
                if _url_now != state.url:
                    console.print("  [yellow]Page drifted during API call -- refreshing.[/yellow]")
                    state = await browser.get_state()
                    _fresh = await browser.screenshot(
                        f"{persona.slug}_step{step_num:02d}_refreshed",
                        steps_dir=steps_dir, step_num=step_num,
                    )
                    if _fresh:
                        prev_screenshot = _fresh

                # 7. TERMINAL REASON FROM MODEL ---------------------------
                _terminal = decision.get("terminal_reason")
                if _terminal:
                    console.print(f"  [bold cyan]Journey ended: {_terminal}[/bold cyan]")
                    memory.add_step(
                        step_number=step_num, url=state.url,
                        page_title=state.title, decision=decision,
                        result=ActionResult(
                            success=True,
                            action=_action_summary,
                            notes=f"Terminal: {_terminal}",
                        ),
                        screenshot=prev_screenshot,
                    )
                    _append_log(log_path, {
                        "step": step_num, "event": "journey_ended_by_model",
                        "terminal_reason": _terminal,
                        "emotion": decision.get("emotion", ""),
                    })
                    terminal_reason = _terminal
                    break

                # 8. EXECUTE PLAYWRIGHT CODE (Webwright code-as-action) ---
                playwright_code = decision.get("playwright_code", "")
                exec_result = await browser.execute_code(playwright_code)

                _exec_success = exec_result.get("success", False)
                _exec_done    = exec_result.get("done", False)
                _exec_stdout  = exec_result.get("stdout", "")
                _exec_error   = exec_result.get("error", "")

                if config.DEBUG_MODE:
                    console.print(
                        f"  [dim]Code: success={_exec_success} done={_exec_done}[/dim]"
                    )
                    if _exec_stdout:
                        console.print(f"  [dim]stdout: {_exec_stdout[:300]}[/dim]")
                    if _exec_error:
                        console.print(f"  [yellow]code error: {_exec_error[:200]}[/yellow]")

                # 8b. CODE TIMEOUT — don't count this as a journey step ----
                # A timeout is a technical failure, not a persona action.
                # Skip add_step() so it doesn't appear in the journey log or
                # consume the step budget visible in the report.
                if _exec_error and "timed out" in _exec_error.lower():
                    console.print(
                        f"  [bold yellow]Code timed out — retrying "
                        f"(step {step_num + 1}/{max_steps} not counted)[/bold yellow]"
                    )
                    _append_log(log_path, {
                        "step": step_num, "event": "code_timeout_skipped",
                        "action": _action_summary, "error": _exec_error,
                    })
                    continue   # back to top of loop — same step_num re-runs

                if _exec_error and not _exec_success:
                    console.print(f"  [yellow]Code error: {_exec_error[:120]}[/yellow]")
                    _append_log(log_path, {
                        "step": step_num, "event": "code_error",
                        "error": _exec_error, "action": _action_summary,
                    })

                # 9. WAIT FOR PAGE SETTLEMENT ----------------------------
                await browser.wait_after_action()

                # 10. POST-STEP SCREENSHOT --------------------------------
                post_screenshot = await browser.screenshot(
                    f"{persona.slug}_step{step_num:02d}_post",
                    steps_dir=steps_dir,
                    step_num=step_num,
                )

                # 11. RECORD TO JOURNEY MEMORY ---------------------------
                memory.add_step(
                    step_number=step_num,
                    url=state.url,
                    page_title=state.title,
                    decision={
                        **decision,
                        "observation": (
                            _exec_stdout[:500]
                            if _exec_stdout
                            else (f"Error: {_exec_error[:200]}" if _exec_error else "ok")
                        ),
                    },
                    result=ActionResult(
                        success=_exec_success,
                        action=_action_summary,
                        error=_exec_error,
                    ),
                    screenshot=post_screenshot or prev_screenshot,
                )

                # 12. CODE SET done=True? --------------------------------
                if _exec_done:
                    console.print(
                        "  [bold cyan]Code set task['done']=True -- ending.[/bold cyan]"
                    )
                    terminal_reason = "done"
                    break

                # 13. CONSECUTIVE FAILURE LIMIT --------------------------
                if not _exec_success:
                    if memory.consecutive_failures >= config.CONSECUTIVE_FAIL_LIMIT:
                        console.print("[bold red]Consecutive failure limit reached.[/bold red]")
                        terminal_reason = "consecutive_failures"
                        break

                prev_screenshot = post_screenshot or prev_screenshot
                await asyncio.sleep(0)   # yield to event loop

              except Exception as _step_exc:
                import traceback as _step_tb
                _step_err = _step_tb.format_exc()
                console.print(
                    f"[bold red]UNHANDLED exception in step {step_num}: "
                    f"{_step_exc}[/bold red]\n[dim]{_step_err}[/dim]"
                )
                _append_log(log_path, {
                    "step": step_num,
                    "event": "step_loop_exception",
                    "error": str(_step_exc),
                    "traceback": _step_err,
                })
                terminal_reason = "fatal_error"
                break

            # "" Final screenshot """"""""""""""""""""""""""""""""""""""""""""""
            await browser.screenshot(
                f"{persona.slug}_final",
                steps_dir=steps_dir,
            )

        memory.video_path = getattr(browser, "video_path", "") or ""
        memory.mark_terminal(terminal_reason)
        duration = time.monotonic() - t_start

        _append_log(log_path, {
            "event": "journey_complete",
            "terminal_reason": terminal_reason,
            "steps": memory.step_count,
            "failures": memory.failure_count,
            "duration_secs": round(duration, 2),
        })

        _technical_failures = {"navigation_failed", "consecutive_failures"}
        console.print(Panel(
            f"[bold]Journey complete[/bold]\n"
            f"Terminal : [yellow]{terminal_reason}[/yellow]\n"
            f"Steps    : {memory.step_count}\n"
            f"Failures : {memory.failure_count}\n"
            f"Duration : {duration:.1f}s\n"
            f"Log      : {log_path}",
            title=" Journey Summary",
            border_style="red" if terminal_reason in _technical_failures else "cyan",
        ))

        return JourneyResult(
            persona=persona, memory=memory,
            duration_secs=duration,
            completed=(terminal_reason not in _technical_failures),
            terminal_reason=terminal_reason,
        )

    # "" Login helper """""""""""""""""""""""""""""""""""""""""""""""""""""""""

    async def _perform_login(
        self,
        browser:        BrowserController,
        login_url:      str,
        username:       str,
        password:       str,       # unused for OTP-based sites; kept for API compat
        log_path:       Path,
        otp_wait_secs:  int = 120, # how long to wait for manual OTP entry
    ) -> bool:
        """
        OTP-aware login flow for Bajaj Finserv (and similar mobile-OTP sites).

        Steps:
          1. Navigate to login page
          2. Enter mobile number
          3. Click the 'Send OTP' / 'Get OTP' button
          4. PAUSE  -- print a clear message telling the user to enter the OTP
             in the browser window (which is visible in headed mode)
          5. Poll the URL every 2 s for up to otp_wait_secs
          6. When URL leaves the OTP page, declare login successful

        Falls back gracefully if the site uses username+password instead of OTP.
        """
        location = login_url or "current page"
        console.print(Panel(
            f"[bold cyan]Performing login[/bold cyan]\n"
            f"Location  : {location}\n"
            f"Mobile    : {username[:3]}{'*' * max(0, len(username) - 3)}",
            title=" Login",
            border_style="cyan",
        ))

        if login_url:
            nav = await browser.navigate(login_url)
            if not nav.success:
                console.print(f"[red]Login navigation failed: {nav.error}[/red]")
                return False

        await asyncio.sleep(2)

        # "" Step 1: Enter mobile number """""""""""""""""""""""""""""""""""""""
        # Try direct CSS selectors first (most reliable for OTP-based fintech sites),
        # then fall back to natural language descriptions.
        typed = False

        # CSS/attribute selectors targeting phone number inputs
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
                console.print(f"  [green] Entered mobile number (selector: {sel})[/green]")
                break
            except Exception:
                continue

        # Fallback to natural language targets
        if not typed:
            for target in [
                "mobile number field", "mobile number or email field",
                "username or email field", "email field", "username field",
            ]:
                result = await browser.execute({"action": "type", "target": target, "value": username})
                if result.success:
                    typed = True
                    console.print(f"  [green] Entered mobile number (target: {target})[/green]")
                    break

        if not typed:
            console.print("[yellow] Could not find mobile/username field  -- you may need to type it manually[/yellow]")

        await asyncio.sleep(0.8)

        # "" Step 2: Click 'Send OTP' or equivalent """"""""""""""""""""""""""""
        otp_triggered = False
        for target in [
            "Get OTP", "Send OTP", "Request OTP", "Generate OTP",
            "LOGIN", "Log In", "Continue", "Proceed",
            "login button", "sign in button", "submit button",
        ]:
            result = await browser.execute({"action": "click", "target": target})
            if result.success:
                otp_triggered = True
                console.print(f"  [green] Clicked '{target}'[/green]")
                break

        await asyncio.sleep(3)   # wait for page to react to button click

        # "" Step 3: Capture current URL as baseline """""""""""""""""""""""""""
        state = await browser.get_state()
        url_before = state.url

        # "" Step 4: Always wait for user to complete login in the browser """""
        # We do NOT try to detect "OTP needed vs not needed"  -- that logic is
        # fragile and has caused false positives. Instead we always hand over
        # to the user and poll until the URL leaves the login/auth area.
        console.print(Panel(
            "[bold yellow]YOUR ACTION REQUIRED  -- COMPLETE LOGIN IN THE BROWSER[/bold yellow]\n\n"
            "The browser is open and waiting.\n\n"
            "  1. Switch to the browser window now\n"
            "  2. If an OTP was sent to your phone  -- enter it and click Verify\n"
            "  3. If you see a CAPTCHA  -- complete it\n"
            "  4. Once you are on the post-login page, come back here\n\n"
            f"This terminal will detect login automatically.\n"
            f"Waiting up to [cyan]{otp_wait_secs} seconds[/cyan]...",
            title=" Complete Login in Browser",
            border_style="yellow",
        ))

        # "" Step 5: Poll every 2s until the page moves past login """"""""""""
        # "Past login" = URL has changed AND does not contain login/otp keywords
        _login_keywords = ("login", "signin", "sign-in", "/auth", "otp", "verify",
                           "access", "password")

        poll_interval = 2
        elapsed       = 0

        while elapsed < otp_wait_secs:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            state = await browser.get_state()
            current_url = state.url

            url_changed      = current_url != url_before
            still_in_auth    = any(k in current_url.lower() for k in _login_keywords)

            # Success: URL changed AND we are not on any auth/login-looking page
            if url_changed and not still_in_auth:
                console.print(
                    f"\n[bold green] Login complete! Now at: {current_url[:100]}[/bold green]"
                )
                _append_log(log_path, {"event": "login_complete", "url": current_url})
                return True

            # Progress reminder every 30s
            if elapsed % 30 == 0:
                remaining = otp_wait_secs - elapsed
                console.print(
                    f"  [dim]Waiting for login... {int(remaining)}s remaining. "
                    f"Current page: {current_url[:60]}[/dim]"
                )

        # "" Timeout """""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        console.print(Panel(
            "[bold red]Login timeout[/bold red]\n\n"
            f"No successful login detected after {otp_wait_secs}s.\n"
            "The audit will now run as a logged-out session.\n\n"
            "To retry: run the command again and complete login faster.",
            title=" Login Timeout",
            border_style="red",
        ))
        _append_log(log_path, {"event": "login_timeout", "waited_secs": otp_wait_secs})
        return False

    # "" Retry / fallback logic """"""""""""""""""""""""""""""""""""""""""""""""

    async def _execute_with_retry(
        self,
        browser:  BrowserController,
        decision: dict,
        state,
    ) -> tuple[ActionResult, bool]:
        """
        Attempt an action up to MAX_RETRIES times.
          attempt 0 ' original action
          attempt 1 ' same action again (transient failure may resolve)
          attempt 2 ' use OpenAI's fallback description

        FIX: result is initialised to a failure stub before the loop so it is
        always bound even if MAX_RETRIES=0 or all iterations skip.
        """
        fallback_text = decision.get("fallback", "")
        used_fallback = False

        # Initialise to a "never ran" failure  -- overwritten on first attempt
        result = ActionResult(
            success=False,
            action=decision.get("action", "unknown"),
            target=decision.get("target", ""),
            error="No execution attempts made (MAX_RETRIES=0?)",
        )

        for attempt in range(max(1, config.MAX_RETRIES)):
            if attempt == 0:
                exec_decision = decision
            elif attempt == 1:
                exec_decision = dict(decision)   # exact retry
                console.print(
                    f"  [yellow] Retry {attempt}/{config.MAX_RETRIES - 1}[/yellow]"
                )
                await asyncio.sleep(0.5)
            else:
                # Fallback strategy
                if fallback_text and _fallback_is_executable(fallback_text):
                    exec_decision = _build_fallback_decision(
                        decision, fallback_text, state
                    )
                    used_fallback = True
                    console.print(
                        f"  [yellow] Fallback: {fallback_text[:80]}[/yellow]"
                    )
                else:
                    break   # no fallback available  -- exit retry loop

            try:
                result = await browser.execute(exec_decision)
            except Exception as _exec_exc:
                console.print(
                    f"  [bold red]browser.execute crashed: {_exec_exc}[/bold red]"
                )
                result = ActionResult(
                    success=False,
                    action=exec_decision.get("action", "unknown"),
                    target=exec_decision.get("target", ""),
                    error=f"browser.execute crash: {_exec_exc}",
                )
                break  # no point retrying a crashed browser

            if result.success:
                return result, used_fallback

            if exec_decision.get("action") == "scroll":
                return result, used_fallback

            await asyncio.sleep(0.8)

        return result, used_fallback

    #  Google Search entry flow 

    async def _run_google_entry(
        self,
        browser,
        persona,
        target_url: str,
        log_path: Path,
    ) -> dict:
        """
        Navigate to Google, search for the persona's intent + 'bajaj finserv',
        record Bajaj URL positions in results, click the first one, and return
        a google_entry dict with the captured metrics.
        """
        from urllib.parse import quote_plus, parse_qs, urlparse, unquote
        import re as _re

        ge: dict = {
            "query":               "",
            "rank":                None,   # SERP position of the URL the persona clicked
            "first_bajaj_rank":    None,   # SERP position of the top-most Bajaj result
            "first_bajaj_url":     "",     # URL of that top-most Bajaj result
            "clicked_bajaj_rank":  None,   # same as rank; explicit for dashboard clarity
            "relevance_skip":      False,  # True when persona skipped the top Bajaj result
            "scroll_depth":        None,
            "landed_url":          "",
            "urls_found":          [],
        }

        try:
            page = browser.page

            # 1. Navigate to Google
            await browser.navigate("https://www.google.com")
            await asyncio.sleep(1.5)

            # 2. Handle consent / cookie popup (multiple selector attempts)
            consent_selectors = [
                'button[aria-label="Accept all"]',
                'button:has-text("Accept all")',
                'button:has-text("I agree")',
                '#L2AGLb',
                'button.tHlp8d',
                'form[action*="consent"] button[type="submit"]',
            ]
            for sel in consent_selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=1500):
                        try:
                            box = await btn.bounding_box()
                            if box:
                                cx = box["x"] + box["width"] / 2
                                cy = box["y"] + box["height"] / 2
                                await page.evaluate(
                                    """([cx, cy]) => {
                                        const d = document.createElement('div');
                                        d.style.cssText = [
                                            'position:fixed','z-index:2147483647',
                                            'pointer-events:none','border-radius:50%',
                                            'left:'+(cx-13)+'px','top:'+(cy-13)+'px',
                                            'width:26px','height:26px',
                                            'background:rgba(255,100,0,0.18)',
                                            'border:2.5px solid rgba(255,90,0,0.9)',
                                        ].join(';');
                                        document.body.appendChild(d);
                                    }""", [cx, cy]
                                )
                                await browser.screenshot(f"{persona.slug}_google_consent_click")
                        except Exception:
                            pass
                        await btn.click()
                        await asyncio.sleep(0.8)
                        break
                except Exception:
                    pass

            # 3. Build a persona-appropriate query -- MUST contain "bajaj"
            query = await _build_google_query(persona, self._engine._client)
            # Hard-guarantee "bajaj" is in the query so BFL results appear
            if "bajaj" not in query.lower():
                query = query.strip() + " bajaj finserv"
            ge["query"] = query
            console.print(f"[cyan]Google search query: \"{query}\"[/cyan]")

            # 4. Try typing the query into Google's search box (best effort).
            #    On mobile emulation the search input selector can differ.
            search_typed = False
            search_selectors = [
                'textarea[name="q"]',
                'input[name="q"]',
                '[role="combobox"]',
                'input[type="search"]',
                'input[type="text"]',
            ]
            for sel in search_selectors:
                try:
                    inp = page.locator(sel).first
                    if not await inp.is_visible(timeout=2000):
                        continue
                    try:
                        box = await inp.bounding_box()
                        if box:
                            cx = box["x"] + box["width"] / 2
                            cy = box["y"] + box["height"] / 2
                            await page.evaluate(
                                """([cx, cy]) => {
                                    const d = document.createElement('div');
                                    d.id = '__cx_google_dot__';
                                    d.style.cssText = [
                                        'position:fixed','z-index:2147483647',
                                        'pointer-events:none','border-radius:50%',
                                        'left:'+(cx-13)+'px','top:'+(cy-13)+'px',
                                        'width:26px','height:26px',
                                        'background:rgba(255,100,0,0.18)',
                                        'border:2.5px solid rgba(255,90,0,0.9)',
                                    ].join(';');
                                    document.body.appendChild(d);
                                }""", [cx, cy]
                            )
                            await browser.screenshot(f"{persona.slug}_google_searchbox_click")
                            await page.evaluate(
                                "() => { const e=document.getElementById('__cx_google_dot__'); if(e) e.remove(); }"
                            )
                    except Exception:
                        pass
                    await inp.click()
                    await asyncio.sleep(0.3)
                    await inp.fill(query)
                    await asyncio.sleep(0.3)
                    await inp.press("Enter")
                    search_typed = True
                    console.print(f"[green]Search typed via selector: {sel}[/green]")
                    break
                except Exception as e:
                    console.print(f"[dim]Selector {sel} failed: {e}[/dim]")

            # 5. If search box typing failed, navigate directly to Google SERP URL.
            #    This is NOT the same as going to BFL homepage -- we still arrive
            #    on the Google SERP and will click the BFL result from there.
            serp_url = f"https://www.google.com/search?q={quote_plus(query)}"
            if not search_typed:
                console.print(
                    f"[yellow]Search box not found on Google page -- "
                    f"navigating directly to SERP URL: {serp_url[:80]}[/yellow]"
                )
                _append_log(log_path, {"step": -1, "event": "google_serp_direct", "url": serp_url})
                try:
                    await page.goto(serp_url, wait_until="domcontentloaded",
                                    timeout=config.PAGE_TIMEOUT)
                except Exception as nav_exc:
                    console.print(f"[red]SERP navigation failed: {nav_exc}[/red]")

            # 6. Wait for SERP to fully render
            await asyncio.sleep(3.0)
            try:
                await browser._wait_for_visual_settle(timeout_ms=3000)
            except Exception:
                pass
            await browser.screenshot(f"{persona.slug}_google_serp")

            current_url = page.url
            console.print(f"[dim]SERP page URL after wait: {current_url[:100]}[/dim]")

            # 7. DIAGNOSTIC: dump first 40 link hrefs to console so we can see
            #    exactly what Google has rendered.
            try:
                all_link_hrefs = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a')).slice(0, 40).map(a => ({
                        href:    a.href    || '',
                        raw:     a.getAttribute('href') || '',
                        text:    (a.innerText || '').trim().slice(0, 50),
                        visible: (a.offsetWidth > 0 && a.offsetHeight > 0),
                    }));
                }
                """)
                bfl_found_diag = [
                    h for h in all_link_hrefs
                    if 'bajajfinserv' in h['href'].lower() or 'bajajfinserv' in h['raw'].lower()
                ]
                console.print(
                    f"[dim]SERP diagnostic -- total <a> tags: {len(all_link_hrefs)}, "
                    f"BFL links: {len(bfl_found_diag)}[/dim]"
                )
                if bfl_found_diag:
                    for lnk in bfl_found_diag[:3]:
                        console.print(f"[dim]  BFL link: {lnk['href'][:90]}[/dim]")
                else:
                    # Log first 10 hrefs to see what IS on the page
                    for lnk in all_link_hrefs[:10]:
                        console.print(f"[dim]  link: {lnk['href'][:70] or lnk['raw'][:70]}[/dim]")
            except Exception as diag_exc:
                console.print(f"[dim]Diagnostic failed: {diag_exc}[/dim]")

            # 8. Find the first visible Bajaj Finserv link on the SERP.
            #    Strategy A: scan all <a> tags -- link.href is the browser-expanded URL
            #    which covers direct hrefs, /url?q=... relative redirects, and
            #    https://www.google.com/url?q=... absolute redirects.
            def _make_bfl_js(extra_scroll: int = 0) -> str:
                return f"""
                () => {{
                    {"window.scrollTo(0," + str(extra_scroll) + ");" if extra_scroll else ""}
                    // Collect all organic result containers (Google uses several layouts).
                    const resultSelectors = [
                        'div.g',
                        'div[data-sokoban-container]',
                        'div[jscontroller] > div[lang]',
                        '.MjjYud > div[class]',
                    ];
                    const seen = new Set();
                    const allResults = [];
                    for (const sel of resultSelectors) {{
                        for (const el of document.querySelectorAll(sel)) {{
                            if (!seen.has(el)) {{ seen.add(el); allResults.push(el); }}
                        }}
                    }}

                    // Collect ALL Bajaj links (not just the first) so the persona
                    // can choose the most intent-relevant one.
                    const bajajLinks = [];
                    const seenUrls   = new Set();
                    for (const link of document.querySelectorAll('a')) {{
                        const fullHref  = link.href || '';
                        const rawHref   = link.getAttribute('href') || '';
                        const dataAttrs = Array.from(link.attributes)
                            .filter(a => a.name.startsWith('data-'))
                            .map(a => a.value).join('|');
                        const allText = (fullHref + '|' + rawHref + '|' + dataAttrs).toLowerCase();
                        if (!allText.includes('bajajfinserv.in')) continue;
                        if (seenUrls.has(fullHref)) continue;
                        seenUrls.add(fullHref);
                        const rect = link.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) continue;

                        // SERP position + result title
                        let serpRank = null, title = '';
                        for (let i = 0; i < allResults.length; i++) {{
                            if (allResults[i].contains(link)) {{
                                serpRank = i + 1;
                                const h3 = allResults[i].querySelector('h3');
                                title = h3 ? h3.innerText.trim() : link.innerText.trim().slice(0, 100);
                                break;
                            }}
                        }}
                        if (!title) title = link.innerText.trim().slice(0, 100) || fullHref;

                        bajajLinks.push({{
                            fullHref,
                            rawHref,
                            cx:         rect.left + rect.width  / 2,
                            cy:         rect.top  + rect.height / 2,
                            top:        rect.top,
                            inViewport: rect.top >= 0 && rect.bottom <= window.innerHeight,
                            serpRank,
                            title,
                        }});
                    }}
                    return bajajLinks.length > 0 ? bajajLinks : null;
                }}
                """

            all_bfl_results = await page.evaluate(_make_bfl_js())

            # Strategy B: scroll down 400px and re-scan (results may be below fold)
            if not all_bfl_results:
                await page.evaluate("window.scrollTo(0, 400)")
                await asyncio.sleep(0.5)
                all_bfl_results = await page.evaluate(_make_bfl_js())

            # Strategy C: extract BFL URLs from raw HTML via regex
            bfl_direct_url: str = ""
            if not all_bfl_results:
                console.print("[yellow]DOM scan found no BFL link -- trying raw HTML extraction[/yellow]")
                try:
                    html = await page.content()
                    raw_matches = _re.findall(
                        r'https?://(?:www\.)?bajajfinserv\.in[^"\'&\s<>]*', html,
                    )
                    if raw_matches:
                        bfl_direct_url = raw_matches[0]
                        console.print(f"[yellow]Raw HTML extraction found: {bfl_direct_url[:80]}[/yellow]")
                        ge["urls_found"] = raw_matches[:5]
                    else:
                        console.print("[red]No bajajfinserv.in URL found anywhere on SERP page.[/red]")
                except Exception as html_exc:
                    console.print(f"[yellow]HTML extraction failed: {html_exc}[/yellow]")

            # Sort by serpRank so index 0 is always the top-most Bajaj result
            if all_bfl_results:
                all_bfl_results.sort(key=lambda r: (r.get("serpRank") or 999))

            ge["urls_found"] = (
                [r["fullHref"] for r in all_bfl_results] if all_bfl_results
                else ge["urls_found"]
            )

            # ── Persona-driven result selection (vision-based) ────────────────
            # The persona sees the SERP screenshot and decides which Bajaj result
            # to click — exactly like a real human would. Their age, digital
            # literacy, intent, and behaviour all influence the choice.
            #
            # Hard rule: the persona MUST click some Bajaj URL so the journey
            # can continue. If the vision call fails, we fall back to the
            # top-ranked Bajaj result (index 0 after sorting by serpRank).
            result_info: "dict | None" = None
            if all_bfl_results:
                console.print(
                    f"[green]{len(all_bfl_results)} Bajaj result(s) found on SERP.[/green]"
                )
                for r in all_bfl_results:
                    console.print(
                        f"  [dim]#{r.get('serpRank','?')} "
                        f"{r.get('title','')[:55]} — {r['fullHref'][:55]}[/dim]"
                    )

                if len(all_bfl_results) == 1:
                    # Only one option — no decision needed
                    result_info = all_bfl_results[0]
                else:
                    # Multiple options — ask the persona (via vision) which to click
                    result_info = await _persona_choose_serp_result(
                        all_results   = all_bfl_results,
                        persona       = persona,
                        page          = page,
                        llm_client    = self._engine._client,
                    )

                console.print(
                    f"[green]Persona chose: #{result_info.get('serpRank','?')} "
                    f"'{result_info.get('title','')[:50]}' — "
                    f"{result_info['fullHref'][:55]}[/green]"
                )

            console.print(
                f"[{'green' if result_info else ('yellow' if bfl_direct_url else 'red')}]"
                f"SERP result: "
                f"{'Clicking: ' + result_info['fullHref'][:70] if result_info else ('raw URL: ' + bfl_direct_url[:70] if bfl_direct_url else 'NO BFL RESULT FOUND')}"
                f"[/{'green' if result_info else ('yellow' if bfl_direct_url else 'red')}]"
            )

            # 9. Click the result or navigate to the extracted URL
            clicked_ok = False

            if result_info:
                first_result  = all_bfl_results[0]  # top-most Bajaj on SERP
                clicked_result = result_info          # what persona chose

                # Record both ranks independently
                ge["first_bajaj_rank"] = first_result.get("serpRank")
                ge["first_bajaj_url"]  = first_result["fullHref"]
                ge["clicked_bajaj_rank"] = clicked_result.get("serpRank")
                ge["rank"]             = ge["clicked_bajaj_rank"]   # backward compat
                ge["scroll_depth"]     = "above_fold" if clicked_result.get("inViewport") else "below_fold"
                ge["relevance_skip"]   = (
                    ge["first_bajaj_rank"] is not None
                    and ge["clicked_bajaj_rank"] is not None
                    and ge["clicked_bajaj_rank"] > ge["first_bajaj_rank"]
                )

                # CX observation when persona skips the top Bajaj result
                if ge["relevance_skip"]:
                    memory.add_cx_observation(
                        step=1, url=ge["first_bajaj_url"],
                        kind="friction",
                        note=(
                            f"For search query \"{ge['query']}\", Bajaj's top organic result "
                            f"(#{ge['first_bajaj_rank']}: \"{first_result.get('title','')}\") "
                            f"was not the most relevant URL for this persona's intent. "
                            f"The persona chose a lower-ranked result "
                            f"(#{ge['clicked_bajaj_rank']}: \"{clicked_result.get('title','')}\") "
                            f"instead — suggesting a keyword-relevance mismatch: the URL "
                            f"Bajaj ranks highest for this query does not best serve users "
                            f"with this specific intent."
                        ),
                        severity="medium",
                    )
                    console.print(
                        f"[yellow]CX insight: persona skipped Bajaj's top SERP result "
                        f"(#{ge['first_bajaj_rank']}) in favour of "
                        f"#{ge['clicked_bajaj_rank']}.[/yellow]"
                    )

                # Scroll into view if needed, then re-read coordinates
                if not clicked_result.get("inViewport"):
                    try:
                        scroll_y = max(0, clicked_result["top"] - 120)
                        await page.evaluate(f"window.scrollTo(0, {scroll_y})")
                        await asyncio.sleep(0.6)
                        # Re-read all results after scroll (coordinates shift)
                        _refreshed = await page.evaluate(_make_bfl_js())
                        if _refreshed:
                            _match = next(
                                (r for r in _refreshed if r["fullHref"] == clicked_result["fullHref"]),
                                None,
                            )
                            if _match:
                                clicked_result = _match
                    except Exception:
                        pass

                cx = clicked_result.get("cx", 0)
                cy = clicked_result.get("cy", 0)

                # Orange circle annotation at click point
                try:
                    await page.evaluate(
                        """([cx, cy]) => {
                            const d = document.createElement('div');
                            d.id = '__cx_serp_click__';
                            d.style.cssText = [
                                'position:fixed','z-index:2147483647',
                                'pointer-events:none','border-radius:50%',
                                'left:'+(cx-20)+'px','top:'+(cy-20)+'px',
                                'width:40px','height:40px',
                                'background:rgba(255,100,0,0.18)',
                                'border:3px solid rgba(255,90,0,0.9)',
                            ].join(';');
                            document.body.appendChild(d);
                        }""", [cx, cy]
                    )
                    await browser.screenshot(f"{persona.slug}_google_result_click")
                    await page.evaluate(
                        "() => { const e=document.getElementById('__cx_serp_click__'); if(e) e.remove(); }"
                    )
                except Exception:
                    pass

                # Click by mouse coordinates (bypasses Playwright locator engine)
                try:
                    await page.mouse.click(cx, cy)
                    await asyncio.sleep(3.5)
                    await browser._ensure_primary_page()
                    clicked_ok = True
                    console.print(f"[green]Clicked SERP result via mouse. Now on: {page.url[:80]}[/green]")
                except Exception as click_exc:
                    console.print(f"[yellow]Mouse click failed: {click_exc}[/yellow]")

                # If mouse click failed, navigate to the href directly
                if not clicked_ok:
                    nav_target = result_info.get("fullHref", "") or result_info.get("rawHref", "")
                    if nav_target and "google.com/url" in nav_target:
                        try:
                            qs = parse_qs(urlparse(nav_target).query)
                            nav_target = unquote(qs.get("q", [nav_target])[0])
                        except Exception:
                            pass
                    if nav_target and "bajajfinserv.in" in nav_target:
                        console.print(f"[yellow]Navigating directly to extracted URL: {nav_target[:80]}[/yellow]")
                        try:
                            await page.goto(nav_target, wait_until="domcontentloaded",
                                            timeout=config.PAGE_TIMEOUT)
                            await asyncio.sleep(2.0)
                            clicked_ok = True
                        except Exception:
                            pass

            # Strategy D: navigate to BFL URL found via raw HTML
            if not clicked_ok and bfl_direct_url:
                console.print(f"[yellow]Navigating to raw-HTML extracted URL: {bfl_direct_url[:80]}[/yellow]")
                try:
                    await page.goto(bfl_direct_url, wait_until="domcontentloaded",
                                    timeout=config.PAGE_TIMEOUT)
                    await asyncio.sleep(2.0)
                    clicked_ok = True
                except Exception:
                    pass

            # Re-apply mobile viewport after landing on Bajaj
            if config.MOBILE_EMULATION:
                try:
                    await page.set_viewport_size({"width": 360, "height": 740})
                    await page.evaluate("""
                        var m = document.querySelector('meta[name="viewport"]');
                        if (!m) {
                            m = document.createElement('meta');
                            m.name = 'viewport';
                            document.head.insertBefore(m, document.head.firstChild);
                        }
                        m.setAttribute('content',
                            'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
                    """)
                except Exception:
                    pass

            ge["landed_url"] = page.url
            console.print(f"[green]Google entry complete. Landed on: {ge['landed_url'][:100]}[/green]")

            _append_log(log_path, {"step": -1, "event": "google_entry", "data": ge})

        except Exception as exc:
            console.print(f"[red]Google entry flow error: {exc}[/red]")
            _append_log(log_path, {"step": -1, "event": "google_entry_error", "error": str(exc)})

        return ge


async def _persona_choose_serp_result(
    all_results: list,
    persona,
    page,
    llm_client,
) -> dict:
    """
    Ask the vision model to decide, AS this persona, which Bajaj SERP result
    to click. The model sees:
      - A screenshot of the actual Google results page
      - The full persona profile (age, literacy, behaviour, intent)
      - The numbered list of Bajaj options with their SERP titles and URLs

    The persona's characteristics drive the choice — a low-literacy user may
    click the first recognisable result; a tech-savvy researcher reads URLs.

    Hard guarantee: always returns one of the items from all_results.
    Falls back to index 0 (top-ranked result) on any failure.
    """
    import base64 as _b64
    import io as _io
    from agents.decision_engine import _compress_screenshot, _PIL_AVAILABLE
    from llm.openai_responses import image_content as _image_content

    # ── 1. Screenshot the current SERP ───────────────────────────────────────
    # Scroll back to top so the persona sees the SERP from the beginning,
    # the way a real user would when the page first loads.
    try:
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.4)
    except Exception:
        pass

    image_b64: str = ""
    img_w: int = 0
    try:
        _raw_ss = await page.screenshot(type="png")
        if _PIL_AVAILABLE:
            from PIL import Image as _PILImage
            with _PILImage.open(_io.BytesIO(_raw_ss)) as _img:
                _img = _img.convert("RGB")
                # Upscale narrow mobile screenshots for clarity
                if _img.width < 720:
                    _ratio = 720 / _img.width
                    _img = _img.resize((720, int(_img.height * _ratio)), _PILImage.LANCZOS)
                img_w = _img.width
                _buf = _io.BytesIO()
                _img.save(_buf, format="JPEG", quality=72, optimize=True)
                image_b64 = _b64.standard_b64encode(_buf.getvalue()).decode("utf-8")
        else:
            image_b64 = _b64.standard_b64encode(_raw_ss).decode("utf-8")
    except Exception:
        pass   # vision unavailable — will fall back to text-only below

    # ── 2. Build persona profile description ─────────────────────────────────
    _age        = getattr(persona, "age",               "") or ""
    _occ        = getattr(persona, "occupation",        "") or ""
    _loc        = getattr(persona, "location",          "") or ""
    _literacy   = getattr(persona, "financial_literacy","") or ""
    _behaviour  = getattr(persona, "behaviour",         "") or ""
    _device     = getattr(persona, "device",            "") or ""
    _constraint = getattr(persona, "constraints",       "") or ""

    _persona_block = (
        f"You are roleplaying as a real person with this profile:\n"
        f"  Name:             {persona.name}\n"
        + (f"  Age:              {_age}\n"        if _age        else "")
        + (f"  Occupation:       {_occ}\n"        if _occ        else "")
        + (f"  Location:         {_loc}\n"        if _loc        else "")
        + (f"  Digital literacy: {_literacy}\n"   if _literacy   else "")
        + (f"  Device:           {_device}\n"     if _device     else "")
        + (f"  Behaviour:        {_behaviour}\n"  if _behaviour  else "")
        + (f"  Constraints:      {_constraint}\n" if _constraint else "")
        + f"  What you want:    {persona.intent}\n"
    )

    # ── 3. List the Bajaj results ─────────────────────────────────────────────
    _results_block = (
        "The Bajaj Finserv results you can see on this Google page are:\n"
        + "\n".join(
            f"  {i+1}. [SERP position #{r.get('serpRank','?')}]  "
            f"{r.get('title','(no title)')}\n"
            f"       URL: {r['fullHref'][:90]}"
            for i, r in enumerate(all_results[:6])
        )
    )

    _instruction = (
        "\nYou MUST click one of the listed Bajaj results to continue your journey. "
        "Based on your persona profile and intent, which result would you click?\n\n"
        "Think about:\n"
        "  - Which title sounds most relevant to what YOU specifically want\n"
        "  - Whether you would read descriptions carefully or just scan titles\n"
        "  - How your digital literacy affects how you read URLs\n"
        "  - Whether you would scroll to find a better result or click the first one\n\n"
        "Reply with ONLY a single integer — the number of the result you would click."
    )

    _full_prompt = _persona_block + "\n" + _results_block + _instruction

    # ── 4. Call the vision model (falls back to text-only if no screenshot) ───
    from llm.openai_responses import text_content as _tc
    try:
        if image_b64:
            _content = _image_content(_full_prompt, image_b64, media_type="image/jpeg")
        else:
            _content = _tc(_full_prompt)

        _resp = await asyncio.wait_for(
            llm_client.respond(
                model=config.OPENAI_MODEL,
                input=[{"role": "user", "content": _content}],
                max_output_tokens=5,
            ),
            timeout=15.0,
        )
        _raw = ""
        for _blk in getattr(_resp, "output", []) or []:
            for _pt in getattr(_blk, "content", None) or []:
                if getattr(_pt, "type", "") == "output_text":
                    _raw = (_pt.text or "").strip()
                    break
            if _raw:
                break

        _idx = int(_raw) - 1
        if 0 <= _idx < len(all_results):
            return all_results[_idx]
    except Exception:
        pass

    # ── 5. Hard fallback: top-ranked Bajaj result ─────────────────────────────
    return all_results[0]


async def _build_google_query(persona, llm_client) -> str:
    """
    Ask OpenAI to produce the exact Google search string this persona would
    type -- casual, natural, their own words, not a formal product name.
    Falls back to a simple heuristic if the LLM call fails.
    """
    try:
        from llm.openai_responses import text_content
        prompt = (
            f"A real person is about to search Google. Their profile:\n"
            f"  Name: {persona.name}, Age: {getattr(persona,'age','')}, "
            f"  Occupation: {getattr(persona,'occupation','')}\n"
            f"  Digital literacy: {getattr(persona,'financial_literacy','medium')}\n"
            f"  What they want: {persona.intent}\n\n"
            f"Write ONLY the Google search query they would type -- in their own natural words, "
            f"casual phrasing (the way a real Indian mobile user types), 3-7 words max. "
            f"The query MUST include the word 'bajaj' (e.g. 'bajaj finserv personal loan', "
            f"'bajaj emi card apply', 'bajaj finserv home loan'). "
            f"No quotes, no punctuation, no explanation -- just the raw query string."
        )
        response = await llm_client.respond(
            model=config.OPENAI_MODEL,
            input=[{"role": "user", "content": text_content(prompt)}],
            max_output_tokens=40,
        )
        raw = ""
        for block in (response.output or []):
            for part in (getattr(block, "content", None) or []):
                if getattr(part, "type", "") == "output_text":
                    raw = part.text.strip().strip('"').strip("'").strip()
                    break
            if raw:
                break
        if raw and 2 <= len(raw.split()) <= 10:
            return raw
    except Exception:
        pass
    # Heuristic fallback
    phrases = _intent_product_phrases(persona.intent)
    base = sorted(phrases, key=len)[0] if phrases else ""
    if not base:
        words = [w for w in re.split(r"[^\w]+", persona.intent.lower())
                 if len(w) > 2 and w not in _INTENT_STOPWORDS]
        base = " ".join(words[:3]) if words else "loan"
    return f"{base} bajaj finserv"


# "" Helpers """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def _build_fallback_decision(
    original: dict, fallback_text: str, state
) -> dict:
    """
    Translate OpenAI's free-text fallback description into an executable
    decision dict. Recognises a few high-frequency patterns.

    IMPORTANT: This function must NEVER force a homepage navigation or any
    navigation the persona wouldn't naturally choose. If the fallback is
    ambiguous, return a short wait so OpenAI sees a fresh screenshot on the
    next step and decides AS THE PERSONA what to do (try again, scroll, search,
    go back, or end the journey). Hardcoded recovery navigations bypass the
    persona model entirely and produce unrealistic journeys.
    """
    lower = fallback_text.lower()

    if "scroll" in lower:
        direction = "up" if "up" in lower else "down"
        return {
            "action": "scroll", "scroll_direction": direction,
            "reasoning": f"Fallback: {fallback_text}",
            "observation": "Trying to reveal element by scrolling",
        }

    if "search bar" in lower or re.search(r"\buse\s+search\b|\bsite\s+search\b", lower):
        return {
            "action": "click",
            "target": "search bar or search icon",
            "reasoning": f"Fallback: {fallback_text}",
            "observation": "Using site search as alternative path",
        }

    if re.search(r"\bgo\s+back\b|\bpress\s+back\b|\breturn\s+to\s+previous\b", lower):
        return {
            "action": "back",
            "reasoning": f"Fallback: {fallback_text}",
            "observation": "Going back to previous page",
        }

    # ── Explicitly do NOT handle "navigate / url / http" here ────────────────
    # Forcing a homepage navigation when the persona encounters friction is
    # unrealistic and masks real CX problems. Instead, return a wait so the
    # agent re-evaluates the current page with a fresh screenshot on the next
    # step. OpenAI will then decide — as this persona — whether to try again,
    # scroll, use search, go back, or abandon the journey. That decision belongs
    # to the persona model, not to a hardcoded recovery heuristic.

    # Generic: treat short fallback as a new click target
    words = fallback_text.strip().split()
    if len(words) <= 8:
        return {
            "action": "click",
            "target": fallback_text,
            "reasoning": f"Fallback attempt: {fallback_text}",
            "observation": "Primary action failed — trying fallback target",
        }

    # Fallback text is a long narrative sentence — not executable as a target.
    # Pause so OpenAI reassesses on the next step with a fresh screenshot.
    return {
        "action": "wait",
        "value": "1200",
        "reasoning": (
            "Primary action failed. Pausing to let the page settle before "
            "reassessing — OpenAI will decide the next persona-appropriate step."
        ),
        "observation": "Waiting after failed action; next step will re-evaluate the page.",
    }


def _fallback_is_executable(fallback_text: str) -> bool:
    """
    Return False for narrative fallback prose like "If this does not open...".
    Those sentences are useful reasoning, but they are not executable targets.
    Treating them as commands caused real CTA clicks to be replaced by unrelated
    search-bar clicks when the text happened to contain the word "search".
    """
    text = (fallback_text or "").strip()
    if not text:
        return False
    lower = text.lower()
    if lower.startswith(("if ", "if this", "if it", "if that", "otherwise", "in case")):
        return False
    if len(text.split()) > 12 and not re.search(r"\b(scroll|go back|back|search bar|search icon)\b", lower):
        return False
    if re.search(r"\b(consider|would|may|might|try another|alternative path)\b", lower):
        return False
    return True


_LOGIN_URL_KEYWORDS = (
    "login", "signin", "sign-in", "/auth", "otp", "verify",
    "myaccount/login", "account/login", "user/login",
    "register", "signup", "sign-up",
)

def _is_safe_navigate_url(
    nav_url: str,
    target_url: str,
    memory: "JourneyMemory",
    auth_mode: str = "logged_out",
) -> bool:
    """
    Return True if navigating to nav_url is legitimate.

    Logged-out: only allow the start URL, previously visited URLs, or root-domain.
      Deep-path URLs the agent constructs from training data are rejected.

    Logged-in: allow any same-domain URL freely  -- personalised dashboard pages,
      account-specific paths, and product application paths are all new (never
      visited before) but are legitimate targets in an authenticated session.
    """
    from urllib.parse import urlparse

    # Always allow the starting target URL
    if nav_url.rstrip("/") == target_url.rstrip("/"):
        return True

    # Allow navigating back to a previously visited URL
    if nav_url in memory.visited_urls:
        return True

    parsed        = urlparse(nav_url)
    target_domain = urlparse(target_url).netloc

    # Allow root-domain navigations (no path beyond /)
    if parsed.path in ("", "/", "/#"):
        return True

    if parsed.netloc == target_domain and parsed.path in ("", "/"):
        return True

    # For logged-in audits: allow any same-domain URL freely.
    # Authenticated sessions legitimately navigate to product pages, dashboard
    # pages, and account-specific paths that have never been visited before.
    # The anti-fabrication guard only makes sense for logged-out crawls where
    # OpenAI might hallucinate URLs it learned during training.
    if auth_mode == "logged_in":
        if not parsed.netloc or parsed.netloc == target_domain:
            return True

    # Logged-out: any deep-path URL not previously visited via clicking is
    # fabricated from training memory, so reject it.
    return False


def _is_login_url(url: str) -> bool:
    """Return True if the URL looks like a login / auth / OTP page."""
    lower = url.lower()
    return any(k in lower for k in _LOGIN_URL_KEYWORDS)


def _is_login_wall(state) -> bool:
    """Return True when the current page appears to be a login / OTP gate."""
    if _is_login_url(state.url):
        return True
    text = f"{state.title} {state.visible_text}".lower()
    signals = (
        "get otp", "send otp",
        "verify otp", "login to continue", "log in to continue",
        "sign in to continue", "create account", "registered mobile",
    )
    return any(signal in text for signal in signals)


def _is_url_rut(memory: JourneyMemory, current_url: str, rut_threshold: int = 3) -> bool:
    """
    Return True if the agent has RETURNED to current_url multiple times  --"
    indicating circular navigation, not legitimate page interaction.

    Counts URL *arrivals* (steps where the URL transitioned TO current_url
    from a different URL), not raw occurrences.  This prevents false positives
    when the agent is legitimately filling a form, reading, or scrolling on a
    single URL across many steps.
    """
    window = memory.steps[-14:]
    if len(window) < 3:
        return False
    arrivals = 0
    for i in range(1, len(window)):
        if window[i].url == current_url and window[i - 1].url != current_url:
            arrivals += 1
    return arrivals >= rut_threshold


def _append_log(path: Path, entry: dict) -> None:
    """
    Append a single JSON line to a JSONL debug log file.
    Never raises  -- log failures must not crash the agent loop.
    """
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _log_state(step: int, state) -> None:
    url_short = state.url[:80] + (" --" if len(state.url) > 80 else "")
    overlay_tag = " [bold red](OVERLAY)[/bold red]" if state.has_overlay else ""
    console.print(
        f"  [dim]State[/dim]  {url_short}{overlay_tag}  "
        f"elements={len(state.interactive_elements)}"
    )
    if config.DEBUG_MODE and state.interactive_elements:
        console.print(
            f"  [dim]  Elements: "
            + ", ".join(
                f"{e.el_type}:{(e.label or e.text)[:20]!r}"
                for e in state.interactive_elements[:6]
            )
            + "[/dim]"
        )


def _log_decision(step: int, decision: dict) -> None:
    action  = decision.get("action", "?")
    target  = decision.get("target", "")
    reason  = decision.get("reasoning", "")

    colour = {
        "click": "blue", "type": "magenta", "scroll": "cyan",
        "navigate": "blue", "wait": "dim", "back": "yellow",
        "hover": "cyan",
        "done": "green", "play_video": "cyan",
    }.get(action, "white")

    t = Text()
    t.append("  Decision  ", style="dim")
    t.append(f"[{action.upper()}]", style=f"bold {colour}")
    if target:
        t.append(f" -> {_short_log_text(target, 70)}")
    console.print(t)
    if reason:
        console.print(f"  [dim]Why:[/dim] {_short_log_text(reason, 140)}")


def _log_result(result: ActionResult, screenshot: str) -> None:
    if result.success:
        console.print(
            f"  [green]OK[/green] {result.action} succeeded "
            f"({result.duration_ms}ms)"
            + (f"  [{result.notes}]" if result.notes else "")
        )
    else:
        console.print(
            f"  [red][/red] {result.action} failed: {result.error[:120]}"
        )
    if screenshot:
        console.print(f"  [dim]Screenshot: {screenshot}[/dim]")


def _short_log_text(value: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:")
    return (cut or text[:limit]).rstrip() + "..."

