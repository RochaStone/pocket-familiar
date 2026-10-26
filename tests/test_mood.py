"""State machine tests: every state, the precedence, streaks, and the outside signals.
Run: python3 -m unittest discover -s tests -v
"""
import os
import sys
import unittest
from datetime import date, datetime, timedelta, timezone

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import mood  # noqa: E402

TZ = timezone(timedelta(hours=8))
NOW = datetime(2026, 10, 26, 14, 0, tzinfo=TZ)
OFF = {"quiet_hours": None}


def feed(hours_ago, kind="sent", **extra):
    return {"at": (NOW - timedelta(hours=hours_ago)).isoformat(), "kind": kind, **extra}


def session(start_h_ago, last_min_ago=1, ended=None):
    return {"start": (NOW - timedelta(hours=start_h_ago)).isoformat(),
            "last": (NOW - timedelta(minutes=last_min_ago)).isoformat(), "ended": ended}


def st(feeds=(), sessions=None):
    return {"name": "Lucky", "feeds": list(feeds), "sessions": sessions or {}}


class EachState(unittest.TestCase):
    def test_fed(self):
        self.assertEqual(mood.decide(st([feed(2)]), OFF, NOW).state, "fed")

    def test_hungry_never_fed(self):
        self.assertEqual(mood.decide(st(), OFF, NOW).state, "hungry")

    def test_hungry_after_limit(self):
        self.assertEqual(mood.decide(st([feed(25)]), OFF, NOW).state, "hungry")
        self.assertEqual(mood.decide(st([feed(23)]), OFF, NOW).state, "fed")

    def test_hunger_hours_configurable(self):
        self.assertEqual(mood.decide(st([feed(5)]), {**OFF, "hunger_hours": 4}, NOW).state, "hungry")

    def test_celebrating_shipped_and_invoiced(self):
        for kind in ("shipped", "invoiced"):
            self.assertEqual(mood.decide(st([feed(0.5, kind)]), OFF, NOW).state, "celebrating")

    def test_celebration_lasts_one_hour(self):
        self.assertEqual(mood.decide(st([feed(1.2, "shipped")]), OFF, NOW).state, "fed")

    def test_other_kinds_do_not_celebrate(self):
        for kind in ("sent", "rested", "closed"):
            self.assertEqual(mood.decide(st([feed(0.2, kind)]), OFF, NOW).state, "fed")

    def test_celebrating_on_milestone(self):
        m = mood.decide(st([feed(0.2, "rested", milestone=3)]), OFF, NOW)
        self.assertEqual((m.state, m.reason), ("celebrating", "3 day streak"))

    def test_sleepy(self):
        self.assertEqual(mood.decide(st([feed(1)], {"a": session(3.5)}), OFF, NOW).state, "sleepy")

    def test_not_sleepy_short_idle_or_ended(self):
        for s in (session(2), session(5, last_min_ago=45), session(5, ended=NOW.isoformat())):
            self.assertEqual(mood.decide(st([feed(1)], {"a": s}), OFF, NOW).state, "fed")

    def test_worried(self):
        m = mood.decide(st([feed(1)]), OFF, NOW, failing_probes=["signup"])
        self.assertEqual(m.state, "worried")
        self.assertIn("signup", m.details)

    def test_restless(self):
        self.assertEqual(mood.decide(st([feed(1)]), OFF, NOW, due_items=["x"]).state, "restless")

    def test_asleep(self):
        late = NOW.replace(hour=23, minute=30)
        self.assertEqual(mood.decide(st([feed(1)]), {"quiet_hours": "23:00-07:00"}, late).state, "asleep")
        self.assertEqual(mood.decide(st([feed(1)]), {"quiet_hours": "23:00-07:00"}, NOW).state, "fed")

    def test_default_quiet_hours_on(self):
        self.assertEqual(mood.decide(st([feed(1)]), {}, NOW.replace(hour=3)).state, "asleep")


class Precedence(unittest.TestCase):
    """asleep > worried > celebrating > sleepy > restless > hungry > fed"""

    def everything(self):
        return st([feed(30), feed(0.3, "shipped")], {"a": session(4)})

    def test_order(self):
        s, late = self.everything(), NOW.replace(hour=23, minute=10)
        q = {"quiet_hours": "23:00-07:00"}
        self.assertEqual(mood.decide(s, q, late, ["p"], ["i"]).state, "asleep")
        self.assertEqual(mood.decide(s, OFF, NOW, ["p"], ["i"]).state, "worried")
        self.assertEqual(mood.decide(s, OFF, NOW, [], ["i"]).state, "celebrating")
        no_party = st([feed(30)], {"a": session(4)})
        self.assertEqual(mood.decide(no_party, OFF, NOW, [], ["i"]).state, "sleepy")
        self.assertEqual(mood.decide(st([feed(30)]), OFF, NOW, [], ["i"]).state, "restless")
        self.assertEqual(mood.decide(st([feed(30)]), OFF, NOW).state, "hungry")
        self.assertEqual(mood.decide(st([feed(3)]), OFF, NOW).state, "fed")

    def test_exactly_one_state_and_a_sprite_each(self):
        self.assertEqual(set(mood.SPRITES), set(mood.STATES))
        for sprite in mood.SPRITES.values():
            self.assertIn("✧", sprite)


