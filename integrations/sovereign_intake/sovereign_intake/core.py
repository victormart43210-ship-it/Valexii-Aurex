import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

MAX_FILE_BYTES = 20 * 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def acquire_local(path: Path, tenant_id: str, source_label: str) -> dict:
    """Offline reference ONLY. Caller must enforce quarantine and safe path policy."""
    if not tenant_id or not source_label:
        raise ValueError('tenant and source label required')
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular non-symlink file required')
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('size limit')
    with path.open('rb') as f:
        data = f.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ValueError('size limit')
    return {'tenant_id':tenant_id, 'source_label':source_label, 'sha256':sha256_bytes(data),
            'size_bytes':len(data), 'acquired_at':datetime.now(timezone.utc).isoformat(),
            'status':'QUARANTINED', 'authority':'NONE'}


def candidate_variance(left: dict, right: dict) -> dict:
    """No auto approval. Inputs are independently extracted assertions."""
    if left.get('tenant_id') != right.get('tenant_id'):
        raise ValueError('cross tenant comparison denied')
    if left.get('currency') != right.get('currency'):
        return {'status':'HOLD','reason':'currency mismatch','authority':'NONE'}
    try:
        from decimal import Decimal
        diff = Decimal(str(left['amount'])) - Decimal(str(right['amount']))
    except (KeyError, ValueError, ArithmeticError):
        return {'status':'HOLD','reason':'unusable amount','authority':'NONE'}
    return {'status':'REVIEW_REQUIRED' if diff else 'CANDIDATE_MATCH',
            'difference':str(diff),'authority':'NONE',
            'alternatives':['extraction error','duplicate','partial payment','credit memo','timing','revision']}


def canonical_receipt(payload: dict) -> dict:
    """Hash-only demonstration, NOT a digital signature or certified receipt."""
    body=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return {'payload':payload,'sha256':sha256_bytes(body),'signature_status':'NOT_SIGNED','authority':'NONE'}
