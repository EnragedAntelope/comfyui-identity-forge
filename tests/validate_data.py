"""Static integrity checks for the IdentityForge data layer.

Run directly (``python tests/validate_data.py``) for a human-readable report,
or import :func:`validate` from the unit tests. Exits non-zero on any failure.

Beyond field/constraint counts this validates *value* integrity: every
constraint trigger / excluded / required value and every archetype field value
must be a real option of the field it references — the class of bug that let
``hair_style="buzzed very short"`` slip into the archetypes earlier.
"""
from __future__ import annotations

import ast
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from data.fields import (
    FIELD_DEFINITIONS, FIELD_FAMILIES, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS,
    ETHNICITY_REGION, STUDIO_BACKDROPS,
)
from data.constraints import CONSTRAINT_RULES
from data.templates import ARCHETYPES, COSTUME_SLOTS
from data.cosplayers import COSPLAYERS
from data.creatures import CREATURES, CREATURE_CLASSES, CREATURE_SLOTS
from data.user_options import USER_ADDED_FIELD_VALUES, USER_ADDED_OUTFIT_STYLES

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


def _duplicate_literal_keys(source_path: Path, dict_name: str) -> list[str]:
    """Duplicate string keys in the literal ``dict_name = {...}`` of a source file.

    Roster dicts are plain literals, so a re-added name silently overrides the
    earlier entry at import (the duplicate "Kang the Conqueror" bug — one of the
    two costumes was dead data). The runtime dict can't reveal this; the AST can.
    """
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        else:
            continue
        if dict_name in names and isinstance(node.value, ast.Dict):
            seen: set[str] = set()
            dups: list[str] = []
            for key in node.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    if key.value in seen:
                        dups.append(key.value)
                    seen.add(key.value)
            return dups
    return []


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
        # A duplicated pool value silently double-weights that draw. Weighting is
        # legitimate but must be the explicit "male_weights" mechanism, never a
        # duplicate entry (which also can't be seen in the widget or audited).
        for pool_key in ("female_options", "male_options"):
            pool = meta.get(pool_key, [])
            if len(pool) != len(set(pool)):
                dups = sorted({v for v in pool if pool.count(v) > 1})
                errors.append(f"{name}: duplicate values in {pool_key}: {dups}")
        # Draw-weight maps lean the random draw; every key must be a real option
        # (a typo would silently weight nothing). "weights" applies to both pools
        # (all-gender rarity); "male_weights" is the male-only overlay. Weights
        # may be floats so a value can be down-weighted below its peers' implicit
        # weight of 1 (e.g. rare bleached eyebrows, rare silky-glossy male hair).
        for weight_key, pool_keys in (
            ("weights", ("female_options", "male_options")),
            ("male_weights", ("male_options",)),
        ):
            weights = meta.get(weight_key)
            if weights is None:
                continue
            if not isinstance(weights, dict) or not weights:
                errors.append(f"{name}: {weight_key} must be a non-empty dict")
                continue
            for value, weight in weights.items():
                if not any(value in meta.get(pk, []) for pk in pool_keys):
                    errors.append(
                        f"{name}: {weight_key} key {value!r} not in "
                        f"{' or '.join(pool_keys)}")
                if isinstance(weight, bool) or not isinstance(weight, (int, float)) \
                        or weight <= 0:
                    errors.append(
                        f"{name}: {weight_key}[{value!r}] must be a positive number")

    for control in ("gender", "hair_color_scope"):
        if not FIELD_DEFINITIONS.get(control, {}).get("control"):
            errors.append(f"control field '{control}' missing or not marked control=True")

    # --- weighted families: each must partition its field's options exactly ---
    # The weighted random picker (_pick_family_weighted) draws from FIELD_FAMILIES;
    # if a field's families drift from its flat option list, some values become
    # unreachable or duplicated. This covers hair_style + every other grown field
    # (expression, mood, pose, lighting, location) from one check.
    for field_name, field_families in FIELD_FAMILIES.items():
        family_variants: list[str] = []
        for fam, meta in field_families.items():
            weight = meta.get("weight")
            if not isinstance(weight, int) or weight <= 0:
                errors.append(f"{field_name} family '{fam}': weight must be a positive int")
            if not meta.get("variants"):
                errors.append(f"{field_name} family '{fam}': empty variants")
            family_variants.extend(meta.get("variants", []))
        if len(family_variants) != len(set(family_variants)):
            errors.append(f"{field_name} FIELD_FAMILIES: duplicate variant across families")
        # user_options.json additions live outside every family by design (the
        # engine draws them via the implicit leftover family) — exempt them so a
        # user's extensions don't read as shipped-data drift.
        field_options = _options(field_name) - USER_ADDED_FIELD_VALUES.get(field_name, set())
        if set(family_variants) != field_options:
            missing = sorted(field_options - set(family_variants))
            extra = sorted(set(family_variants) - field_options)
            errors.append(
                f"{field_name} FIELD_FAMILIES variants != {field_name} options "
                f"(missing: {missing}, extra: {extra})"
            )

    # --- outfit descriptions (gendered buckets) ----------------------
    # User-registered styles (user_options.json "outfits" section) are exempt
    # from the shipped-set equality and the variety/bucket floors: the loader
    # already guarantees a user style carries at least one usable garment string,
    # and any missing bucket simply falls back to unisex at pick time.
    shipped_styles = set(OUTFIT_DESCRIPTIONS) - USER_ADDED_OUTFIT_STYLES
    if shipped_styles != _EXPECTED_OUTFIT_STYLES:
        errors.append(f"OUTFIT_DESCRIPTIONS keys mismatch: {sorted(shipped_styles)}")
    if set(OUTFIT_DESCRIPTIONS) != set(FIELD_DEFINITIONS.get("outfit_style", {}).get("female_options", [])):
        errors.append("OUTFIT_DESCRIPTIONS keys do not match outfit_style options")
    for style, buckets in OUTFIT_DESCRIPTIONS.items():
        if style in USER_ADDED_OUTFIT_STYLES:
            continue
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
    # A merged archetype may carry a ``variants`` block ({"Female"/"Male": {look}});
    # the base holds the soft-preference ``gender`` and shared fields, and each
    # variant is validated as its own field map (but must not restate ``gender``).
    if len(ARCHETYPES) < 20:
        errors.append(f"ARCHETYPES has {len(ARCHETYPES)}; need >= 20")

    def _check_archetype_fields(name: str, fields: dict, where: str) -> None:
        for field, value in fields.items():
            if field == "gender":
                if where != "base":
                    errors.append(f"archetype '{name}' {where}: 'gender' belongs on the base, not a variant")
                elif value not in ("Female", "Male", "Any"):
                    # A list gender would corrupt _meta.gender and the coin-flip.
                    errors.append(f"archetype '{name}': bad gender {value!r}")
                continue
            if field not in FIELD_DEFINITIONS:
                errors.append(f"archetype '{name}' {where}: unknown field {field!r}")
                continue
            # A list value is a curated set of alternatives the Archetype node
            # seed-picks from; each element must be valid on its own.
            if isinstance(value, list):
                if len(value) < 2:
                    errors.append(f"archetype '{name}' {where}: {field} list needs >= 2 alternatives")
                if len(value) != len(set(map(str, value))):
                    errors.append(f"archetype '{name}' {where}: {field} list has duplicates")
                for element in value:
                    if not isinstance(element, str) or not element:
                        errors.append(f"archetype '{name}' {where}: {field} list element {element!r} must be a non-empty string")
                    elif field not in _FREEFORM_FIELDS and element not in _options(field):
                        errors.append(f"archetype '{name}' {where}: {field}={element!r} is not a valid option")
                continue
            if field not in _FREEFORM_FIELDS and value not in _options(field):
                errors.append(f"archetype '{name}' {where}: {field}={value!r} is not a valid option")

    for name, template in ARCHETYPES.items():
        variants = template.get("variants")
        _check_archetype_fields(name, {k: v for k, v in template.items() if k != "variants"}, "base")
        if variants is not None:
            if not isinstance(variants, dict) or set(variants) - {"Female", "Male"} or not variants:
                errors.append(f"archetype '{name}': variants keys must be a non-empty subset of {{Female, Male}}")
            else:
                for vgender, look in variants.items():
                    if not isinstance(look, dict):
                        errors.append(f"archetype '{name}': variant '{vgender}' must be a dict")
                        continue
                    _check_archetype_fields(name, look, f"variant {vgender}")

    # --- costume slots ------------------------------------------------
    for slot, pool in COSTUME_SLOTS.items():
        if not pool:
            errors.append(f"COSTUME_SLOTS['{slot}']: empty pool")
    for name, template in ARCHETYPES.items():
        costumes = [template.get("outfit_description", "")]
        costumes += [look.get("outfit_description", "")
                     for look in (template.get("variants") or {}).values()
                     if isinstance(look, dict)]
        for costume in costumes:
            # outfit_description may be a list of alternative templates.
            for text in (costume if isinstance(costume, list) else [costume]):
                for slot in re.findall(r"\{(\w+)\}", text):
                    if slot not in COSTUME_SLOTS:
                        errors.append(f"archetype '{name}': costume references unknown slot {{{slot}}}")

    # --- roster dicts: no duplicate literal keys (AST-level) ----------
    for filename, dict_name in (
        ("data/cosplayers.py", "COSPLAYERS"),
        ("data/creatures.py", "CREATURES"),
        ("data/templates.py", "ARCHETYPES"),
    ):
        dups = _duplicate_literal_keys(ROOT / filename, dict_name)
        for dup in dups:
            errors.append(f"{filename}: duplicate {dict_name} key {dup!r} "
                          f"(later entry silently overrides the earlier one)")

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
        # Optional free-text eye-colour override: renders verbatim, intentionally
        # bypassing the eye_color option pool (for canonical red/violet/cat-slit eyes
        # without polluting the main node's believable-people dropdown). If present it
        # must be a non-empty string, and must not also be pinned in the signature.
        eyes = entry.get("eyes")
        if eyes is not None and (not isinstance(eyes, str) or not eyes):
            errors.append(f"cosplayer '{name}': 'eyes' must be a non-empty string")
        if eyes and entry.get("signature", {}).get("eye_color"):
            errors.append(f"cosplayer '{name}': set either 'eyes' or signature.eye_color, not both")
        # Optional free-text skin-colour override: anchors the body-paint colour in the
        # skin_tone slot (voiced verbatim, bypassing the human skin_tone pool). If
        # present it must be a non-empty string and must not also pin signature/physique
        # skin_tone. Only meaningful on a body-paint character (the anchor's home).
        skin = entry.get("skin")
        if skin is not None and (not isinstance(skin, str) or not skin):
            errors.append(f"cosplayer '{name}': 'skin' must be a non-empty string")
        if skin and (entry.get("signature", {}).get("skin_tone")
                     or entry.get("physique", {}).get("skin_tone")):
            errors.append(f"cosplayer '{name}': set either 'skin' or skin_tone, not both")
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
    allowed_keys = {"class", "palette", "palette_pool"} | set(CREATURE_SLOTS)
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
            elif key == "palette_pool":
                if not isinstance(value, list) or not value or not all(
                    isinstance(v, str) and v for v in value
                ):
                    errors.append(f"creature '{name}': 'palette_pool' must be a non-empty list of strings")
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
