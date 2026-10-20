from unittest.mock import patch

from aurex.qwen_diagnostic import generate_qwen_workstation_report


def test_qwen_diagnostic_inactive_when_ports_closed() -> None:
    with patch("aurex.qwen_diagnostic.check_port", return_value=False):
        report = generate_qwen_workstation_report()
        assert report["status"] == "INACTIVE"
        assert report["model_serving_verified"] is False


def test_qwen_diagnostic_port_open_unverified() -> None:
    with patch("aurex.qwen_diagnostic.check_port", return_value=True), \
         patch("aurex.qwen_diagnostic.probe_model_serving", return_value=False):
        report = generate_qwen_workstation_report()
        assert report["status"] == "PORT_OPEN_UNVERIFIED"
        assert report["model_serving_verified"] is False


def test_qwen_diagnostic_ready_when_serving_verified() -> None:
    with patch("aurex.qwen_diagnostic.check_port", return_value=True), \
         patch("aurex.qwen_diagnostic.probe_model_serving", return_value=True):
        report = generate_qwen_workstation_report()
        assert report["status"] == "READY"
        assert report["model_serving_verified"] is True
