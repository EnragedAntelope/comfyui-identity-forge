/**
 * jsdom smoke tests for js/identity_forge_picker.js -- the roster search modal
 * (Phase 4b, 1.1.0).
 *
 * Follows the harness pattern in tests/frontend/cosplayer.test.mjs:9-29:
 * installDom() -> dynamic-import the module -> __getExtension(name) ->
 * createNode / createNodeTwice. Fetches are stubbed with a local `fetch`
 * override (there is no shared fetch stub in ./stubs, unlike api.fetchApi,
 * because this module deliberately never uses api.fetchApi -- see the
 * gh-pages absolute-URL requirement in the task brief).
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { installDom, resetDom } from "./dom.mjs";
import { __getExtension } from "./stubs/app.js";
import { createNode, createNodeTwice, makeFakeNode } from "./fake_node.mjs";

installDom();

const pickerModule = await import("../../js/identity_forge_picker.js");
await import("../../js/identity_forge_cosplayer.js"); // needed for the franchise_filter test
const { __testing } = pickerModule;
const pickerExt = __getExtension("identity_forge.picker.ui");
const cosplayerExt = __getExtension("identity_forge.cosplayer.ui");

// The real, generated roster -- these tests assert against actual data
// (brief: "qipa must find Chun-Li", etc.), not a synthetic fixture.
const REAL_ROSTER = JSON.parse(readFileSync(
  fileURLToPath(new URL("../../js/identity_forge_roster.json", import.meta.url)),
  "utf-8",
));

function installFetchStub(handler) {
  const calls = [];
  const previous = global.fetch;
  global.fetch = async (url, opts) => {
    const href = String(url);
    calls.push(href);
    return handler(href, opts);
  };
  return { calls, restore: () => { global.fetch = previous; } };
}

function rosterOkHandler(url) {
  if (url.endsWith("identity_forge_roster.json")) {
    return { ok: true, json: async () => REAL_ROSTER };
  }
  if (url.includes("github.io")) {
    return { ok: true, json: async () => ({ entries: [] }) };
  }
  return { ok: false, status: 404 };
}

function flush() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

test("registered as identity_forge.picker.ui", () => {
  assert.ok(pickerExt, "expected app.registerExtension with name identity_forge.picker.ui");
});

// --- attachment / re-entry guard --------------------------------------------

for (const nodeId of ["IdentityForgeCosplayer", "IdentityForgeArchetype", "IdentityForgeCreature"]) {
  test(`attaches a trigger button to ${nodeId}`, async () => {
    resetDom();
    const node = await createNode(pickerExt, nodeId);
    assert.equal(document.querySelectorAll(".if-picker-trigger-btn").length, 1);
    assert.ok(node.__identityForgePickerAttached);
  });
}

test("re-entry guard: onNodeCreated firing twice adds exactly one button, not two", async () => {
  resetDom();
  await createNodeTwice(pickerExt, "IdentityForgeCosplayer");
  assert.equal(
    document.querySelectorAll(".if-picker-trigger-btn").length,
    1,
    "a second onNodeCreated call must not add a second trigger button",
  );
});

test("does not attach to an unrelated node type", async () => {
  resetDom();
  await createNode(pickerExt, "IdentityForge");
  assert.equal(document.querySelectorAll(".if-picker-trigger-btn").length, 0);
});

test("the trigger button never occupies a widgets_values slot", async () => {
  resetDom();
  const node = await createNode(pickerExt, "IdentityForgeCosplayer");
  // The button must never be pushed into node.widgets at all -- not even
  // with serialize:false, which the 0.89.0 franchise_filter incident showed
  // still consumes a widgets_values slot on read.
  assert.ok(
    !node.widgets.some((w) => w.name === "🔍 Browse roster…" || w === node.__identityForgePickerButton),
    "the trigger button must not be a member of node.widgets",
  );
});

test("legacy widgets_values regression: attaching the button never shifts widget values", async () => {
  resetDom();
  // A minimal LiteGraph-shaped configure(), exactly like cosplayer.test.mjs's
  // createConfigurableNode helper: assign each widgets_values[i] onto
  // node.widgets[i] positionally, across every widget in node.widgets.
  class FakeNodeType {}
  FakeNodeType.prototype.configure = function (info) {
    const values = info?.widgets_values || [];
    (this.widgets || []).forEach((w, i) => {
      if (i < values.length) w.value = values[i];
    });
  };
  await pickerExt.beforeRegisterNodeDef(FakeNodeType, { name: "IdentityForgeCosplayer" });
  const node = makeFakeNode("IdentityForgeCosplayer");
  FakeNodeType.prototype.onNodeCreated.call(node);

  // The button attaches via onNodeCreated, never touching node.widgets, so a
  // full-length legacy widgets_values array (one entry per real schema
  // widget) must still map straight across with no shift at all.
  const saved = node.widgets.map((w) => `saved-${w.name}`);
  FakeNodeType.prototype.configure.call(node, { widgets_values: saved });
  for (const [i, w] of node.widgets.entries()) {
    assert.equal(w.value, saved[i], `${w.name} must hold its saved value unshifted`);
  }
  // The fixture's schema-only widget count (no franchise_filter here, since
  // identity_forge_cosplayer.js's own extension is not applied in this test)
  // must be exactly what the picker leaves behind: it must not append itself,
  // or anything else, to node.widgets.
  assert.equal(node.widgets.length, 8, "the button must not appear in node.widgets at all");
});

// --- search: substring, multi-token AND, cross-tab --------------------------

test("substring and two-token queries match plausible, non-empty sets in the real roster", () => {
  const cases = [
    ["qipa", "Chun-Li"],
    ["beard", null],
    ["skirt", null],
    ["tatt", null],
    ["female pirate", null],
    ["red cape", null],
  ];
  for (const [query, expectName] of cases) {
    const tokens = __testing.tokenize(query);
    const results = REAL_ROSTER.filter((e) => __testing.matchesQuery(e, tokens));
    assert.ok(results.length > 0, `"${query}" should return a non-empty, plausible result set`);
    if (expectName) {
      assert.ok(
        results.some((e) => e.name === expectName),
        `"${query}" should find ${expectName}`,
      );
    }
  }
});

test("cross-tab search: a query matches entries from every kind, not just the active tab", async () => {
  resetDom();
  __testing.__resetForTests();
  const stub = installFetchStub(rosterOkHandler);
  try {
    const node = await createNode(pickerExt, "IdentityForgeCosplayer");
    const picker = new __testing.IdentityForgePicker({
      kind: "cosplayer",
      targetWidgetName: "character",
      title: "test",
      node,
    });
    picker.open();
    await flush();
    // "armor" matches cosplayer, archetype AND creature entries in the real
    // roster. The active tab defaults to "cosplayer" (this node's own kind).
    picker.query = "armor";
    picker.renderGrid();
    const kinds = new Set(picker.visible.map((e) => e.kind));
    assert.ok(kinds.has("archetype"), "a query must surface archetype matches while on the cosplayer tab");
    assert.ok(kinds.has("creature"), "a query must surface creature matches while on the cosplayer tab");
    picker.close();
  } finally {
    stub.restore();
  }
});

test("an empty query is scoped to the active tab", async () => {
  __testing.__resetForTests();
  const stub = installFetchStub(rosterOkHandler);
  try {
    const node = makeFakeNode("IdentityForgeCosplayer");
    const picker = new __testing.IdentityForgePicker({
      kind: "cosplayer",
      targetWidgetName: "character",
      title: "test",
      node,
    });
    resetDom();
    picker.open();
    await flush();
    picker.query = "";
    picker.renderGrid();
    assert.ok(picker.visible.length > 0);
    assert.ok(
      picker.visible.every((e) => e.kind === "cosplayer"),
      "with no query, only the active tab's kind should be visible",
    );
    picker.close();
  } finally {
    stub.restore();
  }
});

// --- selecting sets the combo through the node's normal setter --------------

async function nodeWithFranchiseFilter() {
  class FakeNodeType {}
  await cosplayerExt.beforeRegisterNodeDef(FakeNodeType, { name: "IdentityForgeCosplayer" });
  await pickerExt.beforeRegisterNodeDef(FakeNodeType, { name: "IdentityForgeCosplayer" });
  const node = makeFakeNode("IdentityForgeCosplayer");
  FakeNodeType.prototype.onNodeCreated.call(node);
  return node;
}

test("selecting an entry sets the combo's value via the node's normal setter", async () => {
  resetDom();
  const node = await nodeWithFranchiseFilter();
  const character = node.widgets.find((w) => w.name === "character");
  let callbackValue = null;
  character.callback = (value) => { callbackValue = value; };

  const picker = new __testing.IdentityForgePicker({
    kind: "cosplayer",
    targetWidgetName: "character",
    franchiseFilterWidgetName: "franchise_filter",
    title: "test",
    node,
  });
  picker.select({ kind: "cosplayer", name: "Iron Man" });

  assert.equal(character.value, "Iron Man");
  assert.equal(callbackValue, "Iron Man", "the widget's own callback must fire, not a bare value assignment");
});

test("respects franchise_filter: a pick outside the active filter stays reachable", async () => {
  resetDom();
  const node = await nodeWithFranchiseFilter();
  const character = node.widgets.find((w) => w.name === "character");
  const filter = node.widgets.find((w) => w.name === "franchise_filter");

  filter.callback("Guilty Gear");
  assert.ok(!character.options.values.includes("Iron Man"), "sanity: Iron Man is filtered out by Guilty Gear");

  const picker = new __testing.IdentityForgePicker({
    kind: "cosplayer",
    targetWidgetName: "character",
    franchiseFilterWidgetName: "franchise_filter",
    title: "test",
    node,
  });
  picker.select({ kind: "cosplayer", name: "Iron Man" });

  assert.equal(character.value, "Iron Man");
  assert.ok(
    character.options.values.includes("Iron Man"),
    "the picked character must stay reachable in the combo despite the active franchise filter",
  );
});

test("selecting an entry of a different kind than the node's own is a no-op", async () => {
  resetDom();
  const node = await nodeWithFranchiseFilter();
  const character = node.widgets.find((w) => w.name === "character");
  const before = character.value;

  const picker = new __testing.IdentityForgePicker({
    kind: "cosplayer",
    targetWidgetName: "character",
    franchiseFilterWidgetName: "franchise_filter",
    title: "test",
    node,
  });
  picker.select({ kind: "archetype", name: "Elven Ranger" });

  assert.equal(character.value, before, "a foreign-kind entry must never be written into this node's combo");
});

// --- failed fetch degrades to a retry-able placeholder -----------------------

test("a failed data fetch degrades to a retry-able placeholder and never throws", async () => {
  resetDom();
  __testing.__resetForTests();
  let shouldFail = true;
  const stub = installFetchStub((url) => {
    if (url.endsWith("identity_forge_roster.json")) {
      if (shouldFail) return Promise.reject(new Error("network down"));
      return { ok: true, json: async () => REAL_ROSTER };
    }
    return { ok: true, json: async () => ({ entries: [] }) };
  });
  try {
    const node = makeFakeNode("IdentityForgeCosplayer");
    const picker = new __testing.IdentityForgePicker({
      kind: "cosplayer",
      targetWidgetName: "character",
      title: "test",
      node,
    });
    assert.doesNotThrow(() => picker.open());
    await flush();
    const empty = picker.grid.querySelector(".if-picker-empty");
    assert.ok(empty, "a failed fetch must show a placeholder, not an empty or broken grid");
    const retry = picker.grid.querySelector("button");
    assert.ok(retry, "the placeholder must offer a retry control");

    shouldFail = false;
    retry.dispatchEvent(new window.Event("click"));
    await flush();
    assert.ok(picker.visible.length > 0, "retrying after the network recovers must actually retry, not repeat the failure");
    picker.close();
  } finally {
    stub.restore();
  }
});

// --- thumbnails: opt-in, default off -----------------------------------------

test("thumbnails stay off (no gallery fetch) until the preview toggle is enabled", async () => {
  resetDom();
  __testing.__resetForTests();
  try {
    window.localStorage.removeItem("identity_forge.picker.show_previews");
  } catch (_) { /* ignore */ }
  const stub = installFetchStub(rosterOkHandler);
  try {
    const node = makeFakeNode("IdentityForgeCosplayer");
    const picker = new __testing.IdentityForgePicker({
      kind: "cosplayer",
      targetWidgetName: "character",
      title: "test",
      node,
    });
    picker.open();
    await flush();
    assert.ok(
      !stub.calls.some((u) => u.includes("github.io")),
      "no gallery manifest request must happen before the toggle is enabled",
    );

    picker.previewCheckbox.checked = true;
    picker.previewCheckbox.dispatchEvent(new window.Event("change"));
    await flush();
    assert.ok(
      stub.calls.some((u) => u.includes("github.io") && u.includes("manifest.json")),
      "enabling the toggle must fetch the live gh-pages manifest for the visible kind(s)",
    );
    picker.close();
  } finally {
    stub.restore();
  }
});

