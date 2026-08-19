---
name: docusaurus-github-deployment
description: Deploy Docusaurus sites with custom themes to GitHub Pages.
---

# Docusaurus GitHub Pages Deployment

## When to Use
Use this skill when deploying a Docusaurus documentation site (especially with custom themes) to GitHub Pages via GitHub Actions workflow.

## Key Lessons from Implementation
- Custom themes must be built and made available in the consuming project's `node_modules` before the main build
- Docusaurus treats broken links as build failures by default - fix all links or temporarily adjust `onBrokenLinks`/`onBrokenMarkdownLinks` settings
- GitHub Actions workflows need explicit steps for monorepo/theme dependencies (build theme first, then copy to consuming project)
- For deployment authentication, prefer SSH (`USE_SSH=true`) over HTTPS to avoid credential prompts in CI
- Always verify local build works before pushing to CI

## Key Steps

### 1. Theme Preparation
- Build your custom theme before the docs site build
- For local development: use `npm link` 
- For CI: copy built theme artifacts to `docs/node_modules/@scope/theme-name/`

### 2. Workflow Configuration
Create `.github/workflows/deploy-docs.yml` with:
- Proper Node.js setup and caching
- Theme build step that copies output to docs/node_modules
- Docs build step after theme is available
- Correct permissions for Pages deployment

### 3. Common Fixes Applied
- **Broken links**: Fix the referenced markdown file path (Docusaurus fails build on broken links by default)
- **Theme resolution**: Ensure `themes: ['@scope/theme-name']` matches installed location in node_modules
- **Base URL**: For GitHub Pages project sites, use `baseUrl: '/repository-name/'`
- **Workflow duplicates**: Remove duplicate `cache-dependency-path` entries
- **Missing theme files**: Copy built theme to `docs/node_modules` before build

### 4. Verification Steps
1. Local test: `cd docs && npx docusaurus serve`
2. Check build output: `ls -la docs/build/`
3. Monitor GitHub Actions workflow
4. Visit live site: `https://username.github.io/repository/`

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
- "Theme not found" → Verify theme build output copied to correct node_modules path
- "Broken link" → Fix the referenced markdown file path
- "Git user not set" → Add `GIT_USER` env var or use `USE_SSH=true`
- Build fails silently → Check GitHub Actions logs for each step