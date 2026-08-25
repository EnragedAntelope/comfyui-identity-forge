"""Tests for the IdentityForgeTurnaround node.

The node's whole contract: take ONE resolved character and emit every camera
view of it at once, with nothing but the camera moving between them. Every test
here exists because its violation would silently produce a useless reference
set — a different person per angle, a pose that reads differently from each
side, or a set that does not actually fan out downstream.
"""
from __future__ import annotations

import json
import re
import unittest

from data.fields import FIELD_DEFINITIONS
from nodes.identity_forge import IdentityForge
from nodes.identity_forge_cosplayer import IdentityForgeCosplayer
from nodes.identity_forge_turnaround import (
    _FRAMINGS, _KEEP_POSE, _NEUTRAL_POSES, _REPLAYED_STEERING, _ROTATION_LABELS,
    _VIEW_SETS, IdentityForgeTurnaround, compose_shot, replay_steering,
    resolve_turnaround,
)

_FRAMING_RE = re.compile(r"the framing is ([^,]+(?:, [^,]+)?)(?=, composed| and |, and |\.)")

#: Every rotation that appears in any selectable set, for the "camera only" strip.
_ALL_SHOTS = sorted(
    {compose_shot(framing, rotation)
     for framing in _FRAMINGS
     for rotation in _ROTATION_LABELS},
    key=len, reverse=True,
)


def _forge(seed: int, **steer: str) -> tuple[str, str]:
    """Run the main node the way a user would, and return (prose, prompt_json)."""
    kwargs: dict = {spec.id: "Random" for spec in IdentityForge.define_schema().inputs}
    kwargs.update(
        seed=seed, archetype_json="", set_all_fields="Off", gender="Any",
        wardrobe="Match gender", size_scale="Auto", hair_color_scope="Natural only",
        accessory_density="Balanced", location_setting="Any indoor/outdoor",
    )
    kwargs.update(steer)
    return IdentityForge.execute(**kwargs).args


def _cosplayer_document(name: str, seed: int = 7) -> str:
    kwargs = {spec.id: getattr(spec, "default", None)
              for spec in IdentityForgeCosplayer.define_schema().inputs}
    kwargs.update(character=name, seed=seed, upstream="")
    return IdentityForgeCosplayer.execute(**kwargs).args[0]


def _strip_camera(prompt: str) -> str:
    """Remove every phrase this node is allowed to change, longest match first."""
    for shot in _ALL_SHOTS:
        prompt = prompt.replace(shot, "<SHOT>")
    return prompt


class VocabularySanityTests(unittest.TestCase):
    """Every value this node pins must be an exact engine pool value."""

    def test_every_rotation_is_an_exact_shot_type_value(self):
        pool = set(FIELD_DEFINITIONS["shot_type"]["female_options"])
        for rotation in _ROTATION_LABELS:
            self.assertIn(rotation, pool)

    def test_every_framing_clause_is_an_exact_shot_type_value(self):
        pool = set(FIELD_DEFINITIONS["shot_type"]["female_options"])
        for label, distance in _FRAMINGS.items():
            if distance:
                self.assertIn(distance, pool, label)

    def test_composed_shots_are_free_text_the_gender_gate_lets_through(self):
        # compose_shot emits a value that is NOT in the pool, which is only safe
        # because shot_type's two gender pools are identical -- _gender_permits
        # passes anything then. If they ever diverge, every composed shot is
        # dropped and the turnaround silently loses its camera.
        field = FIELD_DEFINITIONS["shot_type"]
        self.assertEqual(field["female_options"], field["male_options"])

    def test_every_neutral_pose_is_an_exact_pool_value_in_both_genders(self):
        field = FIELD_DEFINITIONS["pose"]
        for pose in _NEUTRAL_POSES:
            self.assertIn(pose, field["female_options"], pose)
            self.assertIn(pose, field["male_options"], pose)

    def test_neutral_poses_are_standing_and_symmetric(self):
        # An asymmetric or seated stance reads as a different body from each
        # side, which defeats the entire point of a turnaround.
        for pose in _NEUTRAL_POSES:
            self.assertTrue(pose.startswith("standing"), pose)
            for asymmetric in ("one hip", "one hand", "one leg", "over one shoulder"):
                self.assertNotIn(asymmetric, pose)

    def test_keep_pose_sentinel_is_not_a_real_pose(self):
        self.assertNotIn(_KEEP_POSE, FIELD_DEFINITIONS["pose"]["female_options"])
        self.assertNotIn(_KEEP_POSE, _NEUTRAL_POSES)

    def test_every_set_starts_front_on_and_names_its_size(self):
        for name, rotations in _VIEW_SETS.items():
            self.assertEqual(rotations[0], "straight-on eye level", name)
            self.assertIn(f"({len(rotations)})", name)
            self.assertEqual(len(rotations), len(set(rotations)), f"{name} repeats a view")

    def test_the_six_view_set_covers_every_labelled_rotation(self):
        self.assertEqual(set(_VIEW_SETS["Turnaround (6)"]), set(_ROTATION_LABELS))


