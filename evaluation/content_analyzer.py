"""
Content Analyzer  (BRD §4.1)
-----------------------------
Evaluates the quality, clarity, and effectiveness of content encountered
during the journey across 8 weighted dimensions.
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

# ── 8 Content Dimensions with weights (BRD §4.1 Annexure) ────────────────────
CONTENT_DIMENSIONS: list[tuple[str, float]] = [
    ("Content Relevance and Goal Alignment",   0.18),
    ("Clarity and Comprehension",              0.16),
    ("Financial Information Accuracy",         0.14),
    ("Regulatory and Compliance Content",      0.14),
    ("Content Structure and Scannability",     0.14),
    ("Multilingual and Localisation Quality",  0.10),
    ("SEO and Discoverability Content",        0.08),
    ("Tone and Audience Alignment",            0.06),
]

_DIM_NAMES  = [d[0] for d in CONTENT_DIMENSIONS]
_DIM_WEIGHT = {d[0]: d[1] for d in CONTENT_DIMENSIONS}

_MAX_SCREENSHOTS = 10
_JPEG_QUALITY    = 72
_MAX_PX          = 1280


# ── Output dataclasses ────────────────────────────────────────────────────────

@dataclass
class ContentDimensionScore:
    dimension_name: str
    score:          float
    is_na:          bool = False
    rationale:      str  = ""
    examples:       list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension_name": self.dimension_name,
            "score":          self.score,
            "is_na":          self.is_na,
            "rationale":      self.rationale,
            "examples":       self.examples,
        }


@dataclass
class ContentAnalysisResult:
    persona_name:          str
    overall_content_score: float
    dimension_scores:      list[ContentDimensionScore]
    content_gaps:          list[str]
    content_strengths:     list[str]
    key_findings:          str
    content_recommendations: list[dict] = field(default_factory=list)
    step_evaluations:      list[dict]   = field(default_factory=list)
    raw_response:          dict         = field(default_factory=dict)

    def to_dict(self) -> dict:
        dims = [
            {
                "dimension_name": d.dimension_name,
                "name":           d.dimension_name,   # dashboard alias
                "score":          d.score,
                "is_na":          d.is_na,
                "rationale":      d.rationale,
                "observation":    d.rationale,         # dashboard alias
                "examples":       d.examples,
            }
            for d in self.dimension_scores
        ]
        return {
            "persona_name":            self.persona_name,
            "overall_content_score":   self.overall_content_score,
            "dimension_scores":        dims,
            "dimensions":              dims,            # dashboard alias
            "content_gaps":            self.content_gaps,
            "content_strengths":       self.content_strengths,
            "key_findings":            self.key_findings,
            "content_summary":         self.key_findings,  # dashboard alias
            "content_recommendations": self.content_recommendations,
            "step_evaluations":        self.step_evaluations,
        }


# ── JSON Schema ───────────────────────────────────────────────────────────────

def _build_schema() -> dict:
    dim_score_schema = {
        "type": "object",
        "properties": {
            "dimension_name": {"type": "string"},
            "score":          {"type": "number", "minimum": 0, "maximum": 10},
            "is_na":          {"type": "boolean"},
            "rationale":      {"type": "string"},
            "examples":       {"type": "array", "items": {"type": "string"}},
        },
        "required":             ["dimension_name", "score", "is_na", "rationale", "examples"],
        "additionalProperties": False,
    }

    step_dim_score_schema = {
        "type": "object",
        "properties": {
            "dimension":   {"type": "string"},
            "score":       {"type": "number", "minimum": 0, "maximum": 10},
            "is_na":       {"type": "boolean"},
            "observation": {"type": "string"},
        },
        "required": ["dimension", "score", "is_na", "observation"],
        "additionalProperties": False,
    }

    step_eval_schema = {
        "type": "object",
        "properties": {
            "step_number":      {"type": "integer"},
            "url":              {"type": "string"},
            "action":           {"type": "string"},
            "dimension_scores": {"type": "array", "items": step_dim_score_schema},
        },
        "required": ["step_number", "url", "action", "dimension_scores"],
        "additionalProperties": False,
    }

    recommendation_schema = {
        "type": "object",
        "properties": {
            "priority":        {"type": "string", "enum": ["P1", "P2", "P3"]},
            "area":            {"type": "string"},
            "recommendation":  {"type": "string"},
            "expected_impact": {"type": "string"},
        },
        "required": ["priority", "area", "recommendation", "expected_impact"],
        "additionalProperties": False,
    }

    return {
        "type": "object",
        "properties": {
            "step_evaluations":        {"type": "array", "items": step_eval_schema, "minItems": 1},
            "dimension_scores":        {"type": "array", "items": dim_score_schema, "minItems": 1},
            "content_gaps":            {"type": "array", "items": {"type": "string"}},
            "content_strengths":       {"type": "array", "items": {"type": "string"}},
            "content_recommendations": {"type": "array", "items": recommendation_schema},
            "key_findings":            {"type": "string"},
        },
        "required": [
            "step_evaluations", "dimension_scores",
            "content_gaps", "content_strengths", "content_recommendations", "key_findings",
        ],
        "additionalProperties": False,
    }


_SCHEMA = _build_schema()


# ── Screenshot helpers ────────────────────────────────────────────────────────

def _compress(path: Path) -> Optional[str]:
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


def _collect_screenshot_images(
    memory: JourneyMemory, max_count: int = _MAX_SCREENSHOTS
) -> tuple[list[dict], list[dict]]:
    """Returns (image_blocks, step_meta_list) — parallel lists."""
    steps_with_screenshots = [
        s for s in memory.steps if s.screenshot and Path(s.screenshot).exists()
    ]
    if not steps_with_screenshots:
        return [], []

    total = len(steps_with_screenshots)
    if total <= max_count:
        selected = steps_with_screenshots
    else:
        step_size = total / max_count
        selected  = [steps_with_screenshots[int(i * step_size)] for i in range(max_count)]

    blocks: list[dict] = []
    meta:   list[dict] = []
    for step in selected:
        b64 = _compress(Path(step.screenshot))
        if b64:
            blocks.append({
                "type":      "input_image",
                "image_url": f"data:image/jpeg;base64,{b64}",
                "detail":    "low",
            })
            meta.append({
                "step_number": step.step_number,
                "url":         step.url or "",
                "action":      step.action or "",
            })
    return blocks, meta


# ── Main analyzer ─────────────────────────────────────────────────────────────

class ContentAnalyzer:

    def __init__(self) -> None:
        self._client = OpenAIResponsesClient()

    async def analyze(self, memory: JourneyMemory, persona: Persona) -> ContentAnalysisResult:
        images, step_meta = _collect_screenshot_images(memory)
        prompt = self._build_prompt(memory, persona, step_meta)
        raw    = await self._call_llm(prompt, images)
        return self._parse(raw, persona)

    # ── Prompt ────────────────────────────────────────────────────────────────

    def _build_prompt(self, memory: JourneyMemory, persona: Persona, step_meta: list[dict]) -> str:
        dim_list = "\n".join(
            f"  {i+1:02d}. {name} (weight {int(w*100)}%)"
            for i, (name, w) in enumerate(CONTENT_DIMENSIONS)
        )

        visited = "\n".join(f"  - {url}" for url in memory.visited_urls[:20])

        screenshot_index = "\n".join(
            f"  Image {i+1}: Step {m['step_number']} | {m['action'].upper()} | {m['url'][:70]}"
            for i, m in enumerate(step_meta)
        ) or "  (no screenshots)"

        return f"""You are a content quality analyst evaluating a financial services website's content.

