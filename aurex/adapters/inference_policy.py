"""Dispatch admission while durable remote accounting is unavailable.

There is deliberately no enable switch. BudgetGuard is memory-only; neither a
positive balance nor an environment flag can authorize a remote request.
"""

from urllib.parse import urlsplit


class RemoteInferenceDenied(RuntimeError):
    """Stable, credential-free denial suitable for execution records."""


def require_local_dispatch(base_url: str, *, local_requested: bool) -> None:
    try:
        url = urlsplit(base_url)
        admitted = (
            local_requested is True
            and url.scheme == "http"
            and url.hostname in ("127.0.0.1", "::1", "localhost")
            and not url.username
            and not url.password
            and not url.query
            and not url.fragment
            and not any(c.isspace() or ord(c) < 32 for c in base_url)
            and "\\" not in base_url
        )
    except (ValueError, TypeError):
        admitted = False
    if not admitted:
        raise RemoteInferenceDenied("REMOTE_INFERENCE_DISABLED")
