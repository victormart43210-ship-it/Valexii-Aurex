import json

import pytest

from training.common import verified_adapter
from training.prepare_dataset import sha


def test_adapter_modified_since_training_is_rejected(tmp_path):
    artifact = tmp_path / "adapter_model.safetensors"
    artifact.write_bytes(b"original")
    (tmp_path / "adapter_config.json").write_text("{}")
    record = {
        "config": {
            "base_model": "Qwen/Qwen2.5-0.5B-Instruct",
            "revision": "a" * 40,
            "max_steps": 2,
            "max_length": 128,
        },
        "artifact_sha256": {p.name: sha(p) for p in tmp_path.iterdir()},
    }
    (tmp_path / "training-record.json").write_text(json.dumps(record))
    assert verified_adapter(tmp_path) == record
    artifact.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        verified_adapter(tmp_path)


def test_adapter_manifest_cannot_escape_directory(tmp_path):
    (tmp_path / "training-record.json").write_text(
        json.dumps({"artifact_sha256": {"../outside": "0" * 64}})
    )
    with pytest.raises(ValueError):
        verified_adapter(tmp_path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_loss_cannot_establish_success(value):
    from training.common import require_finite_loss

    with pytest.raises(ValueError, match="non-finite"):
        require_finite_loss({"train_loss": value}, "train_loss")
