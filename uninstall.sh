#!/bin/bash
# Removes pocket-familiar from Claude Code and unlinks the familiar command.
# Her memories in ~/.familiar stay, in case you come back. Delete that folder to forget her.
set -eu
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
FHOME="${FAMILIAR_HOME:-$HOME/.familiar}"

if [ -f "$SETTINGS" ]; then
  cp "$SETTINGS" "$SETTINGS.pocket-familiar-uninstall-backup-$(date +%Y%m%d%H%M%S)"
  python3 - "$SETTINGS" "$DIR" "$FHOME" <<'PY'
import json, os, sys
settings_path, root, fhome = sys.argv[1], sys.argv[2], sys.argv[3]
with open(settings_path, encoding="utf-8") as fh:
    data = json.load(fh)
def mine(cmd):
    return (cmd or "").startswith(f'bash "{root}/')
if mine((data.get("statusLine") or {}).get("command")):
    prev = os.path.join(fhome, "previous-statusline.json")
    if os.path.exists(prev):
        with open(prev, encoding="utf-8") as fh:
            data["statusLine"] = json.load(fh)
        print("✓ your previous status line is back")
    else:
        data.pop("statusLine", None)
        print("✓ status line removed")
hooks = data.get("hooks", {})
for event in list(hooks):
    groups = []
    for g in hooks[event]:
        kept = [h for h in g.get("hooks", []) if not mine(h.get("command"))]
        if kept:
            groups.append({**g, "hooks": kept})
    if groups:
        hooks[event] = groups
    else:
        del hooks[event]
if not hooks:
    data.pop("hooks", None)
with open(settings_path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
print("✓ hooks removed from " + settings_path)
PY
fi

for d in "$HOME/.local/bin" "/usr/local/bin"; do
  if [ -L "$d/familiar" ] && [ "$(readlink "$d/familiar")" = "$DIR/familiar" ]; then
    rm "$d/familiar"
    echo "✓ unlinked $d/familiar"
  fi
done
echo "Her memories are still in $FHOME. Delete that folder to forget her."
