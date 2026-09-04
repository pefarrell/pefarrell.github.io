#!/usr/bin/env python3
"""Make square, face-centred thumbnails for the photos on people.md.

The full-resolution photo stays in images/ (the thumbnail links to it); this
writes a 1:1 crop to images/thumbs/, framed the same way for everyone: the
crop is a fixed multiple of the detected face height, centred on the face, with
the eyes on a constant line.  Faces are found with the macOS Vision framework
via scripts/facebox.swift.

Usage:
    scripts/make_thumbnails.py              # regenerate any that are missing or stale
    scripts/make_thumbnails.py --force      # regenerate all of them
    scripts/make_thumbnails.py images/x.jpg # just these
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUMBS = ROOT / "images" / "thumbs"
SIZE = 480          # pixels; displayed at 120, so still crisp on retina screens

# Framing.  Everything is measured in eye-to-chin distances, which is far
# steadier across people than the detected face box (that grows with beards and
# with pose).  The crop is CROP_SCALE of those; the head, taken to run from
# HAIR above the eyes down to the chin, is centred at HEAD_CENTRE of the crop.
CROP_SCALE = 3.1
HAIR = 1.15
HEAD_CENTRE = 0.47

# Some photos are cropped too tightly to give the framing above. Up to this
# much of the crop may be filled by extending the edge pixels outwards, which
# is invisible on a plain background; beyond it we give up and use the whole
# photo, so the head comes out larger than everyone else's.
PAD_LIMIT = 1.5


def faces(paths: list[Path]) -> dict[Path, dict]:
    out = subprocess.run(["swift", str(ROOT / "scripts" / "facebox.swift"), *map(str, paths)],
                         capture_output=True, text=True).stdout
    found = {}
    for line in out.splitlines():
        if not line.startswith("{"):
            continue                      # Vision chatters on stdout sometimes
        d = json.loads(line)
        found[Path(d["path"])] = d
    return found


def crop_box(info: dict) -> tuple[int, int, int, str]:
    """Return (side, left, top, how) where how is "crop", "pad" or "fallback".

    left/top may be negative, or run past the edge of the photo, when the crop
    is to be padded.
    """
    w, h = info["width"], info["height"]
    if not info.get("faces"):
        # No face found: fall back to the top-centre square, and say so.
        side = min(w, h)
        return side, (w - side) // 2, 0, "fallback"

    face = max(info["faces"], key=lambda f: f["h"])
    eye_x, eye_y = face["eyeX"], face["eyeY"]
    d = face["chinY"] - eye_y
    if d <= 0:                      # no landmarks; guess from the box
        d = 0.55 * face["h"]

    ideal = CROP_SCALE * d
    how = "crop" if ideal <= min(w, h) else (
        "pad" if ideal <= PAD_LIMIT * min(w, h) else "fallback")
    side = ideal if how != "fallback" else min(w, h)

    head_top, chin = eye_y - HAIR * d, eye_y + d
    top = (head_top + chin) / 2 - HEAD_CENTRE * side
    left = eye_x - side / 2

    if how != "pad":
        # Keep the crop on the photo. When the photo is too small this pushes
        # the head off centre, but never off the crop.
        left = max(0, min(left, w - side))
        top = max(0, min(top, h - side))
    return round(side), round(left), round(top), how


def main() -> int:
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if args:
        sources = [Path(a) for a in args]
    else:
        # The full-size photos, which people.md links to; the <img> itself
        # points at the thumbnail this script writes.
        people = (ROOT / "people.md").read_text(encoding="utf-8")
        names = dict.fromkeys(n for n in
                              re.findall(r'\{\{site\.url\}\}/images/([^"]+)', people)
                              if not n.startswith("thumbs/"))
        sources = [ROOT / "images" / n for n in names]

    THUMBS.mkdir(parents=True, exist_ok=True)
    missing = [s for s in sources if not s.exists()]
    for s in missing:
        print(f"warning: {s} does not exist", file=sys.stderr)
    sources = [s for s in sources if s.exists()]

    todo = [s for s in sources
            if force or not (THUMBS / (s.stem + ".jpg")).exists()
            or (THUMBS / (s.stem + ".jpg")).stat().st_mtime < s.stat().st_mtime]
    if not todo:
        print(f"all {len(sources)} thumbnails are up to date")
        return 0

    info = faces(todo)
    undetected = []
    for src in todo:
        d = info.get(src) or info.get(Path(str(src)))
        if d is None or "error" in d:
            print(f"warning: could not read {src}", file=sys.stderr)
            continue
        side, left, top, how = crop_box(d)
        dst = THUMBS / (src.stem + ".jpg")
        if how == "pad":
            # Render a viewport that reaches past the photo, filling the extra
            # with the edge pixels.
            geometry = ["-virtual-pixel", "edge",
                        "-set", "option:distort:viewport",
                        f"{side}x{side}{left:+d}{top:+d}",
                        "-distort", "SRT", "0"]
        else:
            geometry = ["-crop", f"{side}x{side}+{left}+{top}"]
        subprocess.run(["magick", str(src), *geometry, "+repage",
                        "-resize", f"{SIZE}x{SIZE}>",
                        "-background", "white", "-flatten",
                        "-quality", "88", str(dst)], check=True)
        if how == "fallback":
            undetected.append(src.name)
        note = {"crop": "", "pad": "   (edges extended to fit the framing)",
                "fallback": "   (photo too tight; head larger than the rest)"}[how]
        print(f"{src.name:24s} {d['width']}x{d['height']} -> {side}x{side}{left:+d}{top:+d}{note}")

    if undetected:
        print("\ncheck these by eye: " + ", ".join(undetected), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
