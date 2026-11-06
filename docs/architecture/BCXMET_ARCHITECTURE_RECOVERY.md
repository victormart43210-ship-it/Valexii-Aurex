# BCXMET architecture recovery — KUSANAGI CCXXV

Recovery date: 2026-11-05. Status: **PARTIAL; current GitLab source verification BLOCKED**. This inventory distinguishes inspected source from historical reports and design intent. No Android runtime tests or commercial validation were performed.

## Verified source identity

Authenticated GitHub metadata and commit reads identify `victormart43210-ship-it/CoreGuard-Android`, private, default branch `main`, at **f396d787e687d2e803d41955b09e613badfef7c2**, dated 2026-10-15, “AUREX Independent Verification Audit Report (#320)”. This is an accessible historical Android implementation, not proof of equivalence to GitLab BCXMET.

Original product remote recovered from the saved September convergence report: `https://gitlab.com/valexii-ai-medaurus-group/CoreGuard-Android`. Current read-only `git ls-remote ... HEAD` returned exit 128: `could not read Username for 'https://gitlab.com': No such device or address`. GitLab plugin discovery returned no available connector. Current branch ancestry, V42/V43 source and MRs E1–E5/F1–F5 are therefore **BLOCKED**, not assumed absent.

## Actual code inspected

All source anchors below are relative to `app/src/main/java/com/coldboar/coreguard/` at the exact GitHub commit above. They are source-level observations, not execution PASS results.

| Path | Implemented behavior | Transfer decision / limitation |
|---|---|---|
| `canary/EvidenceLedger.kt` | Deep snapshots; unique IDs; append-only hash linkage; exact correction references; wall/monotonic append times bound to hash | ADAPT immutable lineage concepts; REJECT direct storage reuse: this main implementation is memory-only, not durable or externally witnessed |
| `reasoning/EvidenceDependency.kt` | Case-relative dependency groups; explicit probe roots; UNKNOWN retained when provenance missing; family diversity alone does not establish independence | ADAPT root-dedup principle. Do not port first-parent-only derivation grouping or cybersecurity weighting into financial truth |
| `reasoning/claim/ClaimProof.kt` | Separate provenance, independence, sensor health, missing and counter-evidence; withheld proof requires null disposition; proof explicitly cannot authorize | ADAPT typed qualification/explanation separation |
| `reasoning/claim/ClaimRail.kt` | Presentation ALLOW/DEMOTE/REJECT based on a proof strength ceiling; no promotion or gate-disposition creation | ADAPT ceiling principle; fixed phrase blacklist is not a general financial verification boundary |
| `reasoning/SensorHealth.kt` | HEALTHY, DEGRADED, STALE, FAILED, UNAVAILABLE, SUSPECTED_TAMPER states | ADAPT explicit health. Do not copy permissive stale/degraded `blocksHealthyConclusion=false` semantics to verified financial outcomes |
| `ui/presentation/SecurityPresentationState.kt` | Explicit insufficient/degraded/stale states; CLEAR requires authority binding, usable observations and complete coverage | ADAPT presentation truth contract; no Compose transplant |

Source root: https://github.com/victormart43210-ship-it/CoreGuard-Android/tree/f396d787e687d2e803d41955b09e613badfef7c2

## Historical evidence inspected

The following saved documents were read in full through connected file access. Their claims remain historical and do not substitute for current source or raw test execution.

* `VALEXII_Complete_System_Architecture.pdf` (2026-09-15, `libfile_be565e2e35d481918689a37f070e1e50`): explicitly a design architecture with varying maturity; reusable constitution/evidence/containment core, separate cyber and industrial shells, advisory XAELI, and non-authoritative cross-domain transfer.
* `MEDAURUS_CONVERGENCE_REPORT_2026-09-23.md` (`libfile_50e5f3a6a3348191a2595287384543d6`): reports prior GitHub main `9d6354b5bd3766a949647ea73314762ea3a9d8e4`, Jules candidate `bb96415f4255172159e415eacbfccd3278df3e50`, and audit branch `0fc1a4c95a11ce697866810d43270fa246efb908`. It found failed-write publication, runtime durability wiring, missing freshness, transaction and migration verification gaps. These findings concern those older targets, not newly reproduced defects in current GitLab.
* `BCXMET-V42-R4-WORK-INDEPENDENT-AUDIT-2026-09-30.md` (`libfile_2f53fa6fefb081918c3d67c91d710249`): exact-source audit BLOCKED. Requested base `4f316f458659e13e7e52faef16cd72f7b914ddfc`, final `d936975d963f37f9d115800b210911fc988e55c8`, evidence `b60c93be5e6159e15e648915ebb348a10c5fcb48`; recovered older P0 tip `80ac0a6da8fd1db5c3500b449a41e69e621f7efd`. It records a screenshot pairing UNKNOWN with reassurance; the generating source was not verified. APK identity verification in that report does not prove source linkage.

V8/V9, V43, E1–E5 closure, F1–F5 implementation, Monument 19 and COMET DYNAMICS remain historical design/reference inputs where exact source was not obtained. This operation does not claim to have reused those implementations.

## Kernel constraints recovered

1. Provenance, independence, freshness, qualification and authorization are distinct fields; no single score can replace them.
2. Hash/signature validity authenticates recorded bytes, not source truth or independent origin.
3. Traverse all lineage parents; repeated exports from one root count once. Missing ancestors, cycles and contradictory versions cannot yield VERIFIED.
4. Durable publication follows successful transaction commit. Restart/cancel/lease fencing must prevent orphan workers from publishing a stronger result.
5. Stored historical results are not automatically current results. Freshness must be checked at the consumption boundary.
6. Explanations may narrow or withhold claims; they cannot grant action authority. Preserve UNKNOWN and missing evidence visibly.
7. Cross-domain transfer produces a stripped candidate; destination domain separately qualifies it.
8. Expected recovery, promised payment and reconciled cash are separate states. Independent deposit evidence is required for actual recovered revenue.

## License / provenance boundary

The inspected root `LICENSE` is **MIT**, copyright 2026 victormart43210-ship-it (blob `88516a6bfb38bf78f6da14adb7ae3a1c88aa92a3`). The current README instead says Apache 2.0. Record this conflict; do not claim clean whole-repository licensing. Any substantial code reuse needs the applicable notice and file/dependency provenance resolved. This operation adapts principles in existing Python infrastructure; no Kotlin source is copied. GitLab licensing is unverified.

## Failure lessons applied as verification requirements

The older convergence findings motivate failed-write rollback, interrupted worker/restart, missing lineage, stale-read and presentation-ceiling tests. They are test requirements rather than assertions that the same defects exist in AUREX. E/F labels in the owner's handoff are not treated as proof of source closure. Production HOLD and financial authority NONE remain unchanged.
