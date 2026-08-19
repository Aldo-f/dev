---
name: playwright-setup
description: "Playwright missing: install browsers and Linux libs."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Playwright Setup (Class-Level Skill)

## When to use
Trigger on errors like "Live probe failed: Browser (playwright not installed)" or when a repo lists `@playwright/test` or `playwright`.

## Steps
1. Install pnpm (or your preferred manager): `sudo npm install -g pnpm`.
2. Run `pnpm install` in the workspace root. If it aborts with ignored build scripts, run `pnpm approve-builds` and select needed packages (e.g., `core-js`, `electron`, `esbuild`).
3. Install browsers: `npx playwright install`.
4. Install missing system libraries (Debian/Ubuntu on ARM64). See `references/host-dependencies.md`.
5. Verify: `npx playwright test --project=chromium`.

## Pitfalls & Tips
- `pnpm approve-builds` is required for workspaces with native build steps.
- Library list may vary by distro; adjust package names accordingly.
- Clear Playwright cache if binaries become corrupted: `rm -rf ~/.cache/ms-playwright/*`.

## References
- `references/host-dependencies.md` – full list of required Linux libs.
- Playwright docs: https://playwright.dev/docs/intro
