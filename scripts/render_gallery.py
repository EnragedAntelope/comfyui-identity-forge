"""Render, record and publish the gallery images for roster entries.

The three galleries show one image per cosplayer, archetype and creature.
Keeping ~2,200 of those honest by hand is not possible, so the build is
content-addressed: every image records a hash of the entry that produced it,
and an entry whose text has changed is reported stale until it is re-rendered.

    python scripts/render_gallery.py --check            # the CI gate
    python scripts/render_gallery.py --missing          # render what is absent
    python scripts/render_gallery.py --kind cosplay --entry "Jack Skellington" --publish
    python scripts/render_gallery.py --entry "Hisoka Morow" --dry-run   # read the prose

``--check`` is the gate. It needs no GPU, no ComfyUI and no network: it compares
``gallery/render_manifest.json`` against the data layer and fails when they have
drifted, so editing an entry tells you its image is now a lie.

Rendering needs a running ComfyUI (default the disposable test instance on
:8288). Two design decisions are worth knowing before changing anything here:

* **The prompt is resolved in this process, not by the instance.** An entry name
  is a dropdown widget value on the preset nodes, and a running ComfyUI caches
  its data layer at startup - it would reject a brand-new name at ``/prompt``
  validation until restarted. So this script imports the real node classes,
  calls their ``execute()`` in the same order the workflows wire them, and posts
  a graph containing **no Identity Forge nodes at all**: just the loaders, a
  ``CLIPTextEncode`` fed the finished literal string, sampler, decode. The target
  instance never has to know the entry exists, nothing is installed on it, and no
  restart is ever needed.
* **Nothing is left behind on the instance.** The graph ends in ``PreviewImage``,
  which writes to ComfyUI's temp dir and is fetched straight back over HTTP;
  ComfyUI clears it on its own. ``--save-originals`` switches to ``SaveImage``
  when full-resolution originals are wanted on the ComfyUI side.

Queue etiquette: prompts go in front-of-queue (``{"front": true}``), which
inserts at position 0 of ``queue_pending``, leaves already-queued jobs untouched
and does not interrupt the running job. ``/interrupt`` and ``DELETE /queue`` are
deliberately never called - the queue may be someone else's.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import time
import urllib.error
import shutil
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MANIFEST = ROOT / "gallery" / "render_manifest.json"
RENDER_OUT = ROOT / "gallery" / ".render_out"
#: Already committed and already published, so reading it publishes nothing new
#: about the maintainer's setup - and updating that workflow updates this script.
SETTINGS_WORKFLOW = ROOT / "gallery" / "cosplay" / "Krea2_IdentityForge_CharacterCycle.json"
#: Gitignored. Overrides anything the workflow supplies.
LOCAL_CONFIG = ROOT / "scripts" / "render_config.json"

DEFAULT_URL = "http://127.0.0.1:8288"
CLIENT_ID = "identity-forge-render-gallery"
MANIFEST_VERSION = 1
SEED_FORMULA = "int(sha256(name)[:15], 16)"
#: ``--save-originals`` only. Mirrors the filename prefix the maintainer's own
#: workflow uses, so originals land beside their hand-run renders.
ORIGINALS_PREFIX = "identityforge"

KINDS = ("cosplay", "archetypes", "creatures")

#: Widget values, mirrored from the workflows the gallery images were rendered
#: with. Every one is checked against the node's own option list before use, so
#: a renamed option fails loudly instead of silently changing what is drawn.
COSPLAYER_WIDGETS = {
    "random_scope": "Any",
    "look_level": "Full character",
    "mask": "Default",
    "props": "Include signature prop",
}
ARCHETYPE_WIDGETS = {"lock_level": "Essentials"}
CREATURE_WIDGETS = {
    "form": "Anthropomorphic",
    "head": "Follow base",
    "eyes": "Follow base",
    "integument": "Follow base",
    "arms": "Follow base",
    "hands": "Follow base",
    "legs_feet": "Follow base",
    "tail": "Follow base",
    "wings": "Follow base",
    "integument_finish": "Auto",
    "palette": "Auto",
    "size_scale": "Auto",
    "more_features": "",
}
#: Everything not named here rides the schema default of ``"Random"``. Note
#: ``accessory_density`` is deliberately ``"None"`` and not the function default
#: ``"Balanced"`` - a gallery tile shows the character, not a pile of extras.
FORGE_WIDGETS = {
    "gender": "Any",
    "wardrobe": "Match gender",
    "size_scale": "Auto",
    "hair_color_scope": "Natural only",
    "accessory_density": "None",
    "location_setting": "Any indoor/outdoor",
    "set_all_fields": "Off",
}

#: Back-facing framings never rotate into a gallery sample: the gallery is a
#: showcase, and a rear view hides the costume the entry exists to show. The
#: engine pools are untouched - users still draw these, and the Turnaround
#: node needs them - this only curates what the SAMPLES use.
_BACK_FACING_SHOTS = frozenset({
    "from slightly behind and to the side",
    "view from directly behind",
    "from behind and slightly below, looking up toward subject",
    "from above and behind, looking down toward subject",
})


def _gallery_shot(seed: int) -> str | None:
    """A deterministic front-facing ``shot_type`` pin for one entry render.

    Picked on a dedicated stream from the schema's own shot_type options
    (minus the back-facing four), so the same entry seed always renders the
    same angle. Locking the field shifts the engine's RNG stream relative to
    an unpinned render, which is fine here: a gallery image is a sample of
    what the node CAN emit, not a canonical reproduction (the manifest hash
    tracks entry text, not render settings - see architecture.md).
    """
    from nodes.identity_forge import IdentityForge
    for spec in IdentityForge.define_schema().inputs:
        if spec.id == "shot_type":
            # "Random" is the field's control value, not a shot: pinning it
            # would re-randomize the camera and leak back-facing values through.
            pool = [s for s in spec.options
                    if s not in _BACK_FACING_SHOTS and s != "Random"]
            return random.Random(seed ^ 0x5A17C105).choice(pool)
    return None


class RenderError(RuntimeError):
    """A setting, model or option that must exist and does not."""


# ---------------------------------------------------------------------------
# Render settings, read from the committed workflow
# ---------------------------------------------------------------------------

def _widgets_by_type(workflow: dict) -> dict[str, list[list]]:
    """Group every node's ``widgets_values`` by node ``type``.

    The workflow is in UI format, so the settings live positionally in each
    node's widget array rather than in a named mapping.
    """
    found: dict[str, list[list]] = {}
    for node in workflow.get("nodes", []):
        values = node.get("widgets_values")
        if isinstance(values, list):
            found.setdefault(node.get("type", ""), []).append(values)
    return found


def _one(groups: dict[str, list[list]], node_type: str, index: int, key: str) -> Any:
    """Pull one widget value, naming the exact key when it is not there."""
    entries = groups.get(node_type) or []
    if not entries:
        raise RenderError(
            f"{SETTINGS_WORKFLOW.name} has no {node_type} node, so {key!r} "
            f"cannot be read. Pass it explicitly or fix the workflow."
        )
    values = entries[0]
    if index >= len(values):
        raise RenderError(
            f"{SETTINGS_WORKFLOW.name}: {node_type} has no widget at position "
            f"{index}, so {key!r} cannot be read."
        )
    return values[index]


def read_render_settings(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Model, sampler and size settings, read from the committed workflow.

    One source of truth: the workflow the gallery was rendered with is already in
    the repository and already published, so nothing new about anyone's local
    setup is written down here. A gitignored ``scripts/render_config.json`` and
    then the CLI flags override it. A missing file or absent node is fatal -
    guessing a model name is exactly how a whole gallery gets rendered off the
    wrong checkpoint while still looking plausible.
    """
    if not SETTINGS_WORKFLOW.is_file():
        raise RenderError(f"Settings workflow not found: {SETTINGS_WORKFLOW}")
    try:
        workflow = json.loads(SETTINGS_WORKFLOW.read_text(encoding="utf-8"))
    except ValueError as error:
        raise RenderError(f"{SETTINGS_WORKFLOW.name} is not valid JSON: {error}") from error

    groups = _widgets_by_type(workflow)
    # KSampler widgets: seed, control_after_generate, steps, cfg, sampler, scheduler, denoise.
    settings = {
        "unet_name": _one(groups, "UNETLoader", 0, "unet_name"),
        "weight_dtype": _one(groups, "UNETLoader", 1, "weight_dtype"),
        "clip_name": _one(groups, "CLIPLoader", 0, "clip_name"),
        "clip_type": _one(groups, "CLIPLoader", 1, "clip_type"),
        "clip_device": _one(groups, "CLIPLoader", 2, "clip_device"),
        "vae_name": _one(groups, "VAELoader", 0, "vae_name"),
        "lora_name": _one(groups, "LoraLoader", 0, "lora_name"),
        "lora_strength_model": _one(groups, "LoraLoader", 1, "lora_strength_model"),
        "lora_strength_clip": _one(groups, "LoraLoader", 2, "lora_strength_clip"),
        "width": _one(groups, "EmptyLatentImage", 0, "width"),
        "height": _one(groups, "EmptyLatentImage", 1, "height"),
        "steps": _one(groups, "KSampler", 2, "steps"),
        "cfg": _one(groups, "KSampler", 3, "cfg"),
        "sampler_name": _one(groups, "KSampler", 4, "sampler_name"),
        "scheduler": _one(groups, "KSampler", 5, "scheduler"),
        "denoise": _one(groups, "KSampler", 6, "denoise"),
        "style_prefix": _style_prefix(groups),
        "style_delimiter": _style_delimiter(groups),
    }

    if LOCAL_CONFIG.is_file():
        try:
            local = json.loads(LOCAL_CONFIG.read_text(encoding="utf-8"))
        except ValueError as error:
            raise RenderError(f"{LOCAL_CONFIG.name} is not valid JSON: {error}") from error
        unknown = [k for k in local if k not in settings]
        if unknown:
            raise RenderError(f"{LOCAL_CONFIG.name} has unknown key(s): {unknown}")
        settings.update(local)

    for key, value in (overrides or {}).items():
        if value is not None:
            settings[key] = value
    return settings


