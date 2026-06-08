"""
Appium Driver Factory
---------------------
Creates, configures, and tears down Appium WebDriver sessions.

Usage:
    # Context manager (recommended)
    with AppiumDriverFactory.session("config/app_config.yaml") as driver:
        driver.find_element(...)

    # Manual
    driver = AppiumDriverFactory.create()
    ...
    driver.quit()
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import WebDriverException
from rich.console import Console

console = Console()

_DEFAULT_CONFIG = Path(__file__).parent.parent.parent / "config" / "app_config.yaml"


class DriverInitError(Exception):
    """Raised when Appium driver cannot be initialised."""


class AppiumDriverFactory:
    """
    Encapsulates all driver initialisation logic.
    Keeps journey code free of capability boilerplate.
    """

    # ── Public API ────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        config_path: str | Path = _DEFAULT_CONFIG,
        device_name: str | None = None,
        platform_version: str | None = None,
    ) -> webdriver.Remote:
        """
        Instantiate and return a connected Appium driver.

        Args:
            config_path:      Path to app_config.yaml
            device_name:      Override deviceName capability (e.g. from CLI)
            platform_version: Override platformVersion capability
        """
        cfg = cls._load_config(config_path)
        caps_raw = cfg["capabilities"]

        # CLI overrides
        if device_name:
            caps_raw["deviceName"] = device_name
        if platform_version:
            caps_raw["platformVersion"] = platform_version

        options = cls._build_options(caps_raw)
        server  = cfg.get("appium_server", "http://localhost:4723")

        console.print(
            f"[cyan]Connecting to Appium at [bold]{server}[/bold] "
            f"— device: [yellow]{caps_raw['deviceName']}[/yellow][/cyan]"
        )

        try:
            driver = webdriver.Remote(server, options=options)
        except (WebDriverException, Exception) as exc:
            raise DriverInitError(
                f"Could not connect to Appium server at {server}.\n"
                f"  → Is Appium running? Run: appium\n"
                f"  → Is the emulator started? Run: emulator -avd <name>\n"
                f"  → Original error: {exc}"
            ) from exc

        implicit_wait = caps_raw.get("implicitWait", 10)
        driver.implicitly_wait(implicit_wait)

        console.print(
            f"[green]✓ Driver connected  session={driver.session_id[:8]}…[/green]"
        )
        return driver

    @classmethod
    @contextmanager
    def session(
        cls,
        config_path: str | Path = _DEFAULT_CONFIG,
        device_name: str | None = None,
        platform_version: str | None = None,
    ) -> Generator[webdriver.Remote, None, None]:
        """
        Context manager: creates driver, yields it, always calls quit().

        with AppiumDriverFactory.session() as driver:
            ...
        """
        driver = cls.create(config_path, device_name, platform_version)
        try:
            yield driver
        finally:
            cls._safe_quit(driver)

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _load_config(path: str | Path) -> dict:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"App config not found: {p}\n"
                f"Copy config/app_config.yaml.example → config/app_config.yaml "
                f"and fill in your app details."
            )
        return yaml.safe_load(p.read_text(encoding="utf-8"))

    @staticmethod
    def _build_options(caps: dict) -> UiAutomator2Options:
        opts = UiAutomator2Options()

        opts.platform_name    = caps.get("platformName",   "Android")
        opts.platform_version = caps.get("platformVersion", "") or ""
        opts.device_name      = caps.get("deviceName",     "emulator-5554")
        opts.no_reset         = caps.get("noReset",        True)
        opts.full_reset       = caps.get("fullReset",      False)
        opts.auto_grant_permissions = caps.get("autoGrantPermissions", True)
        opts.new_command_timeout    = caps.get("newCommandTimeout",    120)
        opts.uiautomator2_server_launch_timeout = caps.get(
            "uiautomator2ServerLaunchTimeout", 60_000
        )

        # Browser mode (Chrome on Android) — mutually exclusive with app mode
        browser = caps.get("browserName", "")
        if browser:
            opts.browser_name = browser
            if caps.get("chromedriverAutoDownload"):
                opts.set_capability("chromedriverAutoDownload", True)
        elif "app" in caps:
            opts.app = caps["app"]
        elif "appPackage" in caps:
            opts.app_package  = caps["appPackage"]
            opts.app_activity = caps.get("appActivity", "")

        if "systemPort" in caps:
            opts.set_capability("systemPort", caps["systemPort"])

        return opts

    @staticmethod
    def _safe_quit(driver: webdriver.Remote) -> None:
        try:
            driver.quit()
            console.print("[dim]Driver session closed.[/dim]")
        except Exception:
            pass


# ── Utility: switch between NATIVE_APP and WebView contexts ──────────────────

def switch_to_webview(driver: webdriver.Remote, timeout: int = 10) -> bool:
    """
    Switch driver context to the first available WebView.
    Returns True if successful, False if no WebView found.

    Used for hybrid apps where the chatbot is rendered in a WebView.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        contexts = driver.contexts
        webviews = [c for c in contexts if c.startswith("WEBVIEW")]
        if webviews:
            driver.switch_to.context(webviews[0])
            console.print(f"[cyan]Switched to context: {webviews[0]}[/cyan]")
            return True
        time.sleep(0.5)
    console.print("[yellow]No WebView context found — staying in NATIVE_APP[/yellow]")
    return False


def switch_to_native(driver: webdriver.Remote) -> None:
    """Switch back to NATIVE_APP context."""
    driver.switch_to.context("NATIVE_APP")
