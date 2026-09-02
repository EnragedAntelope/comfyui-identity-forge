"""Package surface of the ``comfy_api.latest`` stub.

``io`` is the submodule next door and is imported by every node module. This
file additionally re-exports **``ComfyExtension``**, which only the repo-root
``__init__.py`` needs (``from comfy_api.latest import ComfyExtension, io``).

That one name is why this file exists. Under
``python -m unittest discover -s tests -t .`` the repo-root ``__init__.py`` is
never imported, so an empty stub package was sufficient and the gap stayed
invisible. pytest puts the rootdir on ``sys.path`` and imports the root package
before collecting ``tests``, so it hit ``ImportError: cannot import name
'ComfyExtension'`` on all 772 tests -- the real reason ``pytest`` "did not work
here", which was previously recorded as a stub *ordering* problem.

Kept as narrow as ``io``: a base class with the two hooks the entrypoint
overrides, and nothing else. The real ``comfy_api`` always wins when ComfyUI is
installed -- see ``tests/__init__.py`` and the rootdir ``conftest.py``.
"""
from __future__ import annotations

from . import io  # noqa: F401  -- re-exported: `from comfy_api.latest import io`

__all__ = ["ComfyExtension", "io"]


class ComfyExtension:
    """Stand-in for the V3 extension base class.

    The real one is what ComfyUI's ``comfy_entrypoint`` mechanism instantiates
    to discover a pack's nodes. Nothing in the test suite runs the discovery
    handshake; this exists so importing the entrypoint module succeeds.
    """

    async def get_node_list(self) -> list[type]:
        return []
