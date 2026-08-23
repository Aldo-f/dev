# Feature Specification: Neobrutalist Theme for the Homepage Dashboard

**Feature Directory**: `specs/001-neobrutalist-theme`
**Date**: 2026-08-23
**Status**: Ready for planning

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cohesive neobrutalist look (Priority: P1)

Aldo opens `https://aldof.duckdns.org/` and sees the dashboard styled in the
neobrutalist aesthetic: every card, widget, and control has thick solid
borders, hard offset shadows (no blur, no gradients), flat high-contrast
colors, and bold uppercase headings. The page reads as one deliberate design,
not a mix of default and custom elements.

**Why**: The dashboard is a showpiece on a personal domain; stock styling looks
generic and Aldo explicitly wants the neobrutalist identity.

**Independent Test**: Load the live site; visually confirm 2px black borders +
hard offset shadows on service cards, info widgets, and bookmarks; confirm no
rounded soft-shadow remnants of the default theme on these elements.

### User Story 2 - Interactions keep tactile feedback (Priority: P2)

Hovering or focusing any interactive element (service cards, links, buttons,
search) gives pressed-style feedback: the element shifts toward its shadow and
the shadow collapses, keyboard focus shows a visible ring. Nothing becomes
invisible or unreadable in any state.

**Why**: Neobrutalism is defined as much by interaction feel as by static
look; feedback must survive mouse *and* keyboard use.

**Independent Test**: Tab through the page — every focusable element shows a
visible ring; hover a service card — it translates with shadow collapse;
nothing loses contrast.

### User Story 3 - Theme survives updates & redeploys (Priority: P3)

The custom styling lives entirely in the dashboard's supported customization
file inside the git-tracked config directory. Rebuilding the container, re-
running infrastructure playbooks, or upgrading the dashboard app does not
lose the theme.

**Why**: Previous infra work proved that untracked runtime edits evaporate;
the theme must be durable like the rest of the config.

**Independent Test**: `docker compose up -d` (recreate) followed by a fresh
page load still shows the themed UI; the file is present in git history.

### Edge Cases

- Dark mode: if the dashboard's dark palette is active, borders/shadows must
  flip color scheme so the style remains visible (light-on-dark), not vanish.
- Status colors: running/stopped indicators must stay distinguishable after
  restyling (green/red semantics preserved or enhanced).
- Long service names/descriptions: hard-bordered boxes must not clip text
  worse than the stock theme.
- Mobile/narrow viewport: cards stack single-column; borders/shadows remain
  intact, no horizontal scroll introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1**: All service cards render with thick solid borders and hard offset
  shadows (no blur) in the neobrutalist style.
- **FR-2**: Information widgets (CPU/memory/disk/temperature/uptime block)
  match the same border/shadow language as service cards.
- **FR-3**: Headings (group titles, section headers) render bold uppercase
  with strong visual weight.
- **FR-4**: Hover/focus states use the pressed treatment (translate toward
  shadow origin + shadow collapse) with a clearly visible focus ring for
  keyboard users.
- **FR-5**: Bookmark tiles follow the same style system.
- **FR-6**: The entire theme is delivered through the dashboard's official
  CSS-customization mechanism only — no forked images, no patched app files.
- **FR-7**: Styling survives container recreation, app upgrade, and
  playbook re-run without manual steps.
- **FR-8**: Dark mode remains usable: shadow/border colors adapt so the
  aesthetic stays visible against dark backgrounds.
- **FR-9**: Existing functionality (links, stats expansion, search) works
  unchanged after theming.
- **FR-10**: Status semantics (online/offline/degraded) remain visually
  distinguishable post-theme.

### Key Entities *(include if feature involves data)*

- **Theme stylesheet**: single customization file in the git-tracked config
  directory; loaded automatically by the dashboard at page render.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1**: Loading `aldof.duckdns.org` shows zero unstyled "stock" cards:
  100% of rendered service cards carry the bordered/shadowed treatment.
- **SC-2**: Keyboard-only navigation reaches all interactive elements with a
  visible indicator at every stop.
- **SC-3**: After `docker compose up -d` recreation + reload, the theme is
  still applied (zero manual re-steps).
- **SC-4**: Page remains responsive: no horizontal scrollbar at common
  widths (≥360px); layout intact at desktop width.
- **SC-5**: Contrast of body text vs. background meets WCAG AA in both
  light and dark modes.

## Assumptions

- The dashboard supports user CSS via a known config file (verified in the
  target deployment).
- The neobrutalism design language follows the HyperUI token set already
  codified in the team's internal skill: 2px black borders, hard offset
  shadows (`4px 4px 0`), yellow accent fills, uppercase bold headings.
- Light mode is the primary presentation; dark mode is best-effort within
  the app's existing dark class hooks.
- No upstream app code changes are in scope.

## Clarifications

*None required — design language, scope, and delivery mechanism were fixed
in conversation prior to specification.*
