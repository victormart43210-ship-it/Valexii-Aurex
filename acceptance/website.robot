*** Settings ***
Documentation    Manual admitted-staging owner UI check. Does not establish independent financial verification.
Library          OperatingSystem
Suite Setup      Open Admitted Owner Session
Suite Teardown   Run Keyword And Ignore Error    Close Browser

*** Variables ***
${SECTION}       section[aria-labelledby="financial-staging-title"]

*** Test Cases ***
Owner Can Retrieve A Persisted Fictional Audit
    Click    text="Financial Audit"
    Check Checkbox    ${SECTION} >> input[type="checkbox"]
    Click    ${SECTION} >> text="Submit fictional staging audit"
    Wait Until Keyword Succeeds    30x    2s    Read Completed Receipt
    ${job}=    Get Property    ${SECTION} >> input[placeholder="job-…"]    value
    Should Match Regexp    ${job}    ^job-[0-9a-f]{24}$
    ${digest}=    Get Text    ${SECTION} >> dt:has-text("SHA-256") + dd
    Should Match Regexp    ${digest}    ^[0-9a-f]{64}$
    Get Text    ${SECTION}    contains    Financial authority: NONE
    Get Text    ${SECTION}    contains    Production release: HOLD

*** Keywords ***
Open Admitted Owner Session
    ${admitted}=    Get Environment Variable    AUREX_BROWSER_STAGING_ADMITTED    0
    Should Be Equal    ${admitted}    1    msg=HOLD: verify staging isolation and backend admission before browser submission.
    ${session}=    Get Environment Variable    AUREX_OWNER_STORAGE_STATE
    File Should Exist    ${session}
    Import Library    Browser
    New Browser    chromium    headless=True
    New Context    storageState=${session}
    New Page    https://valexii.com/admin/sovereign-studio

Read Completed Receipt
    Click    ${SECTION} >> text="Read persisted job and receipt"
    Get Text    ${SECTION} >> [role="status"]    ==    STAGING_EXECUTION
