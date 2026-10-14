# Internal QA test mode (internal-only, not linked from the site)

Purpose: keep the owner's QA/testing clicks out of the NEW custom conversion events. This is browser-local opt-in, not a secret, password or access control. No IP or geolocation is used.

## Enable / disable (in your own browser's DevTools console, on the site's domain)
```js
localStorage.setItem("valexii-internal-test", "on")   // enable
localStorage.removeItem("valexii-internal-test")      // disable
```
Set it separately per browser/device and per domain (valexii.com, www, lovable.app preview are different storage).

## Behaviour
- Test mode ON: custom events are never sent to any adapter; each is logged to the console as `[valexii internal-test] event excluded: {...}` so you can confirm it fired. Nothing leaves the browser.
- Test mode OFF: events are sent only if the visitor allowed optional measurement AND an adapter is configured. Currently no adapter is configured — public events are NOT MEASURED.
- Raw Lovable hosting analytics are unaffected and still count your visits. Past visitors cannot be retroactively identified or separated.

## Conversion events (only from UI that exists)
| Event | Trigger |
|---|---|
| quiz_start / quiz_finish | Scam quiz "Start quick quiz" / "Complete exercise" (educational, not a security result) |
| opt_in_request | Clicking the Weekly Research Dispatch mailto (opens draft; no opt-in confirmed) |
| support_cta_click | Clicking any Cash App link (click only; no payment is observed) |

Attribution attached (consent only, per tab session): coarse referrer class (direct/internal/search/social/other) and sanitized `utm_source`, `utm_medium`, `utm_campaign` (lowercase, ≤40 chars, long digit runs rejected). No URLs, IDs, emails or phone numbers.

## Verification checklist
- [ ] Enable flag, reload, open DevTools console.
- [ ] Start and complete the scam quiz on `/bcxmet` → see quiz_start, quiz_finish logs.
- [ ] On `/support` click a Cash App button → support_cta_click log (cancel the Cash App tab).
- [ ] Click "Request email opt-in" → opt_in_request log (do not send the draft).
- [ ] Disable flag, reload → no console logs; with no adapter, nothing is sent.
