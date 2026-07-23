"""
OpenAI Responses API wrapper.

All model calls in the audit system go through this module so prompts,
schema enforcement, retries, and multimodal input formatting stay separate
from browser/Appium execution logic.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

import httpx
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

import config


# ── Pricing (INR per 1M tokens) ───────────────────────────────────────────────
# Flat INR rates for the model this system runs on, applied directly to the token
# counts. Previously cost was looked up in a USD-per-model table and converted; a
# model name absent from that table fell through to 0.0, which is why every run's
# tile showed ₹0.00. Rates below are per 1,000,000 tokens.
_INR_PER_1M_INPUT        = 165.19    # uncached prompt tokens
_INR_PER_1M_CACHED_INPUT = 16.52     # prompt tokens served from cache
_INR_PER_1M_OUTPUT       = 1321.52   # completion tokens


def compute_cost_inr(
    input_tokens: int,
    output_tokens: int,
    model: str = "",
    cached_input_tokens: int = 0,
) -> float:
    """Return the estimated cost in INR for a completed LLM call.

    `input_tokens` is the total prompt tokens (cached + uncached), matching the
    OpenAI usage object; `cached_input_tokens` is the cached subset, billed at the
    lower cached rate. `model` is accepted for backward compatibility but no longer
    affects the rate.
    """
    uncached_input = max(0, input_tokens - cached_input_tokens)
    cost = (
        uncached_input        / 1_000_000 * _INR_PER_1M_INPUT
        + cached_input_tokens / 1_000_000 * _INR_PER_1M_CACHED_INPUT
        + output_tokens       / 1_000_000 * _INR_PER_1M_OUTPUT
    )
    return round(cost, 4)


def _cached_tokens_from_usage(usage: Any) -> int:
    """Extract cached prompt-token count from an OpenAI usage object.

    Returns 0 when the field is absent (older responses, non-cached calls), so the
    caller simply bills all input at the full rate.
    """
    details = getattr(usage, "input_tokens_details", None)
    if details is None and isinstance(usage, dict):
        details = usage.get("input_tokens_details")
    if details is None:
        return 0
    if isinstance(details, dict):
        return int(details.get("cached_tokens", 0) or 0)
    return int(getattr(details, "cached_tokens", 0) or 0)


class OpenAIResponsesClient:
    """Thin async wrapper over the synchronous OpenAI Responses API client."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        key = api_key or config.OPENAI_API_KEY
        if not key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        self._client = OpenAI(
            api_key=key,
            timeout=config.OPENAI_TIMEOUT_SECONDS,
            http_client=httpx.Client(http2=False),
        )
        self._input_tokens: int = 0
        self._output_tokens: int = 0
        self._cached_input_tokens: int = 0

    async def create_json(
        self,
        *,
        system_prompt: str,
        input_content: str | list[dict[str, Any]],
        schema_name: str,
        schema: dict[str, Any],
        model: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        max_retries: int = 4,
    ) -> dict[str, Any]:
        """Return a JSON object matching the supplied strict JSON schema.

        max_output_tokens=None (default) lets OpenAI use the model's full
        output capacity — no artificial cap.  Pass an explicit integer only
        when you want to deliberately constrain the response length.
        """
        delay = 2.0
        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                call_kwargs: dict[str, Any] = dict(
                    model=model or config.OPENAI_MODEL,
                    instructions=system_prompt,
                    input=[{"role": "user", "content": _normalise_content(input_content)}],
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": schema_name,
                            "strict": True,
                            "schema": _schema_for_openai(schema),
                        }
                    },
                    store=False,
                )
                if max_output_tokens is not None:
                    call_kwargs["max_output_tokens"] = max_output_tokens

                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._client.responses.create(**call_kwargs),
                )
                usage = getattr(response, "usage", None)
                if usage:
                    self._input_tokens        += getattr(usage, "input_tokens",  0)
                    self._output_tokens       += getattr(usage, "output_tokens", 0)
                    self._cached_input_tokens += _cached_tokens_from_usage(usage)
                return _extract_json_object(response)

            except RateLimitError as exc:
                last_error = exc
                if attempt >= max_retries - 1:
                    break
                # For TPM rate limits, respect the retry-after hint if present,
                # otherwise back off generously (15s, 30s, 60s).
                _retry_after = getattr(exc, "response", None)
                _retry_after = (
                    float(_retry_after.headers.get("retry-after", 0))
                    if _retry_after and hasattr(_retry_after, "headers")
                    else 0.0
                )
                _sleep = max(_retry_after + 1.0, 15.0 * (2 ** attempt))
                await asyncio.sleep(_sleep)

            except (APITimeoutError, APIConnectionError) as exc:
                last_error = exc
                if attempt >= max_retries - 1:
                    break
                await asyncio.sleep(delay * (2 ** attempt))

            except APIStatusError as exc:
                last_error = exc
                if exc.status_code in (500, 502, 503, 504, 529) and attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                    continue
                raise

            except Exception as exc:
                last_error = exc
                if attempt >= max_retries - 1:
                    break
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"OpenAI Responses API failed after {max_retries} attempts. Last error: {last_error}"
        )

    async def respond(
        self,
        *,
        model: Optional[str] = None,
        input: list[dict[str, Any]],
        max_output_tokens: int = 50,
    ) -> Any:
        """
        Free-text (non-JSON) response from the Responses API.
        Returns the raw response object so callers can walk response.output
        themselves to extract the text they need.
        Used for lightweight helper calls (intent matching, vision checks)
        where a strict JSON schema would add unnecessary overhead.

        `input` must be a list of message dicts: [{"role": "user", "content": [...]}]
        where content is a list of Responses API content blocks (input_text / input_image).
        """
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._client.responses.create(
                model=model or config.OPENAI_MODEL,
                input=input,
                max_output_tokens=max_output_tokens,
                store=False,
            ),
        )
        usage = getattr(response, "usage", None)
        if usage:
            self._input_tokens        += getattr(usage, "input_tokens",  0)
            self._output_tokens       += getattr(usage, "output_tokens", 0)
            self._cached_input_tokens += _cached_tokens_from_usage(usage)
        return response

    def pop_usage(self) -> dict[str, int]:
        """Return accumulated token counts since last call and reset the counters."""
        result = {
            "input_tokens":         self._input_tokens,
            "output_tokens":        self._output_tokens,
            "cached_input_tokens":  self._cached_input_tokens,
        }
        self._input_tokens        = 0
        self._output_tokens       = 0
        self._cached_input_tokens = 0
        return result


