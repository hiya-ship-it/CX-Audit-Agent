"""
Browser Controller
------------------
Clean Playwright wrapper. Translates action dicts from the agent into
real browser interactions with human-like timing.

BRD Principle 4 timing:
  - Random delay between actions:  700–1800 ms  (ACTION_DELAY_MIN/MAX_MS)
  - Per-character typing delay:    120 ms        (TYPING_DELAY_MS)
  - Hover before every click

Screenshot path: screenshots/{persona-slug}/step_{N:03d}.png  (BRD §1.3)
"""
from __future__ import annotations

import asyncio
import base64
import io
import logging
import random
import re
import shutil
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PwTimeout,
)

try:
    from PIL import Image as _PILImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

import config
from browser.state_extractor import extract_state, PageState

log = logging.getLogger(__name__)


# ── Action result ─────────────────────────────────────────────────────────────

class ActionResult:
    __slots__ = ("success", "action", "target", "error", "screenshot", "duration_ms")

    def __init__(
        self,
        success: bool,
        action: str,
        target: str = "",
        error: str = "",
        screenshot: str = "",
        duration_ms: int = 0,
    ) -> None:
        self.success     = success
        self.action      = action
        self.target      = target
        self.error       = error
        self.screenshot  = screenshot
        self.duration_ms = duration_ms


# ── Human-like delays ─────────────────────────────────────────────────────────

def _action_delay() -> float:
    """Random inter-action delay in seconds (BRD Principle 4: 700–1800 ms)."""
    lo = config.ACTION_DELAY_MIN_MS / 1000
    hi = config.ACTION_DELAY_MAX_MS / 1000
    return random.uniform(lo, hi)


def _typing_delay() -> float:
    """Per-character typing delay in seconds (BRD Principle 4: 120 ms)."""
    return config.TYPING_DELAY_MS / 1000


# ── JS: returns {x, y} centre of every interactive element in viewport ────────
# Used by screenshot_with_markers to draw numbered orange dots.

_ELEMENT_POSITIONS_JS = """
() => {
    const vpH = window.innerHeight;
    const vpW = window.innerWidth;
    const results = [];
    const seen = new Set();

    function inViewport(rect) {
        return rect.bottom > 4 && rect.top < vpH - 4 &&
               rect.right  > 4 && rect.left < vpW - 4 &&
               rect.width >= 8 && rect.height >= 8;
    }

    function isVisible(style) {
        return style.display !== 'none' &&
               style.visibility !== 'hidden' &&
               parseFloat(style.opacity) >= 0.1;
    }

    function tryAdd(el) {
        if (results.length >= 30) return;
        try {
            const style = window.getComputedStyle(el);
            if (!isVisible(style)) return;
            const rect = el.getBoundingClientRect();
            if (!inViewport(rect)) return;
            const cx = Math.round((rect.left + rect.right) / 2);
            const cy = Math.round((rect.top  + rect.bottom) / 2);
            const key = cx + ',' + cy;
            if (seen.has(key)) return;
            seen.add(key);
            results.push({ x: cx, y: cy });
        } catch(e) {}
    }

    // Pass 1: semantic interactive elements
    const sem = [
        'a[href]', 'button:not([disabled])',
        'input:not([type="hidden"]):not([disabled])',
        'select:not([disabled])',
        '[role="button"]', '[role="link"]', '[role="tab"]',
        '[role="menuitem"]', '[role="option"]', '[role="searchbox"]',
        '[tabindex="0"]',
    ].join(', ');
    for (const el of document.querySelectorAll(sem)) {
        tryAdd(el);
    }

    // Pass 2: cursor:pointer non-semantic elements (Angular/React tiles, CTAs)
    const nsq = [
        '[onclick]', '[ng-click]',
        '[data-href]', '[data-link]', '[data-url]', '[data-route]',
        '[class*="btn" i]', '[class*="cta" i]',
        '[class*="tile" i]', '[class*="card" i]',
        '[class*="product" i]', '[class*="item" i]',
        'li', 'div[class]', 'span[class]',
    ].join(', ');
    let p2n = 0;
    for (const el of document.querySelectorAll(nsq)) {
        if (results.length >= 30) break;
        if (p2n++ > 700) break;
        try {
            const style = window.getComputedStyle(el);
            if (style.cursor !== 'pointer') continue;
            tryAdd(el);
        } catch(e) {}
    }

    return results;
}
"""


