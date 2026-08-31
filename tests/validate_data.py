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
    FIELD_DEFINITIONS, FIELD_FAMILIES, FIELD_HELP, OUTFIT_DESCRIPTIONS, SKIN_TONE_BANDS,
    PALETTE_ADJECTIVES, PATTERN_TAILS, WORN_ITEM_RES, SHOE_RE, LEADING_ARTICLE_RE,
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


#: Keys an alternate costume (``costumes`` list) overlay may carry. Mirrors
#: ``nodes.identity_forge_cosplayer._LOOK_OVERRIDE_KEYS`` (kept in sync by hand; the
#: test module intentionally has no import-time dependency on the node layer).
_LOOK_OVERRIDE_KEYS = frozenset({
    "costume", "signature", "mask", "covers_face", "covers_body",
    "covers_hair", "prop", "prop_costume", "body_paint", "skin", "eyes",
})


def _validate_field_map(name: str, section: str, mapping: dict) -> list[str]:
    """Validate a signature/physique map: real fields, valid options, no free-form."""
    errs: list[str] = []
    for field, value in mapping.items():
        if field in _FREEFORM_FIELDS or field in ("gender", "hair_color_scope"):
            errs.append(f"cosplayer '{name}': {section}.{field} is not allowed here")
        elif field not in FIELD_DEFINITIONS:
            errs.append(f"cosplayer '{name}': {section} unknown field {field!r}")
        elif field == "age":
            if value not in _options("age"):
                errs.append(f"cosplayer '{name}': age={value!r} is not a valid option")
        elif value not in _options(field):
            errs.append(f"cosplayer '{name}': {section}.{field}={value!r} is not a valid option")
    return errs


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

    # --- hair_color's "Natural only" scope key (0.91.1) ---------------
    # The scope control filters the hair_color randomization pool through
    # ``natural_hair_colors`` (nodes/identity_forge.py _build_option_pool). Two
    # ways that can rot silently, so both are pinned here:
    #   1. The filter FAILS OPEN -- `field_def.get("natural_hair_colors", base)`
    #      means a missing/renamed key is not an error, it is "no filter at all",
    #      and "Natural only" would quietly start emitting fantasy shades.
    #   2. A value that drifts out of the option pool is simply unreachable.
    # A "full_spectrum_hair_colors" twin also shipped in the field until 0.91.1,
    # read by nothing (the full spectrum IS the option pool) -- the last rule keeps
    # a dead lookalike from being re-added and mistaken for a live one.
    _hair = FIELD_DEFINITIONS.get("hair_color", {})
    natural = _hair.get("natural_hair_colors")
    if not natural:
        errors.append("hair_color: missing 'natural_hair_colors' -- the 'Natural only' "
                      "scope filter fails open without it (every fantasy shade returns)")
    else:
        stray = sorted(set(natural) - _options("hair_color"))
        if stray:
            errors.append(f"hair_color: natural_hair_colors values not in the option "
                          f"pool (unreachable): {stray}")
    dead = sorted(k for k in _hair
                  if k.endswith("_hair_colors") and k != "natural_hair_colors")
    if dead:
        errors.append(f"hair_color: {dead} is not read by the engine -- "
                      f"'natural_hair_colors' is the only scope key")

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

    # --- per-field tooltips (0.78.0) ---------------------------------
    # FIELD_HELP drives every field dropdown's tooltip. A stale key is invisible
    # (the node silently falls back to the generic mechanic line), so pin both
    # directions: no help for a field that no longer exists, and no user-visible
    # field left without help.
    # Mirrors nodes/identity_forge.py's _HIDDEN_FIELDS. Duplicated by hand rather
    # than imported, the same way _LOOK_OVERRIDE_KEYS is: this validator must not
    # depend on the node package. Both are asserted equal in tests/test_engine.py.
    hidden_fields = {"outfit_description", "held_item"}
    visible_fields = {
        name for name, field_def in FIELD_DEFINITIONS.items()
        if not field_def.get("control") and name not in hidden_fields
    }
    for name in sorted(set(FIELD_HELP) - set(FIELD_DEFINITIONS)):
        errors.append(f"FIELD_HELP has an entry for unknown field '{name}'")
    for name in sorted(visible_fields - set(FIELD_HELP)):
        errors.append(f"FIELD_HELP is missing an entry for field '{name}'")
    for name, text in sorted(FIELD_HELP.items()):
        if not text.strip():
            errors.append(f"FIELD_HELP['{name}'] is empty")

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

    # --- the 0.83.0 garment-only corpus contract ---------------------
    # The three Clothing widgets (footwear / clothing_color / clothing_pattern) were
    # drawn every render and never voiced, because OUTFIT_DESCRIPTIONS superseded them
    # and nobody retired them. They now COMPOSE with the generated outfit, which only
    # works while every shipped garment phrase leaves those axes to their own fields.
    #
    # Enforced here so the corpus cannot drift back. HARD rules only -- the axes with a
    # dedicated field that would otherwise render a DUPLICATE ITEM:
    #   * footwear   -> "gown ... and slingback pumps, in ankle boots"
    #   * jewellery  -> two necklaces, two pairs of earrings
    #   * bag        -> two bags
    #   * article    -> "a jewel-toned a satin slip gown"
    #
    # Colour and pattern words are deliberately NOT hard errors. They are MODIFIERS, not
    # items, so a garment naming its own is a legitimate override rather than a
    # duplicate -- "sequined evening gown", "denim overalls", the white bow tie of
    # white-tie dress. The engine's guards suppress that clause and pop the field, which
    # keeps the JSON honest. Measured at 0.83.0: 0.6% of strings state a colour and 4.8%
    # a pattern, nearly all of the latter being genuinely denim garments.
    for style, buckets in OUTFIT_DESCRIPTIONS.items():
        if style in USER_ADDED_OUTFIT_STYLES:
            continue        # user strings keep the old contract; guards handle them
        for bucket, items in buckets.items():
            for item in items:
                where = f"outfit '{style}' ({bucket}) {item!r}"
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"{where}: empty garment phrase")
                    continue
                if not item.isascii():
                    errors.append(f"{where}: must be plain ASCII")
                if LEADING_ARTICLE_RE.match(item):
                    errors.append(f"{where}: must NOT carry a leading article "
                                  f"(the engine articles the composed phrase)")
                if item != item.strip() or item.endswith((".", ",")):
                    errors.append(f"{where}: no surrounding whitespace or trailing punctuation")
                shoe = SHOE_RE.search(item)
                if shoe:
                    errors.append(f"{where}: names footwear ({shoe.group(0)!r}); the "
                                  f"`footwear` field owns that axis")
                for field, pattern in WORN_ITEM_RES.items():
                    hit = pattern.search(item)
                    if hit:
                        errors.append(f"{where}: names a worn item ({hit.group(0)!r}); "
                                      f"the `{field}` field owns that axis")

    # Every palette / pattern option must have a phrasing entry, or the composed prose
    # silently drops that clause -- the exact class of bug this phase exists to kill.
    for field, table, label in (("clothing_color", PALETTE_ADJECTIVES, "PALETTE_ADJECTIVES"),
                                ("clothing_pattern", PATTERN_TAILS, "PATTERN_TAILS")):
        options = set(FIELD_DEFINITIONS.get(field, {}).get("female_options", []))
        missing = sorted(options - set(table))
        if missing:
            errors.append(f"{label} is missing an entry for {missing}")
        stale = sorted(set(table) - options)
        if stale:
            errors.append(f"{label} names non-options {stale}")

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

    # --- cosplayers: near-duplicate names within one franchise --------
    # _duplicate_literal_keys above catches an EXACT repeated key. It cannot catch
    # the same character entered under a longer name ("Violet" + "Violet Parr" in
    # The Incredibles, 0.75.0), which passes every other check while quietly
    # double-weighting that character in the Random pool. Same franchise + one name
    # being a whole-word prefix/suffix of the other is the signature of that
    # mistake; genuinely distinct characters who share a surname ("Anna Williams" /
    # "Nina Williams") differ in the FIRST token, so they do not trip it.
    # A name extending another is not enough on its own: "(Force Ghost)" /
    # "(Julia Carpenter)" parentheticals are the established convention for a
    # deliberate variant or disambiguation, and "Brainiac 5" / "Starro Spore" are
    # genuinely separate characters. The duplicate signature is a matching name
    # PLUS a costume describing the same look, so both must hold.
    _by_franchise: dict[str, list[str]] = {}
    for name, entry in COSPLAYERS.items():
        _by_franchise.setdefault(entry.get("franchise", ""), []).append(name)
    for franchise, names in _by_franchise.items():
        for i, first in enumerate(names):
            for second in names[i + 1:]:
                shorter, longer = sorted((first, second), key=lambda n: len(n.split()))
                short_words, long_words = shorter.lower().split(), longer.lower().split()
                if len(short_words) >= len(long_words):
                    continue
                if long_words[:len(short_words)] != short_words:
                    continue
                if longer[len(shorter):].lstrip().startswith("("):
                    continue  # explicit variant/disambiguation suffix
                a = set(COSPLAYERS[first].get("costume", "").lower().split())
                b = set(COSPLAYERS[second].get("costume", "").lower().split())
                overlap = len(a & b) / max(1, len(a | b))
                if overlap >= 0.4:
                    errors.append(
                        f"cosplayer '{longer}' looks like a duplicate of '{shorter}' "
                        f"in franchise '{franchise}': the name extends it and the "
                        f"costumes overlap {overlap:.0%}. Refine the existing entry "
                        f"instead of adding a second.")

    # --- cosplayers: a parenthetical must not name a narrower franchise ---
    # A key's trailing "(...)" disambiguator may ABBREVIATE the entry's franchise
    # ("Mai (Avatar)" under "Avatar: The Last Airbender") or name a character,
    # alter ego, team or medium ("Blue Beetle (Ted Kord)", "Duke Nukem (video
    # game)"). It may never be a LONGER string that begins with the franchise:
    # that names an installment the pack has deliberately consolidated, so the
    # dropdown would contradict docs/reference/cosplayers.md. "Joker (Persona 5)"
    # under the franchise "Persona" was the one shipped violation, fixed at
    # 0.90.0 by renaming the key to "Joker (Persona)".
    #
    # Word-bounded on purpose, matching _name_already_carries_franchise: a bare
    # startswith would fire on "Persona" vs a hypothetical "Personal ...".
    for name, entry in COSPLAYERS.items():
        franchise = entry.get("franchise", "")
        match = re.match(r"^.*?\s*\(([^()]+)\)\s*$", name)
        if not franchise or not match:
            continue
        paren = match.group(1)
        if paren == franchise:
            continue
        if paren.casefold().startswith(franchise.casefold()) and \
                paren[len(franchise):len(franchise) + 1] in ("", " ", ":", "-"):
            errors.append(
                f"cosplayer '{name}': the parenthetical '{paren}' names something "
                f"narrower than its franchise '{franchise}'. Installments are not "
                f"separate franchises here -- use '({franchise})' so the key agrees "
                f"with docs/reference/cosplayers.md.")

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
        # ``prop_costume`` is the costume with a *worn* signature object removed,
        # swapped in only when the prop toggle is on so the object is not rendered
        # both on the belt and in the hand. Meaningless without a 'prop', and it must
        # actually differ from the costume it replaces.
        prop_costume = entry.get("prop_costume")
        if prop_costume is not None:
            if not isinstance(prop_costume, str) or not prop_costume:
                errors.append(f"cosplayer '{name}': 'prop_costume' must be a non-empty string")
            elif not prop:
                errors.append(f"cosplayer '{name}': 'prop_costume' set but no 'prop' to "
                              f"switch on; it would never be used")
            elif prop_costume == entry.get("costume"):
                errors.append(f"cosplayer '{name}': 'prop_costume' is identical to 'costume'; "
                              f"it must drop the worn object the prop puts in hand")
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
        # Optional extra searchable names (a codename vs. a civilian name). Schema
        # support only -- not authored for the existing roster, grows opportunistically.
        # Folded into the roster search index's haystack by generate_js_data.py.
        aliases = entry.get("aliases")
        if aliases is not None:
            if not isinstance(aliases, list) or not aliases:
                errors.append(f"cosplayer '{name}': 'aliases' must be a non-empty list")
            else:
                for alias in aliases:
                    if not isinstance(alias, str) or not alias or not alias.isascii():
                        errors.append(f"cosplayer '{name}': alias {alias!r} must be a "
                                      f"non-empty ASCII string")
        # Size-scale characters: ``size_scale`` flags the tier and MUST pair with a
        # hand-authored ``scale_prose`` (free text the builder locks into the height
        # slot so the scale reads in the lead sentence). Both texts must be
        # self-contained: naming a reference object ("beside a towering everyday
        # object", "three apples high", "insect-sized") makes T2I models render
        # that object next to the character.
        size_scale = entry.get("size_scale")
        scale_prose = entry.get("scale_prose")
        if size_scale is not None and size_scale not in ("giant", "tiny"):
            errors.append(f"cosplayer '{name}': size_scale must be 'giant' or 'tiny', got {size_scale!r}")
        if size_scale and (not isinstance(scale_prose, str) or not scale_prose):
            errors.append(f"cosplayer '{name}': size_scale requires a non-empty 'scale_prose'")
        # A feral entry may carry ``scale_prose`` on its own: it states a concrete
        # animal size ("about eight feet at the shoulder") without claiming the
        # giant/tiny *tier*, which is a scene control rather than a size. Everyone
        # else still needs the tier to justify the free-text height.
        if scale_prose is not None and not size_scale and entry.get("body_plan") != "feral":
            errors.append(f"cosplayer '{name}': scale_prose is only allowed with "
                          f"size_scale (or on a feral entry)")
        if scale_prose:
            combined = f"{entry.get('costume', '')} {scale_prose or ''}".lower()
            for banned in (r"beside (a|the)\b", r"everyday objects?", r"apples high",
                           r"\binsect[- ]sized", r"\bant[- ]sized", r"\bdoll[- ]sized",
                           r"\bpalm[- ]sized", r"\bdwarfing", r"next to (a|the)\b",
                           # 0.95.0: the same trap in comparative clothing -- "about
                           # the size of a large riding horse" renders the horse. It
                           # slipped past the list above because it names no object
                           # *position*, only a comparison. Caught on a real draft.
                           r"\bsize of (a|an|the)\b", r"\bas (big|large|tall|long) as\b",
                           r"\bthe size of\b", r"\bcompared to\b"):
                if re.search(banned, combined):
                    errors.append(
                        f"cosplayer '{name}': scale text matches comparison-object "
                        f"pattern {banned!r} (must be self-contained)")
        # signature is applied in both modes; physique only in Full character.
        # Every key must be a real field and every value a valid option for it.
        for section in ("signature", "physique"):
            errors += _validate_field_map(name, section, entry.get(section, {}))

        # --- feral body plan (0.95.0) ---------------------------------
        # A named beast rendered as itself rather than as a person in a suit. The
        # entry emits the Creature node's Species & Anatomy payload, so the keys it
        # feeds have to be checked here -- nothing downstream validates slot text
        # (that freedom is what lets a non-human escape the human option pools).
        body_plan = entry.get("body_plan")
        if body_plan is not None:
            if body_plan != "feral":
                errors.append(f"cosplayer '{name}': body_plan must be 'feral', "
                              f"got {body_plan!r}")
            # covers_face/covers_body are what drop the human face, jewellery,
            # ethnicity and skin tone; without them a beast renders a human head
            # and a necklace over its fur. The mask IS the head slot.
            if not entry.get("covers_face"):
                errors.append(f"cosplayer '{name}': a feral entry must set covers_face")
            if not entry.get("covers_body"):
                errors.append(f"cosplayer '{name}': a feral entry must set covers_body")
            creature_of = entry.get("creature_of")
            if not creature_of:
                errors.append(f"cosplayer '{name}': a feral entry needs 'creature_of' "
                              f"(the species noun the prose leads with)")
            elif not isinstance(creature_of, str):
                errors.append(f"cosplayer '{name}': creature_of must be a string")
            else:
                # It renders as "<label>, a {creature_of} with a {build} and {size}",
                # so it must be a BARE noun phrase. A "with" clause inside it collides
                # with the engine's own ("... a creature with a bulb on its back with a
                # stocky build"), and a leading article doubles the one the engine adds.
                # Spaced conjunctions only: a hyphenated compound ("crimson-and-gold
                # phoenix") is one adjective, not a clause.
                if re.search(r"\s(with|and)\s|,", creature_of):
                    errors.append(f"cosplayer '{name}': creature_of must be a bare noun "
                                  f"phrase -- no 'with'/'and'/comma clause "
                                  f"({creature_of!r})")
                if re.match(r"(?i)(a|an|the)\s", creature_of):
                    errors.append(f"cosplayer '{name}': creature_of must not lead with an "
                                  f"article; the engine adds one ({creature_of!r})")
                if creature_of != creature_of.strip() or creature_of[:1].isupper():
                    errors.append(f"cosplayer '{name}': creature_of must be lowercase and "
                                  f"unpadded ({creature_of!r})")
            # A feral entry has no worn look, so a held prop has no hand to hold it.
            # ``eyes`` overrides eye_color, which the head slot suppresses anyway;
            # a feral entry states its eyes in anatomy.eyes instead.
            for banned in ("prop", "prop_costume", "body_paint", "skin", "eyes"):
                if entry.get(banned):
                    errors.append(f"cosplayer '{name}': {banned!r} is not valid on a "
                                  f"feral entry")
            # Alternate looks vary a *costume*; a body plan is not a look.
            if entry.get("costumes"):
                errors.append(f"cosplayer '{name}': 'costumes' alternates are not "
                              f"supported on a feral entry")
        for key in ("anatomy", "poses", "creature_of", "creature_class"):
            if entry.get(key) is not None and body_plan != "feral":
                errors.append(f"cosplayer '{name}': {key!r} requires body_plan 'feral'")

        # --- anatomy_note (0.97.0) ------------------------------------
        # One sentence about the BODY, voiced ahead of the clothing exactly as
        # ``mask`` is. It exists so a MASKLESS entry can state a limb count where
        # the render acts on it -- see ``_ANATOMY_NOTE_KEY`` in
        # nodes/identity_forge.py and architecture.md -> "Limb and part counts".
        note = entry.get("anatomy_note")
        if note is not None:
            if not isinstance(note, str) or not note.strip():
                errors.append(f"cosplayer '{name}': 'anatomy_note' must be a "
                              f"non-empty string")
            elif body_plan == "feral":
                # A beast already has a per-slot ``anatomy`` path; carrying both
                # would describe the same body twice.
                errors.append(f"cosplayer '{name}': 'anatomy_note' is not valid on a "
                              f"feral entry -- use the 'anatomy' slots instead")
            else:
                if note != note.strip() or note[:1].isupper():
                    errors.append(f"cosplayer '{name}': anatomy_note is voiced mid-"
                                  f"sentence after 'He has ', so it must be lowercase "
                                  f"and unpadded ({note!r})")
                if note.endswith("."):
                    errors.append(f"cosplayer '{name}': anatomy_note must not end with "
                                  f"a period; the engine sentences it ({note!r})")
                # The note survives into a render that a DOWNSTREAM node may have
                # re-costumed (``_COSTUME_META_KEYS`` drops it only when the
                # downstream document supplies its own outfit). Naming a garment
                # here would put clothing in the body sentence, where it competes
                # with the real one. Garments belong in ``costume``.
                # Word-boundary anchored, and it has to stay that way: without
                # the \b the alternation matched INSIDE ordinary anatomy words --
                # "sleeveless" hit `sleeve`, "capelike" hit `cape`, "unbelted"
                # hit `belt`. A validator that rejects a correct entry is worse
                # than one that misses a wrong one.
                worn = re.search(
                    r"(?i)\b(shirt|sleeves?|jacket|coat|trousers|pants|dress|skirt|"
                    r"robes?|armou?r|breastplate|boots?|shoes?|gloves?|cape|cloak|"
                    r"belt|vest|tunic|uniform|helmet|mask)\b", note)
                if worn:
                    errors.append(f"cosplayer '{name}': anatomy_note describes the "
                                  f"BODY, not the clothes -- move "
                                  f"{worn.group(0)!r} into 'costume' ({note!r})")
        anatomy = entry.get("anatomy")
        if anatomy is not None:
            if not isinstance(anatomy, dict) or not anatomy:
                errors.append(f"cosplayer '{name}': 'anatomy' must be a non-empty dict")
            else:
                for slot, text in anatomy.items():
                    if slot not in CREATURE_SLOTS:
                        errors.append(f"cosplayer '{name}': anatomy slot {slot!r} is not "
                                      f"a creature slot {list(CREATURE_SLOTS)}")
                    elif slot in ("head", "integument"):
                        errors.append(f"cosplayer '{name}': anatomy.{slot} would collide "
                                      f"with the {'mask' if slot == 'head' else 'costume'} "
                                      f"key, which fills that slot")
                    if not isinstance(text, str) or not text.strip():
                        errors.append(f"cosplayer '{name}': anatomy.{slot} must be a "
                                      f"non-empty string")
        poses = entry.get("poses")
        if poses is not None and (not isinstance(poses, list) or not poses
                                  or not all(isinstance(p, str) and p for p in poses)):
            errors.append(f"cosplayer '{name}': 'poses' must be a non-empty list of "
                          f"non-empty strings")
        creature_class = entry.get("creature_class")
        if creature_class is not None and creature_class not in CREATURE_CLASSES:
            errors.append(f"cosplayer '{name}': creature_class {creature_class!r} is not "
                          f"one of {list(CREATURE_CLASSES)}")
        # Required on a feral entry, for the same reason ``creature_of`` is: the node
        # falls back to ``"Mammals"`` when it is absent, and a silent default is wrong
        # for every dragon, bird, spider and plant on the roster. Every shipped entry
        # sets it, so this pins a latent trap rather than fixing a live bug.
        if body_plan == "feral" and not creature_class:
            errors.append(f"cosplayer '{name}': a feral entry needs 'creature_class' "
                          f"(the node otherwise silently defaults it to 'Mammals')")

        # Optional ``costumes`` alternate-look list: each item is a plain costume
        # string or a dict overlay of _LOOK_OVERRIDE_KEYS. The node rng-picks one look
        # per seed on top of the canonical ``costume`` (which stays required above).
        costumes = entry.get("costumes")
        if costumes is not None:
            if not isinstance(costumes, list) or not costumes:
                errors.append(f"cosplayer '{name}': 'costumes' must be a non-empty list")
            else:
                for i, alt in enumerate(costumes):
                    where = f"costumes[{i}]"
                    if isinstance(alt, str):
                        if not alt:
                            errors.append(f"cosplayer '{name}': {where} is an empty string")
                        continue
                    if not isinstance(alt, dict):
                        errors.append(f"cosplayer '{name}': {where} must be a string or dict")
                        continue
                    bad_keys = set(alt) - _LOOK_OVERRIDE_KEYS
                    if bad_keys:
                        errors.append(f"cosplayer '{name}': {where} has non-overridable "
                                      f"keys {sorted(bad_keys)}")
                    if not (isinstance(alt.get("costume"), str) and alt.get("costume")):
                        errors.append(f"cosplayer '{name}': {where} needs a non-empty 'costume'")
                    # Free-text string overrides must be non-empty strings if present.
                    for key in ("mask", "prop", "skin", "eyes"):
                        if key in alt and not (isinstance(alt[key], str) and alt[key]):
                            errors.append(f"cosplayer '{name}': {where}.{key} must be a non-empty string")
                    if "signature" in alt:
                        errors += _validate_field_map(name, f"{where}.signature", alt["signature"])
                    # Mask coherence for the effective look: covering the face needs a
                    # mask string (from the overlay or falling back to the entry); a mask
                    # without a covered face is meaningless.
                    eff_covers = alt.get("covers_face", entry.get("covers_face"))
                    eff_mask = alt.get("mask", entry.get("mask"))
                    if eff_covers and not eff_mask:
                        errors.append(f"cosplayer '{name}': {where} covers the face but has no 'mask'")
                    if "mask" in alt and not alt.get("covers_face", entry.get("covers_face")):
                        errors.append(f"cosplayer '{name}': {where}.mask set but the look does not cover the face")

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
