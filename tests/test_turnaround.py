"""Tests for the IdentityForgeTurnaround node.

The node's whole contract: one seed-fixed character, N camera views, nothing
else moving between runs. Every test here exists because its violation would
silently produce a useless reference set (a different person per angle, or a
pose that reads differently from each side).
"""
from __future__ import annotations

import math
import re
import unittest

from data.fields import FIELD_DEFINITIONS
from nodes.identity_forge_turnaround import (
    _NEUTRAL_POSES, _VIEW_LABELS, _VIEW_PRESETS, _TURNAROUND_VIEWS,
    IdentityForgeTurnaround, resolve_turnaround_prompt,
)

_STEER = {
    "gender": "Any",
    "wardrobe": "Match gender",
    "size_scale": "Auto",
    "hair_color_scope": "Natural only",
    "accessory_density": "Balanced",
    "location_setting": "Any indoor/outdoor",
}

_FRAMING_RE = re.compile(r"the framing is ([^,]+)")


def _view(seed: int, index: str, views: str = "Portrait set (4)",
          neutral_pose: str = "On", upstream: str = "") -> tuple[str, str, int]:
    return resolve_turnaround_prompt(upstream, seed, views, index, neutral_pose, _STEER)


class ViewPresetSanityTests(unittest.TestCase):
    """Every pinned value must be an exact engine pool value."""

    def test_every_view_is_an_exact_shot_type_value(self):
        pool = set(FIELD_DEFINITIONS["shot_type"]["female_options"])
        self.assertEqual(len(_TURNAROUND_VIEWS), 6)
        for view in _TURNAROUND_VIEWS:
            self.assertIn(view, pool)

    def test_every_neutral_pose_is_an_exact_pool_value_in_both_genders(self):
        for pose in _NEUTRAL_POSES:
            self.assertIn(pose, FIELD_DEFINITIONS["pose"]["female_options"])
            self.assertIn(pose, FIELD_DEFINITIONS["pose"]["male_options"])

    def test_presets_are_ordered_prefixes_of_the_full_turnaround(self):
        self.assertEqual(_VIEW_PRESETS["Turnaround (6)"], _TURNAROUND_VIEWS)
        self.assertEqual(_VIEW_PRESETS["Portrait set (4)"], _TURNAROUND_VIEWS[:4])
        self.assertEqual(
            _VIEW_PRESETS["Front + profile (2)"],
            (_TURNAROUND_VIEWS[0], _TURNAROUND_VIEWS[3]),
        )

    def test_view_labels_cover_every_view_exactly_once(self):
        self.assertEqual(sorted(_VIEW_LABELS), sorted(set(_TURNAROUND_VIEWS)))
        self.assertEqual(len(_VIEW_LABELS), 6)


class TurnaroundStabilityTests(unittest.TestCase):
    """Views of one seed differ ONLY in the framing clause."""

    def test_two_views_share_everything_except_framing(self):
        prompt_a, label_a, count = _view(42, "0")
        prompt_b, label_b, _ = _view(42, "1")
        self.assertEqual(count, 4)
        frame_a = _FRAMING_RE.search(prompt_a)
        frame_b = _FRAMING_RE.search(prompt_b)
        self.assertIsNotNone(frame_a)
        self.assertIsNotNone(frame_b)
        self.assertEqual(
            _FRAMING_RE.sub("", prompt_a), _FRAMING_RE.sub("", prompt_b),
            "non-camera prose drifted between two views of the same seed",
        )
        self.assertNotEqual(frame_a.group(1), frame_b.group(1))
        self.assertEqual(label_a, "front")
        self.assertEqual(label_b, "three-quarter left")

    def test_index_wraps_modulo_the_preset_count(self):
        prompt_front, _, _ = _view(7, "0", views="Front + profile (2)")
        prompt_wrapped, _, _ = _view(7, "2", views="Front + profile (2)")
        self.assertEqual(prompt_front, prompt_wrapped)

    def test_invalid_index_falls_back_to_front(self):
        prompt_front, _, _ = _view(7, "0")
        prompt_junk, label_junk, _ = _view(7, "not-a-number")
        self.assertEqual(prompt_junk, prompt_front)
        self.assertEqual(label_junk, "front")

    def test_different_seeds_give_different_characters(self):
        prompt_a, _, _ = _view(1, "0")
        prompt_b, _, _ = _view(2, "0")
        self.assertNotEqual(prompt_a, prompt_b)


