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
