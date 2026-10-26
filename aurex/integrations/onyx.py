"""Bounded Onyx search wire adapter. All returned text is untrusted candidate data.

No public live route, evidence writes, qualification promotion, or paid-model authorization.
Contract pin: docs/integrations/ONYX_CAPABILITY_MATRIX.md.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import ssl
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from pydantic import BaseModel, ConfigDict, Field

MAX_BYTES = 262144
Transport = Callable[[str, str, bytes, float], tuple[int, bytes]]
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Principal:
    """Trusted server identity only; never construct from a request's tenant fields."""

    principal_id: str
    tenant_id: str


def _identifier(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", value))


def _secure_url(value: str, hosts: frozenset[str], *, origin: bool = False) -> bool:
    try:
        parsed = urlsplit(value)
        return (
            value.isascii()
            and not any(c.isspace() or ord(c) < 32 for c in value)
            and "\\" not in value
            and parsed.scheme == "https"
            and parsed.hostname in hosts
            and parsed.port in (None, 443)
            and not parsed.username
            and not parsed.password
            and (
                not origin
                or (parsed.path in ("", "/") and not parsed.query and not parsed.fragment)
            )
        )
    except ValueError:
        return False


@dataclass(frozen=True)
class OnyxConfig:
    origin: str
    allowed_host: str
    token: str = field(repr=False)
    tenant_id: str
    principal_id: str
    source_hosts: frozenset[str]
    enabled: bool = False
    isolated_owner_admitted: bool = False
    local_only_inference_admitted: bool = False
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if not _secure_url(self.origin, frozenset({self.allowed_host}), origin=True):
            raise ValueError("invalid Onyx origin")
        if (
            not self.token
            or not self.token.isascii()
            or any(c.isspace() or ord(c) < 33 for c in self.token)
        ):
            raise ValueError("invalid Onyx credential")
        if not _identifier(self.tenant_id) or not _identifier(self.principal_id):
            raise ValueError("invalid configured identity")
        if (
            isinstance(self.timeout_seconds, bool)
            or not math.isfinite(self.timeout_seconds)
            or not 0 < self.timeout_seconds <= 5
        ):
            raise ValueError("invalid timeout")
        if any(
            type(v) is not bool
            for v in (
                self.enabled,
                self.isolated_owner_admitted,
                self.local_only_inference_admitted,
            )
        ):
            raise ValueError("admission flags must be boolean")


class Candidate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
    request_id: str
    tenant_id: str
    principal_id: str
    source_system: Literal["onyx"] = "onyx"
    source_document_id: None = None
    document_version: None = None
    retrieved_at: str
    source_modified_at: str | None
    content_excerpt: str
    title: str
    source_type: str
    source_locator: str | None
    citation: int | None
    retrieval_score: None = None
    access_control_state: Literal["NOT_VERIFIED"] = "NOT_VERIFIED"
    provenance_state: Literal["NOT_VERIFIED"] = "NOT_VERIFIED"
    index_freshness_state: Literal["NOT_VERIFIED"] = "NOT_VERIFIED"
    source_age_state: Literal["RECENT", "STALE", "NOT_VERIFIED"] = "NOT_VERIFIED"
    qualification_state: Literal["HOLD"] = "HOLD"
    content_digest: str
    envelope_digest: str = ""


class Retrieval(BaseModel):
    model_config = ConfigDict(frozen=True)
    status: str
    candidates: tuple[Candidate, ...] = ()
    authority: Literal["NONE"] = "NONE"
    independent_verification: Literal["NOT_VERIFIED"] = "NOT_VERIFIED"


class _WireResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")
    citation_id: int | None
    title: str = Field(max_length=1024)
    content: str = Field(max_length=8192)
    link: str | None
    source_type: str = Field(min_length=1, max_length=100)
    updated_at: str | None


class _WireResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")
    results: list[_WireResult] = Field(max_length=20)


def _envelope_digest(candidate: Candidate) -> str:
    raw = json.dumps(
        candidate.model_dump(exclude={"envelope_digest"}),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_candidate(candidate: Candidate) -> bool:
    """Consistency only; an attacker able to recompute hashes can forge this envelope."""
    return (
        hashlib.sha256(candidate.content_excerpt.encode()).hexdigest() == candidate.content_digest
        and _envelope_digest(candidate) == candidate.envelope_digest
    )


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Request, fp: object, code: int, msg: str, headers: object, newurl: str
    ) -> None:
        raise ValueError("redirect denied")


def https_search(url: str, token: str, body: bytes, timeout: float) -> tuple[int, bytes]:
    """TLS validation on; ambient proxies off; no redirects/retries; bounded response."""
    opener = build_opener(
        ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()), _NoRedirect()
    )
    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            return int(response.status), response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        code = exc.code
        exc.close()
        return code, b""


