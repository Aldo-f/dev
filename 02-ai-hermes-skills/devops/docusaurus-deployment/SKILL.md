---
name: docusaurus-deployment
description: Deploy Docusaurus sites with custom themes to GitHub Pages.
---

# Docusaurus GitHub Pages Deployment

## When to Use
Use this skill when deploying a Docusaurus documentation site (especially with custom themes) to GitHub Pages via GitHub Actions workflow.

## Key Steps

### 1. Theme Preparation
- Build your custom theme before the docs site build
- For local development: use `npm link` 
- For CI: copy built theme artifacts to `docs/node_modules/@scope/theme-name/`

### 2. Workflow Configuration
Create `.github/workflows/deploy-docs.yml` with:
- Proper Node.js setup and caching (only one `cache-dependency-path` per step)
- Theme build step that copies output to `docs/node_modules/@scope/theme-name/`
- Docs build step after theme is available
- Correct permissions for Pages deployment

### 3. Common Fixes Applied
- **Broken links**: Docusaurus fails build on broken links by default - fix URLs in markdown (use full GitHub URLs for external links like AGENTS.md, not relative paths)
- **Theme resolution**: Ensure `themes: ['@scope/theme-name']` matches installed location in `docs/node_modules/`
- **Base URL**: For GitHub Pages project sites, use `baseUrl: '/repository-name/'`
- **Workflow duplicates**: Remove duplicate `cache-dependency-path` entries in the same step (causes YAML parse errors)
- **Missing theme files**: Copy built theme to `docs/node_modules` before build
- **Deployment auth**: Use `USE_SSH=true` and/or `GIT_USER` env var for authentication to avoid password prompts

### 4. Verification Steps
1. Local test: `cd docs && npx docusaurus serve`
2. Check build output: `ls -la docs/build/`
3. Monitor GitHub Actions workflow for each step (theme build, docs build, deploy)
4. Visit live site: `https://username.github.io/repository/`
5. Verify specific links (e.g., check if external links like AGENTS.md work correctly)

## Example Commands
```bash
# Build theme and docs locally
cd docs-theme && npm ci && npm run build
cd ../docs && npm ci && npm run build
GIT_USER=your-username USE_SSH=true npx docusaurus deploy

# Or with pre-configured SSH:
cd docs && npx docusaurus deploy
```

## Troubleshooting
- "Theme not found" → Verify theme build output copied to correct node_modules path (`docs/node_modules/@scope/theme-name/`)
- "Broken link" → Fix the referenced markdown file path (use full GitHub URLs for external links)
- "Git user not set" → Add `GIT_USER` env var or use `USE_SSH=true`
- Build fails silently → Check GitHub Actions logs for each step
- YAML parse error → Check for duplicate keys like `cache-dependency-path`
- "Could not read Password" → Use `USE_SSH=true` or ensure SSH agent is configured
4. Visit live site: `https://username.github.io/repository/`
5. Verify specific links (e.g., check if AGENTS.md link works correctly)

## Example Commands
```bash
# Build theme and docs locally
cd docs-theme && npm ci && npm run build
cd ../docs && npm ci && npm run build
GIT_USER=your-username USE_SSH=true npx docusaurus deploy

# Or with pre-configured SSH:
cd docs && npx docusaurus deploy
```

## Troubleshooting
- "Theme not found" → Verify theme build output copied to correct node_modules path (`docs/node_modules/@scope/theme-name/`)
- "Broken link" → Fix the referenced markdown file path (use full GitHub URLs for external links)
- "Git user not set" → Add `GIT_USER` env var or use `USE_SSH=true`
- Build fails silently → Check GitHub Actions logs for each step
- YAML parse error → Check for duplicate keys like `cache-dependency-path`