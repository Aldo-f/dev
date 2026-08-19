# Session Learnings: Fixing script.google CI (August 2026)

## Problem 1: Node 24 + extensionless temp file
**Error**: `TypeError [ERR_UNKNOWN_FILE_EXTENSION]: Unknown file extension ".XXXXXX" for /tmp/tmp.XXXXXX`

**Root cause**: Workflow used `tmpfile=$(mktemp)` (no extension) then `node --check "$tmpfile"`
- Node 20: tolerated extensionless files
- Node 24 (GH Actions forced runner): requires .js/.cjs/.mjs for ESM detection

**Fix**: `tmpfile=$(mktemp --suffix=.js)`

## Problem 2: Workflow YAML parse failure (~0s duration)
**Symptoms**: Job shows 0s duration, "This run likely failed because of a workflow file issue."

**Diagnosis**: Local validation with `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/foo.yml'))"`

**Root cause**: The `run:` step contained unquoted JSON braces:
```yaml
run: echo '{"scriptId": "..."}' > file.json
```
GitHub's YAML 1.2 parser interpreted the `{...}` as a flow mapping inside the scalar value, which is invalid.

**Fix**: Use block scalar (`|`) to treat the entire content as a literal string:
```yaml
run: |
  echo '{"scriptId": "..."}' > file.json
```

## Problem 3: Broken global stubbing in syntax check
**Symptom**: Syntax check passed transform but broke actual code by rewriting `GmailApp.search(...)` into `{...}.search(...)` (invalid JS)

**Root cause**: Over-eager sed stubbing of Apps Script globals for a syntax check that doesn't need them.

**Fix**: For pure syntax validation, simply `cp "$file" "$tmpfile"` and run `node --check` on the copy.
- No globals stubbing needed for syntax-only check
- Preserves original code validity

## Verification
After fixes, validate locally:
```bash
# YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/validate.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/clasp-sync.yml'))"

# Node.js syntax check mimics CI
for f in $(find . -name "*.gs" -not -path "./.clasp/*" -not -path "./node_modules/*"); do
  tmpfile=$(mktemp --suffix=.js)
  cp "$f" "$tmpfile"
  if ! node --check "$tmpfile"; then
    echo "FAIL: $f"
    rm -f "$tmpfile"
    exit 1
  fi
  rm -f "$tmpfile"
done
echo "All .gs files parse successfully"
```

## Key Takeaways
1. **Node version matters**: GH Actions runtime != declared version for deprecated lines
2. **YAML is strict**: Anything that looks like YAML inside a scalar will be parsed as YAML
3. **Syntax ≠ semantics**: A syntax checker doesn't need to execute or stub globals
4. **Local validation saves time**: Catch these before pushing