import { app } from "../../scripts/app.js";

/*
 * A working "Fix node (recreate)" for Identity Forge nodes.
 *
 * Why this file exists
 * --------------------
 * "Fix node (recreate)" is not a ComfyUI feature. It is contributed by
 * ComfyUI-Manager (js/node_fixer.js), and on frontend 1.47 its implementation
 * throws before it finishes:
 *
 *   TypeError: t.findInputSlot is not a function
 *     at LGraphNode.connect
 *     at node_info_copy   (node_fixer.js, reconnecting the inputs)
 *     at callback         (node_fixer.js)
 *
 * Node ids are strings now. Manager calls
 * `src_node.connect(origin_slot, dest.id, input_name)`, and `connect`
 * only resolves its second argument to a node when that argument is a
 * *number*. A string id sails past the lookup and `connect` then calls
 * `findInputSlot` on it.
 *
 * The callback creates the replacement node first and removes the original
 * last, so the exception leaves both on the canvas: the original still
 * wired up, the replacement unconnected and sitting on top of it. That is
 * the whole of the reported bug, and it is not specific to this pack — it
 * happens to any node with a connected input, in any pack. (See
 * comfyui-stylebook's ARCHITECTURE.md for the original writeup; this file
 * is a straight port with one addition for this pack's widget shape.)
 *
 * The fix is to stop relying on that code for our own nodes. This module
 * installs a correct recreate and takes the broken entry out of the menu,
 * for Identity Forge node instances only. Nothing global is patched and no
 * other pack's nodes are touched.
 *
 * Three rules make a recreate correct, and each of them is a bug avoided:
 *
 *   1. Pass the node OBJECT to connect(), never its id. Ids are strings.
 *   2. Restore widget values by NAME, never by index. Recreating a node is
 *      what you do *because* the schema changed, so an index-based copy
 *      writes every value into the wrong widget from the first added or
 *      removed input onward.
 *   3. Reconnect links by SLOT NAME, never by slot number, for the same
 *      reason.
 *
 * One addition beyond the Stylebook port: this pack's main node rebuilds
 * `node.widgets` at creation time into ~66 field combos plus ten button
 * widgets (two master buttons, one collapse header per group — see
 * identity_forge.js `setupIdentityForge`), and `gender` swaps the option
 * list of six other widgets via its wrapped callback. A plain by-name
 * value copy restores every field's *value* correctly, but does not
 * re-run that callback, so a restored non-default gender would leave the
 * gender-divergent widgets' dropdown options scoped to the fresh node's
 * default "Any" pool instead of the restored gender. `recreateNode` below
 * re-invokes the gender widget's own callback after copying values, which
 * re-applies the correct pool exactly as if the user had picked that
 * gender by hand.
 *
 * The whole thing is wrapped so that a failure leaves the graph exactly as
 * it was rather than half-rebuilt.
 */

const EXT_NAME = "identity_forge.recreate";
const MENU_LABEL = "Fix node (recreate)";

function warn(message, error) {
  console.warn("[" + EXT_NAME + "] " + message, error || "");
}

function isIdentityForgeNode(node) {
  const type = node && (node.comfyClass || (node.constructor && node.constructor.type));
  return Boolean(type) && String(type).startsWith("IdentityForge");
}

/** Resolve a link id to its link record across frontend versions. */
function getLink(graph, linkId) {
  if (linkId == null) return null;
  try {
    if (typeof graph.getLink === "function") return graph.getLink(linkId);
  } catch (_) {
    // fall through to the map/proxy form
  }
  try {
    return graph.links[linkId] || null;
  } catch (_) {
    return null;
  }
}

/**
 * Record every link touching *node*, keyed by slot name.
 *
 * Names, not numbers: the point of recreating a node is that its schema
 * moved, so slot 2 before is not slot 2 after.
 */
