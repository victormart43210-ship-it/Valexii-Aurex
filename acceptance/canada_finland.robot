*** Settings ***
Documentation    Local synthetic acceptance only. Reuses canonical tests; never calls Railway or Lovable.
Library          Process
Library          OperatingSystem

*** Variables ***
${PYTHON}        python
${ROOT}          ${CURDIR}/..

*** Test Cases ***
Actual Worker Persists Receipt Across Restart
    Run Canonical Check    tests/test_cxxxii_staging_runtime.py::test_supervised_http_worker_persistence_and_child_failure

Receipt Corruption Is Rejected
    Run Canonical Check    tests/test_cxxxi_receipt_verify.py

Archive Export And Private Access Fail Closed
    Run Canonical Check    tests/test_canada_finland.py

*** Keywords ***
Run Canonical Check
    [Arguments]    ${test}
    ${result}=    Run Process    ${PYTHON}    -m    pytest    -q    ${test}
    ...    cwd=${ROOT}    timeout=90s    on_timeout=kill
    Should Be Equal As Integers    ${result.rc}    0    msg=${result.stdout}\n${result.stderr}