class ComposeShotTests(unittest.TestCase):
    def test_a_framing_precedes_the_rotation(self):
        self.assertEqual(
            compose_shot("Full body", "side profile"),
            "full body shot, side profile",
        )

    def test_unspecified_framing_emits_the_rotation_alone(self):
        self.assertEqual(compose_shot("Unspecified", "side profile"), "side profile")

    def test_an_unknown_framing_degrades_to_the_rotation_alone(self):
        self.assertEqual(compose_shot("nonsense", "side profile"), "side profile")


class TurnaroundStabilityTests(unittest.TestCase):
    """Views of one document differ ONLY in the camera."""

    def test_every_view_shares_all_non_camera_prose(self):
        _, document = _forge(42)
        prompts, _ = resolve_turnaround(document, "Turnaround (6)", "Full body",
                                        _NEUTRAL_POSES[0])
        self.assertEqual(len(prompts), 6)
        stripped = {_strip_camera(prompt) for prompt in prompts}
        self.assertEqual(len(stripped), 1,
                         "non-camera prose drifted between views of one character")

    def test_every_view_states_its_own_camera(self):
        _, document = _forge(42)
        prompts, _ = resolve_turnaround(document, "Turnaround (6)", "Full body",
                                        _NEUTRAL_POSES[0])
        framings = [_FRAMING_RE.search(prompt) for prompt in prompts]
        self.assertTrue(all(framings), "a view emitted no framing clause")
        self.assertEqual(len({match.group(1) for match in framings}), 6)
        for match in framings:
            self.assertIn("full body shot", match.group(1))

    def test_a_cosplayer_keeps_its_costume_and_mask_in_every_view(self):
        for name in ("Iron Man", "She-Hulk", "Darth Vader", "Pikachu", "Godzilla"):
            _, document = _forge(5, archetype_json=_cosplayer_document(name))
            prompts, _ = resolve_turnaround(document, "Turnaround (6)", "Full body",
                                            _NEUTRAL_POSES[0])
            self.assertEqual(len({_strip_camera(p) for p in prompts}), 1, name)
            for prompt in prompts:
                self.assertIn(f"Cosplaying as {name}", prompt)

    def test_it_replays_the_document_rather_than_re_rolling_it(self):
        # The fidelity guarantee the whole design rests on: pin the document's
        # OWN shot and pose and the prose must come back byte-identical, at a
        # seed the original run never saw. Includes wardrobe "Any", which is the
        # case _REPLAYED_STEERING exists for -- without it the engine rebuilds a
        # mixed-gender character under "Match gender" and returns a different
        # person entirely.
        for steer in ({}, {"wardrobe": "Any"}, {"wardrobe": "Masculine", "gender": "Female"},
                      {"hair_color_scope": "Full spectrum"}, {"accessory_density": "Maximal"}):
            for seed in range(12):
                original, document = _forge(seed, **steer)
                fields = {name: value
                          for group, values in json.loads(document).items()
                          if group != "_meta" and isinstance(values, dict)
                          for name, value in values.items()}
                replayed, _ = resolve_turnaround(
                    document, "Front + profile (2)", "Unspecified",
                    fields.get("pose", _KEEP_POSE),
                )
                # View 0 pins the document's own rotation only if it happened to
                # be the front shot, so compare on the shot the document names.
                rebuilt = replayed[0].replace(
                    "straight-on eye level", fields.get("shot_type", ""))
                self.assertEqual(rebuilt, original, f"{steer} seed {seed}")

    def test_the_documents_gender_survives_into_every_view(self):
        # The controls do not share the fields' "Random" vocabulary. Passing
        # "Random" to `gender` is not "Any", so execute() never falls through to
        # the document's _meta.gender and re-rolls it instead -- measured, this
        # turned a woman into a man between the main node and the turnaround.
        for seed in range(20):
            original, document = _forge(seed)
            subject = original.split(" with ")[0]
            prompts, _ = resolve_turnaround(document, "Front + back (2)", "Full body",
                                            _NEUTRAL_POSES[0])
            for prompt in prompts:
                self.assertEqual(prompt.split(" with ")[0], subject, f"seed {seed}")

    def test_no_control_input_is_handed_a_field_value(self):
        # The engine logs and ignores an out-of-vocabulary control rather than
        # raising, so this is the only place the mistake is visible.
        from nodes.identity_forge import _CONTROL_FIELDS
        forge_inputs = {spec.id: spec for spec in IdentityForge.define_schema().inputs}
        controls = [name for name in forge_inputs
                    if name in _CONTROL_FIELDS or name in _REPLAYED_STEERING
                    or name in ("gender", "size_scale", "set_all_fields")]
        self.assertTrue(controls)
        for name in controls:
            spec = forge_inputs[name]
            options = getattr(spec, "options", None) or []
            self.assertIn(spec.default, options, name)
            self.assertNotIn("Random", options, f"{name} would silently accept 'Random'")

    def test_different_characters_give_different_sets(self):
        _, first = _forge(1)
        _, second = _forge(2)
        prompts_a, _ = resolve_turnaround(first, "Front + back (2)", "Full body",
                                          _NEUTRAL_POSES[0])
        prompts_b, _ = resolve_turnaround(second, "Front + back (2)", "Full body",
                                          _NEUTRAL_POSES[0])
        self.assertNotEqual(prompts_a[0], prompts_b[0])

    def test_it_is_deterministic(self):
        _, document = _forge(3)
        first = resolve_turnaround(document, "Turnaround (4)", "Waist up", _NEUTRAL_POSES[1])
        second = resolve_turnaround(document, "Turnaround (4)", "Waist up", _NEUTRAL_POSES[1])
        self.assertEqual(first, second)