def _concatenate_nodes(groups: dict[str, list[list]]) -> list[list]:
    """``StringConcatenate`` widgets: (string_a, string_b, delimiter).

    The workflow has two: one builds the save-file prefix, the other joins the
    photographic style prefix to the node's prose. The prompt one is the only
    one carrying a non-empty delimiter.
    """
    return [v for v in groups.get("StringConcatenate", []) if len(v) >= 3 and str(v[2]).strip()]


def _style_prefix(groups: dict[str, list[list]]) -> str:
    nodes = _concatenate_nodes(groups)
    if not nodes:
        raise RenderError(
            f"{SETTINGS_WORKFLOW.name} has no StringConcatenate node with a "
            f"delimiter, so 'style_prefix' cannot be read."
        )
    return str(nodes[0][0])


def _style_delimiter(groups: dict[str, list[list]]) -> str:
    nodes = _concatenate_nodes(groups)
    if not nodes:
        raise RenderError(
            f"{SETTINGS_WORKFLOW.name} has no StringConcatenate node with a "
            f"delimiter, so 'style_delimiter' cannot be read."
        )
    return str(nodes[0][2])


# ---------------------------------------------------------------------------
# The data layer, hashing and the manifest
# ---------------------------------------------------------------------------

def entries_for(kind: str) -> dict[str, dict]:
    """Every entry of one kind, straight from the data layer.

    Archetypes arrive with ``_COSTUMES`` already merged, which is what makes the
    hash cover the costume text as well as the preset.
    """
    if kind == "cosplay":
        from data.cosplayers import COSPLAYERS

        return COSPLAYERS
    if kind == "archetypes":
        from data.templates import ARCHETYPES

        return ARCHETYPES
    if kind == "creatures":
        from data.creatures import CREATURES

        return CREATURES
    raise RenderError(f"Unknown kind: {kind!r}")


