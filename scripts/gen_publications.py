#!/usr/bin/env python3
"""Generate publications.md for pefarrell.org from the CV.

The single source of truth for publications is ~/git/cv/cv.tex: it lists the
citation keys, in order, under \\section headings ("Articles in review",
"Articles to appear", "Published articles").  The bibliographic data itself
lives in the BibTeX database that cv.tex points at (literature.bib).

This script reads both and writes a Jekyll page.  The numbering matches the CV,
where item [1] is the oldest publication and the highest number is the newest
submission.

Usage:
    scripts/gen_publications.py                 # write publications.md
    scripts/gen_publications.py --check         # exit 1 if it is out of date
"""

from __future__ import annotations

import argparse
import datetime
import html
import os
import re
import sys
from pathlib import Path

# Sections of cv.tex that hold publications, in the order they should appear on
# the page, mapped to the heading used on the website.  Sections of cv.tex that
# are not listed here are ignored.
SECTIONS = {
    "Articles in review": "In review",
    "Articles to appear": "To appear",
    "Published articles": "Published",
}

# Sections for which the journal an article has been submitted to is not shown;
# only the year is.
NO_VENUE = {"Articles in review"}


# ----------------------------------------------------------------------------
# LaTeX -> HTML
# ----------------------------------------------------------------------------

# \'e and friends: accent macro -> combining character.
COMBINING = {
    "`": "\u0300", "'": "\u0301", "^": "\u0302", "~": "\u0303",
    "=": "\u0304", "u": "\u0306", ".": "\u0307", '"': "\u0308",
    "r": "\u030a", "H": "\u030b", "v": "\u030c", "c": "\u0327",
    "k": "\u0328", "d": "\u0323", "b": "\u0331",
}

SYMBOLS = {
    r"\ss": "ß", r"\o": "ø", r"\O": "Ø", r"\l": "ł", r"\L": "Ł",
    r"\aa": "å", r"\AA": "Å", r"\ae": "æ", r"\AE": "Æ",
    r"\oe": "œ", r"\OE": "Œ", r"\i": "ı", r"\j": "ȷ",
    r"\&": "&", r"\%": "%", r"\_": "_", r"\#": "#", r"\$": "$",
    r"\{": "{", r"\}": "}", r"\,": "\u2009", r"\ ": " ",
}

# Macros whose argument we keep and whose markup we drop.
TRANSPARENT = ("emph", "textit", "textbf", "textrm", "textsc", "text", "mbox", "hbox")


def _take_group(s: str, i: int) -> tuple[str, int]:
    """Read the macro argument starting at s[i]; return (contents, index after)."""
    if i < len(s) and s[i] == "{":
        depth = 0
        for j in range(i, len(s)):
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    return s[i + 1:j], j + 1
        return s[i + 1:], len(s)
    if i < len(s):
        return s[i], i + 1
    return "", i


def latex_to_text(s: str) -> str:
    """Convert a BibTeX field value to Unicode text.

    Math ($...$) is passed through untouched, for MathJax to render.
    """
    s = re.sub(r"\s+", " ", s).strip()

    # Set aside math so that nothing below mangles it.
    math: list[str] = []

    def stash(m: re.Match) -> str:
        math.append(m.group(0))
        return f"\x00{len(math) - 1}\x00"

    s = re.sub(r"\$\$.*?\$\$|\$.*?\$", stash, s, flags=re.S)

    out: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue

        # \foo{...} / \foo
        m = re.match(r"\\([A-Za-z]+)", s[i:])
        if m:
            name = m.group(1)
            j = i + m.end()
            if name in TRANSPARENT:
                arg, j = _take_group(s, j)
                out.append(latex_to_text(arg))
            elif "\\" + name in SYMBOLS:
                out.append(SYMBOLS["\\" + name])
                if j < len(s) and s[j] == " ":   # \ss followed by a space
                    j += 1
            elif name in COMBINING and len(name) == 1:
                arg, j = _take_group(s, j)
                out.append(latex_to_text(arg) + COMBINING[name])
            else:
                # Unknown macro: drop it, keep any argument.
                arg, j = _take_group(s, j) if j < len(s) and s[j] == "{" else ("", j)
                out.append(latex_to_text(arg))
                print(f"warning: unknown LaTeX macro \\{name}", file=sys.stderr)
            i = j
            continue

        # \' etc: a one-character accent or escape.
        if i + 1 < len(s):
            c2 = s[i + 1]
            if "\\" + c2 in SYMBOLS:
                out.append(SYMBOLS["\\" + c2])
                i += 2
                continue
            if c2 in COMBINING:
                arg, j = _take_group(s, i + 2)
                out.append(latex_to_text(arg) + COMBINING[c2])
                i = j
                continue
        i += 1

    s = "".join(out)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("---", "\u2014").replace("--", "\u2013")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("~", "\u00a0")   # after collapsing whitespace, which would eat it

    import unicodedata
    s = unicodedata.normalize("NFC", s)

    return re.sub(r"\x00(\d+)\x00", lambda m: math[int(m.group(1))], s)


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# ----------------------------------------------------------------------------
# BibTeX
# ----------------------------------------------------------------------------

