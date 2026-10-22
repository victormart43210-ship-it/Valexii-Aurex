# AUREX canonical ZIP download and verification workflow (XXV)

**State:** draft source change; no production authority or automated deployment.

## Cause and permanent fix

ChromeOS stored the staging diagnostic ZIP using renamed copies ending in -1.zip, -1 (1).zip and -1 (2).zip. The earlier script required the exact original filename and incorrectly concluded that the ZIP was absent. The correct archived bytes were already present in Linux files.

**Permanent fix:** locate new ZIPs by stable filename fragment and verify the *full archive SHA-256* before extracting. Never rely on an exact download filename or skip verification.

## Reusable command (replace version and hash for every new ZIP)

~~~bash
cd "$HOME/aurex-ox-24x7-clean-20261022_112606"
python3 tools/aurex_find_verified_zip.py \
  --fragment "AUREX_OX_XXV_STAGING_DIAGNOSTIC_v6_2" \
  --sha256 "841dd1f06fb49a645b3614cffd3e5f85aac795c247a3efbba21299d99b579e72" \
  --extract-to "$HOME"
~~~

The locator searches the Linux home directory and shared ChromeOS Downloads, including filenames with spaces and suffixes. It refuses mismatched SHA-256, unsafe archive paths, embedded symlinks, expansion bombs, and overwriting differing existing files. Repeating an identical extraction skips existing matching files. No Git, Railway, website, inference, or paid operations are performed.

A checksum verifies bytes, not artifact authorship; signed provenance is a separate future requirement.

## Reuse the successful read-only staging diagnostic

After verified extraction, run offline tests, then Railway staging checks. Do not print service tokens or access production.

~~~bash
KIT="$HOME/AUREX_OX_XXV_STAGING_DIAGNOSTIC_v6_2"
python3 -m unittest discover -s "$KIT/tests" -p 'test_*.py' -v

bash "$KIT/scripts/railway_cli.sh" run \
  --project 78095d3d-5911-41c8-aa3e-f9ebf5d81054 \
  --environment aurex-staging \
  --service aurex-api \
  python3 "$KIT/scripts/diagnose_staging.py" \
  --timeout 12 \
  --retries 1
~~~

Observed on October 22: anonymous GET health rejected (HTTP 401); all six authenticated GET endpoints returned HTTP 200 with valid responses on attempt 1 (health, capabilities, evidence, budgets, jobs, agent/status). The observed client response times for these six checks were 535, 610, 609, 521, 759 and 877 milliseconds. The script reported PASS for this **single read-only snapshot**, authority NONE, release HOLD.

**Not verified:** persistence after restart, sustained uptime, independent real-world accuracy and live NVIDIA inference. An earlier isolated timeout remains relevant for future reliability measurement.

## Canonical release gates

1. ZIP: publish SHA-256; discover by fragment, verify exact hash and extract safely.
2. Dry-run patch; exact Git SHA/branch; no files overwritten without explicit review.
3. Offline unit tests, then independent GitHub CI (lint, types, tests, Docker).
4. Staging-only deploy, pinned SHA and non-root boot; read-only authenticated endpoint probes.
5. Separate fictional-write SQLite persistence/restart tests before release.
6. Measure meaningful p95 latency, error rate and sustained availability, not 100 percent claims from zero traffic.
7. NVIDIA/Hermes spending and egress disabled until explicit user approval and independent safeguards.
8. No automatic production merge/deploy. Evidence → Qualification → Reality → Authority → Effect, no self-witness; unknown is HOLD.
