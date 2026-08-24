/**
 * jsdom-backed smoke tests for js/identity_forge_vault.js -- the only file
 * in this pack's frontend that touches the DOM directly (an inline preview
 * image and the Manage Vault modal). See docs/architecture.md for the
 * harness's layers and honest limits.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { installDom, resetDom } from "./dom.mjs";
import { __getExtension } from "./stubs/app.js";
import { __setFetchApiHandler, __getFetchApiCalls, __resetApi } from "./stubs/api.js";
import { createNode, createNodeTwice } from "./fake_node.mjs";

installDom();

await import("../../js/identity_forge_vault.js");
const ext = __getExtension("identity_forge.vault");

const SAMPLE_CHARACTERS = [
  { name: "Zoe, 25, auburn hair", source_label: "random", created: "2026-08-01T10:00:00", has_preview: true },
  { name: "Sky Pirate cosplay", source_label: "Archetype", created: "2026-08-02T11:00:00", has_preview: false },
];

function respondWithCharacters(characters = SAMPLE_CHARACTERS) {
  __setFetchApiHandler(async (route) => {
    if (route === "/identity_forge/vault/characters") {
      return { ok: true, json: async () => ({ characters }) };
    }
    return { ok: true, json: async () => ({}) };
  });
}

async function flush() {
  // Drains every pending microtask hop in fetchCharacters()/refresh()'s
  // await chain -- a macrotask boundary guarantees they've all settled.
  await new Promise((resolve) => setTimeout(resolve, 0));
}

async function setup(characters = SAMPLE_CHARACTERS) {
  resetDom();
  __resetApi();
  respondWithCharacters(characters);
  const node = await createNode(ext, "IdentityForgeVaultLoad");
  await flush(); // let the initial on-create refresh() settle
  return node;
}

test("registered as identity_forge.vault", () => {
  assert.ok(ext, "expected app.registerExtension to have been called with name identity_forge.vault");
});

test("both picker buttons and the inline preview DOM widget are present, buttons non-serializing", async () => {
  const node = await setup();
  const refreshBtn = node.widgets.find((w) => w.name === "🔄 Refresh");
  const manageBtn = node.widgets.find((w) => w.name === "🗂 Manage Vault…");
  const preview = node.widgets.find((w) => w.name === "vault_preview");

  assert.ok(refreshBtn, "Refresh button must exist");
  assert.ok(manageBtn, "Manage Vault button must exist");
  assert.ok(preview, "vault_preview DOM widget must exist");
  assert.equal(refreshBtn.options?.serialize, false);
  assert.equal(manageBtn.options?.serialize, false);
  assert.equal(preview.options?.serialize, false);
});

test("refresh populates the character combo from the vault characters route", async () => {
  const node = await setup();
  const charW = node.widgets.find((w) => w.name === "character");
  assert.ok(charW);
  assert.deepEqual(charW.options.values, SAMPLE_CHARACTERS.map((c) => c.name));
});

test("an empty vault falls back to the no-characters sentinel, matching the Python default", async () => {
  const node = await setup([]);
  const charW = node.widgets.find((w) => w.name === "character");
  assert.deepEqual(charW.options.values, ["(no characters saved)"]);
});

test("Manage Vault opens an overlay with one card per character, and closes on a backdrop click", async () => {
  const node = await setup();
  const manageBtn = node.widgets.find((w) => w.name === "🗂 Manage Vault…");

  manageBtn.callback();
  await flush(); // openManager's own reload() is async

  const overlay = document.body.firstElementChild;
  assert.ok(overlay, "expected an overlay to be appended to document.body");
  const cards = overlay.querySelectorAll(":scope > div > div[style*='grid'] > div");
  assert.equal(cards.length, SAMPLE_CHARACTERS.length, "expected one card per character");

  // Clicking the panel itself must NOT close the dialog -- only the backdrop.
  overlay.firstElementChild.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(document.body.contains(overlay), true, "a click on the panel must not close the overlay");

  overlay.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  assert.equal(document.body.contains(overlay), false, "a backdrop click must close (remove) the overlay");
});

test("delete posts to the delete route with a JSON content type", async () => {
  const node = await setup();
  const manageBtn = node.widgets.find((w) => w.name === "🗂 Manage Vault…");
  const originalConfirm = globalThis.confirm;
  globalThis.confirm = () => true; // accept the "delete N character(s)?" prompt

  manageBtn.callback();
  await flush();

  const overlay = document.body.firstElementChild;
  const deleteBtn = [...overlay.querySelectorAll("button")].find((b) => b.textContent.includes("Delete selected"));
  assert.ok(deleteBtn, "expected a bulk delete button");

  // Select the first card's checkbox, then bulk-delete.
  overlay.querySelector("input[type=checkbox]").click();
  deleteBtn.click();
  await flush();

  globalThis.confirm = originalConfirm;

  const calls = __getFetchApiCalls().filter((c) => c.route === "/identity_forge/vault/delete");
  assert.equal(calls.length, 1, "expected exactly one delete call");
  assert.equal(calls[0].opts?.method, "POST");
  // Load-bearing per __init__.py's CSRF note: the vault routes require this
  // header on mutating requests specifically so a plain cross-origin HTML
  // form (which cannot set it) can't trigger one.
  assert.equal(calls[0].opts?.headers?.["Content-Type"], "application/json");
});


/* --- Re-entry guard (0.97.0) --------------------------------------------- */
test("a second onNodeCreated adds no second Refresh, Manage or preview widget", async () => {
  resetDom();
  __resetApi();
  respondWithCharacters();
  const node = await createNodeTwice(ext, "IdentityForgeVaultLoad");
  await flush();
  const names = node.widgets.map((w) => w.name);
  const dupes = names.filter((n, i) => names.indexOf(n) !== i);
  assert.deepEqual(dupes, [], `widgets appearing twice: ${dupes.join(", ")}`);
  assert.equal(names.filter((n) => n === "vault_preview").length, 1,
    "a second DOM preview widget is the one that visibly breaks the node");
});

