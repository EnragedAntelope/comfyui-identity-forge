"""Optional user-supplied dropdown options (survive ``git pull``).

Drop a ``user_options.json`` in the pack root to add choices without editing the
source — so updates won't clobber them. Two sections, both optional::

    {
      "fields": {
        "ethnicity": ["Atlantean"],
        "hair_color": ["galaxy swirl", "holographic"],
        "location": ["a floating sky temple"]
      },
      "outfits": {
        "spacesuit": {
          "unisex": ["a sleek white EVA suit with a mirrored gold visor"],
          "female": ["a form-fitting flight suit with magnetic boots"],
          "male":   ["a bulky pressurized exosuit with chest controls"]
        }
      },
      "archetypes": {
        "Sky Pirate": {
          "gender": "Female", "outfit_style": "edgy alternative",
          "outfit_description": "a {color} longcoat over a leather bodice with brass buckles",
          "hair_color": "copper", "expression": "mischievous smile"
        }
      },
      "cosplayers": {
        "Custom Hero (My OC)": {
          "franchise": "Original", "gender": "Female",
          "costume": "a teal-and-silver bodysuit with a star emblem and white boots",
          "prop": "a glowing teal energy glaive held in one hand",
          "signature": {"hair_color": "electric blue", "hair_length": "long"},
          "physique": {"body_type": "athletic", "height": "tall"}
        },
        "Masked Vigilante (My OC)": {
          "franchise": "Original", "gender": "Male",
          "covers_face": true,
          "costume": "a matte-black tactical bodysuit with a grey chest sigil and a long cloak",
          "mask": "a full black helmet with narrow glowing eye slits",
          "physique": {"body_type": "athletic", "height": "tall"}
        }
      },
      "creatures": {
        "axolotl": {
          "class": "Marine Life", "palette": "pale pink",
          "head": "a wide-smiling axolotl head fringed with feathery external gills",
          "eyes": "tiny lidless dark eyes",
          "integument": "smooth translucent amphibian skin",
          "arms": "slender arms", "hands": "delicate four-fingered hands",
          "legs_feet": "small webbed feet", "tail": "a long finned tail"
        }
      }
    }

Reload the node / restart ComfyUI to apply. Notes:

* ``fields`` extends a dropdown's options. Every field can be extended *except*
  the control fields (``gender``, ``hair_color_scope``, ``location_setting``)
  and ``outfit_style`` / ``outfit_description`` — those are coupled to garment
  text and must go through the ``outfits`` section instead (see below).
* ``outfits`` adds a whole new outfit *style*: it registers the garment text
  **and** adds the style name to the ``outfit_style`` dropdown in one step, so
  the style can never be selected without clothing to back it. Buckets are
  ``unisex`` / ``female`` / ``male`` (any subset); ``unisex`` is always eligible,
  the gendered buckets are chosen by the ``wardrobe`` control. A style with no
  usable garment strings is skipped (it would otherwise emit an empty outfit).
* Custom hair colours appear only under the ``Full spectrum`` scope.
* For the three gender-specific fields (``bust``, ``facial_hair``,
  ``makeup_style``) custom options may not survive a live gender switch in the UI.
* ``archetypes`` adds presets to the Archetype node (same ``{field: value}``
  shape as the built-ins; ``outfit_description`` may use ``{slot}`` costume
  placeholders). ``cosplayers`` adds characters to the Cosplayer node (keys:
  ``franchise``, ``gender`` Female/Male, ``costume`` text, optional ``prop`` (a
  signature held item, voiced as "holding …" when the node's prop toggle is on),
  optional ``signature`` / ``physique`` ``{field: value}`` maps). A user entry whose name matches a
  built-in overrides it. Run ``python tests/validate_data.py`` to check that your
  field values are valid options.
* **Masked characters (the ``mask`` flow — easy to get wrong).** For a full
  helmet/mask, set ``"covers_face": true`` *and* put the head covering in a
  separate ``"mask"`` string, keeping it **out** of ``costume`` (note the
  "Masked Vigilante" example above). ``covers_face`` hides the randomized
  face/hair so only the costume shows; the ``mask`` is appended to the costume in
  the node's default mode, but kept separate so its ``Unmask (show face)`` toggle
  can drop the mask and reveal the random head under the suit. Omit both
  ``covers_face`` and ``mask`` whenever the face is visible (an open cowl, body
  paint, a domino mask).

The file is parsed as plain JSON — no code is executed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#: Default location of the user file: the pack root, next to __init__.py.
USER_OPTIONS_PATH = Path(__file__).resolve().parents[1] / "user_options.json"

#: Fields users may NOT extend through the flat ``fields`` section. Control
#: fields are engine-managed; ``outfit_style`` / ``outfit_description`` need
#: paired garment text, so they go through the ``outfits`` section instead.
_NOT_EXTENDABLE: frozenset[str] = frozenset({
    "gender", "hair_color_scope", "location_setting",
    "outfit_style", "outfit_description",
})

#: Garment buckets an ``outfits`` entry may define.
_OUTFIT_BUCKETS: tuple[str, ...] = ("unisex", "female", "male")


def _clean_strings(values: Any) -> list[str]:
    """Return the usable, sentinel-free strings from a JSON list (else [])."""
    if not isinstance(values, list):
        return []
    return [v for v in values if isinstance(v, str) and v and v not in ("Random", "None")]


def _apply_fields(
    fields: dict[str, Any], field_definitions: dict[str, dict[str, Any]]
) -> int:
    """Merge the ``fields`` section into option pools, in place. Returns count."""
    added = 0
    for name, extra in fields.items():
        if name in _NOT_EXTENDABLE or name not in field_definitions:
            continue
        values = _clean_strings(extra)
        meta = field_definitions[name]
        for key in ("female_options", "male_options"):
            pool = meta.get(key)
            if isinstance(pool, list):
                for value in values:
                    if value not in pool:
                        pool.append(value)
                        added += 1
    return added


def _apply_outfits(
    outfits: dict[str, Any],
    field_definitions: dict[str, dict[str, Any]],
    outfit_descriptions: dict[str, dict[str, list[str]]],
) -> int:
    """Register new outfit styles: merge garment text + add to the dropdown.

    A style is only added to the ``outfit_style`` dropdown if it carries at least
    one usable garment string, so the picker can never land on an empty outfit.
    Returns the number of garment strings added.
    """
    style_field = field_definitions.get("outfit_style")
    added = 0
    for style, buckets in outfits.items():
        if not isinstance(style, str) or not style or not isinstance(buckets, dict):
            continue
        cleaned = {b: _clean_strings(buckets.get(b)) for b in _OUTFIT_BUCKETS}
        if not any(cleaned.values()):  # nothing usable — skip the dangling key
            continue

        target = outfit_descriptions.setdefault(style, {})
        for bucket, values in cleaned.items():
            if not values:
                continue
            pool = target.setdefault(bucket, [])
            for value in values:
                if value not in pool:
                    pool.append(value)
                    added += 1

        # Register the style in the dropdown (both gender pools) now that it has
        # garment text behind it.
        if style_field is not None:
            for key in ("female_options", "male_options"):
                pool = style_field.get(key)
                if isinstance(pool, list) and style not in pool:
                    pool.append(style)
    return added


def apply_user_options(
    field_definitions: dict[str, dict[str, Any]],
    outfit_descriptions: dict[str, dict[str, list[str]]] | None = None,
    path: Path | None = None,
) -> int:
    """Merge ``user_options.json`` additions in place. Returns options added.

    Processes the ``fields`` section (dropdown extensions) and, when
    ``outfit_descriptions`` is provided, the ``outfits`` section (new outfit
    styles with their garment text). Fails closed — warns and changes nothing —
    on a missing or malformed file, so a typo can never break node loading.
    """
    path = path or USER_OPTIONS_PATH
    if not path.is_file():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:  # malformed JSON or unreadable
        print(f"[IdentityForge] Ignoring {path.name}: {exc}")
        return 0
    if not isinstance(data, dict):
        return 0

    added = 0
    fields = data.get("fields")
    if isinstance(fields, dict):
        added += _apply_fields(fields, field_definitions)

    outfits = data.get("outfits")
    if isinstance(outfits, dict) and outfit_descriptions is not None:
        added += _apply_outfits(outfits, field_definitions, outfit_descriptions)

    if added:
        print(f"[IdentityForge] Loaded {added} custom option(s) from {path.name}.")
    return added


def _load_user_section(path: Path, section: str) -> dict[str, Any]:
    """Return the dict ``section`` of the user JSON, or {} on any problem.

    Fails closed (warns, returns {}) on a missing/malformed file so a typo can
    never break node loading.
    """
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        print(f"[IdentityForge] Ignoring {path.name}: {exc}")
        return {}
    block = data.get(section) if isinstance(data, dict) else None
    return block if isinstance(block, dict) else {}


def _clean_field_map(value: Any) -> dict[str, str]:
    """Keep only ``{str: non-empty str}`` pairs from a JSON object (else {})."""
    if not isinstance(value, dict):
        return {}
    return {f: v for f, v in value.items() if isinstance(f, str) and isinstance(v, str) and v}


def apply_user_archetypes(archetypes: dict[str, dict], path: Path | None = None) -> int:
    """Merge the ``archetypes`` section of ``user_options.json`` in place.

    Each entry is a ``{field: value}`` preset (same shape as the built-ins;
    ``outfit_description`` may carry ``{slot}`` placeholders). A user entry whose
    name matches a built-in overrides it. Values are not strictly validated here
    — the engine's gender gate and constraints handle stray values at runtime,
    and ``tests/validate_data.py`` reports any invalid options. Returns count.
    """
    path = path or USER_OPTIONS_PATH
    added = 0
    for name, preset in _load_user_section(path, "archetypes").items():
        if not isinstance(name, str) or not name:
            continue
        cleaned = _clean_field_map(preset)
        if not cleaned:
            continue
        archetypes[name] = cleaned
        added += 1
    if added:
        print(f"[IdentityForge] Loaded {added} custom archetype(s) from {path.name}.")
    return added


#: Anatomy slots a ``creatures`` entry may fill (besides ``class`` / ``palette``).
_CREATURE_SLOTS: tuple[str, ...] = (
    "head", "eyes", "integument", "arms", "hands", "legs_feet", "wings", "tail", "extras",
)


def apply_user_creatures(creatures: dict[str, dict], path: Path | None = None) -> int:
    """Merge the ``creatures`` section of ``user_options.json`` in place.

    Each entry needs a ``class`` (which "Random - <class>" pool it joins), a
    ``palette`` (default integument colour) and the three core slots ``head`` /
    ``eyes`` / ``integument``; the limb / tail / wing / extras slots are optional.
    Slot text is free-form prose (not validated against ``data/fields.py`` — the
    species group has its own prose path), but it reaches the prompt, so keep it
    plain ASCII. A user entry whose name matches a built-in overrides it. Returns
    the number of creatures added. ``tests/validate_data.py`` checks the structure.
    """
    path = path or USER_OPTIONS_PATH
    added = 0
    for name, entry in _load_user_section(path, "creatures").items():
        if not isinstance(name, str) or not name or not isinstance(entry, dict):
            continue
        # The three core slots plus class/palette are what make a creature renderable.
        record: dict[str, str] = {}
        for key in ("class", "palette", "head", "eyes", "integument"):
            value = entry.get(key)
            if not isinstance(value, str) or not value:
                break
            record[key] = value
        else:
            for slot in _CREATURE_SLOTS:
                if slot in record:
                    continue
                value = entry.get(slot)
                if isinstance(value, str) and value:
                    record[slot] = value
            creatures[name] = record
            added += 1
            continue
        print(f"[IdentityForge] Skipping creature {name!r}: needs class, palette, "
              f"head, eyes and integument.")
    if added:
        print(f"[IdentityForge] Loaded {added} custom creature(s) from {path.name}.")
    return added


def apply_user_cosplayers(cosplayers: dict[str, dict], path: Path | None = None) -> int:
    """Merge the ``cosplayers`` section of ``user_options.json`` in place.

    Each entry needs a ``costume`` string (the only required key); ``franchise``
    defaults to "", ``gender`` to "Female" (used only for Random scoping),
    ``covers_face`` to ``False`` (set ``True`` for a fully masked head, and put the
    head covering in ``mask`` — see the module docstring), an optional ``prop``
    (a signature held item, emitted only when the Cosplayer node's prop toggle is
    on), and ``signature`` / ``physique`` to empty maps. A user entry whose name
    matches a built-in overrides it. Returns the number of characters added.
    """
    path = path or USER_OPTIONS_PATH
    added = 0
    for name, entry in _load_user_section(path, "cosplayers").items():
        if not isinstance(name, str) or not name or not isinstance(entry, dict):
            continue
        costume = entry.get("costume")
        if not isinstance(costume, str) or not costume:
            continue  # costume is what drives the look; an entry without it is useless
        gender = entry.get("gender")
        franchise = entry.get("franchise")
        mask = entry.get("mask")
        prop = entry.get("prop")
        cosplayers[name] = {
            "franchise": franchise if isinstance(franchise, str) else "",
            "gender": gender if gender in ("Female", "Male") else "Female",
            "covers_face": bool(entry.get("covers_face", False)),
            "costume": costume,
            "mask": mask if isinstance(mask, str) else "",
            "prop": prop if isinstance(prop, str) else "",
            "signature": _clean_field_map(entry.get("signature")),
            "physique": _clean_field_map(entry.get("physique")),
        }
        added += 1
    if added:
        print(f"[IdentityForge] Loaded {added} custom cosplayer(s) from {path.name}.")
    return added