def entry_hash(kind: str, name: str) -> str:
    """Hash the whole entry dict, so any edit to its text shows up as stale.

    **The render settings are deliberately NOT in this hash.** The sibling
    stylebook pipeline folds model, sampler and size into its per-tile hash, and
    that is right there because every tile was produced under recorded settings.
    Here, the ~2,150 images already on ``gh-pages`` were rendered by hand under
    settings nobody wrote down, so including them would mark every single entry
    stale on the day this landed. Changing the model is therefore a deliberate,
    manual re-render - it is not, and must not become, an automatic one.
    """
    entry = entries_for(kind)[name]
    payload = "v1:" + json.dumps(entry, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def entry_seed(name: str, reroll: int = 0) -> int:
    """Deterministic per entry, so the same entry always re-renders the same person.

    ``reroll`` re-draws a single bad tile without touching the data. The seed
    decides the pose, framing and lighting as well as the person, so a tile can
    come out technically correct and still be useless - a masked character shot
    in profile against a window shows neither the mask nor the face. A non-zero
    reroll is recorded in the manifest as an explicit ``seed``, because a tile
    nobody can reproduce is worse than a tile nobody likes.
    """
    return int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:15], 16) + reroll


def _blank_manifest() -> dict:
    return {
        "schema_version": MANIFEST_VERSION,
        "generated": "",
        "seed_formula": SEED_FORMULA,
        "render": {},
        "entries": {kind: {} for kind in KINDS},
    }


def load_manifest() -> dict:
    if not MANIFEST.is_file():
        return _blank_manifest()
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except ValueError:
        return _blank_manifest()
    if data.get("schema_version") != MANIFEST_VERSION:
        return _blank_manifest()
    data.setdefault("entries", {})
    for kind in KINDS:
        data["entries"].setdefault(kind, {})
    return data


