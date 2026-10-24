"""Bounded server-owned fictional audit; attached to the canonical authenticated app."""
from __future__ import annotations

import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

from aurex.governance_math.industrial_demo import build_demo

router = APIRouter()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


@router.post('/v1/industrial/audit/demo')
async def industrial_demo(request: Request, response: Response) -> dict[str, object]:
    if (os.environ.get('AUREX_ENABLE_INDUSTRIAL_DEMO') != '1'
            or os.environ.get('AUREX_DEPLOYMENT_SCOPE') not in ('sandbox', 'staging')):
        raise HTTPException(503, 'NOT_VERIFIED: synthetic sandbox not enabled')
    if request.headers.get('content-type', '').split(';')[0].strip() != 'application/json':
        raise HTTPException(415, 'Only application/json accepted')
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > 128:
            raise HTTPException(413, 'Synthetic selector exceeds 128 bytes')
        body.extend(chunk)
    try:
        data = json.loads(body, object_pairs_hook=unique_object)
        if (not isinstance(data, dict) or set(data) != {'fixture'}
                or data['fixture'] not in ('towing_v1', 'oilfield_v1')):
            raise ValueError('Only fixed synthetic selector accepted')
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'Invalid synthetic selector; customer data not accepted') from None
    try:
        result = build_demo(fixture=data['fixture'])
    except Exception:
        raise HTTPException(503, 'NOT_VERIFIED: classifier unavailable') from None
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return result
