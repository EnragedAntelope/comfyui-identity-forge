/**
 * jsdom smoke tests for js/identity_forge_cosplayer.js -- the franchise filter.
 *
 * The load-bearing claim this file exists to defend is the compatibility one:
 * the filter is a `serialize: false` widget added in JS, so a workflow saved
 * before it existed must still round-trip byte-identically. That is asserted
 * directly (see "widgets_values is unchanged ..."), not assumed.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { installDom } from "./dom.mjs";
import { __getExtension } from "./stubs/app.js";
import {
  createNode, createNodeTwice, makeFakeNode, widgetsFor, driveBeforeRegisterNodeDef,
} from "./fake_node.mjs";

installDom();

await import("../../js/identity_forge_cosplayer.js");
const ext = __getExtension("identity_forge.cosplayer.ui");

const SENTINELS = ["None", "Random — any", "Random — female", "Random — male"];

const widgetNamed = (node, name) => node.widgets.find((w) => w.name === name);
const optionsOf = (w) => w.options.values;
/** Values ComfyUI would actually write into widgets_values. */
const serialized = (node) =>
  node.widgets.filter((w) => w.options?.serialize !== false).map((w) => w.name);

test("registered as identity_forge.cosplayer.ui", () => {
  assert.ok(ext, "expected app.registerExtension with name identity_forge.cosplayer.ui");
});

test("the filter sits directly beneath the character widget it acts on", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  const names = node.widgets.map((w) => w.name);
  assert.equal(
    names.indexOf("franchise_filter"),
    names.indexOf("character") + 1,
    "the filter must render immediately under character, not appended at the end",
  );
});

test("widgets_values is unchanged -- older saved workflows cannot break", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  // The schema order, i.e. what a workflow saved before this file existed holds.
  const fromSchema = widgetsFor("IdentityForgeCosplayer").map((w) => w.name);
  assert.deepEqual(
    serialized(node),
    fromSchema,
    "the filter must not appear in widgets_values, and must not reorder anything that does",
  );
  assert.equal(
    widgetNamed(node, "franchise_filter").options.serialize,
    false,
    "the filter widget must be declared serialize: false",
  );
});

test("filtering to a franchise narrows the list but keeps every sentinel", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  const character = widgetNamed(node, "character");
  const filter = widgetNamed(node, "franchise_filter");

  filter.callback("Guilty Gear");
  const shown = optionsOf(character);

  for (const sentinel of SENTINELS) {
    assert.ok(shown.includes(sentinel), `sentinel ${sentinel} must survive filtering`);
  }
  assert.ok(shown.includes("Baiken"), "an in-franchise character must be shown");
  assert.ok(!shown.includes("Iron Man"), "an out-of-franchise character must be hidden");
  assert.equal(
    shown.length,
    SENTINELS.length + 11,
    "Guilty Gear ships 11 characters, so the list is the sentinels plus those",
  );
});

test("a character already chosen is never filtered away", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  const character = widgetNamed(node, "character");
  const filter = widgetNamed(node, "franchise_filter");

  character.value = "Iron Man";
  filter.callback("Guilty Gear");

  assert.equal(character.value, "Iron Man", "filtering must never change the selection");
  assert.ok(
    optionsOf(character).includes("Iron Man"),
    "the current selection must stay reachable in the list even out of franchise",
  );
});

test("resetting to Any restores the full list, not a narrowed one", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  const character = widgetNamed(node, "character");
  const filter = widgetNamed(node, "franchise_filter");
  const before = optionsOf(character).length;

  filter.callback("Persona");
  assert.ok(optionsOf(character).length < before, "filtering should narrow the list");

  filter.callback("Any");
  assert.equal(
    optionsOf(character).length,
    before,
    "every filter derives from the pristine snapshot, so Any restores it exactly",
  );
});

/**
 * A minimal LiteGraph-shaped base `configure`: assign each `widgets_values[i]`
 * positionally across ALL widgets (not just serializing ones) -- exactly the
 * real-frontend behaviour the WIDGETS_ADDED_BY_RELEASE comment documents ("this
 * node has 8 widgets ... serialize() still emits 8 values -- one per entry in
 * node.widgets. configure() reads them back the same way"). This is what
 * `padLegacyCosplayerValues` exists to feed the right values into: the extension
 * wraps `nodeType.prototype.configure`, pads `info.widgets_values`, then calls the
 * original (this) before LiteGraph's own onConfigure fires.
 */
