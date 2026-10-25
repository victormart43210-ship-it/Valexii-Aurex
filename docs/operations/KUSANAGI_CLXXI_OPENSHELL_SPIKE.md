# KUSANAGI CLXXI — OpenShell integration spike

Status: **PROTOTYPE / NOT ENFORCED / PRODUCTION HOLD**

## Scope
Added a dependency-free, fail-closed **advisory preflight** policy evaluator and synthetic tests. This is not a deployment of NVIDIA OpenShell and is **not a security boundary**. No external agent or customer traffic has been routed through it.

## Why
NVIDIA OpenShell separates the Gateway, Supervisor, Sandbox, and Policy Prover. The supervisor enforces permissions outside the agent process. AUREX must retain CUSTOS authorization and Evidence → Qualification → Reality → Authority → Effect.

## Next integration gates
1. Inspect upstream OpenShell license, exact release/tag and security advisories.
2. Run OpenShell gateway and sandbox in isolated nonproduction infrastructure with explicit resource limits.
3. Configure default-deny filesystem, process and egress policies, broker credentials outside the sandbox, and pin permitted destinations.
4. Bind AUREX worker requests to authenticated per-job identity; never derive authority from model output.
5. Test network denial, credential non-disclosure, malicious redirects, DNS rebinding, cross-tenant isolation, supervisor fail-closed behavior and audit evidence.
6. Verify policy ceiling with upstream prover and independent adversarial review.
7. Produce reproducible logs and exact SHAs before considering staging; production stays HOLD.

## Limits
This preflight is not used for authorization and does not protect against DNS resolution changes, redirects, URL encoding ambiguities, process access, filesystem access, or bypass by an agent. Actual containment requires an externally enforced supervisor. No NVIDIA credentials are required or accessed.

Sources:
- https://www.nvidia.com/en-us/ai/openshell/
- https://github.com/NVIDIA/OpenShell
- https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale/
