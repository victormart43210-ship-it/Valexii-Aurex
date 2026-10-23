# KUSANAGI CI — Orca + Archify + Visual Prompt Library + Hetzner

**Draft / human-reviewed installation only.** This bundle is an offline bootstrap and architecture policy. It does **not** install Orca, Archify, an image model, a GitLab runner, or authenticate to Hetzner on its own. It does not merge PRs or deploy to production.

## The four components and their correct roles

1. **Orca (stablyai/orca)**: A laptop desktop agent-development environment. Coordinate named tasks, keep isolated Git worktrees, inspect diffs, and connect via SSH *after* inspecting fingerprints. Use Codex/Claude/Cursor in the agents you already subscribe to, with controlled cost limits. One canonical GitHub repo: `victormart43210-ship-it/Valexii-Aurex`.
2. **Archify (tt-a1i/archify)**: Schema/layout-validated interactive architecture, flow, workflow, sequence, data-flow diagrams. Link diagrams to immutable commit SHA + source line receipts with our separate proof checker. **Archify's schema/layout pass is not proof of actual deployed runtime or app safety.**
3. **awesome-gpt-image-2 (freestylefly/awesome-gpt-image-2)**: A catalog of visual prompt styles and templates. Use it to draft BCXMET / AUREX concept imagery, never to change canonical evidence, security signals, release decisions, or the production orb's authority. Image generation requires a supported model, separate service and potentially billable API. Default off, $0 unapproved spend.
4. **Hetzner + existing GitLab Runner**: Separate read-only synthetic test jobs per exact PR SHA while GitHub Actions is blocked. This infrastructure is not proven online in our current session. No shell/privileged runner for unreviewed PR code; no production credentials, private PDFs or Docker socket in CI.

## On your laptop: 15-minute first pass

**Step A — Orca:** Obtain the correct platform build directly from https://www.onorca.dev/docs/install (Windows installer, macOS Apple Silicon/Intel, Linux .deb/.rpm/AppImage). Verify official publisher, not a social-video binary or mirror. Install and launch; choose an existing GitHub source checkout or create one safely with the supplied Python script below. Connect your coding-agent account within Orca; third-party subscriptions/quotas are separate.

**Step B — Python/Git:** Open your laptop's own terminal/PowerShell at this bundle's root. Inspect local Git, Python and Node without changing any account using:

```sh
python tools/orca/bootstrap_aurex.py --doctor
```

On Windows use `py -3 tools/orca/bootstrap_aurex.py --doctor` if `python` is not on PATH. If all checks look right, optionally create ONE new AUREX checkout in a directory you choose:

```sh
python tools/orca/bootstrap_aurex.py --clone --destination "AUREX_ORCA"
```

The clone operation uses `git clone` of the **fixed canonical URL**, fails if the folder already exists, does not auto-install repo dependencies or execute repository scripts, and does not switch branches or merge. If you already have a suitable working checkout, **do not clone again**; add your existing repo in Orca.

**Step C — Orca project:** In Orca choose **Add repository** → the local `AUREX_ORCA` folder or an existing AUREX checkout. Create separate *non-overlapping* worktrees (not separate backends): **CI/Hetzner runner repair**, **mainline security and PR convergence**, **APIS PRIME + Folio/finance tests**, **UX/diagram design**. Record base SHA and file ownership before each session. Parallelize only independent files; serialize merged changes one reviewed PR at a time. Do not add secrets to agent prompts.

**Step D — optional Orca agent skills (review before executing):** Orca's official documentation recommends:

```sh
npx skills add https://github.com/stablyai/orca --skill orca-cli --global
npx skills add https://github.com/stablyai/orca --skill orchestration --global
```

On Linux Orca CLI may be `orca-ide`. Agent skills can contain instructions/scripts and can modify your agent home; read upstream contents and the proposed install destination first. This bundle **does not execute those commands**.

**Step E — optional diagram and style skills (review before executing):**

```sh
npx skills add tt-a1i/archify -g
npx skills add freestylefly/awesome-gpt-image-2 --skill gpt-image-2-style-library --agent claude-code codex --global --copy
```

Install only into the agent(s) you actually use; syntax for the specific `skills` CLI version may vary. The pictured `tt-a1i` account contains a numeral **1**, not a lowercase L. For Archify, Node 18+ is required, and the skill can generate locally viewable HTML without needing paid AI image generation. Treat all generated HTML and external content as untrusted during review: use the offline export path; avoid public hosting of internal diagrams.