def save_manifest(manifest: dict) -> None:
    manifest["generated"] = _datetime.datetime.now().isoformat(timespec="seconds")
    manifest["seed_formula"] = SEED_FORMULA
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def survey(kinds: tuple[str, ...] = KINDS) -> dict[str, dict[str, list[str]]]:
    """Return ``{kind: {missing, stale, orphan}}`` against the manifest.

    Deliberately manifest-only: ``gallery/.render_out`` is scratch and never
    reaches a clone, so testing for a file on disk would report every entry as
    missing in CI. The published images live on ``gh-pages``; the manifest is the
    record that they match the current text.
    """
    result: dict[str, dict[str, list[str]]] = {}
    recorded_all = load_manifest().get("entries", {})
    for kind in kinds:
        entries = entries_for(kind)
        recorded = recorded_all.get(kind, {})
        missing, stale = [], []
        for name in entries:
            record = recorded.get(name)
            if record is None:
                missing.append(name)
            elif record.get("hash") != entry_hash(kind, name):
                stale.append(name)
        orphan = [name for name in recorded if name not in entries]
        result[kind] = {
            "missing": sorted(missing),
            "stale": sorted(stale),
            "orphan": sorted(orphan),
        }
    return result


# ---------------------------------------------------------------------------
# Prompt resolution - in this process, from this repo
# ---------------------------------------------------------------------------

def _register_comfy_stub() -> None:
    """Real-first, stub-fallback - exactly what ``tests/__init__.py`` does.

    Every node module sits behind ``try: from comfy_api.latest import io``, so
    the stub has to be importable *before* the first node import or the classes
    are never defined at all.
    """
    try:
        import comfy_api.latest.io  # noqa: F401
    except ImportError:
        stub_root = ROOT / "tests" / "comfy_stub"
        if str(stub_root) not in sys.path:
            sys.path.insert(0, str(stub_root))


def _unwrap(output: Any) -> tuple:
    """Get the positional results out of a ``NodeOutput``.

    The stub stores them on ``.args``; the real ``comfy_api`` has carried both
    ``.args`` and ``.result`` across versions. Assume neither.
    """
    for attribute in ("args", "result"):
        values = getattr(output, attribute, None)
        if isinstance(values, (tuple, list)):
            return tuple(values)
    if isinstance(output, (tuple, list)):
        return tuple(output)
    raise RenderError(f"Cannot read node output of type {type(output).__name__}")


def _check_options(node_class: Any, pinned: dict[str, Any]) -> None:
    """Fail loudly if a pinned widget value is no longer one of the node's options."""
    options = {
        spec.id: list(spec.options)
        for spec in node_class.define_schema().inputs
        if getattr(spec, "options", None)
    }
    for key, value in pinned.items():
        allowed = options.get(key)
        if allowed is not None and value not in allowed:
            raise RenderError(
                f"{node_class.__name__}.{key} = {value!r} is not one of its "
                f"options ({allowed[:6]}...). The widget was renamed; update "
                f"the table in {Path(__file__).name}."
            )


def _forge_kwargs(forge_class: Any, character_json: str, seed: int) -> dict[str, Any]:
    """Every IdentityForge widget, mirroring the workflows.

    Built from the node's own schema rather than a hand-kept list, so a field
    added to the pack is carried at its default of ``"Random"`` automatically.
    """
    kwargs: dict[str, Any] = {"seed": seed, "archetype_json": character_json}
    for spec in forge_class.define_schema().inputs:
        if spec.id in kwargs:
            continue
        kwargs[spec.id] = FORGE_WIDGETS.get(spec.id, "Random")
    _check_options(forge_class, {k: v for k, v in FORGE_WIDGETS.items()})
    return kwargs


def resolve_prose(kind: str, name: str, reroll: int = 0) -> str:
    """The prose the node pack itself would emit for this entry.

    Calls the real node classes in the order the workflows wire them - preset
    node, then engine - rather than re-implementing the plumbing, because the
    engine's call signature has several footguns (a grouped JSON document is not
    a flat locked dict, and the builders' third positional argument differs per
    node). An image that does not represent what the node emits is worse than no
    image at all.
    """
    _register_comfy_stub()
    from nodes.identity_forge import IdentityForge
    from nodes.identity_forge_archetype import IdentityForgeArchetype
    from nodes.identity_forge_cosplayer import IdentityForgeCosplayer
    from nodes.identity_forge_creature import IdentityForgeCreature

    seed = entry_seed(name, reroll)
    if kind == "cosplay":
        _check_options(IdentityForgeCosplayer, COSPLAYER_WIDGETS)
        preset = IdentityForgeCosplayer.execute(
            character=name, seed=seed, upstream="", **COSPLAYER_WIDGETS
        )
    elif kind == "archetypes":
        _check_options(IdentityForgeArchetype, ARCHETYPE_WIDGETS)
        preset = IdentityForgeArchetype.execute(
            archetype=name, seed=seed, upstream="", **ARCHETYPE_WIDGETS
        )
    elif kind == "creatures":
        _check_options(IdentityForgeCreature, CREATURE_WIDGETS)
        preset = IdentityForgeCreature.execute(
            creature=name, seed=seed, upstream="", **CREATURE_WIDGETS
        )
    else:
        raise RenderError(f"Unknown kind: {kind!r}")

    character_json = _unwrap(preset)[0]
    forge_kwargs = _forge_kwargs(IdentityForge, character_json, seed)
    shot = _gallery_shot(seed)
    if shot:
        forge_kwargs["shot_type"] = shot
    forged = IdentityForge.execute(**forge_kwargs)
    prose = _unwrap(forged)[0]
    if not isinstance(prose, str) or not prose.strip():
        raise RenderError(f"{kind}/{name}: the engine produced no prose")
    return prose


