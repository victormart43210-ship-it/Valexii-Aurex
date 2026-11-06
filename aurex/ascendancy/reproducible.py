"""M6. Canonical manifests for a computation.

The digest covers the supplied inputs and outputs. It does not sign a financial
receipt and it does not make this process an independent witness.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def computation_manifest(name: str, inputs: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    body = {
        "name": name,
        "inputs": inputs,
        "outputs": outputs,
        "financial_authority": "NONE",
        "production": "HOLD",
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return {**body, "manifest_sha256": hashlib.sha256(raw).hexdigest()}
