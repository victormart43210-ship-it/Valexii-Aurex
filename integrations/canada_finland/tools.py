"""Offline synthetic preservation and private-access configuration; no network I/O."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import runpy
import shutil
from pathlib import Path
from typing import Any

from aurex.offline_probes import execute_probe

ROOT = Path(__file__).resolve().parents[2]


def export_bag(receipt: dict[str, Any], expected_job_id: str, destination: Path) -> Path:
    """Export only this source revision's fixed fictional receipt as BagIt 0.97.

    Caller supplies a trusted, private parent directory. No database is opened.
    A consistent imported receipt does not prove that a job actually executed.
    """
    verifier = runpy.run_path(str(ROOT / 'scripts/cxxxi_receipt_verify.py'))
    verifier['verify_receipt'](receipt, expected_job_id=expected_job_id)
    # Compare canonical bytes, not Python equality (False == 0), and reject NaN.
    expected = execute_probe({'probe': 'synthetic_field_audit_v1'})
    actual_bytes = json.dumps(receipt['observation'], sort_keys=True, allow_nan=False)
    if actual_bytes != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError('Only the exact current synthetic fixture is exportable')
    payload = (json.dumps(receipt, sort_keys=True, allow_nan=False) + '\n').encode()
    if len(payload) > 24_000:
        raise ValueError('Receipt exceeds bound')
    destination.mkdir(mode=0o700)  # exclusive: never overwrite existing paths/symlinks
    try:
        (destination / 'data').mkdir(mode=0o700)
        files = {
            'data/receipt.json': payload,
            'bagit.txt': b'BagIt-Version: 0.97\nTag-File-Character-Encoding: UTF-8\n',
            'bag-info.txt': (
                f'External-Identifier: {expected_job_id}\n'
                f'Payload-Oxum: {len(payload)}.1\n'
                'Source-Organization: AUREX synthetic demonstration\n'
                'Independent-Verification: NOT VERIFIED\n'
                'Financial-Authority: NONE\nProduction-Release: HOLD\n'
                'Persistence-Provenance: NOT VERIFIED BY EXPORTER\n'
            ).encode(),
            'manifest-sha256.txt': (
                hashlib.sha256(payload).hexdigest() + '  data/receipt.json\n'
            ).encode(),
        }
        files['tagmanifest-sha256.txt'] = ''.join(
            hashlib.sha256(files[name]).hexdigest() + '  ' + name + '\n'
            for name in ('bagit.txt', 'bag-info.txt', 'manifest-sha256.txt')
        ).encode()
        for name, content in files.items():
            path = destination / name
            with path.open('xb') as stream:
                path.chmod(0o600)
                stream.write(content)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return destination


def tailscale_policy(owner: str, host: str, port: int = 443) -> dict[str, Any]:
    """Render a dedicated staging tailnet policy, not an existing-policy merge.

    No enrollment, keys, routes, exit nodes, Tailscale SSH or configuration writes.
    Host identity and staging isolation must be checked separately before use.
    """
    if not re.fullmatch(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}', owner):
        raise ValueError('One explicit owner identity required')
    address = ipaddress.ip_address(host)
    if address not in ipaddress.ip_network('100.64.0.0/10'):
        raise ValueError('One Tailscale IPv4 host required')
    if type(port) is not int or port not in (443, 8443):
        raise ValueError('Only staging HTTPS ports 443 or 8443 allowed')
    return {
        'acls': [], 'ssh': [],
        'grants': [{'src': [owner], 'dst': [host], 'ip': [f'tcp:{port}']}],
        'tests': [{'src': owner, 'accept': [f'{host}:{port}'],
                   'deny': [f'{host}:{p}' for p in (22, 80, 443, 8443, 5432) if p != port]}],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    export = commands.add_parser('export')
    export.add_argument('--receipt', type=Path, required=True)
    export.add_argument('--job-id', required=True)
    export.add_argument('--destination', type=Path, required=True)
    policy = commands.add_parser('tailscale-policy')
    policy.add_argument('--owner', required=True)
    policy.add_argument('--host', required=True)
    policy.add_argument('--port', type=int, default=443)
    args = parser.parse_args()
    if args.command == 'export':
        if args.receipt.is_symlink() or not args.receipt.is_file():
            parser.error('A regular receipt file is required')
        with args.receipt.open('rb') as stream:
            content = stream.read(24_001)
        if len(content) > 24_000:
            parser.error('Receipt exceeds bound')
        export_bag(json.loads(content), args.job_id, args.destination)
        print('Exported synthetic BagIt package; ingest NOT VERIFIED; release HOLD')
    else:
        print(json.dumps(tailscale_policy(args.owner, args.host, args.port), indent=2))


if __name__ == '__main__':
    main()
