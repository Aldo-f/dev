# Plugin Cache Loading Failure Pattern

**Scenario**: Attempts to run npx with a lazy/lazily loaded plugin fail with `ENOENT` or plugin-utils missing, even though the main npm package appears to be installed successfully.

**Root Cause**: Plugin caches under `~/.codex/plugins/` may be incomplete, corrupted, or missing nested dependency files (e.g., `utils/package.json`). This can happen when:
- Plugin installation triggers lazy loading of additional plugin components
- Plugin caches are not cleaned between installs
- Plugin utilities are not installed (e.g., native modules missing build tools on ARM)
- Plugin loading occurs before all repository files are in place

**Symptoms**:
```
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path /home/aldo/.codex/plugins/cache/sisyphuslabs/utils/package.json
npm ERR! errno -2
npm ERR! enoent ENOENT: no such file or directory, open '/home/aldo/.codex/plugins/cache/sisyphuslabs/utils/package.json'
```

**Resolution Patterns**:

**1. Clear and Reinstall Plugin Cache**
```bash
rm -rf ~/.codex/plugins/cache/sisyphuslabs
npm install --force <plugin-name>
npx <plugin-name> install
```

**2. Install Plugin Dependencies Completely**
```bash
# Navigate to plugin's 01-core-infra directory
cd /home/aldo/dev/01-core-infra
# Ensure plugin dependencies are installed
npm install --ignore-scripts
npx <plugin-name> install
```

**3. Verify Plugin Cache Structure**
```bash
ls -la ~/.codex/plugins/cache/sisyphuslabs/
find ~/.codex/plugins -name "package.json" | head -10
```

**4. Create Missing Plugin Utils**
```bash
mkdir -p ~/.codex/plugins/cache/sisyphuslabs/utils
cd ~/.codex/plugins/cache/sisyphuslabs/utils
npm init -y
npm install --global <any additional utils dependencies>
```

**5. Check Plugin Loading Dependencies**
```bash
# Add to package.json if plugin has custom install hooks
"scripts": {
  "prepare": "<plugin-install-hook>",
  "postinstall": "<ensure-plugin-utils>"
}
```

**Prevention**:
- Add a verification step after npm install that checks the existence of critical plugin cache files
- Use `npm install --force` before running plugins that may have nested dependencies
- Consider adding a cleanup step in CI/CD pipelines to avoid stale plugin caches
- When using git repos that clone lazy-loaded plugins, ensure cloning completes before plugin execution

**Reference**: This pattern emerged during `lazycodex-ai` installation in a fresh Node project where the lazy-loaded component required additional utils that weren't pulled during the initial install due to the `--ignore-scripts` default behavior.