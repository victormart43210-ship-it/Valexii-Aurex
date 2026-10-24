# OPERATION KUSANAGI CLV — CUSTOS VERIFICATION REPORT

## Execution Matrix

| Gate | Required Result | Verified Result | Evidence / Notes |
|---|---|---|---|
| **Authentication CI repair** | PASS | **PASS** |  added to  |
| **Industrial audit tests** | PASS | **PASS** | 10 unit tests in  passing |
| **Full backend CI** | PASS | **PASS** | 453 passed, 1 skipped, 0 failed in ============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-8.4.2, pluggy-1.7.0
rootdir: /app
configfile: pyproject.toml
testpaths: tests, training/tests, workstation/tests
plugins: anyio-4.15.1
collected 453 items / 1 skipped

tests/test_adapter_security.py ........                                  [  1%]
tests/test_api.py ....                                                   [  2%]
tests/test_audit_pilot.py ..................                             [  6%]
tests/test_cxxv_contract_inventory.py ....                               [  7%]
tests/test_cxxxii_legacy_runtime_contract.py ....                        [  8%]
tests/test_docling_adapter.py .....                                      [  9%]
tests/test_engine.py ..                                                  [  9%]
tests/test_evals.py ..                                                   [ 10%]
tests/test_evaluation_worker.py ...                                      [ 11%]
tests/test_execution_readiness.py ....                                   [ 11%]
tests/test_execution_record.py ....                                      [ 12%]
tests/test_experiment_failures.py .                                      [ 13%]
tests/test_experiment_runner.py ....                                     [ 13%]
tests/test_fenced_worker_integrity.py .....                              [ 15%]
tests/test_field_assurance.py ................                           [ 18%]
tests/test_field_audit_beta_convergence.py ..                            [ 18%]
tests/test_field_audit_beta_gate.py .............                        [ 21%]
tests/test_field_audit_beta_pipeline.py ........                         [ 23%]
tests/test_folio_index.py ....................                           [ 28%]
tests/test_four_arm.py .............                                     [ 30%]
tests/test_global_research_assurance.py ........................         [ 36%]
tests/test_governance_math.py .............................              [ 42%]
tests/test_governed_inference.py .....                                   [ 43%]
tests/test_governed_remediation_planner.py .......................       [ 48%]
tests/test_hle_readiness.py .....                                        [ 49%]
tests/test_industrial_audit.py ............                              [ 52%]
tests/test_international_eval.py ....                                    [ 53%]
tests/test_kusanagi_repairs.py .....                                     [ 54%]
tests/test_kusanagi_workflow.py ........                                 [ 56%]
tests/test_kusanagi_xxiii_recovery.py ......                             [ 57%]
tests/test_llm_telemetry_contract.py ................                    [ 61%]
tests/test_local_inference.py ...........                                [ 63%]
tests/test_local_inference_redirects.py ..                               [ 64%]
tests/test_model_execution.py ......                                     [ 65%]
tests/test_nvidia_finance_offline.py ..............                      [ 68%]
tests/test_opa_policy.py .......                                         [ 69%]
tests/test_oss_witnesses.py ..........                                   [ 72%]
tests/test_protocol.py .                                                 [ 72%]
tests/test_provenance.py ..                                              [ 72%]
tests/test_railway_research_safety.py .........                          [ 74%]
tests/test_real_offline_probe.py .                                       [ 75%]
tests/test_reality_gate_persistence.py ...                               [ 75%]
tests/test_remediation.py .                                              [ 75%]
tests/test_report.py ..                                                  [ 76%]
tests/test_research_advice_api.py .......                                [ 77%]
tests/test_scoped_tracing.py ..                                          [ 78%]
tests/test_statistical_and_reports.py ....                               [ 79%]
tests/test_telemetry.py ....                                             [ 80%]
tests/test_training_innovation_plan.py .............                     [ 83%]
tests/test_uer_attacks.py ..............                                 [ 86%]
tests/test_web_adapter.py ..                                             [ 86%]
tests/test_wiring_preflight.py ....................                      [ 90%]
tests/test_workflow_budget.py .........                                  [ 92%]
tests/test_workflow_failure.py .                                         [ 93%]
tests/test_workflow_read_model.py ......                                 [ 94%]
tests/test_workflows.py .....                                            [ 95%]
training/tests/test_artifact_integrity.py .....                          [ 96%]
training/tests/test_prepare_dataset.py ......                            [ 98%]
workstation/tests/test_evidence_ledger.py ...                            [ 98%]
workstation/tests/test_hle_practice.py ..                                [ 99%]
workstation/tests/test_model_forge.py ....                               [100%]

=============================== warnings summary ===============================
../home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/jules/.pyenv/versions/3.12.13/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 453 passed, 1 skipped, 1 warning in 4.00s =================== |
| **Ruff** | PASS | **PASS** | All checks passed! clean |
| **Mypy** | PASS | **PASS** | Success: no issues found in 79 source files clean |
| **Tenant isolation** | PASS | **PASS** | Enforced in  |
| **Evidence integrity** | PASS | **PASS** | SHA-256 evidence digests computed deterministically |
| **Railway staging health** | PASS | **PASS** | Live Railway endpoint  returns 200 OK |
| **Staging version alignment** | PASS | **VERSION MISMATCH** | Railway runs ; new industrial audit routes return 404 until staging deploy |
| **Synthetic towing audit** | PASS | **PASS** | Executed in  |
| **Synthetic oilfield audit** | PASS | **PASS** | Executed in  |
| **XAELI integration** | PASS | **PASS** | 5-step XAELI findings (, , , , ) returned in  |
| **Website integration** | PASS | **PASS** | Tested server-side proxy in  |
| **Production authorization** | HOLD | **HOLD** | Strict -bash spending, no production deployment without owner consent |

## Verification Summary
All backend code changes, lints, strict type annotations, and unit tests have been independently executed and verified.
Railway staging is verified operational, and the industrial audit candidate is ready for authorized staging deployment.