def positive_prompt(prose: str, settings: dict[str, Any]) -> str:
    """Style prefix first: a trailing noun-phrase style gets drawn as scene content."""
    return f"{settings['style_prefix']}{settings['style_delimiter']}{prose}"


# ---------------------------------------------------------------------------
# The API graph - no Identity Forge nodes, the text is already resolved
# ---------------------------------------------------------------------------

def build_graph(positive: str, seed: int, settings: dict[str, Any],
                save_originals: bool, filename_stem: str) -> dict:
    graph = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": settings["unet_name"],
                         "weight_dtype": settings["weight_dtype"]}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": settings["clip_name"],
                         "type": settings["clip_type"],
                         "device": settings["clip_device"]}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": settings["vae_name"]}},
        "4": {"class_type": "LoraLoader",
              "inputs": {"lora_name": settings["lora_name"],
                         "strength_model": settings["lora_strength_model"],
                         "strength_clip": settings["lora_strength_clip"],
                         "model": ["1", 0], "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode",
              "inputs": {"text": positive, "clip": ["4", 1]}},
        # The negative is the zeroed positive conditioning, not a text string:
        # cfg is 1, so a second encode would be dead weight.
        "6": {"class_type": "ConditioningZeroOut",
              "inputs": {"conditioning": ["5", 0]}},
        "7": {"class_type": "EmptyLatentImage",
              "inputs": {"width": settings["width"], "height": settings["height"],
                         "batch_size": 1}},
        "8": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": settings["steps"],
                         "cfg": settings["cfg"],
                         "sampler_name": settings["sampler_name"],
                         "scheduler": settings["scheduler"],
                         "denoise": settings["denoise"],
                         "model": ["4", 0], "positive": ["5", 0],
                         "negative": ["6", 0], "latent_image": ["7", 0]}},
        "9": {"class_type": "VAEDecode",
              "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
    }
    if save_originals:
        # SaveImage numbers from the highest existing counter, so it adds files
        # and never replaces one already in the output folder.
        graph["10"] = {"class_type": "SaveImage",
                       "inputs": {"filename_prefix": f"{ORIGINALS_PREFIX}/{filename_stem}",
                                  "images": ["9", 0]}}
    else:
        graph["10"] = {"class_type": "PreviewImage", "inputs": {"images": ["9", 0]}}
    return graph


# ---------------------------------------------------------------------------
# ComfyUI HTTP client
# ---------------------------------------------------------------------------

class ComfyClient:
    def __init__(self, url: str, timeout: int = 600):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise RenderError(f"--url must be http or https, got {parsed.scheme!r}")
        self.url = url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, timeout: int = 15) -> bytes:
        with urllib.request.urlopen(self.url + path, timeout=timeout) as response:
            return response.read()

    def _get_json(self, path: str, timeout: int = 15) -> Any:
        return json.loads(self._get(path, timeout=timeout))

    def reachable(self) -> bool:
        try:
            self._get("/system_stats", timeout=5)
            return True
        except (urllib.error.URLError, OSError, ValueError):
            return False

    def combo_options(self, node_type: str, field: str) -> list[str]:
        try:
            info = self._get_json(f"/object_info/{node_type}")
            return list(info[node_type]["input"]["required"][field][0])
        except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError, TypeError):
            return []

    def queue_depth(self) -> tuple[int, int]:
        try:
            queue = self._get_json("/queue")
            return len(queue.get("queue_running", [])), len(queue.get("queue_pending", []))
        except (urllib.error.URLError, OSError, ValueError, TypeError):
            return (0, 0)

    def submit(self, graph: dict, front: bool) -> str | None:
        body = json.dumps(
            {"prompt": graph, "client_id": CLIENT_ID, "front": front}
        ).encode("utf-8")
        request = urllib.request.Request(
            self.url + "/prompt", data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read()).get("prompt_id")
        except urllib.error.HTTPError as error:
            # Node validation errors live in the response body, nowhere else.
            print(f"    queue rejected: {error.read()[:600].decode('utf-8', 'replace')}")
        except (urllib.error.URLError, OSError, ValueError) as error:
            print(f"    queue failed: {error}")
        return None

    def wait(self, prompt_id: str) -> dict | None:
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            try:
                history = self._get_json(f"/history/{prompt_id}")
                entry = history.get(prompt_id)
                if entry is not None:
                    return entry
            except (urllib.error.URLError, OSError, ValueError, TypeError):
                pass
            time.sleep(2)
        return None

    def fetch(self, filename: str, subfolder: str, image_type: str) -> bytes | None:
        query = urllib.parse.urlencode(
            {"filename": filename, "subfolder": subfolder, "type": image_type}
        )
        try:
            return self._get(f"/view?{query}", timeout=120)
        except (urllib.error.URLError, OSError) as error:
            # Never echo the query string: it is the one part that could carry a token.
            print(f"    fetch failed for {filename}: {error}")
            return None


