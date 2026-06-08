"""
Audit Logger
------------
Writes every step of a mobile journey to:
  • JSON Lines file  (.jsonl)  — primary, machine-readable
  • CSV file         (.csv)    — optional, spreadsheet-friendly

Each record captures:
  step_name, timestamp, action, selector, value,
  response, status, error, duration_ms, screenshot

Usage:
    logger = AuditLogger(journey_name="login_journey", output_dir=Path("logs/mobile"))
    logger.log_step(
        step_name="open_chatbot",
        action="click",
        selector="//android.widget.ImageButton",
        status="success",
        duration_ms=412,
    )
    logger.close()   # flushes CSV if enabled
"""
from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ── Step record ───────────────────────────────────────────────────────────────

@dataclass
class StepLog:
    step_name:   str
    timestamp:   str
    action:      str
    selector:    str        = ""
    value:       str        = ""      # text typed / message sent
    response:    str        = ""      # chatbot response or element text captured
    status:      str        = "success"   # success | fail | skip
    error:       str        = ""
    duration_ms: int        = 0
    screenshot:  str        = ""
    extra:       dict       = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["extra"] = self.extra       # keep nested
        return d


# ── CSV column order ──────────────────────────────────────────────────────────

_CSV_FIELDS = [
    "step_name", "timestamp", "action", "selector",
    "value", "response", "status", "error", "duration_ms", "screenshot",
]


# ── Logger ────────────────────────────────────────────────────────────────────

class AuditLogger:
    """
    Thread-safe (single-threaded use) step logger for mobile journeys.
    Auto-creates output directories on first write.
    """

    def __init__(
        self,
        journey_name: str,
        output_dir: Path | str = Path("logs/mobile"),
        csv_enabled: bool = True,
        persona: str = "",
    ) -> None:
        self.journey_name = journey_name
        self.persona      = persona
        self._output_dir  = Path(output_dir)
        self._csv_enabled = csv_enabled

        self._steps: list[StepLog] = []
        self._started_at = datetime.now(timezone.utc).isoformat()

        # Paths
        self._output_dir.mkdir(parents=True, exist_ok=True)
        slug = journey_name.lower().replace(" ", "_")
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._jsonl_path = self._output_dir / f"{slug}_{ts}.jsonl"
        self._csv_path   = self._output_dir / f"{slug}_{ts}.csv"
        self._json_path  = self._output_dir / f"{slug}_{ts}.json"

        # Open CSV writer
        if csv_enabled:
            self._csv_file = open(self._csv_path, "w", newline="", encoding="utf-8")
            self._csv_writer = csv.DictWriter(
                self._csv_file, fieldnames=_CSV_FIELDS, extrasaction="ignore"
            )
            self._csv_writer.writeheader()
        else:
            self._csv_file   = None
            self._csv_writer = None

    # ── Public API ────────────────────────────────────────────────────────────

    def log_step(
        self,
        step_name:   str,
        action:      str,
        selector:    str  = "",
        value:       str  = "",
        response:    str  = "",
        status:      str  = "success",
        error:       str  = "",
        duration_ms: int  = 0,
        screenshot:  str  = "",
        **extra,
    ) -> StepLog:
        """
        Log one step. Returns the StepLog so callers can inspect it.
        Never raises — log failures must not crash the journey.
        """
        record = StepLog(
            step_name   = step_name,
            timestamp   = datetime.now(timezone.utc).isoformat(),
            action      = action,
            selector    = selector,
            value       = value,
            response    = response,
            status      = status,
            error       = error,
            duration_ms = duration_ms,
            screenshot  = screenshot,
            extra       = extra or {},
        )
        self._steps.append(record)
        self._write_jsonl(record)
        if self._csv_writer:
            self._write_csv(record)
        return record

    def log_chatbot_exchange(
        self,
        message:     str,
        response:    str,
        duration_ms: int  = 0,
        screenshot:  str  = "",
        error:       str  = "",
    ) -> StepLog:
        """Convenience wrapper for chatbot send/receive pairs."""
        return self.log_step(
            step_name   = "chatbot_exchange",
            action      = "send_message",
            value       = message,
            response    = response,
            status      = "success" if not error else "fail",
            error       = error,
            duration_ms = duration_ms,
            screenshot  = screenshot,
        )

    def log_error(
        self,
        step_name: str,
        action:    str,
        error:     str,
        selector:  str = "",
        screenshot: str = "",
    ) -> StepLog:
        """Convenience wrapper for failure steps."""
        return self.log_step(
            step_name  = step_name,
            action     = action,
            selector   = selector,
            status     = "fail",
            error      = error,
            screenshot = screenshot,
        )

    def close(self) -> dict:
        """
        Flush files and write the final consolidated JSON report.
        Returns the summary dict.
        """
        if self._csv_file:
            self._csv_file.close()

        summary = self._build_summary()
        self._json_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return summary

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def json_path(self) -> Path:
        return self._json_path

    @property
    def jsonl_path(self) -> Path:
        return self._jsonl_path

    @property
    def csv_path(self) -> Path:
        return self._csv_path

    @property
    def step_count(self) -> int:
        return len(self._steps)

    @property
    def failure_count(self) -> int:
        return sum(1 for s in self._steps if s.status == "fail")

    @property
    def steps(self) -> list[StepLog]:
        return list(self._steps)

    # ── Private ───────────────────────────────────────────────────────────────

    def _write_jsonl(self, record: StepLog) -> None:
        try:
            with open(self._jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _write_csv(self, record: StepLog) -> None:
        try:
            row = {k: getattr(record, k, "") for k in _CSV_FIELDS}
            self._csv_writer.writerow(row)
            self._csv_file.flush()
        except Exception:
            pass

    def _build_summary(self) -> dict:
        steps_list  = [s.to_dict() for s in self._steps]
        chatbot_exchanges = [
            s for s in self._steps if s.step_name == "chatbot_exchange"
        ]
        return {
            "journey_name":  self.journey_name,
            "persona":       self.persona,
            "started_at":    self._started_at,
            "completed_at":  datetime.now(timezone.utc).isoformat(),
            "total_steps":   self.step_count,
            "failures":      self.failure_count,
            "success_rate":  (
                round((self.step_count - self.failure_count) / max(self.step_count, 1), 2)
            ),
            "chatbot_messages_sent": len(chatbot_exchanges),
            "steps":         steps_list,
            "output_files": {
                "jsonl": str(self._jsonl_path),
                "csv":   str(self._csv_path),
                "json":  str(self._json_path),
            },
        }


# ── Module-level convenience ──────────────────────────────────────────────────

def make_logger(
    journey_name: str,
    config: dict | None = None,
    persona: str = "",
) -> AuditLogger:
    """
    Create an AuditLogger from a config dict (loaded from app_config.yaml).
    Falls back to sensible defaults.
    """
    out_cfg = (config or {}).get("output", {})
    return AuditLogger(
        journey_name = journey_name,
        output_dir   = Path(out_cfg.get("logs_dir", "logs/mobile")),
        csv_enabled  = out_cfg.get("csv_log", True),
        persona      = persona,
    )
