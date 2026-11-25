#!/usr/bin/env python3
"""Zero-dependency quality checks for the devdunlap.site static site.

Runs the same locally and in GitHub Actions:

    python3 scripts/check_site.py

Every check prints PASS/FAIL; the script exits 1 if anything fails.
The checks are deliberately boring and deterministic — no network calls,
no third-party packages — so a red run always means the site changed,
never that a checker flaked.
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
SIZE_BUDGET_BYTES = 100 * 1024  # the whole pitch of a static site is "instant"

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
# Elements whose end tag HTML allows authors to omit.
OPTIONAL_CLOSE = {"li", "p", "dt", "dd", "tr", "td", "th", "option", "thead", "tbody"}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.balance_errors = []
        self.ids = []
        self.imgs = []
        self.links = []          # (href, attrs dict)
        self.local_refs = []     # src/href values that point at local files
        self.title_parts = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "img":
            self.imgs.append(attrs)
        if tag == "a" and "href" in attrs:
            self.links.append((attrs["href"], attrs))
        for key in ("src", "href"):
            value = attrs.get(key)
            if value and not value.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:")):
                self.local_refs.append(value)
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in VOID_ELEMENTS:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                unclosed = self.stack.pop()
                if unclosed not in OPTIONAL_CLOSE:
                    self.balance_errors.append(f"<{unclosed}> implicitly closed by </{tag}>")
            self.stack.pop()
        else:
            self.balance_errors.append(f"stray </{tag}>")

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)


def main():
    if not os.path.isfile(INDEX):
        check("index.html exists at repo root", False, INDEX)
        return 1
    check("index.html exists at repo root", True)

    raw = open(INDEX, "rb").read()
    html = raw.decode("utf-8", errors="replace")
    size = len(raw)
    check(f"page weight within budget ({size:,} / {SIZE_BUDGET_BYTES:,} bytes)",
          size <= SIZE_BUDGET_BYTES)

    check("DOCTYPE html declared", html.lstrip().lower().startswith("<!doctype html"))
    check('<html lang="..."> set', bool(re.search(r'<html[^>]+lang="[a-zA-Z-]+"', html)))
    check("meta viewport present", 'name="viewport"' in html)
    desc = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', html)
    check("meta description present and meaningful (>= 50 chars)",
          bool(desc) and len(desc.group(1)) >= 50,
          f"{len(desc.group(1)) if desc else 0} chars")

    parser = SiteParser()
    parser.feed(html)
    leftover = [t for t in parser.stack if t not in OPTIONAL_CLOSE]
    balance_problems = parser.balance_errors + [f"<{t}> never closed" for t in leftover]
    check("HTML tags balanced", not balance_problems, "; ".join(balance_problems[:3]))

    title = "".join(parser.title_parts).strip()
    check("<title> present and non-empty", len(title) >= 8, title[:60])

    dupes = sorted({i for i in parser.ids if parser.ids.count(i) > 1})
    check("element ids are unique", not dupes, ", ".join(dupes))

    missing = [r for r in parser.local_refs if not os.path.exists(os.path.join(ROOT, r))]
    check("local file references exist", not missing, ", ".join(missing))

    id_set = set(parser.ids)
    broken_anchors = [h for h, _ in parser.links
                      if h.startswith("#") and len(h) > 1 and h[1:] not in id_set]
    check("in-page anchor targets exist", not broken_anchors, ", ".join(broken_anchors))

    imgs_without_alt = [i.get("src", "?") for i in parser.imgs if not i.get("alt")]
    check("every <img> has alt text", not imgs_without_alt, ", ".join(imgs_without_alt))

    blank_without_noopener = [
        h for h, a in parser.links
        if a.get("target") == "_blank" and "noopener" not in a.get("rel", "")
    ]
    check('target="_blank" links carry rel="noopener"',
          not blank_without_noopener, ", ".join(blank_without_noopener))

    check("no insecure http:// URLs", "http://" not in html)
    check("no inline onclick handlers", not re.search(r"\sonclick\s*=", html, re.I))
    check("no placeholder text (lorem ipsum / TODO)",
          not re.search(r"lorem ipsum|\bTODO\b", html, re.I))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