def parse_bib(text: str) -> dict[str, dict[str, str]]:
    """Parse a .bib file into {key: {"entrytype": ..., field: value, ...}}."""
    entries: dict[str, dict[str, str]] = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        entrytype = m.group(1).lower()
        if entrytype in ("comment", "preamble", "string"):
            continue
        start = text.index("{", m.start())
        depth = 0
        end = len(text)
        for j in range(start, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        entry = {"entrytype": entrytype}
        entry.update(parse_fields(text[m.end():end]))
        entries[m.group(2)] = entry
    return entries


def parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    i = 0
    while i < len(body):
        m = re.compile(r"\s*(\w+)\s*=\s*").match(body, i)
        if not m:
            break
        name = m.group(1).lower()
        i = m.end()
        if body[i] == "{":
            value, i = _take_group(body, i)
        elif body[i] == '"':
            j = body.index('"', i + 1)
            value, i = body[i + 1:j], j + 1
        else:
            j = i
            while j < len(body) and body[j] not in ",}":
                j += 1
            value, i = body[i:j].strip(), j
        fields[name] = value
        # Skip to the start of the next field.
        while i < len(body) and body[i] in " \t\r\n,":
            i += 1
    return fields


# ----------------------------------------------------------------------------
# cv.tex
# ----------------------------------------------------------------------------

def strip_comments(tex: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in tex.split("\n"))


def parse_cv(tex: str) -> list[tuple[str, list[str]]]:
    """Return [(section title, [citation keys])] for the publication sections."""
    tex = strip_comments(tex)
    sections: list[tuple[str, list[str]]] = []
    current: str | None = None
    for m in re.finditer(r"\\section\{([^}]*)\}|\\fullcite\{([^}]*)\}", tex):
        if m.group(1) is not None:
            current = latex_to_text(m.group(1))
            sections.append((current, []))
        elif sections:
            sections[-1][1].append(m.group(2))
    return [(t, keys) for t, keys in sections if keys]


def find_bib(cv_tex: Path, tex: str) -> Path:
    m = re.search(r"\\(?:bibliography|addbibresource)\{([^}]*)\}", strip_comments(tex))
    name = m.group(1) if m else "literature.bib"
    for candidate in (name, name + ".bib"):
        path = cv_tex.parent / candidate
        if path.exists():
            return path
    raise SystemExit(f"error: cannot find the bibliography ({name}) next to {cv_tex}")


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------

def authors_html(entry: dict[str, str]) -> str:
    names = [esc(latex_to_text(a))
             for a in re.split(r"\s+and\s+", entry.get("author", "")) if a.strip()]
    if len(names) > 1:
        return ", ".join(names[:-1]) + " and " + names[-1]
    return "".join(names)


def links(entry: dict[str, str]) -> tuple[str | None, list[tuple[str, str]]]:
    """Return (url for the title, [(label, url), ...] for the link line)."""
    doi = entry.get("doi", "").strip()
    if not doi:
        return None, []
    m = re.fullmatch(r"10\.48550/arXiv\.(.+)", doi, flags=re.I)
    if m:
        url = f"https://arxiv.org/abs/{m.group(1)}"
        return url, [(f"arXiv:{m.group(1)}", url)]
    url = f"https://doi.org/{doi}"
    return url, [(f"doi:{doi}", url)]


def venue_html(entry: dict[str, str], show_venue: bool = True) -> str:
    """The journal/booktitle line, with volume, issue, pages and year.

    With show_venue false, only the year is given: where an article has been
    submitted to is nobody's business but the referees'.
    """
    year = latex_to_text(entry.get("year", ""))
    bits: list[str] = []

    if not show_venue:
        return esc(year) + "." if year else ""

    journal = entry.get("journal") or entry.get("journaltitle")
    booktitle = entry.get("booktitle")
    status = entry.get("note") or entry.get("annote")

    if journal:
        where = f"<em>{esc(latex_to_text(journal))}</em>"
        volume = latex_to_text(entry.get("volume", ""))
        number = latex_to_text(entry.get("number") or entry.get("issue", ""))
        # Page ranges are written both as 709-732 and as 709--732 in the .bib.
        pages = re.sub(r"(?<=\d)-(?=\d)", "\u2013", latex_to_text(entry.get("pages", "")))
        if volume:
            where += f" <strong>{esc(volume)}</strong>"
            if number:
                where += f"({esc(number)})"
        if pages:
            where += (":" if volume else ", ") + esc(pages)
        bits.append(where)
    elif booktitle:
        where = f"In <em>{esc(latex_to_text(booktitle))}</em>"
        for field in ("publisher", "address"):
            if entry.get(field):
                where += ", " + esc(latex_to_text(entry[field]))
        bits.append(where)
    elif status:
        bits.append(esc(latex_to_text(status)))
    else:
        bits.append("Preprint")

    if year:
        bits.append(esc(year))
    return ", ".join(bits) + "."


def entry_html(key: str, entry: dict[str, str], number: int,
               show_venue: bool = True) -> str:
    title = esc(latex_to_text(entry.get("title", key))).rstrip(".")
    url, link_list = links(entry)
    title_html = f'<a href="{url}">{title}</a>' if url else title
    linkline = " ".join(
        f'<a class="pub-link" href="{u}">{esc(label)}</a>' for label, u in link_list
    )
    return (
        f'<li class="pub" id="{key}">\n'
        f'  <span class="pub-num">[{number}]</span>\n'
        f'  <span class="pub-title">{title_html}</span>\n'
        f'  <span class="pub-authors">{authors_html(entry)}</span>\n'
        f'  <span class="pub-venue">{venue_html(entry, show_venue)} {linkline}</span>\n'
        f"</li>"
    )


def render(sections: list[tuple[str, list[str]]], bib: dict[str, dict[str, str]]) -> str:
    total = sum(len(keys) for _, keys in sections)

    out = [
        "---",
        "title: Publications",
        "---",
        "",
        "<!-- This page is generated from ~/git/cv/cv.tex by",
        "     scripts/gen_publications.py.  Do not edit it by hand. -->",
        "",
    ]

    number = total
    for title, keys in sections:
        heading = SECTIONS.get(title, title)
        out.append(f'<h2 id="{heading.lower().replace(" ", "-")}">{esc(heading)}</h2>')
        out.append('<ol class="pub-list">')
        for key in keys:
            if key not in bib:
                raise SystemExit(f"error: {key} is cited in cv.tex but not in the bibliography")
            out.append(entry_html(key, bib[key], number, title not in NO_VENUE))
            number -= 1
        out.append("</ol>")
        out.append("")

    # A few titles contain mathematics; render it with MathJax, but only load
    # MathJax on the days when there is some.
    if "$" in "\n".join(out):
        out.append("<script>")
        out.append("  window.MathJax = {tex: {inlineMath: [['$', '$'], "
                   "['\\\\(', '\\\\)']]}};")
        out.append("</script>")
        out.append(
            '<script id="MathJax-script" async '
            'src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
        )
        out.append("")

    out.append(f"<p class=\"pub-updated\">Last updated "
               f"{datetime.date.today().isoformat()}.</p>")
    out.append("")
    return "\n".join(out)


# ----------------------------------------------------------------------------

def main() -> int:
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cv", type=Path,
                        default=Path(os.environ.get("CV_TEX",
                                                    Path.home() / "git/cv/cv.tex")),
                        help="path to cv.tex (default: ~/git/cv/cv.tex)")
    parser.add_argument("--bib", type=Path, default=None,
                        help="path to the .bib file (default: taken from cv.tex)")
    parser.add_argument("-o", "--output", type=Path, default=here / "publications.md",
                        help="output file (default: publications.md)")
    parser.add_argument("--check", action="store_true",
                        help="do not write; exit 1 if the output is out of date")
    args = parser.parse_args()

    if not args.cv.exists():
        raise SystemExit(f"error: {args.cv} does not exist")
    tex = args.cv.read_text(encoding="utf-8")
    bib_path = args.bib or find_bib(args.cv, tex)

    sections = parse_cv(tex)
    sections = [(t, k) for t, k in sections if t in SECTIONS]
    if not sections:
        raise SystemExit(f"error: no publication sections found in {args.cv}; "
                         f"expected one of {', '.join(SECTIONS)}")

    bib = parse_bib(bib_path.read_text(encoding="utf-8"))
    page = render(sections, bib)

    # The date stamp changes every day; ignore it when checking.
    def sansdate(s: str) -> str:
        return re.sub(r"Last updated \d{4}-\d\d-\d\d", "", s)

    if args.check:
        old = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if sansdate(old) != sansdate(page):
            print(f"{args.output} is out of date; rerun {Path(__file__).name}",
                  file=sys.stderr)
            return 1
        return 0

    if args.output.exists() and sansdate(args.output.read_text(encoding="utf-8")) == sansdate(page):
        print(f"{args.output} is already up to date")
        return 0

    args.output.write_text(page, encoding="utf-8")
    n = sum(len(k) for _, k in sections)
    print(f"wrote {args.output} ({n} publications from {args.cv})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