function snapshotLinks(node) {
  const graph = node.graph;
  const inputs = [];
  const outputs = [];

  for (const input of node.inputs || []) {
    const link = getLink(graph, input.link);
    if (!link) continue;
    const origin = graph.getNodeById(link.origin_id);
    if (!origin) continue;
    inputs.push({ name: input.name, origin, originSlot: link.origin_slot });
  }

  for (const output of node.outputs || []) {
    for (const linkId of output.links || []) {
      const link = getLink(graph, linkId);
      if (!link) continue;
      const target = graph.getNodeById(link.target_id);
      if (!target) continue;
      outputs.push({ name: output.name, target, targetSlot: link.target_slot });
    }
  }

  return { inputs, outputs };
}

/** The selectable values of a combo widget, or null if it is not one. */
function comboValues(widget) {
  const values = widget && widget.options && widget.options.values;
  if (typeof values === "function") {
    try {
      return values(widget) || null;
    } catch (_) {
      return null;
    }
  }
  return Array.isArray(values) ? values : null;
}

/**
 * Copy widget values from *from* to *to*, matched by name.
 *
 * A value that no longer exists in a combo's options is dropped rather
 * than forced, because writing an invalid value onto a widget produces a
 * node that fails prompt validation with a message about a value the user
 * never chose. The fresh node's default is the honest result, and the
 * dropped names are returned so the caller can say what happened.
 *
 * Button widgets (the two master buttons plus one collapse header per
 * field group) are skipped outright rather than relying on
 * `widget.serialize === false` alone: this pack ships ten of them, they
 * carry no data, and a toggled collapse header's *name* changes at
 * runtime ("▾ Body" / "▸ Body"), which would otherwise report every
 * collapsed group as a "dropped" widget on every recreate.
 */
function copyWidgetValues(from, to) {
  const dropped = [];
  const target = new Map();
  for (const widget of to.widgets || []) {
    if (widget && widget.name) target.set(widget.name, widget);
  }

  for (const widget of from.widgets || []) {
    if (!widget || !widget.name) continue;
    if (widget.type === "button" || widget.serialize === false) continue;
    const match = target.get(widget.name);
    if (!match) {
      dropped.push(widget.name);
      continue;
    }
    const values = comboValues(match);
    if (values && !values.includes(widget.value)) {
      dropped.push(widget.name);
      continue;
    }
    match.value = widget.value;
  }
  return dropped;
}

/**
 * Re-run the `gender` widget's own callback on the fresh node so the six
 * gender-divergent field widgets (bust, hair_length, hair_style,
 * facial_hair, hair_accessory, makeup_style) get their option lists
 * re-scoped to the just-restored gender, exactly as if the user had
 * picked it by hand. Without this the widgets keep the correct *value*
 * (copyWidgetValues already restored that) but the fresh node's default
 * "Any" pool as their *option list* until the user touches gender again.
 */
function reapplyGenderPools(node) {
  const genderWidget = (node.widgets || []).find((w) => w.name === "gender");
  if (!genderWidget || typeof genderWidget.callback !== "function") return;
  try {
    genderWidget.callback(genderWidget.value, app.canvas, node);
  } catch (error) {
    warn("could not re-apply gender-scoped options after recreate", error);
  }
}

/**
 * Replace *node* with a fresh instance of the same type, keeping its
 * position, size, title, colours, widget values and every link.
 */
