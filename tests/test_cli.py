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
                    "FAMILIAR_NOW": "2026-10-26T14:00:00+08:00", "NO_COLOR": "1",
                    "HOME": self.tmp.name}  # never sees a real goal-tests install or style
        self.env.pop("GOAL_TESTS_HOME", None)

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

    def test_goal_tests_found_on_its_own(self):
        gt = os.path.join(self.tmp.name, "gt")
        os.makedirs(gt)
        with open(os.path.join(ROOT, "tests", "fixtures", "goal-tests-ledger.real.json")) as src, \
                open(os.path.join(gt, "ledger.json"), "w") as dst:
            dst.write(src.read())
        self.env["GOAL_TESTS_HOME"] = gt
        self.env["FAMILIAR_NOW"] = "2026-10-26T16:00:00+08:00"
        self.run_cli("hatch", "--name", "Lucky")
        self.run_cli("config", "--quiet", "off")
        self.run_cli("feed", "sent")
        status = self.run_cli("status").stdout
        self.assertIn("worried", status)
        self.assertIn("offer-page", status)
        self.run_cli("config", "--ledger", "off")
        self.assertNotIn("worried", self.run_cli("status").stdout)
        self.assertIn("ledger        auto", self.run_cli("config", "--ledger", "auto").stdout)
        os.remove(os.path.join(gt, "ledger.json"))  # not installed: no worry
        self.assertNotIn("worried", self.run_cli("status").stdout)

    def test_hooks_track_sessions(self):
        self.run_cli("hatch", "--name", "Lucky")
        r = self.run_cli("hook", "session-start", stdin='{"session_id":"s1","source":"startup"}')
        self.assertIn("Lucky", r.stdout)
        self.run_cli("hook", "stop", stdin='{"session_id":"s1","hook_event_name":"SessionEnd"}')
        self.assertTrue(self.state()["sessions"]["s1"]["ended"])
        self.assertEqual(self.run_cli("hook", "stop", stdin="not json").returncode, 0)


    def test_second_style_changes_card(self):
        self.run_cli("hatch", "--name", "Lucky")
        self.run_cli("config", "--quiet", "off")
        self.run_cli("feed", "shipped", "the newsletter")
        house = os.path.join(self.tmp.name, "house.html")
        self.run_cli("web", "--no-open", "--out", house)
        second = os.path.join(ROOT, "tests", "fixtures", "style.second.json")
        r = self.run_cli("config", "--style", second)
        self.assertIn("style.second.json", r.stdout)
        mine = os.path.join(self.tmp.name, "mine.html")
        self.run_cli("web", "--no-open", "--out", mine)
        with open(house) as fh:
            a = fh.read()
        with open(mine) as fh:
            b = fh.read()
        self.assertIn('"hero": "#50163C"', a)
        self.assertIn('"celebrate": "I AM SO LUCKY"', a)
        self.assertIn('"hero": "#0B7A75"', b)
        self.assertIn('"celebrate": "SHE PURRS FOR ME"', b)
        self.assertIn('"plum": "#50163C"', b)  # blank keys fall back key by key
        card = self.run_cli("card").stdout
        self.assertIn("SHE PURRS FOR ME", card)
        self.assertIn("TO DO: TEST LINE", card)
        self.assertNotIn("I AM SO LUCKY", card)
        env = {**self.env, "FAMILIAR_COLOR": "1"}
        env.pop("NO_COLOR")
        coloured = subprocess.run([sys.executable, CLI, "status"], capture_output=True, text=True, env=env).stdout
        self.assertIn("38;2;159;226;221", coloured)  # accent #9FE2DD in the terminal too

    def test_user_style_never_borrows_her_words(self):
        mine = os.path.join(self.tmp.name, "style.json")
        with open(mine, "w") as fh:
            json.dump({"palette": {"hero": "#0B7A75"}}, fh)  # colours only, no lines, no owner
        self.run_cli("hatch", "--name", "Lucky")
        self.run_cli("config", "--quiet", "off", "--style", mine)
        self.run_cli("feed", "shipped", "the newsletter")
        out = os.path.join(self.tmp.name, "c.html")
        self.run_cli("web", "--no-open", "--out", out)
        with open(out) as fh:
            html = fh.read()
        self.assertIn('"hero": "#0B7A75"', html)
        self.assertIn('"plum": "#50163C"', html)              # palette may fall back
        self.assertIn('"masthead": "Fraunces"', html)  # fonts may fall back
        for hers in ("I AM SO LUCKY", "EVERYTHING WORKS OUT", "BUILD YOUR FOUNDER WORLD", "Rocha", "@rocheverse"):
            self.assertNotIn(hers, html.split("const DATA")[1].split("const SAMPLE")[0])
        card = self.run_cli("card").stdout
        for hers in ("I AM SO LUCKY", "BUILD YOUR FOUNDER WORLD"):
            self.assertNotIn(hers, card)
        self.assertIn("GUEST CHECK", card)

    def test_bad_style_values_fall_back(self):
        bad = os.path.join(self.tmp.name, "style.json")
        with open(bad, "w") as fh:
            json.dump({"palette": {"hero": "red;}</style><script>"}, "fonts": {"body": "x\"><script>"}}, fh)
        self.run_cli("hatch", "--name", "Lucky")
        self.run_cli("config", "--style", bad)
        out = os.path.join(self.tmp.name, "c.html")
        self.run_cli("web", "--no-open", "--out", out)
        with open(out) as fh:
            html = fh.read()
        self.assertIn('"hero": "#50163C"', html)
        self.assertNotIn("<script>\"", html)


if __name__ == "__main__":
    unittest.main()
