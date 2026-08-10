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
  createNode, makeFakeNode, widgetsFor, driveBeforeRegisterNodeDef,
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