PERSONA
-------
Name:   {persona.name}
Intent: {persona.intent}

JOURNEY CONTEXT
---------------
Steps:  {memory.step_count} | Terminal reason: {memory.terminal_reason}
Visited URLs:
{visited or "  (none recorded)"}

SCREENSHOT INDEX
----------------
Images are attached in this order — use step_number and url in step_evaluations:
{screenshot_index}

EVALUATION INSTRUCTIONS
-----------------------
You are provided with {len(step_meta)} screenshots from this persona's journey.
Evaluate content quality in TWO passes:

PASS 1 — PER-SCREENSHOT (step_evaluations)
For EACH screenshot, produce one step_evaluation entry:
- step_number, url, action: from the Screenshot Index above
- dimension_scores: for every content dimension observable in THAT screenshot:
    - dimension: exact name from the list below
    - score: 0–10 for the content quality on THIS specific screen
    - is_na: true only if the dimension is completely unobservable here
    - observation: ONE specific sentence about the actual content you see —
      quote exact headings, labels, or copy; note what information is missing.
      Example: "The EMI section headline reads 'Flexible repayment options' but
      gives no actual tenure range or rate — leaves {persona.name} with nothing
      concrete to evaluate." Never write generic observations.

PASS 2 — AGGREGATE (dimension_scores)
For each of the 8 dimensions, produce one aggregate entry:
- rationale: ONE analytical verdict sentence explaining what the score means overall —
  why it is not higher and not lower. Do NOT repeat the observations from step_evaluations.
  Example: "Starting rates are shown but no rate personalisation exists, leaving the
  persona unable to assess their actual cost." This is interpretation, not evidence.
