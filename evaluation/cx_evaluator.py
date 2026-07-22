"""
CX Evaluator  (BRD §2.3, §2.4)
-------------------------------
Evaluates the customer experience journey across 20 weighted dimensions.
Sends sampled screenshots + journey transcript to OpenAI; performs weighted
aggregation locally (BRD Step 2.4).
"""
from __future__ import annotations

import base64
import io
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from PIL import Image as _PILImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

import config
from agents.memory import JourneyMemory
from parsers.persona_parser import Persona
from llm.openai_responses import OpenAIResponsesClient

log = logging.getLogger(__name__)

# ── 20 CX Dimensions with weights (BRD Annexure) ─────────────────────────────
CX_DIMENSIONS: list[tuple[str, float]] = [
    ("Task Success and Goal Completion",              0.07),
    ("Discoverability and Information Architecture",  0.06),
    ("Content Quality and Comprehension",             0.06),
    ("Financial Clarity and Disclosure",              0.06),
    ("Trust and Credibility",                         0.06),
    ("Conversation and Task Flow",                    0.06),
    ("Cognitive Load and Decision Simplicity",        0.06),
    ("Emotional Experience and Persona Fit",          0.05),
    ("Mobile and Touch Experience",                   0.05),
    ("Accessibility and Inclusive Design",            0.06),
    ("Error Handling and Recovery",                   0.05),
    ("System Feedback and Load Experience",           0.04),
    ("Microcopy and Language Quality",                0.04),
    ("Form Design and Data Collection UX",            0.06),
    ("Navigation Depth and Efficiency",               0.05),
    ("Personalisation and Context Awareness",         0.03),
    ("Pre-Sales Support and Help Availability",       0.03),
    ("Visual Hierarchy and Scannability",             0.04),
    ("Consistency and Standards",                     0.04),
    ("Data Privacy and Consent UX",                  0.03),
]

_DIM_NAMES  = [d[0] for d in CX_DIMENSIONS]
_DIM_WEIGHT = {d[0]: d[1] for d in CX_DIMENSIONS}

_MAX_SCREENSHOTS = 12   # max images sent to OpenAI
_JPEG_QUALITY    = 72
_MAX_PX          = 1280

# Per-step scoring is the token-heavy half of the evaluation: every step emits 20
# dimension scores *with rationales*. A 50-step journey therefore asks for ~1000
# rationales in a single response, which exceeds the model's output-token ceiling
# and comes back truncated (→ ValueError → empty result → every dimension silently
# defaults to 5.0). Scoring is batched over steps so no single response can hit the
# ceiling, and the journey-level synthesis runs as its own small call.
_STEP_BATCH_SIZE = 10


# ── Output dataclass ──────────────────────────────────────────────────────────

@dataclass
class DimensionScore:
    dimension_name: str
    score:          float        # 0–10; meaningless if is_na
    is_na:          bool = False
    rationale:      str  = ""

    def to_dict(self) -> dict:
        return {
            "dimension_name": self.dimension_name,
            "name":           self.dimension_name,   # dashboard alias
            "dimension":      self.dimension_name,   # step-panel alias
            "score":          self.score,
            "is_na":          self.is_na,
            "rationale":      self.rationale,
            "observation":    self.rationale,         # dashboard alias
        }


@dataclass
class StepEvaluation:
    step_number:          int
    overall_step_quality: float            # 0–10
    dimension_scores:     list[DimensionScore] = field(default_factory=list)
    action:               str = ""         # from journey memory (for dashboard timeline)
    url:                  str = ""         # from journey memory (for dashboard timeline)
    key_cx_finding:       str = ""         # top CX observation for this step

    def to_dict(self) -> dict:
        return {
            "step_number":          self.step_number,
            "overall_step_quality": self.overall_step_quality,
            "dimension_scores":     [d.to_dict() for d in self.dimension_scores],
            "action":               self.action,
            "url":                  self.url,
            "key_cx_finding":       self.key_cx_finding,
        }


@dataclass
class EmotionalStage:
    stage:   str
    emotion: str
    trigger: str

    def to_dict(self) -> dict:
        return {"stage": self.stage, "emotion": self.emotion, "trigger": self.trigger}


