#!/usr/bin/env bash
# Deterministic fixture tests for safe_sync() extracted from ~/dev/install.sh.
# Upstream commits are authored in a SEPARATE clone so the "work" checkout can
# stay genuinely dirty while origin moves ahead.
set -euo pipefail

INSTALLER="$HOME/dev/install.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

eval "$(sed -n '/^safe_sync() {/,/^}/p' "$INSTALLER")"

# Shared history: seed -> bare origin -> two clones (upstream author, user work).
git init -q "$TMP/seed"
git -C "$TMP/seed" config user.email t@t; git -C "$TMP/seed" config user.name t
echo base  > "$TMP/seed/file.txt"; echo base2 > "$TMP/seed/other.txt"
git -C "$TMP/seed" add .; git -C "$TMP/seed" commit -qm base
git init -q --bare "$TMP/origin.git"
git -C "$TMP/seed" push -q "$TMP/origin.git" main
git clone -q "$TMP/origin.git" "$TMP/upstream"
git clone -q "$TMP/origin.git" "$TMP/work"

pass=0; fail=0
check() { if [[ "$3" == *"$2"* ]]; then echo "PASS: $1"; pass=$((pass+1));
  else echo "FAIL: $1 — expected '$2' in output:"; echo "$3"; fail=$((fail+1)); fi }

# --- 1. up-to-date -> no-op
out=$(safe_sync "$TMP/work" main)
check "1 up-to-date short-circuit" "up to date" "$out"

# --- 2. clean + behind -> fast-forward
(cd "$TMP/upstream" && echo v2 > file.txt && git commit -qam v2 && git push -q origin main)
out=$(safe_sync "$TMP/work" main)
[[ $(cat "$TMP/work/file.txt") == "v2" ]] \
  && { echo "PASS: 2 clean fast-forward to v2"; pass=$((pass+1)); } \
  || { echo "FAIL: 2 expected v2, got '$(cat "$TMP/work/file.txt")'"; fail=$((fail+1)); }

# --- 3. dirty + behind -> stash, update, restore
echo local-edit >> "$TMP/work/other.txt"          # genuine uncommitted change
(cd "$TMP/upstream" && echo v3 > file.txt && git commit -qam v3 && git push -q origin main)
out=$(safe_sync "$TMP/work" main)
check "3a dirty sync reports restore" "Local changes restored" "$out"
grep -q local-edit "$TMP/work/other.txt" \
  && { echo "PASS: 3b local edit survived"; pass=$((pass+1)); } \
  || { echo "FAIL: 3b local edit LOST"; fail=$((fail+1)); }
[[ $(cat "$TMP/work/file.txt") == "v3" ]] \
  && { echo "PASS: 3c fast-forwarded under dirty tree"; pass=$((pass+1)); } \
  || { echo "FAIL: 3c not fast-forwarded, got '$(cat "$TMP/work/file.txt")'"; fail=$((fail+1)); }
[[ -z "$(git -C "$TMP/work" stash list)" ]] \
  && { echo "PASS: 3d stash popped away (no leftovers)"; pass=$((pass+1)); } \
  || { echo "FAIL: 3d stash entry left behind"; fail=$((fail+1)); }

# --- 4. dirty + behind + INSTALL_SKIP_IF_DIRTY=1 -> skip entirely
echo another-edit >> "$TMP/work/other.txt"
(cd "$TMP/upstream" && echo v4 > file.txt && git commit -qam v4 && git push -q origin main)
out=$(INSTALL_SKIP_IF_DIRTY=1 safe_sync "$TMP/work" main)
check "4a skip-if-dirty honored" "INSTALL_SKIP_IF_DIRTY=1" "$out"
grep -q another-edit "$TMP/work/other.txt" \
  && { echo "PASS: 4b dirty change untouched"; pass=$((pass+1)); } \
  || { echo "FAIL: 4b dirty change lost"; fail=$((fail+1)); }
[[ $(cat "$TMP/work/file.txt") == "v3" ]] \
  && { echo "PASS: 4c update skipped (still v3)"; pass=$((pass+1)); } \
  || { echo "FAIL: 4c update NOT skipped, got '$(cat "$TMP/work/file.txt")'"; fail=$((fail+1)); }

# --- 5. local unpushed commits -> untouched
(cd "$TMP/upstream" && echo v5 > file.txt && git commit -qam v5 && git push -q origin main)
(cd "$TMP/work" && echo unpushed > unp.txt && git add unp.txt && git commit -qm unpushed)
out=$(safe_sync "$TMP/work" main)
check "5a unpushed commits respected" "unpushed commits" "$out"
[[ -f "$TMP/work/unp.txt" ]] \
  && { echo "PASS: 5b unpushed commit preserved"; pass=$((pass+1)); } \
  || { echo "FAIL: 5b unpushed commit clobbered"; fail=$((fail+1)); }
[[ $(cat "$TMP/work/file.txt") == "v3" ]] \
  && { echo "PASS: 5c behind-with-unpushed did NOT update"; pass=$((pass+1)); } \
  || { echo "FAIL: 5c unexpected update, got '$(cat "$TMP/work/file.txt")'"; fail=$((fail+1)); }

echo
echo "RESULT: $pass passed, $fail failed"
exit $((fail > 0))
