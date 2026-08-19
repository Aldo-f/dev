---
name: github-pages-docs
category: infrastructure
description: Deploy Docusaurus sites to GitHub Pages.
---

# GitHub Pages Docusaurus Deployment

**Trigger**: User needs to deploy, update, or troubleshoot a Docusaurus documentation site hosted on GitHub Pages via GitHub Actions workflow.

## When to Use
- Deploying a Docusaurus site to GitHub Pages for the first time
- Updating documentation and triggering a redeploy
- Troubleshooting build failures (theme resolution, broken links, MDX errors)
- Fixing GitHub Pages source configuration (should be gh-pages branch, not main branch)
- Disabling unused features like blog to simplify the site

## Core Principles
1. **Theme must be in node_modules**: Docusaurus resolves themes from `node_modules/@scope/theme-name`, not from sibling directories
2. **Fix ownership before npm**: In Ansible/workflows, fix file permissions as root FIRST, then run npm as user
3. **MDX is strict**: Treat .mdx files as JSX-adjacent; escape HTML-like syntax (`<`, `>`) in tables and text
4. **GitHub Pages vs Actions**: For Docusaurus, use GitHub Actions to build and deploy to `gh-pages` branch
5. **Verify baseUrl**: For GitHub Pages project sites, use `baseUrl: '/<repo-name>/'`

## Standard Workflow

### 1. Local Development & Testing
```bash
# Install dependencies
cd /path/to/docs
npm install

# Build locally
npm run build

# Preview locally  
npm run serve

# Deploy manually (use SSH key)
USE_SSH=true GIT_USER= npx docusaurus deploy
```

### 2. GitHub Actions Deployment (`.github/workflows/deploy-docs.yml`)
```yaml
name: Deploy Docusaurus to GitHub Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: false
          fetch-depth: 0

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 20.x
          cache: 'npm'
          cache-dependency-path: docs/package-lock.json

      - name: Install and build theme
        run: |
          cd docs-theme
          npm ci
          npm run build
          mkdir -p ../docs/node_modules/@your-scope/your-theme
          cp -r dist/* ../docs/node_modules/@your-scope/your-theme/

      - name: Install dependencies
        run: |
          cd docs
          npm ci

      - name: Build Docusaurus site
        run: |
          cd docs
          npm run build

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/build

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Common Issues & Fixes

### ❌ "docusaurus: not found" when running npx
**Cause**: Local docusaurus not installed in project  
**Fix**: `npm install` in the docs/ directory (not global install)

### ❌ Theme not found: "Unable to resolve the '@scope/theme-name' theme"
**Cause**: Theme built but not copied to `docs/node_modules/@scope/theme-name/`  
**Fix**: Add copy step in workflow or local build process:
```bash
cd themes/your-theme && npm ci && npm run build
cd ../docs && mkdir -p node_modules/@your-scope/your-theme && cp -r ../themes/your-theme/dist/* node_modules/@your-scope/your-theme/
```

### ❌ Build fails on broken links when `onBrokenLinks: 'throw'`
**Cause**: Relative links like `[AGENTS.md](/AGENTS.md)` that don't resolve to actual files  
**Fix**: Use absolute URLs or ensure file exists:
```markdown
[AGENTS.md](https://github.com/your-username/your-repo/blob/main/AGENTS.md)
```

### ❌ MDX compilation fails with "Unexpected character '<'"
**Cause**: Tables or text containing `<` or `>` that Docusaurus interprets as JSX  
**Fix**: Escape as HTML entities:
- `<` → `<`
- `>` → `>`

### ❌ Site shows Jekyll template instead of Docusaurus build
**Cause**: GitHub Pages source configured as `main` branch `/docs` folder (triggers Jekyll)  
**Fix**: Set source to `gh-pages` branch `/` (for Docusaurus build output):
```bash
gh api -X PUT repos/OWNER/REPO/pages \
  -f "source[branch]=gh-pages" \
  -f "source[path]=/"
```

### ❌ 404 on docs pages after deploy
**Cause**: `baseUrl` misconfiguration  
**Fix**: In `docusaurus.config.ts`:
```typescript
// For GitHub Pages project site: https://username.github.io/repo-name/
baseUrl: '/repo-name/';
// For user/org site: https://username.github.io/
baseUrl: '/',
```

## File Structure Expectations
```
/docs
  /docs-content          # Your .md and .mdx files
  /src                   # Custom components and CSS
    /components/HomepageFeatures/index.tsx  # Override homepage features
  /static                # Static assets (images, favicon)
  docusaurus.config.ts   # Site configuration
  sidebars.ts            # Sidebar definition
  package.json           # Scripts and dependencies
/node_modules            # Built themes go here: @your-scope/your-theme
/docs-theme              # Optional: separate theme package
  /dist                  # Built theme output (copied to docs/node_modules)
```

## Performance Tips
- Use `--legacy-peer-deps` with npm ci for React 18/19 ecosystems
- Set `npm config set unsafe-perm true` instead of `--unsafe-perm` flag (deprecated)
- Always add `/bin` to PATH explicitly in shell tasks: `PATH: "...:/bin:$PATH"`
- Keep theme lightweight: only export what Docusaurus needs (theme.js, CSS, etc.)

## Validation Checklist
- [ ] Local build succeeds: `npm run build`
- [ ] Local preview works: `npm run serve` 
- [ ] Manual deploy works: `USE_SSH=true GIT_USER= npx docusaurus deploy`
- [ ] GitHub Actions workflow runs successfully
- [ ] GitHub Pages source is `gh-pages` branch `/`
- [ ] Site loads at `https://username.github.io/repo-name/`
- [ ] All docs pages render correctly
- [ ] Unused features (blog, etc.) are disabled if not needed
- [ ] No console errors in browser dev tools

## Related Skills
- `ansible-troubleshooting` - For npm/node permission fixes in Ansible contexts
- `freellmapi-integration` - See references for how this skill documents cross-skill learnings