# CCLVI frontend review

The CCLVI commits do not change `website/` or `dispater-web/`. The review rechecked the tree that Copilot integrated.

## Website

- Vitest: 23 files, 157 passed.
- `npx tsc --noEmit`: exit 0.
- `npm run build`: exit 0.
- `/dispater` still says the sample is synthetic, that identified exposure is not recovered revenue, and that the customer decides. No vendor is contacted.
- `/xaeli` still says it is not a connected assistant.
- `/bcxmet` remains presentation. It is not a security authority.
- Visual language was not redesigned. No second navigation was added.

## DISPATER-web

`npm test` in `dispater-web/`: 25 passed, 0 failed. The package is a separate surface from the `aurex` API. Its staging adapter fails closed when unconfigured.

## Not verified in a browser this turn

No new screen was added. The synthetic console banner was checked in CCLII and the component text is unchanged. A fresh browser pass was not repeated.

## Open

`confirmed_recovery_usd` in `website/src/lib/dispater-contract.ts` is `z.string()`. The server hardcodes `0.00`. The schema would accept another string if a future server sent one.
