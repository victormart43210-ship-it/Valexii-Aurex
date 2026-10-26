"""Fail-closed NVIDIA staging readiness endpoint.

No outbound inference. This route is a zero-spend readiness check, not an
NVIDIA connectivity test. Owner identity is enforced by the website gateway;
the backend additionally requires the existing service credential.
"""
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException

router = APIRouter(prefix="/v1/owner/nvidia", tags=["owner-staging"])


def require_service(authorization: str = Header(default="")):
    expected = os.getenv("AUREX_SERVICE_TOKEN", "")
    if len(expected) < 32:
        raise HTTPException(503, "service not configured")
    if not hmac.compare_digest(authorization, "Bearer " + expected):
        raise HTTPException(401, "unauthorized")


@router.post("/probe", dependencies=[Depends(require_service)])
def probe_nvidia():
    """Return staging readiness only. NEVER call NVIDIA from this route."""
    if os.getenv("AUREX_NVIDIA_STAGING_ENABLED") != "true":
        raise HTTPException(503, "NVIDIA staging disabled; HOLD")
    return {
        "connected": False,
        "probeExecuted": False,
        "synthetic": True,
        "spendingUsd": 0,
        "reason": "Provider inference disabled until durable reservation, owner gateway, and audit receipts are verified",
        "authority": "NONE",
        "independentVerification": "NOT_VERIFIED",
        "release": "HOLD",
    }