function recreateNode(node) {
  const graph = node.graph || app.graph;
  const LiteGraph = window.LiteGraph;
  if (!graph || !LiteGraph) return false;

  const type = node.comfyClass || node.type;
  const fresh = LiteGraph.createNode(type);
  if (!fresh) {
    warn("could not create a replacement node of type " + type);
    return false;
  }

  const links = snapshotLinks(node);

  fresh.pos = [node.pos[0], node.pos[1]];
  if (node.title) fresh.title = node.title;
  if (node.color) fresh.color = node.color;
  if (node.bgcolor) fresh.bgcolor = node.bgcolor;
  graph.add(fresh);

  const dropped = copyWidgetValues(node, fresh);
  reapplyGenderPools(fresh);

  // Size after adding, so the node's own layout has already run and we are
  // widening rather than fighting it.
  if (node.size) {
    fresh.setSize([
      Math.max(node.size[0], fresh.size[0]),
      Math.max(node.size[1], fresh.size[1]),
    ]);
  }

  // Remove the original before reconnecting. An input holds one link, so
  // reconnecting first would fight the link that is still attached.
  graph.remove(node);

  // A link whose slot the fresh node doesn't expose -- most commonly a
  // widget the user converted to an input socket (right-click "Convert to
  // input"), which a freshly created node always reverts to a plain widget.
  // Silently dropping it would leave a graph that looks fixed but has quietly
  // lost a connection; name it instead, same as the dropped-widgets warning
  // below.
  const unresolvedLinks = [];
  for (const link of links.inputs) {
    const slot = fresh.findInputSlot(link.name);
    // The node object, never its id. Ids are strings, and connect() only
    // resolves numbers.
    if (slot >= 0) link.origin.connect(link.originSlot, fresh, slot);
    else unresolvedLinks.push(link.name);
  }
  for (const link of links.outputs) {
    const slot = fresh.findOutputSlot(link.name);
    if (slot >= 0) fresh.connect(slot, link.target, link.targetSlot);
    else unresolvedLinks.push(link.name);
  }

  if (unresolvedLinks.length) {
    warn(
      "recreated " + type + ", but these connections could not be restored " +
      "-- the fresh node no longer exposes a matching input/output slot " +
      "(likely a widget that was converted to a socket, which a fresh node " +
      "always reverts to a plain widget): " + unresolvedLinks.join(", ")
    );
  }

  if (dropped.length) {
    warn(
      "recreated " + type + ", but these widgets no longer exist or no " +
      "longer accept their saved value and were left at their default: " +
      dropped.join(", ")
    );
  }

  if (typeof graph.afterChange === "function") graph.afterChange();
  if (app.canvas) app.canvas.setDirty(true, true);
  return true;
}

/**
 * Drop any other pack's recreate entry and add ours in its place.
 *
 * Same label, so the entry stays where the muscle memory expects it.
 */
function replaceRecreateOption(node, options) {
  for (let index = options.length - 1; index >= 0; index -= 1) {
    const entry = options[index];
    if (entry && entry.content === MENU_LABEL) options.splice(index, 1);
  }
  options.push({
    content: MENU_LABEL,
    callback: () => {
      try {
        recreateNode(node);
      } catch (error) {
        warn("recreate failed; the graph was left unchanged", error);
      }
    },
  });
}

app.registerExtension({
  name: EXT_NAME,

  async nodeCreated(node) {
    try {
      if (!isIdentityForgeNode(node)) return;
      // NO re-entry guard here, deliberately. An audit listed this file with the
      // four setups that needed one at 0.97.0; measured, it does not. Re-entry
      // wraps our own wrapper, but `inherited` is captured before the assignment,
      // so the upstream handler still runs exactly once per menu open, and
      // replaceRecreateOption() de-duplicates by label so the entry appears once.
      // Both properties are pinned in tests/frontend/recreate.test.mjs -- a
      // refactor that breaks either one turns them red, which is worth more than
      // a flag guarding a failure that cannot happen.

      // An own property on the instance, not another prototype wrapper.
      // Every pack that contributes menu entries does it by wrapping the
      // prototype, and the last wrapper installed runs its own additions
      // last. An instance property shadows the whole prototype chain, so
      // we see the finished option list no matter what order the
      // extensions loaded in.
      const inherited = node.getExtraMenuOptions;
      node.getExtraMenuOptions = function (canvas, options) {
        let result;
        if (typeof inherited === "function") {
          try {
            result = inherited.call(this, canvas, options);
          } catch (error) {
            warn("an upstream menu handler failed", error);
          }
        }
        try {
          replaceRecreateOption(this, options);
        } catch (error) {
          warn("could not install the recreate menu entry", error);
        }
        return result;
      };
    } catch (error) {
      warn("menu setup failed", error);
    }
  },
});