// --- trait facet vocabulary ---------------------------------------------------

test("trait facets mirror the six _SPECIAL_SCOPES values plus Task 2's three random_pool values", () => {
  const expected = [
    "All characters",
    "Giant characters",
    "Tiny characters",
    "Non-human / colored",
    "Masked",
    "Mascot / full-suit",
    "Beast / non-humanoid",
    "People only — no mascot suits or beasts",
    "Mascot suits and beasts only",
  ];
  assert.deepEqual(__testing.FACETS, expected);
});

test("facet predicates match real entries with the corresponding trait word", () => {
  const kingShark = REAL_ROSTER.find((e) => e.name === "King Shark");
  const teemo = REAL_ROSTER.find((e) => e.name === "Teemo");
  assert.ok(__testing.FACET_PREDICATES["Giant characters"](kingShark));
  assert.ok(__testing.FACET_PREDICATES["Mascot / full-suit"](teemo));
  assert.ok(!__testing.FACET_PREDICATES["People only — no mascot suits or beasts"](teemo));
  assert.ok(__testing.FACET_PREDICATES["Mascot suits and beasts only"](teemo));
});

test('"Non-human / colored" also matches the "an even ... coat of" phrasing, not just the two "smooth"/"uniform" wordings', () => {
  // Fix-round finding: the facet originally checked only two of the backend
  // regex's three alternatives, missing every entry using the legacy
  // "an even, all-over coat of <colour> <material>" wording (Maui among them)
  // -- 97 of ~301 backend-flagged entries in the real roster.
  const maui = REAL_ROSTER.find((e) => e.name === "Maui");
  assert.ok(maui, "sanity: Maui exists in the real roster");
  assert.ok(
    __testing.FACET_PREDICATES["Non-human / colored"](maui),
    'Maui uses "coat of" phrasing and must match the facet',
  );
});

