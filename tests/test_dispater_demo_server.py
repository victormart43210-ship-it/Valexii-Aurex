"""Loopback-only HTTP smoke tests of the synthetic DISPATER interface."""

from __future__ import annotations

import http.client
import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from aurex.dispater_demo_server import make_handler

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def local_demo_server() -> Iterator[int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def request(
    port: int, method: str, path: str, body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, Any]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        payload = response.read()
        if response.getheader("Content-Type", "").startswith("application/json"):
            return response.status, json.loads(payload)
        return response.status, payload.decode("utf-8")
    finally:
        conn.close()


def test_local_browser_renders_explicit_synthetic_disclaimer() -> None:
    with local_demo_server() as port:
        code, html = request(port, "GET", "/")
        assert code == 200
        assert "CONCEPT PREVIEW" in html
        assert "NVIDIA" in html
        assert "NOT RUN" in html


def test_local_example_audit_and_human_review() -> None:
    with local_demo_server() as port:
        code, example = request(port, "GET", "/api/example/towing")
        assert code == 200
        assert example["dataset_type"] == "SYNTHETIC_ONLY"
        body = json.dumps(example).encode()
        code, report = request(
            port, "POST", "/api/report", body=body,
            headers={"Content-Type": "application/json"},
        )
        assert code == 200
        assert report["counts"]["revenue_findings"] == 3
        assert report["status"] == "HOLD"
        assert report["nvidia_inference"] == "NOT RUN"
        first = report["findings"][0]["finding_id"]
        example["review"]["decisions"] = [{
            "finding_id": first, "decision": "ACKNOWLEDGED", "note": "demo only",
        }]
        code, revised = request(
            port, "POST", "/api/report", body=json.dumps(example).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert code == 200
        assert revised["counts"]["reviewed"] == 1
        assert revised["status"] == "HOLD"


def test_rejects_real_inputs_origin_mismatch_and_non_json() -> None:
    with local_demo_server() as port:
        example = json.loads(
            (ROOT / "examples" / "dispater_towing_synthetic.json").read_text()
        )
        example["dataset_type"] = "REAL_CUSTOMER"
        code, _ = request(port, "POST", "/api/report", body=json.dumps(example).encode(),
                          headers={"Content-Type": "application/json"})
        assert code == 422
        example["dataset_type"] = "SYNTHETIC_ONLY"
        code, _ = request(port, "POST", "/api/report", body=json.dumps(example).encode(),
                          headers={"Content-Type": "application/json", "Origin": "https://evil.example"})
        assert code == 403
        code, _ = request(port, "POST", "/api/report", body=b"anything",
                          headers={"Content-Type": "text/plain"})
        assert code == 415
