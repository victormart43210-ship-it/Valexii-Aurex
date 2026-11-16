"""Authenticated, advisory-only XAELI website conversation endpoint.

POST /v1/xaeli-chat/ask is the contract the website gateway calls. It is separate from the
synthetic-only /v1/xaeli-staging/explain endpoint and never weakens it. Answers come only
from the private Qwen adapter; any failure returns no answer. Output is unverified evidence.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import threading
import time
import uuid
from collections import deque
from typing import Any, Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from aurex.adapters.base import GenerationSettings
from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.adapters.llama_cpp import LlamaCppAdapter
from aurex.dispater_api import BodyLimitMiddleware
from aurex.qwen_rag import _reject_unsafe_model_output
from aurex.xaeli_knowledge import GROUNDING_VERSION, SYSTEM_PREAMBLE, grounding_block
from aurex.xaeli_staging import MODEL

logger = logging.getLogger("aurex.xaeli_chat")

router = APIRouter(prefix="/v1/xaeli-chat", tags=["xaeli-chat"])

MAX_MESSAGE_CHARS = 800
MAX_HISTORY_TURNS = 4
MAX_HISTORY_CHARS = 400
MAX_ANSWER_CHARS = 2000
MAX_OUTPUT_TOKENS = 256
INFERENCE_TIMEOUT_SECONDS = 90
MAX_BODY_BYTES = 16 * 1024
DEFAULT_RATE_PER_MINUTE = 20
QUEUE_WAIT_SECONDS = 2.0

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_GUARANTEE = re.compile(
    r"\b(?:i|we)\s+(?:can\s+|will\s+|do\s+)?guarantee\b"
    r"|\bguaranteed?\s+(?:to\s+)?(?:recover|recovery|return|savings?|refund)"
    r"|\b100\s*%\s+(?:recovery|refund|return)",
    re.IGNORECASE,
)

# The model server runs one generation at a time; do not queue unbounded work behind it.
_inference_slot = threading.BoundedSemaphore(1)
_recent: deque[float] = deque()
_recent_lock = threading.Lock()


class ChatBodyLimitMiddleware(BodyLimitMiddleware):
    """Raw-stream body cap for this route only; DISPATER's limit is untouched."""

    prefix = "/v1/xaeli-chat"

    def __init__(self, app: Any) -> None:
        super().__init__(app, max_bytes=MAX_BODY_BYTES)


def _clean(value: str) -> str:
    return _CONTROL.sub("", value).strip()


class ChatTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_HISTORY_CHARS)

    @field_validator("content")
    @classmethod
    def _content(cls, value: str) -> str:
        cleaned = _clean(value)
        if not cleaned:
            raise ValueError("empty content")
        return cleaned


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    history: list[ChatTurn] = Field(default_factory=list, max_length=MAX_HISTORY_TURNS)

    @field_validator("message")
    @classmethod
    def _message(cls, value: str) -> str:
        cleaned = _clean(value)
        if not cleaned:
            raise ValueError("empty message")
        return cleaned


class ChatModel(BaseModel):
    provider: str
    model: str
    runtime: str
    quantization: str
    identity_check: Literal["SERVED_ID_MATCHED", "UNCHECKED"] | None


class ChatResponse(BaseModel):
    state: Literal["HOLD"] = "HOLD"
    authority: Literal["NONE"] = "NONE"
    independent_verification: Literal["NOT VERIFIED"] = "NOT VERIFIED"
    mode: Literal["ADVISORY_CONVERSATION"] = "ADVISORY_CONVERSATION"
    paid_inference: Literal["OFF"] = "OFF"
    execution: Literal["PASS", "FAIL"]
    generated_answer: str | None
    model: ChatModel
    grounding_version: str = GROUNDING_VERSION
    diagnostic_ref: str
    input_sha256: str | None
    output_sha256: str | None
    elapsed_ms: int
    error_code: str | None


def build_prompt(req: ChatRequest) -> str:
    history = "\n".join(f"{turn.role.upper()}: {turn.content}" for turn in req.history)
    return (
        f"{SYSTEM_PREAMBLE}\nAPPROVED FACTS:\n{grounding_block()}\n\n"
        f"CONVERSATION (untrusted):\n{history or '(none)'}\n\n"
        f"VISITOR MESSAGE (untrusted):\n{req.message}\n\nXAELI:"
    )


