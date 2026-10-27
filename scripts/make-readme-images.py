#!/usr/bin/env python3
"""Makes every image in the README from the tool itself.

  python3 scripts/make-readme-images.py

Renders the sample week (examples/sample-state.json) with Rocha's bundled style in all three
motifs, then uses headless Chrome to take:
  docs/img/hero.png       the y2k-blog window (README hero)
  docs/img/triptych.png   analog | cyberpunk | y2k-blog side by side
and writes the tiny pixel SVGs: docs/img/step-01.svg ... step-05.svg, divider.svg, heart.svg.
Set CHROME to your Chrome or Chromium path if it is not found on its own.
"""
import html
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs", "img")
NOW = "2026-10-23T16:20:00+08:00"
MOTIFS = ("analog", "cyberpunk", "y2k-blog")
PLUM, CANDY, GOLD = "#50163C", "#FE9DCA", "#E9B949"

DIGITS = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
          "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
          "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"]}


def find_chrome():
    for c in (os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")):
        if c and os.path.exists(c):
            return c
    sys.exit("Chrome or Chromium is needed for the PNGs. Set CHROME=/path/to/chrome and run again.")


def badge(n):
    """A pixel step badge: candy digits on a plum tile, 3px pixels."""
    text = f"{n:02d}"
    rects = []
    for i, ch in enumerate(text):
        for y, row in enumerate(DIGITS[ch]):
            for x, bit in enumerate(row):
                if bit == "1":
                    rects.append(f'<rect x="{2 + i * 4 + x}" y="{2 + y}" width="1" height="1"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="33" height="27" viewBox="0 0 11 9" shape-rendering="crispEdges">'
            f'<rect width="11" height="9" fill="{PLUM}"/><g fill="{CANDY}">{"".join(rects)}</g></svg>\n')


def divider():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="6" viewBox="0 0 360 6" shape-rendering="crispEdges">'
            f'<defs><pattern id="p" width="8" height="6" patternUnits="userSpaceOnUse"><rect y="2" width="4" height="2" fill="{GOLD}"/></pattern></defs>'
            f'<rect width="360" height="6" fill="url(#p)"/></svg>\n')


def heart():
    rows = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, r in enumerate(rows) for x, b in enumerate(r) if b == "1")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="21" height="18" viewBox="0 0 7 6" shape-rendering="crispEdges">'
            f'<g fill="{GOLD}">{rects}</g></svg>\n')


def shot(chrome, page, png, w, h):
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size={w},{h}", "--virtual-time-budget=8000", f"--screenshot={png}", "file://" + page],
                   check=True, capture_output=True, timeout=120)


def main():
    os.makedirs(OUT, exist_ok=True)
    for n in range(1, 6):
        with open(os.path.join(OUT, f"step-{n:02d}.svg"), "w") as fh:
            fh.write(badge(n))
    with open(os.path.join(OUT, "divider.svg"), "w") as fh:
        fh.write(divider())
    with open(os.path.join(OUT, "heart.svg"), "w") as fh:
        fh.write(heart())

    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        fhome = os.path.join(tmp, "familiar")
        os.makedirs(fhome)
        shutil.copy(os.path.join(ROOT, "examples", "sample-state.json"), os.path.join(fhome, "state.json"))
        shutil.copy(os.path.join(ROOT, "examples", "sample-config.json"), os.path.join(fhome, "config.json"))
        # A clean HOME, so the bundled style is used and no real install leaks in.
        env = {**os.environ, "HOME": tmp, "FAMILIAR_HOME": fhome, "FAMILIAR_NOW": NOW}
        env.pop("GOAL_TESTS_HOME", None)
        pages = {}
        for m in MOTIFS:
            pages[m] = os.path.join(tmp, f"{m}.html")
            subprocess.run([sys.executable, os.path.join(ROOT, "familiar"), "web", "--no-open", "--motif", m,
                            "--out", pages[m]], check=True, env=env, cwd=tmp, capture_output=True)
        shot(chrome, pages["y2k-blog"], os.path.join(OUT, "hero.png"), 860, 860)

        frames = []
        for m in MOTIFS:
            with open(pages[m], encoding="utf-8") as fh:
                doc = html.escape(fh.read(), quote=True)
            frames.append(f'<figure><div class="clip"><iframe srcdoc="{doc}"></iframe></div><figcaption>{m}</figcaption></figure>')
        strip = os.path.join(tmp, "triptych.html")
        with open(strip, "w", encoding="utf-8") as fh:
            fh.write(f"""<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Silkscreen&display=swap" rel="stylesheet">
<style>
body {{ margin: 0; background: {PLUM}; display: flex; gap: 18px; padding: 18px; }}
figure {{ margin: 0; }}
.clip {{ width: 202px; height: 470px; overflow: hidden; border-radius: 6px; }}
iframe {{ width: 480px; height: 1120px; border: 0; transform: scale(.42); transform-origin: 0 0; }}
figcaption {{ font-family: Silkscreen, monospace; color: #FFF7F4; font-size: 13px; text-align: center; margin-top: 8px; }}
</style>{''.join(frames)}""")
        shot(chrome, strip, os.path.join(OUT, "triptych.png"), 696, 534)
    for name in sorted(os.listdir(OUT)):
        print(f"  docs/img/{name}  {os.path.getsize(os.path.join(OUT, name))} bytes")


if __name__ == "__main__":
    main()
