# MkDocs Multirepo Migration Error Reference

## Session: 2026-08-03 Aldo-f.github.io Migration

### Problem: YAML `!import` Tag Not Recognized

**Error:**
```
Error: MkDocs encountered an error parsing the configuration file: 
could not determine a constructor for the tag '!import'
  in "/home/aldo/dev/06-apps-aldo-f-github-io/mkdocs.yml", line 31, column 12
```

**Root Cause:** The `!import` tag was not quoted in the YAML navigation section.

**Solution:** Quote the import statement:
```yaml
# Wrong
nav:
  - Thuis: !import https://github.com/Aldo-f/thuis

# Correct
nav:
  - Thuis: '!import https://github.com/Aldo-f/thuis'
```

---

### Problem: Remote Branch Not Found

**Error:**
```
Cloning into 'thuis'...
warning: Could not find remote branch master to clone.
fatal: Remote branch master not found in upstream origin
```

**Root Cause:** The `thuis` repository uses `main` as its default branch, not `master`.

**Solution:** Specify the branch explicitly in the import URL:
```yaml
nav:
  - Thuis: '!import https://github.com/Aldo-f/thuis?branch=main'
```

---

### Problem: Source Repo Uses Docusaurus, Not MkDocs

**Error:**
```
mkdocs_multirepo_plugin.util.ImportDocsException: core-infra doesn't have mkdocs.yml at ...
```

**Investigation:**
```bash
# Checked 01-core-infra repository structure
find /tmp/01-core-infra -name "mkdocs.yml" -type f
# Result: No mkdocs.yml found in root

# Found Docusaurus config instead
ls -la /tmp/01-core-infra/01-core-infra/docs/
# Contains: docusaurus.config.ts, package.json, tsconfig.json

# CI workflow confirmed Docusaurus deployment
cat /tmp/01-core-infra/.github/workflows/deploy-docs.yml
# Uses: actions/setup-node, npm ci, npm run build
```

**Root Cause:** The `01-core-infra` repository uses Docusaurus (React-based SSG), not MkDocs. The multirepo plugin can only import MkDocs-based documentation sites.

**Solution:** Remove the import for non-MkDocs repositories:
```yaml
nav:
  - Home: docs/index.md
  - Thuis: '!import https://github.com/Aldo-f/thuis?branch=main'
  # Note: 01-core-infra uses Docusaurus, not MkDocs - cannot be imported directly
```

---

### Working Configuration

Final working `mkdocs.yml`:
```yaml
site_name: Aldo Fieuw Documentation
site_url: https://aldo-f.github.io
repo_url: https://github.com/Aldo-f/Aldo-f.github.io
repo_name: Aldo-f/Aldo-f.github.io
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
    - navigation.top
    - navigation.sections
    - toc.follow
    - toc.integrate
plugins:
  - search
  - multirepo
nav:
  - Home: docs/index.md
  - Thuis: '!import https://github.com/Aldo-f/thuis?branch=main'
  # Note: 01-core-infra uses Docusaurus, not MkDocs - cannot be imported directly
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/Aldo-f
    - icon: fontawesome/brands/linkedin
      link: https://linkedin.com/in/aldo-fieuw
    - icon: fontawesome/brands/mastodon
      link: https://mastodon.social/@aldo_fieuw
markdown_extensions:
  - toc:
      permalink: true
```

---

### Build Output

```
INFO    -  Multirepo plugin importing docs...
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /home/aldo/dev/06-apps-aldo-f-github-io/site
INFO    -  Multirepo plugin is not copying config file: thuis/mkdocs.yml
INFO    -  Documentation built in 2.12 seconds
```

Build successful with one warning about `docs/index.md` not being found (expected - the file needs to be created with content).

---

### Git Status After Migration

```
On branch master
Changes not staged for commit:
  modified:   mkdocs.yml
  modified:   .gitignore

Untracked files:
  migrate.sh
  site/
```

The `site/` directory and `migrate.sh` should be added to `.gitignore`:
```gitignore
_site
.sass-cache
.jekyll-metadata
site/
migrate.sh
.venv/
venv/
```

---

### Verification Commands

```bash
# Check build output structure
ls -la site/
ls -la site/thuis/

# Preview site locally
source venv/bin/activate
mkdocs serve

# Check GitHub Pages status
gh repo view Aldo-f/Aldo-f.github.io --json pages
```