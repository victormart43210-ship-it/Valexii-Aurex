# AUREX Threat Model

## Assets protected

AUREX protects evaluation integrity, evidence provenance, challenge-result integrity, and the boundary between external witness output and product authority.

## Primary threats

1. Self-witnessing: a generator validates its own claim without an independent witness.
2. Evidence laundering: missing, stale, synthetic, or circular evidence is presented as verified.
3. Authority escalation: an advisory result is treated as permission for a security-sensitive effect.
4. Benchmark contamination: test items leak into prompts, training, tuning, or manual intervention.
5. Provider coupling: one vendor silently becomes both claimant and verifier.
6. Secret leakage: credentials or proprietary BCXMET internals enter public fixtures/logs.
7. Replay/staleness: historically valid evidence is reused as if it were current.

## Non-negotiable invariant

AUREX output is evidence, not authority. The public protocol defaults `authority_granted` to false, and the engine rejects any challenger result that attempts to set it true.

## Trust boundary

AUREX may be called by BCXMET, VALEXII tooling, CI, researchers, or model agents. The caller remains responsible for qualification and authority decisions.
