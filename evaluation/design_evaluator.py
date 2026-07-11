"""
Design Evaluator  (BRD §3.1)
-----------------------------
Evaluates the visual / brand / layout quality across 12 weighted dimensions.
Loads a design knowledge base from design_kb/ before calling the LLM.
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

# ── 12 Design Dimensions — single source of truth ────────────────────────────
# The canonical framework is design_kb/design_evaluation_parameters.json (v3.0):
# names, weightages, and the full per-dimension rubric all come from there. The
# list below is only a fallback for a missing/corrupt file — kept in sync with
# the KB, and a drift between the two is logged (see _load_design_framework).
_KB_PARAMS_FILE = "design_evaluation_parameters.json"

_FALLBACK_DIMENSIONS: list[tuple[str, float]] = [
    ("Typography System Execution",                    0.11),
    ("Color System Application & Contrast",            0.11),
    ("Layout Grid & Spatial Rhythm",                   0.10),
    ("Visual Hierarchy & Attention Guidance",          0.11),
    ("Component Design Quality & System Consistency",  0.10),
    ("Interactive States & Focus Design",              0.08),
    ("Iconography & Visual Communication Quality",     0.06),
    ("Touch Ergonomics & Spatial Accessibility",       0.08),
    ("Form Design & Label Accessibility",              0.08),
    ("System Feedback & Status Visibility",            0.06),
    ("Brand Identity & Visual Consistency",            0.05),
    ("Cognitive Accessibility & Information Density",  0.06),
]


def _load_design_framework() -> dict:
    """
    Load the 12 design dimensions, weights, and full per-dimension rubric from
    design_kb/design_evaluation_parameters.json — the single source of truth
    for the whole design audit (prompt list, schema names, and aggregation all
    read from what this returns). Falls back to _FALLBACK_DIMENSIONS (no rubric)
    only if the file is missing/corrupt.

    Returns {dimensions: [(name, weight)], rubric: {name: {...}}, meta: {...}}.
    """
    path = config.DESIGN_KB_DIR / _KB_PARAMS_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        dims: list[tuple[str, float]] = []
        rubric: dict[str, dict] = {}
        for d in data.get("dimensions", []):
            name = (d.get("name") or "").strip()
            if not name:
                continue
            dims.append((name, float(d.get("weightage", 0)) / 100.0))
            rubric[name] = d
        if not dims:
            raise ValueError("no dimensions found in KB")

        # ── Drift / sanity guards (item F) ──
        total = sum(w for _, w in dims)
        if abs(total - 1.0) > 0.02:
            log.warning("Design KB weightages sum to %.3f (expected ~1.0)", total)
        if [n for n, _ in dims] != [n for n, _ in _FALLBACK_DIMENSIONS]:
            log.warning(
                "Design KB dimensions differ from the in-code fallback — using the "
                "KB (file is authoritative). Update _FALLBACK_DIMENSIONS to match."
            )
        log.info("Design framework loaded from KB: %d dimensions, weights sum %.2f", len(dims), total)
        return {
            "dimensions": dims,
            "rubric":     rubric,
            "meta": {
                "description":       data.get("description", ""),
                "audit_scope":       data.get("audit_scope", ""),
                "framework_sources": data.get("framework_sources", []),
                "scoring_scale":     data.get("scoring_scale", {}),
                "issue_severity":    data.get("issue_severity", {}),
            },
        }
    except Exception as exc:
        log.error("Could not load design framework from %s (%s) — using built-in fallback.", path, exc)
        return {"dimensions": list(_FALLBACK_DIMENSIONS), "rubric": {}, "meta": {}}


_FRAMEWORK      = _load_design_framework()
DESIGN_DIMENSIONS: list[tuple[str, float]] = _FRAMEWORK["dimensions"]
_DIM_NAMES      = [d[0] for d in DESIGN_DIMENSIONS]
_DIM_WEIGHT     = {d[0]: d[1] for d in DESIGN_DIMENSIONS}
_DIM_RUBRIC     = _FRAMEWORK["rubric"]
_FRAMEWORK_META = _FRAMEWORK["meta"]

_MAX_SCREENSHOTS = 12
_JPEG_QUALITY    = 72
_MAX_PX          = 1280


# ── Output dataclasses ────────────────────────────────────────────────────────

@dataclass
class DesignDimensionScore:
    dimension_name:  str
    score:           float
    is_na:           bool = False
    rationale:       str  = ""
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension_name":  self.dimension_name,
            "name":            self.dimension_name,   # dashboard alias
            "score":           self.score,
            "is_na":           self.is_na,
            "rationale":       self.rationale,
            "observation":     self.rationale,        # dashboard alias
            "recommendations": self.recommendations,
        }


@dataclass
class DesignAuditResult:
    persona_name:         str
    overall_design_score: float
    dimension_scores:     list[DesignDimensionScore]
    brand_alignment:      str
    critical_issues:      list[dict]
    positive_findings:    list[str]
    design_verdict:       str       = ""
    design_tldr:          str       = ""
    key_findings:         list[str] = field(default_factory=list)
    wcag_compliance_level: str      = ""
    ds_adherence_level:   str       = ""
    step_evaluations:     list[dict] = field(default_factory=list)
    raw_response:         dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        dims = [d.to_dict() for d in self.dimension_scores]
        issues_with_alias = [
            {**issue, "location": issue.get("dimension", ""), "impact": issue.get("recommendation", "")}
            for issue in self.critical_issues
        ]
        return {
            # canonical names
            "persona_name":         self.persona_name,
            "overall_design_score": self.overall_design_score,
            "dimension_scores":     dims,
            "brand_alignment":      self.brand_alignment,
            "critical_issues":      self.critical_issues,
            "positive_findings":    self.positive_findings,
            "design_verdict":       self.design_verdict,
            "design_tldr":          self.design_tldr,
            "key_findings":         self.key_findings,
            "wcag_compliance_level": self.wcag_compliance_level,
            "ds_adherence_level":   self.ds_adherence_level,
            "step_evaluations":     self.step_evaluations,
            # dashboard aliases
            "overall_score":        self.overall_design_score,
            "dimensions":           dims,
            "issues":               issues_with_alias,
            "positives":            self.positive_findings,
        }


# ── JSON Schema ───────────────────────────────────────────────────────────────

def _build_schema() -> dict:
    dim_score_schema = {
        "type": "object",
        "properties": {
            "dimension_name":  {"type": "string"},
            "score":           {"type": "number", "minimum": 0, "maximum": 10},
            "is_na":           {"type": "boolean"},
            "rationale":       {"type": "string"},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
        "required":             ["dimension_name", "score", "is_na", "rationale", "recommendations"],
        "additionalProperties": False,
    }

    issue_schema = {
        "type": "object",
        "properties": {
            "severity":       {"type": "string", "enum": ["critical", "major", "minor"]},
            "dimension":      {"type": "string"},
            "description":    {"type": "string"},
            "recommendation": {"type": "string"},
        },
        "required":             ["severity", "dimension", "description", "recommendation"],
        "additionalProperties": False,
    }

    step_dim_score_schema = {
        "type": "object",
        "properties": {
            "dimension": {"type": "string"},
            "score":     {"type": "number", "minimum": 0, "maximum": 10},
            "is_na":     {"type": "boolean"},
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

    return {
        "type": "object",
        "properties": {
            "step_evaluations":     {"type": "array", "items": step_eval_schema, "minItems": 1},
            "dimension_scores":     {"type": "array", "items": dim_score_schema, "minItems": 1},
            "brand_alignment":      {"type": "string"},
            "critical_issues":      {"type": "array", "items": issue_schema},
            "positive_findings":    {"type": "array", "items": {"type": "string"}},
            "design_verdict":       {"type": "string"},
            "design_tldr":          {"type": "string"},
            "key_findings":         {"type": "array", "items": {"type": "string"}},
            "wcag_compliance_level": {"type": "string"},
            "ds_adherence_level":   {"type": "string"},
        },
        "required": [
            "step_evaluations", "dimension_scores", "brand_alignment",
            "critical_issues", "positive_findings",
            "design_verdict", "design_tldr", "key_findings",
            "wcag_compliance_level", "ds_adherence_level",
        ],
        "additionalProperties": False,
    }


_SCHEMA = _build_schema()


# ── Knowledge base loader ─────────────────────────────────────────────────────

def _load_knowledge_base() -> str:
    """
    Build the design-audit knowledge base injected into the prompt from the
    already-loaded framework (_FRAMEWORK). Unlike the old loader, this does NOT
    truncate: it emits, per dimension, the definition + screenshot checks +
    scoring anchors + common violations — i.e. the actual grading rubric the
    model needs — plus the Bajaj brand principles in full.
    """
    sections: list[str] = []
    meta = _FRAMEWORK_META

    # ── Framework header: scope, sources, scoring scale, severity ──
    head: list[str] = []
    if meta.get("audit_scope"):
        head.append(f"AUDIT SCOPE: {meta['audit_scope']}")
    if meta.get("framework_sources"):
        head.append("FRAMEWORK SOURCES: " + "; ".join(meta["framework_sources"]))
    if meta.get("scoring_scale"):
        head.append("SCORING SCALE:\n" + "\n".join(f"  {k}: {v}" for k, v in meta["scoring_scale"].items()))
    if meta.get("issue_severity"):
        head.append("ISSUE SEVERITY:\n" + "\n".join(f"  {k}: {v}" for k, v in meta["issue_severity"].items()))
    if head:
        sections.append("=== DESIGN & ACCESSIBILITY FRAMEWORK (WCAG 2.2 + Bajaj) ===\n" + "\n".join(head))

    # ── Per-dimension rubric — the real grading signal ──
    if _DIM_RUBRIC:
        blocks: list[str] = []
        for i, (name, weight) in enumerate(DESIGN_DIMENSIONS, 1):
            d = _DIM_RUBRIC.get(name, {})
            parts = [f"{i:02d}. {name}  (weight {int(round(weight * 100))}%)"]
            if d.get("definition"):
                parts.append(f"   What it measures: {d['definition']}")
            if d.get("what_this_is_not"):
                parts.append(f"   Scope boundary: {d['what_this_is_not']}")
            checks = d.get("screenshot_checks") or []
            if checks:
                parts.append("   Screenshot checks:")
                parts.extend(f"     - {c}" for c in checks)
            rub = d.get("scoring_rubric") or {}
            anchors = [(k, rub[k]) for k in ("9-10", "5-6", "0-2") if k in rub]
            if anchors:
                parts.append("   Score anchors:")
                parts.extend(f"     {k}: {v}" for k, v in anchors)
            viol = (d.get("common_violations") or [])[:3]
            if viol:
                parts.append("   Common violations:")
                parts.extend(f"     - {v}" for v in viol)
            blocks.append("\n".join(parts))
        sections.append("=== 12 DESIGN DIMENSIONS — FULL RUBRIC ===\n" + "\n\n".join(blocks))

    # ── Bajaj brand principles (full — small file, no truncation) ──
    principles_path = config.DESIGN_KB_DIR / "bajaj_principles_summary.md"
    if principles_path.exists():
        try:
            sections.append("=== BAJAJ BRAND PRINCIPLES ===\n" + principles_path.read_text(encoding="utf-8"))
        except Exception as exc:
            log.warning("Could not load bajaj_principles_summary.md: %s", exc)

    if not sections:
        return "(No design knowledge base available — evaluate on general visual-design and WCAG 2.2 A/AA principles.)"
    return "\n\n".join(sections)


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
    """
    Returns (image_blocks, step_meta_list).
    image_blocks: OpenAI input_image content blocks (one per sampled step).
    step_meta_list: parallel list of {step_number, url, action} for each image.
    """
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


# ── Main evaluator ────────────────────────────────────────────────────────────

class DesignEvaluator:

    def __init__(self) -> None:
        self._client         = OpenAIResponsesClient()
        self._knowledge_base = _load_knowledge_base()

    async def evaluate(self, memory: JourneyMemory, persona: Persona) -> DesignAuditResult:
        images, step_meta = _collect_screenshot_images(memory)
        prompt = self._build_prompt(memory, persona, step_meta)
        raw    = await self._call_llm(prompt, images)
        return self._parse(raw, persona)

    # ── Prompt ────────────────────────────────────────────────────────────────

    def _build_prompt(self, memory: JourneyMemory, persona: Persona, step_meta: list[dict]) -> str:
        dim_list = "\n".join(
            f"  {i+1:02d}. {name} (weight {int(w*100)}%)"
            for i, (name, w) in enumerate(DESIGN_DIMENSIONS)
        )

        screenshot_index = "\n".join(
            f"  Image {i+1}: Step {m['step_number']} | {m['action'].upper()} | {m['url'][:70]}"
            for i, m in enumerate(step_meta)
        ) or "  (no screenshots)"

        return f"""You are a senior visual design auditor evaluating a financial services website.

