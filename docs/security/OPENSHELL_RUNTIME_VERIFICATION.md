# NVIDIA OpenShell Security & Runtime Containment Report

**Operation**: KUSANAGI CLXXII — PROJECT IRON CONVERGENCE
**Agent**: Jules
**Date**: October 25, 2026
**Status**: Isolated Security Contract Verified / Host Supervisor Runtime NOT RUN

---

## 1. Executive Summary

NVIDIA OpenShell provides kernel-level sandbox isolation, supervisor mediation, and formal policy verification for autonomous AI agents. In Operation KUSANAGI CLXXII, we integrated OpenShell's policy preflight evaluation engine into AUREX-OX (`aurex/openshell_policy.py`) to enforce default-deny egress filtering, path-traversal prevention, and filesystem access rules without weakening existing Railway staging container security.

Because the current execution environment does not run the native external OpenShell supervisor daemon (`openshell-supervisor`), runtime supervisor containment is recorded as **NOT RUN**.

---

## 2. Policy Security Architecture

### A. Egress Network Policy
- **Default-Deny Policy**: All outbound connections are blocked unless explicitly match an HTTPS allowlist rule with port 443.
- **Header & Credential Scrubbing**: Requests containing raw user credentials or non-HTTPS schemes are rejected with `invalid_destination`.
- **Method Restriction**: Egress decisions enforce exact HTTP method allowlisting (`GET`, `POST`).

### B. Filesystem Isolation Rules
- **Path Prefix Allowlisting**: File reads and writes are restricted to explicitly permitted directories (e.g. `/app/aurex`, `/tmp/sandbox`).
- **Path Traversal Protection**: Any path containing relative traversal patterns (`..`) is rejected fail-closed with `path_traversal_attempt`.

---

## 3. Adversarial Security Verification Results

| Test ID | Security Boundary | Target Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| ADV-01 | Network Containment | Outbound POST to unauthorized host | Blocked (default_deny) | Blocked | PASS |
| ADV-02 | Network Containment | Outbound HTTP request | Blocked (invalid_destination) | Blocked | PASS |
| ADV-03 | Credential Protection | Secret token handling | Fail-closed len check | Validated | PASS |
| ADV-04 | Filesystem Isolation | Read `/etc/shadow` via traversal (`..`) | Blocked (path_traversal) | Blocked | PASS |
| ADV-05 | Filesystem Isolation | Read `/root/.ssh/id_rsa` | Blocked (default_deny_fs) | Blocked | PASS |
| ADV-06 | Tenant Isolation | Cross-tenant data retrieval | Tenant fields distinct | Isolated | PASS |
| ADV-07 | Prompt-Injection | Raw instruction injection | Authority stays NONE | Authority NONE | PASS |
| ADV-08 | Policy Modification | Mutate frozen policy rule | AttributeError raised | Protected | PASS |
| ADV-09 | Evidence Integrity | Audit digest tampering | Detected as CONFLICTING | Detected | PASS |
| ADV-10 | Failure Recovery | Worker process termination | Lease cancelled safely | Recovered | PASS |

---

## 4. Governance & Non-Self-Witnessing Authority

NVIDIA OpenShell serves exclusively as an execution-security layer. Per AUREX Core Governing Rules:
- OpenShell does NOT grant release, financial, or regulatory authority.
- `MODEL OUTPUT AUTHORITY = NONE`.
- `PRODUCTION RELEASE = HOLD`.
- System pipeline remains: **Evidence → Qualification → Reality → Authority → Effect**.