# ── Browser controller ────────────────────────────────────────────────────────

class BrowserController:
    """
    Async context manager wrapping a Playwright browser session.

    Usage:
        async with BrowserController(persona_slug="manoj-kumar") as bc:
            await bc.navigate("https://www.bajajfinserv.in")
            state = await bc.get_state()
            result = await bc.execute("click", "Personal Loan")
    """

    def __init__(self, persona_slug: str = "persona", persona=None) -> None:
        self._slug     = persona_slug
        self._persona  = persona
        self._pw       = None
        self._browser: Optional[Browser]        = None
        self._context: Optional[BrowserContext] = None
        self._page:    Optional[Page]           = None
        self._step_counter: int                 = 0
        # Path to the finalised journey recording, set in __aexit__ after the
        # context closes (Playwright only finalises the video on close).
        self.video_path:    str                 = ""

    async def __aenter__(self) -> "BrowserController":
        self._pw = await async_playwright().start()

        launch_kwargs: dict = dict(
            slow_mo=config.SLOW_MO,
            headless=not config.HEADED,
        )
        if hasattr(config, "BROWSER_CHANNEL") and config.BROWSER_CHANNEL:
            launch_kwargs["channel"] = config.BROWSER_CHANNEL

        # Ensure screenshot directory exists (BRD §1.3 path)
        (config.SCREENSHOTS_DIR / self._slug).mkdir(parents=True, exist_ok=True)

        video_dir = None
        if config.RECORD_VIDEO:
            video_dir = str(config.VIDEOS_DIR / self._slug)
            Path(video_dir).mkdir(parents=True, exist_ok=True)

        self._browser = await self._pw.chromium.launch(**launch_kwargs)

        vp = {"width": 360, "height": 740} if config.MOBILE_EMULATION else {"width": 1280, "height": 800}
        context_kwargs: dict = dict(viewport=vp)
        if config.MOBILE_EMULATION:
            context_kwargs["user_agent"] = (
                "Mozilla/5.0 (Linux; Android 8.0.0; SM-G950F) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Mobile Safari/537.36"
            )
            context_kwargs["has_touch"] = True
            context_kwargs["is_mobile"] = True

        if video_dir:
            context_kwargs["record_video_dir"]  = video_dir
            context_kwargs["record_video_size"] = vp

        self._context = await self._browser.new_context(**context_kwargs)
        self._context.set_default_timeout(config.PAGE_TIMEOUT)
        self._page    = await self._context.new_page()
        return self

    async def __aexit__(self, *_) -> None:
        if self._context:
            # Capture the video handle BEFORE closing. Playwright finalises the
            # recording only when the context closes, so we must close FIRST and
            # then persist it. The previous order (rename before close) always
            # hit an unfinalised/locked file and silently lost every video.
            video = self._page.video if (config.RECORD_VIDEO and self._page) else None
            try:
                await self._context.close()
            except Exception as exc:
                log.warning("Browser context close failed: %s", exc)

            # Consolidate the journey recording into a flat videos/<slug>.webm so
            # the report + dashboard can reference it directly (no server fallback
            # needed). Do NOT rely solely on self._page.video: multi-page journeys
            # and popups leave that handle pointing at the wrong page (or None),
            # which silently lost every recording. Playwright writes one raw file
            # per page under videos/<slug>/; pick the largest (the main journey)
            # and copy it to the flat path. This is deterministic and only needs
            # the raw files that context.close() has already finalised.
            if config.RECORD_VIDEO:
                dest = config.VIDEOS_DIR / f"{self._slug}.webm"
                raw_dir = config.VIDEOS_DIR / self._slug
                raws = (sorted(raw_dir.glob("*.webm"),
                               key=lambda p: p.stat().st_size, reverse=True)
                        if raw_dir.is_dir() else [])
                if raws:
                    try:
                        shutil.copy2(str(raws[0]), str(dest))
                        self.video_path = str(dest)
                        log.info("Saved journey video for %s → %s", self._slug, dest.name)
                    except Exception as exc:
                        log.warning("Could not consolidate journey video for %s: %s", self._slug, exc)
                elif video is not None:
                    # No raw file found (rare) — fall back to the page handle.
                    try:
                        await video.save_as(str(dest))
                        self.video_path = str(dest)
                    except Exception as exc:
                        log.warning("Could not save journey video for %s: %s", self._slug, exc)
                else:
                    log.warning("No screen recording captured for %s", self._slug)
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._pw:
            try:
                await self._pw.stop()
            except Exception:
                pass

    @property
    def page(self) -> Page:
        return self._page

    # ── Navigation ────────────────────────────────────────────────────────────

    async def navigate(self, url: str) -> ActionResult:
        t0 = time.monotonic()
        try:
            await self._page.goto(url, wait_until="domcontentloaded", timeout=config.PAGE_TIMEOUT)
            await asyncio.sleep(1.5)
            return ActionResult(success=True, action="navigate", target=url,
                                duration_ms=int((time.monotonic() - t0) * 1000))
        except Exception as e:
            return ActionResult(success=False, action="navigate", target=url,
                                error=str(e)[:200], duration_ms=int((time.monotonic() - t0) * 1000))

    # ── State ─────────────────────────────────────────────────────────────────

    async def get_state(self) -> PageState:
        return await extract_state(self._page)

    # ── Screenshot (BRD §1.3 path: screenshots/{slug}/step_{N:03d}.png) ──────

    async def screenshot(self, step_label: str) -> str:
        """Save screenshot and return its absolute path string."""
        ss_dir = config.SCREENSHOTS_DIR / self._slug
        ss_dir.mkdir(parents=True, exist_ok=True)
        path = ss_dir / f"{step_label}.png"
        try:
            await self._page.screenshot(path=str(path), full_page=False)
            return str(path)
        except Exception:
            return ""

    def compress_screenshot(self, path: str) -> Optional[str]:
        """Return base64-encoded JPEG (72%, max 1280px) for LLM vision (BRD §1.3)."""
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

    async def screenshot_with_markers(
        self, step_label: str
    ) -> tuple[str, str, dict[int, tuple[float, float]]]:
        """
        Take a screenshot, then produce a second annotated copy with numbered orange
        circles drawn at the pixel-perfect centre of every interactive element.

        Returns (marked_path, raw_path, marker_map):
          marked_path — annotated PNG (used by the LLM for this decision only)
          raw_path    — clean PNG saved to disk and recorded in memory
                        (used by CX/Design/Content evaluators — must never have
                        orange circles on it, otherwise evaluations are contaminated)
          marker_map  — {1: (x1, y1), 2: (x2, y2), ...}  (1-indexed)

        Falls back to (raw_path, raw_path, {}) if PIL is unavailable or JS fails.
        """
        raw_path = await self.screenshot(step_label)
        if not raw_path or not _PIL_AVAILABLE:
            return raw_path, raw_path, {}

        try:
            positions = await self._page.evaluate(_ELEMENT_POSITIONS_JS)
        except Exception:
            return raw_path, raw_path, {}

        if not positions:
            return raw_path, raw_path, {}

        marker_map: dict[int, tuple[float, float]] = {}
        marked_path = raw_path.replace(".png", "_marked.png")
        try:
            from PIL import ImageDraw, ImageFont
            img  = _PILImage.open(raw_path).convert("RGB")
            draw = ImageDraw.Draw(img)
            r    = 12  # marker radius in pixels

            for i, pos in enumerate(positions[:30], 1):
                cx = int(pos.get("x", 0))
                cy = int(pos.get("y", 0))
                if cx <= 0 and cy <= 0:
                    continue
                marker_map[i] = (float(cx), float(cy))

                # White ring (outer) then orange fill (inner) — avoids outline= width quirks
                draw.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1],
                             fill=(255, 255, 255))
                draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                             fill=(255, 80, 0))

                # White number centred in the circle
                lbl = str(i)
                try:
                    font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), lbl, font=font)
                    tw   = bbox[2] - bbox[0]
                    th   = bbox[3] - bbox[1]
                    draw.text((cx - tw / 2, cy - th / 2), lbl,
                              fill=(255, 255, 255), font=font)
                except Exception:
                    draw.text((cx - 4, cy - 6), lbl, fill=(255, 255, 255))

            # Save annotated copy separately — never overwrite the raw screenshot
            img.save(marked_path, format="PNG")
        except Exception:
            return raw_path, raw_path, {}

        return marked_path, raw_path, marker_map

    # ── Action dispatcher ─────────────────────────────────────────────────────

    async def execute(
        self,
        action: str,
        target: str = "",
        value:  str = "",
        x: float = 0.0,
        y: float = 0.0,
        x2: float = 0.0,
        y2: float = 0.0,
    ) -> ActionResult:
        t0 = time.monotonic()
        dur = lambda: int((time.monotonic() - t0) * 1000)

        # Human-like inter-action delay (BRD Principle 4)
        await asyncio.sleep(_action_delay())

        try:
            if action == "scroll_down":
                await self._scroll("down")
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action == "scroll_up":
                await self._scroll("up")
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action == "scroll_right":
                await self._scroll("right")
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action == "scroll_left":
                await self._scroll("left")
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action == "click":
                ok, err = await self._click(x, y)
                return ActionResult(success=ok, action=action, target=target, error=err, duration_ms=dur())

            elif action == "type":
                ok, err = await self._type(x, y, value)
                return ActionResult(success=ok, action=action, target=target, error=err, duration_ms=dur())

            elif action == "drag":
                ok, err = await self._drag(x, y, x2, y2)
                return ActionResult(success=ok, action=action, target=target, error=err, duration_ms=dur())

            elif action == "select":
                ok, err = await self._select(x, y, value)
                return ActionResult(success=ok, action=action, target=target, error=err, duration_ms=dur())

            elif action == "search":
                ok, err = await self._search(value or target)
                return ActionResult(success=ok, action=action, target=target, error=err, duration_ms=dur())

            elif action in ("dismiss_overlay", "dismiss_popup"):
                await self._dismiss_overlay()
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action in ("navigate_back", "back"):
                await self._navigate_back()
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action == "wait":
                ms = int(value) if value and str(value).isdigit() else 1500
                await asyncio.sleep(ms / 1000)
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            elif action == "done":
                return ActionResult(success=True, action=action, target=target, duration_ms=dur())

            else:
                return ActionResult(success=False, action=action, target=target,
                                    error=f"Unknown action: {action}", duration_ms=dur())

        except Exception as e:
            return ActionResult(success=False, action=action, target=target,
                                error=str(e)[:300], duration_ms=dur())

    # ── Scroll ────────────────────────────────────────────────────────────────

    async def _scroll(self, direction: str) -> None:
        # Guard: if a search input is currently focused it creates a full-screen
        # overlay.  A real human finger cannot scroll behind it — dismiss first.
        try:
            is_search_focused = await self._page.evaluate("""
                () => {
                    const el = document.activeElement;
                    if (!el) return false;
                    const t = el.tagName.toLowerCase();
                    if (t !== 'input' && t !== 'textarea') return false;
                    const type = (el.getAttribute('type')        || '').toLowerCase();
                    const ph   = (el.getAttribute('placeholder') || '').toLowerCase();
                    const al   = (el.getAttribute('aria-label')  || '').toLowerCase();
                    const role = (el.getAttribute('role')        || '').toLowerCase();
                    return type === 'search' || role === 'searchbox' ||
                           ph.includes('search') || al.includes('search');
                }
            """)
            if is_search_focused:
                await self._page.keyboard.press("Escape")
                await asyncio.sleep(0.4)
        except Exception:
            pass

        # Show dot at viewport centre so the human can see the scroll direction
        try:
            vp = self._page.viewport_size or {"width": 360, "height": 740}
            await self._show_dot(vp["width"] / 2, vp["height"] / 2)
        except Exception:
            pass
        if direction in ("down", "up"):
            sign = 1 if direction == "down" else -1
            # Single deliberate scroll: 75 % of viewport — visible, not a micro-jitter
            await self._page.evaluate(
                f"window.scrollBy({{top: {sign} * Math.round(window.innerHeight * 0.75), behavior: 'smooth'}})"
            )
            await asyncio.sleep(random.uniform(0.8, 1.2))
        else:
            # Horizontal scroll for carousels — pick the carousel currently IN the
            # viewport (largest visible, horizontally-scrollable strip), not just
            # the first one in the DOM which may be off-screen. (issue 11)
            sign = 1 if direction == "right" else -1
            await self._page.evaluate(
                """([dx]) => {
                    const vpH = window.innerHeight, vpW = window.innerWidth;
                    const cands = [...document.querySelectorAll(
                        '[class*=carousel i],[class*=slider i],[class*=scroll-x i],'
                        + '[class*=swiper i],[class*=track i],[class*=rail i]')];
                    let best = null, bestArea = 0;
                    for (const el of cands) {
                        const r = el.getBoundingClientRect();
                        if (r.bottom <= 0 || r.top >= vpH) continue;       // not in viewport
                        if (el.scrollWidth <= el.clientWidth + 4) continue; // not scrollable
                        const visH = Math.min(r.bottom, vpH) - Math.max(r.top, 0);
                        const visW = Math.min(r.right, vpW) - Math.max(r.left, 0);
                        const area = Math.max(0, visH) * Math.max(0, visW);
                        if (area > bestArea) { bestArea = area; best = el; }
                    }
                    (best || window).scrollBy({left: dx, behavior: 'smooth'});
                }""",
                [sign * 300],
            )
            await asyncio.sleep(0.4)

    # ── Click — coordinate-based (pure vision) ───────────────────────────────

    async def _click(self, x: float, y: float) -> tuple[bool, str]:
        """Tap at pixel coordinates (x, y) — exactly like a human finger tap."""
        if not x and not y:
            return False, "No coordinates (x=0, y=0)"
        try:
            await self._show_dot(x, y)
            await self._page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.08, 0.18))
            await self._page.mouse.click(x, y)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            try:
                await self._page.wait_for_load_state("domcontentloaded", timeout=8000)
            except Exception:
                pass
            return True, ""
        except Exception as e:
            return False, str(e)[:200]

    # ── Type — click-to-focus at coordinates, then keyboard ──────────────────

    async def _type(self, x: float, y: float, text: str) -> tuple[bool, str]:
        """
        Tap at (x, y) to focus the field, clear any pre-filled content, then
        type character by character.

        Clearing strategy (belt-and-suspenders):
          1. Triple-click — reliably selects all text in the focused element
             across standard inputs, React controlled inputs, and number fields.
          2. Control+a — backup for inputs where triple-click leaves partial
             selections.
          3. JS evaluate fallback — for React inputs that ignore keyboard
             selection entirely; sets the native value and dispatches the input
             event so React's onChange fires.
        The first keystroke then replaces whatever selection remains.
        """
        if not text:
            return False, "No text to type"
        try:
            await self._show_dot(x, y)

            # Triple-click focuses AND selects all existing text in the field
            await self._page.mouse.click(x, y, click_count=3)
            await asyncio.sleep(0.2)

            # Belt-and-suspenders: keyboard select-all on top of triple-click
            await self._page.keyboard.press("Control+a")
            await asyncio.sleep(0.1)

            # JS fallback for React-controlled inputs that ignore keyboard selection:
            # clear the native value and fire both 'input' and 'change' so the
            # framework's state update runs before we start typing.
            try:
                await self._page.evaluate("""
                    (() => {
                        const el = document.activeElement;
                        if (!el || (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA')) return;
                        const existing = el.value || '';
                        if (!existing) return;          // already empty — nothing to do
                        // Use the native setter so React's value tracking is bypassed
                        // before we dispatch the synthetic events that React listens to.
                        const nativeSetter = Object.getOwnPropertyDescriptor(
                            el.tagName === 'TEXTAREA'
                                ? window.HTMLTextAreaElement.prototype
                                : window.HTMLInputElement.prototype,
                            'value'
                        )?.set;
                        if (nativeSetter) nativeSetter.call(el, '');
                        el.dispatchEvent(new Event('input',  { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    })()
                """)
            except Exception:
                pass  # non-fatal — triple-click + Control+a selection covers most cases

            await asyncio.sleep(0.1)

            # Type character by character; first char replaces any remaining selection
            for ch in text:
                await self._page.keyboard.type(ch)
                await asyncio.sleep(_typing_delay())

            return True, ""
        except Exception as e:
            return False, str(e)[:200]

    # ── Drag — slider thumb, like a finger dragging it ───────────────────────

    async def _drag(self, x: float, y: float, x2: float, y2: float) -> tuple[bool, str]:
        """
        Drag from (x, y) to (x2, y2) — used to move a slider thumb. Mimics a
        finger press-move-release with intermediate steps so range inputs and
        custom sliders register the gesture.
        """
        if not x and not y:
            return False, "No drag start coordinates"
        if not x2 and not y2:
            return False, "No drag destination coordinates"
        try:
            await self._show_dot(x, y)
            await self._page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.2))
            await self._page.mouse.down()
            await asyncio.sleep(0.15)
            # Move in a few intermediate steps so the slider tracks the drag
            steps = 12
            for i in range(1, steps + 1):
                ix = x + (x2 - x) * i / steps
                iy = y + (y2 - y) * i / steps
                await self._page.mouse.move(ix, iy)
                await asyncio.sleep(0.02)
            await asyncio.sleep(0.15)
            await self._page.mouse.up()
            await self._show_dot(x2, y2)
            await asyncio.sleep(random.uniform(0.4, 0.7))
            return True, ""
        except Exception as e:
            try:
                await self._page.mouse.up()
            except Exception:
                pass
            return False, str(e)[:200]

    # ── Select — choose an option from a dropdown / picker ────────────────────

    async def _select(self, x: float, y: float, option: str) -> tuple[bool, str]:
        """
        Choose an option from a dropdown. A native <select> opens an OS picker
        that is not in the screenshot, so we set it via the value/label the model
        named (the human-equivalent of 'tap the field, pick the option'). If the
        element under the tap is NOT a native <select>, fall back to tapping it so
        a custom dropdown opens and the model can read/pick the option next step.
        """
        if not option:
            return False, "No option to select"
        try:
            await self._show_dot(x, y)
            # Find the element at the tap point
            handle = await self._page.evaluate_handle(
                "([cx, cy]) => document.elementFromPoint(cx, cy)", [x, y]
            )
            el = handle.as_element()
            if el is not None:
                tag = (await el.evaluate("e => e.tagName") or "").upper()
                # If it's not a <select>, climb to the nearest <select> ancestor
                if tag != "SELECT":
                    sel_handle = await el.evaluate_handle("e => e.closest('select')")
                    sel_el = sel_handle.as_element()
                    if sel_el is not None:
                        el, tag = sel_el, "SELECT"
                if tag == "SELECT":
                    # Try by label, then by value — the human picks by what they read
                    for how in ("label", "value"):
                        try:
                            await el.select_option(**{how: option})
                            await asyncio.sleep(random.uniform(0.4, 0.7))
                            return True, ""
                        except Exception:
                            continue
                    # Last resort: partial label match
                    try:
                        await el.select_option(label=option)
                        await asyncio.sleep(0.4)
                        return True, ""
                    except Exception:
                        pass
            # Not a native select (or value not found) — tap to open the custom
            # dropdown so the model can pick a visible option on the next step.
            await self._page.mouse.click(x, y)
            await asyncio.sleep(random.uniform(0.5, 0.9))
            return True, ""
        except Exception as e:
            return False, str(e)[:200]

    # ── Search ────────────────────────────────────────────────────────────────

    async def _search(self, keyword: str) -> tuple[bool, str]:
        if not keyword:
            return False, "No search keyword"

        for opener in [
            self._page.get_by_role("button", name=re.compile(r"search", re.I)),
            self._page.locator("[aria-label*='search' i]"),
            self._page.locator("[title*='search' i]"),
            self._page.locator("button[class*='search' i]"),
        ]:
            try:
                if await opener.count() > 0 and await opener.first.is_visible():
                    await asyncio.sleep(random.uniform(0.3, 0.6))
                    await opener.first.click()
                    await asyncio.sleep(0.8)
                    break
            except Exception:
                continue

        search_input = None
        for loc in [
            self._page.get_by_role("searchbox"),
            self._page.locator("input[type='search']"),
            self._page.locator("input[placeholder*='search' i]"),
            self._page.locator("input[placeholder*='find' i]"),
            self._page.locator("input[aria-label*='search' i]"),
        ]:
            try:
                if await loc.count() > 0 and await loc.first.is_visible():
                    search_input = loc.first
                    break
            except Exception:
                continue

        if search_input is None:
            return False, "Search bar not found"

        try:
            await search_input.click()
            await asyncio.sleep(0.3)
            for ch in keyword:
                await self._page.keyboard.type(ch)
                await asyncio.sleep(_typing_delay())
            # Wait for the suggestion drawer to populate, then STOP.
            # A real person READS the suggestion list and decides which one (if any)
            # matches what they want — so we do NOT auto-pick the first suggestion
            # and we do NOT press Enter (which loads the Akamai-blocked /search/content).
            # The persona will see the suggestions on the next screenshot and click
            # the relevant one — or judge them irrelevant and do something else. (issue 5)
            await asyncio.sleep(1.5)
            return True, ""
        except Exception as e:
            return False, str(e)[:200]

    # ── Dismiss overlay ───────────────────────────────────────────────────────

    async def _dismiss_overlay(self) -> None:
        # Human-parity: a person on a phone dismisses a popup by tapping the
        # visible × (close) button, or by tapping the dark area OUTSIDE the popup.
        # No Escape key (a phone has none) and no DOM hiding. (issue 4)
        vp = self._page.viewport_size or {"width": 360, "height": 740}
        W, H = vp["width"], vp["height"]

        _OVERLAY_SEL = (
            "[role=dialog],[role=alertdialog],"
            "[class*=modal i],[class*=popup i],[class*=dialog i]"
        )

        # 1. Tap a visible close / × button inside the overlay (finger tap at its
        #    on-screen centre — exactly what the model would do via click).
        try:
            close_pt = await self._page.evaluate(
                """(sel) => {
                    const ovs = [...document.querySelectorAll(sel)].filter(el => {
                        const s = getComputedStyle(el); const r = el.getBoundingClientRect();
                        return s.display!=='none' && s.visibility!=='hidden' && r.width>80 && r.height>60;
                    });
                    if (!ovs.length) return null;
                    const ov = ovs[0];
                    const closeRe = /close|dismiss|×|✕|✖|no\\s*thanks|not\\s*now|maybe\\s*later|skip/i;
                    const cands = [...ov.querySelectorAll('button,a,span,div,i,[role=button],[aria-label]')];
                    for (const b of cands) {
                        const lbl = (b.getAttribute('aria-label')||'') + ' ' +
                                    (b.getAttribute('title')||'') + ' ' + (b.textContent||'').trim();
                        const cls = (b.className && b.className.toString) ? b.className.toString() : '';
                        const txt = (b.textContent||'').trim();
                        const isX = txt === '×' || txt === '✕' || txt === '✖' || txt.toLowerCase() === 'x';
                        if (closeRe.test(lbl) || /close|dismiss/i.test(cls) || isX) {
                            const r = b.getBoundingClientRect();
                            if (r.width>0 && r.height>0 && r.top>=0 && r.left>=0)
                                return {x: r.left + r.width/2, y: r.top + r.height/2};
                        }
                    }
                    return null;
                }""",
                _OVERLAY_SEL,
            )
        except Exception:
            close_pt = None

        if close_pt and 0 < close_pt["x"] < W and 0 < close_pt["y"] < H:
            try:
                await self._show_dot(close_pt["x"], close_pt["y"])
                await self._page.mouse.click(close_pt["x"], close_pt["y"])
                await asyncio.sleep(0.5)
                return
            except Exception:
                pass

        # 2. No visible close button — tap the dark backdrop OUTSIDE the modal,
        #    keeping clear of the top-left logo and the bottom nav bar.
        try:
            rect = await self._page.evaluate(
                """(sel) => {
                    const ovs = [...document.querySelectorAll(sel)].filter(el => {
                        const s = getComputedStyle(el); const r = el.getBoundingClientRect();
                        return s.display!=='none' && s.visibility!=='hidden' && r.width>80 && r.height>60;
                    });
                    if (!ovs.length) return null;
                    const r = ovs[0].getBoundingClientRect();
                    return {top: r.top, bottom: r.bottom};
                }""",
                _OVERLAY_SEL,
            )
        except Exception:
            rect = None

        tap_x = W / 2          # centre column avoids the top-left logo
        tap_y = None
        if rect:
            if rect["top"] > 110:                 # gap above the modal (below logo)
                tap_y = max(85, rect["top"] - 18)
            elif rect["bottom"] < H - 80:         # gap below the modal (above nav)
                tap_y = min(H - 75, rect["bottom"] + 18)
        if tap_y is None:
            tap_y = 90                            # safe fallback: top area, below logo
        try:
            await self._show_dot(tap_x, tap_y)
            await self._page.mouse.click(tap_x, tap_y)
            await asyncio.sleep(0.5)
        except Exception:
            pass

    # ── Navigate back ─────────────────────────────────────────────────────────

    async def _navigate_back(self) -> None:
        try:
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await self._page.go_back(wait_until="domcontentloaded", timeout=config.PAGE_TIMEOUT)
            await asyncio.sleep(random.uniform(0.5, 1.0))
        except Exception:
            pass

    # ── Orange dot — visual interaction indicator ─────────────────────────────

    async def _show_dot(self, x: float, y: float) -> None:
        """Flash a small orange circle at (x, y) so the human watching the browser
        can see what Playwright is clicking, typing into, or scrolling through."""
        try:
            await self._page.evaluate("""
                ([cx, cy]) => {
                    const d = document.createElement('div');
                    d.style.cssText = (
                        'position:fixed;z-index:2147483647;pointer-events:none;' +
                        'border-radius:50%;background:rgba(255,100,0,0.88);' +
                        'width:28px;height:28px;' +
                        'left:' + (cx - 14) + 'px;top:' + (cy - 14) + 'px;' +
                        'box-shadow:0 0 0 5px rgba(255,100,0,0.30);' +
                        'transition:opacity 0.65s ease-out;'
                    );
                    document.body.appendChild(d);
                    setTimeout(function() { d.style.opacity = '0'; }, 80);
                    setTimeout(function() {
                        if (d.parentNode) d.parentNode.removeChild(d);
                    }, 800);
                }
            """, [x, y])
        except Exception:
            pass
