"""NVIDIA NIM owner-only synthetic connectivity probe; not mounted or deployed.

Mount behind an independently verified owner authentication boundary ONLY.
The additional secret below is not a substitute for authenticated owner identity.
"""
import hmac
import json
import os
import urllib.error
import urllib.request

from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/v1/owner/nvidia", tags=["owner-staging"])
_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
_MODEL = "meta/llama-3.1-8b-instruct"


@router.post("/probe")
def probe_nvidia(authorization: str = Header(default="")):
    """Fixed synthetic prompt only. Never accept user-supplied content."""
    if os.getenv("AUREX_NVIDIA_STAGING_ENABLED") != "true":
        raise HTTPException(503, "NVIDIA staging disabled; HOLD")
    token = os.getenv("AUREX_NVIDIA_PROBE_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(503, "owner probe not configured")
    if not hmac.compare_digest(authorization, "Bearer " + token):
        raise HTTPException(401, "unauthorized")
    api_key = os.getenv("NVIDIA_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "NVIDIA_API_KEY missing in server secrets")
    body = json.dumps({
        "model": _MODEL,
        "messages": [{"role": "user", "content": "Synthetic connection test. Reply with the word READY."}],
        "max_tokens": 32,
        "stream": False,
        "temperature": 0,
    }).encode("utf-8")
    req = urllib.request.Request(
        _ENDPOINT, data=body, method="POST",
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = response.read(16385)
            if len(raw) > 16384:
                raise HTTPException(502, "provider response too large")
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        # Never return provider body or headers, which may contain sensitive data.
        raise HTTPException(502, "NVIDIA provider rejected probe") from None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        raise HTTPException(502, "NVIDIA provider unavailable") from None
    if not isinstance(data, dict) or not data.get("choices"):
        raise HTTPException(502, "unexpected NVIDIA response")
    return {
        "connected": True,
        "model": _MODEL,
        "synthetic": True,
        "authority": "NONE",
        "independentVerification": "NOT_VERIFIED",
        "release": "HOLD",
    }
