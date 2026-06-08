"""
Journey Memory
--------------
Stores the complete record of one persona's browsing journey.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class JourneyStep:
    step_number:          int
    timestamp:            str
    url:                  str
    page_title:           str
    action:               str       # scroll_down | scroll_up | tap_element | type_text | search | navigate_back | done
    target:               str       # element description
    value:                str       # typed text (for type/search)
    inner_monologue:      str       # first-person thought process
    reasoning:            str       # why this action
    emotion:              str       # emotional state
    cx_note:              str       # persona's first-person experience at this moment
    cognitive_load:       str       # LOW/MEDIUM/HIGH + explanation
    trust_signals:        str       # trust signals present/absent
    unanswered_questions: str       # questions forming in their mind
    guiding_factors:      str       # what drove the decision
    visible_content:      str       # what was prominent on screen
    attention_focus:      str       # what the persona is actually reading vs. ignoring
    state_of_mind:        str       # deeper psychological state (BRD §5.3)
    success:              bool
    error:                str
    screenshot:           str       # absolute path to screenshot
    duration_ms:          int

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def summary(self) -> str:
        tick = "✓" if self.success else "✗"
        emotion_tag = f" [{self.emotion}]" if self.emotion else ""
        mono = (self.inner_monologue[:100] + "…") if len(self.inner_monologue) > 100 else self.inner_monologue
        lines = [f"  Step {self.step_number:02d} {tick}{emotion_tag}  {self.action} › {(self.target or self.url)[:60]}"]
        if mono:
            lines.append(f"    💭 {mono}")
        if not self.success and self.error:
            lines.append(f"    ✗ {self.error[:80]}")
        return "\n".join(lines)


class JourneyMemory:
    """Complete state of one persona's journey."""

    def __init__(self, persona_name: str, persona_intent: str, persona_data: dict | None = None) -> None:
        self.persona_name   = persona_name
        self.persona_intent = persona_intent
        self.persona_data   = persona_data or {}
        self.started_at     = datetime.now(timezone.utc).isoformat()

        self.steps:         list[JourneyStep] = []
        self.visited_urls:  list[str]         = []
        self.failed_actions: list[dict]       = []
        self.video_path:    str               = ""
        self.final_screenshot: str            = ""
        self.token_usage:   dict[str, int]    = {"input_tokens": 0, "output_tokens": 0}

        # Dashboard-consumed metadata (populated by the agent where available;
        # safe defaults so journey_log.json always has a consistent shape).
        self.run_id:               str            = ""
        self.model:                str            = ""
        self.cost_inr:             Optional[float] = None
        self.is_technical_failure: bool           = False
        self.google_entry:         Optional[dict] = None
        self.cx_observations:      list           = []
        self.login_wall_encounters: int           = 0
        self.login_wall_decisions:  list[dict]    = []

        self.terminal_reason: Optional[str] = None
        self.completed:       bool          = False

        self._jsonl_path: Optional[Path] = None

    def add_step(
        self,
        step_number: int,
        url: str,
        page_title: str,
        decision: dict,
        success: bool,
        error: str,
        screenshot: str,
        duration_ms: int,
    ) -> JourneyStep:
        step = JourneyStep(
            step_number          = step_number,
            timestamp            = datetime.now(timezone.utc).isoformat(),
            url                  = url,
            page_title           = page_title,
            action               = decision.get("action", ""),
            target               = decision.get("target", ""),
            value                = decision.get("value", ""),
            inner_monologue      = decision.get("inner_monologue", ""),
            reasoning            = decision.get("reasoning", ""),
            emotion              = decision.get("emotion", ""),
            cx_note              = decision.get("cx_note", ""),
            cognitive_load       = decision.get("cognitive_load", ""),
            trust_signals        = decision.get("trust_signals", ""),
            unanswered_questions = decision.get("unanswered_questions", ""),
            guiding_factors      = decision.get("guiding_factors", ""),
            visible_content      = decision.get("visible_content", ""),
            attention_focus      = decision.get("attention_focus", ""),
            state_of_mind        = decision.get("state_of_mind", ""),
            success              = success,
            error                = error,
            screenshot           = screenshot,
            duration_ms          = duration_ms,
        )
        self.steps.append(step)

        if url and url not in self.visited_urls:
            self.visited_urls.append(url)

        if not success:
            self.failed_actions.append({
                "step": step_number, "action": step.action,
                "target": step.target, "error": error,
            })

        if self._jsonl_path is not None:
            try:
                record = {"event": "step", "persona": self.persona_name}
                record.update(step.to_dict())
                with open(self._jsonl_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception:
                pass

        return step

    def mark_terminal(self, reason: str) -> None:
        self.terminal_reason = reason
        self.completed = reason not in {"navigation_failed", "fatal_error"}

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def failure_count(self) -> int:
        return sum(1 for s in self.steps if not s.success)

    @property
    def consecutive_failures(self) -> int:
        count = 0
        for step in reversed(self.steps):
            if not step.success:
                count += 1
            else:
                break
        return count

    def recent_history(self, n: int = 6) -> str:
        """Compact summary of last N steps for the LLM prompt."""
        recent = self.steps[-n:]
        if not recent:
            return "  (journey just started — no steps yet)"
        return "\n".join(s.summary() for s in recent)

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Strip query/hash so SPA calculator URL mutations aren't seen as navigation."""
        if not url:
            return ""
        return url.split("#", 1)[0].split("?", 1)[0].rstrip("/")

    def is_looping(self) -> bool:
        """
        True only when the agent is going in circles between pages with no progress.
        Staying on one URL and scrolling/reading/interacting is NOT a loop —
        that is normal human reading behaviour on a long page. URLs are normalised
        (query/hash stripped) so SPA calculator state changes don't count as
        navigation. (issue 9)
        """
        if len(self.steps) < 8:
            return False
        # Only flag as loop if the agent keeps navigating AWAY from a URL and
        # returning to it repeatedly — meaning it is bouncing between pages
        # without making forward progress.
        recent = self.steps[-14:]
        norm = [self._normalize_url(s.url) for s in recent]
        url_counts: dict = {}
        for i in range(1, len(norm)):
            if norm[i] != norm[i - 1]:
                url_counts[norm[i]] = url_counts.get(norm[i], 0) + 1
        # If any URL has been arrived at from a different URL 4+ times → genuine loop
        if any(v >= 4 for v in url_counts.values()):
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "persona":          self.persona_name,
            "intent":           self.persona_intent,
            "persona_data":     self.persona_data,
            "started_at":       self.started_at,
            "terminal_reason":  self.terminal_reason,
            "completed":        self.completed,
            "step_count":       self.step_count,
            "failure_count":    self.failure_count,
            "visited_urls":     self.visited_urls,
            "failed_actions":   self.failed_actions,
            "video_path":       self.video_path,
            "final_screenshot": self.final_screenshot,
            "token_usage":      self.token_usage,
            # Dashboard metadata
            "run_id":               self.run_id,
            "model":                self.model,
            "cost_inr":             self.cost_inr,
            "is_technical_failure": self.is_technical_failure,
            "google_entry":         self.google_entry,
            "cx_observations":      self.cx_observations,
            "login_wall_encounters": self.login_wall_encounters,
            "login_wall_decisions":  self.login_wall_decisions,
            "steps":            [s.to_dict() for s in self.steps],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
