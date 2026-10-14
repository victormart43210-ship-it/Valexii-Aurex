# Release gates

**NOT READY FOR DEPLOYMENT. PRODUCTION DEPLOYMENT NOT AUTHORIZED.**

Required next sequence:
1. Independent security review of this backend diff, including attestation migration and fail-closed job behavior. Do not merge automatically.
2. Identify actual Lovable-linked GitHub repository/branch, verify current SHA, apply website patch in an isolated branch and run full build/tests; retain existing design.
3. Reconcile shared OpenAPI and identity/ownership contract; implement real bounded advisory worker, immutable job-scoped evidence and concurrent idempotency before exposing job creation.
4. Recover synchronized Linux gateway and exact model artifact; run local evidence script/commands with no public inference ports.
5. Establish explicitly authorized server-to-server connectivity, credentials and egress. Keep paid-provider defaults disabled.
6. Execute authenticated staging end-to-end and adversarial matrices. CONNECTED requires actual connectivity evidence appropriate to the promised capability.
7. Human approval for any merge or production deployment; none granted here.

No source merges, DNS changes, production deployments, new service activation, billing changes or tunnels were performed.
