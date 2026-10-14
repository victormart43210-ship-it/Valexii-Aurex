# Shared frontend contracts

The existing premium visual system is retained. This is an incremental frontend enhancement, not a claim of device protection or certified accessibility.

## Architecture and APIs

- `site.tsx`: PageShell, PageHero (`eyebrow`, `title`, `children`, optional `visual`) and backward-compatible SectionHeading use shared layout contracts across the public pages.
- `ui-system.tsx`: SectionHeader (`eyebrow`, `title`, optional `copy`, `action`, `id`); Card (`padding`, native article attributes); StatePanel (`title`, `children`, `action`, `tone`, `announce`, `headingLevel`); EmptyState and ErrorState share its accessible defaults.
- ActionButton extends the existing Button variants and native attributes with `busy` and `busyLabel`; label icon-only actions explicitly. Use a native disabled button during busy work; `asChild` is for navigation, not busy submissions.
- LoadingSkeleton exposes one loading announcement and bounded 1–6 decorative lines. Router pending presentation is delayed to avoid flashing on fast navigation.
- SectionIllustration retains responsive WebP, intrinsic dimensions, provenance captions and authored alt text; `loading` defaults to lazy, with eager available for a genuine first-screen illustration.
- Root and router defaults share missing/loading/error presentation. Retry invalidates before clearing the error boundary; raw exception messages never appear in public UI.

## Usage

```tsx
<SectionHeader eyebrow="RESEARCH" title="Evidence before conclusions" />
<Card padding="compact"><h3>Source record</h3><p>Authored fixture only.</p></Card>
<EmptyState title="UNKNOWN">No observations available; missing ≠ PASS.</EmptyState>
<ErrorState title="Unavailable" announce="polite" action={<ActionButton onClick={retry}>Try again</ActionButton>} />
<ActionButton busy={preparing} busyLabel="Preparing draft…">Compose draft</ActionButton>
```

## Practices

Use existing semantic color tokens and shared 44px minimum button targets. Keep text shrinkable with min-width zero; use bounded grid tracks for text plus fixed widgets. Do not mask page overflow to conceal defects. Keep status labels alongside colors. Announcements default off for static panels to avoid repeated screen-reader noise. Respect reduced motion. Do not add fake delays, data fetching or loading states to static content.

Phone fixtures and canonical demo timers remain unchanged. One content-sized bounded viewport owns phone scrolling, Radix controls keyboard navigation, and the outside collapsed drawer contains simulated events. Evidence → Qualification → Reality → Authority → Effect; no self-witness; UNKNOWN ≠ SAFE; ORB MOTION AUTHORITY = NONE.

No services, DNS, payments or research claims are activated by these UI primitives.