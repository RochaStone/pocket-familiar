"""Painted Lucky: a soft-shaded SVG leopard (400 x 400) in seven moods.

Same mood state as the pixel Lucky. Shapes are filled and shaded with gentle gradients in the
style.json palette (fur = accent, rosettes = wine, shadows = plum, grill = gold, cream for the
muzzle and belly). No pixels, no outline-only clip art, no blur or glow filters.

  svg(mood, palette, uid="")  -> SVG markup (str). uid keeps gradient ids unique on one page.
"""
from __future__ import annotations

MOODS = ("fed", "celebrating", "sleepy", "asleep", "hungry", "worried", "restless")
DEFAULT = {"accent": "#FE9DCA", "wine": "#682047", "plum": "#50163C", "gold": "#E9B949",
           "paper": "#FFF7F4", "paper_pink": "#FFE3F1", "ink": "#3B1230", "marker": "#C2246E"}


def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a: str, b: str, t: float) -> str:
    """t=0 gives a, t=1 gives b."""
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def _star(x, y, s, fill, stroke, cls="glint"):
    k = s * .28
    return (f'<path class="{cls}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" d="M{x} {y - s}L{x + k} {y - k}L{x + s} {y}'
            f'L{x + k} {y + k}L{x} {y + s}L{x - k} {y + k}L{x - s} {y}L{x - k} {y - k}Z"/>')


def _rosette(x, y, r, rot, wine, centre, gap=70):
    """A leopard rosette: three or four short wine arcs around a slightly darker fur centre."""
    import math
    n = 4 if int(rot) % 3 else 3
    out = [f'<ellipse cx="{x}" cy="{y}" rx="{r * .6:.1f}" ry="{r * .5:.1f}" fill="{centre}"/>']
    span = 360 / n
    for k in range(n):
        a0 = math.radians(rot + k * span + 8)
        a1 = math.radians(rot + (k + 1) * span - 22)
        x1, y1 = x + r * math.cos(a0), y + r * .85 * math.sin(a0)
        x2, y2 = x + r * math.cos(a1), y + r * .85 * math.sin(a1)
        out.append(f'<path d="M{x1:.1f} {y1:.1f} A{r} {r * .85:.1f} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{wine}" '
                   f'stroke-width="{max(3.2, r * .5):.1f}" stroke-linecap="round"/>')
    return "".join(out)


