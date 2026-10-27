"""Shared Rocha Coded style.json: one file styles every tool.

Lookup order, first file found wins:
  1. the path set with `familiar config --style PATH`
  2. ./style.json (the folder you are working in)
  3. ~/.rocha-coded/style.json
  4. examples/style.rocha-coded.json bundled here (Rocha's look, the house example)
Inheritance: when a user style.json is found, only blank or missing palette and fonts keys
fall back to the bundled example. Lines, owner, handle, name, references and notes never
borrow Rocha's words: a missing line stays blank and the card simply leaves it out. Her lines
appear only when the bundled example itself is the style in use. Colours must be hex
(#RGB or #RRGGBB) and font names plain letters, digits and spaces, or they fall back too.
The familiar's own name lives in her state, never in style.json.
"""
from __future__ import annotations

import json
import os
import re

HERE = os.path.dirname(os.path.realpath(__file__))
BUNDLED = os.path.join(HERE, "examples", "style.rocha-coded.json")
HEX = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}")
FONT = re.compile(r"[A-Za-z0-9 ]{1,48}")
TEXT_KEYS = ("name", "owner", "handle", "site", "motif", "notes")
MOTIFS = ("analog", "cyberpunk", "y2k-blog")
# Older motif names map to the nearest of the three families.
MOTIF_ALIASES = {"guest-check": "analog", "front-page": "analog", "magazine-scrawl": "analog",
                 "pink-paper": "analog", "rotary": "analog", "neutral": "analog",
                 "retro-tv": "cyberpunk", "leopard": "cyberpunk", "sticker-collage": "y2k-blog",
                 "y2k": "y2k-blog", "blog": "y2k-blog"}


def motif(value) -> str:
    """One of analog, cyberpunk, y2k-blog. Anything unknown is analog."""
    v = str(value or "").strip().lower()
    return v if v in MOTIFS else MOTIF_ALIASES.get(v, "analog")


def candidates(override: str | None = None, cwd: str | None = None) -> list:
    paths = []
    if override:
        paths.append(os.path.expanduser(override))
    paths.append(os.path.join(cwd or os.getcwd(), "style.json"))
    paths.append(os.path.expanduser("~/.rocha-coded/style.json"))
    paths.append(BUNDLED)
    return paths


def _read(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        return None


def merge(base: dict, user: dict) -> dict:
    out = {"palette": dict(base.get("palette", {})), "fonts": dict(base.get("fonts", {})),
           "lines": {}, "references": []}
    for key in TEXT_KEYS:
        out[key] = ""
    out["motif"] = base.get("motif", "neutral")
    for key in TEXT_KEYS:
        v = user.get(key)
        if isinstance(v, str) and v.strip():
            out[key] = v.strip()[:200]
    for group, rule in (("palette", HEX), ("fonts", FONT), ("lines", None)):
        given = user.get(group)
        if not isinstance(given, dict):
            continue
        for k, v in given.items():
            if not isinstance(v, str) or not v.strip():
                continue
            v = v.strip()
            if rule is None or rule.fullmatch(v):
                out.setdefault(group, {})[k] = v[:80]
    if isinstance(user.get("references"), list):
        out["references"] = [str(r)[:300] for r in user["references"]][:20]
    return out


def load(override: str | None = None, cwd: str | None = None) -> tuple:
    """Returns (style dict, path it came from)."""
    base = _read(BUNDLED) or {}
    for path in candidates(override, cwd):
        data = _read(path)
        if data is not None:
            if os.path.realpath(path) == os.path.realpath(BUNDLED):
                return base, path
            return merge(base, data), path
    return base, BUNDLED


def rgb(hex_colour: str) -> tuple:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
