"""Guard against a relative markdown link rotting.

Scans README.md and docs/*.md (excluding docs/worklog/, which is gitignored
and so would make this test behave differently locally than on a fresh
clone) for `[text](path)` links, and checks that every relative path
resolves to a real file. External links (http(s)://, mailto:) and same-file
anchor links (`#section`) are skipped; an anchor fragment on a cross-file
link (`architecture.md#some-heading`) is stripped before checking, since
verifying the fragment itself actually exists in the target file is not
worth the complexity for how rarely that specific thing breaks.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_DOC_FILES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]


def _iter_relative_links():
    for doc_path in _DOC_FILES:
        text = doc_path.read_text(encoding="utf-8")
        for match in _LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue  # a same-file anchor like "#section"
            yield doc_path, path_part


class RelativeDocLinksTests(unittest.TestCase):
    def test_every_relative_link_resolves_to_a_real_file(self) -> None:
        broken = []
        for doc_path, path_part in _iter_relative_links():
            resolved = (doc_path.parent / path_part).resolve()
            if not resolved.is_file():
                broken.append(f"{doc_path.relative_to(ROOT)} -> {path_part}")
        self.assertFalse(
            broken,
            "broken relative link(s) found (fix the link or the file that moved): "
            + "; ".join(broken),
        )

    def test_scan_actually_covers_a_nonzero_number_of_links(self) -> None:
        # A regex that stopped matching (e.g. after a README rewrite changed
        # the link syntax) would make the test above pass by finding nothing
        # to check -- this catches that.
        count = sum(1 for _ in _iter_relative_links())
        self.assertGreater(count, 5, "expected to find more than a handful of "
                            "relative links across README.md and docs/*.md")


if __name__ == "__main__":
    unittest.main()