def _eye(cx, cy, mood, p, u):
    ink, plum, paper = p["ink"], p["plum"], p["paper"]
    if mood == "fed":          # content: closed, smiling
        return f'<path d="M{cx - 16} {cy + 4} Q{cx} {cy - 12} {cx + 16} {cy + 4}" fill="none" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
    if mood == "asleep":       # closed, soft
        return (f'<path d="M{cx - 16} {cy - 2} Q{cx} {cy + 12} {cx + 16} {cy - 2}" fill="none" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
                f'<path d="M{cx - 14} {cy + 6} l-4 5 M{cx} {cy + 9} l0 6 M{cx + 14} {cy + 6} l4 5" stroke="{ink}" stroke-width="2.5" stroke-linecap="round"/>')
    big = mood in ("celebrating", "hungry")
    rx, ry = (19, 18) if big else (17, 16)
    if mood == "worried":
        rx, ry = 19, 20
    iris_r = {"worried": 7, "celebrating": 13, "hungry": 13}.get(mood, 12)
    dx = 6 if mood == "restless" else 0
    dy = -3 if mood == "hungry" else 0
    out = [f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{paper}"/>',
           f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{iris_r}" fill="url(#iris{u})"/>',
           f'<ellipse cx="{cx + dx}" cy="{cy + dy}" rx="{iris_r * .42:.1f}" ry="{iris_r * .75:.1f}" fill="{plum}"/>',
           f'<circle cx="{cx + dx - iris_r * .4:.1f}" cy="{cy + dy - iris_r * .45:.1f}" r="{max(2.5, iris_r * .32):.1f}" fill="#FFFFFF"/>']
    if big:
        out.append(f'<circle cx="{cx + dx + iris_r * .38:.1f}" cy="{cy + dy + iris_r * .4:.1f}" r="2" fill="#FFFFFF"/>')
    if mood in ("sleepy", "restless"):   # a heavy lid over the top half
        lid_y = cy - (2 if mood == "sleepy" else 6)
        out.append(f'<path d="M{cx - rx - 2} {lid_y} Q{cx} {cy - ry - 8} {cx + rx + 2} {lid_y} L{cx + rx + 2} {cy - ry - 4} L{cx - rx - 2} {cy - ry - 4}Z" fill="url(#head{u})"/>')
        out.append(f'<path d="M{cx - rx} {lid_y} Q{cx} {lid_y - 3} {cx + rx} {lid_y}" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
    else:
        out.append(f'<path d="M{cx - rx} {cy - 2} Q{cx} {cy - ry - 6} {cx + rx} {cy - 2}" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
    return "".join(out)


def svg(mood: str, palette: dict | None = None, uid: str = "") -> str:
    mood = mood if mood in MOODS else "fed"
    p = {**DEFAULT, **{k: v for k, v in (palette or {}).items() if k in DEFAULT and v}}
    if not (palette or {}).get("wine"):
        p["wine"] = p["plum"] if palette and palette.get("plum") else DEFAULT["wine"]
    u = f"-{uid}" if uid else f"-{mood}"
    fur, wine, plum, gold, paper, blush, ink = p["accent"], p["wine"], p["plum"], p["gold"], p["paper"], p["paper_pink"], p["ink"]
    light, shade = mix(fur, paper, .45), mix(fur, wine, .28)
    centre = mix(fur, wine, .18)
    up = mood == "celebrating"
    defs = f"""<defs>
<radialGradient id="head{u}" gradientUnits="userSpaceOnUse" cx="180" cy="120" r="150"><stop offset="0" stop-color="{light}"/><stop offset=".55" stop-color="{fur}"/><stop offset="1" stop-color="{shade}"/></radialGradient>
<radialGradient id="body{u}" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="{light}"/><stop offset=".5" stop-color="{fur}"/><stop offset="1" stop-color="{shade}"/></radialGradient>
<radialGradient id="belly{u}" cx="50%" cy="35%" r="70%"><stop offset="0" stop-color="{paper}"/><stop offset="1" stop-color="{blush}"/></radialGradient>
<linearGradient id="tail{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{fur}"/><stop offset="1" stop-color="{shade}"/></linearGradient>
<linearGradient id="gold{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mix(gold, paper, .45)}"/><stop offset=".5" stop-color="{gold}"/><stop offset="1" stop-color="{mix(gold, wine, .3)}"/></linearGradient>
<linearGradient id="gem{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="{blush}"/></linearGradient>
<radialGradient id="iris{u}" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="{mix(gold, paper, .3)}"/><stop offset=".7" stop-color="{gold}"/><stop offset="1" stop-color="{mix(gold, wine, .45)}"/></radialGradient>
<radialGradient id="ear{u}" cx="50%" cy="60%" r="60%"><stop offset="0" stop-color="{mix(wine, fur, .35)}"/><stop offset="1" stop-color="{wine}"/></radialGradient>
</defs>"""
    parts = [defs, f'<ellipse cx="200" cy="374" rx="128" ry="14" fill="{plum}" opacity=".18"/>']

    # tail: curled around the side (her signature), flicked up when restless
    tail = ("M268 336 C340 330 378 268 356 206 C348 184 322 190 328 210" if mood == "restless"
            else "M266 340 C336 350 366 304 346 258 C336 234 308 240 314 262")
    parts.append(f'<path d="{tail}" fill="none" stroke="url(#tail{u})" stroke-width="26" stroke-linecap="round"/>')
    tip = (328, 210) if mood == "restless" else (314, 262)
    parts.append(f'<circle cx="{tip[0]}" cy="{tip[1]}" r="12" fill="{wine}"/>')
    for tx, ty in ((320, 340), (348, 300)) if mood != "restless" else ((330, 320), (362, 262)):
        parts.append(f'<ellipse cx="{tx}" cy="{ty}" rx="7" ry="5" fill="{wine}"/>')
    if mood == "restless":   # two small motion arcs by the tail
        parts.append(f'<path d="M372 186 q12 6 10 20 M384 172 q14 8 12 26" fill="none" stroke="{plum}" stroke-width="3" stroke-linecap="round" opacity=".55"/>')

    # haunches, body, belly
    parts += [f'<ellipse cx="136" cy="344" rx="44" ry="28" fill="url(#body{u})"/>',
              f'<ellipse cx="264" cy="344" rx="44" ry="28" fill="url(#body{u})"/>',
              f'<path d="M200 205 C266 205 292 270 290 320 C288 356 256 372 200 372 C144 372 112 356 110 320 C108 270 134 205 200 205Z" fill="url(#body{u})"/>',
              f'<ellipse cx="200" cy="318" rx="50" ry="52" fill="url(#belly{u})"/>']
    for (x, y, r, rot) in ((146, 252, 13, 20), (256, 246, 12, 200), (134, 300, 12, 110), (268, 302, 13, 300),
                           (124, 344, 10, 60), (278, 342, 11, 240), (200, 238, 9, 150)):
        parts.append(_rosette(x, y, r, rot, wine, centre))

    # arms: down with paws, or up in the air
    if not up:
        for x in (160, 210):
            parts.append(f'<rect x="{x}" y="296" width="30" height="72" rx="15" fill="url(#body{u})"/>')
            parts.append(f'<ellipse cx="{x + 15}" cy="366" rx="21" ry="11" fill="{light}"/>')
            parts.append(f'<path d="M{x + 8} 362 v6 M{x + 15} 361 v7 M{x + 22} 362 v6" stroke="{wine}" stroke-width="2.5" stroke-linecap="round" opacity=".55"/>')

    # ears, head, cheek fluff
    parts += [f'<ellipse cx="126" cy="90" rx="30" ry="34" transform="rotate(-22 126 90)" fill="url(#head{u})"/>',
              f'<ellipse cx="274" cy="90" rx="30" ry="34" transform="rotate(22 274 90)" fill="url(#head{u})"/>',
              f'<ellipse cx="129" cy="95" rx="15" ry="20" transform="rotate(-22 129 95)" fill="url(#ear{u})"/>',
              f'<ellipse cx="271" cy="95" rx="15" ry="20" transform="rotate(22 271 95)" fill="url(#ear{u})"/>',
              f'<ellipse cx="200" cy="160" rx="100" ry="86" fill="url(#head{u})"/>',
              f'<ellipse cx="114" cy="188" rx="30" ry="24" fill="url(#head{u})"/>',
              f'<ellipse cx="286" cy="188" rx="30" ry="24" fill="url(#head{u})"/>']
    for (x, y, r, rot) in ((146, 108, 11, 30), (254, 106, 11, 210), (118, 160, 10, 80), (284, 158, 10, 260),
                           (200, 96, 8, 120), (178, 82, 6, 0), (222, 82, 6, 180)):
        parts.append(_rosette(x, y, r, rot, wine, centre))

    if up:   # arms up in the air, drawn over the cheeks so her paws show
        for sx, hx in ((150, 66), (250, 334)):
            parts.append(f'<path d="M{sx} 262 Q{(sx + hx) / 2:.0f} 236 {hx} 128" fill="none" stroke="url(#tail{u})" stroke-width="28" stroke-linecap="round"/>')
            parts.append(f'<circle cx="{hx}" cy="122" r="19" fill="{light}"/>')
            parts.append(f'<path d="M{hx - 8} 114 v6 M{hx} 111 v7 M{hx + 8} 114 v6" stroke="{wine}" stroke-width="2.5" stroke-linecap="round" opacity=".6"/>')

    # brows for the feelings that need them
    if mood == "worried":
        parts.append(f'<path d="M140 118 Q156 108 172 116 M228 116 Q244 108 260 118" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
    if mood == "hungry":
        parts.append(f'<path d="M142 120 Q158 112 174 120 M226 120 Q242 112 258 120" fill="none" stroke="{ink}" stroke-width="3.5" stroke-linecap="round"/>')
    parts.append(_eye(160, 150, mood, p, u))
    parts.append(_eye(240, 150, mood, p, u))

    # muzzle, nose, whiskers
    parts += [f'<ellipse cx="183" cy="198" rx="27" ry="21" fill="url(#belly{u})"/>',
              f'<ellipse cx="217" cy="198" rx="27" ry="21" fill="url(#belly{u})"/>',
              f'<path d="M187 177 Q200 170 213 177 Q207 191 200 193 Q193 191 187 177Z" fill="{plum}"/>',
              f'<ellipse cx="196" cy="178" rx="4" ry="2.5" fill="#FFFFFF" opacity=".5"/>']
    for side in (-1, 1):
        x0 = 200 + side * 34
        parts.append(f'<path d="M{x0} 196 l{side * 44} -8 M{x0} 203 l{side * 46} 2 M{x0} 210 l{side * 40} 12" '
                     f'stroke="{plum}" stroke-width="2" stroke-linecap="round" opacity=".45"/>')

    # mouth and the grill: four diamonds set in gold
    if mood == "hungry":
        parts.append(f'<path d="M176 203 Q200 252 224 203Z" fill="{plum}"/>')
        parts.append(f'<ellipse cx="200" cy="232" rx="13" ry="8" fill="{p["marker"]}"/>')
    elif mood == "worried":
        parts.append(f'<path d="M178 203 Q200 214 222 203 L222 213 Q200 222 178 213Z" fill="{plum}"/>')
    elif mood in ("asleep", "sleepy"):
        parts.append(f'<path d="M184 203 Q200 216 216 203Z" fill="{plum}"/>')
    else:
        parts.append(f'<path d="M176 203 Q200 230 224 203Z" fill="{plum}"/>')
    gx0, gw = (184, 32) if mood in ("asleep", "sleepy") else (180, 40)
    parts.append(f'<rect x="{gx0}" y="202" width="{gw}" height="11" rx="5" fill="url(#gold{u})"/>')
    for i in range(4):
        cx = gx0 + gw * (i + .5) / 4
        parts.append(f'<path d="M{cx:.1f} 203.5 L{cx + 3.6:.1f} 207.5 L{cx:.1f} 211.5 L{cx - 3.6:.1f} 207.5Z" fill="url(#gem{u})" stroke="{mix(gold, wine, .3)}" stroke-width=".8"/>')
    parts.append(f'<circle cx="{gx0 + 6}" cy="205" r="1.6" fill="#FFFFFF"/>')   # the grill's shine

    # mood extras
    if mood in ("sleepy", "asleep"):
        z = "Zz" if mood == "asleep" else "z"
        parts.append(f'<text x="300" y="72" font-family="Fraunces, Georgia, serif" font-weight="900" font-size="{40 if mood == "asleep" else 30}" fill="{plum}" opacity=".85">{z}</text>')
    if mood == "worried":
        parts.append(f'<path d="M300 104 Q288 126 300 134 Q312 126 300 104Z" fill="{paper}" stroke="{plum}" stroke-width="2.5"/>'
                     f'<ellipse cx="297" cy="124" rx="2.5" ry="4" fill="#FFFFFF"/>')
    if up:   # twinkles and fairy dust: celebrations only
        for x, y, s in ((40, 70, 13), (360, 66, 15), (366, 214, 10), (34, 210, 9), (200, 36, 11), (300, 34, 7), (104, 40, 8)):
            parts.append(_star(x, y, s, mix(gold, paper, .35), gold))
        parts.append(_star(gx0 + 10, 207, 7, "#FFFFFF", gold, "glint grill"))
    return (f'<svg class="painted-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400" '
            f'role="img" aria-label="Painted Lucky, {mood}" data-mood="{mood}">' + "".join(parts) + "</svg>")
