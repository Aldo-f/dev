# Docusaurus Deployment Fix - 01-core-infra

## Problem
- Docusaurus build failed with "docusaurus: not found" when running `npx docusaurus deploy`
- Root cause: Theme `@aldo-f/docusaurus-theme` not resolvable during build
- Secondary issues: broken relative link in getting-started.md, blog still enabled

## Solution Implemented

### 1. Fixed Theme Resolution
**Issue**: The custom theme wasn't being copied to `docs/node_modules/@allo-f/docusaurus-theme` where Docusaurus expects it.

**Fix in GitHub Actions** (`.github/workflows/deploy-docs.yml`):
```yaml
- name: Install and build theme
  run: |
    cd docs-theme
    npm ci
    npm run build
    mkdir -p ../docs/node_modules/@allo-f/docusaurus-theme
    cp -r dist/* ../docs/node_modules/@allo-f/docusaurus-theme/
```

### 2. Fixed Broken Link
**Issue**: `docs/docs/getting-started.md` had broken relative link `[AGENTS.md](/AGENTS.md)` causing Docusaurus build to fail on `onBrokenLinks: 'throw'`.

**Fix**: Changed to absolute URL
```markdown
[AGENTS.md](https://github.com/Aldo-f/01-core-infra/blob/main/AGENTS.md)
```

### 3. Disabled Blog (Not Needed)
**Issue**: Unused blog was generating 404 and cluttering navbar/footer.

**Fix** (`docs/docusaurus.config.ts`):
```typescript
blog: false, // Disabled blog plugin
```
Removed blog items from navbar and footer.

### 4. Escaped MDX-Unsafe Characters
**Issue**: Tables containing `<` and `>` in deployment.md and reference.md caused MDX to interpret them as JSX.

**Fix**: Escaped as HTML entities
- `4B (<12GB)` → `4B (<12GB)`
- `12–20 GB` → `12–20 GB` (safe)
- `32 GB+` → `32 GB+` (safe)
- Systemd service names: `app-<name>.service` → `app-<name>.service`

### 5. Corrected GitHub Pages Source
**Issue**: GitHub Pages was configured to serve from `main` branch `/docs` folder (Jekyll), not from `gh-pages` branch (Docusaurus build output).

**Fix**: Updated via GitHub API
```bash
gh api -X PUT repos/Aldo-f/01-core-infra/pages \
  -f "source[branch]=gh-pages" \
  -f "source[path]=/"
```

### 6. Workflow Improvements
- Removed duplicate `cache-dependency-path: docs/package-lock.json` line
- Added explicit theme build and copy step before docs install/build
- Ensured proper Node.js setup with caching

## Verification
After fixes:
- Local build: `npm run build` succeeds
- Local preview: `npm run serve` works
- Deployment: `USE_SSH=true GIT_USER= npx docusaurus deploy` succeeds
- GitHub Actions: `deploy-docs.yml` runs successfully
- Live site: https://aldo-f.github.io/01-core-infra/ shows correct homepage with feature cards
- All docs pages accessible: `/docs/intro`, `/docs/getting-started`, `/docs/architecture`, etc.
- Blog returns 404 (as intended)

## Key Learnings
1. **Theme must be in node_modules**: Docusaurus resolves themes from `node_modules`, not from sibling directories
2. **Order matters in Ansible/npm workflows**: Fix ownership as root FIRST, then run npm as user
3. **MDX is strict**: Treat `.mdx` files as JSX-adjacent; escape HTML-like syntax
4. **GitHub Pages vs Actions**: For Docusaurus, use GitHub Actions to build and deploy to `gh-pages` branch
5. **Verify baseUrl**: For GitHub Pages project sites, `baseUrl: '/<repo-name>/'` is correct

## Files Modified
- `.github/workflows/deploy-docs.yml` - Added theme copy step, fixed caching
- `docs/docs/getting-started.md` - Fixed AGENTS.md link
- `docs/docusaurus.config.ts` - Disabled blog, removed blog nav/footer links
- `docs/docs/deployment.md` - Escaped `<` and `>` in tables
- `docs/docs/reference.md` - Escaped `<` and `>` in tables and service names