@dataclass
class CXAuditResult:
    persona_name:                str
    overall_cx_score:            float
    dimension_scores:            list[DimensionScore]
    step_evaluations:            list[StepEvaluation]
    emotional_journey:           list[EmotionalStage]
    persona_emotional_narrative: str
    objective_scores:            dict[str, Any]
    issues:                      list[dict]
    delight_points:              list[str]
    tldr:                        str = ""
    journey_verdict:             str = ""
    key_takeaways:               list[str] = field(default_factory=list)
    recommendations:             list[dict] = field(default_factory=list)
    raw_response:                dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        # Dashboard expects dimension objects with "name" key (not "dimension_name")
        dash_dims = [
            {"name": d.dimension_name, "score": d.score, "is_na": d.is_na, "rationale": d.rationale}
            for d in self.dimension_scores
        ]
        # Dashboard expects friction_points with "location" and "impact" keys
        dash_friction = [
            {
                "severity":    i.get("severity", "minor"),
                "location":    i.get("location") or i.get("dimension", ""),
                "description": i.get("description", ""),
                "impact":      i.get("impact") or i.get("recommendation", ""),
            }
            for i in self.issues
        ]
        return {
            # ── canonical fields ──────────────────────────────────────────────
            "persona_name":                self.persona_name,
            "overall_cx_score":            self.overall_cx_score,
            "dimension_scores":            [d.to_dict() for d in self.dimension_scores],
            "step_evaluations":            [s.to_dict() for s in self.step_evaluations],
            "emotional_journey":           [e.to_dict() for e in self.emotional_journey],
            "persona_emotional_narrative": self.persona_emotional_narrative,
            "objective_scores":            self.objective_scores,
            "issues":                      self.issues,
            "delight_points":              self.delight_points,
            # ── new fields ────────────────────────────────────────────────────
            "tldr":            self.tldr,
            "journey_verdict": self.journey_verdict,
            "key_takeaways":   self.key_takeaways,
            "recommendations": self.recommendations,
            # ── dashboard-compatibility aliases ───────────────────────────────
            "overall_score":   self.overall_cx_score,
            "dimensions":      dash_dims,
            "friction_points": dash_friction,
            "positive_moments": self.delight_points,
        }


# ── JSON Schema for OpenAI structured output ─────────────────────────────────

def _build_schema() -> dict:
    dim_score_schema = {
        "type": "object",
        "properties": {
            "dimension_name": {"type": "string"},
            "score":          {"type": "number", "minimum": 0, "maximum": 10},
            "is_na":          {"type": "boolean"},
            "rationale":      {"type": "string"},
        },
        "required":              ["dimension_name", "score", "is_na", "rationale"],
        "additionalProperties":  False,
    }

    step_eval_schema = {
        "type": "object",
        "properties": {
            "step_number":          {"type": "integer"},
            "overall_step_quality": {"type": "number", "minimum": 0, "maximum": 10},
            "dimension_scores":     {"type": "array", "items": dim_score_schema},
            "key_cx_finding":       {"type": "string"},  # top CX observation for this step
        },
        "required":             ["step_number", "overall_step_quality", "dimension_scores"],
        "additionalProperties": False,
    }

    emotional_stage_schema = {
        "type": "object",
        "properties": {
            "stage":   {"type": "string"},
            "emotion": {"type": "string"},
            "trigger": {"type": "string"},
        },
        "required":             ["stage", "emotion", "trigger"],
        "additionalProperties": False,
    }

    issue_schema = {
        "type": "object",
        "properties": {
            "severity":       {"type": "string", "enum": ["critical", "major", "minor"]},
            "dimension":      {"type": "string"},
            "description":    {"type": "string"},
            "recommendation": {"type": "string"},
            "location":       {"type": "string"},  # page area / screen where issue occurs
            "impact":         {"type": "string"},  # user-impact statement
        },
        "required":             ["severity", "dimension", "description", "recommendation"],
        "additionalProperties": False,
    }

    rec_schema = {
        "type": "object",
        "properties": {
            "priority": {"type": "string", "enum": ["P1", "P2", "P3"]},
            "area":     {"type": "string"},
            "action":   {"type": "string"},
        },
        "required":             ["priority", "area", "action"],
        "additionalProperties": False,
    }

    return {
        "type": "object",
        "properties": {
            "step_evaluations": {
                "type": "array",
                "items": step_eval_schema,
                "minItems": 1,
            },
            "emotional_journey": {
                "type": "array",
                "items": emotional_stage_schema,
                "minItems": 6,
                "maxItems": 12,
            },
            "persona_emotional_narrative": {"type": "string"},
            "objective_scores": {
                "type": "object",
                "properties": {
                    "task_completion_rate":           {"type": "number"},
                    "navigation_efficiency":          {"type": "number"},
                    "error_encounter_rate":           {"type": "number"},
                    "time_to_first_relevant_content": {"type": "number"},
                },
                "required": [
                    "task_completion_rate",
                    "navigation_efficiency",
                    "error_encounter_rate",
                    "time_to_first_relevant_content",
                ],
                "additionalProperties": False,
            },
            "issues": {
                "type": "array",
                "items": issue_schema,
            },
            "delight_points": {
                "type": "array",
                "items": {"type": "string"},
            },
            "tldr": {
                "type": "string",
                "description": "2-3 sentence TL;DR of the overall CX experience for this persona.",
            },
            "journey_verdict": {
                "type": "string",
                "description": "One-sentence verdict on whether the journey succeeded for this persona.",
            },
            "key_takeaways": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 6,
                "description": "3-6 most important findings from this journey.",
            },
            "recommendations": {
                "type": "array",
                "items": rec_schema,
                "description": "Prioritised action list (P1=critical fix, P2=important, P3=nice-to-have).",
            },
        },
        "required": [
            "step_evaluations",
            "emotional_journey",
            "persona_emotional_narrative",
            "objective_scores",
            "issues",
            "delight_points",
            "tldr",
            "journey_verdict",
            "key_takeaways",
            "recommendations",
        ],
        "additionalProperties": False,
    }