class ViewSetTests(unittest.TestCase):
    def test_each_set_emits_exactly_its_own_count(self):
        _, document = _forge(11)
        for name, rotations in _VIEW_SETS.items():
            prompts, labels = resolve_turnaround(document, name, "Full body",
                                                 _NEUTRAL_POSES[0])
            self.assertEqual(len(prompts), len(rotations), name)
            self.assertEqual(len(labels), len(rotations), name)

    def test_an_unknown_set_falls_back_to_the_full_turnaround(self):
        _, document = _forge(11)
        prompts, _ = resolve_turnaround(document, "nonsense", "Full body",
                                        _NEUTRAL_POSES[0])
        self.assertEqual(len(prompts), 6)

    def test_labels_are_numbered_in_rotation_order_and_filename_safe(self):
        _, document = _forge(11)
        _, labels = resolve_turnaround(document, "Turnaround (6)", "Full body",
                                       _NEUTRAL_POSES[0])
        self.assertEqual(labels[0], "1-front")
        self.assertEqual([label.split("-", 1)[0] for label in labels],
                         [str(n) for n in range(1, 7)])
        for label in labels:
            self.assertRegex(label, r"^[0-9a-z-]+$")


class PoseTests(unittest.TestCase):
    def test_the_chosen_stance_is_voiced_in_every_view(self):
        _, document = _forge(8)
        for pose in _NEUTRAL_POSES:
            prompts, _ = resolve_turnaround(document, "Turnaround (4)", "Full body", pose)
            for prompt in prompts:
                self.assertIn(pose, prompt)

    def test_keep_pose_leaves_the_characters_own_stance_alone(self):
        _, document = _forge(8)
        own = {name: value
               for group, values in json.loads(document).items()
               if group != "_meta" and isinstance(values, dict)
               for name, value in values.items()}.get("pose")
        self.assertIsNotNone(own, "seed 8 resolved no pose; pick another seed")
        prompts, _ = resolve_turnaround(document, "Turnaround (4)", "Full body", _KEEP_POSE)
        for prompt in prompts:
            self.assertIn(own, prompt)

    def test_keep_pose_still_holds_the_pose_still_across_views(self):
        _, document = _forge(8)
        prompts, _ = resolve_turnaround(document, "Turnaround (6)", "Full body", _KEEP_POSE)
        self.assertEqual(len({_strip_camera(prompt) for prompt in prompts}), 1)


