# Implementation Plan: Neobrutalist Theme for the Homepage Dashboard

**Feature**: `specs/001-neobrutalist-theme` · **Branch artifacts**: this directory
**Date**: 2026-08-23

## Technical Context

| Aspect | Value (verified on this host) |
|---|---|
| App | gethomepage **v1.13.2**, container `homepage`, port 3000 |
| Stack | Next.js ^16.2.6, React ^19.2.5, **Tailwind CSS ^4.3** (`@tailwindcss/forms`, headlessui) |
| Config mount | `~/dev/06-apps-neo-brutalist-home/config` → `/app/config` (git-tracked) |
| Delivery mechanism | `config/custom.css` — official customization file, auto-injected by the app (satisfies spec FR-6/FR-7) |
| Services render | client-side; SSR HTML contains only the shell → selectors must be harvested from the shipped JS bundles |
| Skill | `neobrutalism-ui` (HyperUI tokens; assumes TW v4 — matches app exactly) |

## Constitution Check (vs `~/dev/AGENTS.md`)

- Single git root: ✓ all changes inside monorepo-tracked paths.
- No generated-runtime edits: ✓ `config/custom.css` is source-of-truth (mount), survives redeploys.
- Idempotency: ✓ static CSS file, no deploy steps beyond file presence.
- Real-runtime verification: ✓ every task ends with live-site evidence (curl + rendered-page check).

## Design Decisions

- **D1 — Canonical tokens** (from `neobrutalism-ui` skill): `border-2 black`,
  hard shadows `4px 4px 0 #000`, pressed hover `translate(2px,2px)+shadow:none`,
  accent `#fef08a` (yellow-200), bold uppercase headings, visible focus ring.
- **D2 — Plain CSS, no build step**: `custom.css` cannot rely on app-side
  `@apply`; implement tokens as hand-written CSS with custom properties
  mirroring the HyperUI values.
- **D3 — Selector strategy**: harvest the *actual* class names gethomepage
  ships (grep `/_next/static/chunks/*.js` for card/widget/status class
  strings), record them in `specs/001-neobrutalist-theme/selectors.md`, then
  write overrides keyed on those stable structural classes. Prefer adding
  box-shadow/border/background over resetting layout properties.
- **D4 — `!important` policy**: allowed sparingly where the app's own
  utilities win the cascade; every use gets a comment naming the overridden
  utility.
- **D5 — Dark mode**: best-effort via the app's dark-theme hook if
  discoverable in the same harvest; otherwise document limitation (spec
  allows light-first).
- **D6 — Status semantics**: never recolor status dots; only box treatment.

## Risks

- Selector drift on app upgrade → mitigated by recording the harvest +
  preferring broad structural selectors over exact utility chains.
- Cascade wars with TW v4 utilities → D4 policy keeps it debuggable.
- Client-only rendering means no server-side style proof → verify via
  preview pane render + screenshot instead of raw HTML greps.

## Testing / Validation

Evidence-based per house rule:

1. `curl -sk https://aldof.duckdns.org/ | grep -c custom.css` ≥ 1 (injection proof).
2. Rendered-page inspection through the desktop preview pane (correct Host,
   full hydration); screenshot + vision pass for borders/shadows/focus ring.
3. Durability: `docker compose up -d` recreate → reload → theme intact.
