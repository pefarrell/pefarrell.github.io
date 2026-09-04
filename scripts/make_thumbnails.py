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

# Framing. The crop is CROP_SCALE times the height of the detected face box,
# with the eyes EYE_LINE of the way down the crop.
CROP_SCALE = 2.5
EYE_LINE = 0.40


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


def crop_box(info: dict) -> tuple[int, int, int, int, bool]:
    """Return (side, left, top, detected)."""
    w, h = info["width"], info["height"]
    if not info.get("faces"):
        # No face found: fall back to the top-centre square, and say so.
        side = min(w, h)
        return side, (w - side) // 2, 0, False

    face = max(info["faces"], key=lambda f: f["h"])
    side = min(CROP_SCALE * face["h"], w, h)
    left = face["eyeX"] - side / 2
    top = face["eyeY"] - EYE_LINE * side
    left = max(0, min(left, w - side))
    top = max(0, min(top, h - side))
    return round(side), round(left), round(top), True


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
        side, left, top, detected = crop_box(d)
        dst = THUMBS / (src.stem + ".jpg")
        subprocess.run(["magick", str(src),
                        "-crop", f"{side}x{side}+{left}+{top}", "+repage",
                        "-resize", f"{SIZE}x{SIZE}>",
                        "-background", "white", "-flatten",
                        "-quality", "88", str(dst)], check=True)
        if not detected:
            undetected.append(src.name)
        print(f"{src.name:24s} {d['width']}x{d['height']} -> {side}x{side}+{left}+{top}"
              f"{'' if detected else '   (no face found; top-centre crop)'}")

    if undetected:
        print("\nno face detected, check these by eye: " + ", ".join(undetected),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
