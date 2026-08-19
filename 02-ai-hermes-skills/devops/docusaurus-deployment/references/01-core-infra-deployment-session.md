# 01-Core-Infra Docusaurus Deployment Session Notes

## Problem
The Docusaurus documentation site was failing to deploy due to:
1. Broken relative link in `docs/docs/getting-started.md` pointing to `/AGENTS.md`
2. Custom theme `@aldo-f/docusaurus-theme` not being resolved during build
3. GitHub Actions workflow having duplicate cache-dependency-path entries
4. Deployment authentication issues with git push

## Solution Implemented

### 1. Fixed Broken Link
Changed in `docs/docs/getting-started.md`:
```diff
-For the full system documentation, architecture overview, and deployment instructions, please refer to the [AGENTS.md](/AGENTS.md) file in the repository root.
+For the full system documentation, architecture overview, and deployment instructions, please refer to the [AGENTS.md](https://github.com/Aldo-f/01-core-infra/blob/main/AGENTS.md) file in the repository root.
```

### 2. Theme Resolution Fix
Updated GitHub Actions workflow (`.github/workflows/deploy-docs.yml`):
- Added step to copy built theme to `docs/node_modules/@allo-f/docusaurus-theme/`
- Removed duplicate `cache-dependency-path` entry
- Ensured theme build occurs before docs build

### 3. Local Verification Process
```bash
# Build theme
cd docs-theme
npm ci
npm run build

# Copy theme to docs
cd ..
rm -rf docs/theme
cp -r docs-theme/dist docs/theme

# Build docs site
cd docs
npm ci
npm run build
GIT_USER=aldo-f USE_SSH=true npx docusaurus deploy
```

### 4. Key Learnings
- Docusaurus treats broken links as fatal errors by default (controlled by `onBrokenLinks` config)
- Custom themes must be available in `node_modules` at build time, not just linked
- GitHub Actions workflows need explicit steps for monorepo/theme dependencies
- SSH deployment (`USE_SSH=true`) avoids credential prompts in CI
- Always verify local build works before pushing to CI

## Files Modified
- `docs/docs/getting-started.md` - Fixed broken AGENTS.md link
- `.github/workflows/deploy-docs.yml` - Fixed workflow duplicates and added theme copy step

## Verification
- Local build: `cd docs && npm run build` succeeds
- Deployment: `cd docs && GIT_USER=aldo-f USE_SSH=true npx docusaurus deploy` succeeds
- Live site: https://aldo-f.github.io/01-core-infra/ returns HTTP 200

## Related Issues
- Theme resolution requires physical presence in node_modules, not just npm link
- Workflow must respect dependency order: theme build → docs build → deploy
- Duplicate configuration entries in YAML can cause silent failures