"""Governed local inference; model output is unverified evidence, never authority."""
from __future__ import annotations
import hashlib
import ipaddress
import json
import socket
from dataclasses import dataclass
from urllib.request import Request, build_opener, HTTPHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

MAX_PROMPT_BYTES = 8192
MAX_RESPONSE_BYTES = 131072

class LocalInferenceError(RuntimeError):
    pass

class _NoRedirect(HTTPHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise LocalInferenceError('redirect refused')
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302

@dataclass(frozen=True)
class LocalResult:
    provider: str
    model: str
    text: str
    sha256: str
    verified: bool = False
    authority_granted: bool = False

def _endpoint(base_url: str) -> str:
    p = urlsplit(base_url)
    if p.scheme != 'http' or p.username or p.password or p.query or p.fragment:
        raise ValueError('only unauthenticated HTTP loopback endpoints are allowed')
    if p.hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('non-loopback inference endpoint rejected')
    if p.path not in ('', '/'):
        raise ValueError('base URL must not contain a path')
    try:
        port = p.port
    except ValueError as exc:
        raise ValueError('invalid port') from exc
    if port is None:
        raise ValueError('explicit port required')
    # Use numeric IPv4 loopback to avoid DNS rebinding and ambiguous localhost resolution.
    return f'http://127.0.0.1:{port}'

def run_local_inference(*, prompt: str, model: str, base_url: str,
                        backend: str = 'llama.cpp', approved: bool = False,
                        timeout_seconds: float = 60.0) -> LocalResult:
    if approved is not True:
        raise PermissionError('explicit local inference approval required')
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode('utf-8')) > MAX_PROMPT_BYTES:
        raise ValueError('prompt empty or too large')
    if not isinstance(model, str) or not model or len(model) > 128 or any(c in model for c in '\r\n'):
        raise ValueError('invalid model name')
    if backend not in ('llama.cpp', 'ollama'):
        raise ValueError('unsupported local backend')
    if not 0 < timeout_seconds <= 120:
        raise ValueError('timeout must be between 0 and 120 seconds')
    root = _endpoint(base_url)
    if backend == 'ollama':
        path = '/api/generate'
        payload = {'model': model, 'prompt': prompt, 'stream': False}
    else:
        path = '/v1/chat/completions'
        payload = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'stream': False}
    request = Request(root + path, data=json.dumps(payload).encode('utf-8'),
                      headers={'Content-Type': 'application/json'}, method='POST')
    opener = build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise LocalInferenceError('local model returned non-200 status')
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise LocalInferenceError(f'local model unavailable: {type(exc).__name__}') from exc
    if len(raw) > MAX_RESPONSE_BYTES:
        raise LocalInferenceError('model response exceeds size limit')
    try:
        data = json.loads(raw)
        text = data['response'] if backend == 'ollama' else data['choices'][0]['message']['content']
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise LocalInferenceError('invalid model response') from exc
    if not isinstance(text, str):
        raise LocalInferenceError('model response text is not a string')
    return LocalResult(provider=backend, model=model, text=text,
                       sha256=hashlib.sha256(text.encode('utf-8')).hexdigest())
