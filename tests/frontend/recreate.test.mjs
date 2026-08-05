/**
 * jsdom-free smoke tests for js/identity_forge_recreate.js -- a working
 * "Fix node (recreate)" for Identity Forge nodes, replacing ComfyUI-Manager's
 * broken one. See docs/architecture.md for the harness's layers and honest
 * limits.
 *
 * Recreate is pure LiteGraph mechanics (nodes, sockets, links) -- distinct
 * from the Python-schema-derived widgets fake_node.mjs builds -- so the
 * graph/socket layer below lives in this file rather than the shared driver.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { __getExtension } from "./stubs/app.js";
import { makeFakeNode } from "./fake_node.mjs";

await import("../../js/identity_forge_recreate.js");
const ext = __getExtension("identity_forge.recreate");

// -- fake LiteGraph graph + socket layer ------------------------------------

function makeGraph() {
  let nextNodeId = 1;
  let nextLinkId = 1;
  const nodes = new Map();
  const links = new Map();
  const graph = {
    add(node) {
      if (node.id == null) node.id = nextNodeId++;
      node.graph = graph;
      nodes.set(node.id, node);
    },
    // Mirrors real LiteGraph: removing a node disconnects every link
    // touching it (both ends), not just the node record itself. Without
    // this, a dangling link record would survive on the *other* node's
    // socket after removal and be double-counted once the recreate flow
    // reconnects a fresh link to replace it.
    remove(node) {
      for (const input of node.inputs || []) {
        if (input.link == null) continue;
        const link = links.get(input.link);
        if (link) {
          const originNode = nodes.get(link.origin_id);
          const originOutput = originNode && originNode.outputs[link.origin_slot];
          if (originOutput) originOutput.links = originOutput.links.filter((id) => id !== input.link);
          links.delete(input.link);
        }
        input.link = null;
      }
      for (const output of node.outputs || []) {
        for (const linkId of output.links || []) {
          const link = links.get(linkId);
          if (link) {
            const targetNode = nodes.get(link.target_id);
            const targetInput = targetNode && targetNode.inputs[link.target_slot];
            if (targetInput) targetInput.link = null;
            links.delete(linkId);
          }
        }
        output.links = [];
      }
      nodes.delete(node.id);
    },
    getNodeById(id) { return nodes.get(id) ?? null; },
    getLink(id) { return links.get(id) ?? null; },
    afterChange() {},
    __addLink(originNode, originSlot, targetNode, targetSlot) {
      const id = nextLinkId++;
      links.set(id, {
        id, origin_id: originNode.id, origin_slot: originSlot,
        target_id: targetNode.id, target_slot: targetSlot,
      });
      return id;
    },
  };
  return graph;
}

function withSockets(node, { inputs = [], outputs = [] } = {}) {
  node.inputs = inputs.map((name) => ({ name, link: null }));
  node.outputs = outputs.map((name) => ({ name, links: [] }));
  node.findInputSlot = function (name) { return this.inputs.findIndex((i) => i.name === name); };
  node.findOutputSlot = function (name) { return this.outputs.findIndex((o) => o.name === name); };
  // Mirrors real LiteGraph: connect(originSlot, targetNode, targetSlotOrName)
  // called on the ORIGIN node. Deliberately requires a real node object with
  // findInputSlot -- passing a bare id here throws, which is exactly how
  // this test catches rule 1 (connect() must receive the object, not an id).
  node.connect = function (originSlot, targetNode, targetSlotOrName) {
    const targetIndex = typeof targetSlotOrName === "number"
      ? targetSlotOrName : targetNode.findInputSlot(targetSlotOrName);
    if (targetIndex < 0) return null;
    const linkId = this.graph.__addLink(this, originSlot, targetNode, targetIndex);
    this.outputs[originSlot].links.push(linkId);
    targetNode.inputs[targetIndex].link = linkId;
    return linkId;
  };
  return node;
}

function wireLink(graph, originNode, outputName, targetNode, inputName) {
  const originSlot = originNode.outputs.findIndex((o) => o.name === outputName);
  const targetSlot = targetNode.inputs.findIndex((i) => i.name === inputName);
  assert.ok(originSlot >= 0 && targetSlot >= 0, "wireLink: named socket not found on test fixture");
  const linkId = graph.__addLink(originNode, originSlot, targetNode, targetSlot);
  originNode.outputs[originSlot].links.push(linkId);
  targetNode.inputs[targetSlot].link = linkId;
}

// The one socket shape LiteGraph.createNode needs to know to build a
// *fresh* IdentityForge node -- matches nodes/identity_forge.py's real
// schema (one force_input socket in, two String outputs).
const FRESH_SOCKETS = { inputs: ["archetype_json"], outputs: ["prompt_text", "prompt_json"] };

function installLiteGraphStub() {
  globalThis.window = globalThis.window ?? {};
  window.LiteGraph = {
    createNode(type) {
      const node = makeFakeNode(type);
      withSockets(node, FRESH_SOCKETS);
      node.pos = [0, 0];
      return node;
    },
  };
}

function makeStubNode(graph, id, { comfyClass, widgets = [], inputs = [], outputs = [] }) {
  const node = { id, comfyClass, widgets, pos: [0, 0] };
  withSockets(node, { inputs, outputs });
  graph.add(node);
  return node;
}

async function captureWarnings(fn) {
  const calls = [];
  const original = console.warn;
  console.warn = (...args) => calls.push(args.join(" "));
  try {
    await fn();
  } finally {
    console.warn = original;
  }
  return calls;
}

function getRecreateCallback(node) {
  const options = [];
  node.getExtraMenuOptions(null, options);
  const entry = options.find((o) => o.content === "Fix node (recreate)");
  assert.ok(entry, "expected a Fix node (recreate) menu entry");
  return { options, callback: entry.callback };
}

/** Wraps graph.add/graph.remove to capture the fresh replacement node and
 * the add/remove order, without guessing at auto-assigned ids. */
