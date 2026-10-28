"""The web card in all three motifs: one render path, three structures.
The browser checks render each motif in headless Chrome at phone width (390px) and read the
finished page. They are skipped, not failed, when Chrome is not installed."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import style  # noqa: E402

CLI = os.path.join(ROOT, "familiar")
MARKERS = {"analog": "Guest Check", "cyberpunk": "rocheverse:~$", "y2k-blog": "you are visitor no."}


def chrome():
    for c in (os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")):
        if c and os.path.exists(c):
            return c
    return None


class Motifs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {**os.environ, "HOME": self.tmp.name, "FAMILIAR_HOME": os.path.join(self.tmp.name, "f"),
                    "FAMILIAR_NOW": "2026-10-23T16:20:00+08:00", "NO_COLOR": "1"}
        self.env.pop("GOAL_TESTS_HOME", None)
        os.makedirs(self.env["FAMILIAR_HOME"])
        shutil.copy(os.path.join(ROOT, "examples", "sample-state.json"), os.path.join(self.env["FAMILIAR_HOME"], "state.json"))
        shutil.copy(os.path.join(ROOT, "examples", "sample-config.json"), os.path.join(self.env["FAMILIAR_HOME"], "config.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def web(self, *extra):
        out = os.path.join(self.tmp.name, "card-" + "-".join(extra or ("default",)) + ".html")
        r = subprocess.run([sys.executable, CLI, "web", "--no-open", "--out", out, *extra],
                           capture_output=True, text=True, env=self.env, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out) as fh:
            return out, fh.read()

    def test_motif_flag_and_default(self):
        _, html = self.web()
        self.assertIn('"motif": "analog"', html)   # the bundled style says analog
        for m in MARKERS:
            _, html = self.web("--motif", m)
            self.assertIn(f'"motif": "{m}"', html)
            self.assertNotIn("/*__FAMILIAR_JS__*/", html)
            self.assertNotIn("/*__MOTIFS_CSS__*/", html)

    def test_old_motif_names_map_to_a_family(self):
        self.assertEqual(style.motif("guest-check"), "analog")
        self.assertEqual(style.motif("retro-tv"), "cyberpunk")
        self.assertEqual(style.motif("sticker-collage"), "y2k-blog")
        self.assertEqual(style.motif("something else"), "analog")
        self.assertEqual(style.motif("Y2K-BLOG"), "y2k-blog")

    @unittest.skipUnless(chrome(), "headless Chrome not installed")
    def test_each_motif_renders_its_signature_at_phone_width(self):
        for m, marker in MARKERS.items():
            path, _ = self.web("--motif", m)
            dom = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--dump-dom", "--window-size=390,900",
                                  "--virtual-time-budget=4000", "file://" + path],
                                 capture_output=True, text=True, timeout=90).stdout
            with self.subTest(motif=m):
                self.assertIn(f'data-motif="{m}"', dom)
                self.assertIn('data-rendered="ok"', dom)
                self.assertIn(marker, dom)
                self.assertIn('data-overflow="no"', dom)   # no sideways scroll at 390px
                if m == "cyberpunk":
                    self.assertIn("Pixel leopard", dom)       # cyberpunk keeps the pixel Lucky
                else:
                    self.assertIn("Painted Lucky", dom)       # analog and y2k-blog use the painted Lucky


    @unittest.skipUnless(chrome(), "headless Chrome not installed")
    def test_every_mood_draws_in_pixel(self):
        path, html = self.web("--motif", "cyberpunk")
        moods = ["fed", "celebrating", "sleepy", "asleep", "hungry", "worried", "restless"]
        harness = path.replace(".html", "-moods.html")
        with open(harness, "w") as fh:   # draw all seven pixel moods on one page, then read it back
            fh.write(html.replace("</body>", "<script>document.body.insertAdjacentHTML('beforeend', "
                                  + repr(moods).replace("'", '"') + ".map(petSvg).join(''));</script></body>", 1))
        dom = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--dump-dom", "--virtual-time-budget=3000",
                              "file://" + harness], capture_output=True, text=True, timeout=90).stdout
        for mood in moods:
            with self.subTest(mood=mood):
                self.assertIn(f'aria-label="Pixel leopard, {mood}"', dom)


if __name__ == "__main__":
    unittest.main()
