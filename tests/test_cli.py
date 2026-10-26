"""CLI tests: hatch, feed, status, card, web, config, hooks, in a throwaway FAMILIAR_HOME."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CLI = os.path.join(ROOT, "familiar")


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {**os.environ, "FAMILIAR_HOME": self.tmp.name,
                    "FAMILIAR_NOW": "2026-10-26T14:00:00+08:00", "NO_COLOR": "1"}

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, stdin=""):
        return subprocess.run([sys.executable, CLI, *args], input=stdin, capture_output=True,
                              text=True, env=self.env, timeout=20)

    def state(self):
        with open(os.path.join(self.tmp.name, "state.json")) as fh:
            return json.load(fh)

    def test_full_loop(self):
        self.assertEqual(self.run_cli("status").returncode, 1)
        r = self.run_cli("hatch", "--name", "Lucky")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.run_cli("hatch").returncode, 1)  # no accidental re-hatch
        self.run_cli("config", "--quiet", "off")
        self.assertIn("hungry", self.run_cli("status").stdout)
        r = self.run_cli("feed", "invoiced", "brand", "day")
        self.assertIn("Invoiced", r.stdout)
        self.assertEqual(self.state()["feeds"][0]["note"], "brand day")
        self.assertIn("celebrating", self.run_cli("status").stdout)
        card = self.run_cli("card").stdout
        for word in ("GUEST CHECK", "INVOICED", "0 TOKENS", "THANK YOU!"):
            self.assertIn(word, card)
        out = os.path.join(self.tmp.name, "card.html")
        self.assertEqual(self.run_cli("web", "--no-open", "--out", out).returncode, 0)
        with open(out) as fh:
            html = fh.read()
        self.assertNotIn("/*__FAMILIAR_DATA__*/null", html)
        self.assertIn('"state": "celebrating"', html)

    def test_feed_rejects_unknown_kind(self):
        self.run_cli("hatch", "--name", "Lucky")
        self.assertNotEqual(self.run_cli("feed", "tokens").returncode, 0)

    def test_notes_cannot_break_out_of_the_page(self):
        self.run_cli("hatch", "--name", "Lucky")
        self.run_cli("feed", "shipped", "</script><img src=x onerror=alert(1)>")
        out = os.path.join(self.tmp.name, "card.html")
        self.run_cli("web", "--no-open", "--out", out)
        with open(out) as fh:
            self.assertNotIn("</script><img", fh.read())

    def test_config_signals(self):
        self.run_cli("hatch", "--name", "Lucky")
        self.run_cli("config", "--quiet", "off", "--ledger", os.path.join(ROOT, "examples", "ledger.example.json"))
        self.run_cli("feed", "sent")
        self.assertIn("worried", self.run_cli("status").stdout)
        self.run_cli("config", "--ledger", "off", "--open-items", os.path.join(ROOT, "examples", "open-items.example.md"))
        self.assertIn("restless", self.run_cli("status").stdout)
        self.assertEqual(self.run_cli("config", "--watch", "nonsense").returncode, 1)
        self.assertEqual(self.run_cli("config", "--quiet", "late").returncode, 1)

    def test_hooks_track_sessions(self):
        self.run_cli("hatch", "--name", "Lucky")
        r = self.run_cli("hook", "session-start", stdin='{"session_id":"s1","source":"startup"}')
        self.assertIn("Lucky", r.stdout)
        self.run_cli("hook", "stop", stdin='{"session_id":"s1","hook_event_name":"SessionEnd"}')
        self.assertTrue(self.state()["sessions"]["s1"]["ended"])
        self.assertEqual(self.run_cli("hook", "stop", stdin="not json").returncode, 0)


if __name__ == "__main__":
    unittest.main()
