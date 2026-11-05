"""Regression tests for CCXIX defect D-1: DISPATER body limit must act on the raw stream."""

import asyncio
from typing import Any

from fastapi import FastAPI

from aurex import dispater_api
from aurex.api import app as aurex_app

PATH = "/v1/dispater/reconciliation"
CHUNK = b"x" * (1024 * 1024)


def _bare_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(dispater_api.BodyLimitMiddleware)
    app.include_router(dispater_api.router)
    return app


async def _call(
    app: Any, chunks: list[bytes], headers: list[tuple[bytes, bytes]], path: str = PATH
) -> tuple[int, list[int | None]]:
    queue = list(chunks)
    received = 0

    async def receive() -> dict[str, Any]:
        nonlocal received
        if queue:
            chunk = queue.pop(0)
            received += len(chunk)
            return {"type": "http.request", "body": chunk, "more_body": bool(queue)}
        await asyncio.sleep(30)
        return {"type": "http.disconnect"}

    sent: list[dict[str, Any]] = []

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 1),
        "server": ("test", 80),
        "scheme": "http",
        "root_path": "",
    }
    await asyncio.wait_for(app(scope, receive, send), 10)
    statuses = [m.get("status") for m in sent if m["type"] == "http.response.start"]
    return received, statuses


JSON_HEADER = (b"content-type", b"application/json")


def test_chunked_oversize_is_rejected_without_full_buffering() -> None:
    received, statuses = asyncio.run(_call(_bare_app(), [CHUNK] * 20, [JSON_HEADER]))
    assert statuses == [413]
    assert received <= dispater_api.MAX_BODY_BYTES + len(CHUNK)


def test_dishonest_small_content_length_is_still_bounded() -> None:
    headers = [JSON_HEADER, (b"content-length", b"10")]
    received, statuses = asyncio.run(_call(_bare_app(), [CHUNK] * 20, headers))
    assert statuses == [413]
    assert received <= dispater_api.MAX_BODY_BYTES + len(CHUNK)


def test_declared_oversize_content_length_rejected_before_reading() -> None:
    headers = [JSON_HEADER, (b"content-length", str(dispater_api.MAX_BODY_BYTES + 1).encode())]
    received, statuses = asyncio.run(_call(_bare_app(), [CHUNK], headers))
    assert statuses == [413]
    assert received == 0


def test_malformed_content_length_rejected() -> None:
    headers = [JSON_HEADER, (b"content-length", b"-5")]
    _, statuses = asyncio.run(_call(_bare_app(), [b"{}"], headers))
    assert statuses == [413]


def test_legitimate_body_reaches_the_route_unconsumed() -> None:
    body = b'{"tenant_id": "t"}'
    headers = [JSON_HEADER, (b"content-length", str(len(body)).encode())]
    _, statuses = asyncio.run(_call(_bare_app(), [body], headers))
    # Not 413: the body passed the limiter and was parsed downstream (auth/validation reject it).
    assert statuses and statuses[0] != 413


def test_limit_is_installed_on_the_real_aurex_app() -> None:
    received, statuses = asyncio.run(_call(aurex_app, [CHUNK] * 20, [JSON_HEADER]))
    assert statuses == [413]
    assert received <= dispater_api.MAX_BODY_BYTES + len(CHUNK)


def test_non_dispater_paths_are_untouched() -> None:
    _, statuses = asyncio.run(_call(_bare_app(), [CHUNK] * 6, [JSON_HEADER], path="/nope"))
    assert statuses == [404]
