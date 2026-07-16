"""Preview the Cosplayer node end-to-end without ComfyUI.

Wires IdentityForgeCosplayer into IdentityForge exactly as the graph does, so you
can eyeball real output (prose + optional JSON) for any character.

Examples (run from the repo root)::

    python tests/preview_cosplayer.py "She-Hulk"
    python tests/preview_cosplayer.py "Captain Marvel" --male          # crossplay
    python tests/preview_cosplayer.py "2B" --full --seed 7 --json
    python tests/preview_cosplayer.py "Iron Man" --unmask              # helmet off
    python tests/preview_cosplayer.py "Indiana Jones" --props          # signature prop on
    python tests/preview_cosplayer.py --random-female --seed 3
    python tests/preview_cosplayer.py --list
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.cosplayers import get_cosplayer_names
from nodes.identity_forge import (
    generate_character, _parse_archetype_json, _COSPLAY_LABEL_KEY, _COVERS_FACE_KEY,
    _COVERS_BODY_KEY, _COVERS_HAIR_KEY, _CONTROL_FIELDS,
)
from nodes.identity_forge_cosplayer import (
    build_cosplayer_json, _MASK_DEFAULT, _MASK_OFF,
)


def render(
    character: str, gender: str, look_level: str, seed: int, mask_mode: str = _MASK_DEFAULT,
    include_prop: bool = False,
) -> tuple[str, str]:
    """Build the cosplay JSON and run it through the IdentityForge engine."""
    flat = _parse_archetype_json(
        build_cosplayer_json(character, seed, look_level, mask_mode, include_prop)
    )
    if not flat:
        raise SystemExit(f"No output for {character!r} — unknown name or empty Random pool.")
    label = flat.pop(_COSPLAY_LABEL_KEY, None)
    covers_face = bool(flat.pop(_COVERS_FACE_KEY, None))
    covers_body = bool(flat.pop(_COVERS_BODY_KEY, None))
    covers_hair = bool(flat.pop(_COVERS_HAIR_KEY, None))
    # The IdentityForge node forwards the parsed _meta gender; mirror that so the
    # person defaults to the character's gender unless --male/--female overrides.
    resolved_gender = gender or flat.get("gender", "Any")
    locked = {k: v for k, v in flat.items() if k not in _CONTROL_FIELDS}
    return generate_character(
        seed, resolved_gender, locked, cosplay_label=label, covers_face=covers_face,
        covers_body=covers_body, covers_hair=covers_hair,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview a Cosplayer render without ComfyUI.")
    parser.add_argument("character", nargs="?", help="Character name (see --list).")
    parser.add_argument("--list", action="store_true", help="List all character names and exit.")
    parser.add_argument("--random-any", action="store_true", help="Pick a random character.")
    parser.add_argument("--random-female", action="store_true", help="Random female-source character.")
    parser.add_argument("--random-male", action="store_true", help="Random male-source character.")
    parser.add_argument("--male", action="store_true", help="Render the person as male (crossplay).")
    parser.add_argument("--female", action="store_true", help="Render the person as female.")
    parser.add_argument("--full", action="store_true", help="Full character (lock physique too).")
    parser.add_argument("--unmask", action="store_true",
                        help="Drop the mask on a full-mask character (show the random head).")
    parser.add_argument("--props", action="store_true",
                        help="Include the character's signature prop (off by default, as in the node).")
    parser.add_argument("--seed", type=int, default=42, help="Seed (default 42).")
    parser.add_argument("--json", action="store_true", help="Also print the prompt_json.")
    args = parser.parse_args(argv)

    if args.list:
        names = get_cosplayer_names()
        print(f"{len(names)} characters:\n")
        print("\n".join(names))
        return 0

    if args.random_any:
        character = "Random — any"
    elif args.random_female:
        character = "Random — female"
    elif args.random_male:
        character = "Random — male"
    else:
        character = args.character
    if not character:
        parser.error("give a character name, a --random-* flag, or --list")

    gender = "Male" if args.male else "Female" if args.female else ""
    look_level = "Full character" if args.full else "Costume only"
    mask_mode = _MASK_OFF if args.unmask else _MASK_DEFAULT

    prose, js = render(character, gender, look_level, args.seed, mask_mode, args.props)
    print(prose)
    if args.json:
        print("\n--- prompt_json ---")
        print(js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