_SCHEMA = _build_schema()


def _subset_schema(keys: list[str]) -> dict:
    """
    Build a standalone schema containing only `keys` from _SCHEMA.

    Derived from _SCHEMA rather than redeclared so the batched calls can never
    drift from the canonical field definitions.
    """
    props = {
        k: json.loads(json.dumps(v))
        for k, v in _SCHEMA["properties"].items()
        if k in keys
    }
    return {
        "type":                 "object",
        "properties":           props,
        "required":             list(props.keys()),
        "additionalProperties": False,
    }


# Schema for one batch of per-step scoring.
_STEP_SCHEMA = _subset_schema(["step_evaluations"])

# Schema for the journey-level synthesis (everything except per-step scoring).
_SYNTHESIS_SCHEMA = _subset_schema(
    [k for k in _SCHEMA["properties"] if k != "step_evaluations"]
)


# ── Screenshot helpers ────────────────────────────────────────────────────────

def _compress(path: Path) -> Optional[str]:
    """Return base64-encoded JPEG string (BRD §2.3: 72% quality, max 1280px)."""
    try:
        if not _PIL_AVAILABLE:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        img = _PILImage.open(path).convert("RGB")
        w, h = img.size
        if max(w, h) > _MAX_PX:
            scale = _MAX_PX / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), _PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=_JPEG_QUALITY)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as exc:
        log.warning("Screenshot compress failed %s: %s", path, exc)
        return None


def _collect_screenshot_images(memory: JourneyMemory, max_count: int = _MAX_SCREENSHOTS) -> list[dict]:
    """
    Evenly sample up to max_count screenshots from the journey.
    Returns list of OpenAI Responses API input_image content blocks.
    """
    steps_with_screenshots = [
        s for s in memory.steps if s.screenshot and Path(s.screenshot).exists()
    ]
    if not steps_with_screenshots:
        return []

    total = len(steps_with_screenshots)
    if total <= max_count:
        selected = steps_with_screenshots
    else:
        step_size = total / max_count
        selected  = [steps_with_screenshots[int(i * step_size)] for i in range(max_count)]

    blocks = []
    for step in selected:
        b64 = _compress(Path(step.screenshot))
        if b64:
            blocks.append({
                "type":      "input_image",
                "image_url": f"data:image/jpeg;base64,{b64}",
                "detail":    "low",
            })
    return blocks


def _collect_images_for_steps(steps: list, max_count: int = _STEP_BATCH_SIZE) -> list[dict]:
    """
    Screenshots for a specific batch of steps (not the whole journey).

    Same output format as _collect_screenshot_images, but scoped to the steps the
    batch is actually scoring so each call sees the screens it is grading.
    """
    with_screenshots = [s for s in steps if s.screenshot and Path(s.screenshot).exists()]
    if not with_screenshots:
        return []

    total = len(with_screenshots)
    if total <= max_count:
        selected = with_screenshots
    else:
        step_size = total / max_count
        selected  = [with_screenshots[int(i * step_size)] for i in range(max_count)]

    blocks = []
    for step in selected:
        b64 = _compress(Path(step.screenshot))
        if b64:
            blocks.append({
                "type":      "input_image",
                "image_url": f"data:image/jpeg;base64,{b64}",
                "detail":    "low",
            })
    return blocks


