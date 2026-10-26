#!/bin/bash
# Smoke test: feed sample status JSON to statusline.sh and check the one line it prints.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
export FAMILIAR_HOME="$TMP" FAMILIAR_NOW="2026-10-26T14:00:00+08:00" NO_COLOR=1
fail=0
ok() { if eval "$2"; then echo "✓ $1"; else echo "✗ $1"; fail=1; fi; }

egg="$(bash "$ROOT/statusline.sh" < "$ROOT/tests/fixtures/statusline-input.json")"
echo "  before hatch: $egg"
ok "egg line before hatching" '[[ "$egg" == *"familiar hatch"* ]]'

python3 "$ROOT/familiar" hatch --name Lucky >/dev/null
python3 "$ROOT/familiar" config --quiet off >/dev/null
python3 "$ROOT/familiar" feed shipped "the newsletter" >/dev/null
line="$(bash "$ROOT/statusline.sh" < "$ROOT/tests/fixtures/statusline-input.json")"
echo "  after feed:   $line"
ok "one line" '[ "$(printf "%s\n" "$line" | wc -l | tr -d " ")" = "1" ]'
ok "name, mood, streak, model" '[[ "$line" == *Lucky*celebrating*"streak 1d"*"Opus 5.5"* ]]'
ok "cost when present" '[[ "$line" == *0.42* ]]'
ok "diamond grill in sprite" '[[ "$line" == *✧* ]]'

for input in "" "not json" "[1,2]" '{"model":"plain-string"}'; do
  out="$(printf '%s' "$input" | bash "$ROOT/statusline.sh")"; rc=$?
  ok "survives input: ${input:-<empty>}" '[ $rc -eq 0 ] && [[ "$out" == *Lucky* ]]'
done

colour="$(env -u NO_COLOR bash "$ROOT/statusline.sh" < "$ROOT/tests/fixtures/statusline-input.json")"
ok "hot pink ANSI when colour is on" '[[ "$colour" == *"38;2;255;45;138"* ]]'
exit $fail
