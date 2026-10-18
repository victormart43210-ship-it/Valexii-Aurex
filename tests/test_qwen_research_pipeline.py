"""Offline XCV integration tests. Third-party OpusFilter runtime is stubbed here."""
from __future__ import annotations

import hashlib
import json
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from workstation import qwen_research_pipeline as xcv


def test_optional_opusfilter_missing_never_installs(monkeypatch):
    monkeypatch.setattr(xcv, "version", lambda _: "1.0.0")
    assert xcv.official_opusfilter_demo(executable="/bin/true")["status"] == (
        "OPUSFILTER_NOT_INSTALLED_OR_VERSION_MISMATCH"
    )


def test_pinned_opusfilter_synthetic_demo_compares_against_expected(monkeypatch):
    monkeypatch.setattr(xcv, "version", lambda _: "3.3.1")

    def fake_run(args, **kw):
        root = kw["cwd"]
        assert args[0] == "/usr/local/bin/opusfilter"
        assert args[1].endswith("/config.yaml")
        assert kw["timeout"] <= 60
        assert kw["stdin"] == subprocess.DEVNULL
        assert "https_proxy" not in {k.lower() for k in kw["env"]}
        (root / "source.filtered.txt").write_text(
            "Inspect a sample record\nTest the local service\n", encoding="utf-8"
        )
        (root / "target.filtered.txt").write_text(
            "Review the sample record\nValidate the local service\n", encoding="utf-8"
        )
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(xcv.subprocess, "run", fake_run)
    report = xcv.official_opusfilter_demo(executable="/usr/local/bin/opusfilter")
    assert report["status"] == "SYNTHETIC_OPUSFILTER_3_3_1_OBSERVED_UNVERIFIED"
    assert report["accepted_pairs"] == 2
    assert report["authority"] == "NONE"
    assert len(report["filtered_sha256"]) == 64


def test_external_filter_mismatch_holds(monkeypatch):
    monkeypatch.setattr(xcv, "version", lambda _: "3.3.1")

    def bad_runner(args, **kw):
        root = kw["cwd"]
        (root / "source.filtered.txt").write_text("wrong\n", encoding="utf-8")
        (root / "target.filtered.txt").write_text("wrong\n", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(xcv.subprocess, "run", bad_runner)
    assert xcv.official_opusfilter_demo(executable="/fake")["status"] == "OPUSFILTER_DEMO_HOLD"


def test_optional_filter_process_failure_sanitized(monkeypatch):
    monkeypatch.setattr(xcv, "version", lambda _: "3.3.1")

    def fails(*_, **__):
        raise subprocess.TimeoutExpired("private path", 60)

    monkeypatch.setattr(xcv.subprocess, "run", fails)
    r = xcv.official_opusfilter_demo(executable="/fake")
    assert r["status"] == "OPUSFILTER_DEMO_HOLD"
    assert "private path" not in json.dumps(r)


def test_qwen_requires_explicit_operator_approval():
    checker = Mock()
    runner = Mock()
    with pytest.raises(PermissionError):
        xcv.evaluate_local_qwen(
            backend="llama.cpp", model="qwen", port=8080, approved=False,
            checker=checker, runner=runner,
        )
    checker.assert_not_called()
    runner.assert_not_called()


def test_no_model_means_no_inference():
    runner = Mock()
    r = xcv.evaluate_local_qwen(
        backend="llama.cpp", model="missing", port=8080, approved=True,
        checker=lambda **_: {"status": "MODEL_NOT_LISTED"}, runner=runner,
    )
    assert r["status"] == "HOLD_MODEL_NOT_READY"
    runner.assert_not_called()


def test_approved_synthetic_qwen_plan_observed_no_output_disclosure():
    raw = '{"steps":["inspect","test","review"]}'
    expected = hashlib.sha256(raw.encode()).hexdigest()
    runner = Mock(return_value=SimpleNamespace(text=raw))
    r = xcv.evaluate_local_qwen(
        backend="llama.cpp", model="qwen-local", port=8080, approved=True,
        checker=lambda **_: {"status": "MODEL_ADVERTISED_UNVERIFIED"},
        runner=runner,
    )
    assert r["status"] == "LOCAL_SYNTHETIC_PLAN_OBSERVED_UNVERIFIED"
    assert r["plan_status"] == "STRUCTURE_MATCH_ONLY"
    assert r["response_sha256"] == expected
    assert r["authority"] == "NONE" and r["independent_verification"] == "NOT_VERIFIED"
    assert raw not in json.dumps(r) and "qwen-local" not in json.dumps(r)
    assert runner.call_args.kwargs["base_url"] == "http://127.0.0.1:8080"
    assert runner.call_args.kwargs["approved"] is True


def test_invalid_qwen_output_stays_hold():
    runner = Mock(return_value=SimpleNamespace(text='{"steps":["deploy","pay","announce"]}'))
    r = xcv.evaluate_local_qwen(
        backend="ollama", model="qwen", port=11434, approved=True,
        checker=lambda **_: {"status": "MODEL_ADVERTISED_UNVERIFIED"},
        runner=runner,
    )
    assert r["status"] == "HOLD_PLAN_REJECTED"
    assert r["plan_status"] == "HOLD"


def test_qwen_inference_failure_is_sanitized():
    runner = Mock(side_effect=RuntimeError("/home/secret-model.gguf token"))
    r = xcv.evaluate_local_qwen(
        backend="llama.cpp", model="qwen", port=8080, approved=True,
        checker=lambda **_: {"status": "MODEL_ADVERTISED_UNVERIFIED"},
        runner=runner,
    )
    assert r["status"] == "HOLD_LOCAL_INFERENCE_FAILED"
    assert "secret" not in json.dumps(r)


def test_default_cli_runs_only_synthetic_offline(capsys):
    assert xcv.main(["--check"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["kind"] == "SYNTHETIC_ONLY_NOT_MODEL_INFERENCE"


def test_real_inference_cli_requires_explicit_approval():
    with pytest.raises(SystemExit) as err:
        xcv.main(["--infer", "--model", "qwen"])
    assert err.value.code == 2
