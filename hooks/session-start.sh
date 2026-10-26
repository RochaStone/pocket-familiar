#!/bin/bash
# SessionStart hook: records the session start and greets you with her mood in one line.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$DIR/familiar" hook session-start 2>/dev/null
exit 0
