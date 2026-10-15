#!/usr/bin/env python
"""Sweep ``generate_character``'s resolved fields over many seeds and compare each
value's share against a committed baseline.

``AGENTS.md``'s coherence checklist has always asked for "a before/after sweep of
every field's marginals ... no share moves you did not intend" before shipping any
new value, phrase or rule -- but every session wrote its own throwaway version of
this, including the one that found the 1.5.5 vitiligo/eye-colour/tattoo-placement
over-draws. This is that script, committed, so the sweep becomes a gate instead of
something re-derived by eye each release.

Usage (from the repo root)::

    python scripts/sweep_marginals.py --write           # (re)write the baseline
    python scripts/sweep_marginals.py --check            # fail if shares drifted (CI)
    python scripts/sweep_marginals.py --report            # print 2x-mean outliers
    python scripts/sweep_marginals.py --unreachable       # pool values that never draw

``--write`` and ``--check`` both refuse to run against a local ``user_options.json``
-- the baseline is ``{gender: {field: {value: count}}}``, so a custom field value,
archetype or cosplayer would write the maintainer's private additions straight into
a committed, published file. Same class of trap ``generate_js_data.py`` documents
at length, reached by running the engine instead of parsing the source with ``ast``.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.fields import FIELD_DEFINITIONS  # noqa: E402
from data.user_options import USER_OPTIONS_PATH  # noqa: E402
from nodes.identity_forge import generate_character  # noqa: E402

BASELINE_PATH = ROOT / "tests" / "fixtures" / "marginals_baseline.json"
UNREACHABLE_PATH = ROOT / "tests" / "fixtures" / "unreachable_by_design.json"
GENDERS = ("Female", "Male", "Any")
DEFAULT_N = 4000

#: Fields excluded from the sweep: free text (no fixed pool of values to track) or
#: so large that every seed draws a near-unique value (nothing meaningful to sum).
_SKIPPED_FIELDS = frozenset({"outfit_description", "held_item"})

#: The "nothing drawn" tokens across every field's absence convention (see
#: ``_EXTRA_ABSENCE`` / ``_is_absent`` in nodes/identity_forge.py). A value in this
#: set is excluded from the "2x the field's mean" outlier check in --report, since
#: it is expected to dominate its field by design, not by accident.
_ABSENT_TOKENS = frozenset({
    "none", "no notable marks", "no tattoos", "no visible legwear", "no bag",
    "no accessories", "no hair accessory", "no piercings beyond ears",
    "no other jewelry", "no necklace", "no earrings", "no makeup",
    "no eyeshadow", "no eyeliner", "no blush", "clean-shaven", "no outerwear",
})

#: A value's z-score tolerance in --check: how many standard deviations a share may
#: move from the baseline (at the baseline's own N) before it is flagged. 4.5 is
#: generous enough that normal sampling noise at DEFAULT_N never trips it, but a
#: weight change of the kind this release makes (a multi-point share move) always
#: does.
_Z_TOLERANCE = 4.5


def _refuse_if_private_data() -> None:
    if USER_OPTIONS_PATH.is_file():
        raise SystemExit(
            f"Refusing to run: {USER_OPTIONS_PATH} exists. A custom field value, "
            "archetype, cosplayer or creature it adds would be swept into the "
            "baseline and committed. Temporarily move it aside, or run this from "
            "a clean checkout, then regenerate."
        )


def _flatten(document: dict, out: dict[str, str]) -> dict[str, str]:
    for key, value in document.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            _flatten(value, out)
        elif isinstance(value, str):
            out[key] = value
    return out


def _sweep(n: int) -> dict[str, dict[str, Counter]]:
    """Return ``{gender: {field: Counter({value: count})}}`` over ``n`` seeds."""
    result: dict[str, dict[str, Counter]] = {}
    for gender in GENDERS:
        counts: dict[str, Counter] = defaultdict(Counter)
        for seed in range(n):
            _, js = generate_character(seed, gender, {})
            flat = _flatten(json.loads(js), {})
            for field, value in flat.items():
                if field in _SKIPPED_FIELDS:
                    continue
                counts[field][value] += 1
        result[gender] = dict(counts)
    return result


def _write(n: int) -> None:
    _refuse_if_private_data()
    swept = _sweep(n)
    payload = {
        "n": n,
        "genders": {
            gender: {field: dict(counter) for field, counter in fields.items()}
            for gender, fields in swept.items()
        },
    }
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    print(f"Wrote baseline from {n} seeds/gender to {BASELINE_PATH}")


def _check(n: int) -> int:
    _refuse_if_private_data()
    if not BASELINE_PATH.is_file():
        print(f"No baseline at {BASELINE_PATH}; run --write first.", file=sys.stderr)
        return 1
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    base_n = baseline["n"]
    current = _sweep(n)

    drifted: list[str] = []
    for gender, fields in current.items():
        base_fields = baseline["genders"].get(gender, {})
        for field, counter in fields.items():
            base_counter = base_fields.get(field, {})
            values = set(counter) | set(base_counter)
            for value in sorted(values):
                base_count = base_counter.get(value, 0)
                base_p = max(base_count / base_n, 0.5 / base_n)
                cur_p = counter.get(value, 0) / n
                # Standard error of the DIFFERENCE between two independent binomial
                # proportions at sample sizes base_n and n.
                se = (base_p * (1 - base_p) / base_n + cur_p * (1 - cur_p) / n) ** 0.5
                if se == 0:
                    continue
                z = abs(cur_p - base_p) / se
                if z > _Z_TOLERANCE:
                    drifted.append(
                        f"  {gender}.{field} = {value!r}: "
                        f"{base_p:.1%} -> {cur_p:.1%} (z={z:.1f})")

    if drifted:
        print(f"Marginal share drift detected ({n} seeds/gender vs a "
              f"{base_n}-seed baseline):")
        print("\n".join(drifted))
        print("\nIf this move was intended, regenerate the baseline:\n"
              "  python scripts/sweep_marginals.py --write")
        return 1
    print(f"No marginal drift: {n} seeds/gender match the {base_n}-seed baseline.")
    return 0


def _report(n: int) -> None:
    swept = _sweep(n)
    for gender, fields in swept.items():
        print(f"\n######## {gender} (N={n})")
        for field in sorted(fields):
            counter = fields[field]
            present = {v: c for v, c in counter.items() if v.lower() not in _ABSENT_TOKENS}
            if len(present) < 4:
                continue
            mean = sum(present.values()) / len(present)
            outliers = [f"{v} {c / n:.1%}" for v, c in
                        sorted(present.items(), key=lambda kv: -kv[1])
                        if c >= 2 * mean]
            if outliers:
                print(f"  {field}: {'; '.join(outliers)}")


def _unreachable(baseline: dict) -> list[tuple[str, str]]:
    """Every ``(field, value)`` in a field's pools that no gender lock drew in
    ``baseline``. A value that only one gender draws is not listed: a gendered
    coherence filter is intended; a value nothing draws is either a control
    setting or an accidental gate."""
    drawn = baseline["genders"].values()
    found: list[tuple[str, str]] = []
    for field, definition in sorted(FIELD_DEFINITIONS.items()):
        pool: dict[str, None] = {}
        for key in ("female_options", "male_options"):
            for value in definition.get(key, ()):
                if isinstance(value, str):
                    pool[value] = None
        for value in pool:
            if not any(g.get(field, {}).get(value, 0) for g in drawn):
                found.append((field, value))
    return found


def _committed_unreachable() -> list[tuple[str, str]]:
    """The ``(field, value)`` pairs ``unreachable_by_design.json`` accounts for."""
    groups = json.loads(UNREACHABLE_PATH.read_text(encoding="utf-8"))["unreachable"]
    return sorted((g["field"], v) for g in groups for v in g["values"])


def _unreachable_report() -> int:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    found = sorted(_unreachable(baseline))
    expected = _committed_unreachable()
    for field, value in found:
        print(f"  {field} = {value!r}")
    new = [pair for pair in found if pair not in expected]
    stale = [pair for pair in expected if pair not in found]
    for field, value in new:
        print(f"UNEXPLAINED (an accidental gate?): {field} = {value!r}", file=sys.stderr)
    for field, value in stale:
        print(f"STALE exception (now draws, or left the pool): {field} = {value!r}",
              file=sys.stderr)
    if new or stale:
        return 1
    print(f"{len(found)} unreachable values, all accounted for in "
          f"{UNREACHABLE_PATH.name}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true",
                       help="(Re)write the committed baseline.")
    group.add_argument("--check", action="store_true",
                       help="Fail if any value's share drifted from the baseline (CI).")
    group.add_argument("--report", action="store_true",
                       help="Print values at >=2x their field's mean share. "
                            "Informational only; never fails.")
    group.add_argument("--unreachable", action="store_true",
                       help="List pool values the baseline never draws and fail if the "
                            "list differs from tests/fixtures/unreachable_by_design.json.")
    parser.add_argument("-n", type=int, default=DEFAULT_N,
                       help=f"Seeds per gender (default {DEFAULT_N}).")
    args = parser.parse_args(argv)

    if args.write:
        _write(args.n)
        return 0
    if args.check:
        return _check(args.n)
    if args.unreachable:
        return _unreachable_report()
    _report(args.n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
