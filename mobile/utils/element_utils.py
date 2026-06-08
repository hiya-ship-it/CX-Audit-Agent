"""
Element Utilities
-----------------
All Appium element interactions go through this module.
Provides:
  • Explicit waits with configurable timeout
  • Click, type, clear, swipe
  • Retry decorator
  • Screenshot on failure
  • Selector strategy helper (prefer resource-id > accessibility_id > xpath)
"""
from __future__ import annotations

import functools
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, TypeVar

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementNotInteractableException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from rich.console import Console

console = Console()

F = TypeVar("F", bound=Callable)

_RETRYABLE = (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    ElementNotInteractableException,
)


# ── Retry decorator ───────────────────────────────────────────────────────────

def retry(times: int = 3, delay: float = 1.5, exceptions: tuple = _RETRYABLE):
    """Retry a method up to `times` times on specified exceptions."""
    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < times - 1:
                        console.print(
                            f"  [yellow]↻ Retry {attempt + 1}/{times - 1}: "
                            f"{fn.__name__}[/yellow]"
                        )
                        time.sleep(delay)
            raise last_exc  # type: ignore[misc]
        return wrapper  # type: ignore[return-value]
    return decorator


# ── Result type ───────────────────────────────────────────────────────────────

@dataclass
class ActionResult:
    success:     bool
    action:      str
    selector:    str  = ""
    value:       str  = ""
    error:       str  = ""
    duration_ms: int  = 0
    screenshot:  str  = ""

    def __bool__(self) -> bool:
        return self.success


# ── ElementInteractor ─────────────────────────────────────────────────────────