function instrumentGraph(graph, originalNode) {
  const order = [];
  let freshNode = null;
  const originalAdd = graph.add.bind(graph);
  const originalRemove = graph.remove.bind(graph);
  graph.add = (n) => { order.push("add"); if (n !== originalNode) freshNode = n; originalAdd(n); };
  graph.remove = (n) => { order.push("remove"); originalRemove(n); };
  return { order, getFreshNode: () => freshNode };
}

// -- tests --------------------------------------------------------------

test("registered as identity_forge.recreate", () => {
  assert.ok(ext, "expected app.registerExtension to have been called with name identity_forge.recreate");
});

test("getExtraMenuOptions yields exactly one entry, replacing a pre-existing same-label one", async () => {
  const graph = makeGraph();
  const node = makeStubNode(graph, 1, {
    comfyClass: "IdentityForge", widgets: [], inputs: ["archetype_json"], outputs: ["prompt_text", "prompt_json"],
  });
  await ext.nodeCreated(node);

  const managersBrokenEntry = {
    content: "Fix node (recreate)",
    callback: () => { throw new Error("Manager's broken version must not run"); },
  };
  const options = [managersBrokenEntry, { content: "Something else" }];
  node.getExtraMenuOptions(null, options);

  const recreateEntries = options.filter((o) => o.content === "Fix node (recreate)");
  assert.equal(recreateEntries.length, 1, "must replace, not duplicate, a same-label entry");
  assert.notEqual(recreateEntries[0], managersBrokenEntry, "must be OUR callback, not Manager's");
  assert.ok(options.some((o) => o.content === "Something else"), "unrelated entries must survive");
});

test("a full recreate restores locked values by name, removes the original before reconnecting, and relinks by slot name", async () => {
  const graph = makeGraph();
  installLiteGraphStub();

  const upstream = makeStubNode(graph, 10, { comfyClass: "IdentityForgeArchetype", outputs: ["character_json"] });
  const downstream = makeStubNode(graph, 20, { comfyClass: "CLIPTextEncode", inputs: ["text"] });

  // Real, fixture-valid values -- copyWidgetValues checks the value against
  // the *fresh* node's own (real, Python-schema-derived) option list, so a
  // value that isn't actually one of them would be legitimately dropped,
  // not a bug this test is trying to catch.
  const node = makeStubNode(graph, 30, {
    comfyClass: "IdentityForge",
    widgets: [
      { name: "age", type: "combo", value: "18" },
      { name: "composition", type: "combo", value: "the subject on a rule-of-thirds line" },
    ],
    inputs: ["archetype_json"], outputs: ["prompt_text", "prompt_json"],
  });
  wireLink(graph, upstream, "character_json", node, "archetype_json");
  wireLink(graph, node, "prompt_text", downstream, "text");

  await ext.nodeCreated(node);
  const { callback } = getRecreateCallback(node);
  const { order, getFreshNode } = instrumentGraph(graph, node);

  callback();

  assert.deepEqual(order, ["add", "remove"],
    "the fresh node must be added, and the original removed, before any reconnect is attempted");

  assert.equal(graph.getNodeById(30), null, "the original node's id must no longer resolve");
  const freshNode = getFreshNode();
  assert.ok(freshNode, "expected the recreate to have added a fresh node");
  assert.equal(freshNode.comfyClass, "IdentityForge");

  // Rule 2: values restored by name.
  const ageW = freshNode.widgets.find((w) => w.name === "age");
  const compW = freshNode.widgets.find((w) => w.name === "composition");
  assert.equal(ageW.value, "18");
  assert.equal(compW.value, "the subject on a rule-of-thirds line");

  // Rule 3 + the input side of rule 1: the upstream node's output link now
  // targets the fresh node's "archetype_json" input, not the old node.
  assert.equal(upstream.outputs[0].links.length, 1);
  const upstreamLink = graph.getLink(upstream.outputs[0].links[0]);
  assert.equal(upstreamLink.target_id, freshNode.id);
  const archetypeSlot = freshNode.findInputSlot("archetype_json");
  assert.equal(upstreamLink.target_slot, archetypeSlot);

  // The output side: downstream's "text" input now links from the fresh
  // node's "prompt_text" output, reconnected by name.
  const textLink = graph.getLink(downstream.inputs.find((i) => i.name === "text").link);
  assert.equal(textLink.origin_id, freshNode.id);
  assert.equal(textLink.origin_slot, freshNode.findOutputSlot("prompt_text"));
});

