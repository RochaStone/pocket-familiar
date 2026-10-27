#!/bin/bash
# Installs pocket-familiar.
#   bash install.sh             CLI + Claude Code status line + hooks
#   bash install.sh --cli-only  just the familiar command (any terminal, no Claude Code changes)
# Your Claude Code settings are backed up before anything changes. Undo: bash uninstall.sh
set -eu
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
FHOME="${FAMILIAR_HOME:-$HOME/.familiar}"
CLI_ONLY=0
[ "${1:-}" = "--cli-only" ] && CLI_ONLY=1

command -v python3 >/dev/null 2>&1 || { echo "pocket-familiar needs python3 (3.10 or newer). Install it, then run this again."; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || { echo "pocket-familiar needs Python 3.10 or newer."; exit 1; }

chmod +x "$DIR/familiar" "$DIR/statusline.sh" "$DIR/hooks/"*.sh "$DIR/uninstall.sh"

# 1. The familiar command
BIN=""
for d in "$HOME/.local/bin" "/usr/local/bin"; do
  if [ "$d" = "$HOME/.local/bin" ]; then mkdir -p "$d" 2>/dev/null || true; fi
  if [ -d "$d" ] && [ -w "$d" ]; then BIN="$d"; break; fi
done
if [ -n "$BIN" ]; then
  ln -sf "$DIR/familiar" "$BIN/familiar"
  echo "✓ familiar linked into $BIN"
  case ":$PATH:" in
    *":$BIN:"*) ;;
    *) # Teach the terminal where she lives, once, in your shell profile (uninstall.sh takes it out again)
       case "${SHELL:-}" in *bash) RC="$HOME/.bashrc" ;; *) RC="$HOME/.zshrc" ;; esac
       if ! grep -q "# pocket-familiar PATH" "$RC" 2>/dev/null; then
         printf '\nexport PATH="%s:$PATH"  # pocket-familiar PATH\n' "$BIN" >> "$RC"
       fi
       echo "✓ added $BIN to your PATH in $RC"
       echo "  Open a new terminal window so it takes effect." ;;
  esac
else
  echo "! Could not find a writable bin folder. Run her directly: python3 \"$DIR/familiar\" status"
fi

if [ "$CLI_ONLY" = "1" ]; then
  echo "Done. Hatch her: familiar hatch"
  exit 0
fi

# 2. Claude Code status line and hooks (merged with Python, backup first)
mkdir -p "$(dirname "$SETTINGS")" "$FHOME"
BACKUP=""
if [ -f "$SETTINGS" ]; then
  BACKUP="$SETTINGS.pocket-familiar-backup-$(date +%Y%m%d%H%M%S)"
  cp "$SETTINGS" "$BACKUP"
  echo "✓ backed up your settings to $BACKUP"
fi
python3 - "$SETTINGS" "$DIR" "$FHOME" <<'PY'
import json, os, sys
settings_path, root, fhome = sys.argv[1], sys.argv[2], sys.argv[3]
data = {}
if os.path.exists(settings_path):
    with open(settings_path, encoding="utf-8") as fh:
        text = fh.read().strip()
    data = json.loads(text) if text else {}
status_cmd = f'bash "{root}/statusline.sh"'
prev = data.get("statusLine")
if prev and (not isinstance(prev, dict) or prev.get("command") != status_cmd):
    with open(os.path.join(fhome, "previous-statusline.json"), "w", encoding="utf-8") as fh:
        json.dump(prev, fh, indent=2)
    print(f"  your old status line was saved; uninstall.sh puts it back")
data["statusLine"] = {"type": "command", "command": status_cmd, "padding": 0}
hooks = data.setdefault("hooks", {})
wanted = {
    "SessionStart": f'bash "{root}/hooks/session-start.sh"',
    "Stop": f'bash "{root}/hooks/stop.sh"',
    "SessionEnd": f'bash "{root}/hooks/stop.sh"',
}
for event, cmd in wanted.items():
    groups = hooks.setdefault(event, [])
    if not any(cmd == h.get("command") for g in groups for h in g.get("hooks", [])):
        groups.append({"hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
tmp = settings_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
os.replace(tmp, settings_path)
print("✓ status line and hooks added to " + settings_path)
PY

echo
echo "Next: hatch her.   familiar hatch"
echo "Then restart Claude Code and look at the bottom of the window."
echo
echo "To undo:  bash \"$DIR/uninstall.sh\""
[ -n "$BACKUP" ] && echo "   or restore the backup:  cp \"$BACKUP\" \"$SETTINGS\""
exit 0
