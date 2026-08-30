/**
 * Builds a LiteGraph-shaped fake node from the Python-derived fixture
 * (tests/frontend/fixtures/nodes.json — see scripts/dump_frontend_fixtures.py)
 * and drives an extension's registration lifecycle against it.
 *
 * Stylebook's own harness drove `ext.nodeCreated(fakeNode)` directly, because
 * every one of its extensions used that hook. Three of this pack's four
 * extensions (identity_forge.ui, identity_forge.creature.ui,
 * identity_forge.vault) hook `beforeRegisterNodeDef` instead — only
 * identity_forge.recreate uses `nodeCreated`. `beforeRegisterNodeDef` is
 * `async` and receives `(nodeType, nodeData)`; each extension reads
 * `nodeData.name`, and (if it matches) wraps `nodeType.prototype.onNodeCreated`.
 * So driving these requires a fake *class* with a real `.prototype` object,
 * not just a fake node instance.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const FIXTURE_PATH = fileURLToPath(new URL("./fixtures/nodes.json", import.meta.url));
const FIXTURES = JSON.parse(readFileSync(FIXTURE_PATH, "utf-8"));

/** Raw widget specs for a node id, in real define_schema() order. */
export function widgetsFor(nodeId) {
  const spec = FIXTURES[nodeId];
  if (!spec) throw new Error(`No fixture entry for node id ${JSON.stringify(nodeId)}`);
  return spec;
}

/** One fixture widget spec -> a LiteGraph-shaped fake widget. */
export function makeWidget(spec) {
  const widget = {
    name: spec.name,
    type: spec.type === "combo" ? "combo" : spec.type,
    value: spec.default,
    callback: null,
  };
  widget.options = spec.type === "combo" ? { values: [...spec.options] } : {};
  return widget;
}

/**
 * A bare fake node: widgets built from the fixture (plus any `extraWidgets`),
 * and the LiteGraph surface every extension in this pack actually touches.
 * No extension applied yet -- call `applyExtension` next, or drive the
 * lifecycle by hand for a test that needs finer control.
 */
export function makeFakeNode(nodeId, { extraWidgets = [], graph = null } = {}) {
  const widgets = [...widgetsFor(nodeId).map(makeWidget), ...extraWidgets];
  return {
    comfyClass: nodeId,
    type: nodeId,
    widgets,
    size: [300, 200],
    pos: [0, 0],
    graph,
    title: null,
    color: null,
    bgcolor: null,
    setSize(sz) { this.size = sz; },
    computeSize() { return [300, 24 * this.widgets.length]; },
    setDirtyCanvas() {},
    // Mirrors the real (comfyui-frontend-package) `LGraphNode.prototype
    // .getLayoutWidgets` used by `_arrangeWidgets` to decide DRAW order --
    // filtered by `.hidden`, otherwise in `this.widgets` array order. Needed
    // so a node-instance override of this method (identity_forge_cosplayer.js's
    // visual-only reorder) has something real to shadow, the same as it would
    // on a live node.
    getLayoutWidgets() { return this.widgets.filter((w) => !w.hidden); },
    // Mirrors the real LGraphNode field of the same name: `_arrangeWidgets`
    // (which reads `getLayoutWidgets()` to compute each widget's drawn `.y`)
    // only runs on the graph's next draw pass when this is true, and only
    // `arrange()` finishing clears it. A caught-live bug: overriding
    // `getLayoutWidgets` alone does nothing until something sets this.
    _widgetSlotsDirty: false,
    // Deliberately mirrors a verified real-frontend quirk (0.85.0 worklog,
    // Phase 5b): passing `{serialize: false}` here sets `widget.options.serialize`
    // only -- it does NOT also set a top-level `widget.serialize` property, even
    // though some call sites check for one. Synthesizing that top-level
    // property here would make this fake more helpful than the real frontend
    // and mask exactly the kind of gap that check exists to guard against.
    addWidget(type, name, value, callback, options = {}) {
      const w = { type, name, value, callback, options };
      this.widgets.push(w);
      return w;
    },
    addDOMWidget(name, type, element, options = {}) {
      const w = { name, type, element, options, value: options.value ?? element?.value };
      this.widgets.push(w);
      return w;
    },
    findInputSlot() { return -1; },
    findOutputSlot() { return -1; },
  };
}

/**
 * Builds a fake `nodeType` class with a real `.prototype`, runs
 * `beforeRegisterNodeDef(FakeType, { name: nodeId })` against it, and
 * returns the class. A `nodeData.name` mismatch is exactly what every
 * extension's own early-return guards against -- pass a different `nodeId`
 * than the extension expects to exercise that path.
 */
export async function driveBeforeRegisterNodeDef(ext, nodeId) {
  class FakeNodeType {}
  await ext.beforeRegisterNodeDef(FakeNodeType, { name: nodeId });
  return FakeNodeType;
}

/**
 * End-to-end: build a fake node, register the extension's hook against a
 * fake nodeType for `nodeId`, then invoke the (now possibly wrapped)
 * `onNodeCreated` on the node -- exactly what ComfyUI does when a node is
 * dropped on the canvas.
 */
export async function createNode(ext, nodeId, opts = {}) {
  const node = makeFakeNode(nodeId, opts);
  const FakeNodeType = await driveBeforeRegisterNodeDef(ext, nodeId);
  if (typeof FakeNodeType.prototype.onNodeCreated === "function") {
    FakeNodeType.prototype.onNodeCreated.call(node);
  }
  return node;
}

/**
 * Fires `onNodeCreated` TWICE on the same node, which ComfyUI genuinely does on
 * some paths -- the comment that has sat in identity_forge_cosplayer.js since
 * 0.89.0 says so, and 0.97.0 added the same guard to the other four setups.
 * The single-creation `createNode` above cannot see a duplicate-widget bug,
 * because there is nothing to duplicate on the first pass.
 */
export async function createNodeTwice(ext, nodeId, opts = {}) {
  const node = makeFakeNode(nodeId, opts);
  const FakeNodeType = await driveBeforeRegisterNodeDef(ext, nodeId);
  if (typeof FakeNodeType.prototype.onNodeCreated === "function") {
    FakeNodeType.prototype.onNodeCreated.call(node);
    FakeNodeType.prototype.onNodeCreated.call(node);
  }
  return node;
}