test("a button whose name changed at runtime (a collapsed header) is skipped, never reported dropped", async () => {
  const graph = makeGraph();
  installLiteGraphStub();
  const node = makeStubNode(graph, 40, {
    comfyClass: "IdentityForge",
    widgets: [
      // Simulates a group collapsed by the user before recreate: the
      // header's *name* is "▸ Body", which will not exist verbatim on a
      // fresh node (freshly created headers always start expanded, "▾ Body").
      { name: "▸ Body", type: "button", value: null, options: { serialize: false } },
    ],
    inputs: ["archetype_json"], outputs: ["prompt_text", "prompt_json"],
  });
  await ext.nodeCreated(node);
  const { callback } = getRecreateCallback(node);
  instrumentGraph(graph, node);

  const warnings = await captureWarnings(async () => callback());
  assert.ok(!warnings.some((w) => w.includes("▸ Body")),
    "a renamed button must never be reported as a dropped widget");
});

test("a saved value invalid for the fresh node's options falls back to default with exactly one named warning", async () => {
  const graph = makeGraph();
  installLiteGraphStub();
  const node = makeStubNode(graph, 50, {
    comfyClass: "IdentityForge",
    widgets: [
      { name: "size_scale", type: "combo", value: "Off", options: { values: ["Auto", "giant", "tiny"] } },
    ],
    inputs: ["archetype_json"], outputs: ["prompt_text", "prompt_json"],
  });
  await ext.nodeCreated(node);
  const { callback } = getRecreateCallback(node);
  const { getFreshNode } = instrumentGraph(graph, node);

  const warnings = await captureWarnings(async () => callback());
  const matching = warnings.filter((w) => w.includes("size_scale"));
  assert.equal(matching.length, 1, "expected exactly one warning naming the dropped widget");

  const sizeScaleW = getFreshNode().widgets.find((w) => w.name === "size_scale");
  assert.notEqual(sizeScaleW.value, "Off", "an invalid saved value must not be forced onto the fresh widget");
});

test("an input link the fresh node cannot resolve a matching slot for is not silently dropped", async () => {
  // Simulates a widget converted to an input socket (right-click "Convert
  // to input") on the original node -- flagged as a known, deferred
  // limitation in the 0.85.0 worklog: the fresh node reverts it to a plain
  // widget, so `findInputSlot` fails and (before this revision's fix) the
  // link vanished with no message at all.
  const graph = makeGraph();
  installLiteGraphStub(); // fresh IdentityForge nodes only ever expose archetype_json
  const upstream = makeStubNode(graph, 70, { comfyClass: "IdentityForgeArchetype", outputs: ["character_json"] });
  const node = makeStubNode(graph, 80, {
    comfyClass: "IdentityForge",
    widgets: [],
    inputs: ["archetype_json", "gender"], // "gender" simulates the converted widget
    outputs: ["prompt_text", "prompt_json"],
  });
  wireLink(graph, upstream, "character_json", node, "gender");

  await ext.nodeCreated(node);
  const { callback } = getRecreateCallback(node);

  const warnings = await captureWarnings(async () => callback());
  assert.ok(warnings.some((w) => w.includes("gender")),
    "a link the fresh node can't reconnect must produce a warning naming the affected input, " +
    "not vanish silently");
});
