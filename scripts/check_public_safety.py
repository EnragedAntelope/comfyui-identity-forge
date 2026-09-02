"""Scan tracked markdown for categorical leaks before it goes public.

**This is not the maintainer's denylist checker and does not replace it.** That
one lives outside this repo, encodes private terms, and stays uncopied by
design. This script is the half a *contributor* can run: it knows nothing
private, only the shapes of things that should never appear in a public
document.

What it flags, all categorical:

* Windows absolute paths (``C:\\Users\\...``), and ``/home/<user>`` /
  ``/Users/<user>`` paths - these carry a real username.
* RFC1918 private IP addresses - these describe someone's LAN.
* ``.env``-style ``KEY=value`` secrets (``TOKEN``/``SECRET``/``PASSWORD``/
  ``API_KEY``...) with a non-placeholder value.
* Long base64/hex blobs, which is what a leaked key looks like.

Deliberately NOT flagged: relative paths, ``~/`` paths, public IPs and
documented localhost ports (``127.0.0.1:8188`` is in the render instructions on
purpose). Fenced code blocks are scanned too - a leaked token in a shell example
is still leaked.

Stdlib only, so it runs on the dependency-free CI job.

Usage::

    python scripts/check_public_safety.py              # every tracked .md
    python scripts/check_public_safety.py AGENTS.md    # specific files

Exits non-zero on the first finding, listing every one.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: A placeholder is the whole point of a placeholder - do not flag it.
_PLACEHOLDER = re.compile(
    r"^(?:<[^>]*>|\{[^}]*\}|\$\{?[A-Z_]+\}?|x{3,}|\.{3}|your[-_ ]?\w+|"
    r"changeme|placeholder|example|redacted|\*+|none|null|\"\"|'')$",
    re.IGNORECASE,
)

CHECKS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "windows-path",
        re.compile(r"[A-Za-z]:\\+(?:Users|Documents and Settings)\\+[^\\\s\"'`)\]]+"),
        "a Windows path under a real user profile",
    ),
    (
        "unix-home-path",
        # ~/ is fine; /home/<name> and /Users/<name> name a person.
        re.compile(r"(?<![\w~])/(?:home|Users)/(?!<)[A-Za-z][\w.-]*"),
        "an absolute home directory naming a real user",
    ),
    (
        "private-ip",
        re.compile(
            r"(?<![\w.])(?:"
            r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|192\.168\.\d{1,3}\.\d{1,3}"
            r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
            r")(?![\w.])"
        ),
        "an RFC1918 private IP address (someone's LAN)",
    ),
    (
        "secret-assignment",
        re.compile(
            r"\b([A-Z][A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|"
            r"ACCESS_KEY|PRIVATE_KEY|CREDENTIALS?))\s*[=:]\s*"
            r"[\"']?([^\s\"'`,;]+)"
        ),
        "an environment-variable secret with a value",
    ),
    (
        "long-blob",
        # 40+ chars of base64/hex with no spaces: the shape of a key. Requires a
        # digit AND a letter so it cannot fire on a long English word or a rule
        # of underscores.
        re.compile(r"(?<![\w/])(?=[A-Za-z0-9+/=]*\d)(?=[A-Za-z0-9+/=]*[A-Za-z])"
                   r"[A-Za-z0-9+/=]{40,}(?![\w/])"),
        "a long base64/hex blob (the shape of a leaked key)",
    ),
]


def tracked_markdown() -> list[Path]:
    """Every tracked ``*.md``, straight from git so untracked drafts are skipped."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.md", "**/*.md"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return sorted(ROOT.rglob("*.md"))
    return [ROOT / line for line in out.splitlines() if line.strip()]


def scan(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{path}: could not read ({exc})"]

    for number, line in enumerate(text.splitlines(), 1):
        for name, pattern, why in CHECKS:
            for match in pattern.finditer(line):
                if name == "secret-assignment":
                    value = match.group(2)
                    if _PLACEHOLDER.match(value):
                        continue
                snippet = match.group(0)
                if len(snippet) > 70:
                    snippet = snippet[:67] + "..."
                rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                findings.append(f"{rel}:{number}: [{name}] {why} -> {snippet}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="files to scan (default: tracked *.md)")
    args = parser.parse_args(argv)

    paths = [Path(p) if Path(p).is_absolute() else ROOT / p for p in args.paths]
    if not paths:
        paths = tracked_markdown()

    findings: list[str] = []
    for path in paths:
        if path.is_file():
            findings.extend(scan(path))

    if findings:
        print(f"PUBLIC SAFETY CHECK FAILED ({len(findings)} finding(s)):")
        for line in findings:
            print(f"  - {line}")
        print("\nThis checks CATEGORICAL leaks only. The maintainer's denylist "
              "checker is separate, lives outside this repo, and still has to "
              "pass before pushing AGENTS.md or CLAUDE.md.")
        return 1

    print(f"Public safety check passed ({len(paths)} file(s) scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
