"""Zero-network tests for local Qwen readiness and human-gated inference."""
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from workstation.qwen_readiness import check_local_qwen, main, synthetic_smoke


class Reply:
    status = 200

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, _):
        return self.data


def opener(data=None, error=None):
    opened = Mock()
    if error:
        opened.open.side_effect = error
    else:
        opened.open.return_value = Reply(json.dumps(data).encode() if not isinstance(data, bytes) else data)
    return opened


def test_llama_check_only_counts_models_not_inference():
    o = opener({"data": [{"id": "qwen-local"}]})
    r = check_local_qwen(backend="llama.cpp", model="qwen-local", port=8080, opener=o)
    assert r["status"] == "MODEL_ADVERTISED_UNVERIFIED"
    assert r["models_listed"] == 1 and r["inference"] == "NOT_RUN"
    assert r["authority"] == "NONE" and r["external_spend_usd"] == 0
    assert "qwen-local" not in json.dumps(r)
    assert o.open.call_args.args[0].full_url == "http://127.0.0.1:8080/v1/models"


def test_ollama_check_does_not_download():
    o = opener({"models": [{"name": "qwen2.5:0.5b"}]})
    r = check_local_qwen(backend="ollama", model="qwen2.5:0.5b", port=11434, opener=o)
    assert r["status"] == "MODEL_ADVERTISED_UNVERIFIED"
    assert o.open.call_args.args[0].get_method() == "GET"


def test_model_not_listed_stays_unverified():
    r = check_local_qwen(backend="ollama", model="missing", port=11434,
                         opener=opener({"models": []}))
    assert r["status"] == "MODEL_NOT_LISTED"


def test_server_unavailable_is_not_pass():
    r = check_local_qwen(backend="llama.cpp", model="qwen", port=8080,
                         opener=opener(error=OSError("private diagnostic")))
    assert r["status"] == "SERVER_UNAVAILABLE"
    assert "private diagnostic" not in json.dumps(r)


@pytest.mark.parametrize("body", [b"not-json", b"\xff\xfe", b"x" * 65537,
                                   b'{"data":"bad"}', b'{"data":[{}]}'])
def test_invalid_or_oversized_body_holds(body):
    r = check_local_qwen(backend="llama.cpp", model="qwen", port=8080, opener=opener(body))
    assert r["status"] == "INVALID_MODEL_LIST"


@pytest.mark.parametrize("backend,model,port", [
    ("remote", "qwen", 8080), ("llama.cpp", "", 8080),
    ("llama.cpp", "name\nInjected", 8080), ("llama.cpp", "qwen", 0),
    ("ollama", "qwen", 65536), ("ollama", " qwen", 11434),
])
def test_invalid_settings_never_call_local_server(backend, model, port):
    o = Mock()
    with pytest.raises(ValueError):
        check_local_qwen(backend=backend, model=model, port=port, opener=o)
    o.open.assert_not_called()


def test_no_smoke_without_operator_approval():
    with pytest.raises(PermissionError):
        synthetic_smoke(backend="llama.cpp", model="qwen", port=8080, approved=False,
                        opener=Mock(), runner=Mock())


def test_no_smoke_if_model_not_listed():
    runner = Mock()
    out = synthetic_smoke(backend="llama.cpp", model="qwen", port=8080,
                          approved=True, opener=opener({"data": []}), runner=runner)
    assert out["status"] == "MODEL_NOT_LISTED"
    runner.assert_not_called()


def test_explicit_smoke_sanitizes_output_but_preserves_hash():
    response = "Private answer should not leave local process"
    h = hashlib.sha256(response.encode()).hexdigest()
    runner = Mock(return_value=SimpleNamespace(text=response, sha256=h))
    out = synthetic_smoke(backend="llama.cpp", model="qwen", port=8080,
                          approved=True, opener=opener({"data": [{"id": "qwen"}]}), runner=runner)
    assert out["status"] == "LOCAL_INFERENCE_OBSERVED_UNVERIFIED"
    assert out["inference"] == "OBSERVED_UNVERIFIED"
    assert out["answer_sha256"] == h
    assert response not in json.dumps(out)
    assert runner.call_args.kwargs["base_url"] == "http://127.0.0.1:8080"


def test_smoke_error_never_leaks():
    runner = Mock(side_effect=RuntimeError("my private GGUF path /secret"))
    out = synthetic_smoke(backend="ollama", model="qwen", port=11434,
                          approved=True, opener=opener({"models": [{"name": "qwen"}]}), runner=runner)
    assert out["status"] == "LOCAL_INFERENCE_FAILED"
    assert "/secret" not in json.dumps(out)


def test_infer_cli_requires_extra_approval():
    with pytest.raises(SystemExit) as ex:
        main(["--model", "qwen", "--infer"])
    assert ex.value.code == 2


def test_default_probe_cli_never_performs_inference(capsys):
    with patch("workstation.qwen_readiness.check_local_qwen") as p:
        p.return_value = {"status": "MODEL_NOT_LISTED"}
        assert main(["--model", "qwen", "--check"]) == 1
        assert "MODEL_NOT_LISTED" in capsys.readouterr().out
