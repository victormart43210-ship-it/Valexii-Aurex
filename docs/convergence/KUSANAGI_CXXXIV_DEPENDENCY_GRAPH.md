# KUSANAGI CXXXIV — Dependency and Divergence Checkpoint

**Status: partial graph; all integration remains HOLD.** Snapshot is against `main` SHA `df0654390049118a142ec3b3356f0f40b4789fe4`.

## Observed ancestry and PR bases

```text
main (df0654390049118a142ec3b3356f0f40b4789fe4)
├── PR #97 (f44571a463ea46cd00c25bb1f672dd5fe6e9e382) [base: main]
└── PR #117 (82d70c0da20ba5128c48c254987cb433ddae6b35) [base: main]
    └── PR #118 (6adc1936d09534b134182e769f88fea9c5a0125a)
        ├── PR #119 (522807e0b9b9ff5ba6e996fb4a154c0fd8455ea6)
        └── PR #120 (3e7ce03d72031e048f0101e3484f176b56b542fa)
```

#119 and #120 both target the #118 branch, not `main`. Their branches are siblings at the observed #118 SHA. #119 has exact-head lint and test failures; #120 has passing observed check runs but lacks independent review. The implementation/content overlap must be established from source and behavior before consolidating either.

PR #97 and the #117–#120 chain independently target or descend from `main`; the observed GitHub metadata does not establish equivalence between these lines. #97's passing checks are not an independent review. No branch in this graph is approved for merge.

## Unknown edges

For the other 73 PRs, the live PR listing establishes branch/base references and heads, but this checkpoint does not claim full ancestry, code-equivalence, dependency, or conflict analysis. They remain `VERIFICATION_REQUIRED` in the [matrix](KUSANAGI_CXXXIV_78_PR_MATRIX.json). Filename overlap is not proof of supersession.

## Safe integration invariant

Use fresh `main` as the only integration base. After evidence and independent review, reconcile one capability at a time, run exact-head checks, and refresh `main` after each authorized merge. Do not use the divergent staging/convergence branches as a canonical production base. No deployment or schema migration is authorized.