PERSONA
-------
Name:   {persona.name}
Intent: {persona.intent}

JOURNEY CONTEXT
---------------
Steps:  {memory.step_count} | Terminal reason: {memory.terminal_reason}

DESIGN KNOWLEDGE BASE
---------------------
{self._knowledge_base}

SCREENSHOT INDEX
----------------
The images attached are labelled in this order — use step_number and url when writing step_evaluations:
{screenshot_index}

EVALUATION INSTRUCTIONS
-----------------------
You are provided with {len(step_meta)} screenshots sampled from this persona's journey.
Evaluate the website's design quality in TWO passes:

PASS 1 — PER-SCREENSHOT (step_evaluations)
For EACH screenshot in the index above, produce one step_evaluation entry with:
- step_number: as listed in the index
- url: as listed in the index
- action: as listed in the index
- dimension_scores: for every dimension you can observe in THAT specific screenshot:
    - dimension: exact name from the list below
    - score: 0–10 for what you see on THIS screen specifically
    - is_na: true only if the dimension is completely unobservable in this screenshot
    - observation: ONE specific sentence naming the exact visual element, colour, spacing,
      type treatment, or layout choice you are reacting to — e.g.
      "The card heading uses 14px medium weight with 1.3 line-height — cramped for a dense
       information page" or "The orange CTA button has 4.6:1 contrast ratio — passes AA
       but barely." Never write generic observations. If is_na=true, observation can be empty.

