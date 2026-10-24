"""Behavior gates for optional preservation/access integrations."""
import copy
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def integration():
    return importlib.import_module('integrations.canada_finland.tools')


@pytest.fixture
def receipt():
    return json.loads((ROOT / 'website/tests/cxxxii-receipt.json').read_text())


def test_archive_is_standard_bagit_and_contains_only_receipt(tmp_path, receipt):
    path = integration().export_bag(receipt, receipt['jobId'], tmp_path / 'bag')
    import bagit
    assert bagit.Bag(str(path)).validate()
    assert {p.name for p in (path / 'data').iterdir()} == {'receipt.json'}
    assert json.loads((path / 'data/receipt.json').read_text()) == receipt
    assert 'Financial-Authority: NONE' in (path / 'bag-info.txt').read_text()
    assert (path.stat().st_mode & 0o777) == 0o700
    assert ((path / 'data/receipt.json').stat().st_mode & 0o777) == 0o600


@pytest.mark.parametrize('mutation', ['digest', 'authority', 'job', 'cancelled', 'extra', 'count', 'bool', 'nan'])
def test_export_rejects_invalid_receipt_before_writing(tmp_path, receipt, mutation):
    changed = copy.deepcopy(receipt)
    if mutation == 'digest':
        changed['sha256'] = '0' * 64
    elif mutation == 'authority':
        changed['authority'] = 'APPROVED'
    elif mutation == 'job':
        changed['jobId'] = 'job-' + '0' * 24
    elif mutation == 'cancelled':
        changed['state'] = 'cancelled'
    else:
        observation = changed['observation']
        if mutation == 'extra':
            observation['customer_document'] = 'must never be exported'
        elif mutation == 'count':
            observation['finding_labels'] = 69
        elif mutation == 'bool':
            observation['false_positive_flags'] = False
        else:
            observation['false_positive_flags'] = float('nan')
        import hashlib
        changed['sha256'] = hashlib.sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()
    with pytest.raises(ValueError):
        integration().export_bag(changed, receipt['jobId'], tmp_path / 'bag')
    assert not (tmp_path / 'bag').exists()


def test_existing_destination_and_symlink_are_not_overwritten(tmp_path, receipt):
    destination = tmp_path / 'existing'
    destination.mkdir()
    (destination / 'keep').write_text('unchanged')
    with pytest.raises(FileExistsError):
        integration().export_bag(receipt, receipt['jobId'], destination)
    link = tmp_path / 'link'
    link.symlink_to(destination, target_is_directory=True)
    with pytest.raises(FileExistsError):
        integration().export_bag(receipt, receipt['jobId'], link)
    assert (destination / 'keep').read_text() == 'unchanged'


def test_tailscale_policy_is_narrow_and_denies_other_ports():
    policy = integration().tailscale_policy('owner@example.com', '100.64.0.10', 443)
    assert policy['grants'] == [{'src': ['owner@example.com'], 'dst': ['100.64.0.10'], 'ip': ['tcp:443']}]
    assert policy['acls'] == []
    assert policy['ssh'] == []
    assert policy['tests'][0]['accept'] == ['100.64.0.10:443']
    assert '100.64.0.10:22' in policy['tests'][0]['deny']
    assert '*' not in json.dumps(policy)


@pytest.mark.parametrize('owner,host,port', [('*','100.64.0.10',443), ('autogroup:member','100.64.0.10',443), ('owner@example.com','0.0.0.0/0',443), ('owner@example.com','127.0.0.1',443), ('owner@example.com','8.8.8.8',443), ('owner@example.com','100.64.0.10',22), ('owner@example.com','100.64.0.10',True)])
def test_tailscale_rejects_broad_or_unapproved_access(owner, host, port):
    with pytest.raises(ValueError):
        integration().tailscale_policy(owner, host, port)
