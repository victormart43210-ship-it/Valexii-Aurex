import base64
import hashlib
import json
from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from aurex.adapters.base import ModelAdapter, ModelAnswer
from aurex.adapters.execution import InferenceClient, ModelSpec
from aurex.evals.four_arm import PromptItem, run_four_arms, score_run
from aurex.evals.governance import Claim, Witness, qualify
from aurex.provenance import fingerprint

NOW = datetime(2026, 10, 8, tzinfo=UTC)


def signed(**kw):
    key = Ed25519PrivateKey.generate()
    fields = {
        "witness_id": "w1",
        "source_id": "external",
        "context_sha256": fingerprint({"item_id": "q1", "prompt": "2+2"}),
        "claim_sha256": hashlib.sha256(b"4").hexdigest(),
        "outcome": "PASS",
        "observed_at": NOW - timedelta(seconds=1),
        "expires_at": NOW + timedelta(seconds=60),
        "revoked_at": None,
        "evidence_sha256": "a" * 64,
    }
    fields.update(kw)
    w = Witness(**fields, signature="")
    w = w.model_copy(update={"signature": base64.b64encode(key.sign(w.signing_bytes())).decode()})
    return w, {"external": key.public_key()}


@pytest.mark.parametrize(
    "case", ["missing", "stale", "revoked", "skip", "failed", "forged", "future"]
)
def test_bad_witness_never_passes(case):
    kw = {}
    if case == "stale":
        kw["expires_at"] = NOW
    if case == "revoked":
        kw["revoked_at"] = NOW
    if case == "skip":
        kw["outcome"] = "NOT RUN"
    if case == "failed":
        kw["outcome"] = "FAIL"
    if case == "future":
        kw["observed_at"] = NOW + timedelta(seconds=10)
    w, roots = signed(**kw)
    if case == "forged":
        w = w.model_copy(update={"signature": "invalid"})
    result = qualify(
        Claim(answer="4", status="PASS", evidence_ids=("w1",)),
        () if case == "missing" else (w,),
        roots,
        NOW,
        fingerprint({"item_id": "q1", "prompt": "2+2"}),
    )
    assert result.status != "PASS"


def test_verified_witness_and_conflict():
    w, roots = signed()
    claim = Claim(answer="4", status="PASS", evidence_ids=("w1",))
    assert (
        qualify(claim, (w,), roots, NOW, fingerprint({"item_id": "q1", "prompt": "2+2"})).status
        == "PASS"
    )
    other, roots2 = signed(witness_id="w2", source_id="second", outcome="FAIL")
    roots.update({"second": roots2["external"]})
    # signed source second must verify with the corresponding public key
    assert (
        qualify(
            claim, (w, other), roots, NOW, fingerprint({"item_id": "q1", "prompt": "2+2"})
        ).status
        != "PASS"
    )


class Echo(ModelAdapter):
    def answer(self, prompt):
        assert "reference-secret" not in prompt
        return ModelAnswer(
            provider="fixture",
            model="tiny",
            text=json.dumps({"answer": "4", "status": "PASS", "evidence_ids": ["w1"]}),
        )


def test_four_arm_missing_model_and_scoring():
    c = InferenceClient(Echo(), ModelSpec(provider="fixture", model="tiny", revision="v1"))
    w, roots = signed()
    run = run_four_arms([PromptItem(item_id="q1", prompt="2+2")], c, None, {"q1": (w,)}, roots, NOW)
    assert run["arms"]["C"]["status"] == "NOT RUN"
    report = score_run(run, {"q1": {"answer": "4", "status": "PASS"}})
    assert report["arms"]["A"]["accuracy"] == 1
    assert report["arms"]["B"]["accuracy"] == 1
    assert report["independent_review"] == "NOT VERIFIED"
    run["arms"]["A"]["rows"].append(run["arms"]["A"]["rows"][0])
    with pytest.raises(ValueError):
        score_run(run, {"q1": {"answer": "4", "status": "PASS"}})


def test_signed_witness_cannot_be_replayed_for_another_question():
    c = InferenceClient(Echo(), ModelSpec(provider="fixture", model="tiny", revision="v1"))
    w, roots = signed()
    run = run_four_arms(
        [PromptItem(item_id="different", prompt="2+3")], c, None, {"different": (w,)}, roots, NOW
    )
    assert run["arms"]["B"]["rows"][0]["decision"] == "HOLD"


@pytest.mark.parametrize("arms", [{}, {a: {"status": "NOT RUN", "rows": []} for a in "ABCD"}])
def test_missing_execution_cannot_score_pass(arms):
    body = {"item_ids": ["q"], "arms": arms}
    with pytest.raises(ValueError):
        score_run(
            {**body, "run_sha256": fingerprint(body)}, {"q": {"answer": "4", "status": "PASS"}}
        )


def test_conflicting_signed_answers_are_preserved_as_hold():
    w, roots = signed()
    other, keys = signed(
        witness_id="w2", source_id="second", claim_sha256=hashlib.sha256(b"5").hexdigest()
    )
    roots["second"] = keys["external"]
    result = qualify(
        Claim(answer="4", evidence_ids=("w1",)),
        (w, other),
        roots,
        NOW,
        fingerprint({"item_id": "q1", "prompt": "2+2"}),
    )
    assert result.status == "HOLD"
