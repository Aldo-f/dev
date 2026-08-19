---
name: github-actions-ci-troubleshooting
description: Debug and fix common GitHub Actions CI failures
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Actions, CI/CD, DevOps, Troubleshooting]
---

# GitHub Actions CI Troubleshooting

Quick-reference guide for diagnosing and fixing common GitHub Actions failures.

## Table of Contents
1. [Node.js Version / Temp-File Gotcha](#nodejs-version--temp-file-gotcha-node-24)
2. [Workflow YAML Parse Failures](#workflow-yaml-parse-failures-0s-duration)
3. [General CI Failure Patterns](#general-ci-failure-patterns)
4. [Decision Tree](#decision-tree)
5. [Verification & Re-running](#verification--re-running)

---

## Node.js Version / Temp-File Gotcha (Node 24)

### Symptoms in logs
```
TypeError [ERR_UNKNOWN_FILE_EXTENSION]: Unknown file extension ".XXXXXX" for /tmp/tmp.XXXXXX
    at checkSyntax (node:internal/main/check_syntax:69:20)
```

### What happened
Your workflow ran `node --check "$(mktemp)"` (no file extension) on a temp file.
- Node 20 tolerated extensionless files
- GitHub Actions now forces these jobs onto **Node 24** (Node 20 deprecated)
- Node 24’s ESM loader strictly requires `.js`, `.cjs`, or `.mjs` extension
→ throws `ERR_UNKNOWN_FILE_EXTENSION`

### Fix
Give the temp file a `.js` suffix so Node recognizes it as a CommonJS module:
```yaml
tmpfile=$(mktemp --suffix=.js)
cp "$file" "$tmpfile"   # or apply your transform here
if ! node --check "$tmpfile"; then
  rm -f "$tmpfile"
  exit 1
fi
```

Or skip globals substitution for pure syntax check:
```yaml
tmpfile=$(mktemp --suffix=.js)
cp "$file" "$tmpfile"   # plain copy is enough for syntax
if ! node --check "$tmpfile"; then
  rm -f "$tmpfile"
  exit 1
fi
```

---

## Workflow YAML Parse Failures (0s Duration)

### Symptoms in logs
- Job ID shows `0s` duration
- GitHub UI: “This run likely failed because of a workflow file issue.”
- No job steps ran; runner rejected workflow before starting

### What happened
GitHub’s YAML 1.2 parser rejected the workflow file. Common causes:
- Plain scalars where a mapping was expected (or vice versa)
- Using flow-style JSON (`{...}`) inside a `run:` string without quoting as block scalar
- Tabs instead of spaces
- Incorrect `on:` triggers or missing required keys

### Diagnose locally
```bash
# Install pyyaml if needed: pip install pyyaml
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/foo.yml'))"
# If it throws, the exception tells you exact line and column
```

### Typical fixes
- **Flow mapping in `run:`**: `run: echo '{...}'` looks like a YAML mapping  
  Fix: Use block scalar (`|`) so GitHub treats it as literal string:
  ```yaml
  run: |
    echo '{"scriptId": "..."}' > file.json
  ```
- Replace tabs with spaces (run `yamllint` locally)
- Ensure `on:` keys are exactly `push:`, `pull_request:`, `workflow_dispatch:`

---

## General CI Failure Patterns

### Test Failures
**Signatures**: `FAILED tests/test_foo.py::test_bar - AssertionError`, `ModuleNotFoundError`
**Fixes**: Update assertions, fix logic, add missing dependencies

### Lint / Formatting Failures
**Signatures**: `file.py:45:1: E302 expected 2 blank lines, got 1`, `line too long`
**Fixes**: Run formatter locally (`black .`, `isort .`, `ruff check --fix`), fix style violations

### Type Check Failures (mypy/pyright)
**Signatures**: `file.py:23: error: Argument 1 to "process" has incompatible type "str"; expected "int"`
**Fixes**: Fix type mismatches, add missing return statements

### Build Failures
**Signatures**: `ModuleNotFoundError`, `Cannot find module`, version conflicts
**Fixes**: Add missing dependencies to requirements files, update/pin versions

### Permission Errors
**Signatures**: `Error: Process completed with exit code 1.`, permission denied on deploy
**Fixes**: Usually requires updating workflow permissions (may need manual intervention)

---

## Decision Tree

```
CI Failed
├── Test failure
│   ├── Assertion mismatch → update test or fix logic
│   └── Import/module error → add dependency
├── Lint failure → run formatter, fix style
├── Type error → fix types
├── Build failure
│   ├── Missing dep → add to requirements
│   └── Version conflict → update pins
├── Permission error → update workflow permissions (needs user)
├── Temp-file/Node 24 → add .js suffix to mktemp or avoid node --check on extensionless files
└── Workflow YAML parse → lint locally, fix illegal YAML (often flow mapping in run:)
    └── Timeout → investigate perf (may need user input)
```

---

## Verification & Re-running

After fixing:
```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push

# Monitor results
gh pr checks --watch 2>/dev/null || \\
  echo "Poll with: curl -s -H 'Authorization: token ...' \\
    https://api.github.com/repos/OWNER/REPO/commits/$(git rev-parse HEAD)/status"
```

---

## Pro Tips
1. **Always validate YAML locally** before pushing workflow changes
2. **Use `mktemp --suffix=.js`** for any `node --check` temp files
3. **Prefer `cp "$file" "$tmpfile"`** over complex sed transforms when only checking syntax
4. **Keep workflows simple** – complex bash in YAML is hard to debug
5. **Log filesystem layout** when debugging paths: `ls -laR` in relevant directories