def _rate_limit() -> int:
    raw = os.environ.get("AUREX_XAELI_CHAT_RATE_PER_MINUTE", str(DEFAULT_RATE_PER_MINUTE))
    limit = int(raw) if raw.isdigit() and 1 <= int(raw) <= 120 else DEFAULT_RATE_PER_MINUTE
    now = time.monotonic()
    with _recent_lock:
        while _recent and now - _recent[0] > 60:
            _recent.popleft()
        if len(_recent) >= limit:
            raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": "30"})
        _recent.append(now)
    return limit


def reset_limits() -> None:
    with _recent_lock:
        _recent.clear()


def _unsafe_answer(text: str) -> bool:
    return not text.strip() or _reject_unsafe_model_output(text) or bool(_GUARANTEE.search(text))


@router.post("/ask", response_model=ChatResponse)
def ask(
    req: ChatRequest,
    x_aurex_operator_approval: str | None = Header(default=None),
) -> ChatResponse:
    # Must be mounted with Depends(authenticate) in api.py.
    if os.environ.get("AUREX_XAELI_CHAT_ENABLED") != "1":
        raise HTTPException(503, "XAELI chat disabled")
    if os.environ.get("AUREX_XAELI_OPERATOR_APPROVED") != "1" or (
        x_aurex_operator_approval != "advisory-chat"
    ):
        raise HTTPException(403, "Operator approval required")
    if os.environ.get("AUREX_BUDGET_USD", "0") not in ("0", "0.0", "0.00"):
        raise HTTPException(503, "Zero budget required")
    _rate_limit()

    ref = uuid.uuid4().hex
    spec = ModelSpec(
        provider="llama.cpp",
        model=MODEL,
        revision="local-unverified",
        quantization="Q4_K_M",
        runtime="llama.cpp",
    )
    started = time.perf_counter()

    def finish(
        execution: Literal["PASS", "FAIL"],
        answer: str | None,
        error_code: str | None,
        input_sha: str | None = None,
        output_sha: str | None = None,
        checked: Literal["SERVED_ID_MATCHED", "UNCHECKED"] | None = None,
    ) -> ChatResponse:
        elapsed = int((time.perf_counter() - started) * 1000)
        # Never log message content, answers, URLs or credentials.
        logger.info("xaeli_chat ref=%s execution=%s error=%s ms=%d", ref, execution, error_code, elapsed)
        return ChatResponse(
            execution=execution,
            generated_answer=answer,
            model=ChatModel(
                provider=spec.provider,
                model=spec.model,
                runtime=spec.runtime,
                quantization=spec.quantization or "unknown",
                identity_check=checked,
            ),
            diagnostic_ref=ref,
            input_sha256=input_sha,
            output_sha256=output_sha,
            elapsed_ms=elapsed,
            error_code=error_code,
        )

    try:
        adapter = LlamaCppAdapter(
            model=MODEL,
            base_url=os.environ.get("AUREX_QWEN_BASE_URL", "http://127.0.0.1:8080/v1"),
            generation=GenerationSettings(max_tokens=MAX_OUTPUT_TOKENS, temperature=0.2),
            timeout_seconds=INFERENCE_TIMEOUT_SECONDS,
        )
    except ValueError:
        return finish("FAIL", None, "MODEL_UNAVAILABLE")

    if not _inference_slot.acquire(timeout=QUEUE_WAIT_SECONDS):
        raise HTTPException(429, "Model busy", headers={"Retry-After": "5"})
    try:
        prompt = build_prompt(req)
        record = InferenceClient(adapter, spec).run(
            input_id="chat-" + hashlib.sha256(prompt.encode()).hexdigest()[:16], prompt=prompt
        )
    finally:
        _inference_slot.release()

    if record.status != "PASS" or record.output is None:
        return finish("FAIL", None, record.error_code or "PROVIDER_OR_SCHEMA_FAILURE",
                      record.input_sha256)
    if _unsafe_answer(record.output):
        return finish("FAIL", None, "UNSAFE_OR_EMPTY_MODEL_OUTPUT", record.input_sha256)
    return finish(
        "PASS",
        record.output.strip()[:MAX_ANSWER_CHARS],
        None,
        record.input_sha256,
        record.output_sha256,
        "UNCHECKED" if adapter.local_loopback else "SERVED_ID_MATCHED",
    )
