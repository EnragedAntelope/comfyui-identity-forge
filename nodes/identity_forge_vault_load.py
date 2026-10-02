"""IdentityForgeVaultLoad node — recall a saved character from the local vault.

Pick a previously saved character and emit its resolved document as ``character_json``
— the *same* output type the Cosplayer / Archetype / Modifier nodes emit — so it wires
into IdentityForge's ``archetype_json`` and even stacks with other presets through the
optional ``upstream`` input.

Recall is deliberately a **string-preset merge**, not a per-widget round-trip: the saved
document flows back through IdentityForge's ``archetype_json`` and is applied by the
existing ``_parse_archetype_json`` / ``merge_preset_documents`` machinery. Because no
Combo widgets are re-populated, recall stays robust if field option lists change later —
renamed / removed options or fields degrade gracefully instead of becoming invalid widget
values.

If the selected character is missing (e.g. a workflow saved a name that was later
deleted), the node logs a warning and emits ``"{}"`` so the upstream passes through and
the graph never hard-fails.

The read / management engine (:func:`list_characters`, :func:`load_character`,
:func:`delete_characters`, :func:`rename_character`) is pure and testable without
ComfyUI; it reuses the path-safety helpers from
:mod:`nodes.identity_forge_vault_save`.
"""
from __future__ import annotations

import logging

import json
from pathlib import Path
from typing import Any

# Dual import: package-relative inside ComfyUI, absolute when run standalone.
#: 1.2.0: runtime messages go to the logger, not stdout. ComfyUI owns root
#: logging configuration, so there is deliberately no handler and no
#: logging.basicConfig() call here. The logger NAME carries what the old
#: '[NodeName]' message prefix used to say, so those prefixes went with them.
_LOG = logging.getLogger(__name__)

try:
    from .identity_forge import merge_preset_documents
    from .identity_forge_vault_save import (
        _CHARACTER_FILE, _META_FILE, _PROMPT_FILE, _entry_dir,
        _source_label, sanitize_name,
    )
except ImportError:  # pragma: no cover — standalone/test context
    from nodes.identity_forge import merge_preset_documents
    from nodes.identity_forge_vault_save import (
        _CHARACTER_FILE, _META_FILE, _PROMPT_FILE, _entry_dir,
        _source_label, sanitize_name,
    )

try:
    from comfy_api.latest import io  # type: ignore[import-not-found]
    _COMFY_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — exercised only outside ComfyUI
    _COMFY_AVAILABLE = False

#: Shown in the combo when the vault is empty (kept stable so saved workflows match).
_NO_CHARACTERS = "(no characters saved)"


def _is_entry(path: Path) -> bool:
    """A folder is a character iff it holds a ``character.json``."""
    return path.is_dir() and (path / _CHARACTER_FILE).is_file()


def list_character_names(vault_root: Path | str) -> list[str]:
    """Sorted names of every saved character (case-insensitive); ``[]`` if none."""
    root = Path(vault_root)
    if not root.is_dir():
        return []
    return sorted(
        (p.name for p in root.iterdir() if _is_entry(p)),
        key=str.lower,
    )


def _entry_info(path: Path) -> dict[str, Any]:
    """Read an entry's display metadata, preferring ``meta.json``.

    Falls back to the resolved document's ``_meta`` (so fork-style or hand-made
    entries without a sidecar still list cleanly).
    """
    name = path.name
    source_label, created = "", ""
    try:
        meta = json.loads((path / _META_FILE).read_text(encoding="utf-8"))
        source_label = str(meta.get("source_label", "") or "")
        created = str(meta.get("created", "") or "")
    except (OSError, ValueError, TypeError, AttributeError):
        # 1.5.5: a hand-edited meta.json that isn't a JSON object (a string, a
        # list, null) made meta.get(...) raise AttributeError, uncaught — this
        # made the WHOLE /identity_forge/vault/characters route 500 for every
        # entry, not just the malformed one. Falls through to the character.json
        # fallback below, same as any other unreadable sidecar.
        pass
    if not source_label:
        try:
            source_label = _source_label((path / _CHARACTER_FILE).read_text(encoding="utf-8"))
        except OSError:
            pass
    return {
        "name": name,
        "source_label": source_label,
        "created": created,
        "has_preview": (path / "preview.png").is_file(),
    }


def list_characters(vault_root: Path | str) -> list[dict[str, Any]]:
    """Sorted ``{name, source_label, created, has_preview}`` for every entry."""
    root = Path(vault_root)
    if not root.is_dir():
        return []
    return [_entry_info(p) for p in sorted(root.iterdir(), key=lambda p: p.name.lower())
            if _is_entry(p)]


