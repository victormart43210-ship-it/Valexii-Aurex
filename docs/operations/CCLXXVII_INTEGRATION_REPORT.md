# CCLXXVII integration report

Starting commit `dfcc17d516d354c830a7d9236cb66fde01c93302` on pull request 196. Canonical `main` remains `061b97022797013ccd1395a377b9489e59ba83f3`. Neither pull request 196 nor 193 was merged.

The DISPATER page already called reconciliation, document admission, stored runs, and export. It did not call the relationship or explanation routes. `Run golden ledger` now posts the committed synthetic fixture through `POST /v1/dispater/relationships`, reads the stored run back, reads the links, and reads `FND-UNBILLED_JOB-J02`. The page shows the API dollars. Equipment that is absent from the fixture stays `NOT IN SOURCE`. An unresolved endpoint stays `ENDPOINT_NOT_IN_SOURCE`.

Local Chrome on `http://127.0.0.1:5180/dispater`, about 9:02 PM CT, reached this status after the golden button: `LIVE DATA · API link: CONNECTED`. The figures were identified `385.00`, withheld `150.00`, and confirmed `0.00`. The explanation line showed suspected `100.00`, calculated none, and authority `NONE`.

`/xaeli` rendered `Model link: unavailable`. No model text was received. `qwen-private-staging.railway.internal` did not resolve.

Pytest: 784 passed, 1 skipped. Website Vitest: 168 passed, then the link test again after the loading-label fix. `npx tsc --noEmit` passed. `npx vite build` passed. Ruff passed on the touched Python files.

Seven of the eleven inventoried checks passed. Two display labels were not captured. Qwen is blocked. Restart recovery was not tested. That is not 100 percent coverage.

Production stays HOLD. Merge stays NONE. Independent review stays pending.