- examples: up to 3 LITERAL strings — exact headline text, button labels, or specific
  numbers copied verbatim from the pages. These are evidence fragments, not sentences.
  Example: ["7.25% p.a.*", "Apply for Home Loan", "Prime Rewards"].
  Never paraphrase. Never repeat what rationale already says.

CONTENT DIMENSIONS:
{dim_list}

SCORING ANCHOR:
  9–10 = content fully answers this persona's questions, nothing missing
  7–8  = mostly useful, minor gaps or clarity issues
  5–6  = partially meets the need, significant gaps
  3–4  = frequently misleads or leaves key questions unanswered
  1–2  = content actively confuses or mis-sells to this persona

Also provide:
- content_gaps: specific information missing that this persona needed (be concrete)
- content_strengths: specific content elements that worked for this persona
- content_recommendations: prioritised fixes (P1/P2/P3) with area, recommendation, expected_impact
- key_findings: 2–3 paragraph narrative of the overall content experience for this persona
"""

    # ── LLM call ──────────────────────────────────────────────────────────────

    async def _call_llm(self, prompt: str, images: list[dict]) -> dict:
        input_content: list[dict] = [{"type": "input_text", "text": prompt}] + images
        try:
            return await self._client.create_json(
                system_prompt    = "You are a content quality analyst. Respond strictly with the requested JSON.",
                input_content    = input_content,
                schema_name      = "content_analysis_result",
                schema           = _SCHEMA,
                max_output_tokens= 8192,
            )
        except Exception as exc:
            log.error("Content analysis LLM call failed: %s", exc)
            return {}

    # ── Parse + aggregate ─────────────────────────────────────────────────────

    def _parse(self, raw: dict, persona: Persona) -> ContentAnalysisResult:
        raw_dims = {d.get("dimension_name", ""): d for d in raw.get("dimension_scores", [])}

        dimension_scores: list[ContentDimensionScore] = []
        for name, global_weight in CONTENT_DIMENSIONS:
            d = raw_dims.get(name, {})
            dimension_scores.append(ContentDimensionScore(
                dimension_name=name,
                score=float(d.get("score", 5.0)),
                is_na=bool(d.get("is_na", False)),
                rationale=d.get("rationale", ""),
                examples=d.get("examples", []),
            ))

        non_na_pairs = [
            (global_weight, dim_obj.score)
            for (_, global_weight), dim_obj in zip(CONTENT_DIMENSIONS, dimension_scores)
            if not dim_obj.is_na
        ]
        if non_na_pairs:
            total_active_weight = sum(w for w, _ in non_na_pairs)
            overall = sum(w * score / total_active_weight for w, score in non_na_pairs)
        else:
            overall = 5.0

        # Normalise step_evaluations — drop is_na entries
        raw_step_evals = []
        for se in raw.get("step_evaluations", []):
            dim_scores = [
                {
                    "dimension":   ds.get("dimension", ""),
                    "score":       ds.get("score", 5.0),
                    "is_na":       ds.get("is_na", False),
                    "observation": ds.get("observation", ""),
                }
                for ds in se.get("dimension_scores", [])
                if not ds.get("is_na", False)
            ]
            if dim_scores:
                raw_step_evals.append({
                    "step_number":      se.get("step_number", -1),
                    "url":              se.get("url", ""),
                    "action":           se.get("action", ""),
                    "dimension_scores": dim_scores,
                })

        return ContentAnalysisResult(
            persona_name=persona.name,
            overall_content_score=round(overall, 2),
            dimension_scores=dimension_scores,
            content_gaps=raw.get("content_gaps", []),
            content_strengths=raw.get("content_strengths", []),
            key_findings=raw.get("key_findings", ""),
            content_recommendations=raw.get("content_recommendations", []),
            step_evaluations=raw_step_evals,
            raw_response=raw,
        )
