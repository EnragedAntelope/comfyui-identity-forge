"""A record-only stand-in for ``comfy_api.latest.io``, used only when the
real package is not importable (i.e. this process has no ComfyUI install).

Without this, every node class in ``nodes/*.py`` sits behind that module's
own ``try: from comfy_api.latest import io / except ImportError`` guard and
is never *defined* outside a running ComfyUI — so nothing here can ever be
schema-tested, and ``scripts/dump_frontend_fixtures.py`` (which reads real
``define_schema()`` output to keep the frontend jsdom tests honest) would
have nothing to read from on a CI runner.

**This must never become the only thing anything sees.** Registration
happens in ``tests/__init__.py``, which imports the *real* package first and
falls back to this one only on ``ImportError`` — so on a machine with
ComfyUI installed, everything runs against the genuine API, and this stub
exists purely to cover the gap on a runner that has neither.

Scope is deliberately narrow: only the surface this pack actually calls,
confirmed by grepping every ``io.*`` construction across ``nodes/*.py``:
``Schema``, ``ComfyNode``, ``NodeOutput``, ``Combo.Input``, ``String.Input``,
``String.Output``, ``Int.Input``, ``Image.Input``. No ``Float``, ``Custom``,
``Hidden`` or ``NumberDisplay`` — this pack doesn't use them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class Input:
    """Base for every ``*.Input`` below: id/display/optional/tooltip only.

    Deliberately carries no ``default`` — matching the real API, where the
    base ``Input`` (what a socket-only type extends) has no ``default``
    attribute at all, and only ``WidgetInput`` adds one. ``Image.Input`` is
    this pack's one socket-only type, and it extends this class directly so
    that structural gap survives here too (``hasattr(inp, "default")`` tells
    a real widget apart from a link-only socket without a name list).
    """

    def __init__(
        self,
        id: str,
        display_name: str | None = None,
        optional: bool = False,
        tooltip: str | None = None,
        **extra: Any,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.optional = optional
        self.tooltip = tooltip
        for key, value in extra.items():
            setattr(self, key, value)


class WidgetInput(Input):
    """Base for an Input that has a widget on the node face, and so
    contributes an entry to a saved workflow's ``widgets_values``."""

    def __init__(
        self,
        id: str,
        display_name: str | None = None,
        optional: bool = False,
        tooltip: str | None = None,
        default: Any = None,
        **extra: Any,
    ) -> None:
        super().__init__(id, display_name, optional, tooltip, **extra)
        self.default = default


class Output:
    """Base for every ``*.Output`` below."""

    def __init__(
        self,
        id: str | None = None,
        display_name: str | None = None,
        tooltip: str | None = None,
        is_output_list: bool = False,
        **extra: Any,
    ) -> None:
        self.id = id
        self.display_name = display_name if display_name else id
        self.tooltip = tooltip
        self.is_output_list = is_output_list
        for key, value in extra.items():
            setattr(self, key, value)


class Int:
    class Input(WidgetInput):
        def __init__(
            self,
            id: str,
            display_name: str | None = None,
            default: int | None = None,
            min: int | None = None,
            max: int | None = None,
            control_after_generate: str | bool | None = None,
            tooltip: str | None = None,
            optional: bool = False,
            **extra: Any,
        ) -> None:
            super().__init__(id, display_name, optional, tooltip, default, **extra)
            self.min = min
            self.max = max
            self.control_after_generate = control_after_generate

    class Output(Output):
        pass


class String:
    class Input(WidgetInput):
        def __init__(
            self,
            id: str,
            display_name: str | None = None,
            multiline: bool = False,
            optional: bool = False,
            default: str | None = None,
            force_input: bool = False,
            tooltip: str | None = None,
            **extra: Any,
        ) -> None:
            super().__init__(id, display_name, optional, tooltip, default, **extra)
            self.multiline = multiline
            self.force_input = force_input

    class Output(Output):
        pass


class Combo:
    class Input(WidgetInput):
        def __init__(
            self,
            id: str,
            options: list[str] | None = None,
            display_name: str | None = None,
            default: str | None = None,
            control_after_generate: str | bool | None = None,
            tooltip: str | None = None,
            optional: bool = False,
            **extra: Any,
        ) -> None:
            super().__init__(id, display_name, optional, tooltip, default, **extra)
            # Real ComfyUI stores the raw list here; the options-object shape
            # (``.values``) shows up on the *frontend* widget, not this
            # schema Input. The fixture generator reads this list directly.
            self.options = options if options is not None else []
            self.control_after_generate = control_after_generate


class Image:
    class Input(Input):
        """Socket-only — extends plain ``Input`` (no widget, no default),
        matching the real API. This pack's one and only such type."""


@dataclass
class Schema:
    """Definition of a V3 node's inputs/outputs. Subset of the real fields —
    exactly what ``nodes/*.py`` passes to ``io.Schema(...)``."""

    node_id: str
    display_name: str | None = None
    category: str = "sd"
    inputs: list[Input] = field(default_factory=list)
    outputs: list[Output] = field(default_factory=list)
    description: str = ""
    is_output_node: bool = False


class ComfyNode:
    """Common base every node schema class here inherits from.

    No execution-time behaviour: nothing in this repo's Python suite calls
    ``execute()`` through the real ComfyUI queue plumbing — the engine
    functions it delegates to are tested directly instead.
    """

    @classmethod
    def fingerprint_inputs(cls, **kwargs: Any) -> Any:
        """Declared solely so the stub matches the real base class.

        The real ``ComfyNode`` declares this (raising ``NotImplementedError``)
        whether or not a node overrides it, so ``hasattr(cls,
        "fingerprint_inputs")`` is True for EVERY node in ComfyUI. Without it
        here, a test asserting a node has no cache override passed against the
        stub and would have asserted nothing against the real API — check
        ``"fingerprint_inputs" in vars(cls)`` instead.
        """
        raise NotImplementedError


class NodeOutput:
    """Positional output bundle. Storage only; never inspected by these tests."""

    def __init__(self, *args: Any) -> None:
        self.args = args
