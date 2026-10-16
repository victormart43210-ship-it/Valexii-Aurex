# PALIMPSEST — defensive IP hardening (proposal)

**Status: experimental / NOT VERIFIED.** This is a bounded defensive fixture generator, **not** a deployed anti-reverse-engineering control.

## Scope
- Keep authentication, execution authority, signing keys, evidence qualification, and proprietary model routing server-side.
- Review browser source maps, mobile build symbols, credentials, public API errors, dependencies, and licensing before release.
- Treat obfuscation as a speed bump, not a security boundary.
- Generate *inert* honeycode fixtures only in an isolated, disposable directory. Never ship them as authoritative components.
- Honeytokens must be fake and privilege-free. Collect only minimal telemetry with explicit retention and access controls.
- Never write or execute files on an investigator's device, induce loops, exhaust resources, or retaliate.
- Never classify reverse engineering alone as proof of malice.

## Voynich-inspired research metaphor
Opaque identifiers, multiple apparent structures, and context-dependent mappings can inspire **nonfunctional test fixtures**. This is not based on a verified Voynich decipherment. Do not use cryptic structure as a substitute for cryptography.

## Run (local only)
```bash
python tools/palimpsest_decoys.py /tmp/palimpsest-fixtures --count 4
```
Output directory must not exist. Maximum 16 files and 32 KiB. Generated modules are data-only and contain no imports, execution, or network operations.

## Required release gates
1. Independent review of client/server trust boundaries.
2. Secret scanning and source-map exposure audit.
3. Verify generated decoys cannot affect evidence, authority, billing, or job lifecycle.
4. Verify no new runtime dependencies or startup effects.
5. Prove authorized debugging and incident response remain possible.
6. Confirm legal/privacy review before honeytoken telemetry or public deployment.

**Release authority: HOLD.** No deployment or claim of reverse-engineering prevention without independent evidence.
