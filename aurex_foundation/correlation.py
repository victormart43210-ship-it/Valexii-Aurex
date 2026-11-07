"""Request correlation middleware; never records sensitive request content."""

import re
import uuid
from contextvars import ContextVar

from starlette.types import ASGIApp, Message, Receive, Scope, Send

request_id_context: ContextVar[str] = ContextVar(
    "aurex_request_id",
    default="",
)

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def correlation_id(incoming: str | None = None) -> str:
    if isinstance(incoming, str) and SAFE_ID.fullmatch(incoming):
        return incoming
    return uuid.uuid4().hex


class CorrelationMiddleware:
    """ASGI middleware that attaches a validated X-Request-ID."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        incoming = headers.get(b"x-request-id", b"").decode(
            "ascii",
            errors="ignore",
        )

        rid = correlation_id(incoming)
        token = request_id_context.set(rid)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                message = dict(message)
                response_headers = list(message.get("headers", []))
                response_headers.append(
                    (b"x-request-id", rid.encode("ascii"))
                )
                message["headers"] = response_headers

            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            request_id_context.reset(token)
