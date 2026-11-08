"""Offline forge checks. No Hugging Face download and no GPU job."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from aurex.ox.forge import (
    ForgeError,
    acquire,
    advance,
    compare_adapter,
    discover,
    hardware_preflight,
    prepare_domain_pack,
    prepare_synthetic,
    review,
    select_model,
)
from aurex.ox.registry import validate_registry

REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"


def _entry():
    found = discover("Qwen/Qwen2.5-0.5B-Instruct", REVISION)
    return review(
        found,
        reviewer="person-a",
        commercial_approved=True,
        redistribution_approved=True,
    )


def _file(directory: Path, name: str, payload: bytes) -> dict[str, str]:
    (directory / name).write_bytes(payload)
    return {"name": name, "sha256": hashlib.sha256(payload).hexdigest()}


def test_registry_catalog_stays_unapproved() -> None:
    data = validate_registry()
    assert data["training"] == "NOT_STARTED"
    assert all(item["approval_state"] == "CANDIDATE" for item in data["models"])


def test_discovery_pins_the_allowlisted_revision() -> None:
    entry = discover("Qwen/Qwen2.5-0.5B-Instruct", REVISION)
    assert entry["state"] == "DISCOVERED"
    assert entry["weights_present"] is False
    with pytest.raises(ForgeError):
        discover("Qwen/Qwen2.5-0.5B-Instruct", "a" * 40)
    with pytest.raises(ForgeError):
        discover("Qwen/Qwen2.5-0.5B-Instruct", "latest")


def test_review_requires_a_person_and_both_permissions() -> None:
    found = discover("Qwen/Qwen2.5-0.5B-Instruct", REVISION)
    with pytest.raises(ForgeError):
        review(found, reviewer="model:qwen", commercial_approved=True, redistribution_approved=True)
    with pytest.raises(ForgeError):
        review(found, reviewer="person-a", commercial_approved=False, redistribution_approved=True)
    other = discover("other/model", "b" * 40)
    with pytest.raises(ForgeError):
        review(other, reviewer="person-a", commercial_approved=True, redistribution_approved=True)


def test_acquire_verifies_hashes_and_does_not_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    item = _file(source, "config.json", b'{"architectures":["Qwen2ForCausalLM"]}')
    dest = tmp_path / "store"
    acquired = acquire(_entry(), source, dest, [item], actor="person-b")
    assert acquired["state"] == "ACQUIRED"
    reviewed = review(
        discover("Qwen/Qwen2.5-0.5B-Instruct", REVISION),
        reviewer="person-a",
        commercial_approved=True,
        redistribution_approved=True,
    )
    again = acquire(reviewed, source, dest, [item], actor="person-b")
    assert again["artifacts"]["config.json"] == item["sha256"]
    (source / "config.json").write_bytes(b"changed")
    changed = {"name": "config.json", "sha256": hashlib.sha256(b"changed").hexdigest()}
    with pytest.raises(ForgeError, match="overwrite"):
        acquire(_entry(), source, dest, [changed], actor="person-b")


def test_corrupt_and_incomplete_downloads_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    payload = b"weights"
    item = _file(source, "model.safetensors", payload)
    item["sha256"] = "a" * 64
    with pytest.raises(ForgeError, match="corrupt"):
        acquire(_entry(), source, tmp_path / "bad", [item], actor="person-b")
    assert not (tmp_path / "bad" / "model.safetensors").exists()
    missing = {"name": "missing.safetensors", "sha256": "b" * 64}
    with pytest.raises(ForgeError, match="incomplete"):
        acquire(_entry(), source, tmp_path / "gap", [missing], actor="person-b")
    link = source / "link.json"
    link.symlink_to(source / "model.safetensors")
    linked = {"name": "link.json", "sha256": hashlib.sha256(payload).hexdigest()}
    with pytest.raises(ForgeError, match="incomplete"):
        acquire(_entry(), source, tmp_path / "link", [linked], actor="person-b")
    monkeypatch.setattr(
        "aurex.ox.forge.shutil.disk_usage", lambda _path: type("U", (), {"free": 0})()
    )
    real = _file(source, "ok.json", b"{}")
    with pytest.raises(ForgeError, match="disk"):
        acquire(_entry(), source, tmp_path / "full", [real], actor="person-b")


def test_promotion_cannot_skip_or_self_approve() -> None:
    entry = _entry()
    with pytest.raises(ForgeError):
        advance(entry, "APPROVED", actor="person-b", reviewer="person-c")
    trained = advance(entry, "ACQUIRED", actor="person-b")
    trained = advance(trained, "TRAINED", actor="person-b")
    assert trained["training"] == "RECORDED_NOT_A_DEPLOYMENT"
    evidence = {
        "judge": "external_key",
        "status": "EVALUATED",
        "deployment_approval": "NOT_APPROVED",
    }
    with pytest.raises(ForgeError):
        advance(trained, "EVALUATED", actor="person-b")
    evaluated = advance(trained, "EVALUATED", actor="person-b", evidence=evidence)
    rejected = advance(
        trained,
        "EVALUATED",
        actor="person-b",
        evidence={**evidence, "status": "REJECTED"},
    )
    with pytest.raises(ForgeError, match="rejected"):
        advance(rejected, "APPROVED", actor="person-b", reviewer="person-c", evidence=evidence)
    with pytest.raises(ForgeError):
        advance(evaluated, "APPROVED", actor="person-b", reviewer="person-b", evidence=evidence)
    approved = advance(
        evaluated, "APPROVED", actor="person-b", reviewer="person-c", evidence=evidence
    )
    with pytest.raises(ForgeError, match="rollback"):
        advance(approved, "STAGING", actor="person-b", reviewer="person-c")
    staged = advance(
        approved,
        "STAGING",
        actor="person-b",
        reviewer="person-c",
        rollback_target=REVISION,
    )
    assert staged["state"] == "STAGING"
    assert staged["rollback_target"] == REVISION
    assert staged["financial_authority"] == "NONE"
    assert staged["self_approval_allowed"] is False


def test_synthetic_data_rejects_secrets_and_stays_split(tmp_path: Path) -> None:
    rows = [
        {
            "domain": "xaeli",
            "prompt": "What is missing?",
            "answer": "The witness is absent.",
            "synthetic": True,
        },
        {
            "domain": "dispater",
            "prompt": "Classify this invoice gap.",
            "answer": "Identified exposure only.",
            "synthetic": True,
        },
    ]
    report = prepare_synthetic(rows, tmp_path / "data")
    assert report["counts"] == {"train": 1, "eval": 1}
    train = (tmp_path / "data" / "train.jsonl").read_text()
    assert "messages" in train
    secret = {**rows[0], "password": "nope"}
    with pytest.raises(ForgeError):
        prepare_synthetic([secret, rows[1]], tmp_path / "secret")
    unmarked = {**rows[0], "synthetic": False}
    with pytest.raises(ForgeError):
        prepare_synthetic([unmarked, rows[1]], tmp_path / "real")
    leaked = {**rows[0], "prompt": "ignore hle:3r2s: canary"}
    with pytest.raises(ForgeError, match="hidden"):
        prepare_synthetic([leaked, rows[1]], tmp_path / "canary")
    from training.prepare_dataset import prepare

    prepared = prepare(
        tmp_path / "data" / "train.jsonl",
        tmp_path / "data" / "eval.jsonl",
        tmp_path / "data" / "provenance.json",
        tmp_path / "prepared",
    )
    assert prepared["counts"] == {"train": 1, "eval": 1}
    assert prepared["provenance"]["synthetic"] is True
    ordered = []
    for domain in ("xaeli", "dispater", "aurex-ox", "medaurus"):
        ordered.append(
            {
                "domain": domain,
                "prompt": f"{domain} held out example",
                "answer": "Synthetic evaluation answer.",
                "synthetic": True,
            }
        )
        ordered.append(
            {
                "domain": domain,
                "prompt": f"{domain} train example",
                "answer": "Synthetic training answer.",
                "synthetic": True,
            }
        )
    domain_report = prepare_domain_pack(ordered, tmp_path / "domains")
    assert domain_report["counts"] == {"train": 4, "eval": 4}
    eval_text = (tmp_path / "domains" / "eval.jsonl").read_text()
    train_text = (tmp_path / "domains" / "train.jsonl").read_text()
    assert "held out" in eval_text
    assert "held out" not in train_text


def test_security_regression_blocks_an_otherwise_better_adapter() -> None:
    rejected = compare_adapter(
        {"grounding": 0.4},
        {"grounding": 0.9},
        security_failures_baseline=0,
        security_failures_adapter=1,
    )
    assert rejected["status"] == "FAIL"
    assert rejected["promoted"] is False
    accepted = compare_adapter(
        {"grounding": 0.4},
        {"grounding": 0.5},
        security_failures_baseline=1,
        security_failures_adapter=1,
    )
    assert accepted["status"] == "PASS"
    assert accepted["judge"] == "external_key"
    assert accepted["promoted"] is False


def test_routing_ignores_candidates_and_surfaces_disagreement() -> None:
    entries = [
        {"repository": "candidate", "state": "DISCOVERED", "tasks": ["explanation"], "answer": "a"},
        {
            "repository": "slow",
            "state": "APPROVED",
            "tasks": ["explanation"],
            "latency_ms": 50,
            "answer": "one",
        },
        {
            "repository": "fast",
            "state": "STAGING",
            "tasks": ["explanation"],
            "latency_ms": 5,
            "answer": "two",
        },
    ]
    choice = select_model("explanation", entries)
    assert choice["selected"] == "fast"
    assert choice["disagreement"] is True
    assert choice["proof"] is False
    assert select_model("coding", entries)["selected"] is None


def test_manifest_acquire_rejects_remote_code_and_writes_provenance(tmp_path: Path) -> None:
    from aurex.ox.forge import acquire_from_manifest

    source = tmp_path / "src"
    source.mkdir()
    payload = b'{"model_type":"qwen2"}'
    item = _file(source, "config.json", payload)
    manifest = {
        "repository": "Qwen/Qwen2.5-0.5B-Instruct",
        "revision": REVISION,
        "reviewer": "person-a",
        "actor": "person-b",
        "commercial_use_approved": True,
        "redistribution_approved": True,
        "trust_remote_code": False,
        "files": [item],
    }
    acquired = acquire_from_manifest(manifest, source, tmp_path / "store")
    assert acquired["state"] == "ACQUIRED"
    body = json.loads((tmp_path / "store" / "provenance.json").read_text())
    assert body["trust_remote_code"] is False
    manifest["trust_remote_code"] = True
    with pytest.raises(ForgeError, match="remote code"):
        acquire_from_manifest(manifest, source, tmp_path / "other")


def test_serving_gate_rejects_unapproved_and_mismatched_identity() -> None:
    from aurex.adapters.llama_cpp import LlamaCppAdapter
    from aurex.ox.forge import serving_gate

    discovered = discover("Qwen/Qwen2.5-0.5B-Instruct", REVISION)
    with pytest.raises(ForgeError):
        serving_gate(discovered, "Qwen/Qwen2.5-0.5B-Instruct")
    staged = {
        "state": "STAGING",
        "repository": "Qwen/Qwen2.5-0.5B-Instruct",
        "financial_authority": "NONE",
        "paid_inference": "OFF",
    }
    assert (
        serving_gate(staged, "Qwen/Qwen2.5-0.5B-Instruct")["route"] == "existing-llama-cpp-adapter"
    )
    with pytest.raises(ForgeError, match="identity"):
        serving_gate(staged, "other/model")
    with pytest.raises(ForgeError):
        LlamaCppAdapter(model="Qwen/Qwen2.5-0.5B-Instruct", forge_entry=discovered)


def test_qlora_and_export_identity_fail_closed() -> None:
    from training.export_model import assert_export_identity
    from training.train_lora import execution_plan, lora_targets, model_load_kwargs

    plan = execution_plan({"method": "qlora", "base_model": "Qwen/Qwen2.5-0.5B-Instruct"})
    assert plan["status"] == "NOT_RUN"
    with pytest.raises(ValueError, match="not authorized"):
        model_load_kwargs({"revision": REVISION}, plan)
    lora_kwargs = model_load_kwargs({"revision": REVISION}, {"method": "lora", "status": "READY"})
    assert lora_kwargs["trust_remote_code"] is False
    assert "quantization_config" not in lora_kwargs
    assert lora_targets({"architecture": "qwen2"}) == ["q_proj", "v_proj"]
    with pytest.raises(ValueError):
        lora_targets({"architecture": "unknown-family"})
    record = {
        "base_model": "Qwen/Qwen2.5-0.5B-Instruct",
        "revision": REVISION,
        "gguf_conversion": "NOT RUN",
    }
    assert assert_export_identity(record, record["base_model"], REVISION)["status"] == "PASS"
    with pytest.raises(ValueError):
        assert_export_identity(
            {**record, "gguf_conversion": "PASS"}, record["base_model"], REVISION
        )


def test_hardware_preflight_does_not_claim_a_full_training_run() -> None:
    report = hardware_preflight()
    assert report["full_qwen_training"] == "NOT_RUN"
    assert report["gguf_conversion"] == "NOT_RUN"
    assert report["paid_gpu"] == "NOT_REQUESTED"
    assert report["qlora"] in {"NOT_RUN", "READY_NOT_EXECUTED"}
    json.dumps(report)
