"""OPA is advisory qualification only. Missing/error/denial => HOLD."""
import json
from dataclasses import dataclass
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class PolicyResult:
    disposition: str
    reason: str


def evaluate_policy(payload, *, endpoint="http://127.0.0.1:8181/v1/data/aurex/allow", timeout=1.0, opener=urlopen):
    if not endpoint.startswith("http://127.0.0.1:") and not endpoint.startswith("http://localhost:"):
        return PolicyResult("HOLD", "non_loopback_opa_endpoint_not_approved")
    if not isinstance(payload, dict):
        return PolicyResult("HOLD", "invalid_input")
    try:
        body = json.dumps({"input": payload}, allow_nan=False).encode("utf-8")
        if len(body) > 16384:
            return PolicyResult("HOLD", "input_too_large")
        req = Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with opener(req, timeout=timeout) as response:
            if response.status != 200:
                return PolicyResult("HOLD", "opa_http_error")
            raw = response.read(16385)
        if len(raw) > 16384:
            return PolicyResult("HOLD", "opa_response_too_large")
        parsed = json.loads(raw)
        if parsed.get("result") is True:
            return PolicyResult("QUALIFIED", "opa_allow_not_execution_authority")
        return PolicyResult("HOLD", "opa_deny_or_undefined")
    except (Exception):
        return PolicyResult("HOLD", "opa_unavailable_or_invalid")
