"""comfyui-identity-forge — V3 custom node pack entrypoint.

Exposes three nodes:

* ``IdentityForge`` — a 70+ field character description randomizer with a
  constraint engine and dual prose/JSON output.
* ``IdentityForgeArchetype`` — themed presets that seed IdentityForge.
* ``IdentityForgeCosplayer`` — fictional-character cosplay presets that seed
  IdentityForge (a random person cosplaying a chosen character).

Discovery uses the ComfyUI V3 ``comfy_entrypoint`` mechanism. Frontend widgets
live in ``./js`` and are served via ``WEB_DIRECTORY``.
"""
from comfy_api.latest import ComfyExtension, io

# Package-relative inside ComfyUI; absolute fallback keeps the entrypoint
# importable in flatter layouts.
try:
    from .nodes.identity_forge import IdentityForge
    from .nodes.identity_forge_archetype import IdentityForgeArchetype
    from .nodes.identity_forge_cosplayer import IdentityForgeCosplayer
except ImportError:  # pragma: no cover
    from nodes.identity_forge import IdentityForge
    from nodes.identity_forge_archetype import IdentityForgeArchetype
    from nodes.identity_forge_cosplayer import IdentityForgeCosplayer

#: Tells ComfyUI where to find this pack's frontend JavaScript.
WEB_DIRECTORY = "./js"

__all__ = ["comfy_entrypoint", "WEB_DIRECTORY"]


class IdentityForgeExtension(ComfyExtension):
    """Registers the IdentityForge node pack with ComfyUI."""

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [IdentityForge, IdentityForgeArchetype, IdentityForgeCosplayer]


async def comfy_entrypoint() -> IdentityForgeExtension:
    return IdentityForgeExtension()