// --- bug 1 (critical): the trigger button must be inert while its node is a
// LiteGraph "ghost" (spawned from the node-search palette, still following
// the mouse, not yet placed) -- clicking it in that state, then pressing
// Escape, let LiteGraph's own "cancel node placement" shortcut delete the
// node from underneath an open dialog. Verified live via Playwright before
// this fix (see the 1.1.0 fix-round report); this pins the click-side guard,
// which holds regardless of whether the position-tracking rAF loop is
// running (it never runs at all under this jsdom harness).

test("the trigger button does nothing while its node is still a LiteGraph ghost (unplaced)", async () => {
  resetDom();
  const node = await createNode(pickerExt, "IdentityForgeCosplayer");
  node.flags = { ghost: true };
  const button = node.__identityForgePickerButton;
  button.click();
  assert.equal(
    document.querySelector('[role="dialog"]'),
    null,
    "clicking the trigger while the node is an unplaced ghost must not open the picker",
  );
});

test("the trigger button works normally once the node is no longer a ghost", async () => {
  resetDom();
  const node = await createNode(pickerExt, "IdentityForgeCosplayer");
  node.flags = { ghost: false };
  const button = node.__identityForgePickerButton;
  button.click();
  assert.ok(
    document.querySelector('[role="dialog"]'),
    "a placed (non-ghost) node's trigger button must still open the picker",
  );
});