/* --- A failed fetch is not an empty vault (0.97.0) ----------------------- */
test("an unreachable vault API is reported, not rendered as an empty vault", async () => {
  resetDom();
  __resetApi();
  __setFetchApiHandler(async () => { throw new Error("connection refused"); });
  const node = await createNode(ext, "IdentityForgeVaultLoad");
  await flush();
  const charW = node.widgets.find((w) => w.name === "character");
  assert.deepEqual(charW.options.values, ["(vault unavailable \u2014 press Refresh)"]);
  assert.notDeepEqual(charW.options.values, ["(no characters saved)"],
    "a dead server must not look like an empty vault");
});

test("a non-ok response is treated as unavailable, not as an empty vault", async () => {
  resetDom();
  __resetApi();
  __setFetchApiHandler(async () => ({ ok: false, status: 500, json: async () => ({}) }));
  const node = await createNode(ext, "IdentityForgeVaultLoad");
  await flush();
  const charW = node.widgets.find((w) => w.name === "character");
  assert.deepEqual(charW.options.values, ["(vault unavailable \u2014 press Refresh)"]);
});

/* --- A failed delete must not look like a success (0.97.0) --------------- */
test("a failed delete surfaces the error instead of silently reloading", async () => {
  resetDom();
  __resetApi();
  const alerts = [];
  globalThis.alert = (message) => alerts.push(String(message));
  globalThis.confirm = () => true;
  __setFetchApiHandler(async (route) => {
    if (route === "/identity_forge/vault/characters") {
      return { ok: true, json: async () => ({ characters: SAMPLE_CHARACTERS }) };
    }
    if (route === "/identity_forge/vault/delete") {
      return { ok: false, status: 500, json: async () => ({ error: "disk is read-only" }) };
    }
    return { ok: true, json: async () => ({}) };
  });
  const node = await createNode(ext, "IdentityForgeVaultLoad");
  await flush();
  const manage = node.widgets.find((w) => w.name === "\u{1F5C2} Manage Vault\u2026");
  assert.ok(manage, "Manage Vault button must exist");
  manage.callback();
  await flush();

  const del = [...document.querySelectorAll("button")]
    .find((b) => b.textContent === "\u{1F5D1}");
  assert.ok(del, "expected a per-card delete button");
  del.onclick();
  await flush();

  assert.ok(alerts.some((m) => m.includes("disk is read-only")),
    `expected the server's reason to reach the user; got ${JSON.stringify(alerts)}`);
});
