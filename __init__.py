"""comfyui-identity-forge — V3 custom node pack entrypoint.

Exposes seven nodes:

* ``IdentityForge`` — a 70+ field character description randomizer with a
  constraint engine and dual prose/JSON output.
* ``IdentityForgeArchetype`` — themed presets that seed IdentityForge.
* ``IdentityForgeCosplayer`` — fictional-character cosplay presets that seed
  IdentityForge (a random person cosplaying a chosen character).
* ``IdentityForgeCreature`` — a non-human form layer (animal / monster / alien /
  mythic), optionally hybridized slot-by-slot, that seeds IdentityForge.
* ``IdentityForgeModifier`` — prepends custom descriptors to individual fields /
  groups (e.g. "sci-fi" shoes) for per-element stylistic tilts.
* ``IdentityForgeVaultSave`` — save a generated character to a local vault.
* ``IdentityForgeVaultLoad`` — recall a saved character as a chainable preset.

Discovery uses the ComfyUI V3 ``comfy_entrypoint`` mechanism. Frontend widgets
live in ``./js`` and are served via ``WEB_DIRECTORY``. The vault nodes also
register a few read/management HTTP routes (see ``_register_vault_routes``).
"""
from comfy_api.latest import ComfyExtension, io

# Package-relative inside ComfyUI; absolute fallback keeps the entrypoint
# importable in flatter layouts.
try:
    from .nodes.identity_forge import IdentityForge
    from .nodes.identity_forge_archetype import IdentityForgeArchetype
    from .nodes.identity_forge_cosplayer import IdentityForgeCosplayer
    from .nodes.identity_forge_creature import IdentityForgeCreature
    from .nodes.identity_forge_modifier import IdentityForgeModifier
    from .nodes.identity_forge_vault_save import IdentityForgeVaultSave
    from .nodes.identity_forge_vault_load import IdentityForgeVaultLoad
except ImportError:  # pragma: no cover
    from nodes.identity_forge import IdentityForge
    from nodes.identity_forge_archetype import IdentityForgeArchetype
    from nodes.identity_forge_cosplayer import IdentityForgeCosplayer
    from nodes.identity_forge_creature import IdentityForgeCreature
    from nodes.identity_forge_modifier import IdentityForgeModifier
    from nodes.identity_forge_vault_save import IdentityForgeVaultSave
    from nodes.identity_forge_vault_load import IdentityForgeVaultLoad

#: Tells ComfyUI where to find this pack's frontend JavaScript.
WEB_DIRECTORY = "./js"

__all__ = ["comfy_entrypoint", "WEB_DIRECTORY"]


def _register_vault_routes() -> None:
    """Register the vault's HTTP API for the frontend (list/preview/manage).

    Best-effort and idempotent: the routes power the Vault Load node's Refresh,
    thumbnails and manager modal. Graph execution never depends on them, so any
    failure here is logged and ignored rather than breaking node loading.
    """
    try:
        from aiohttp import web
        from server import PromptServer  # type: ignore[import-not-found]

        from .nodes.identity_forge_vault_save import (
            _PREVIEW_FILE, _entry_dir, save_character,  # noqa: F401 (save re-exported for symmetry)
        )
        from .nodes.identity_forge_vault_save import _vault_root
        from .nodes.identity_forge_vault_load import (
            delete_characters, list_characters, rename_character,
        )
    except Exception as exc:  # noqa: BLE001 — never block node registration
        print(f"[IdentityForge] Vault API routes not registered: {exc}")
        return

    routes = PromptServer.instance.routes

    @routes.get("/identity_forge/vault/characters")
    async def _characters(_request):  # type: ignore[no-untyped-def]
        return web.json_response({"characters": list_characters(_vault_root())})

    @routes.get("/identity_forge/vault/preview/{name}")
    async def _preview(request):  # type: ignore[no-untyped-def]
        name = request.match_info["name"]
        try:
            path = _entry_dir(_vault_root(), name) / _PREVIEW_FILE
        except ValueError:
            return web.Response(status=400, text="bad name")
        if not path.is_file():
            return web.Response(status=404, text="no preview")
        return web.FileResponse(path)

    @routes.post("/identity_forge/vault/delete")
    async def _delete(request):  # type: ignore[no-untyped-def]
        body = await request.json()
        names = body.get("names") or ([body["name"]] if body.get("name") else [])
        survivors = delete_characters(_vault_root(), names)
        return web.json_response({"characters": survivors})

    @routes.post("/identity_forge/vault/rename")
    async def _rename(request):  # type: ignore[no-untyped-def]
        body = await request.json()
        try:
            new_name = rename_character(_vault_root(), body.get("from", ""), body.get("to", ""))
        except ValueError as exc:
            return web.json_response({"error": str(exc)}, status=400)
        return web.json_response({"name": new_name})

    print("[IdentityForge] Vault API routes registered.")


_register_vault_routes()


class IdentityForgeExtension(ComfyExtension):
    """Registers the IdentityForge node pack with ComfyUI."""

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [IdentityForge, IdentityForgeArchetype, IdentityForgeCosplayer,
                IdentityForgeCreature, IdentityForgeModifier,
                IdentityForgeVaultSave, IdentityForgeVaultLoad]


async def comfy_entrypoint() -> IdentityForgeExtension:
    return IdentityForgeExtension()