**Step F — Hetzner SSH:** In Orca **Settings → SSH → Add Target**; use your existing known `~/.ssh/config` identity/host entry. Test host connectivity and verify its **known_hosts fingerprint** with your Hetzner console before accepting a new or changed key. No passwords, bearer keys or root tokens in this chat or GitHub. Choose that SSH target when adding the project/worktree only *after* the repo is installed there. GitLab runner registration and Docker isolation must be reviewed separately. See `ci/hetzner/read_only_preflight.sh` and `docs/KUSANAGI_C_HETZNER_GITLAB_CI_BRIDGE.md` in draft AUREX PR #92.

**Step G — first Archify diagram and source evidence:**

> Use Archify to diagram the **observed source** of AUREX, not hypothetical finished architecture. Show: browser→authenticated proxy→API→durable worker/SQLite→source evidence→one private owner report, with each boundary clearly tagged as CODE / CI / DEPLOYED / E2E-NOT-VERIFIED. Separate **existing** features from **PR-staged** capabilities. Keep 8–12 primary nodes; link source references to an exact Git commit and line range. Do not mark an unverified system as live. Run Archify's schema/layout validation, then independently check `diagram_source_proof.py` receipts before sharing.

Store the generated diagram in a worktree's **review-only** `artifacts/diagrams/` folder and mark it `SOURCE_ONLY` until the exact source and drawing are externally examined. `diagram_source_proof.py` validates only commit/path/line existence and computes digests; it cannot validate product behavior or deployment identity.

**Step H — image/design references (concept art only):**

> Use the visual style library to propose **two restrained, premium near-black/navy, cyan/teal, metallic-gold concepts** for the BCXMET/AUREX *marketing hero background* or an explanatory technical illustration. Preserve accessible contrast, reduced motion, legible content, canonical names and the invariant **ORB MOTION AUTHORITY = NONE**. Output prompt templates first, **do not call an image API**, and never include passwords, private documents, tokens, internal proprietary source or unpublished invention claims.

The output is a *prompt*, not a generated image, a working frontend, or a deployed change. Any proposed Lovable edits remain separately budget/approval gated.

## Safe engineering assignment for Orca

Tell Orca's coordinator:

> Work ONLY on `victormart43210-ship-it/Valexii-Aurex`. First read `AGENTS.md`, `docs/KUSANAGI_LX_AGENT_KNOWLEDGE_PLAYBOOK.md` and `docs/AGENT_MAINLINE_POLICY.md`; fetch fresh protected `main` SHA. Preserve all 51+ open PRs as read-only candidate input, not automatic bulk merges. Assign 1 isolated worktree each to Hetzner runner diagnostics, security/provenance audit, APIS PRIME and Folio/finance convergence, and source-backed Archify diagrams. No file overlap. Orca coordinates; Hetzner/GitLab runs test suites against exact PR SHAs (after runner is confirmed online); Archify is visual communication only; the image prompt library is advisory, no model calls without opt-in. Produce a review table with PASS/FAIL/NOT RUN/NOT VERIFIED, independent witness, source SHA, CI artifacts, rollback. Stop at HOLD. No paid API, cloud deployment, customer ingestion, unsafe commands, or secret exposure. Merge one independently verified PR at a time only when policy requirements hold.

## First-step verification checklist

- [ ] Laptop OS and official Orca installer selected; app launched.
- [ ] Git and Python present; `--doctor` outputs observed versions.
- [ ] Orca project points to existing or new correct canonical repo.
- [ ] SSH runner connectivity/fingerprint personally verified and GitLab runner is online, non-privileged.
- [ ] GitLab exact-SHA job actually runs and produces independent test logs (not just 0-step failure).
- [ ] Archify installed in selected agent and sample diagram schema/layout checks pass.
- [ ] Diagram receipt checker confirms exact source SHA/path/line ranges and no secrets.
- [ ] Prompt-library installed only if desired; no paid image/model inference by default.
- [ ] Production release STILL HOLD until separate owner authorization and end-to-end proof.

**The system may never be its own sole witness.** Source diagram schema validation, source file SHA, test suite PASS, live deployments and finance authority are separate verification claims.