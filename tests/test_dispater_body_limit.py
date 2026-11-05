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


# --- CCXXI: boundary, interruption and concurrency against a minimal inner app ---


async def _drain_app(scope: Any, receive: Any, send: Any) -> None:
    total = 0
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            return
        total += len(message.get("body", b""))
        if not message.get("more_body"):
            break
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": str(total).encode()})


def _limited(limit: int) -> Any:
    return dispater_api.BodyLimitMiddleware(_drain_app, max_bytes=limit)


def test_exactly_at_limit_is_accepted_and_one_over_is_rejected() -> None:
    limit = 1000
    ok = asyncio.run(_call(_limited(limit), [b"a" * 400, b"a" * 600], [], path="/v1/dispater/x"))
    assert ok[1] == [200]
    over = asyncio.run(_call(_limited(limit), [b"a" * 400, b"a" * 601], [], path="/v1/dispater/x"))
    assert over[1] == [413]


def test_exact_content_length_at_limit_passes_and_one_over_fails() -> None:
    limit = 1000
    at = [(b"content-length", b"1000")]
    assert asyncio.run(_call(_limited(limit), [b"a" * 1000], at, path="/v1/dispater/x"))[1] == [200]
    over = [(b"content-length", b"1001")]
    assert asyncio.run(_call(_limited(limit), [b"a"], over, path="/v1/dispater/x"))[1] == [413]


def test_interrupted_upload_does_not_raise_or_send_413() -> None:
    async def scenario() -> list[int | None]:
        sent: list[dict[str, Any]] = []
        queue: list[dict[str, Any]] = [
            {"type": "http.request", "body": b"abc", "more_body": True},
            {"type": "http.disconnect"},
        ]

        async def receive() -> dict[str, Any]:
            return queue.pop(0)

        async def send(message: dict[str, Any]) -> None:
            sent.append(message)

        scope = {"type": "http", "path": "/v1/dispater/x", "headers": []}
        await _limited(1000)(scope, receive, send)
        return [m.get("status") for m in sent if m["type"] == "http.response.start"]

    assert asyncio.run(scenario()) == []


def test_concurrent_uploads_are_isolated() -> None:
    async def scenario() -> list[list[int | None]]:
        app = _limited(1000)
        jobs = [
            _call(app, [b"a" * (500 if i % 2 else 1500)], [], path="/v1/dispater/x") for i in range(20)
        ]
        return [r[1] for r in await asyncio.gather(*jobs)]

    results = asyncio.run(scenario())
    assert results == [[200] if i % 2 else [413] for i in range(20)]


def test_slow_streaming_client_still_bounded() -> None:
    chunks = [b"a" * 10] * 200  # many tiny chunks totalling 2000 > 1000
    received, statuses = asyncio.run(_call(_limited(1000), chunks, [], path="/v1/dispater/x"))
    assert statuses == [413]
    assert received <= 1010