# ── Main evaluator class ──────────────────────────────────────────────────────

class CXEvaluator:

    def __init__(self) -> None:
        self._client = OpenAIResponsesClient()

    # ── Public API ────────────────────────────────────────────────────────────

    async def evaluate(self, memory: JourneyMemory, persona: Persona) -> CXAuditResult:
        """
        Run the CX evaluation and return a CXAuditResult.

        Per-step scoring is batched (_STEP_BATCH_SIZE steps per call) so no single
        response can exceed the model's output-token ceiling; the journey-level
        synthesis is a separate call. The batch results are merged back into one
        raw dict with exactly the shape _parse_and_aggregate already expects, so
        aggregation and the emitted report are unchanged.
        """
        step_evaluations = await self._evaluate_steps_batched(memory, persona)
        synthesis        = await self._synthesise(memory, persona, step_evaluations)

        # Journey-level fields from the synthesis call; step scores from the batches.
        raw = dict(synthesis)
        raw["step_evaluations"] = step_evaluations

        return self._parse_and_aggregate(raw, memory, persona)

    # ── Batched per-step scoring ──────────────────────────────────────────────

    async def _evaluate_steps_batched(
        self,
        memory: JourneyMemory,
        persona: Persona,
    ) -> list[dict]:
        """
        Score every step in batches and return the merged step_evaluations list.

        Batches are run sequentially to stay within rate limits. A batch that fails
        is logged and skipped — the remaining batches still contribute, so a partial
        failure degrades the report instead of blanking it.
        """
        steps = list(memory.steps)
        if not steps:
            return []

        batches = [
            steps[i:i + _STEP_BATCH_SIZE]
            for i in range(0, len(steps), _STEP_BATCH_SIZE)
        ]
        log.info(
            "CX evaluation: scoring %d steps in %d batch(es) of up to %d",
            len(steps), len(batches), _STEP_BATCH_SIZE,
        )

        merged: dict[int, dict] = {}
        for idx, batch in enumerate(batches, start=1):
            prompt = self._build_step_batch_prompt(memory, persona, batch, idx, len(batches))
            images = _collect_images_for_steps(batch)
            try:
                raw = await self._call_llm(
                    prompt,
                    images,
                    schema_name="cx_step_scores",
                    schema=_STEP_SCHEMA,
                )
            except Exception as exc:                       # defensive: _call_llm already traps
                log.error("CX step batch %d/%d failed: %s", idx, len(batches), exc)
                continue

            expected = {s.step_number for s in batch}
            returned = raw.get("step_evaluations", []) or []
            for se in returned:
                num = se.get("step_number")
                # Ignore steps outside this batch and duplicates — either would
                # skew the weighted aggregation.
                if num in expected and num not in merged:
                    merged[num] = se

            if not returned:
                log.warning("CX step batch %d/%d returned no step evaluations", idx, len(batches))
            elif len(merged) < sum(len(b) for b in batches[:idx]):
                log.warning(
                    "CX step batch %d/%d: expected %d steps, have %d scored so far",
                    idx, len(batches), sum(len(b) for b in batches[:idx]), len(merged),
                )

        if not merged:
            log.error("CX evaluation: no step scores were produced by any batch")

        return [merged[k] for k in sorted(merged)]

    # ── Journey-level synthesis ───────────────────────────────────────────────

    async def _synthesise(
        self,
        memory: JourneyMemory,
        persona: Persona,
        step_evaluations: list[dict],
    ) -> dict:
        """
        Produce the journey-level fields (issues, delight points, emotional arc,
        narrative, verdict, recommendations) in a single small call, grounded in
        the per-step scores already computed.
        """
        prompt = self._build_synthesis_prompt(memory, persona, step_evaluations)
        images = _collect_screenshot_images(memory)
        return await self._call_llm(
            prompt,
            images,
            schema_name="cx_journey_synthesis",
            schema=_SYNTHESIS_SCHEMA,
        )

    # ── Prompt construction ───────────────────────────────────────────────────

    def _build_prompt(self, memory: JourneyMemory, persona: Persona) -> str:
        dim_list = "\n".join(
            f"  {i+1:02d}. {name} (weight {int(w*100)}%)"
            for i, (name, w) in enumerate(CX_DIMENSIONS)
        )

        steps_summary = []
        for s in memory.steps:
            line = (
                f"  Step {s.step_number:02d} | {s.action} | {s.target or s.url[:60]} | "
                f"success={s.success} | emotion={s.emotion} | state_of_mind={s.state_of_mind[:80] if s.state_of_mind else ''}"
            )
            steps_summary.append(line)

        journey_text = "\n".join(steps_summary) or "  (no steps recorded)"

        return f"""You are an expert CX researcher auditing a persona's journey on a financial services website.

PERSONA
-------
Name:   {persona.name}
Intent: {persona.intent}
Profile: {json.dumps(memory.persona_data, ensure_ascii=False)[:500]}

JOURNEY SUMMARY
---------------
Steps completed:  {memory.step_count}
Steps failed:     {memory.failure_count}
Terminal reason:  {memory.terminal_reason}
Journey completed: {memory.completed}
Visited URLs: {len(memory.visited_urls)}

STEP LOG
--------
{journey_text}

SCREENSHOTS
-----------
{len(_collect_screenshot_images(memory))} screenshots are attached (evenly sampled from the journey).

EVALUATION INSTRUCTIONS
-----------------------
Evaluate this journey across ALL 20 CX dimensions listed below. For each step in the journey,
provide a per-step evaluation (step_evaluations). For each dimension in each step, assign a
score 0–10 OR mark is_na=true if the dimension was not observable in that step.

DO NOT aggregate scores yourself — just provide raw per-step scores. The aggregation will be
done in post-processing.

CX DIMENSIONS (with global weights for reference only):
{dim_list}

REQUIRED OUTPUT FIELDS
----------------------
1. step_evaluations: array (one entry per step)
   - step_number: integer
   - overall_step_quality: 0–10 (holistic quality of this specific step)
   - dimension_scores: array of 20 objects, one per dimension
     - dimension_name: exact string from the list above
     - score: 0–10
     - is_na: true if dimension not observable this step
     - rationale: 1–2 sentence explanation

2. emotional_journey: 6–12 stage arc of the persona's emotional progression
   - stage: label (e.g. "Arrival", "Exploration", "Confusion", "Recovery", "Decision", "Exit")
   - emotion: the dominant emotion (e.g. "curious", "frustrated", "hopeful")
   - trigger: what caused this emotional state

3. persona_emotional_narrative: 3–4 paragraph narrative describing the persona's complete
   emotional experience from first impression to exit. Written in third person. Must reference
   specific moments from the journey log.

4. objective_scores: computed metrics (0–1 scale except where noted):
   - task_completion_rate: fraction of the persona's goal achieved (0–1)
   - navigation_efficiency: 1 / (1 + navigation_errors), higher is better
   - error_encounter_rate: steps_failed / total_steps
   - time_to_first_relevant_content: estimated steps before first relevant content (integer)

5. issues: list of CX issues found
   - severity: "critical" | "major" | "minor"
   - dimension: which of the 20 dimensions this maps to
   - description: specific, evidence-based observation
   - recommendation: actionable fix
   - location: page/screen area where the issue occurs (e.g. "Personal Loan homepage", "EMI calculator")
   - impact: user-impact statement (e.g. "Anxious users like this persona will abandon before completing")

6. delight_points: list of positive CX moments observed (strings)

7. tldr: 2–3 sentence TL;DR summary of the overall CX experience for this persona.

8. journey_verdict: Single sentence — did this journey succeed for this persona? Why or why not?

9. key_takeaways: 3–6 bullet strings — the most important, actionable findings.

10. recommendations: prioritised action list (max 10 items)
    - priority: "P1" (critical, fix immediately) | "P2" (important, next sprint) | "P3" (nice-to-have)
    - area: which site area / dimension this relates to
    - action: specific, concrete recommendation

Be specific and evidence-based. Reference actual step numbers, observed emotions, and
visible content when possible. Score rigorously — a 7 means genuinely good, 5 means
mediocre, 3 means problematic.
"""

    # ── Batched prompt construction ───────────────────────────────────────────

    @staticmethod
    def _dim_list() -> str:
        return "\n".join(
            f"  {i+1:02d}. {name} (weight {int(w*100)}%)"
            for i, (name, w) in enumerate(CX_DIMENSIONS)
        )

    @staticmethod
    def _journey_text(memory: JourneyMemory) -> str:
        steps_summary = []
        for s in memory.steps:
            line = (
                f"  Step {s.step_number:02d} | {s.action} | {s.target or s.url[:60]} | "
                f"success={s.success} | emotion={s.emotion} | state_of_mind={s.state_of_mind[:80] if s.state_of_mind else ''}"
            )
            steps_summary.append(line)
        return "\n".join(steps_summary) or "  (no steps recorded)"

    def _build_step_batch_prompt(
        self,
        memory: JourneyMemory,
        persona: Persona,
        batch: list,
        batch_index: int,
        batch_total: int,
    ) -> str:
        """Prompt for scoring one batch of steps. The full journey log is included
        for context, but only the batch's steps are to be scored."""
        batch_numbers = [s.step_number for s in batch]
        batch_detail = "\n".join(
            f"  Step {s.step_number:02d} | {s.action} | {s.target or s.url[:60]} | "
            f"success={s.success} | emotion={s.emotion} | "
            f"state_of_mind={s.state_of_mind[:200] if s.state_of_mind else ''}"
            for s in batch
        )

        return f"""You are an expert CX researcher auditing a persona's journey on a financial services website.

You are scoring BATCH {batch_index} OF {batch_total} of this journey. Score ONLY the steps listed
under STEPS TO SCORE. The full journey log is provided for context only.

PERSONA
-------
Name:   {persona.name}
Intent: {persona.intent}
Profile: {json.dumps(memory.persona_data, ensure_ascii=False)[:500]}

JOURNEY CONTEXT (full journey — for context only, do NOT score these)
---------------------------------------------------------------------
Steps completed:  {memory.step_count}
Steps failed:     {memory.failure_count}
Terminal reason:  {memory.terminal_reason}
Journey completed: {memory.completed}

{self._journey_text(memory)}

STEPS TO SCORE (this batch only — step numbers {batch_numbers})
---------------------------------------------------------------
{batch_detail}

SCREENSHOTS
-----------
{len(_collect_images_for_steps(batch))} screenshots from the steps in THIS batch are attached.

CX DIMENSIONS (with global weights for reference only)
------------------------------------------------------
{self._dim_list()}

EVALUATION INSTRUCTIONS
-----------------------
Return step_evaluations containing EXACTLY {len(batch)} entries — one for each step number
in {batch_numbers}. Do not include any other step numbers.

For each step:
  - step_number: integer (must be one of {batch_numbers})
  - overall_step_quality: 0–10 (holistic quality of this specific step)
  - dimension_scores: array of 20 objects, one per dimension listed above
    - dimension_name: exact string from the list above
    - score: 0–10
    - is_na: true if the dimension was not observable in that step
    - rationale: 1–2 sentence explanation
  - key_cx_finding: the single most important CX observation for this step

DO NOT aggregate scores yourself — provide raw per-step scores only. Aggregation is done
in post-processing.

Be specific and evidence-based. Score rigorously — a 7 means genuinely good, 5 means
mediocre, 3 means problematic. Keep each rationale to 1–2 sentences.
"""

    def _build_synthesis_prompt(
        self,
        memory: JourneyMemory,
        persona: Persona,
        step_evaluations: list[dict],
    ) -> str:
        """Prompt for the journey-level synthesis, grounded in the batch scores."""
        # Compact digest of the per-step scoring so the synthesis is evidence-based
        # without re-sending every rationale.
        digest_lines = []
        for se in step_evaluations:
            worst = sorted(
                (
                    d for d in se.get("dimension_scores", [])
                    if not d.get("is_na", False)
                ),
                key=lambda d: d.get("score", 10),
            )[:3]
            worst_txt = ", ".join(
                f"{d.get('dimension_name', '')}={d.get('score', '')}" for d in worst
            )
            digest_lines.append(
                f"  Step {se.get('step_number', 0):02d} | quality={se.get('overall_step_quality', '')} | "
                f"weakest: {worst_txt} | {se.get('key_cx_finding', '')}"
            )
        digest = "\n".join(digest_lines) or "  (no per-step scores were produced)"

        return f"""You are an expert CX researcher auditing a persona's journey on a financial services website.

Per-step scoring has already been completed. Your job now is the JOURNEY-LEVEL SYNTHESIS.
Do NOT re-score individual steps.

PERSONA
-------
Name:   {persona.name}
Intent: {persona.intent}
Profile: {json.dumps(memory.persona_data, ensure_ascii=False)[:500]}

JOURNEY SUMMARY
---------------
Steps completed:  {memory.step_count}
Steps failed:     {memory.failure_count}
Terminal reason:  {memory.terminal_reason}
Journey completed: {memory.completed}
Visited URLs: {len(memory.visited_urls)}

STEP LOG
--------
{self._journey_text(memory)}

PER-STEP SCORING ALREADY COMPLETED (use as evidence)
-----------------------------------------------------
{digest}

SCREENSHOTS
-----------
{len(_collect_screenshot_images(memory))} screenshots are attached (evenly sampled from the journey).

CX DIMENSIONS (for reference when attributing issues)
------------------------------------------------------
{self._dim_list()}

REQUIRED OUTPUT FIELDS
----------------------
1. emotional_journey: 6–12 stage arc of the persona's emotional progression
   - stage: label (e.g. "Arrival", "Exploration", "Confusion", "Recovery", "Decision", "Exit")
   - emotion: the dominant emotion (e.g. "curious", "frustrated", "hopeful")
   - trigger: what caused this emotional state

2. persona_emotional_narrative: 3–4 paragraph narrative describing the persona's complete
   emotional experience from first impression to exit. Written in third person. Must reference
   specific moments from the journey log.

3. objective_scores: computed metrics (0–1 scale except where noted):
   - task_completion_rate: fraction of the persona's goal achieved (0–1)
   - navigation_efficiency: 1 / (1 + navigation_errors), higher is better
   - error_encounter_rate: steps_failed / total_steps
   - time_to_first_relevant_content: estimated steps before first relevant content (integer)

4. issues: list of CX issues found
   - severity: "critical" | "major" | "minor"
   - dimension: which of the 20 dimensions this maps to
   - description: specific, evidence-based observation
   - recommendation: actionable fix
   - location: page/screen area where the issue occurs (e.g. "Personal Loan homepage", "EMI calculator")
   - impact: user-impact statement (e.g. "Anxious users like this persona will abandon before completing")

5. delight_points: list of positive CX moments observed (strings)

6. tldr: 2–3 sentence TL;DR summary of the overall CX experience for this persona.

7. journey_verdict: Single sentence — did this journey succeed for this persona? Why or why not?

8. key_takeaways: 3–6 bullet strings — the most important, actionable findings.

9. recommendations: prioritised action list (max 10 items)
   - priority: "P1" (critical, fix immediately) | "P2" (important, next sprint) | "P3" (nice-to-have)
   - area: which site area / dimension this relates to
   - action: specific, concrete recommendation

Be specific and evidence-based. Reference actual step numbers, observed emotions, and
visible content when possible. Ground your issues and delight points in the per-step
scoring digest above.
"""

    # ── LLM call ──────────────────────────────────────────────────────────────

    async def _call_llm(
        self,
        prompt: str,
        images: list[dict],
        schema_name: str = "cx_audit_result",
        schema: Optional[dict] = None,
    ) -> dict:
        input_content: list[dict] = [{"type": "input_text", "text": prompt}] + images
        try:
            # No max_output_tokens cap: a 30-step journey × 20 dimensions × rationale
            # easily exceeds 8192 tokens and causes a truncated/incomplete response,
            # which the client then raises as ValueError → silently returns {} → all
            # dimensions default to 5.0 with no observations.
            return await self._client.create_json(
                system_prompt = "You are an expert CX researcher. Respond strictly with the requested JSON.",
                input_content = input_content,
                schema_name   = schema_name,
                schema        = schema if schema is not None else _SCHEMA,
            )
        except Exception as exc:
            log.error("CX evaluation LLM call failed (%s): %s", schema_name, exc)
            return {}

    # ── Aggregation (BRD Step 2.4) ────────────────────────────────────────────

    def _parse_and_aggregate(
        self,
        raw: dict,
        memory: JourneyMemory,
        persona: Persona,
    ) -> CXAuditResult:
        """
        Aggregate per-step dimension scores into global dimension scores using
        overall_step_quality as the weight for each step (BRD §2.4).
        """
        # Build memory lookup so step_evaluations can be enriched with action/url
        step_memory_map = {s.step_number: s for s in memory.steps}

        step_evals: list[StepEvaluation] = []
        for se_raw in raw.get("step_evaluations", []):
            dim_scores = [
                DimensionScore(
                    dimension_name=ds.get("dimension_name", ""),
                    score=float(ds.get("score", 5.0)),
                    is_na=bool(ds.get("is_na", False)),
                    rationale=ds.get("rationale", ""),
                )
                for ds in se_raw.get("dimension_scores", [])
            ]
            step_num = se_raw.get("step_number", 0)
            mem_step = step_memory_map.get(step_num)
            step_evals.append(StepEvaluation(
                step_number=step_num,
                overall_step_quality=float(se_raw.get("overall_step_quality", 5.0)),
                dimension_scores=dim_scores,
                action=getattr(mem_step, "action", "") or "",
                url=getattr(mem_step, "url", "") or "",
                key_cx_finding=se_raw.get("key_cx_finding", ""),
            ))

        # Build per-dimension weighted aggregates
        # For each dimension: weighted_sum / total_weight (skip is_na steps)
        dim_weighted_sum  = {name: 0.0 for name in _DIM_NAMES}
        dim_total_weight  = {name: 0.0 for name in _DIM_NAMES}
        # Collect (score, rationale) pairs per dimension to synthesise an observation
        dim_observations: dict[str, list[tuple[float, str]]] = {name: [] for name in _DIM_NAMES}

        for step_eval in step_evals:
            w = step_eval.overall_step_quality  # step-level weight
            for ds in step_eval.dimension_scores:
                name = ds.dimension_name
                if name in dim_total_weight and not ds.is_na:
                    dim_weighted_sum[name] += w * ds.score
                    dim_total_weight[name] += w
                    if ds.rationale:
                        dim_observations[name].append((ds.score, ds.rationale))

        aggregated_dims: list[DimensionScore] = []
        for name, global_weight in CX_DIMENSIONS:
            total_w = dim_total_weight[name]
            if total_w > 0:
                agg_score = dim_weighted_sum[name] / total_w
                is_na     = False
            else:
                agg_score = 5.0   # neutral default when no observable steps
                is_na     = True

            # Pick the most informative rationale: lowest-scoring observation (biggest
            # pain point).  Fall back to the first available rationale.
            obs_pairs = dim_observations.get(name, [])
            if obs_pairs:
                obs_pairs_sorted = sorted(obs_pairs, key=lambda x: x[0])
                rationale = obs_pairs_sorted[0][1]   # worst-scoring step's rationale
            else:
                rationale = ""

            aggregated_dims.append(DimensionScore(
                dimension_name=name,
                score=round(agg_score, 2),
                is_na=is_na,
                rationale=rationale,
            ))

        # Overall CX score: redistribute NA weights proportionally to avoid deflation.
        non_na_pairs = [
            (global_weight, dim_obj.score)
            for (_, global_weight), dim_obj in zip(CX_DIMENSIONS, aggregated_dims)
            if not dim_obj.is_na
        ]
        if non_na_pairs:
            total_active_weight = sum(w for w, _ in non_na_pairs)
            overall = sum(w * score / total_active_weight for w, score in non_na_pairs)
        else:
            overall = 5.0

        # Emotional journey
        emotional_journey = [
            EmotionalStage(
                stage=e.get("stage", ""),
                emotion=e.get("emotion", ""),
                trigger=e.get("trigger", ""),
            )
            for e in raw.get("emotional_journey", [])
        ]

        # Objective scores
        total_steps = max(memory.step_count, 1)
        objective_scores = raw.get("objective_scores", {})
        if not objective_scores:
            objective_scores = {
                "task_completion_rate":           1.0 if memory.completed else 0.0,
                "navigation_efficiency":          round(1 / (1 + memory.failure_count), 3),
                "error_encounter_rate":           round(memory.failure_count / total_steps, 3),
                "time_to_first_relevant_content": min(5, total_steps),
            }

        # Issues
        issues = raw.get("issues", [])

        # Delight points
        delight_points = raw.get("delight_points", [])

        return CXAuditResult(
            persona_name=persona.name,
            overall_cx_score=round(overall, 2),
            dimension_scores=aggregated_dims,
            step_evaluations=step_evals,
            emotional_journey=emotional_journey,
            persona_emotional_narrative=raw.get("persona_emotional_narrative", ""),
            objective_scores=objective_scores,
            issues=issues,
            delight_points=delight_points,
            tldr=raw.get("tldr", ""),
            journey_verdict=raw.get("journey_verdict", ""),
            key_takeaways=raw.get("key_takeaways", []),
            recommendations=raw.get("recommendations", []),
            raw_response=raw,
        )