async function createConfigurableNode() {
  class FakeNodeType {}
  FakeNodeType.prototype.configure = function (info) {
    const values = info?.widgets_values || [];
    (this.widgets || []).forEach((w, i) => {
      if (i < values.length) w.value = values[i];
    });
  };
  await ext.beforeRegisterNodeDef(FakeNodeType, { name: "IdentityForgeCosplayer" });
  const node = makeFakeNode("IdentityForgeCosplayer");
  FakeNodeType.prototype.onNodeCreated.call(node);
  return { node, FakeNodeType };
}

test("configure pads an 8-value (pre-random_pool) widgets_values onto the right widgets", async () => {
  const { node, FakeNodeType } = await createConfigurableNode();

  // A workflow saved after franchise_filter existed (0.89.0) but before
  // random_pool (1.1.0): one value per widget except the newest addition.
  const oldOrder = node.widgets.filter((w) => w.name !== "random_pool");
  assert.equal(oldOrder.length, 8, "sanity: 8 pre-1.1.0 widgets");
  const saved = oldOrder.map((w) => `saved-${w.name}`);

  FakeNodeType.prototype.configure.call(node, { widgets_values: saved });

  for (const [i, w] of oldOrder.entries()) {
    assert.equal(w.value, saved[i], `${w.name} should hold its saved value`);
  }
  assert.equal(
    widgetNamed(node, "random_pool").value,
    "All characters",
    "the newly added widget must fall back to its own default, not shift a saved value",
  );
});

test("configure pads a 7-value (pre-franchise_filter) widgets_values onto the right widgets", async () => {
  const { node, FakeNodeType } = await createConfigurableNode();

  // A workflow saved before franchise_filter (0.89.0) AND before random_pool
  // (1.1.0) -- both widgets_values additions must be padded in together.
  const oldOrder = node.widgets.filter(
    (w) => w.name !== "random_pool" && w.name !== "franchise_filter",
  );
  assert.equal(oldOrder.length, 7, "sanity: 7 pre-0.89.0 widgets");
  const saved = oldOrder.map((w) => `saved-${w.name}`);

  FakeNodeType.prototype.configure.call(node, { widgets_values: saved });

  for (const [i, w] of oldOrder.entries()) {
    assert.equal(w.value, saved[i], `${w.name} should hold its saved value`);
  }
  assert.equal(
    widgetNamed(node, "random_pool").value,
    "All characters",
    "random_pool must fall back to its own default",
  );
});

test("configure leaves a full 9-value (1.1.0) widgets_values untouched", async () => {
  const { node, FakeNodeType } = await createConfigurableNode();

  const saved = node.widgets.map((w) => `saved-${w.name}`);
  assert.equal(saved.length, 9, "sanity: 9 current widgets");

  FakeNodeType.prototype.configure.call(node, { widgets_values: saved });

  for (const [i, w] of node.widgets.entries()) {
    assert.equal(w.value, saved[i], `${w.name} should hold its saved value unshifted`);
  }
});

/**
 * Bug 2 (1.1.0 fix round, critical): ComfyUI's own V3 `ComfyNode.prototype.configure`
 * runs a `migrateWidgetsValues(nodeData.inputs, node.widgets, widgets_values)` step
 * -- shipped in ComfyUI's own frontend bundle, not this repo's code -- before handing
 * off to the real positional assignment. That helper strips a stale `widgets_values`
 * slot for any schema input that is now `forceInput` (always a socket, e.g. this
 * node's `upstream` chaining input), based on a slot count computed PURELY from the
 * Python schema. It has no idea this file adds an extra JS-only widget
 * (`franchise_filter`), so when its schema-derived count coincidentally equals the
 * real `widgets_values.length` -- which it always does for this node's current
 * (1.1.0) shape: 6 plain inputs + 2 slots for `seed`'s `control_after_generate` + 1
 * for the always-`forceInput` `upstream` = 9, matching this node's real 9-widget
 * count once `franchise_filter` and `random_pool` both exist -- it unconditionally
 * strips the LAST element of `widgets_values`, because `random_pool` (not
 * `upstream`) is actually the last schema input. That is `random_pool`'s slot. Confirmed live
 * against a real ComfyUI instance via Playwright (see the fix-round report); this
 * test reproduces the exact algorithm (mirrored from the shipped bundle, decompiled
 * via `configure.toString()` during that live investigation) against a fake node so
 * a regression is caught without a browser.
 */