PASS 2 — AGGREGATE (dimension_scores)
For each of the 12 dimensions, aggregate your step-level evidence into a single score
with a 2–3 sentence rationale that cites which specific screens drove the score up or down,
and list 1–3 concrete recommendations.

DESIGN DIMENSIONS:
{dim_list}

SCORING ANCHOR:
  9–10 = exceptional, sets an industry standard
  7–8  = genuinely good, minor issues only
  5–6  = mediocre — works but wastes opportunity
  3–4  = problematic — harms trust or comprehension
  1–2  = broken — actively hurts the experience

Also provide:
- brand_alignment: 2–3 sentences on Bajaj brand expression and financial trust signalling
- critical_issues: design problems observed (severity: critical/major/minor), each with
  the specific screen/element that caused it
- positive_findings: specific design strengths with screen evidence
- design_verdict: one-line verdict (e.g. "Strong visual brand, but spacing inconsistencies hurt trust")
- design_tldr: 2–3 sentence plain-English summary for a non-designer stakeholder
- key_findings: 3–5 single-sentence most important design observations
- wcag_compliance_level: "AA", "A", "Partial A", "Fails A", or "Unknown"
- ds_adherence_level: "High", "Medium", "Low", or "Unknown"
"""

    # ── LLM call ──────────────────────────────────────────────────────────────

    async def _call_llm(self, prompt: str, images: list[dict]) -> dict:
        input_content: list[dict] = [{"type": "input_text", "text": prompt}] + images
        try:
            return await self._client.create_json(
                system_prompt    = "You are a senior visual design auditor. Respond strictly with the requested JSON.",
                input_content    = input_content,
                schema_name      = "design_audit_result",
                schema           = _SCHEMA,
                max_output_tokens= 10000,
            )
        except Exception as exc:
            log.error("Design evaluation LLM call failed: %s", exc)
            return {}

    # ── Parse + aggregate ─────────────────────────────────────────────────────

    def _parse(self, raw: dict, persona: Persona) -> DesignAuditResult:
        # Match returned dimensions to canonical KB names case/space-insensitively
        # so a minor formatting difference doesn't silently drop a real score.
        def _norm(s: str) -> str:
            return "".join((s or "").lower().split())

        raw_by_norm = {_norm(d.get("dimension_name", "")): d for d in raw.get("dimension_scores", [])}

        dimension_scores: list[DesignDimensionScore] = []
        for name, _global_weight in DESIGN_DIMENSIONS:
            d = raw_by_norm.get(_norm(name))
            if d is None:
                # The model did not return this dimension. Mark it not-evaluated
                # rather than emitting a silent 5.0 that masquerades as a real
                # "mediocre" score and skews the weighted average.
                dimension_scores.append(DesignDimensionScore(
                    dimension_name=name, score=0.0, is_na=True,
                    rationale="Not evaluated — no dimension score returned for this journey.",
                    recommendations=[],
                ))
                continue
            dimension_scores.append(DesignDimensionScore(
                dimension_name=name,
                score=float(d.get("score", 5.0)),
                is_na=bool(d.get("is_na", False)),
                rationale=d.get("rationale", ""),
                recommendations=d.get("recommendations", []),
            ))

        non_na_pairs = [
            (global_weight, dim_obj.score)
            for (_, global_weight), dim_obj in zip(DESIGN_DIMENSIONS, dimension_scores)
            if not dim_obj.is_na
        ]
        if non_na_pairs:
            total_active_weight = sum(w for w, _ in non_na_pairs)
            overall = sum(w * score / total_active_weight for w, score in non_na_pairs)
        else:
            # Nothing was evaluated (e.g. LLM/JSON failure). Report 0.0 so the run
            # reads as "no design data" instead of a fabricated 5.0 — the dashboard
            # hides the design tab when the score is 0.
            overall = 0.0
            log.warning("Design audit for %s produced no observable dimensions.", persona.name)

        # Normalise step_evaluations: rename 'observation' → matches dashboard expectation
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

        return DesignAuditResult(
            persona_name=persona.name,
            overall_design_score=round(overall, 2),
            dimension_scores=dimension_scores,
            brand_alignment=raw.get("brand_alignment", ""),
            critical_issues=raw.get("critical_issues", []),
            positive_findings=raw.get("positive_findings", []),
            design_verdict=raw.get("design_verdict", ""),
            design_tldr=raw.get("design_tldr", ""),
            key_findings=raw.get("key_findings", []),
            wcag_compliance_level=raw.get("wcag_compliance_level", ""),
            ds_adherence_level=raw.get("ds_adherence_level", ""),
            step_evaluations=raw_step_evals,
            raw_response=raw,
        )
