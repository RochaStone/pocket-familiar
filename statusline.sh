#!/bin/bash
# pocket-familiar status line for Claude Code.
# Claude Code pipes its status JSON on stdin. We print one line: sprite, name, mood, streak, model.
# If anything goes wrong we still print a line, so your status bar never goes blank.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$(python3 "$DIR/familiar" line 2>/dev/null)"
if [ -n "$out" ]; then
  printf '%s\n' "$out"
else
  printf '%s\n' "(  ✧  ) familiar is napping. Run: familiar status"
fi
exit 0
