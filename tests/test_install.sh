#!/bin/bash
# Installs into a fake HOME, checks settings.json is merged (not clobbered), then uninstalls.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAKE="$(mktemp -d)"; trap 'rm -rf "$FAKE"' EXIT
mkdir -p "$FAKE/.claude"
cat > "$FAKE/.claude/settings.json" <<'JSON'
{"model":"opus","statusLine":{"type":"command","command":"echo old"},"hooks":{"Stop":[{"hooks":[{"type":"command","command":"echo mine"}]}]}}
JSON
fail=0
ok() { if eval "$2"; then echo "✓ $1"; else echo "✗ $1"; fail=1; fi; }
HOME="$FAKE" bash "$ROOT/install.sh" >"$FAKE/out.txt" 2>&1
ok "install exits 0" '[ $? -eq 0 ]'
S="$FAKE/.claude/settings.json"
ok "backup made" 'ls "$FAKE/.claude/" | grep -q pocket-familiar-backup'
ok "status line points at us" 'grep -q "statusline.sh" "$S"'
ok "existing hook and model kept" 'grep -q "echo mine" "$S" && grep -q "\"opus\"" "$S"'
ok "three hooks added" '[ "$(grep -c "pocket-familiar/hooks\|/hooks/s" "$S")" -ge 3 ]'
ok "CLI linked" '[ -L "$FAKE/.local/bin/familiar" ]'
ok "prints how to undo" 'grep -q "uninstall.sh" "$FAKE/out.txt"'
ok "PATH line added once to the shell profile" '[ "$(cat "$FAKE"/.zshrc "$FAKE"/.bashrc 2>/dev/null | grep -c "pocket-familiar PATH")" = "1" ]'
HOME="$FAKE" bash "$ROOT/install.sh" >/dev/null 2>&1
ok "idempotent (no duplicate hooks)" '[ "$(grep -c "hooks/stop.sh" "$S")" = "2" ]'
HOME="$FAKE" bash "$ROOT/uninstall.sh" >/dev/null 2>&1
ok "uninstall restores old status line" 'grep -q "echo old" "$S"'
ok "uninstall removes our hooks only" '! grep -q "hooks/stop.sh" "$S" && grep -q "echo mine" "$S"'
ok "uninstall unlinks CLI" '[ ! -e "$FAKE/.local/bin/familiar" ]'
ok "uninstall removes the PATH line" '! cat "$FAKE"/.zshrc "$FAKE"/.bashrc 2>/dev/null | grep -q "pocket-familiar PATH"'
exit $fail
