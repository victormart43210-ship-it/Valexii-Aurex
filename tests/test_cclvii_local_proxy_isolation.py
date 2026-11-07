"""Local-only inference must deliver prompts directly even when a proxy is configured."""
import json
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest

from aurex.adapters.ollama import OllamaAdapter
from aurex.local_inference import run_local_inference


@contextmanager
def local_receiver(reply: str) -> Iterator[tuple[str, list[tuple[str, bytes]]]]:
    received: list[tuple[str, bytes]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            body = self.rfile.read(int(self.headers["Content-Length"]))
            received.append((self.path, body))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"response": reply}).encode())

        def log_message(self, format: str, *args: object) -> None:
            pass

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02})
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", received
        finally:
            server.shutdown()
            thread.join()


@pytest.mark.parametrize("client", ["local_inference", "ollama_adapter"])
def test_local_prompt_bypasses_configured_proxy(client: str, monkeypatch: pytest.MonkeyPatch) -> None:
    prompt = "synthetic isolated prompt"
    with local_receiver("direct") as (endpoint, direct), local_receiver("proxy") as (proxy_url, proxy):
        for key in ("http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
            monkeypatch.setenv(key, proxy_url)
        for key in ("no_proxy", "NO_PROXY"):
            monkeypatch.delenv(key, raising=False)
        if client == "local_inference":
            result = run_local_inference(
                prompt=prompt, model="synthetic", backend="ollama", base_url=endpoint,
                approved=True, timeout_seconds=2,
            )
        else:
            result = OllamaAdapter("synthetic", endpoint, timeout_seconds=2).answer(prompt)
        assert proxy == []
        assert result.text == "direct"
        assert len(direct) == 1
        path, body = direct[0]
        assert path == "/api/generate"
        assert json.loads(body)["prompt"] == prompt