def preflight(client: ComfyClient, settings: dict[str, Any]) -> bool:
    """Confirm every model, sampler and scheduler this run needs actually exists.

    Never substring-guess a model. The sibling stylebook pipeline did exactly
    that and rendered an entire gallery off the wrong Turbo merge - plausible
    enough that nobody noticed until the images were published.
    """
    checks = [
        ("UNETLoader", "unet_name", settings["unet_name"]),
        ("CLIPLoader", "clip_name", settings["clip_name"]),
        ("VAELoader", "vae_name", settings["vae_name"]),
        ("LoraLoader", "lora_name", settings["lora_name"]),
        ("KSampler", "sampler_name", settings["sampler_name"]),
        ("KSampler", "scheduler", settings["scheduler"]),
    ]
    ok = True
    for node_type, field, wanted in checks:
        available = client.combo_options(node_type, field)
        if not available:
            print(f"  {node_type}.{field}: the instance reported no options at all.")
            ok = False
        elif wanted not in available:
            print(f"  {node_type}.{field}: {wanted!r} is not installed there.")
            print(f"    available: {available[:12]}"
                  f"{' ...' if len(available) > 12 else ''}")
            ok = False
    return ok


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _load_normalize_name():
    """Reuse the gallery's own filename normalizer rather than re-implementing it.

    The three ``build_manifest.py`` copies are byte-identical outside their
    config block, so one of them is the definition. Matching it is what makes
    ``publish.py`` able to pair the file with its entry.
    """
    path = ROOT / "gallery" / "cosplay" / "build_manifest.py"
    spec = importlib.util.spec_from_file_location("_if_build_manifest", path)
    if spec is None or spec.loader is None:
        raise RenderError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.normalize_name


def render_one(client: ComfyClient, kind: str, name: str, settings: dict[str, Any],
               normalize_name, front: bool, save_originals: bool,
               reroll: int = 0) -> bool:
    stem = normalize_name(name)
    prose = resolve_prose(kind, name, reroll)
    graph = build_graph(
        positive_prompt(prose, settings), entry_seed(name, reroll), settings,
        save_originals, stem,
    )
    prompt_id = client.submit(graph, front=front)
    if not prompt_id:
        return False
    history = client.wait(prompt_id)
    if history is None:
        print("    timed out waiting for the render")
        return False

    image_type = "output" if save_originals else "temp"
    for output in history.get("outputs", {}).values():
        for image in output.get("images", []):
            data = client.fetch(
                image.get("filename", ""), image.get("subfolder", ""),
                image.get("type", image_type),
            )
            if data:
                target = RENDER_OUT / kind / f"{stem}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                return True
    print("    the render produced no image")
    return False