function reproduceRealComfyMigrateWidgetsValues(node, values) {
  const widgetNames = new Set((node.widgets || []).map((w) => w.name));
  const inputs = node.constructor.nodeData.inputs;
  const mask = [];
  for (const input of Object.values(inputs)) {
    if (!(widgetNames.has(input.name) || input.forceInput)) continue;
    if (input.control_after_generate) mask.push(false, false);
    else mask.push(Boolean(input.forceInput));
  }
  if (mask.length !== values.length) return values;
  return values.filter((_, i) => !mask[i]);
}

test("random_pool survives ComfyUI's own widgets_values migration step (bug 2 regression)", async () => {
  class FakeNodeType {}
  // Mirrors nodes/identity_forge_cosplayer.py's real define_schema() input shape --
  // in particular, `upstream` is `forceInput: true` and `random_pool` is the LAST
  // schema input (appended after `upstream`), and `seed` carries
  // `control_after_generate`.
  FakeNodeType.nodeData = {
    inputs: {
      character: { name: "character" },
      random_scope: { name: "random_scope" },
      look_level: { name: "look_level" },
      mask: { name: "mask" },
      props: { name: "props" },
      seed: { name: "seed", control_after_generate: true },
      upstream: { name: "upstream", forceInput: true },
      random_pool: { name: "random_pool" },
    },
  };
  // A minimal base `configure()` that ONLY does what ComfyUI's real one does before
  // the (unmodelled here) LiteGraph positional assignment: run the migration, then
  // assign positionally. This is deliberately the same shape as
  // createConfigurableNode()'s fake base configure elsewhere in this file, plus the
  // migration step that reproduces the real bug.
  FakeNodeType.prototype.configure = function (info) {
    const values = reproduceRealComfyMigrateWidgetsValues(this, info?.widgets_values || []);
    (this.widgets || []).forEach((w, i) => { if (i < values.length) w.value = values[i]; });
  };
  await ext.beforeRegisterNodeDef(FakeNodeType, { name: "IdentityForgeCosplayer" });
  const node = makeFakeNode("IdentityForgeCosplayer");
  node.constructor = FakeNodeType;
  FakeNodeType.prototype.onNodeCreated.call(node);

  const saved = [
    "Chun-Li", "Any", "Any", "Costume only", "Default", "No prop", 12345, "fixed",
    "Mascot suits and beasts only",
  ];
  assert.equal(node.widgets.length, saved.length, "sanity: 9 widgets for 9 saved values");

  FakeNodeType.prototype.configure.call(node, { widgets_values: saved });

  assert.equal(
    widgetNamed(node, "random_pool").value,
    "Mascot suits and beasts only",
    "random_pool must round-trip through ComfyUI's own migration step, not silently revert to its default",
  );
  // Every other widget must still land correctly too -- the fix must not shift
  // anything else to compensate.
  const expected = ["character", "franchise_filter", "random_scope", "look_level",
    "mask", "props", "seed", "control_after_generate", "random_pool"];
  assert.deepEqual(node.widgets.map((w) => w.name), expected, "sanity: widget order unchanged");
  for (const [i, name] of expected.entries()) {
    if (name === "franchise_filter") continue; // view-only, not part of `saved`'s intent
    assert.equal(widgetNamed(node, name).value, saved[i], `${name} must hold its saved value`);
  }
});

test("a character the generated map does not know stays visible under every filter", async () => {
  // Stands in for a user_options.json addition: present in the live combo, absent
  // from the AST-generated map. It must never be hidden by a filter.
  const node = makeFakeNode("IdentityForgeCosplayer");
  const character = widgetNamed(node, "character");
  character.options.values = [...character.options.values, "My Private OC"];

  const FakeNodeType = await driveBeforeRegisterNodeDef(ext, "IdentityForgeCosplayer");
  FakeNodeType.prototype.onNodeCreated.call(node);

  widgetNamed(node, "franchise_filter").callback("Guilty Gear");
  assert.ok(
    optionsOf(character).includes("My Private OC"),
    "an unknown name is treated as unfiltered -- hiding a user's own character is the worst failure",
  );
});

// Task 4c: `random_pool` visually draws grouped with `random_scope` (the other
// randomization-constraint widget) without moving in `node.widgets` -- unlike
// `franchise_filter` above, `random_pool` IS a serializing, Python-schema
// widget, so its array index must never change (see `js/identity_forge_cosplayer.js`'s
// `applyVisualWidgetOrder` comment for the full mechanism and why
// `franchise_filter`'s own array-splice trick does not generalize to it).

const APPROVED_VISUAL_ORDER = [
  "character", "franchise_filter", "random_scope", "random_pool",
  "look_level", "mask", "props", "seed",
  // LiteGraph's own auto-added companion widget for an int with
  // control_after_generate -- not in the brief's list, so it keeps its
  // natural place directly after the widget it belongs to.
  "control_after_generate",
];