class ElementInteractor:
    """
    Wraps a WebDriver instance and exposes clean, retry-safe action methods.

    Usage:
        ei = ElementInteractor(driver, timeout=15, screenshot_dir=Path("screenshots/mobile"))
        ei.click("//android.widget.Button[@text='Login']")
        ei.type_text("//android.widget.EditText[@hint='Phone']", "9999999999")
    """

    def __init__(
        self,
        driver: WebDriver,
        timeout: int = 15,
        screenshot_dir: Path | None = None,
        action_delay_ms: int = 800,
    ) -> None:
        self._driver       = driver
        self._timeout      = timeout
        self._ss_dir       = screenshot_dir
        self._action_delay = action_delay_ms / 1000.0

    # ── Element finding ───────────────────────────────────────────────────────

    def find(self, selector: str, timeout: int | None = None) -> WebElement:
        """
        Find element using the best-matching strategy:
          • resource-id (contains ':id/')
          • accessibility-id (starts with '~')
          • UiAutomator2 (starts with 'new Ui')
          • XPath (fallback)
        Raises TimeoutException if not found within timeout.
        """
        by, value = self._resolve_selector(selector)
        wait_t = timeout or self._timeout
        return WebDriverWait(self._driver, wait_t).until(
            EC.presence_of_element_located((by, value))
        )

    def find_visible(self, selector: str, timeout: int | None = None) -> WebElement:
        """Find element and wait for it to be visible (not just present)."""
        by, value = self._resolve_selector(selector)
        wait_t = timeout or self._timeout
        return WebDriverWait(self._driver, wait_t).until(
            EC.visibility_of_element_located((by, value))
        )

    def find_clickable(self, selector: str, timeout: int | None = None) -> WebElement:
        """Find element and wait for it to be clickable."""
        by, value = self._resolve_selector(selector)
        wait_t = timeout or self._timeout
        return WebDriverWait(self._driver, wait_t).until(
            EC.element_to_be_clickable((by, value))
        )

    def find_all(self, selector: str) -> list[WebElement]:
        """Find all elements matching selector. Returns [] if none found."""
        by, value = self._resolve_selector(selector)
        try:
            return self._driver.find_elements(by, value)
        except Exception:
            return []

    def exists(self, selector: str, timeout: int = 3) -> bool:
        """Non-raising check — returns True if element found within timeout."""
        try:
            self.find(selector, timeout=timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_gone(self, selector: str, timeout: int = 10) -> bool:
        """Wait until element disappears (e.g. loading spinner). Returns True when gone."""
        by, value = self._resolve_selector(selector)
        try:
            WebDriverWait(self._driver, timeout).until_not(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    # ── Actions ───────────────────────────────────────────────────────────────

    @retry(times=3, delay=1.5)
    def click(self, selector: str, label: str = "") -> ActionResult:
        """Click an element. Retries up to 3 times on transient failures."""
        t0 = time.time()
        element = self.find_clickable(selector)
        element.click()
        time.sleep(self._action_delay)
        ms = int((time.time() - t0) * 1000)
        desc = label or selector[:60]
        console.print(f"  [blue]CLICK[/blue] → {desc}  ({ms}ms)")
        return ActionResult(success=True, action="click", selector=selector, duration_ms=ms)

    @retry(times=3, delay=1.5)
    def type_text(
        self, selector: str, text: str,
        clear_first: bool = True,
        label: str = "",
    ) -> ActionResult:
        """Type text into an input field."""
        t0 = time.time()
        element = self.find_clickable(selector)
        if clear_first:
            element.clear()
        element.send_keys(text)
        time.sleep(self._action_delay)
        ms = int((time.time() - t0) * 1000)
        desc = label or selector[:60]
        console.print(f"  [magenta]TYPE[/magenta] '{text}' → {desc}  ({ms}ms)")
        return ActionResult(
            success=True, action="type", selector=selector, value=text, duration_ms=ms
        )

    def tap(self, x: int, y: int) -> ActionResult:
        """Tap absolute screen coordinates."""
        t0 = time.time()
        self._driver.tap([(x, y)])
        time.sleep(self._action_delay)
        ms = int((time.time() - t0) * 1000)
        console.print(f"  [blue]TAP[/blue] ({x}, {y})  ({ms}ms)")
        return ActionResult(success=True, action="tap", duration_ms=ms)

    def swipe_up(self, distance: float = 0.4) -> ActionResult:
        """Swipe up by `distance` fraction of screen height."""
        return self._swipe(direction="up", distance=distance)

    def swipe_down(self, distance: float = 0.4) -> ActionResult:
        return self._swipe(direction="down", distance=distance)

    def scroll_to_text(self, text: str, max_swipes: int = 5) -> bool:
        """Scroll until element with given text is visible. Returns True if found."""
        selector = (
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().text("{text}"))'
        )
        try:
            self._driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
            return True
        except Exception:
            return False

    def dismiss_keyboard(self) -> None:
        """Hide software keyboard if visible."""
        try:
            if self._driver.is_keyboard_shown():
                self._driver.hide_keyboard()
        except Exception:
            pass

    def wait_for_loading(self, spinner_selector: str, timeout: int = 30) -> None:
        """Wait for a loading indicator to disappear."""
        if self.exists(spinner_selector, timeout=2):
            self.wait_gone(spinner_selector, timeout=timeout)
            console.print("  [dim]Loading complete.[/dim]")

    # ── Screenshot ────────────────────────────────────────────────────────────

    def screenshot(self, name: str) -> str:
        """
        Save screenshot to screenshot_dir/name.png.
        Returns the file path string, or "" on failure.
        """
        if not self._ss_dir:
            return ""
        try:
            self._ss_dir.mkdir(parents=True, exist_ok=True)
            path = self._ss_dir / f"{name}.png"
            self._driver.save_screenshot(str(path))
            return str(path)
        except Exception as exc:
            console.print(f"  [dim]Screenshot failed: {exc}[/dim]")
            return ""

    def screenshot_on_error(self, action: str) -> str:
        """Take an error screenshot tagged with timestamp."""
        ts = int(time.time())
        return self.screenshot(f"error_{action}_{ts}")

    # ── Private ───────────────────────────────────────────────────────────────

    def _swipe(self, direction: str, distance: float) -> ActionResult:
        t0   = time.time()
        size = self._driver.get_window_size()
        w, h = size["width"], size["height"]
        cx   = w // 2

        if direction == "up":
            start_y = int(h * 0.7)
            end_y   = int(h * (0.7 - distance))
        else:
            start_y = int(h * 0.3)
            end_y   = int(h * (0.3 + distance))

        self._driver.swipe(cx, start_y, cx, end_y, duration=600)
        time.sleep(self._action_delay)
        ms = int((time.time() - t0) * 1000)
        console.print(f"  [cyan]SWIPE {direction.upper()}[/cyan]  ({ms}ms)")
        return ActionResult(success=True, action=f"swipe_{direction}", duration_ms=ms)

    @staticmethod
    def _resolve_selector(selector: str) -> tuple[str, str]:
        """
        Map selector string to (By, value) pair.

        Conventions:
          ~label           → accessibility id
          new Ui...        → android uiautomator
          com.foo:id/bar   → resource id
          //android.*      → xpath
        """
        if selector.startswith("~"):
            return AppiumBy.ACCESSIBILITY_ID, selector[1:]
        if selector.startswith("new Ui"):
            return AppiumBy.ANDROID_UIAUTOMATOR, selector
        if ":id/" in selector and not selector.startswith("//"):
            return AppiumBy.ID, selector
        return AppiumBy.XPATH, selector