class OnyxAdapter:
    def __init__(self, config: OnyxConfig):
        self.config = config

    def search(
        self,
        query: str,
        principal: Principal | None,
        *,
        request_id: str,
        transport: Transport = https_search,
        now: datetime | None = None,
    ) -> Retrieval:
        config = self.config
        if (
            principal is None
            or principal.tenant_id != config.tenant_id
            or principal.principal_id != config.principal_id
        ):
            return self._result("ACCESS_NOT_VERIFIED")
        if not (
            config.enabled
            and config.isolated_owner_admitted
            and config.local_only_inference_admitted
        ):
            return self._result("RETRIEVAL_UNAVAILABLE")
        if (
            not isinstance(query, str)
            or not query.strip()
            or len(query) > 512
            or not _identifier(request_id)
        ):
            return self._result("INVALID_REQUEST")
        at = now or datetime.now(UTC)
        if at.tzinfo is None or at.utcoffset() is None:
            return self._result("INVALID_REQUEST")
        try:
            code, raw = transport(
                config.origin.rstrip("/") + "/api/search",
                config.token,
                json.dumps({"query": query, "skip_query_expansion": True}).encode(),
                config.timeout_seconds,
            )
        except Exception:
            # Provider exceptions may contain secrets; do not log or chain them.
            return self._result("RETRIEVAL_UNAVAILABLE")
        if code != 200:
            return self._result(
                {401: "AUTHENTICATION_FAILED", 403: "AUTHORIZATION_FAILED"}.get(
                    code, "RETRIEVAL_UNAVAILABLE"
                )
            )
        try:
            if len(raw) > MAX_BYTES:
                raise ValueError("response exceeds limit")
            wire = _WireResponse.model_validate(json.loads(raw, object_pairs_hook=_unique_keys))
            candidates: list[Candidate] = []
            seen: set[tuple[str | None, str]] = set()
            for row in wire.results:
                if row.link is not None and (
                    len(row.link) > 2048 or not _secure_url(row.link, config.source_hosts)
                ):
                    raise ValueError("unapproved citation")
                age: Literal["RECENT", "STALE", "NOT_VERIFIED"] = "NOT_VERIFIED"
                if row.updated_at:
                    try:
                        timestamp = datetime.fromisoformat(row.updated_at.replace("Z", "+00:00"))
                        if timestamp.tzinfo is not None:
                            seconds = (at - timestamp).total_seconds()
                            if seconds >= 0:
                                age = "STALE" if seconds > 30 * 86400 else "RECENT"
                    except ValueError:
                        pass
                content_hash = hashlib.sha256(row.content.encode()).hexdigest()
                key = (row.link, content_hash)
                if key in seen:
                    continue
                seen.add(key)
                c = Candidate(
                    request_id=request_id,
                    tenant_id=principal.tenant_id,
                    principal_id=principal.principal_id,
                    retrieved_at=at.astimezone(UTC).isoformat(),
                    source_modified_at=row.updated_at,
                    content_excerpt=row.content,
                    title=row.title,
                    source_type=row.source_type,
                    source_locator=row.link,
                    citation=row.citation_id,
                    source_age_state=age,
                    content_digest=content_hash,
                )
                candidates.append(c.model_copy(update={"envelope_digest": _envelope_digest(c)}))
            return self._result("CANDIDATES" if candidates else "EMPTY", tuple(candidates))
        except (ValueError, TypeError, OverflowError, RecursionError):
            return self._result("INVALID_RESPONSE")

    @staticmethod
    def _result(status: str, candidates: tuple[Candidate, ...] = ()) -> Retrieval:
        logger.info("onyx_retrieval status=%s count=%d", status, len(candidates))
        return Retrieval(status=status, candidates=candidates)
