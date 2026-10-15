# Canonical inventory

| Component | Inspected source | Implementation / test evidence | Live status |
|---|---|---|---|
| Backend | `victormart43210-ship-it/Valexii-Aurex` main `f8df262ce39be2ba3b25046d94632e86179e15dd` | Local checkout, full tests; repair branch changes | NOT VERIFIED |
| Website candidate | `victormart43210-ship-it/Valexii-nexus` main `583495dfe33d44222a2d8327fe5efed6bf99f7eb` | Only LICENSE; only one branch returned | FAIL as website-source candidate |
| Actual website source | Lovable `811ffc43-2c8b-4c88-ab4c-4de668d089cb`, commit `8353b5e9ac32e6c5d983151acfabd02f29e46bd8` | TanStack Start/React 19/Vite; server functions; Supabase middleware; source inspected | Public /aurex observed, deployed SHA NOT VERIFIED |
| Server adapter | Same Lovable SHA, `src/lib/aurex-client.server.ts` | Existing owner-only diagnostics; contract mismatches reproduced; local patch | NOT VERIFIED |
| Authentication | Backend API; website auth middleware | Bearer comparison and owner guard exist; local backend rejection tests pass | Owner session/non-owner server execution NOT RUN |
| SQLite jobs | Backend `aurex/database.py` | Baseline unconstrained updates; repair enforces transaction and allowed transitions | Persistence on real host NOT VERIFIED |
| Ed25519 | Backend `aurex/experiments/admission.py` | Cryptographic primitive exists; trust not established in baseline; repair requires operator pin | Key custody/operational rotation NOT VERIFIED |
| Inference adapter | Backend `aurex/adapters/llama_cpp.py` | Loopback adapter exists; API does not invoke it | NOT VERIFIED |
| Native Qwen/gateway | No synchronized Phase 44/45 or port-8944 gateway located in inspected backend | Host not accessible | BLOCKED |
| Full bridge | No complete job-to-inference path recovered | No end-to-end real response | BLOCKED |

Accessible repository-name search returned seven repositories; no additional website-named upstream was located. This search is not proof that no inaccessible repository exists. Lovable source instructions describe synchronization in general, but provide neither the connected repository nor branch. Bidirectionality, tracked branch, uncommitted/unpublished edits, and website PR conflicts: NOT VERIFIED.

Evidence: `evidence/branch-inventory.json`, `evidence/pr-inventory.json`, GitHub branches/contents APIs, Lovable pinned source and edit metadata. Public site badge points to an opaque Lovable project identifier; it does not establish the GitHub mapping.
