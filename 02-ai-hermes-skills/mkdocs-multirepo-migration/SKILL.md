---
name: mkdocs-multirepo-migration
category: documentation
description: Migrate docs to MkDocs multirepo for multi-repo aggregation.
tags:
  - mkdocs
  - multirepo
  - github-pages
  - documentation
  - migration
---

# MkDocs Multirepo Migration

Migrating documentation sites to MkDocs with the `mkdocs-multirepo-plugin` to aggregate multiple repositories into a single documentation hub.

## Triggers

- User wants to create a central documentation hub
- Migrating from Jekyll to MkDocs
- Need to aggregate docs from multiple GitHub repositories
- Setting up Material for MkDocs with multirepo plugin

## Prerequisites

1. **Source repositories must use MkDocs** — Docusaurus, Jekyll, or other SSGs cannot be imported via the multirepo plugin
2. **GitHub CLI (`gh`)** installed and authenticated
3. **Python 3.8+** with pip access

## Standard Workflow

### 1. Repository Setup

```bash
gh repo clone <owner>/<repo>
cd <repo>
```

### 2. Jekyll Cleanup (if migrating from Jekyll)

```bash
rm -rf _includes _layouts _posts pages
rm -f _config.yml Gemfile Gemfile.lock
```

### 3. Create Required Files

**requirements.txt:**
```
mkdocs
mkdocs-material
mkdocs-multirepo-plugin
```

**mkdocs.yml:**
```yaml
site_name: Documentation Hub
site_url: https://owner.github.io
repo_url: https://github.com/owner/repo
repo_name: owner/repo
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
plugins:
  - search
  - multirepo
nav:
  - Home: docs/index.md
  - 'Thuis: "!import https://github.com/owner/thuis?branch=main"'
  - 'Core Infra: "!import https://github.com/owner/infra?branch=main"'
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/owner
markdown_extensions:
  - toc:
      permalink: true
```

**GitHub Actions workflow (`.github/workflows/deploy.yml`):**
```yaml
name: Deploy MkDocs site to GitHub Pages

on:
  push:
    branches:
      - master

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Build site
        run: mkdocs build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 4. Commit and Push

```bash
git add .
git commit -m "Migrate to MkDocs with multirepo plugin"
git push origin master
```

## Critical Syntax Rules

### YAML `!import` Tag

The `!import` tag **MUST be quoted** in navigation items:

```yaml
# Wrong
nav:
  - Thuis: !import https://github.com/owner/repo

# Correct
nav:
  - Thuis: '!import https://github.com/owner/repo'
```

### Branch Specification

Always specify the branch explicitly:

```yaml
nav:
  - Thuis: '!import https://github.com/owner/thuis?branch=main'
```

### Config File Path

If the source repo doesn't have `mkdocs.yml` in the root, specify the path:

```yaml
nav:
  - Thuis: '!import https://github.com/owner/repo?branch=main&config=path/to/mkdocs.yml'
```

## Common Pitfalls

### Importing Non-MkDocs Repos

**Error:** `ImportDocsException: repo doesn't have mkdocs.yml at ...`

**Cause:** The target repository uses Docusaurus, Jekyll, or another SSG, not MkDocs.

**Fix:** Remove the import or convert the source repo to MkDocs first.

### YAML Tag Not Recognized

**Error:** `could not determine a constructor for the tag '!import'`

**Cause:** The `!import` tag is not quoted in the YAML.

**Fix:** Wrap in single or double quotes: `'!import ...'`

### Wrong Branch Name

**Error:** `fatal: Remote branch master not found in upstream origin`

**Cause:** The default branch is `main`, not `master`.

**Fix:** Specify the correct branch: `?branch=main`

### GitHub Pages Still Using Legacy (Jekyll) Build

**Symptom:** Actions workflow reports "Deploy to GitHub Pages — success" but the live site returns 404 with Jekyll generator tag (`<meta name="generator" content="Jekyll v3.10.0" />`).

**Root Cause:** GitHub Pages is configured with `build_type: "legacy"` (source = branch + Jekyll) instead of `build_type: "workflow"` (source = Actions artifact).

**Fix:** Switch to workflow mode via GitHub API:

```bash
# Check current config
gh api repos/:owner/:repo/pages --jq '{build_type, source}'

# Switch to workflow mode (PUT, not PATCH)
gh api -X PUT repos/:owner/:repo/pages -f build_type=workflow
```

**Verification:** After the change, `gh api repos/:owner/:repo/pages --jq '.build_type'` should return `"workflow"`, and subsequent deployments will serve the Actions artifact.

## Verification

Build locally to verify:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdocs build
```

## Related Skills

- `static-site-publishing` — Deploy Docusaurus sites to GitHub Pages