class ReplaySteeringTests(unittest.TestCase):
    def test_it_reads_the_documents_recorded_controls(self):
        _, document = _forge(4, wardrobe="Any", hair_color_scope="Full spectrum")
        self.assertEqual(
            replay_steering(document),
            {"wardrobe": "Any", "hair_color_scope": "Full spectrum"},
        )

    def test_every_replayed_control_is_actually_recorded_in_meta(self):
        # If the main node stops writing one of these into _meta, the replay
        # silently falls back to a default and rebuilds a different person.
        _, document = _forge(4)
        meta = json.loads(document)["_meta"]
        for name in _REPLAYED_STEERING:
            self.assertIn(name, meta)

    def test_garbage_and_absence_degrade_to_the_widget_defaults(self):
        for raw in ("", "not json {{", "[1,2,3]", "{}", '{"_meta": "nope"}',
                    '{"_meta": {"wardrobe": 7}}'):
            self.assertEqual(replay_steering(raw), _REPLAYED_STEERING, raw)

    def test_an_empty_document_still_renders_a_person(self):
        prompts, labels = resolve_turnaround("", "Front + back (2)", "Full body",
                                             _NEUTRAL_POSES[0])
        self.assertEqual(len(prompts), 2)
        self.assertEqual(labels, ["1-front", "2-back"])
        for prompt in prompts:
            self.assertTrue(prompt.strip())


class SchemaShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = IdentityForgeTurnaround.define_schema()
        cls.by_id = {spec.id: spec for spec in cls.schema.inputs}

    def test_node_registers_under_conditioning_character(self):
        self.assertEqual(self.schema.node_id, "IdentityForgeTurnaround")
        self.assertEqual(self.schema.category, "conditioning/character")

    def test_both_outputs_are_lists(self):
        names = [output.display_name for output in self.schema.outputs]
        self.assertEqual(names, ["prompt", "view_label"])
        for output in self.schema.outputs:
            self.assertTrue(
                output.is_output_list,
                f"{output.display_name} must be a list output -- it is what makes "
                "one queue render the whole set",
            )

    def test_it_exposes_only_camera_controls(self):
        # The 0.98.0 draft re-exposed six IdentityForge steering widgets, so a
        # user could not tell which node's copy won and silently lost the other
        # ~75 fields. The character is configured upstream now; anything here
        # that names an engine field other than the two the camera owns is a
        # regression back to that.
        self.assertEqual(list(self.by_id), ["character_json", "views", "framing", "pose"])
        forge_inputs = {spec.id for spec in IdentityForge.define_schema().inputs}
        overlap = set(self.by_id) & forge_inputs
        self.assertEqual(overlap, {"pose"},
                         "only 'pose' may share a name with an IdentityForge input")

    def test_no_widget_auto_advances(self):
        # The corollary of having no fingerprint_inputs: this node is a pure
        # function, so ComfyUI's normal caching is correct. A widget with
        # control_after_generate would reintroduce ComfyUI#11905 and need the
        # NaN signature back (architecture.md -> "Seeded nodes re-roll every queue").
        for spec in self.schema.inputs:
            self.assertIsNone(getattr(spec, "control_after_generate", None), spec.id)
        # `vars`, not `hasattr`: the real comfy_api's ComfyNode base declares
        # fingerprint_inputs (raising NotImplementedError), so hasattr is True on
        # every node and would assert nothing. The stub declares no such method,
        # which is exactly how a hasattr check passes here and fails in ComfyUI.
        self.assertNotIn("fingerprint_inputs", vars(IdentityForgeTurnaround))

    def test_character_json_is_a_required_socket_not_a_multiline_box(self):
        spec = self.by_id["character_json"]
        self.assertFalse(spec.optional)
        self.assertTrue(getattr(spec, "force_input", False))
        self.assertFalse(getattr(spec, "multiline", False))

    def test_combo_defaults_are_offered_options(self):
        for name in ("views", "framing", "pose"):
            spec = self.by_id[name]
            self.assertIn(spec.default, spec.options, name)

    def test_every_widget_carries_a_tooltip(self):
        for spec in self.schema.inputs:
            self.assertTrue((spec.tooltip or "").strip(), f"{spec.id} has no tooltip")

    def test_every_output_carries_a_tooltip(self):
        for output in self.schema.outputs:
            self.assertTrue((output.tooltip or "").strip(),
                            f"{output.display_name} has no tooltip")

    def test_execute_returns_two_matching_lists(self):
        _, document = _forge(9)
        prompts, labels = IdentityForgeTurnaround.execute(
            character_json=document, views="Turnaround (4)",
            framing="Full body", pose=_NEUTRAL_POSES[0],
        ).args
        self.assertIsInstance(prompts, list)
        self.assertIsInstance(labels, list)
        self.assertEqual(len(prompts), 4)
        self.assertEqual(len(labels), 4)


if __name__ == "__main__":
    unittest.main()
