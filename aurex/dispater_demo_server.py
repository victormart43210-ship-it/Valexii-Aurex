"""127.0.0.1-only synthetic DISPATER audit demo. NOT a deployable service."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast

from aurex.dispater_demo import MAX_INPUT_BYTES, build_demo_report
from aurex.dispater_pilot import InvalidSnapshot

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "demo" / "dispater_demo.html"


def make_handler() -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "DISPATER-Synthetic/0.1"

        def _json(self, code: int, value: object) -> None:
            body = json.dumps(value, sort_keys=True).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _local_port(self) -> int:
            return cast(ThreadingHTTPServer, self.server).server_port

        def _valid_host(self) -> bool:
            port = self._local_port()
            return self.headers.get("Host") == f"127.0.0.1:{port}"

        def do_GET(self) -> None:
            if not self._valid_host():
                self._json(403, {"error": "invalid loopback host"})
                return
            if self.path == "/":
                body = HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("X-Frame-Options", "DENY")
                self.send_header(
                    "Content-Security-Policy",
                    "default-src 'none'; connect-src 'self'; style-src 'unsafe-inline'; "
                    "script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
                )
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            sector = {
                "/api/example/towing": "towing",
                "/api/example/oilfield": "oilfield",
            }.get(self.path)
            if sector:
                data = (ROOT / "examples" / f"dispater_{sector}_synthetic.json").read_text("utf-8")
                self._json(200, json.loads(data))
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if not self._valid_host():
                self._json(403, {"error": "invalid loopback host"})
                return
            origin = self.headers.get("Origin")
            if origin is not None and origin != f"http://127.0.0.1:{self._local_port()}":
                self._json(403, {"error": "invalid origin"})
                return
            if self.path != "/api/report":
                self._json(404, {"error": "not found"})
                return
            if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                self._json(415, {"error": "application/json required"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._json(400, {"error": "invalid body length"})
                return
            if length < 1 or length > MAX_INPUT_BYTES:
                self._json(413, {"error": "synthetic input size invalid or too large"})
                return
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                result = build_demo_report(data)
            except (InvalidSnapshot, ValueError, UnicodeDecodeError) as exc:
                self._json(422, {"error": str(exc)[:220]})
                return
            self._json(200, result)

    return Handler


def main() -> None:
    if os.environ.get("DISPATER_ALLOW_LOCAL_SYNTHETIC_DEMO") != "1":
        raise SystemExit(
            "Set DISPATER_ALLOW_LOCAL_SYNTHETIC_DEMO=1 for fictional-data local preview"
        )
    port = int(os.environ.get("DISPATER_LOCAL_PORT", "8777"))
    if not 1024 <= port <= 65535:
        raise SystemExit("Invalid local port")
    with ThreadingHTTPServer(("127.0.0.1", port), make_handler()) as server:
        print(
            f"SYNTHETIC / HOLD — open http://127.0.0.1:{server.server_port}/; "
            "never upload real records"
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
