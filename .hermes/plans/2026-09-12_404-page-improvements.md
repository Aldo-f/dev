# 404 Page Improvement Proposals — `06-apps-aldo-f-github-io`

Goal: Make the "Pagina niet gevonden" page memorable, helpful, and on-brand for the documentation hub.

---

## Current State
- Static markdown (`docs/nl/404.md`) promoted via hook to `site/404.html` and `site/nl/404/index.html`.
- Asset URLs now absolute (`/assets/...`) — no more 404s on CSS/JS.
- Minimal content: title, short sentence, two links (home, projects).

---

## Proposal 1 — "Friendly Guide" (Low Effort, High Clarity)

**Concept**: Treat the 404 as a helpful concierge. Keep it light, add search, surface the most useful destinations.

### Content Changes
| Section | What to Add |
|---------|-------------|
| **Headline** | "🗺️ Waar ben ik? — De pagina bestaat niet (of is verhuisd)." |
| **Search Box** | Embed the existing MkDocs search (`<input data-md-component="search" …>`) so visitors can search immediately. |
| **Quick Links** | 4–5 cards with icons: **Home**, **Blog**, **Projects**, **Home-lab Docs**, **Zoeken**. |
| **Recent Posts** | Auto-injected list of 3 latest blog posts (reuse `related_posts` hook logic). |
| **Tone** | Friendly Dutch: "Geen paniek — dit komt voor. Probeer één van de opties hieronder." |

### Implementation
- Edit `docs/nl/404.md` (front-matter + markdown).
- Add a small `{% include "partials/404-quick-links.html" %}` partial in `overrides/` for the card grid.
- No JS required; search works via existing Material search index.

### Effort
~30 min. One commit, no new dependencies.

---

## Proposal 2 — "Home-Lab Easter Egg" (Medium Effort, Memorable)

**Concept**: Lean into the home-lab theme. Show a tiny interactive "server rack" where each blinking LED is a link to a major section.

### Visual
```
┌─────────────────────────────────────┐
│  [█]  Home          [█]  Blog       │
│  [█]  Projects      [█]  Thuis      │
│  [█]  Clock         [█]  Radio      │
│  [█]  Search  🔍                    │
└─────────────────────────────────────┘
   "Rack unit 404 — geen verbinding."
   [Knop] "Reset & ga naar Home"
```

### Features
- CSS-only "blinking" LEDs (`animation: blink 1.5s infinite`).
- Each LED is an `<a>` to the section.
- Small tooltip on hover: project tagline.
- "Reset" button = link to `/nl/`.
- Keeps search input at bottom.

### Implementation
- New partial `overrides/partials/404-rack.html` (HTML + inline `<style>`).
- Include from `docs/nl/404.md` via `{% include "partials/404-rack.html" %}`.
- No JS; works with CSP.

### Effort
~1.5 h. Design the rack SVG/CSS, add partial, test mobile.

---

## Proposal 3 — "Mini Post-Mortem" (Content-Heavy, On-Brand)

**Concept**: Pretend the 404 is an incident report. Show a tiny "post-mortem" card with runbook-style steps.

### Copy Example
```
# Incident 404 — Pagina niet gevonden
**Severity**: SEV-3 (Non-critical)
**Impact**: Bezoeker ziet geen content.
**Root Cause**: URL typo / verplaatst / verwijderd.

## Runbook
1. ☐ Controleer spelling
2. ☐ Zoek via het zoekvak ↓
3. ☐ Ga naar [Home](/nl/) of [Projects](/nl/projects/)
4. ☐ Open een issue als het een echte dode link is → [GitHub Issues](https://github.com/Aldo-f/Aldo-f.github.io/issues/new)

**Owner**: @Aldo-f  •  **Status**: Investigating…
```

### Extras
- Collapsible "Gerelateerde incidenten" = last 3 blog posts.
- Link to "Runbook repo" (your `thuis`/`clock` repos).
- Tiny ASCII server icon (`/assets/images/server-404.svg`).

### Implementation
- Markdown + a custom CSS class `.incident-box` in `overrides/assets/css/404.incident.css`.
- Include the CSS via `extra_css` in `mkdocs.nl.yml` (conditional on 404 page — can use a small JS snippet to inject only on 404).

### Effort
~1 h. Mostly copy + a little CSS.

---

## Comparison

| Criteria | Proposal 1 | Proposal 2 | Proposal 3 |
|----------|------------|------------|------------|
| **Time** | 30 min | 1.5 h | 1 h |
| **Memorability** | ★★☆ | ★★★★ | ★★★☆ |
| **Usefulness** | ★★★★★ | ★★★★ | ★★★★ |
| **On-Brand (Home-Lab)** | ★★☆ | ★★★★★ | ★★★★★ |
| **Maintenance** | Near-zero | Low (CSS) | Low (copy) |
| **Mobile Friendly** | Yes | Yes (flex grid) | Yes |

---

## Recommendation
Start with **Proposal 1** (quick win — search + clear links).  
If you want personality, layer **Proposal 2** on top (the rack) — it’s pure CSS, no runtime cost.  
Proposal 3 is fun if you like the "incident report" voice; can be combined with 1.

---

## Next Steps (Pick One)
1. **Approve a proposal** → I’ll create the partials, update `docs/nl/404.md`, and rebuild.
2. **Mix & match** → Tell me which pieces you like; I’ll merge them.
3. **Defer** → Keep current minimal page; revisit later.

Let me know which direction you prefer.