import importlib.util
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
