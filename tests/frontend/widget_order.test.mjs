/**
 * Saved `widgets_values` is in SCHEMA order for the three nodes whose JS re-sorts or
 * inserts widgets (1.8.0), so a tool without a browser can map the array by position.
 *
 * ComfyUI writes one value per entry of `node.widgets`, buttons and headers included.
 * IdentityForge and IdentityForgeCreature group their widgets under headers and
 * IdentityForgeCosplayer splices `franchise_filter` in after `character`; each saves
 * the schema widgets only and marks the save with `properties.if_widget_order`.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { installDom } from "./dom.mjs";
import { __getExtension } from "./stubs/app.js";
import { makeFakeNode, widgetsFor } from "./fake_node.mjs";

installDom();

await import("../../js/identity_forge.js");
await import("../../js/identity_forge_creature.js");
await import("../../js/identity_forge_cosplayer.js");

const NODES = [
  ["IdentityForge", "identity_forge.ui"],
  ["IdentityForgeCreature", "identity_forge.creature.ui"],
  ["IdentityForgeCosplayer", "identity_forge.cosplayer.ui"],
];

/** A fake node type with a LiteGraph-shaped serialize/configure pair, extension applied. */
async function build(nodeId, extName) {
  class FakeNodeType {}
  FakeNodeType.prototype.configure = function (info) {
    const values = info?.widgets_values || [];
    (this.widgets || []).forEach((w, i) => { if (i < values.length) w.value = values[i]; });
    this.properties = { ...(info?.properties || {}) };
  };
  FakeNodeType.prototype.serialize = function () {
    const o = {
      widgets_values: this.widgets.map((w) => (w ? w.value : null)),
      properties: { ...(this.properties || {}) },
    };
    this.onSerialize?.(o);
    return o;
  };
  await __getExtension(extName).beforeRegisterNodeDef(FakeNodeType, { name: nodeId });
  const node = makeFakeNode(nodeId);
  Object.setPrototypeOf(node, FakeNodeType.prototype);
  FakeNodeType.prototype.onNodeCreated.call(node);
  return { node, FakeNodeType };
}

const schemaNames = (nodeId) => widgetsFor(nodeId).map((w) => w.name);
const byName = (node, name) => node.widgets.find((w) => w.name === name);

for (const [nodeId, extName] of NODES) {
  test(`${nodeId}: serializes the schema widgets in schema order, marked, with no gaps`, async () => {
    const { node } = await build(nodeId, extName);
    for (const name of schemaNames(nodeId)) byName(node, name).value = `saved-${name}`;

    const saved = node.serialize();
    assert.deepEqual(saved.widgets_values, schemaNames(nodeId).map((n) => `saved-${n}`));
    assert.ok(saved.widgets_values.every((v) => v !== null && v !== undefined));
    assert.equal(saved.properties.if_widget_order, "schema");
  });

  test(`${nodeId}: a schema-order save round-trips onto the right widgets`, async () => {
    const { node } = await build(nodeId, extName);
    for (const name of schemaNames(nodeId)) byName(node, name).value = `saved-${name}`;
    const saved = JSON.parse(JSON.stringify(node.serialize()));

    const { node: fresh } = await build(nodeId, extName);
    fresh.configure({ widgets_values: saved.widgets_values, properties: saved.properties });
    for (const name of schemaNames(nodeId)) {
      assert.equal(byName(fresh, name).value, `saved-${name}`, `${name} should be restored`);
    }
  });

  test(`${nodeId}: a pre-1.8.0 interleaved save still loads by position`, async () => {
    const { node } = await build(nodeId, extName);
    // What 1.7.0 wrote: one value per entry of node.widgets, display order, no marker.
    const legacy = node.widgets.map((w, i) => `legacy-${i}-${w.name}`);

    node.configure({ widgets_values: legacy });
    node.widgets.forEach((w, i) => {
      assert.equal(w.value, legacy[i], `${w.name} should hold the value saved at its slot`);
    });
  });

  test(`${nodeId}: a marked save one field short leaves the missing field at its default`, async () => {
    const { node } = await build(nodeId, extName);
    const names = schemaNames(nodeId);
    for (const name of names) byName(node, name).value = `saved-${name}`;
    const saved = JSON.parse(JSON.stringify(node.serialize()));
    // A save from before the last schema field existed.
    const short = saved.widgets_values.slice(0, -1);

    const { node: fresh } = await build(nodeId, extName);
    const lastName = names[names.length - 1];
    const dflt = byName(fresh, lastName).value;
    fresh.configure({ widgets_values: short, properties: saved.properties });

    assert.equal(byName(fresh, lastName).value, dflt, `${lastName} keeps its default`);
    for (const name of names.slice(0, -1)) {
      assert.equal(byName(fresh, name).value, `saved-${name}`, `${name} restored`);
    }
  });
}

test("IdentityForgeCosplayer: franchise_filter is not saved", async () => {
  const { node } = await build("IdentityForgeCosplayer", "identity_forge.cosplayer.ui");
  assert.ok(byName(node, "franchise_filter"), "the filter widget exists on the node");
  const saved = node.serialize();
  assert.equal(saved.widgets_values.length, schemaNames("IdentityForgeCosplayer").length);
});
