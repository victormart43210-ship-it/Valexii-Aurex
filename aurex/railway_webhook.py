"""Inert, bounded Railway webhook intake verification.

Railway's project webhooks are NOT signed, not guaranteed, and not ordered.
A static custom header supplies only shared-secret possession, not signed
provenance. Never treat a parsed webhook as independent evidence or an
authorization to act. No HTTP route, logging or network operation is added.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

_MAX_BYTES = 16 * 1024
_EVENT = re.compile(r"^(Deployment|Service|Volume|Monitor)\.[A-Za-z]{2,32}$")


@dataclass(frozen=True, slots=True)
class WebhookReview:
    status: str
    reason: str
    event_type: str | None = None
    payload_sha256: str | None = None
    authority: str = "NONE"
    independently_verified: bool = False


def review_railway_webhook(
    *,
    bearer_header: str,
    expected_secret: str,
    raw_body: bytes,
    expected_project_id: str,
    expected_environment_id: str,
    now: datetime,
) -> WebhookReview:
    """Review one claimed event; every accepted event needs API reconciliation.

    An untrusted sender could have stolen the shared secret. Callers must
    independently check the event's *current* state using Railway's API before
    using it as operational evidence, and must deduplicate delivery attempts.
    """
    hold = WebhookReview("HOLD", "UNVERIFIED_OR_UNSAFE_DELIVERY")
    if (
        not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None
        or not isinstance(bearer_header, str)
        or not isinstance(expected_secret, str)
        or len(expected_secret) < 32 or len(expected_secret) > 4096
        or not isinstance(raw_body, bytes) or not 0 < len(raw_body) <= _MAX_BYTES
        or not expected_project_id or not expected_environment_id
    ):
        return hold
    if not hmac.compare_digest(bearer_header, "Bearer " + expected_secret):
        return hold
    try:
        body = json.loads(raw_body)
        if not isinstance(body, dict):
            return hold
        event_type = body.get("type")
        if not isinstance(event_type, str) or _EVENT.fullmatch(event_type) is None:
            return hold
        resource = body["resource"]
        if not isinstance(resource, dict):
            return hold
        project, environment = resource["project"], resource["environment"]
        if not isinstance(project, dict) or not isinstance(environment, dict):
            return hold
        if (
            project.get("id") != expected_project_id
            or environment.get("id") != expected_environment_id
        ):
            return hold
        stamp = body["timestamp"]
        if not isinstance(stamp, str) or len(stamp) > 64:
            return hold
        observed_at = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if (
            observed_at.tzinfo is None or observed_at.utcoffset() is None
            or not now - timedelta(minutes=30) <= observed_at <= now + timedelta(minutes=1)
        ):
            return hold
    except (KeyError, TypeError, ValueError, OverflowError):
        return hold
    return WebhookReview(
        status="RECONCILE_WITH_RAILWAY_API",
        reason="SHARED_HEADER_MATCHED_EVENT_UNTRUSTED_UNTIL_RECONCILED",
        event_type=event_type,
        payload_sha256=hashlib.sha256(raw_body).hexdigest(),
    )