def load_character(vault_root: Path | str, name: str) -> tuple[str, str]:
    """Return ``(character_json, prompt_text)`` for ``name``.

    Missing / unreadable entries yield ``("{}", "")`` so recall degrades to a
    no-op passthrough rather than raising.
    """
    try:
        entry = _entry_dir(Path(vault_root), name)
    except ValueError:
        return "{}", ""
    if not _is_entry(entry):
        return "{}", ""
    try:
        character_json = (entry / _CHARACTER_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # 1.5.5: this read was unwrapped, so a permission error or a non-UTF-8
        # character.json (both reachable: the sidecar can be hand-edited, or a
        # disk/permission issue can arrive between the is_file() check above and
        # this read) raised uncaught -- contradicting this function's own
        # "unreadable entries yield ('{}', '')" promise above.
        return "{}", ""
    try:
        prompt_text = (entry / _PROMPT_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        prompt_text = ""
    return character_json, prompt_text


def delete_characters(vault_root: Path | str, names: list[str]) -> list[str]:
    """Delete the named entries (ignoring unknown ones); return the survivors."""
    import shutil

    root = Path(vault_root)
    for name in names or []:
        try:
            entry = _entry_dir(root, name)
        except ValueError:
            continue
        # 1.5.5: was `entry.is_dir()` -- deletes ANY directory that sanitizes to
        # that name, not only a real vault entry. `_is_entry` requires a
        # character.json, matching what list_character_names considers an entry.
        if _is_entry(entry):
            shutil.rmtree(entry, ignore_errors=True)
    return list_character_names(root)


def rename_character(vault_root: Path | str, old: str, new: str) -> str:
    """Rename entry ``old`` → sanitized ``new``; return the final name.

    Raises ``ValueError`` if ``old`` is missing, ``new`` is unusable, or ``new``
    already exists (the caller surfaces a clear message).
    """
    root = Path(vault_root)
    src = _entry_dir(root, old)
    if not _is_entry(src):
        raise ValueError(f"No saved character named {old!r}.")
    if not sanitize_name(new):
        raise ValueError(f"Unusable new name: {new!r}.")
    dst = _entry_dir(root, new)
    if dst.exists() and dst != src:
        raise ValueError(f"A character named {dst.name!r} already exists.")
    src.rename(dst)
    # Keep the sidecar's display_name in step with the folder.
    meta_path = dst / _META_FILE
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["display_name"] = dst.name
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except (OSError, ValueError, TypeError):
        pass
    return dst.name


#: Sentinel :func:`_character_fingerprint` returns for "no selection" or "the
#: entry is gone/unreadable" -- any string works as long as it is stable, since
#: the node's own ``character`` input already changing is what the DEFAULT
#: cache key catches for those cases; this fingerprint only has to additionally
#: catch a change to the FILE under an unchanged selection.
_NO_FINGERPRINT = "none"


def _character_fingerprint(vault_root: Path | str, name: str) -> Any:
    """``(mtime_ns, size)`` of ``name``'s character.json, or a stable sentinel.

    ComfyUI's default cache key is built from the literal input VALUES, so
    recalling the same ``character`` name twice looks identical even after a
    Vault Save Overwrite, or a rename/delete from the Manage Vault modal,
    changed what is actually on disk -- the node would then serve a stale
    cached ``character_json`` instead of re-reading the file. Folding the
    selected entry's mtime + size into :meth:`fingerprint_inputs` makes a
    changed (or now-missing) file force a cache miss; an unchanged file still
    caches normally, unlike the NaN pattern the other preset nodes use (which
    disables caching on every queue, not only on a real change).
    """
    try:
        entry = _entry_dir(Path(vault_root), name)
        stat = (entry / _CHARACTER_FILE).stat()
        return (stat.st_mtime_ns, stat.st_size)
    except (ValueError, OSError):
        return _NO_FINGERPRINT


if _COMFY_AVAILABLE:

    # 1.5.5: was a byte-for-byte duplicate of identity_forge_vault_save._vault_root.
    # Only reachable when _COMFY_AVAILABLE is True here, which means vault_save's
    # own _COMFY_AVAILABLE is True too (same `comfy_api.latest` check, same
    # process), so this is safe where the top-of-file dual import is not: that one
    # imports names that exist unconditionally in vault_save, this one does not.
    try:
        from .identity_forge_vault_save import _vault_root
    except ImportError:  # pragma: no cover — standalone/test context
        from nodes.identity_forge_vault_save import _vault_root

    class IdentityForgeVaultLoad(io.ComfyNode):  # type: ignore[misc, valid-type]
        """Recall a saved character and emit it as a chainable character_json."""

        @classmethod
        def define_schema(cls) -> "io.Schema":
            names = list_character_names(_vault_root()) or [_NO_CHARACTERS]
            return io.Schema(
                node_id="IdentityForgeVaultLoad",
                display_name="Identity Forge Vault Load",
                category="conditioning/character",
                description=(
                    "Recall a character saved with Identity Forge Vault Save and emit it as "
                    "character_json — wire it into Identity Forge's 'archetype_json', or chain "
                    "after another preset via 'upstream'. Use the Refresh / Manage Vault "
                    "controls to update the list, preview, rename or delete entries."
                ),
                inputs=[
                    io.Combo.Input(
                        "character",
                        options=names,
                        default=names[0],
                        tooltip="Saved character to recall. Click Refresh after saving new "
                                "ones, or Manage Vault to browse with thumbnails.",
                    ),
                    io.String.Input(
                        "upstream",
                        default="",
                        optional=True,
                        force_input=True,
                        tooltip="Optional: connect another preset's character_json here to "
                                "stack presets. This saved character wins on overlap.",
                    ),
                ],
                outputs=[io.String.Output(display_name="character_json")],
            )

        @classmethod
        def fingerprint_inputs(cls, **kwargs: Any) -> Any:
            # 1.5.5: see _character_fingerprint. Folds the SELECTED entry's
            # mtime+size into the cache key so an Overwrite/rename/delete that
            # left the `character` widget unchanged still invalidates the cache.
            return _character_fingerprint(_vault_root(), kwargs.get("character", _NO_CHARACTERS))

        @classmethod
        def execute(cls, **kwargs: Any) -> "io.NodeOutput":
            character = kwargs.get("character", _NO_CHARACTERS)
            own = "{}"
            if character and character != _NO_CHARACTERS:
                own, _ = load_character(_vault_root(), character)
                if own == "{}":
                    _LOG.warning(f"Saved character {character!r} not "
                          f"found; passing upstream through.")
            character_json = merge_preset_documents(kwargs.get("upstream", ""), own)
            return io.NodeOutput(character_json)
