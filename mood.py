"""The familiar's moods. One pure function, decide(), picks exactly one state.

States, checked in this order. The first rule that matches wins.

  1. asleep       Now is inside the quiet hours (config "quiet_hours", default "23:00-07:00",
                  null turns it off). She sleeps through everything, like a real pet.
  2. worried      The probe ledger (config "ledger") shows at least one failing probe.
                  Something you shipped is broken. That outranks any party.
  3. celebrating  In the last hour you fed her "shipped" or "invoiced", or a feed in the
                  last hour took your streak to 3, 7 or 21 days.
  4. sleepy       A Claude Code session has been open longer than "sleepy_hours" (default 3)
                  and was active in the last 30 minutes. Care beats chores, so this sits
                  above restless.
  5. restless     The open-items file (config "open_items") has items whose default date
                  has arrived.
  6. hungry       No feed for "hunger_hours" (default 24), or she has never eaten.
  7. fed          None of the above.

Streak: consecutive local days with at least one feed, counted back from today. A streak
stays alive until the end of the day after your last feed.

Everything here is pure (no file or clock access) so the tests can pin every rule.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

STATES = ("asleep", "worried", "celebrating", "sleepy", "restless", "hungry", "fed")
KINDS = ("shipped", "sent", "invoiced", "rested", "closed")
CELEBRATE_KINDS = ("shipped", "invoiced")
MILESTONES = (3, 7, 21)
CELEBRATE_FOR = timedelta(hours=1)
ACTIVE_WINDOW = timedelta(minutes=30)

DEFAULT_CONFIG = {
    "hunger_hours": 24,
    "sleepy_hours": 3,
    "quiet_hours": "23:00-07:00",
    "ledger": None,
    "open_items": None,
    "watch": "shipped",
    "style": None,
}

# Seven sprites, one per state. The ✧ in the mouth is her diamond grill. ∴ are her spots.
SPRITES = {
    "fed": "∴(=^･✧･^=)∴",
    "hungry": "∴(=°✧°=)っ",
    "sleepy": "∴(=-✧-=)ᶻ",
    "celebrating": "✧\\(=^✧^=)/✧",
    "worried": "∴(=ﾟ✧ﾟ;=)∴",
    "restless": "≋(=･✧･=)≋",
    "asleep": "∴(=_✧_=)zZ",
}
EGG = "(  ✧  )"


@dataclass
class Mood:
    state: str
    reason: str
    details: list = field(default_factory=list)

    @property
    def sprite(self) -> str:
        return SPRITES[self.state]


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def feed_times(state: dict) -> list:
    return sorted(parse_time(f["at"]) for f in state.get("feeds", []))


def streak(state: dict, now: datetime) -> int:
    """Consecutive local days with a feed, ending today (or yesterday if today is empty)."""
    days = {parse_time(f["at"]).astimezone(now.tzinfo).date() for f in state.get("feeds", [])}
    today = now.date()
    cursor = today if today in days else today - timedelta(days=1)
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


def milestone_for_new_feed(state: dict, now: datetime) -> int | None:
    """Called before a feed is stored. Returns 3, 7 or 21 if this feed reaches a milestone."""
    days = {parse_time(f["at"]).astimezone(now.tzinfo).date() for f in state.get("feeds", [])}
    if now.date() in days:
        return None  # only the first feed of a day can move the streak
    trial = {"feeds": list(state.get("feeds", [])) + [{"at": now.isoformat()}]}
    n = streak(trial, now)
    return n if n in MILESTONES else None


def hours_since_feed(state: dict, now: datetime) -> float | None:
    times = feed_times(state)
    if not times:
        return None
    return (now - times[-1]).total_seconds() / 3600


def hunger_percent(state: dict, config: dict, now: datetime) -> int:
    h = hours_since_feed(state, now)
    if h is None:
        return 100
    limit = float(config.get("hunger_hours") or DEFAULT_CONFIG["hunger_hours"])
    return max(0, min(100, int(round(h / limit * 100))))


def in_quiet_hours(quiet: str | None, now: datetime) -> bool:
    if not quiet:
        return False
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*", str(quiet))
    if not m:
        return False
    start = int(m.group(1)) * 60 + int(m.group(2))
    end = int(m.group(3)) * 60 + int(m.group(4))
    t = now.hour * 60 + now.minute
    if start == end:
        return False
    if start < end:
        return start <= t < end
    return t >= start or t < end  # wraps past midnight


def long_session_hours(state: dict, config: dict, now: datetime) -> float | None:
    """Length in hours of the longest active session over the sleepy limit, else None."""
    limit = float(config.get("sleepy_hours") or DEFAULT_CONFIG["sleepy_hours"])
    best = None
    for s in state.get("sessions", {}).values():
        if s.get("ended"):
            continue
        start, last = parse_time(s["start"]), parse_time(s.get("last") or s["start"])
        if now - last > ACTIVE_WINDOW:
            continue
        length = (now - start).total_seconds() / 3600
        if length >= limit and (best is None or length > best):
            best = length
    return best


def celebration(state: dict, now: datetime) -> str | None:
    for f in reversed(state.get("feeds", [])):
        age = now - parse_time(f["at"])
        if age < timedelta(0) or age > CELEBRATE_FOR:
            continue
        if f.get("milestone"):
            return f"{f['milestone']} day streak"
        if f.get("kind") in CELEBRATE_KINDS:
            return f"you {f['kind']}" + (f": {f['note']}" if f.get("note") else "")
    return None


def decide(state: dict, config: dict, now: datetime,
           failing_probes: list | None = None, due_items: list | None = None) -> Mood:
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    failing_probes = failing_probes or []
    due_items = due_items or []

    if in_quiet_hours(cfg.get("quiet_hours"), now):
        return Mood("asleep", f"quiet hours ({cfg['quiet_hours']})")
    if failing_probes:
        return Mood("worried", f"{len(failing_probes)} failing probe(s)",
                    list(failing_probes))
    why = celebration(state, now)
    if why:
        return Mood("celebrating", why)
    long_h = long_session_hours(state, cfg, now)
    if long_h is not None:
        return Mood("sleepy", f"session open {long_h:.1f}h")
    if due_items:
        return Mood("restless", f"{len(due_items)} open item(s) past their default", list(due_items))
    h = hours_since_feed(state, now)
    if h is None:
        return Mood("hungry", "she has not eaten yet")
    if h >= float(cfg["hunger_hours"]):
        return Mood("hungry", f"last meal {h:.0f}h ago")
    return Mood("fed", f"last meal {h:.1f}h ago" if h >= 1 else "just ate")


# ---------------------------------------------------------------- outside signals

FAIL_WORDS = {"fail", "failed", "failing", "red", "broken", "error"}


def _entry_fails(value) -> bool:
    if isinstance(value, bool):
        return value is False
    if isinstance(value, str):
        return value.strip().lower() in FAIL_WORDS
    if isinstance(value, dict):
        if "status" in value:
            return _entry_fails(value["status"])
        for key in ("ok", "pass", "passed"):
            if key in value:
                return value[key] is False
    return False


def failing_from_ledger(text: str) -> list:
    """Names of failing probes. Accepts JSON (list, {"probes": [...]}, or {name: status})
    or a plain log where lines read like "[time] FAIL name: ..." (the latest line per name wins)."""
    try:
        data = json.loads(text)
    except ValueError:
        latest = {}
        for line in text.splitlines():
            m = re.search(r"\b(PASS|FAIL)\b[\s:]+([A-Za-z0-9_.-]+)", line)
            if m:
                latest[m.group(2)] = m.group(1)
        return sorted(name for name, s in latest.items() if s == "FAIL")

    if isinstance(data, dict) and isinstance(data.get("failing"), list):
        # goal-tests ledger (claude-code-for-founders): {"version", "failing": [names],
        # "probes": {name: {"status": "pass"|"fail", ...}}, "runs", "last_run"}. "failing" is
        # the runner's verdict for the latest sweep, so it is the one we trust.
        return sorted(str(n) for n in data["failing"])
    if isinstance(data, dict):
        for key in ("probes", "goals", "results"):
            if key in data:
                data = data[key]
                break
    out = []
    if isinstance(data, list):
        for i, entry in enumerate(data):
            if _entry_fails(entry):
                name = entry.get("name") or entry.get("id") if isinstance(entry, dict) else None
                out.append(str(name or f"probe {i + 1}"))
    elif isinstance(data, dict):
        out = [str(k) for k, v in data.items() if _entry_fails(v)]
    return sorted(out)


DATE_RE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
DONE_RE = re.compile(r"~~|✅|\[x\]|\bDONE\b|\bCLOSED\b", re.IGNORECASE)


def due_open_items(text: str, today: date) -> list:
    """Open items whose default date has arrived. An item is a markdown table row or an
    unticked "- [ ]" line. It is due when any YYYY-MM-DD date in it is today or earlier.
    Struck-through, ticked or DONE rows are skipped."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        is_row = s.startswith("|") and not re.fullmatch(r"[|\s:-]+", s)
        is_todo = s.startswith("- [ ]")
        if not (is_row or is_todo) or DONE_RE.search(s):
            continue
        dates = []
        for d in DATE_RE.findall(s):
            try:
                dates.append(date.fromisoformat(d))
            except ValueError:
                continue
        if dates and min(dates) <= today:
            label = re.sub(r"\s+", " ", s.strip("|- []")).strip()
            out.append(label[:60])
    return out
