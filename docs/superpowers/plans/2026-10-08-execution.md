# Amaterasu executable readiness plan

Goal: implement the user's October 8 execution specification on an isolated branch.
Architecture: retain existing model adapters and UER. Add immutable inference records,
reference-separated four-arm evaluation, and an optional Transformers/PEFT LoRA pipeline.
No model output grants authority. No HLE or paid GPU execution in this change.
Execution: sequential fallback explicitly authorized in the handoff; Astral preflight unavailable.

1. Reproduce canonical lint/type failures and UER unsigned-admission/provider-error defects.
   Repair typed exception boundaries; unsigned positive attestations remain NOT VERIFIED.
2. Add provider generation parameters, usage, identity-bound inference records, local
   llama-server support; test timeouts/malformed replies/secret-safe errors with local fixtures.
3. Add original-fixture generation then separate scoring commands for A/B/C/D, exact IDs,
   frozen denominators, abstentions/errors, paired discordance and deterministic checks.
   Missing C/D models remain NOT RUN; never manufacture them.
4. Add JSONL validation, duplicate/near-duplicate/contradiction and train/eval leakage gates,
   source hashes and provenance manifest. Add LoRA train/evaluate/merge-export commands.
   Reject GGUF as training input. Test fixtures, never claim access to Chromebook data.
5. Test adversarial governance, complete suite, package install and CLI smoke. Publish a
   dedicated draft PR and check its exact remote CI. Preserve independent-review HOLD.

Review focus: malformed provider output; missing and expired/revoked witnesses; hidden
reference leakage; train/eval near-duplicates; incomplete or duplicate evaluation rows.
