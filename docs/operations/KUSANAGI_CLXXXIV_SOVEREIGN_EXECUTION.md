# CLXXXIV current-state inventory

Main: 551625e5be41ef6fd16e70e7a72404400032f4bc, fetched 2026-10-26 UTC.

| PR | Current state | Exact head |
|---|---|---|
|145|Open, conflicts; Jules active source; not imported|f145187acce5bf61ba2a0cafcc7bbf95663dd2d6|
|146|Draft, mergeable, governed Onyx synthetic adapter|c1d6f3aeb9451c1c5d79dc0bae150512998a51e6|
|147|Draft, mergeable, website copy only|0693f0cb2d4c7e38977fd3d86e4bcf9ba6446510|
|149|Draft, mergeable, runner preparation|0b8b0b282ffa11ec814268a54647fd1769a42537|

Main has no root RECOVERY.json or RESUME.md. Other branches' histories are preserved. PR146 CP004 remote head was read back in GitHub; its CP005 continuation remains unfinished. Do not duplicate its Onyx adapter.

Confirmed gap: InferenceClient calls adapter.answer without a budget guard; CLI factory constructs client without one. BudgetGuard is Decimal-based but mutable, memory-only, with no concurrency/restart durability. A zero reservation is accepted. Do not change that shared contract blindly.

Owned files: inference policy, OpenAI-compatible transport, execution client, Ollama and CLI compatibility, focused tests and recovery docs. No parallel writers. Acceptance: no remote dispatch, even through direct adapter calls, while durable accounting is unavailable; local loopback behavior survives. No paid positive-path claim. Rollback is main base above; no infrastructure changes. Independent reviewer pending Jules.

PR145, runner, website/Railway, pricing and full DISPATER convergence remain unfinished. No claim of live interoperability, GPU capacity or deployed containment.
