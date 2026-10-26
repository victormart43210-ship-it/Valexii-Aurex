"""Optional private synthetic interoperability check; never enabled in default CI."""
import os

import pytest

from aurex.integrations.onyx import OnyxAdapter, OnyxConfig, Principal, verify_candidate


@pytest.mark.skipif(os.getenv('AUREX_ONYX_LIVE_TEST') != '1', reason='Private Onyx live test not authorized/configured')
def test_private_synthetic_onyx_interoperability():
    # Require independent deployment admission; setting a flag is not that evidence.
    assert os.environ.get('AUREX_ONYX_ISOLATED_SYNTHETIC') == '1'
    assert os.environ.get('AUREX_ONYX_LOCAL_ONLY_INFERENCE') == '1'
    config = OnyxConfig(origin=os.environ['AUREX_ONYX_ORIGIN'],
        allowed_host=os.environ['AUREX_ONYX_ALLOWED_HOST'], token=os.environ['AUREX_ONYX_TOKEN'],
        tenant_id='synthetic-owner', principal_id='owner', source_hosts=frozenset({'records.example'}),
        enabled=True,isolated_owner_admitted=True,local_only_inference_admitted=True)
    result=OnyxAdapter(config).search('Find synthetic dispatch TOW-101',
        Principal('owner','synthetic-owner'),request_id='authorized-live-synthetic')
    assert result.status=='CANDIDATES', result.status
    assert all(verify_candidate(c) and c.qualification_state=='HOLD' for c in result.candidates)
    assert any('TOW-101' in c.content_excerpt for c in result.candidates)
