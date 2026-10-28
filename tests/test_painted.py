"""Painted Lucky: every mood renders as clean, shaded SVG in the style.json palette."""
import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import mood  # noqa: E402
import painted  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"


class Painted(unittest.TestCase):
    def test_same_moods_as_the_state_machine(self):
        self.assertEqual(set(painted.MOODS), set(mood.STATES))

    def test_every_mood_is_valid_svg(self):
        for m in painted.MOODS:
            with self.subTest(mood=m):
                root = ET.fromstring(painted.svg(m))
                self.assertEqual(root.get("viewBox"), "0 0 400 400")
                self.assertEqual(root.get("data-mood"), m)
                self.assertTrue(root.findall(f".//{NS}radialGradient"))      # soft shading, not flat clip art
                gems = [p for p in root.iter(f"{NS}path") if (p.get("fill") or "").startswith("url(#gem")]
                self.assertEqual(len(gems), 4)                              # four diamonds in the grill

    def test_no_pixels_no_glow(self):
        for m in painted.MOODS:
            s = painted.svg(m)
            for banned in ("feGaussianBlur", "<filter", "crispEdges", "drop-shadow"):
                self.assertNotIn(banned, s)

    def test_sparkles_only_when_celebrating(self):
        for m in painted.MOODS:
            has = 'class="glint' in painted.svg(m)
            self.assertEqual(has, m == "celebrating", m)

    def test_moods_look_different(self):
        self.assertEqual(len({painted.svg(m) for m in painted.MOODS}), 7)
        self.assertIn("Zz", painted.svg("asleep"))
        self.assertIn('stroke-width="28"', painted.svg("celebrating"))    # arms up

    def test_palette_retones_her(self):
        teal = painted.svg("fed", {"accent": "#0B7A75", "wine": "#222222"})
        self.assertIn("#0B7A75", teal.upper())
        self.assertIn("#222222", teal)
        self.assertNotIn("#FE9DCA", teal.upper())

    def test_ids_stay_unique_per_card(self):
        a, b = painted.svg("fed", uid="a"), painted.svg("fed", uid="b")
        self.assertIn('id="head-a"', a)
        self.assertIn('id="head-b"', b)


if __name__ == "__main__":
    unittest.main()