// --- bug 3 (moderate): loadManifest() must stay a Promise on repeat calls ---

test("loadManifest() returns a thenable on every call, including repeats after a successful fetch", async () => {
  __testing.__resetForTests();
  const stub = installFetchStub((url) => {
    if (url.includes("manifest.json")) {
      return {
        ok: true,
        json: async () => ({
          entries: [{ name: "Chun-Li", has_image: true, image: "images/Chun-Li.jpeg" }],
        }),
      };
    }
    return { ok: false, status: 404 };
  });
  try {
    const first = __testing.loadManifest("cosplayer");
    assert.equal(typeof first.then, "function", "the first call must return a thenable");
    const firstMap = await first;
    assert.equal(firstMap.get("Chun-Li"), "images/Chun-Li.jpeg");

    // The regression: after a successful resolution, the cache used to hold
    // the bare resolved Map instead of the Promise, so this second call
    // returned a non-Promise and `.then()` on it threw synchronously.
    const second = __testing.loadManifest("cosplayer");
    assert.equal(
      typeof second.then,
      "function",
      "a repeat call for an already-loaded kind must still return a thenable, not the raw resolved value",
    );
    const secondMap = await second;
    assert.equal(secondMap.get("Chun-Li"), "images/Chun-Li.jpeg");
  } finally {
    stub.restore();
  }
});

