"""Static integrity checks for the IdentityForge data layer.

Run directly (``python tests/validate_data.py``) for a human-readable report,
or import :func:`validate` from the unit tests. Exits non-zero on any failure.

Beyond field/constraint counts this validates *value* integrity: every
constraint trigger / excluded / required value and every archetype field value
must be a real option of the field it references — the class of bug that let
``hair_style="buzzed very short"`` slip into the archetypes earlier.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import re

from data.fields import (
    FIELD_DEFINITIONS, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS, ETHNICITY_REGION,
    STUDIO_BACKDROPS,
)
from data.constraints import CONSTRAINT_RULES
from data.templates import ARCHETYPES, COSTUME_SLOTS
from data.cosplayers import COSPLAYERS
from data.creatures import CREATURES, CREATURE_CLASSES, CREATURE_SLOTS

_EXPECTED_GROUPS = {
    "Demographics", "Body", "Face", "Hair", "Makeup",
    "Jewelry & Nails", "Clothing", "Setting & Shot",
}
_EXPECTED_OUTFIT_STYLES = {
    "casual", "smart casual", "business casual", "business formal",
    "evening formal", "cocktail semi-formal", "streetwear", "bohemian",
    "athletic", "resort vacation", "edgy alternative",
    "preppy", "vintage retro", "loungewear",
}
#: Hidden fields whose values are free-form prose (a costume override, a held
#: prop), so their values are not validated against an option pool — and they are
#: not allowed in a cosplayer's signature/physique maps.
_FREEFORM_FIELDS = {"outfit_description", "held_item"}


def _options(field: str) -> set[str]:
    meta = FIELD_DEFINITIONS.get(field, {})
    return set(meta.get("female_options", [])) | set(meta.get("male_options", []))


def validate() -> list[str]:
    """Return a list of error strings; empty means the data layer is valid."""
    errors: list[str] = []

    # --- fields -------------------------------------------------------
    if len(FIELD_DEFINITIONS) < 65:
        errors.append(f"FIELD_DEFINITIONS has {len(FIELD_DEFINITIONS)} fields; need >= 65")

    groups = {meta["group"] for meta in FIELD_DEFINITIONS.values()}
    missing_groups = _EXPECTED_GROUPS - groups
    if missing_groups:
        errors.append(f"missing field groups: {sorted(missing_groups)}")

    for name, meta in FIELD_DEFINITIONS.items():
        for key in ("group", "female_options", "male_options", "optional"):
            if key not in meta:
                errors.append(f"{name}: missing '{key}'")
        if not meta.get("female_options") or not meta.get("male_options"):
            errors.append(f"{name}: empty option pool")
        for sentinel in ("Random", "None"):
            if sentinel in meta.get("female_options", []) or sentinel in meta.get("male_options", []):
                errors.append(f"{name}: option pool contains reserved sentinel '{sentinel}'")

    for control in ("gender", "hair_color_scope"):
        if not FIELD_DEFINITIONS.get(control, {}).get("control"):
            errors.append(f"control field '{control}' missing or not marked control=True")

    # --- outfit descriptions (gendered buckets) ----------------------
    if set(OUTFIT_DESCRIPTIONS) != _EXPECTED_OUTFIT_STYLES:
        errors.append(f"OUTFIT_DESCRIPTIONS keys mismatch: {sorted(OUTFIT_DESCRIPTIONS)}")
    if set(OUTFIT_DESCRIPTIONS) != set(FIELD_DEFINITIONS.get("outfit_style", {}).get("female_options", [])):
        errors.append("OUTFIT_DESCRIPTIONS keys do not match outfit_style options")
    for style, buckets in OUTFIT_DESCRIPTIONS.items():
        if set(buckets) < {"female", "male", "unisex"}:
            errors.append(f"outfit style '{style}': missing female/male/unisex buckets")
            continue
        # Each gender must have enough variety (its bucket + the unisex bucket).
        for bucket in ("female", "male"):
            available = len(buckets[bucket]) + len(buckets["unisex"])
            if available < 4:
                errors.append(f"outfit style '{style}' ({bucket}): only {available} options")

    # --- constraints: structure AND value validity -------------------
    if len(CONSTRAINT_RULES) < 15:
        errors.append(f"CONSTRAINT_RULES has {len(CONSTRAINT_RULES)} rules; need >= 15")
    for i, rule in enumerate(CONSTRAINT_RULES):
        if rule.get("type") not in ("exclusion", "requirement"):
            errors.append(f"rule {i}: bad type {rule.get('type')!r}")
            continue
        field = rule.get("field")
        if field not in FIELD_DEFINITIONS:
            errors.append(f"rule {i}: unknown trigger field {field!r}")
        elif rule["value"] not in _options(field):
            errors.append(f"rule {i}: trigger value {rule['value']!r} not an option of {field}")

        if rule["type"] == "exclusion":
            target = rule.get("excludes_field")
            values = rule.get("excludes_values", [])
            if len(values) != len(set(values)):
                errors.append(f"rule {i}: duplicate excludes_values")
        else:
            target = rule.get("requires_field")
            values = [rule.get("requires_value")]
        if target not in FIELD_DEFINITIONS:
            errors.append(f"rule {i}: unknown target field {target!r}")
        else:
            bad = [v for v in values if v not in _options(target)]
            if bad:
                errors.append(f"rule {i}: values not options of {target}: {bad}")

    # --- archetypes: every value must be a real option ---------------
    if len(ARCHETYPES) < 20:
        errors.append(f"ARCHETYPES has {len(ARCHETYPES)}; need >= 20")
    for name, template in ARCHETYPES.items():
        for field, value in template.items():
            if field == "gender":
                if value not in ("Female", "Male", "Any"):
                    errors.append(f"archetype '{name}': bad gender {value!r}")
                continue
            if field not in FIELD_DEFINITIONS:
                errors.append(f"archetype '{name}': unknown field {field!r}")
            elif field not in _FREEFORM_FIELDS and value not in _options(field):
                errors.append(f"archetype '{name}': {field}={value!r} is not a valid option")

    # --- costume slots ------------------------------------------------
    for slot, pool in COSTUME_SLOTS.items():
        if not pool:
            errors.append(f"COSTUME_SLOTS['{slot}']: empty pool")
    for name, template in ARCHETYPES.items():
        costume = template.get("outfit_description", "")
        for slot in re.findall(r"\{(\w+)\}", costume):
            if slot not in COSTUME_SLOTS:
                errors.append(f"archetype '{name}': costume references unknown slot {{{slot}}}")

    # --- cosplayers: costume/signature/physique validity -------------
    if len(COSPLAYERS) < 50:
        errors.append(f"COSPLAYERS has {len(COSPLAYERS)}; need >= 50")
    for name, entry in COSPLAYERS.items():
        for key in ("franchise", "gender", "costume"):
            if not entry.get(key):
                errors.append(f"cosplayer '{name}': missing '{key}'")
        if entry.get("gender") not in ("Female", "Male"):
            errors.append(f"cosplayer '{name}': bad gender {entry.get('gender')!r}")
        # Masks: a full-mask character must carry a non-empty ``mask`` string (the
        # head covering kept out of ``costume`` so the Unmask toggle can drop it);
        # a face-visible character must not have one.
        mask = entry.get("mask")
        if entry.get("covers_face"):
            if not isinstance(mask, str) or not mask:
                errors.append(f"cosplayer '{name}': covers_face entry missing 'mask' text")
        elif mask is not None:
            errors.append(f"cosplayer '{name}': 'mask' set but covers_face is not True")
        # An optional signature prop is free-text; if present it must be a string.
        prop = entry.get("prop")
        if prop is not None and (not isinstance(prop, str) or not prop):
            errors.append(f"cosplayer '{name}': 'prop' must be a non-empty string")
        # signature is applied in both modes; physique only in Full character.
        # Every key must be a real field and every value a valid option for it.
        for section in ("signature", "physique"):
            for field, value in entry.get(section, {}).items():
                if field in _FREEFORM_FIELDS or field in ("gender", "hair_color_scope"):
                    errors.append(f"cosplayer '{name}': {section}.{field} is not allowed here")
                elif field not in FIELD_DEFINITIONS:
                    errors.append(f"cosplayer '{name}': {section} unknown field {field!r}")
                elif field == "age":
                    if value not in _options("age"):
                        errors.append(f"cosplayer '{name}': age={value!r} is not a valid option")
                elif value not in _options(field):
                    errors.append(f"cosplayer '{name}': {section}.{field}={value!r} is not a valid option")

    # --- creatures: structure + class coverage -----------------------
    # Slot text is free-form prose (rendered by the species path, not the human
    # field engine), so only structure is checked here, not value membership.
    if len(CREATURES) < 40:
        errors.append(f"CREATURES has {len(CREATURES)}; need >= 40")
    allowed_keys = {"class", "palette"} | set(CREATURE_SLOTS)
    class_counts = {cls: 0 for cls in CREATURE_CLASSES}
    for name, entry in CREATURES.items():
        if not isinstance(entry, dict):
            errors.append(f"creature '{name}': not a dict")
            continue
        for key in ("class", "palette", "head", "eyes", "integument"):
            if not isinstance(entry.get(key), str) or not entry.get(key):
                errors.append(f"creature '{name}': missing/empty required '{key}'")
        creature_class = entry.get("class")
        if creature_class not in CREATURE_CLASSES:
            errors.append(f"creature '{name}': unknown class {creature_class!r}")
        else:
            class_counts[creature_class] += 1
        for key, value in entry.items():
            if key not in allowed_keys:
                errors.append(f"creature '{name}': unexpected key {key!r}")
            elif value is not None and (not isinstance(value, str) or not value):
                errors.append(f"creature '{name}': slot {key!r} must be a non-empty string")
    thin = [cls for cls, count in class_counts.items() if count < 3]
    if thin:
        errors.append(f"creature classes with < 3 entries: {thin}")

    # --- studio backdrops: must be real location options -------------
    # The engine matches the resolved location against STUDIO_BACKDROPS by exact
    # string, so any entry missing from the location pool would silently break the
    # "Studio / solid backdrop" filter.
    location_options = _options("location")
    missing_backdrops = [b for b in STUDIO_BACKDROPS if b not in location_options]
    if missing_backdrops:
        errors.append(f"STUDIO_BACKDROPS not in location options: {sorted(missing_backdrops)}")

    # --- skin-tone affinity maps -------------------------------------
    skin_options = _options("skin_tone")
    for band, tones in SKIN_TONE_BANDS.items():
        bad = [t for t in tones if t not in skin_options]
        if bad:
            errors.append(f"SKIN_TONE_BANDS['{band}']: not skin_tone options: {bad}")
    ethnicities = _options("ethnicity")
    for ethnicity, band in ETHNICITY_REGION.items():
        if ethnicity not in ethnicities:
            errors.append(f"ETHNICITY_REGION: unknown ethnicity {ethnicity!r}")
        if band not in SKIN_TONE_BANDS:
            errors.append(f"ETHNICITY_REGION['{ethnicity}']: unknown band {band!r}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("VALIDATION PASSED")
    print(f"  Fields:      {len(FIELD_DEFINITIONS)}")
    print(f"  Constraints: {len(CONSTRAINT_RULES)}")
    print(f"  Archetypes:  {len(ARCHETYPES)}")
    print(f"  Cosplayers:  {len(COSPLAYERS)}")
    print(f"  Creatures:   {len(CREATURES)}")
    print(f"  Outfit sets: {len(OUTFIT_DESCRIPTIONS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
