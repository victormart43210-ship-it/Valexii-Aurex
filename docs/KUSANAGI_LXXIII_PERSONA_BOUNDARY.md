# KUSANAGI LXXIII — CUSTOS Persona Boundary: offline diagnostics and challenge schema

**Status: DRAFT / HOLD.** This work was based on current canonical main SHA
`df0654390049118a142ec3b3356f0f40b4789fe4`. It does not merge other
agent branches, contact model providers, download weights, train, deploy, publish,
grant authority, or access real user conversations.

## Threat model and trust boundaries

A generated answer, retrieved document or tool output may impersonate a named
persona, owner, developer, or independent reviewer. Claims such as "I am Ghost",
"I am Leviathan", "Verified by CUSTOS" or generated JSON setting
`authority_granted=true` are untrusted text, NOT authentication, evidence
admission, signature verification or effect authorization.

1. `aurex/evals/persona_boundary.py` adds a bounded, offline, deterministic
   lexical diagnostic for untrusted turns. It returns SHA-256 digests (not
   signatures), fixed non-authoritative source labels, optional lexical flags,
   and a review suggestion. It does not retain raw text in the result or
   execute commands.
2. `aurex/protocol/models.py` hardens the existing `ChallengeResult` schema:
   `extra='forbid'` rejects fabricated control fields, and
   `revalidate_instances='always'` prevents previously constructed or
   mutated instances from skipping validation. The existing `AurexEngine`
   continues to reject authority grants, unrecognized evidence IDs and
   unsupported empty evidence citations.
3. `tests/test_persona_boundary.py` and
   `tests/test_persona_authority_attacks.py` are deterministic,
   synthetic, zero-network fixtures covering roleplay, forged system and owner
   claims, fabricated CUSTOS endorsements, repeated identity assertions,
   oversized inputs, spoofed record types, and challenger result manipulation.

**Critical distinction:** the lexical recognizer is NOT an enforcement
boundary and makes NO claim to prevent prompt injection, identify actual
threats, detect all attacks, authenticate signatures, or observe latent
assistant/persona activation directions. A benign roleplay about Leviathan
must not be blocked merely because of that name. A prompt injection that
avoids the patterns may produce no flags. The lack of flags is never evidence
of safety. Do not wire these flags directly to a production effect gate.

## Research attribution vs engineering proof

Anthropic's *Assistant Axis* and *Persona Selection Model* provide research
motivation for examining identity drift and representation. This module is
**NOT** their activation-steering implementation or a replication. It examines
only text markers in supplied offline fixtures.

- Research explanation: https://www.anthropic.com/research/assistant-axis
- Persona discussion: https://alignment.anthropic.com/2026/psm/

`activation_measurement='NOT MEASURED'` is mandatory. No
percent improvement or measured reduction in harmful outputs is established.

## Qwen/activation compatibility matrix (repository-observed only)

- A pinned **training configuration** exists for
  `Qwen/Qwen2.5-0.5B-Instruct` at revision
  `7ae557604adf67be50417f59c2c2f167def9a775`. Its existence
  does not prove installation, training, model identity or execution.
- The repository has loopback Ollama/llama.cpp and HTTPS-compatible adapters,
  but none proves an available Qwen3-32B runtime or internal activation access.
- No model weights, activation hooks, Qwen3-32B inference, intervention
  experiments, reward models, GPUs or paid APIs were run.
- Activation steering compatibility: **NOT VERIFIED**.
- Live behavioral intervention efficacy: **NOT RUN**.

## Verification performed / still required

An isolated local source mirror on Python 3.13.5 ran targeted
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` tests: **48 passed**,
using exact Git blob contents for the submitted persona module and challenge
schema. This is **targeted local source validation**, not the repository's full
Python 3.12 CI, independent external replication or staging verification.
Use actual exact SHA, GitHub workflow links and updated counts in PR after
publication; do not infer successful CI from local execution.

GitHub Actions issue #58 reports runner allocation failures before steps start.
Owner can use the **draft** local offline verification procedure in PR #62
only as diagnostic evidence (do not merge #62 to bypass CI). Required Ruff,
strict Mypy, full Pytest, Docker checks and CUSTOS independent review must be
observed at the final SHA before release. Do not auto merge/deploy.

## Future gated work

If an installed compatible model is later verified, evaluate a separate
controlled study with a preregistered dataset, independent judges, clear false
positive/negative denominators, measured latency/cost, leakage controls, and
separate owner approval for any activation-level intervention. Keep authority
outside the model in every condition.

**Authority invariant:** Evidence → Qualification → Reality → Authority →
Effect; text style/identity/activation measurements have no return edge into
execution permission. **Current release: HOLD**.
