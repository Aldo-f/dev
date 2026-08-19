---
name: mkdocs-multirepo-setup
description: Setup guide for mkdocs‑multirepo‑plugin imports.
version: 1.0.0
author: Hermes Agent
license: MIT
category: software-development
---

# MkDocs Multirepo Setup

This skill captures the reliable workflow for using **mkdocs‑multirepo‑plugin** to import documentation from other repositories into a single MkDocs site.

## Prerequisites
- Python 3.8+ with `pip`.
- Target site repository (Git) you can push to.
- Source repos must contain a `mkdocs.yml` (or custom config) with a `nav` section.

## Installation
```bash
pip install mkdocs mkdocs-material mkdocs-multirepo-plugin
```

## mkdocs.yml – Correct Structure
```yaml
site_name: My Docs
site_url: https://mydomain.github.io
repo_url: https://github.com/me/my-docs-repo
repo_name: me/my-docs-repo

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
    - scheme: slate
      primary: indigo
      accent: indigo
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.top
    - search.highlight
    - search.share
    - navigation.indexes
    - toc.integrate
    - navigation.sections
    - toc.follow

plugins:
  - search
  - multirepo:
      nav_repos:
        - name: thuis
          url: https://github.com/Aldo-f/thuis
        - name: infra
          url: https://github.com/Aldo-f/01-core-infra

nav:
  - Home: docs/index.md
  - Thuis: !import [thuis]
  - Core Infra: !import [infra]
```

### Key Points
1. **`nav_repos` entries must have a `name`** that matches the identifier inside `!import [...]`.
2. The `!import` syntax **requires square brackets** around the name, *not* the raw URL.
3. To import a specific branch, add `?branch=branchname` to the URL, e.g. `url: https://github.com/me/repo?branch=dev`.
4. The plugin clones the source repo (sparse‑clone if supported) into a temporary directory at build time.

## Common Pitfalls
| Symptom | Cause | Fix |
|---|---|---|
| `Error: could not determine a constructor for the tag '!import'` | Used `!import https://...` or omitted brackets. | Use `!import [name]` with a matching entry in `nav_repos`.
| `unknown config key(s), "url" for MultirepoConfig` | Wrong field name for older plugin versions. | Use `import_url:` instead of `url:` or upgrade the plugin.
| `fatal: repository '[repo]' does not exist` | `name` in `!import` does not match any `nav_repos` entry. | Ensure the `name` values match exactly.
| Docs missing in final site | Source repo lacks a `nav` block. | Add a proper `nav:` section to the source repo’s `mkdocs.yml`.

## Workflow Summary
1. Clone/create the site repo.
2. Add the above `mkdocs.yml` (or adapt it).
3. Place site content under `docs/`.
4. Commit & push.
5. Run `mkdocs build` locally to verify.
6. Set up CI (GitHub Actions) to build and deploy via `actions/upload-pages-artifact` and `actions/deploy-pages`.

---

## References
- `references/example-mkdocs.yml` – minimal working example.
- `templates/migrate.sh` – script that automates a full migration from Jekyll to MkDocs with multirepo imports.