test("random_pool's visual reorder never moves node.widgets' real array order", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  const fromSchema = widgetsFor("IdentityForgeCosplayer").map((w) => w.name);
  const expectedRealOrder = [
    fromSchema[0], "franchise_filter", ...fromSchema.slice(1),
  ];
  assert.deepEqual(
    node.widgets.map((w) => w.name),
    expectedRealOrder,
    "random_pool must stay in its define_schema()-appended (last) slot in node.widgets",
  );
  assert.equal(
    node.widgets[node.widgets.length - 1].name,
    "random_pool",
    "random_pool must remain the LAST widget in the real array, exactly as define_schema() put it",
  );
});

test("random_pool draws grouped with random_scope via getLayoutWidgets, not array order", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");

  assert.equal(
    typeof node.getLayoutWidgets,
    "function",
    "sanity: the fake node must expose getLayoutWidgets for this override to have anything to shadow",
  );
  assert.deepEqual(
    node.getLayoutWidgets().map((w) => w.name),
    APPROVED_VISUAL_ORDER,
    "getLayoutWidgets() -- what LiteGraph's _arrangeWidgets iterates to assign each " +
    "widget's drawn `.y` -- must reflect the approved visual order",
  );
  // The override must return the SAME widget objects, not copies -- otherwise
  // `.y`/`.last_y` assigned during layout would land on a throwaway object and
  // hit-testing/serialization (which use the real node.widgets objects) would
  // never see it.
  const realRandomPool = widgetNamed(node, "random_pool");
  const layoutRandomPool = node.getLayoutWidgets().find((w) => w.name === "random_pool");
  assert.equal(layoutRandomPool, realRandomPool, "getLayoutWidgets must return the real widget object");

  // And the real array is still untouched (belt-and-suspenders alongside the
  // dedicated test above -- this is the one hard constraint nothing here may break).
  assert.equal(
    node.widgets[node.widgets.length - 1].name,
    "random_pool",
    "the getLayoutWidgets override must not have moved random_pool in node.widgets",
  );
});

// Caught live against the real :8288 instance: overriding getLayoutWidgets alone
// visually did NOTHING, through a fresh node add and a full ComfyUI restart,
// because LiteGraph's _arrangeWidgets (which reads getLayoutWidgets) only re-runs
// when node._widgetSlotsDirty is true, and every widget here already went through
// one such pass -- using the OLD order -- during the node's own construction,
// before onNodeCreated (and this override) ever ran. Nothing else flips that flag
// back on for a getLayoutWidgets-only change, so the stale `.y` from that first
// pass would otherwise just keep drawing forever.
test("the reorder marks the node's widget layout dirty so LiteGraph actually redraws it", async () => {
  const node = await createNode(ext, "IdentityForgeCosplayer");
  assert.equal(
    node._widgetSlotsDirty,
    true,
    "must flip the same dirty flag addWidget/removeWidget use, or the graph's draw " +
    "loop never calls arrange() again and the old layout keeps drawing forever",
  );
});

test("visual reorder is idempotent across a duplicate onNodeCreated firing", async () => {
  const node = await createNodeTwice(ext, "IdentityForgeCosplayer");
  assert.deepEqual(
    node.getLayoutWidgets().map((w) => w.name),
    APPROVED_VISUAL_ORDER,
    "a second onNodeCreated firing must not double-wrap or corrupt the layout order",
  );
  assert.equal(
    node.widgets[node.widgets.length - 1].name,
    "random_pool",
    "a second onNodeCreated firing must not move random_pool in node.widgets either",
  );
});

test("the visual reorder is inert (never throws, never moves node.widgets) on a frontend with no getLayoutWidgets", async () => {
  // Older/classic LiteGraph has no getLayoutWidgets indirection point at all --
  // this is the fallback this fix must degrade to safely rather than error.
  const node = makeFakeNode("IdentityForgeCosplayer");
  delete node.getLayoutWidgets;

  const FakeNodeType = await driveBeforeRegisterNodeDef(ext, "IdentityForgeCosplayer");
  assert.doesNotThrow(() => FakeNodeType.prototype.onNodeCreated.call(node));

  assert.equal(
    typeof node.getLayoutWidgets,
    "undefined",
    "no getLayoutWidgets must be synthesized on a node whose frontend never had one",
  );
  assert.equal(
    node.widgets[node.widgets.length - 1].name,
    "random_pool",
    "node.widgets must still be untouched even when the cosmetic reorder cannot apply",
  );
});