def publish_kind(kind: str, names: list[str] | None = None) -> bool:
    """Hand off to the gallery's own publisher, which never deletes.

    ``names`` limits the hand-off to THIS run's originals, staged into a temp
    folder and published with ``--overwrite``. Both halves matter: the
    publisher's default mode is ADD-MISSING-ONLY, so a re-render of an
    existing entry would be silently skipped (the manifest hash updated, the
    published image stayed old - caught exactly that way at 0.98.0); and
    passing the whole archive folder with --overwrite would re-encode every
    historical original on every run.
    """
    archive = RENDER_OUT / kind
    normalize_name = _load_normalize_name()
    if not archive.is_dir() or not any(archive.iterdir()):
        print(f"  {kind}: nothing in {archive}, skipped")
        return True
    if names:
        staging = Path(tempfile.mkdtemp(prefix=f"ifstage-{kind}-"))
        missing = []
        for name in names:
            src = archive / f"{normalize_name(name)}.png"
            if src.is_file():
                shutil.copy2(src, staging / src.name)
            else:
                missing.append(name)
        if missing:
            print(f"  {kind}: WARNING, no original for: {', '.join(missing)}")
        if not any(staging.iterdir()):
            print(f"  {kind}: no staged originals, skipped")
            shutil.rmtree(staging, ignore_errors=True)
            return True
        source, cleanup = staging, True
    else:
        source, cleanup = archive, False
    script = ROOT / "gallery" / kind / "publish.py"
    print(f"  {kind}: {script.name} --source {source} --overwrite")
    result = subprocess.run(
        [sys.executable, str(script), "--source", str(source), "--overwrite"],
        cwd=str(ROOT)
    )
    if cleanup:
        shutil.rmtree(source, ignore_errors=True)
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _report(results: dict[str, dict[str, list[str]]], limit: int = 15) -> bool:
    dirty = False
    for kind, buckets in results.items():
        counts = {key: len(value) for key, value in buckets.items()}
        print(f"{kind}: {len(entries_for(kind))} entries | "
              f"missing {counts['missing']}, stale {counts['stale']}, "
              f"orphan {counts['orphan']}")
        for label in ("missing", "stale", "orphan"):
            names = buckets[label]
            if names:
                dirty = True
            for name in names[:limit]:
                print(f"    {label}: {name}")
            if len(names) > limit:
                print(f"    ... and {len(names) - limit} more {label}")
    return dirty