def image_content(text: str, image_b64: str, media_type: str = "image/jpeg") -> list[dict[str, Any]]:
    """Build a Responses API multimodal content list from text and base64 image data."""
    return [
        {"type": "input_text", "text": text},
        {
            "type": "input_image",
            "image_url": f"data:{media_type};base64,{image_b64}",
            "detail": "high",
        },
    ]


def text_content(text: str) -> list[dict[str, Any]]:
    """Build a Responses API text-only content list."""
    return [{"type": "input_text", "text": text}]


def _normalise_content(content: str | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Accept native Responses content or legacy Anthropic-style content blocks."""
    if isinstance(content, str):
        return text_content(content)

    normalised: list[dict[str, Any]] = []
    for item in content:
        item_type = item.get("type")
        if item_type in {"input_text", "input_image", "input_file"}:
            normalised.append(item)
        elif item_type == "text":
            normalised.append({"type": "input_text", "text": item.get("text", "")})
        elif item_type == "image":
            source = item.get("source") or {}
            data = source.get("data", "")
            media_type = source.get("media_type", "image/jpeg")
            if data:
                normalised.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:{media_type};base64,{data}",
                        "detail": "high",
                    }
                )
    if not normalised:
        raise ValueError("No valid OpenAI input content blocks were supplied.")
    return normalised


def _schema_for_openai(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise a JSON schema for OpenAI strict structured outputs.
    - Adds additionalProperties: False and required: [all keys] to every object node.
    - Removes minimum/maximum (enforced in application code instead).
    """
    copied = json.loads(json.dumps(schema))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("minimum", None)
            node.pop("maximum", None)
            if node.get("type") == "object":
                props = node.get("properties", {})
                node["additionalProperties"] = False
                node["required"] = list(props.keys())
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(copied)
    return copied


def _extract_json_object(response: Any) -> dict[str, Any]:
    # Check for response-level truncation before touching the text.
    status = getattr(response, "status", None)
    if status == "incomplete":
        details = getattr(response, "incomplete_details", None)
        reason  = getattr(details, "reason", "unknown") if details else "unknown"
        raise ValueError(
            f"OpenAI response was truncated (status=incomplete, reason={reason}). "
            "The output was cut off before the JSON could be completed. "
            "This usually means the response was longer than the model's output limit — "
            "remove the max_output_tokens cap or reduce the prompt size."
        )

    raw = getattr(response, "output_text", "") or ""
    if not raw:
        parts: list[str] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", "") != "message":
                continue
            for content in getattr(item, "content", []) or []:
                ctype = getattr(content, "type", "")
                if ctype == "output_text":
                    parts.append(getattr(content, "text", ""))
                elif ctype == "refusal":
                    refusal = getattr(content, "refusal", "Model refused the request.")
                    raise ValueError(f"OpenAI refused to produce structured output: {refusal}")
        raw = "".join(parts)

    if not raw.strip():
        raise ValueError("OpenAI response did not contain output_text.")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        # Surface truncation clearly — a partial JSON almost always means the
        # output was cut off even if the status didn't say "incomplete".
        raise ValueError(
            f"OpenAI response JSON could not be parsed (likely truncated output): {exc}. "
            f"Raw tail: ...{raw[-200:]!r}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("OpenAI structured output was not a JSON object.")
    return parsed
