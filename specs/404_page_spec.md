# 404 Page – Spec Kit

## Purpose
Create a memorable, **multilingual**, **DRY** “404 Dungeon” experience that is fully integrated into the existing MkDocs site. The page must:
- Appear for any missing route (both English `/404-pagina/` and Dutch `/nl/404-pagina/`).
- Share the site header/footer, theme variables, and navigation (no standalone HTML).  
- Use **Material Design 3** components (cards, buttons, chips, progress).  
- Provide a simple state‑machine adventure (5 nodes) with HP/Confusion stats.
- Keep translations as the **only** difference – all code & layout are shared.

---

## Functional Requirements
| ID | Requirement | Details |
|----|--------------|---------|
| **FR‑01** | Multilingual rendering | The same Jinja template (`overrides/404.html`) is used for both EN and NL builds. Language is selected via `page.meta.lang` (Material’s `autotranslate` plugin). |
| **FR‑02** | DRY assets | All CSS/JS asset URLs must be absolute (`/assets/...`). The `hooks/slugmap.py` rewrites `nl/assets/` and `../assets/` → `/assets/`. |
| **FR‑03** | State‑machine adventure | JSON file `data/404_dungeon.json` defines nodes, text (EN/NL), choices, and stat deltas. The page loads it at runtime (`fetch('assets/data/404_dungeon.json')`). |
| **FR‑04** | UI components | Uses Material‑Design‑3 tokens (`--md-sys-color-primary`, `--md-sys-color-surface`, etc.). Elements: `md-card`, `md-button`, `md-chip`, `md-linear-progress`. |
| **FR‑05** | Accessibility | `prefers-reduced-motion` disables animation; all interactive elements have `aria-label`s. |
| **FR‑06** | Navigation exclusion | The 404 page is **not** added to the site `nav`; it is reachable only via a 404 error (i.e. “lost realm”). |
| **FR‑07** | Playwright E2E test | `tests/e2e/test_404_dungeon_multilingual.py` verifies:
  - Page loads at `/nl/404-pagina/` (and `/404-pagina/`).
  - `#dungeon-scene` is visible.
  - Absolute asset URLs exist in the HTML.
  - Title contains “The 404 Dungeon”. |

---

## Data Model (`data/404_dungeon.json`)
```json
{
  "version": "1.0.1",
  "name": "404 Dungeon",
  "description": "Multilingual 404 D&D adventure; EN/NL text lives in docs/<lang>/404_dungeon.md, shared state machine here.",
  "nodes": [
    {
      "id": "start",
      "text": {"en": "You awaken in a dim corridor...", "nl": "Je wordt wakker in een schemerige gang..."},
      "choices": [
        {"label": {"en": "Take the torch", "nl": "Pak de fakkel"}, "next": "torch"},
        {"label": {"en": "Walk forward", "nl": "Vooruit lopen"}, "next": "corridor"}
      ]
    },
    {
      "id": "torch",
      "text": {"en": "The torch flickers, revealing a slime.", "nl": "De fakkel flikkert en onthult een slijm."},
      "choices": [
        {"label": {"en": "Fight", "nl": "Strijden"}, "next": "slime_help", "statDelta": 1},
        {"label": {"en": "Run", "nl": "Vlucht"}, "next": "dead_end", "statDelta": -1}
      ]
    },
    {
      "id": "corridor",
      "text": {"en": "The corridor narrows...", "nl": "De gang versmalt..."},
      "choices": [
        {"label": {"en": "Explore", "nl": "Verkennen"}, "next": "slime_help"},
        {"label": {"en": "Turn back", "nl": "Terugkeren"}, "next": "dead_end"}
      ]
    },
    {
      "id": "slime_help",
      "text": {"en": "A friendly slime offers aid.", "nl": "Een vriendelijke slijm biedt hulp."},
      "choices": [{"label": {"en": "Escape", "nl": "Ontsnappen"}, "next": "escape"}]
    },
    {
      "id": "dead_end",
      "text": {"en": "A dead end blocks your path.", "nl": "Een dood einde blokkeert je weg."},
      "choices": [{"label": {"en": "Escape", "nl": "Ontsnappen"}, "next": "escape"}]
    },
    {
      "id": "escape",
      "text": {"en": "You find the exit and return home.", "nl": "Je vindt de uitgang en keert thuis."},
      "choices": []
    }
  ]
}
```
*Only the `text` field is bilingual; all other fields are shared.*

---

## Template (`overrides/404.html`)
Key points in the Jinja file:
- Extends `base.html` to inherit header/footer and theme.
- Uses `{{ base_url }}` for static assets (CSS/JS).  
- Sets `LANG = 'nl'` for the NL build (`page.meta.lang` for EN).  
- Loads the JSON via `fetch('assets/data/404_dungeon.json')`.  
- Renders the current node, HP (`MAX_CONF - confusion`), and the choice buttons.  
- The “Back to Homepage” button appears only in the `escape` node.  
- Respects `prefers-reduced-motion` by disabling button animations.

---

## Build Process
1. **Install dependencies** (always via `uv pip`):
   ```bash
   uv pip install -r requirements.txt  # mkdocs, material, multirepo, autotranslate, pytest, playwright
   uv pip install pytest-playwright   # for the E2E test
   playwright install chromium       # browsers for Playwright
   ```
2. **Generate absolute asset URLs** – `hooks/slugmap.py` runs after the MkDocs build and:
   - Copies `nl/assets/...` → `/assets/...`.
   - Copies `../assets/...` → `/assets/...`.
   - Copies the shared JSON to both `site/assets/data/` and `site/nl/assets/data/`.
3. **MkDocs build** (strict mode):
   ```bash
   mkdocs build -f mkdocs.en.yml   # English root (assets at /assets/)
   mkdocs build -f mkdocs.nl.yml   # Dutch under /nl/ (same assets)
   ```
4. **Verify** – `tests/test_asset_paths.py` checks that **all** `href`/`src` attributes contain `/assets/`.
5. **Run Playwright test**:
   ```bash
   pytest tests/e2e/test_404_dungeon_multilingual.py
   ```
   The test starts a local server (`python -m http.server 8000 --directory site`) and asserts the UI elements described above.

---

## Verification Checklist
- [ ] `site/404.html` and `site/nl/404/index.html` contain the rendered dungeon (no Jinja tags).  
- [ ] All asset URLs start with `/assets/`.  
- [ ] `data/404_dungeon.json` is present in the repo and copied to `site/assets/data/`.  
- [ ] Playwright E2E test passes on both language URLs.  
- [ ] The 404 page **does not** appear in the `nav:` section of any MkDocs config.  
- [ ] CI pipeline (`.github/workflows/deploy.yml`) runs both builds, runs the tests, and deploys only on success.

---

## Future Extensions (optional)
- Add more nodes or random events to increase replayability.  
- Pull translations from a separate i18n service instead of embedding them in the JSON.  
- Replace the hard‑coded `LANG = 'nl'` with `page.meta.lang` so a single build can serve both languages without separate copies of the JSON (still copy to both `site/assets/...`).  
- Add a small animation or sound effect gated behind the `prefers-reduced-motion` check.

---

## References
- **Material Design 3** token guide – `overrides/404.html` uses `--md-sys-color-*` tokens.  
- **MkDocs multirepo** – `mkdocs.base.yml` `plugins.multirepo.nav_repos` loads external docs.  
- **Playwright** – `pytest-playwright` documentation for the `page` fixture.  
- **Spec‑Kit** – This document follows the organization's spec‑kit pattern: purpose, functional requirements, data model, template notes, build process, verification checklist, future extensions.
