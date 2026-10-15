"""KUSANAGI XXII: local inference execution boundary.

Model output is evidence, never independent authority.
No inference occurs without an approved workflow job.
"""

from __future__ import annotations

from typing import Any

from aurex.local_inference import run_local_inference


def execute_local_model(
    *,
    payload: dict[str, Any],
    approved: bool,
) -> dict[str, Any]:
    """Execute one explicitly approved local model request."""

    if approved is not True:
        raise PermissionError("workflow approval required")

    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    prompt = payload.get("prompt")
    model = payload.get("model")
    base_url = payload.get("base_url", "http://127.0.0.1:8080")
    backend = payload.get("backend", "llama.cpp")

    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")

    if not isinstance(model, str):
        raise ValueError("model must be a string")

    result = run_local_inference(
        prompt=prompt,
        model=model,
        base_url=base_url,
        backend=backend,
        approved=True,
        timeout_seconds=120.0,
    )

    return {
        "status": "LOCAL_INFERENCE_COMPLETED",
        "provider": result.provider,
        "model": result.model,
        "text": result.text,
        "sha256": result.sha256,
        "verified": False,
        "authority_granted": False,
        "spend_usd": 0.0,
    }
