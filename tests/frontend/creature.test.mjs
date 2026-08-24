/**
 * jsdom-free smoke tests for js/identity_forge_creature.js -- the multiline
 * DOM-textarea positioning, hybrid-slot bulk buttons, and collapse round-trip.
 * See docs/architecture.md for the harness's layers and honest limits.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { installDom } from "./dom.mjs";
import { __getExtension } from "./stubs/app.js";
import { createNode, createNodeTwice } from "./fake_node.mjs";

// No DOM manipulation happens in this file, but the module unconditionally
// calls requestAnimationFrame() at the end of setup (to correct the
// more_features textarea's position after first layout) -- installDom()
// is the harness's one source of that global.
installDom();

await import("../../js/identity_forge_creature.js");
const ext = __getExtension("identity_forge.creature.ui");

const SLOT_NAMES = ["head", "eyes", "integument", "arms", "hands", "legs_feet", "tail", "wings"];

test("registered as identity_forge.creature.ui", () => {
  assert.ok(ext, "expected app.registerExtension to have been called with name identity_forge.creature.ui");
});

test("more_features sits immediately after the headline widgets, above both group headers", async () => {
  const node = await createNode(ext, "IdentityForgeCreature");
  const names = node.widgets.map((w) => w.name);
  const moreFeaturesIndex = names.indexOf("more_features");
  const hybridHeaderIndex = names.indexOf("▾ Hybrid slots");
  const detailHeaderIndex = names.indexOf("▾ Detail");

  assert.notEqual(moreFeaturesIndex, -1, "more_features widget must exist");
  assert.notEqual(hybridHeaderIndex, -1, "Hybrid slots header must exist");
  assert.notEqual(detailHeaderIndex, -1, "Detail header must exist");

  // The file's own header comment explains why: a textarea placed below a
  // collapsible group desyncs on first paint (ComfyUI positions DOM widgets
  // by summing the heights of everything above them). Anchoring it right
  // after the stable headline widgets, above both groups, is the fix.
  assert.ok(moreFeaturesIndex < hybridHeaderIndex,
    "more_features must sit above the Hybrid slots group header");
  assert.ok(moreFeaturesIndex < detailHeaderIndex,
    "more_features must sit above the Detail group header");

  // Nothing but headline widgets (creature/form/seed/control_after_generate)
  // precedes it.
  for (let i = 0; i < moreFeaturesIndex; i++) {
    assert.ok(!SLOT_NAMES.includes(names[i]) && names[i] !== "integument_finish" &&
      names[i] !== "palette" && names[i] !== "size_scale",
      `widget "${names[i]}" (a grouped field) must not sit above more_features`);
  }
});

test("collapsing then re-expanding Hybrid slots does not leave a stale computeSize stub", async () => {
  const node = await createNode(ext, "IdentityForgeCreature");
  const header = node.widgets.find((w) => w.name === "▾ Hybrid slots");
  const headSlot = node.widgets.find((w) => w.name === "head");
  assert.ok(header && headSlot);

  assert.equal(Object.prototype.hasOwnProperty.call(headSlot, "computeSize"), false);

  header.callback(); // collapse
  assert.equal(header.name, "▸ Hybrid slots");

  header.callback(); // re-expand
  assert.equal(header.name, "▾ Hybrid slots");
  assert.equal(Object.prototype.hasOwnProperty.call(headSlot, "computeSize"), false,
    "re-expanding must remove the computeSize stub (delete), not reassign it to undefined");
});

test("Slots: all Random / all Follow base set every slot widget and fire its callback", async () => {
  const node = await createNode(ext, "IdentityForgeCreature");
  const calls = [];
  for (const name of SLOT_NAMES) {
    const w = node.widgets.find((x) => x.name === name);
    w.callback = (v) => calls.push([name, v]);
  }

  const allRandom = node.widgets.find((w) => w.name === "Slots: all Random");
  const allFollow = node.widgets.find((w) => w.name === "Slots: all Follow base");
  assert.ok(allRandom && allFollow, "expected both bulk-set buttons");

  allRandom.callback();
  for (const name of SLOT_NAMES) {
    const w = node.widgets.find((x) => x.name === name);
    assert.equal(w.value, "Random");
  }
  assert.equal(calls.length, SLOT_NAMES.length, "every slot's callback must fire on bulk-set");

  calls.length = 0;
  allFollow.callback();
  for (const name of SLOT_NAMES) {
    const w = node.widgets.find((x) => x.name === name);
    assert.equal(w.value, "Follow base");
  }
  assert.equal(calls.length, SLOT_NAMES.length);
});

test("both bulk-set buttons and both group headers are created with options.serialize === false", async () => {
  const node = await createNode(ext, "IdentityForgeCreature");
  const buttons = node.widgets.filter((w) => w.type === "button");
  assert.equal(buttons.length, 4, "2 bulk-set buttons + 2 group headers");
  for (const b of buttons) {
    assert.equal(b.options?.serialize, false, `button "${b.name}" must set serialize:false`);
  }
});


/* --- Re-entry guard (0.97.0) --------------------------------------------- */
test("a second onNodeCreated adds no second set of headers or bulk buttons", async () => {
  const once = await createNode(ext, "IdentityForgeCreature");
  const twice = await createNodeTwice(ext, "IdentityForgeCreature");

  assert.equal(twice.widgets.length, once.widgets.length,
    "re-entry duplicated widgets");
  const names = twice.widgets.map((w) => w.name);
  const dupes = names.filter((n, i) => names.indexOf(n) !== i);
  assert.deepEqual(dupes, [], `widgets appearing twice: ${dupes.join(", ")}`);
  assert.equal(names.filter((n) => n === "Slots: all Follow base").length, 1);
  assert.equal(names.filter((n) => n === "Slots: all Random").length, 1);
});

/* --- Bulk-set must not abort halfway (0.97.0) ---------------------------- */
test("one throwing slot callback does not stop the rest of the bulk set", async () => {
  const node = await createNode(ext, "IdentityForgeCreature");
  const bulk = node.widgets.find((w) => w.name === "Slots: all Random");
  assert.ok(bulk, "the bulk-set button must exist");

  // Every slot the button drives, identified the way the module does: the
  // widgets that sit between the two bulk buttons and the next group header.
  const slots = node.widgets.filter(
    (w) => w.type === "combo" && typeof w.value === "string"
      && (w.options?.values || []).includes("Follow base"));
  assert.ok(slots.length >= 3, "expected several hybrid slots to exist");

  let calls = 0;
  for (const w of slots) {
    w.callback = () => { calls += 1; throw new Error("boom"); };
  }
  bulk.callback();

  assert.equal(calls, slots.length,
    "the loop stopped at the first throwing callback");
  for (const w of slots) {
    assert.equal(w.value, "Random", `${w.name} was left unset`);
  }
});

/* --- The hidden-widget sentinel (0.97.0) --------------------------------- */
test("a collapsed widget carries the same hidden type string as the main node", async () => {
  const node = await createNode(ext, "IdentityForgeCreature");
  const header = node.widgets.find((w) => typeof w.name === "string"
    && w.name.startsWith("\u25BE "));
  assert.ok(header, "expected at least one group header");
  header.callback();
  const hidden = node.widgets.filter((w) => w.type === "if_hidden");
  assert.ok(hidden.length > 0, "collapsing set no widget to the shared sentinel");
  assert.equal(
    node.widgets.filter((w) => w.type === "if_creature_hidden").length, 0,
    "the old creature-only sentinel is still in use");
});
