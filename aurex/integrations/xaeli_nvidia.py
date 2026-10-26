"""Read-only XAELI compatibility contract; never dispatches inference or writes evidence."""

import os
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/v1/agent", tags=["xaeli-governed-inference"])


@router.get("/status")
def status() -> dict[str, object]:
    missing = []
    if not os.environ.get("AUREX_NVIDIA_API_KEY", "").strip():
        missing.append("provider_credential")
    if not os.environ.get("AUREX_NVIDIA_MODEL", "").strip():
        missing.append("model")
    return {
        "chatConfigured": False,
        "modelProvider": "NVIDIA_NIM",
        "providerConnection": "NOT_VERIFIED",
        "inferenceState": "DISABLED_BY_POLICY",
        "missingConfiguration": missing,
        "budgetLimitUsd": "0.00",
        "budgetAuthorization": "NOT_GRANTED",
        "openshellRuntime": "NOT_VERIFIED",
        "checkedAt": datetime.now(UTC).isoformat(),
        "authority": "NONE",
        "verification": "NOT_VERIFIED",
        "release": "HOLD",
    }


@router.post("/ask")
def ask() -> None:
    # No body parsing, provider object, credential read, reservation or network.
    # A bearer authenticates the service, not financial/model execution authority.
    raise HTTPException(
        403,
        detail={
            "code": "REMOTE_INFERENCE_DISABLED",
            "reason": "Durable spending authorization is unavailable",
            "authority": "NONE",
            "verification": "NOT_VERIFIED",
            "release": "HOLD",
        },
    )
