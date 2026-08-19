---
name: static-site-publishing
category: deployment
description: Deploy Docusaurus docs sites to GitHub Pages via CI.
---

# Static Site Publishing (GitHub Pages)

Publishing a Docusaurus (or other SSG) documentation site to GitHub Pages. Covers CI setup, custom theme linking, source config, and common failure modes.

## Triggers

- User asks to "deploy the docs site" or "fix the documentation"
- Site shows stale content (Jekyll instead of Docusaurus)
- "Trigger rebuild" or similar placeholder text is the only content visible

## Quick CI Template (`.github/workflows/deploy-docs.yml`)

Use GitHub Actions with `actions/deploy-pages@v4` — not the legacy Jekyll `main/docs` source:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/setup-node@v3
        with:
          node-version: 20.x
          cache: 'npm'
          cache-dependency-path: docs/package-lock.json
      - run: cd docs && npm ci && npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/build
      - uses: actions/deploy-pages@v4
```

## Docusaurus Configuration (`docusaurus.config.ts`)

```typescript
const config: Config = {
  url: 'https://org-name.github.io',
  baseUrl: '/repo-name/',            // Must match repo name
  trailingSlash: true,
  organizationName: 'org-name',
  projectName: 'repo-name',
  onBrokenLinks: 'throw',            // Switch to 'warn' while developing
};
```

## GitHub Pages Source Config via `gh`

```bash
# Check current config
gh api repos/:owner/:repo/pages --jq '{branch, path, build_type}'

# Switch to GitHub Actions mode (serves from gh-pages branch)
gh api -X PUT repos/:owner/:repo/pages \
  -f "source[branch]=gh-pages" \
  -f "source[path]=/"
```

If `build_type` is not `workflow`, GitHub serves the `gh-pages` branch through Jekyll (stale!). Fix with the PUT above.

## Local Build & Deploy

```bash
# Build
cd docs && npm run build

# Deploy via SSH (avoids HTTPS credential prompts)
cd docs && USE_SSH=true GIT_USER= npx docusaurus deploy
```

## Common Pitfalls

### Custom Theme Not Found

Error: `"Docusaurus was unable to resolve the '@scope/theme-name' theme"`

Fix in CI: build the theme before docs, and copy dist into node_modules:

```yaml
- name: Build theme
  run: |
    cd docs-theme
    npm ci && npm run build
    mkdir -p ../docs/node_modules/@scope/theme-name
    cp -r dist/* ../docs/node_modules/@scope/theme-name/
```

In `docs/package.json`: `"@scope/theme-name": "file:../docs-theme"`

### MDX Compilation Errors

Error: `"Unexpected character '<' before name"` — MDX treats `<` as JSX.

Fix: In table cells, use `&lt;` instead of `<`. In inline code, escape angle brackets:

```md
| RAM | Model |
|-----|-------|
| &lt; 12 GB | qwen3:4b |
```

Also: backtick code in tables needs `&lt;` and `&gt;` for angle brackets.

### HTTPS Credential Prompt During Deploy

Error: `"fatal: could not read Password for 'https://github.com': No such device or address"`

Fix: Use SSH authentication:
```bash
USE_SSH=true GIT_USER= npx docusaurus deploy
```

### Site Shows Stale Content or "Trigger rebuild"

The GitHub Pages config is pointing at the wrong source. Fix:
1. Switch to GitHub Actions deployment via `gh api` (see above)
2. Make sure the workflow actually pushed real docs content (not placeholders)
3. Write actual documentation pages in `docs/docs/`

### YAML: Duplicate Keys

A workflow file with two identical `cache-dependency-path` keys is invalid YAML (parser rejects duplicate keys). Remove the duplicate.

## Writing Site Content

If the site shows only "Trigger rebuild" or the page title is just git commit messages, the `docs/` directory only has placeholder files:

1. Write real `.mdx`/`.md` pages in `docs/docs/` with frontmatter:
   ```md
   ---
   sidebar_position: 1
   ---
   # Page Title
   ```
2. Update `src/pages/index.tsx` to link to your docs instead of the Docusaurus tutorial
3. Update `src/components/HomepageFeatures/index.tsx` with project-specific features
4. Remove any placeholder README.md files that snuck in from commit spam
