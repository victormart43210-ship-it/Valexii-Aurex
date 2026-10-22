"""Opt-in, owner-only text answers from an allowlisted LLM API.

No tools, browsing, customer records, job execution, autonomous calls, or authority.
Public website must NEVER receive this API key. Railway/edge/website owner guards
are separately required. Configured != verified access to provider or model.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from urllib import error, request

# Pinned official OpenAI-compatible Chat Completions endpoints. Never accept
# provider endpoint URLs from user input or environment (SSRF/secret exfiltration).
ENDPOINT = 'https://api.openai.com/v1/chat/completions'  # backwards compat v2
NVIDIA_ENDPOINT = 'https://integrate.api.nvidia.com/v1/chat/completions'
MAX_REPLY_BYTES = 32768
MAX_QUESTION_CHARS = 1000
MODEL_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_./-]{0,79}$')
SYSTEM_PROMPT = (
    'You are XAELI, an informational assistant for VALEXII/AUREX. '
    'No tools, browsing, filesystem, payment actions, or customer data are available. '
    'Do not claim to have run audits, scanned devices, inspected records, '
    'performed independent verification, or taken actions. '
    'Model outputs are unverified suggestions, never evidence or authority. '
    'Never request or reveal credentials. State uncertainty; people make decisions.'
)

class AgentUnavailable(Exception):
    """A deliberately sanitized and non-sensitive HOLD condition."""

@dataclass(frozen=True)
class Provider:
    name: str
    url: str
    model: str
    api_key: str


def provider_name() -> str:
    p = os.environ.get('AUREX_LLM_PROVIDER', 'openai').lower()
    return {'nvidia': 'NVIDIA_NIM', 'openai': 'OPENAI'}.get(p, 'UNSUPPORTED')


def _provider_config() -> Provider | None:
    p = os.environ.get('AUREX_LLM_PROVIDER', 'openai').lower()
    if p == 'nvidia':
        cfg = Provider('NVIDIA_NIM', NVIDIA_ENDPOINT,
                       os.environ.get('AUREX_NVIDIA_MODEL', ''),
                       os.environ.get('AUREX_NVIDIA_API_KEY', ''))
    elif p == 'openai':
        cfg = Provider('OPENAI', ENDPOINT,
                       os.environ.get('AUREX_LLM_MODEL', ''),
                       os.environ.get('AUREX_LLM_API_KEY', ''))
    else:
        return None
    if len(cfg.api_key) < 20 or not MODEL_RE.fullmatch(cfg.model):
        return None
    return cfg


def configured() -> bool:
    """Configuration gate only. NEVER a connection/entitlement confirmation."""
    return (
        os.environ.get('AUREX_LLM_ENABLED') == 'true'
        and os.environ.get('AUREX_LLM_ALLOW_BILLING') == 'true'
        and _provider_config() is not None
    )


def status() -> dict[str, str | bool]:
    p = _provider_config()
    return {
        'provider': provider_name(),
        'model': p.model if p else 'NOT_CONFIGURED',
        'configured': configured(),
        'providerConnection': 'NOT_VERIFIED',
        'authority': 'NONE',
        'verification': 'NOT_VERIFIED',
    }


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def answer(question: str) -> dict[str, str]:
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= MAX_QUESTION_CHARS or '\x00' in question:
        raise ValueError('Question is empty or exceeds 1000 characters')
    if not configured():
        raise AgentUnavailable('Model disabled or unconfigured; HOLD')
    cfg = _provider_config()
    if cfg is None:
        raise AgentUnavailable('Invalid provider configuration; HOLD')

    payload = {
        'model': cfg.model,
        'stream': False,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': question},
        ],
    }
    # NVIDIA NIM API uses max_tokens; retain OpenAI's original request format.
    if cfg.name == 'NVIDIA_NIM':
        payload['max_tokens'] = 256
    else:
        payload['max_completion_tokens'] = 256
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = request.Request(cfg.url, data=body, method='POST', headers={
        'Authorization': 'Bearer ' + cfg.api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    opener = request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=12) as res:
            if res.status != 200:
                raise AgentUnavailable('Provider unavailable; HOLD')
            # Fast reject for truthful Content-Length, then enforce actual read cap.
            if int(res.headers.get('Content-Length') or '0') > MAX_REPLY_BYTES:
                raise AgentUnavailable('Provider response too large; HOLD')
            raw = res.read(MAX_REPLY_BYTES + 1)
            if len(raw) > MAX_REPLY_BYTES:
                raise AgentUnavailable('Provider response too large; HOLD')
    except (OSError, error.HTTPError, ValueError, OverflowError) as exc:
        # Never reflect third-party error bodies, headers or request secrets.
        raise AgentUnavailable('Provider unavailable; HOLD') from exc
    try:
        item = json.loads(raw.decode('utf-8'))
        choices = item['choices']
        content = choices[0]['message']['content']
        if not isinstance(content, str) or not content.strip():
            raise ValueError('Missing final content')
    except (KeyError, ValueError, IndexError, TypeError, UnicodeDecodeError) as exc:
        raise AgentUnavailable('Unexpected provider response; HOLD') from exc
    return {
        'reply': content[:1500],
        'model': cfg.model,
        'provider': cfg.name,
        'authority': 'NONE',
        'verification': 'NOT_VERIFIED',
    }
