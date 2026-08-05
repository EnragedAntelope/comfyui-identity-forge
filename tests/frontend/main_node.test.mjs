/**
 * jsdom-free smoke tests for js/identity_forge.js (the main node's group
 * collapsing, master buttons, and gender-pool swapping). Each test is pinned
 * to a real or latent bug, not generic coverage -- see docs/architecture.md
 * for the harness's layers and honest limits.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { __getExtension } from "./stubs/app.js";
import { createNode, widgetsFor } from "./fake_node.mjs";

await import("../../js/identity_forge.js");
const ext = __getExtension("identity_forge.ui");

const GROUP_ORDER = [
  "Demographics", "Body", "Face", "Hair", "Makeup",
  "Jewelry & Nails", "Clothing", "Setting & Shot",
];

// The widgets define_schema() builds *before* looping over FIELD_DEFINITIONS
// (nodes/identity_forge.py) -- everything else in the fixture is a
// randomizable field. control_after_generate is the fixture generator's own
// synthetic addition (see scripts/dump_frontend_fixtures.py), not a second
// define_schema() entry, but it belongs in this list for the same reason.
const CONTROL_WIDGET_NAMES = [
  "seed", "control_after_generate", "gender", "wardrobe", "size_scale",
  "hair_color_scope", "accessory_density", "location_setting", "set_all_fields",
];

test("registered as identity_forge.ui", () => {
  assert.ok(ext, "expected app.registerExtension to have been called with name identity_forge.ui");
});

test("every non-control fixture widget lands under a group header, in GROUP_ORDER order", async () => {
  const fixtureNames = widgetsFor("IdentityForge").map((w) => w.name);
  const expectedFields = new Set(fixtureNames.filter((n) => !CONTROL_WIDGET_NAMES.includes(n)));

  const node = await createNode(ext, "IdentityForge");

  let currentGroup = null;
  const seenGroupsInOrder = [];
  const fieldsUnderGroup = new Set();

  for (const w of node.widgets) {
    if (w.type === "button" && /^[▾▸] /.test(w.name)) {
      const label = w.name.slice(2);
      if (GROUP_ORDER.includes(label)) {
        currentGroup = label;
        seenGroupsInOrder.push(label);
      }
      continue;
    }
    if (currentGroup && expectedFields.has(w.name)) fieldsUnderGroup.add(w.name);
  }

  assert.deepEqual(seenGroupsInOrder, GROUP_ORDER,
    "group headers must appear exactly once each, in GROUP_ORDER order");
  assert.deepEqual([...fieldsUnderGroup].sort(), [...expectedFields].sort(),
    "every non-control field from the live Python schema must land under some group header " +
    "-- a field missing here means js/identity_forge.js's hand-maintained FIELD_TO_GROUP is " +
    "stale relative to data/fields.py");
});

test("every original widget survives setup exactly once, plus only master buttons and headers added", async () => {
  const originalNames = widgetsFor("IdentityForge").map((w) => w.name);
  const node = await createNode(ext, "IdentityForge");
  const finalNames = node.widgets.map((w) => w.name);

  assert.equal(new Set(finalNames).size, finalNames.length, "no widget should appear twice");
  for (const name of originalNames) {
    assert.ok(finalNames.includes(name), `expected original widget ${name} to survive setup`);
  }

  const added = finalNames.filter((n) => !originalNames.includes(n));
  const masterNames = added.filter((n) => n.includes("Unlock all") || n.includes("Roll + lock all"));
  const headerNames = added.filter((n) => /^[▾▸] /.test(n));
  assert.equal(masterNames.length, 2, "expected exactly the two master buttons");
  assert.equal(added.length, masterNames.length + headerNames.length,
    "only master buttons and group headers should be new widgets");
});

test("collapsing then re-expanding a group does not leave a stale computeSize stub", async () => {
  const node = await createNode(ext, "IdentityForge");
  const header = node.widgets.find((w) => w.name === "▾ Body");
  const bodyField = node.widgets.find((w) => w.name === "height");
  assert.ok(header && bodyField);

  assert.equal(Object.prototype.hasOwnProperty.call(bodyField, "computeSize"), false,
    "a never-collapsed widget should not carry a computeSize override");

  header.callback(); // collapse
  assert.equal(header.name, "▸ Body");

  header.callback(); // re-expand
  assert.equal(header.name, "▾ Body");
  assert.equal(Object.prototype.hasOwnProperty.call(bodyField, "computeSize"), false,
    "re-expanding must remove the computeSize stub (delete), not reassign it to undefined " +
    "-- an own property with value undefined still fails a hasOwnProperty-style layout check");

  // A second full round-trip -- off->on->off->on -- must behave identically.
  header.callback();
  header.callback();
  assert.equal(header.name, "▾ Body");
  assert.equal(Object.prototype.hasOwnProperty.call(bodyField, "computeSize"), false);
});

test("seed's control_after_generate sibling survives and stays immediately adjacent", async () => {
  const node = await createNode(ext, "IdentityForge");
  const seedIndex = node.widgets.findIndex((w) => w.name === "seed");
  assert.notEqual(seedIndex, -1);
  assert.equal(node.widgets[seedIndex + 1]?.name, "control_after_generate");
});

test("every button widget is created with options.serialize === false", async () => {
  const node = await createNode(ext, "IdentityForge");
  const buttons = node.widgets.filter((w) => w.type === "button");
  assert.ok(buttons.length >= 10, "expected 2 master buttons + one header per non-empty group");
  for (const b of buttons) {
    assert.equal(b.options?.serialize, false, `button "${b.name}" must set serialize:false`);
  }
});

test("switching gender re-scopes gender-divergent option lists and resets an invalid lock", async () => {
  const node = await createNode(ext, "IdentityForge");
  const genderW = node.widgets.find((w) => w.name === "gender");
  const facialHairW = node.widgets.find((w) => w.name === "facial_hair");
  assert.ok(genderW && facialHairW);

  // "goatee" is male-only per data/fields.py's facial_hair pool.
  facialHairW.value = "goatee";
  assert.ok(facialHairW.options.values.includes("goatee"), "sanity: goatee starts available under Any");

  genderW.value = "Female";
  genderW.callback("Female");
  assert.ok(!facialHairW.options.values.includes("goatee"),
    "the Female pool must not offer a male-only facial_hair value");
  assert.equal(facialHairW.value, "Random",
    "a lock that's invalid for the new gender must reset to Random rather than stick");

  genderW.value = "Male";
  genderW.callback("Male");
  assert.ok(facialHairW.options.values.includes("goatee"),
    "switching back to Male must restore the male-only option");
});