class Streaks(unittest.TestCase):
    def days(self, *offsets):
        return st([feed(24 * d + 1) for d in offsets])

    def test_streak_counts_back(self):
        self.assertEqual(mood.streak(self.days(0, 1, 2), NOW), 3)

    def test_streak_alive_from_yesterday(self):
        self.assertEqual(mood.streak(self.days(1, 2), NOW), 2)

    def test_streak_broken(self):
        self.assertEqual(mood.streak(self.days(2, 3), NOW), 0)
        self.assertEqual(mood.streak(self.days(0, 2), NOW), 1)

    def test_milestones(self):
        self.assertEqual(mood.milestone_for_new_feed(self.days(1, 2), NOW), 3)
        self.assertEqual(mood.milestone_for_new_feed(self.days(*range(1, 7)), NOW), 7)
        self.assertEqual(mood.milestone_for_new_feed(self.days(*range(1, 21)), NOW), 21)
        self.assertIsNone(mood.milestone_for_new_feed(self.days(1), NOW))
        self.assertIsNone(mood.milestone_for_new_feed(self.days(0, 1, 2), NOW))  # second feed today

    def test_quiet_hours_parse(self):
        self.assertTrue(mood.in_quiet_hours("22:00-02:00", NOW.replace(hour=1)))
        self.assertFalse(mood.in_quiet_hours("garbage", NOW))
        self.assertTrue(mood.in_quiet_hours("13:00-15:00", NOW))


class Signals(unittest.TestCase):
    def test_ledger_shapes(self):
        self.assertEqual(mood.failing_from_ledger('{"probes":[{"name":"a","status":"pass"},{"name":"b","status":"FAIL"}]}'), ["b"])
        self.assertEqual(mood.failing_from_ledger('{"a":"pass","b":{"ok":false}}'), ["b"])
        self.assertEqual(mood.failing_from_ledger('[{"id":"x","passed":false}]'), ["x"])
        self.assertEqual(mood.failing_from_ledger('{"all":"good"}'), [])

    def test_goal_tests_ledger_exact_shape(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
        with open(os.path.join(root, "goal-tests-ledger.json")) as fh:
            self.assertEqual(mood.failing_from_ledger(fh.read()), ["newsletter-signup"])
        fresh = '{"version": 1, "failing": [], "probes": {}, "runs": []}'
        self.assertEqual(mood.failing_from_ledger(fresh), [])

    def test_goal_tests_real_sample_and_staleness(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
        with open(os.path.join(root, "goal-tests-ledger.real.json")) as fh:
            text = fh.read()
        fresh = datetime(2026, 10, 26, 16, 0, tzinfo=TZ)
        self.assertEqual(mood.failing_from_ledger(text, fresh), ["offer-page"])
        self.assertEqual(mood.failing_from_ledger(text, fresh + timedelta(hours=27)), [])  # sweep stopped: unknown
        self.assertEqual(mood.failing_from_ledger(text), ["offer-page"])  # no clock given: trust the list
        skipped = text.replace('"version": 1,', '"version": 1, "last_skipped": {"at": "2026-10-26T15:40:00", "reason": "offline"},')
        self.assertEqual(mood.failing_from_ledger(skipped, fresh), ["offer-page"])

    def test_ledger_log_latest_wins(self):
        log = "[t1] FAIL signup: broke\n[t1] FAIL booking rc=1\n[t2] PASS booking: ok\n"
        self.assertEqual(mood.failing_from_ledger(log), ["signup"])

    def test_example_files(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples")
        with open(os.path.join(root, "ledger.example.json")) as fh:
            self.assertEqual(mood.failing_from_ledger(fh.read()), ["newsletter-signup"])
        with open(os.path.join(root, "open-items.example.md")) as fh:
            due = mood.due_open_items(fh.read(), date(2026, 10, 26))
        self.assertEqual(len(due), 2)  # cover (24 Oct) and welcome email (25 Oct); venue is 2 Nov
        self.assertTrue(any("cover" in d for d in due))

    def test_open_items_skips_done(self):
        text = "| 1 | ~~old~~ 2026-01-01 |\n- [x] done 2026-01-01\n| 2 | DONE 2026-01-01 |\n|---|---|\n"
        self.assertEqual(mood.due_open_items(text, date(2026, 10, 26)), [])


if __name__ == "__main__":
    unittest.main()
