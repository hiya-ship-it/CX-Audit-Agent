"""
Central configuration — loaded once at import time.
All tunables come from environment variables (.env file).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).parent

# ── Output directories ────────────────────────────────────────────────────────
REPORTS_DIR     = BASE_DIR / "reports"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"   # BRD §1.3: screenshots/{persona-slug}/step_{N}.png
LOGS_DIR        = BASE_DIR / "logs"
VIDEOS_DIR      = BASE_DIR / "videos"
DESIGN_KB_DIR   = BASE_DIR / "design_kb"

for _d in (REPORTS_DIR, SCREENSHOTS_DIR, LOGS_DIR, VIDEOS_DIR, DESIGN_KB_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── OpenAI ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL           = os.getenv("OPENAI_MODEL", "gpt-4.1")
OPENAI_TIMEOUT         = float(os.getenv("OPENAI_TIMEOUT", "120"))
OPENAI_TIMEOUT_SECONDS = OPENAI_TIMEOUT   # alias used by llm/openai_responses.py

# ── Target ────────────────────────────────────────────────────────────────────
TARGET_URL = os.getenv("TARGET_URL", "https://www.bajajfinserv.in")

# ── Agent loop ────────────────────────────────────────────────────────────────
MAX_STEPS              = int(os.getenv("MAX_STEPS", "50"))
CONSECUTIVE_FAIL_LIMIT = int(os.getenv("CONSECUTIVE_FAIL_LIMIT", "4"))  # BRD §1.7 Condition C

# ── Browser ───────────────────────────────────────────────────────────────────
HEADED           = os.getenv("HEADED", "true").lower() == "true"
SLOW_MO          = int(os.getenv("SLOW_MO", "0"))        # use natural timing; explicit delays below
MOBILE_EMULATION = os.getenv("MOBILE_EMULATION", "true").lower() == "true"
RECORD_VIDEO     = os.getenv("RECORD_VIDEO", "true").lower() == "true"
DEBUG_MODE       = os.getenv("DEBUG_MODE", "false").lower() == "true"

PAGE_TIMEOUT    = 30_000   # ms
ELEMENT_TIMEOUT = 5_000    # ms

# ── Human-like timing (BRD Principle 4) ──────────────────────────────────────
ACTION_DELAY_MIN_MS = int(os.getenv("ACTION_DELAY_MIN_MS",  "700"))   # ms between actions
ACTION_DELAY_MAX_MS = int(os.getenv("ACTION_DELAY_MAX_MS", "1800"))   # ms between actions
TYPING_DELAY_MS     = int(os.getenv("TYPING_DELAY_MS",      "120"))   # ms per character
