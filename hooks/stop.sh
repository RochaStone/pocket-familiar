#!/bin/bash
# Stop and SessionEnd hook: records when the session was last active and how long it has run.
# Silent, and always exits 0, so it can never block Claude.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$DIR/familiar" hook stop >/dev/null 2>&1
exit 0
