"""Owner-gated synthetic-only XAELI inference; no authority or effects."""
import hashlib
import os
from typing import Literal
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from aurex.adapters.base import GenerationSettings
from aurex.adapters.llama_cpp import LlamaCppAdapter
from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.qwen_rag import _reject_unsafe_model_output

router = APIRouter(prefix='/v1/xaeli-staging', tags=['xaeli-staging'])
MODEL = 'qwen2.5-0.5b-instruct-q4_k_m'

class SyntheticRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prompt: Literal[
        'Explain a synthetic app permission change.',
        'Explain a synthetic suspicious message.',
        'Explain a synthetic field ticket discrepancy.',
    ]

class SyntheticResponse(BaseModel):
    state: Literal['HOLD'] = 'HOLD'
    authority: Literal['NONE'] = 'NONE'
    independent_verification: Literal['NOT VERIFIED'] = 'NOT VERIFIED'
    mode: Literal['SYNTHETIC_DEMO_ONLY'] = 'SYNTHETIC_DEMO_ONLY'
    execution: Literal['PASS', 'FAIL']
    generated_answer: str | None
    input_sha256: str
    output_sha256: str | None
    error_code: str | None

@router.post('/explain', response_model=SyntheticResponse)
def explain_synthetic(req: SyntheticRequest, x_aurex_operator_approval: str | None = Header(default=None)) -> SyntheticResponse:
    # Must be mounted with Depends(authenticate) in api.py.
    if os.environ.get('AUREX_XAELI_STAGING_ENABLED') != '1':
        raise HTTPException(503, 'Staging disabled')
    if os.environ.get('AUREX_XAELI_OPERATOR_APPROVED') != '1' or x_aurex_operator_approval != 'synthetic-only':
        raise HTTPException(403, 'Operator approval required')
    if os.environ.get('AUREX_BUDGET_USD', '0') not in ('0', '0.0', '0.00'):
        raise HTTPException(503, 'Zero budget required')
    # Explicitly configured endpoint; default remains local loopback.
    # Railway-private HTTP still requires the shared server API key.
    adapter = LlamaCppAdapter(
        model=MODEL,
        base_url=os.environ.get('AUREX_QWEN_BASE_URL', 'http://127.0.0.1:8080/v1'),
        generation=GenerationSettings(max_tokens=64),
        timeout_seconds=90,
    )
    spec = ModelSpec(provider='llama.cpp', model=MODEL, revision='local-unverified', quantization='Q4_K_M', runtime='llama.cpp')
    prompt = 'Synthetic demo only. No real users, security verdicts, financial actions or authority. Explain uncertainty clearly. ' + req.prompt
    record = InferenceClient(adapter, spec).run(input_id='synthetic-'+hashlib.sha256(prompt.encode()).hexdigest()[:16], prompt=prompt)
    # Model output is unverified evidence, never authority.
    answer = record.output
    error_code = record.error_code
    execution = record.status

    if execution == 'PASS' and (
        not answer or not answer.strip() or _reject_unsafe_model_output(answer)
    ):
        answer = None
        execution = 'FAIL'
        error_code = 'UNSAFE_OR_EMPTY_MODEL_OUTPUT'

    return SyntheticResponse(
        execution=execution,
        generated_answer=answer[:4000] if answer else None,
        input_sha256=record.input_sha256,
        output_sha256=record.output_sha256,
        error_code=error_code,
    )