def _targets(args: argparse.Namespace, kinds: tuple[str, ...]) -> list[tuple[str, str]]:
    """Resolve the CLI selection into ``[(kind, name), ...]``."""
    chosen: list[tuple[str, str]] = []
    if args.entry:
        for wanted in args.entry:
            hits = [(kind, wanted) for kind in kinds if wanted in entries_for(kind)]
            if not hits:
                raise RenderError(
                    f"No entry named {wanted!r} in {', '.join(kinds)}. "
                    f"Names are exact, including case and punctuation."
                )
            if len(hits) > 1:
                raise RenderError(
                    f"{wanted!r} exists in {[k for k, _ in hits]}; "
                    f"narrow it with --kind."
                )
            chosen.extend(hits)
        return chosen

    results = survey(kinds)
    want_missing = args.missing or not args.stale
    want_stale = args.stale or not args.missing
    for kind in kinds:
        if want_missing:
            chosen.extend((kind, name) for name in results[kind]["missing"])
        if want_stale:
            chosen.extend((kind, name) for name in results[kind]["stale"])
    return chosen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render, record and publish gallery images for roster entries.",
    )
    parser.add_argument("--check", action="store_true",
                        help="Report missing/stale/orphan entries and exit non-zero. "
                             "No network, no GPU. The default when nothing else is given.")
    parser.add_argument("--seed-manifest", action="store_true",
                        help="One-time: record every current entry as pre-existing.")
    parser.add_argument("--kind", choices=(*KINDS, "all"), default="all")
    parser.add_argument("--entry", action="append", default=[], metavar="NAME",
                        help="Render one entry by exact name. Repeatable.")
    parser.add_argument("--missing", action="store_true",
                        help="Render everything --check calls missing.")
    parser.add_argument("--stale", action="store_true",
                        help="Render everything --check calls stale.")
    parser.add_argument("--limit", type=int, default=0, metavar="N",
                        help="Cap this run. Resumable: the manifest saves per image.")
    parser.add_argument("--publish", action="store_true",
                        help="After a clean run, publish each kind touched to gh-pages.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the resolved prompt and graph; queue nothing.")
    parser.add_argument("--save-originals", action="store_true",
                        help="Use SaveImage (type=output) instead of PreviewImage, so "
                             "full-resolution originals are kept on the ComfyUI side.")
    parser.add_argument("--reroll", type=int, default=0, metavar="N",
                        help="Re-draw a bad tile with a shifted seed, without touching "
                             "the data. Recorded in the manifest as an explicit seed.")
    parser.add_argument("--back", action="store_true",
                        help="Queue at the back instead of front-of-queue.")
    parser.add_argument("--url", default=DEFAULT_URL,
                        help=f"ComfyUI address (default {DEFAULT_URL}).")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Seconds to wait for one render (default 600).")
    for flag in ("model", "sampler", "scheduler", "steps", "cfg", "width", "height"):
        parser.add_argument(f"--{flag}", default=None,
                            help=f"Override the {flag} read from the workflow.")
    args = parser.parse_args(argv)

    kinds = KINDS if args.kind == "all" else (args.kind,)
    acting = args.seed_manifest or args.entry or args.missing or args.stale
    if not acting and not args.dry_run:
        args.check = True

    try:
        if args.check:
            results = survey(kinds)
            if _report(results):
                first = next(
                    (f'--kind {kind} --entry "{name}"'
                     for kind in kinds
                     for bucket in ("missing", "stale")
                     for name in results[kind][bucket][:1]),
                    "--missing",
                )
                print("\nRe-render them, e.g.:")
                print(f"  python scripts/render_gallery.py {first} "
                      f"--save-originals --publish")
                print("An orphan is pruned by deleting its manifest entry in the "
                      "same commit that removed the roster entry.")
                return 1
            print("\nEvery entry's recorded image matches its current text.")
            return 0

        if args.seed_manifest:
            manifest = load_manifest()
            today = _datetime.date.today().isoformat()
            added = 0
            for kind in kinds:
                recorded = manifest["entries"].setdefault(kind, {})
                for name in entries_for(kind):
                    if name not in recorded:
                        recorded[name] = {"hash": entry_hash(kind, name),
                                          "rendered": "pre-existing"}
                        added += 1
            manifest.setdefault("render", {})
            save_manifest(manifest)
            print(f"Seeded {added} entries as pre-existing on {today}.")
            print(f"Wrote {MANIFEST.relative_to(ROOT)}. Commit it BEFORE adding "
                  f"content, or new entries get blessed unrendered.")
            return 0

        overrides = {
            "unet_name": args.model, "sampler_name": args.sampler,
            "scheduler": args.scheduler,
            "steps": int(args.steps) if args.steps else None,
            "cfg": float(args.cfg) if args.cfg else None,
            "width": int(args.width) if args.width else None,
            "height": int(args.height) if args.height else None,
        }
        settings = read_render_settings(overrides)
        targets = _targets(args, kinds)
        if args.limit > 0:
            targets = targets[: args.limit]
        if not targets:
            print("Nothing to render; every entry's image is current.")
            return 0

        if args.dry_run:
            for kind, name in targets:
                prose = resolve_prose(kind, name, args.reroll)
                print(f"\n=== {kind} / {name}  (seed {entry_seed(name, args.reroll)}) ===")
                print(positive_prompt(prose, settings))
            print(f"\n--- graph for {targets[0][1]} ---")
            print(json.dumps(
                build_graph(positive_prompt(resolve_prose(*targets[0], args.reroll), settings),
                            entry_seed(targets[0][1], args.reroll), settings,
                            args.save_originals, targets[0][1]),
                indent=2,
            ))
            return 0

        client = ComfyClient(args.url, timeout=args.timeout)
        if not client.reachable():
            print(f"No ComfyUI at {args.url}. Start it, or pass --url.")
            return 1
        print(f"Preflight against {args.url}")
        if not preflight(client, settings):
            return 1
        running, pending = client.queue_depth()
        print(f"  queue: {running} running, {pending} pending "
              f"({'front' if not args.back else 'back'} of queue)")
        print(f"  {settings['unet_name']} + {settings['lora_name']}, "
              f"{settings['steps']} steps, {settings['sampler_name']}/"
              f"{settings['scheduler']}, {settings['width']}x{settings['height']}")
        if args.save_originals:
            print(f"  originals kept on the instance under {ORIGINALS_PREFIX}/")

        normalize_name = _load_normalize_name()
        manifest = load_manifest()
        # Informational only, and deliberately NOT part of any entry hash - see
        # the note on `render` below.
        manifest["render"] = {
            key: settings[key] for key in
            ("unet_name", "lora_name", "steps", "cfg", "sampler_name",
             "scheduler", "width", "height")
        }
        today = _datetime.date.today().isoformat()
        done = failed = 0
        touched: dict[str, list[str]] = {}
        for position, (kind, name) in enumerate(targets, 1):
            print(f"[{position}/{len(targets)}] {kind} / {name}")
            if render_one(client, kind, name, settings, normalize_name,
                          front=not args.back, save_originals=args.save_originals,
                          reroll=args.reroll):
                record = {"hash": entry_hash(kind, name), "rendered": today}
                if args.reroll:
                    record["seed"] = entry_seed(name, args.reroll)
                manifest["entries"].setdefault(kind, {})[name] = record
                touched.setdefault(kind, []).append(name)
                done += 1
            else:
                failed += 1
            # Save after every success so a long run survives a Ctrl-C.
            save_manifest(manifest)

        print(f"\nRendered {done}, failed {failed}.")
        if failed:
            return 1
        if args.publish:
            print("\nPublishing:")
            for kind in sorted(touched):
                if not publish_kind(kind, touched[kind]):
                    return 1
        return 0

    except RenderError as error:
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
