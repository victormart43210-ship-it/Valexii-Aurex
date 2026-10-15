import subprocess

from scripts.verify_release_integrity import verify_integrity


def test_integrity_gate_sha_mismatch_returns_hold() -> None:
    manifest = verify_integrity("0000000000000000000000000000000000000000")
    assert manifest["status"] == "HOLD"
    assert manifest["reason"] == "Target commit SHA does not match current HEAD SHA"


def test_integrity_gate_structure() -> None:
    res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    head_sha = res.stdout.strip()
    assert len(head_sha) == 40
