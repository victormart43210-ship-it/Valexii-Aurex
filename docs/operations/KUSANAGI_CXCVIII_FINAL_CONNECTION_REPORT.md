# CXCVIII — final connection checkpoint

Outcome: Qwen authentication configuration corrected; AUREX staging deployment blocked by tool approval control. No live inference or website success claimed.

Reviewed deploy SHA: d2e55319f3261f51b2239350e44952e96b7db074, PR156. Predeployment recovery commit33db59db6c1938dca7e6cb3c3b37b7efcd6cf193 remotely verified. No application source changed this operation. Prior independent source/mock review remains limited to that code; no new live reviewer certification.

Applied only to Qwen staging: LLAMA_API_KEY references existing AUREX staging model credential via Railway. No secret value was retrieved or displayed. Deployment2e8a0944-592b-4e7f-a53f-73b04de12a39 SUCCESS, model loaded on IPv6; no-key warning absent. Request-level valid/invalid/missing authentication tests are NOT VERIFIED.

Pending patch89057db4-9bb5-4390-be04-f63ffdd687b0 contains exactly seven changes: staging-only PR156 branch/exact SHA, legacy root/Dockerfile, staging-only volume mount removal preserving data, and two nonsecret bridge variables. Production retains its original source, deployment and /data attachment. No new service, volume or resource allocation.

Attempted railway_accept_deploy(environment98c103eb-a1af-46b6-948e-19c80e4d720d). Result: Cancelled — the user did not approve this action. No changes were made. Error INVALID_ARGUMENT. No alternate deployment route attempted. Pending patch remains STAGED.

Smallest next action: approve this exact staging patch, inspect it again for concurrent changes, apply it, then verify deployed SHA/health and production unchanged. Do not merge main. Model ID remains unset until runtime discovery.

Railway documents that pre-deploy commands can access the private network and service variables. An approved bounded diagnostic command can test missing/invalid/valid Qwen authentication and retrieve /v1/models without exposing secrets; it must not use uncontrolled prompts or read a database. Existing OAuth connector withholds secret values and has no container-exec tool, so it cannot directly perform the authenticated HTTP request in the present environment. Do not expose Qwen publicly as a workaround.

Gates: A PASS reviewed source; B NOT VERIFIED authentication requests; C NOT VERIFIED actual model ID; D NOT VERIFIED service-to-service reachability (IPv6 listener observed); E BLOCKED pending staging data-mount removal; F BLOCKED approval; G BLOCKED no live inference; H BLOCKED live validation; I BLOCKED website; J BLOCKED DISPATER explanation; K PASS prior exact-source dedicated tests38; L PASS prior backend487/2skip and exact-head CI4workflows (not a new local rerun); M NOT VERIFIED live independent review; N PASS production metadata unchanged; O PASS no paid-provider calls; P PASS release HOLD.

Rollback: preserve Qwen supported auth setting. Pending staging patch has not changed AUREX runtime. If subsequently deployed, restore prior legacy root/main585023a09fdbff5ec2349a67cc50ef45a9b6f9fd and disable probe if needed; do not remount unverified data automatically. No deletion occurred.
