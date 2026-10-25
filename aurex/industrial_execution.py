"""Fixed fictional towing execution using the canonical fenced SQLite ledger.

Synchronous bounded worker, not a daemon. Hashes detect inconsistent records,
not hostile database-owner rewrites or independent financial truth.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

from aurex.database import DEFAULT_DB_PATH, create_job, get_db, get_job
from aurex.dispater_pilot import audit_synthetic, digest
from aurex.fenced_worker import claim_job, finalize_job
from aurex.governance_math.industrial_api import unique_object

router = APIRouter()
PARAMS = {'fixture': 'heavy_recovery_v1'}
PREFIX = '/v1/industrial/audit/towing'


def observation() -> dict[str, Any]:
    """Versioned server-owned fixture; amounts are exact cents/Decimal."""
    charges = [('heavy_recovery', 1, 250000), ('wrecker_service', 3, 30000),
               ('scene_support', 3, 15000)]
    source: dict[str, Any] = {
        'dataset_type': 'SYNTHETIC_ONLY', 'jobs': [], 'rates': [],
        'invoices': [], 'payments': [],
    }
    lines = []
    for code, quantity, unit_cents in charges:
        cents = quantity * unit_cents
        source['jobs'].append({'job_id': code, 'customer_id': 'FICTIONAL',
                               'service_code': code, 'date': '2026-10-25'})
        source['rates'].append({'rate_id': 'rate-' + code, 'customer_id': 'FICTIONAL',
                                'service_code': code, 'start': '2026-01-01',
                                'end': '2026-12-31', 'amount': str(Decimal(cents) / 100)})
        # Explicit zero-dollar fictional invoices let the existing engine calculate deltas.
        source['invoices'].append({'invoice_id': 'invoice-' + code, 'job_id': code,
                                   'amount': '0.00', 'status': 'open'})
        lines.append({'service': code, 'quantity': quantity,
                      'unit_amount_cents': unit_cents, 'expected_cents': cents})
    report = audit_synthetic(source)
    candidate = -sum((Decimal(f['difference_usd']) for f in report['findings']
                      if f['code'] == 'RATE_MISMATCH'), Decimal(0))
    return {'schema': 'aurex.synthetic.towing.v1', 'calculation_version': 'dispater-fixed-rate-v1',
            'fixture': PARAMS['fixture'], 'source': source, 'source_sha256': digest(source),
            'charges': lines, 'reconciliation': report, 'candidate_amount_cents': int(candidate * 100),
            'confirmed_revenue_cents': 0, 'synthetic': True,
            'review_actions': ['Verify dispatch, service evidence and rate approval with a human'],
            'authority': 'NONE', 'release': 'HOLD', 'review': 'NOT_REVIEWED'}


def _enabled() -> str:
    if (os.environ.get('AUREX_ENABLE_INDUSTRIAL_DEMO') != '1'
            or os.environ.get('AUREX_DEPLOYMENT_SCOPE') not in ('sandbox', 'staging')):
        raise HTTPException(503, 'NOT_VERIFIED: synthetic execution disabled')
    path = os.environ.get('AUREX_DB_PATH', DEFAULT_DB_PATH)
    # Read-only admission: never 'migrate' an unknown legacy database on request.
    if Path(path).is_file():
        try:
            conn = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
            try:
                tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                required = {
                    'jobs': {'id', 'kind', 'state', 'idempotency_key', 'params_json',
                             'reservation_usd', 'created_at', 'updated_at', 'result_json',
                             'lease_token', 'lease_expires_at', 'worker_id', 'request_id',
                             'trace_id', 'evidence_id', 'error_json'},
                    'evidence_records': {'id', 'capability_id', 'kind', 'collected_at',
                                         'sha256', 'summary', 'source_ref',
                                         'integrity_status', 'verification_status'},
                }
                if tables and any(name not in tables or not columns.issubset(
                        {r[1] for r in conn.execute('PRAGMA table_info(' + name + ')')})
                        for name, columns in required.items()):
                    raise sqlite3.DatabaseError('Incompatible schema')
            finally:
                conn.close()
        except sqlite3.Error:
            raise HTTPException(503, 'NOT_VERIFIED: explicit database migration required') from None
    return path


def _receipt(path: str, job_id: str) -> dict[str, Any]:
    if not re.fullmatch(r'cliv_[0-9a-f]{32}', job_id):
        raise HTTPException(422, 'Invalid synthetic job identifier')
    row = get_job(path, job_id)
    if row is None:
        raise HTTPException(404, 'Job not found')
    if row['state'] != 'succeeded':
        raise HTTPException(409, 'NOT_VERIFIED: job has no completed receipt')
    result = row.get('result', {})
    if not isinstance(result, dict):
        raise HTTPException(409, 'NOT_VERIFIED: receipt corruption')
    observed = result.get('observation')
    expected = observation()
    stored_canonical = json.dumps(observed, sort_keys=True, allow_nan=False)
    expected_canonical = json.dumps(expected, sort_keys=True, allow_nan=False)
    expected_digest = hashlib.sha256(stored_canonical.encode()).hexdigest()
    conn = get_db(path)
    try:
        evidence = conn.execute('SELECT * FROM evidence_records WHERE id=?', (row['evidence_id'],)).fetchone()
    finally:
        conn.close()
    if (row['kind'] != 'regression_scan' or row['params'] != PARAMS
            or stored_canonical != expected_canonical or not evidence or evidence['sha256'] != expected_digest
            or result.get('evidence_id') != row['evidence_id']
            or row['evidence_id'] != 'evidence_' + job_id
            or evidence['collected_at'] != row['updated_at']
            or evidence['capability_id'] != 'regression_scan'
            or evidence['kind'] != 'offline_probe'
            or evidence['integrity_status'] != 'RECORDED'
            or evidence['verification_status'] != 'UNVERIFIED'
            or row['lease_token'] is not None or row['lease_expires_at'] is not None):
        raise HTTPException(409, 'NOT_VERIFIED: receipt integrity mismatch')
    if datetime.fromisoformat(evidence['collected_at']).tzinfo is None:
        raise HTTPException(409, 'NOT_VERIFIED: receipt timestamp corruption')
    return {'job_id': job_id, 'state': row['state'], 'evidence_id': evidence['id'],
            'recorded_at': evidence['collected_at'], 'sha256': expected_digest,
            'observation_canonical': stored_canonical,
            'serialization': 'json.dumps(sort_keys=True), UTF-8', 'observation': observed,
            'integrity': 'CONSISTENT', 'verification': 'NOT_VERIFIED', 'review': 'NOT_REVIEWED',
            'authority': 'NONE', 'release': 'HOLD',
            'storage_limit': 'Mutable SQLite; digest consistency is not immutable storage or independent proof'}


@router.post(PREFIX)
async def execute(request: Request, response: Response) -> dict[str, Any]:
    path = _enabled()
    key = request.headers.get('idempotency-key', '')
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,80}', key):
        raise HTTPException(422, 'Bounded Idempotency-Key required')
    if request.headers.get('content-type', '').split(';')[0].strip() != 'application/json':
        raise HTTPException(415, 'application/json required')
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > 128:
            raise HTTPException(413, 'Fixed selector exceeds 128 bytes')
        raw.extend(chunk)
    try:
        data = json.loads(raw, object_pairs_hook=unique_object)
        if data != PARAMS:
            raise ValueError('Invalid selector')
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'Only server-owned synthetic fixture accepted') from None
    try:
        row = create_job(path, 'cliv_' + secrets.token_hex(16), 'regression_scan', PARAMS,
                         idempotency_key='cliv:' + key)
        job_id = row['id']
        if row['state'] not in ('succeeded', 'failed', 'cancelled'):
            lease = claim_job(path, job_id, 'cliv-sync', ttl_seconds=60)
            if lease is None:
                raise HTTPException(409, 'NOT_VERIFIED: worker owns job; retry same key')
            observed = observation()
            sha = hashlib.sha256(json.dumps(observed, sort_keys=True).encode()).hexdigest()
            finalize_job(path, job_id, 'cliv-sync', lease['lease_token'], lease['lease_generation'],
                         observed, sha, 'evidence_' + job_id)
        receipt = _receipt(path, job_id)
    except (sqlite3.Error, OSError):
        raise HTTPException(503, 'NOT_VERIFIED: evidence storage unavailable') from None
    except ValueError:
        raise HTTPException(409, 'NOT_VERIFIED: execution or integrity conflict') from None
    response.headers['Cache-Control'] = 'no-store'
    return receipt


@router.get(PREFIX + '/{job_id}/receipt')
def receipt(job_id: str, response: Response) -> dict[str, Any]:
    path = _enabled()
    try:
        result = _receipt(path, job_id)
    except (sqlite3.Error, OSError):
        raise HTTPException(503, 'NOT_VERIFIED: evidence storage unavailable') from None
    except (ValueError, TypeError):
        raise HTTPException(409, 'NOT_VERIFIED: receipt corruption') from None
    response.headers['Cache-Control'] = 'no-store'
    return result
