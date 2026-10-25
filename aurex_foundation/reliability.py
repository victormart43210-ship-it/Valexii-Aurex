"""Pure validation helpers, not a replacement for durable queue semantics."""
import hashlib
import json


def idempotency_fingerprint(operation: object, synthetic_payload: object) -> str:
    if not isinstance(operation, str) or not operation or len(operation) > 128:
        raise ValueError("invalid operation")
    canonical = json.dumps([operation, synthetic_payload], sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(canonical) > 16384:
        raise ValueError("payload too large")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def bounded_retry(attempt: int, max_attempts: int = 3) -> bool:
    if not isinstance(attempt, int) or isinstance(attempt, bool) or not 1 <= max_attempts <= 5:
        raise ValueError("invalid retry settings")
    return 1 <= attempt < max_attempts