class NeutralPoseTests(unittest.TestCase):
    """The pose pin is what makes the set read as one person from N sides."""

    def test_pose_is_pinned_identically_across_views(self):
        poses = []
        for index in ("0", "1", "2", "3"):
            prompt, _, _ = _view(99, index)
            match = re.search(r"\b(?:He|She) is ([^.]+)\.", prompt)
            self.assertIsNotNone(match, f"no pose sentence in: {prompt[:120]}")
            poses.append(match.group(1))
        self.assertEqual(len(set(poses)), 1, f"pose moved between views: {poses}")
        # The pinned pose must be one of the curated neutral stances.
        self.assertIn(poses[0], _NEUTRAL_POSES)

    def test_pose_choice_is_deterministic_per_seed(self):
        prompt_a, _, _ = _view(5, "0")
        prompt_b, _, _ = _view(5, "0")
        self.assertEqual(prompt_a, prompt_b)

    def test_neutral_pose_off_leaves_the_engine_pool_free(self):
        prompt_on, _, _ = _view(11, "0", neutral_pose="On")
        prompt_off, _, _ = _view(11, "0", neutral_pose="Off")
        # With the pin removed the RNG stream gains a draw, so the outputs differ.
        self.assertNotEqual(prompt_on, prompt_off)


class UpstreamWiringTests(unittest.TestCase):
    """A wired preset turns THAT character around."""

    def test_wired_cosplayer_keeps_its_label_and_mask(self):
        from nodes.identity_forge_cosplayer import build_cosplayer_json
        raw = build_cosplayer_json("Grogu", 21, "Full character")
        prompt, label, count = _view(21, "0", upstream=raw)
        self.assertIn("Cosplaying as Grogu", prompt)
        self.assertNotIn("Latero", prompt)  # no cross-entry bleed
        self.assertEqual(count, 4)

    def test_empty_upstream_still_renders_a_person(self):
        prompt, _, _ = _view(3, "0")
        self.assertTrue(prompt.strip())
        self.assertNotIn("Cosplaying as", prompt)


class SchemaShapeTests(unittest.TestCase):
    """The frontend contract: widgets, controls, output order."""

    def setUp(self):
        self.schema = IdentityForgeTurnaround.define_schema()
        self.by_id = {spec.id: spec for spec in self.schema.inputs}

    def test_node_registers_under_conditioning_character(self):
        self.assertEqual(self.schema.node_id, "IdentityForgeTurnaround")
        self.assertEqual(self.schema.category, "conditioning/character")

    def test_output_order_is_prompt_label_count(self):
        self.assertEqual(
            [out.display_name for out in self.schema.outputs],
            ["prompt", "view_label", "view_count"],
        )

    def test_seed_defaults_to_fixed_and_index_to_increment(self):
        self.assertEqual(self.by_id["seed"].control_after_generate, "fixed")
        self.assertEqual(self.by_id["index"].control_after_generate, "increment")

    def test_index_options_cover_the_largest_preset(self):
        self.assertEqual(
            self.by_id["index"].options,
            ["0", "1", "2", "3", "4", "5"],
        )

    def test_steering_widgets_match_identityforge_option_lists(self):
        from nodes.identity_forge import IdentityForge
        forge_by_id = {
            spec.id: spec for spec in IdentityForge.define_schema().inputs
        }
        for name in ("gender", "wardrobe", "size_scale", "hair_color_scope",
                     "accessory_density", "location_setting"):
            self.assertEqual(
                self.by_id[name].options,
                list(forge_by_id[name].options),
                f"{name} options drifted from the main node",
            )
            self.assertEqual(
                self.by_id[name].default, forge_by_id[name].default,
                f"{name} default drifted from the main node",
            )

    def test_every_widget_carries_a_tooltip(self):
        # The pack's own convention and the node's only in-UI documentation.
        # 0.98.0 first shipped the six steering widgets with none at all.
        for spec in self.schema.inputs:
            self.assertTrue(
                (getattr(spec, "tooltip", None) or "").strip(),
                f"{spec.id} has no tooltip",
            )

    def test_steering_tooltips_reuse_the_main_node_text(self):
        # Not merely "present": the same sentence as the control it forwards,
        # so the two copies cannot drift as the main node's help is edited.
        from nodes.identity_forge import IdentityForge
        forge_by_id = {spec.id: spec for spec in IdentityForge.define_schema().inputs}
        for name in _STEER:
            self.assertIn(forge_by_id[name].tooltip, self.by_id[name].tooltip)

    def test_it_re_executes_every_queue(self):
        # An auto-advanced widget can otherwise be served from cache and the
        # view "sticks" (ComfyUI#11905) -- the same workaround the four
        # randomizers carry. This node auto-advances 'index' by design, so
        # losing this turns a six-run queue into six copies of one view.
        self.assertTrue(
            math.isnan(IdentityForgeTurnaround.fingerprint_inputs(seed=0, index="0")),
        )

    def test_upstream_is_an_optional_socket_not_a_multiline_box(self):
        spec = self.by_id["upstream"]
        self.assertTrue(spec.optional)
        self.assertTrue(getattr(spec, "force_input", False))
        self.assertFalse(getattr(spec, "multiline", False))


if __name__ == "__main__":
    unittest.main()
