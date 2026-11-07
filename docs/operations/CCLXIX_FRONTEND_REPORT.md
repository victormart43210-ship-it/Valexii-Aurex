# CCLXIX frontend report

Code SHA `44b30cb68269e4a36e7edac3a4773b5b095ae7ef`.

The DISPATER console now has four authorized actions beyond the existing audit:

- Read stored history. The list shows time, status, run id, and receipt prefix. Opening a row loads that stored report.
- Download verified export. The file comes from the API export. A `FAIL` authenticity result is rejected before download.
- Record ZAYLEE observation. The browser sends only the receipt digest. The server sets the effect to `NONE`.
- A newer request id ignores an older response, so a slow audit cannot overwrite a later CSV admission or history read.

Errors use `role="alert"`. The new controls use a 44px minimum height and stack on a narrow screen.

Commands:

- `npx vitest run` in `website`: 167 passed.
- `npx tsc --noEmit`: pass.
- `npm run build`: pass. The DISPATER client chunk is 25.67 kB, gzip 7.87 kB. The main client chunk is 362.44 kB, gzip 113.62 kB.

Headless Chrome at 390 by 844 pixels, at 5:28 PM CT, completed a synthetic audit, read the stored history, and recorded a ZAYLEE observation. Confirmed recovery stayed $0.00. The service token was not in the page text. This was the same session, not an independent witness. No WCAG conformance audit was performed.

XAELI remains an honest unavailable or scripted page. Fleet maintenance has no backend and was not given a fake screen.
