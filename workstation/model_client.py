"""Bounded OpenAI-compatible chat completion client; stdlib only."""
import json
import os
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

def generate(question):
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError("Question must be 1–4000 characters")
    endpoint = os.environ.get("AUREX_MODEL_ENDPOINT", "").strip()
    model = os.environ.get("AUREX_MODEL_NAME", "").strip()
    if not endpoint or not model:
        raise ValueError("Model not configured. Set AUREX_MODEL_ENDPOINT and AUREX_MODEL_NAME.")
    parsed = urlsplit(endpoint)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Invalid model endpoint")
    if parsed.scheme == "http" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("Remote endpoints must use HTTPS")
    if not endpoint.endswith("/chat/completions"):
        raise ValueError("Endpoint must end in /chat/completions")
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": question}], "temperature": 0, "max_tokens": 256, "stream": False}).encode()
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("AUREX_MODEL_API_KEY", "")
    if key:
        headers["Authorization"] = "Bearer " + key
    req = Request(endpoint, data=payload, headers=headers, method="POST")
    with urlopen(req, timeout=45) as response:
        if int(response.headers.get("Content-Length", "0")) > 200000:
            raise ValueError("Model response too large")
        raw = response.read(200001)
    if len(raw) > 200000:
        raise ValueError("Model response too large")
    obj = json.loads(raw)
    answer = obj["choices"][0]["message"]["content"]
    if not isinstance(answer, str):
        raise ValueError("Model returned non-text answer")
    return {"status": "GENERATED_NOT_VERIFIED", "model": model, "answer": answer[:12000], "official_hle": False, "independent_validation": "NOT_VERIFIED"}
