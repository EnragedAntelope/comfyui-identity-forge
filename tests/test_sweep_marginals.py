"""Targeted tests for ``scripts/sweep_marginals.py``'s two safety properties.

Not a re-run of the full sweep (that is the separate, slower CI step --
``python scripts/sweep_marginals.py --check`` -- see ``.github/workflows/ci.yml``
and ``AGENTS.md``'s build/test list). These two just pin the guard and the drift
math in isolation, with everything pointed at temp files so a failure here can
never touch the real committed baseline or create a real ``user_options.json``.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_SCRIPT_PATH = ROOT / "scripts" / "sweep_marginals.py"
_spec = importlib.util.spec_from_file_location("sweep_marginals", _SCRIPT_PATH)
sweep_marginals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sweep_marginals)


class PrivateDataGuardTests(unittest.TestCase):
    def test_refuses_when_user_options_json_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_user_options = Path(tmp) / "user_options.json"
            fake_user_options.write_text("{}", encoding="utf-8")
            with mock.patch.object(sweep_marginals, "USER_OPTIONS_PATH", fake_user_options):
                with self.assertRaises(SystemExit):
                    sweep_marginals._refuse_if_private_data()

    def test_allows_when_user_options_json_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "user_options.json"
            with mock.patch.object(sweep_marginals, "USER_OPTIONS_PATH", missing):
                sweep_marginals._refuse_if_private_data()  # must not raise


class CheckDetectsDriftTests(unittest.TestCase):
    """``_check`` must fail on a real, large share change and pass on none."""

    @classmethod
    def setUpClass(cls):
        # One real sweep shared by both tests below -- the engine call is the slow
        # part, so run it once. Large enough that zeroing out a whole field's
        # baseline reliably crosses _Z_TOLERANCE (a common eye_color value alone
        # needs roughly n >= 300 to do that; smaller n makes the drift test flaky).
        cls._n = 500
        cls._baseline = {
            "n": cls._n,
            "genders": {
                gender: {field: dict(counter) for field, counter in fields.items()}
                for gender, fields in sweep_marginals._sweep(cls._n).items()
            },
        }

    def _run_check_against(self, baseline: dict) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            baseline_path = Path(tmp) / "marginals_baseline.json"
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
            missing_user_options = Path(tmp) / "user_options.json"
            with mock.patch.object(sweep_marginals, "BASELINE_PATH", baseline_path), \
                 mock.patch.object(sweep_marginals, "USER_OPTIONS_PATH", missing_user_options):
                return sweep_marginals._check(self._n)

    def test_an_unperturbed_baseline_passes(self):
        self.assertEqual(self._run_check_against(self._baseline), 0)

    def test_a_zeroed_out_field_fails(self):
        # Deterministic regardless of RNG: eye_color is voiced on every character
        # (see FIELD_DEFINITIONS), so zeroing its baseline counts while the real
        # sweep still draws it guarantees a large, reproducible drift.
        perturbed = json.loads(json.dumps(self._baseline))  # deep copy
        for fields in perturbed["genders"].values():
            fields["eye_color"] = {}
        self.assertEqual(self._run_check_against(perturbed), 1)


if __name__ == "__main__":
    unittest.main()
