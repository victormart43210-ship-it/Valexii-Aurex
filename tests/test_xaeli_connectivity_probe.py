import importlib.util
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "tools" / "verify_xaeli_private_qwen.py"
spec = importlib.util.spec_from_file_location("xaeli_probe", PATH)
assert spec and spec.loader
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_all_passes_are_the_only_verified_state():
    report = probe.assess({name: "pass" for name in probe.REQUIRED})
    assert report["state"] == "CONNECTED_VERIFIED"
    assert report["passed"] == report["required"] == 12


def test_current_contract_survives_a_store_outage_and_rejects_the_old_body():
    outage = json.dumps(
        {
            "detail": {
                "process": "PROCESS_HEALTHY",
                "readiness": "DEPENDENCY_UNAVAILABLE",
                "stores": {"aurex": "DEPENDENCY_UNAVAILABLE", "dispater": "DEPENDENCY_UNAVAILABLE"},
                "model": "CONFIGURED_UNVERIFIED",
            }
        }
    )
    assert probe.classify_health(503, outage) == "pass"
    assert probe.classify_health(200, '{"status":"ok","version":"0.1.0a1"}') == "fail"


def test_http_200_without_generated_text_is_not_inference_success():
    result = probe.classify_inference(
        200, '{"execution":"FAIL","generated_answer":null,"error_code":"MODEL_IDENTITY_MISMATCH"}'
    )
    assert result["invalid_model_identity_rejected"] == "pass"
    assert result["qwen_generated_text"] == "fail"
    assert result["synthetic_end_to_end"] == "blocked"
    empty = probe.classify_inference(200, '{"execution":"PASS","generated_answer":"  "}')
    assert empty["qwen_generated_text"] == "fail"


def test_static_website_bundle_does_not_count_as_a_displayed_answer():
    reaches, displays = probe.classify_website_bundle("static XAELI page")
    assert reaches == "blocked"
    assert displays == "fail"
    leaked, _shown = probe.classify_website_bundle("Authorization: Bearer secret")
    assert leaked == "fail"


def test_missing_live_inference_is_not_verified():
    report = probe.assess(
        {
            "railway_aurex_current_contract": "fail",
            "private_qwen_dns": "fail",
            "unauthorized_rejected": "pass",
        }
    )
    assert report["state"] == "PARTIALLY_CONNECTED"
    assert report["passed"] == 1
    assert report["checks"]["synthetic_end_to_end"] == "blocked"
    assert report["state"] != "CONNECTED_VERIFIED"