// --- bug 4 (minor): the query must survive a tab click ----------------------

test("switching tabs preserves the current search query, per the documented cross-tab design", async () => {
  resetDom();
  __testing.__resetForTests();
  const stub = installFetchStub(rosterOkHandler);
  try {
    const node = makeFakeNode("IdentityForgeCosplayer");
    const picker = new __testing.IdentityForgePicker({
      kind: "cosplayer",
      targetWidgetName: "character",
      title: "test",
      node,
    });
    picker.open();
    await flush();
    picker.query = "tatt";
    picker.renderGrid();
    const before = picker.visible.length;
    assert.ok(before > 0 && before < REAL_ROSTER.length, "sanity: the query narrowed the grid");

    const archetypesTab = Array.from(picker.tabs.children).find((el) => el.textContent === "Archetypes");
    assert.ok(archetypesTab, "sanity: an Archetypes tab exists");
    archetypesTab.click();

    assert.equal(picker.query, "tatt", "the query must survive a tab click");
    assert.equal(
      picker.visible.length,
      before,
      "the grid must still reflect the query, not reset to the clicked tab's full list",
    );
    picker.close();
  } finally {
    stub.restore();
  }
});

// --- bug 6 (minor): closing and reopening must show a consistent default ----
// state -- previously the search <input> reset to empty on rebuild but the
// `query`/`facet` state it reads from did not, so the box read empty while
// the grid stayed narrowed to whatever was typed or picked last time.

test("closing and reopening the picker resets both the search box and the grid together", async () => {
  resetDom();
  __testing.__resetForTests();
  const stub = installFetchStub(rosterOkHandler);
  try {
    const node = makeFakeNode("IdentityForgeCosplayer");
    const picker = new __testing.IdentityForgePicker({
      kind: "cosplayer",
      targetWidgetName: "character",
      title: "test",
      node,
    });
    picker.open();
    await flush();
    picker.query = "tatt";
    picker.renderGrid();
    assert.ok(picker.visible.length < REAL_ROSTER.length, "sanity: the query narrowed the grid");
    picker.facet = "Giant characters";

    picker.close();
    picker.open();
    await flush();

    assert.equal(picker.searchInput.value, "", "the reopened search box must be empty");
    assert.equal(picker.query, "", "the query state must be reset, not just the input's displayed value");
    assert.equal(picker.facet, "All characters", "the facet must reset to its default too");
    assert.ok(
      picker.visible.every((e) => e.kind === "cosplayer") && picker.visible.length > 1,
      "the grid must show the default unfiltered view for this node's kind, not the stale filtered set",
    );
    picker.close();
  } finally {
    stub.restore();
  }
});
