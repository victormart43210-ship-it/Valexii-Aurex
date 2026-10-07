# AUREX — HLE Readiness (experimental)

**Status: NOT RUN / NOT CERTIFIED.** This repository contains no HLE question/answer corpus or official HLE grading results.

## Purpose

`aurex.evals.hle_gate.assess_pair(manifest_path, outcomes_path)` checks *structural completeness* of externally graded baseline-vs-AUREX paired outcomes. It is not a benchmark runner, a grading service, or a claim of better performance. Manifest declarations are untrusted assertions until verified by an independent auditor.

## Admission sequence

1. Obtain lawful/authorized HLE access under the applicable benchmark terms. Pin an exact dataset revision; record full corpus checksum and stable item IDs without committing private questions or answers.
2. Freeze baseline and AUREX prompt templates, model identifiers/versions, inference parameters, tools, retries, timeouts, cost accounting and randomization in a hashed evaluation protocol.
3. Use paired items and fixed scoring rules. AUREX may challenge a candidate, but may not invent ground truth, certify its own score, see withheld references during generation, or grant authority.
4. Independent scoring must produce JSONL records with `item_id`, boolean `base_correct`, and boolean `governed_correct`. An independent reviewer must *verify*, not simply tick, manifest claims of authorized access, judge separation and contamination checks.
5. Validate all expected paired outcomes with `assess_pair`. Duplicates, missing outcomes, unresolved grades and scope mismatches must cause HOLD. Then separately audit scoring evidence, blind adjudication, trace provenance and statistical confidence before any external claim.
6. Publish both raw correct counts and paired improvements/regressions. Distinguish percentage-point delta from relative uplift; add uncertainty intervals and per-category analyses before any claim about superiority.

## Manifest shape (illustrative, not an attestation)

```json
{
  "dataset_sha256": "<64 hexadecimal characters>",
  "dataset_revision": "<immutable authorized revision>",
  "item_ids": ["example-id-1"],
  "baseline_model": "<frozen base model/settings>",
  "aurex_model": "<frozen governed model/settings>",
  "judge_id": "<independent scorer identity>",
  "judge_independent": true,
  "contamination_checked": true,
  "dataset_authorized": true,
  "evaluation_protocol_sha256": "<64 hexadecimal characters>"
}
```

**Current limitations:** field-level declarations can be falsified, hashes are not signed, the scorer is not integrated, response size and schema need further hardening, and no HLE dataset or score is present. For these reasons this gate returns `PAIRED_COUNTS_VALIDATED_NOT_HLE_CERTIFIED` even on structurally complete inputs. No passing HLE status is implied.

## Independent audit blockers

- Verify immutable, authenticated benchmark provenance and independent scoring.
- Fix provider endpoint/redirect, SSRF, credential-scope, and bounded-response risks.
- Execute packaging installation, pytest, Ruff, mypy and CI on the exact PR SHA.
- Check model family overlap, leaked references, duplicate items and non-independent evaluation.
