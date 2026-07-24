import { app } from "../../scripts/app.js";

/*
 * IdentityForge frontend extension.
 *
 * Data (GROUP_ORDER / FIELD_TO_GROUP / GENDER_POOLS) is generated from
 * data/fields.py — regenerate it if the Python field definitions change.
 *
 * Features (all degrade gracefully; any failure is caught so the node still
 * works headless):
 *   - Master buttons: set every field to "Random", or lock every field to a
 *     concrete random value.
 *   - Collapsible group sections so the many widgets stay manageable.
 *   - Gender pool-swapping: changing the gender toggle restricts the
 *     gender-divergent dropdowns and resets any now-invalid lock to "Random".
 *
 * Per-field locking needs no JS: selecting a concrete value locks a field,
 * selecting "Random" unlocks it. "Random"/"None" persist through ComfyUI's
 * native widget serialization, so saved workflows round-trip unchanged.
 */

const GROUP_ORDER = ["Demographics", "Body", "Face", "Hair", "Makeup", "Jewelry & Nails", "Clothing", "Setting & Shot"];
const FIELD_TO_GROUP = {
  "age": "Demographics",
  "ethnicity": "Demographics",
  "skin_tone": "Body",
  "body_type": "Body",
  "height": "Body",
  "bust": "Body",
  "waist": "Body",
  "hips": "Body",
  "face_shape": "Face",
  "eye_color": "Face",
  "eye_shape": "Face",
  "nose": "Face",
  "lips": "Face",
  "cheekbones": "Face",
  "jawline": "Face",
  "chin": "Face",
  "eyebrows": "Face",
  "skin_details": "Face",
  "hair_color": "Hair",
  "hair_length": "Hair",
  "hair_texture": "Hair",
  "hair_style": "Hair",
  "facial_hair": "Hair",
  "hair_accessory": "Hair",
  "makeup_style": "Makeup",
  "eye_makeup": "Makeup",
  "eyeliner": "Makeup",
  "lashes": "Makeup",
  "lips_makeup": "Makeup",
  "blush": "Makeup",
  "skin_finish": "Makeup",
  "earrings": "Jewelry & Nails",
  "necklace": "Jewelry & Nails",
  "other_jewelry": "Jewelry & Nails",
  "piercings": "Jewelry & Nails",
  "nails": "Jewelry & Nails",
  "outfit_style": "Clothing",
  "bag": "Clothing",
  "accessories": "Clothing",
  "expression": "Setting & Shot",
  "location": "Setting & Shot",
  "lighting": "Setting & Shot",
  "shot_type": "Setting & Shot",
  "forehead": "Face",
  "smile_type": "Face",
  "freckles_density": "Face",
  "complexion": "Face",
  "shoulder_width": "Body",
  "neck_length": "Body",
  "posture": "Body",
  "fitness_level": "Body",
  "hair_part": "Hair",
  "hair_highlights": "Hair",
  "eyebrow_makeup": "Makeup",
  "contour": "Makeup",
  "highlight": "Makeup",
  "rings": "Jewelry & Nails",
  "bracelet": "Jewelry & Nails",
  "watch_type": "Jewelry & Nails",
  "footwear": "Clothing",
  "clothing_color": "Clothing",
  "clothing_pattern": "Clothing",
  "season": "Setting & Shot",
  "mood": "Setting & Shot",
  "pose": "Setting & Shot"
};
const GENDER_POOLS = {
  "bust": {
    "Female": [
      "Random",
      "very small",
      "small",
      "modest",
      "medium",
      "full",
      "large",
      "very large",
      "generously proportioned",
      "None"
    ],
    "Male": [
      "Random",
      "flat",
      "slightly defined",
      "average",
      "broad",
      "muscular",
      "large",
      "None"
    ],
    "Any": [
      "Random",
      "very small",
      "small",
      "modest",
      "medium",
      "full",
      "large",
      "very large",
      "generously proportioned",
      "flat",
      "slightly defined",
      "average",
      "broad",
      "muscular",
      "None"
    ]
  },
  "facial_hair": {
    "Female": [
      "Random",
      "None"
    ],
    "Male": [
      "Random",
      "stubble",
      "short beard",
      "full beard",
      "goatee",
      "mustache",
      "van dyke",
      "soul patch",
      "mutton chops",
      "five o'clock shadow",
      "None"
    ],
    "Any": [
      "Random",
      "stubble",
      "short beard",
      "full beard",
      "goatee",
      "mustache",
      "van dyke",
      "soul patch",
      "mutton chops",
      "five o'clock shadow",
      "None"
    ]
  },
  "makeup_style": {
    "Female": [
      "Random",
      "barely there natural makeup",
      "soft natural makeup",
      "fresh-faced dewy look",
      "classic no-makeup makeup",
      "soft everyday glam",
      "soft glam",
      "full glam",
      "bold glam",
      "heavy glam",
      "editorial makeup",
      "vintage 1950s pin-up makeup",
      "mod 1960s eye makeup",
      "gothic dark makeup",
      "club makeup",
      "None"
    ],
    "Male": [
      "Random",
      "barely there natural makeup",
      "soft natural makeup",
      "fresh-faced dewy look",
      "classic no-makeup makeup",
      "None"
    ],
    "Any": [
      "Random",
      "barely there natural makeup",
      "soft natural makeup",
      "fresh-faced dewy look",
      "classic no-makeup makeup",
      "soft everyday glam",
      "soft glam",
      "full glam",
      "bold glam",
      "heavy glam",
      "editorial makeup",
      "vintage 1950s pin-up makeup",
      "mod 1960s eye makeup",
      "gothic dark makeup",
      "club makeup",
      "None"
    ]
  },
  "hair_accessory": {
    "Female": [
      "Random",
      "hair bow",
      "oversized hair bow",
      "satin ribbon tied in hair",
      "silk headband",
      "knotted headband",
      "padded headband",
      "scrunchie",
      "claw clip",
      "small hair clip",
      "decorative hair pins",
      "jeweled hair comb",
      "thin scarf tied in hair",
      "flower crown",
      "None"
    ],
    "Male": [
      "Random",
      "thin headband",
      "bandana tied over hair",
      "None"
    ],
    "Any": [
      "Random",
      "hair bow",
      "oversized hair bow",
      "satin ribbon tied in hair",
      "silk headband",
      "knotted headband",
      "padded headband",
      "scrunchie",
      "claw clip",
      "small hair clip",
      "decorative hair pins",
      "jeweled hair comb",
      "thin scarf tied in hair",
      "flower crown",
      "thin headband",
      "bandana tied over hair",
      "None"
    ]
  },
  "hair_length": {
    "Female": [
      "Random",
      "buzzed very short",
      "very short",
      "short pixie",
      "ear length",
      "chin length bob",
      "jaw length",
      "shoulder length",
      "slightly past shoulders",
      "mid back",
      "lower back",
      "long",
      "very long",
      "waist length",
      "hip length",
      "None"
    ],
    "Male": [
      "Random",
      "bald",
      "buzzed very short",
      "very short",
      "short pixie",
      "ear length",
      "chin length bob",
      "jaw length",
      "shoulder length",
      "slightly past shoulders",
      "mid back",
      "lower back",
      "long",
      "very long",
      "waist length",
      "hip length",
      "None"
    ],
    "Any": [
      "Random",
      "buzzed very short",
      "very short",
      "short pixie",
      "ear length",
      "chin length bob",
      "jaw length",
      "shoulder length",
      "slightly past shoulders",
      "mid back",
      "lower back",
      "long",
      "very long",
      "waist length",
      "hip length",
      "bald",
      "None"
    ]
  },
  "hair_style": {
    "Female": [
      "Random",
      "worn down",
      "half up half down",
      "high ponytail",
      "low ponytail",
      "side ponytail",
      "messy bun",
      "sleek bun",
      "top knot",
      "chignon",
      "side braid",
      "fishtail braid",
      "French braid",
      "dutch braids",
      "crown braid",
      "waterfall braid",
      "loose braids",
      "box braids",
      "cornrows",
      "locs",
      "space buns",
      "pigtails",
      "high pigtails",
      "low pigtails",
      "curled pigtails",
      "braided pigtails",
      "bantu knots",
      "afro",
      "twist-out",
      "updo",
      "French twist",
      "slicked back",
      "curtain bangs",
      "blunt bangs",
      "wet look",
      "windswept",
      "freshly blown out",
      "natural and unstyled",
      "tousled bedhead",
      "ballerina bun",
      "braided ponytail",
      "None"
    ],
    "Male": [
      "Random",
      "worn down",
      "half up half down",
      "high ponytail",
      "low ponytail",
      "side ponytail",
      "messy bun",
      "sleek bun",
      "top knot",
      "chignon",
      "side braid",
      "fishtail braid",
      "French braid",
      "dutch braids",
      "crown braid",
      "waterfall braid",
      "loose braids",
      "box braids",
      "cornrows",
      "locs",
      "space buns",
      "pigtails",
      "high pigtails",
      "low pigtails",
      "curled pigtails",
      "braided pigtails",
      "bantu knots",
      "afro",
      "twist-out",
      "updo",
      "French twist",
      "slicked back",
      "curtain bangs",
      "blunt bangs",
      "wet look",
      "windswept",
      "freshly blown out",
      "natural and unstyled",
      "tousled bedhead",
      "ballerina bun",
      "braided ponytail",
      "comb over",
      "mullet",
      "None"
    ],
    "Any": [
      "Random",
      "worn down",
      "half up half down",
      "high ponytail",
      "low ponytail",
      "side ponytail",
      "messy bun",
      "sleek bun",
      "top knot",
      "chignon",
      "side braid",
      "fishtail braid",
      "French braid",
      "dutch braids",
      "crown braid",
      "waterfall braid",
      "loose braids",
      "box braids",
      "cornrows",
      "locs",
      "space buns",
      "pigtails",
      "high pigtails",
      "low pigtails",
      "curled pigtails",
      "braided pigtails",
      "bantu knots",
      "afro",
      "twist-out",
      "updo",
      "French twist",
      "slicked back",
      "curtain bangs",
      "blunt bangs",
      "wet look",
      "windswept",
      "freshly blown out",
      "natural and unstyled",
      "tousled bedhead",
      "ballerina bun",
      "braided ponytail",
      "comb over",
      "mullet",
      "None"
    ]
  }
};

function isFieldWidget(w) {
  return w && Object.prototype.hasOwnProperty.call(FIELD_TO_GROUP, w.name);
}

function setWidgetValue(node, w, value) {
  if (!w) return;
  w.value = value;
  if (typeof w.callback === "function") {
    try { w.callback(value, app.canvas, node); } catch (e) { /* ignore */ }
  }
}

function lockToRandomValue(node, w) {
  const opts = (w.options && w.options.values) || [];
  const concrete = opts.filter((o) => o !== "Random" && o !== "None");
  if (!concrete.length) return;
  const pick = concrete[Math.floor(Math.random() * concrete.length)];
  setWidgetValue(node, w, pick);
}

// --- collapse helpers (hide a widget without losing its type) -------------
function hideWidget(w) {
  if (w.__hidden) return;
  w.__hidden = true;
  w.__origType = w.type;
  w.__origComputeSize = w.computeSize;
  w.type = "if_hidden";
  w.computeSize = () => [0, -4];
}

function showWidget(w) {
  if (!w.__hidden) return;
  w.__hidden = false;
  w.type = w.__origType;
  w.computeSize = w.__origComputeSize;
  w.__origType = null;
  w.__origComputeSize = null;
}

function resize(node) {
  if (typeof node.computeSize === "function") {
    const sz = node.computeSize();
    node.setSize([Math.max(node.size[0], sz[0]), sz[1]]);
  }
  node.setDirtyCanvas(true, true);
}

function setupIdentityForge(node) {
  const original = node.widgets ? node.widgets.slice() : [];
  if (!original.length) return;

  const fields = original.filter(isFieldWidget);
  const fieldSet = new Set(fields);
  // Everything that isn't a randomizable field — the seed (and its auto-added
  // control_after_generate widget) and the global controls (gender, wardrobe,
  // hair_color_scope, accessory_density, location_setting) — kept in original
  // schema order. Filtering by "not a field" (rather than a name allow-list)
  // means linked/auto widgets like control_after_generate are never dropped.
  const preFields = original.filter((w) => !fieldSet.has(w));

  // --- master buttons ---
  // "Random" on a field = randomize it each run; any concrete value = lock it.
  const allRandom = node.addWidget("button", "🎲 Unlock all (set to Random)", null, () => {
    for (const w of fields) setWidgetValue(node, w, "Random");
    resize(node);
  }, { serialize: false });

  const lockAll = node.addWidget("button", "🔒 Roll + lock all fields", null, () => {
    for (const w of fields) if (w.value === "Random") lockToRandomValue(node, w);
    resize(node);
  }, { serialize: false });

  // --- group headers + collapse ---
  const groups = new Map();
  for (const groupName of GROUP_ORDER) groups.set(groupName, []);
  for (const w of fields) {
    const g = FIELD_TO_GROUP[w.name];
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(w);
  }

  const headers = [];
  const ordered = [...preFields, allRandom, lockAll];
  for (const [groupName, groupWidgets] of groups) {
    if (!groupWidgets.length) continue;
    const state = { collapsed: false };
    const header = node.addWidget("button", "▾ " + groupName, null, () => {
      state.collapsed = !state.collapsed;
      header.name = (state.collapsed ? "▸ " : "▾ ") + groupName;
      for (const w of groupWidgets) (state.collapsed ? hideWidget : showWidget)(w);
      resize(node);
    }, { serialize: false });
    headers.push(header);
    ordered.push(header, ...groupWidgets);
  }

  // Safety net: append any original widget we didn't explicitly place, so a
  // future auto-added widget can never silently disappear.
  const placed = new Set(ordered);
  for (const w of original) if (!placed.has(w)) ordered.push(w);

  // Re-order the widget array so headers sit above their groups.
  node.widgets = ordered.filter((w, i) => ordered.indexOf(w) === i);

  // --- gender pool swapping ---
  const genderW = original.find((w) => w.name === "gender");
  if (genderW) {
    const prev = genderW.callback;
    genderW.callback = function (value) {
      if (typeof prev === "function") prev.apply(this, arguments);
      applyGender(node, value);
    };
    applyGender(node, genderW.value);
  }

  resize(node);
}

function applyGender(node, gender) {
  for (const [field, pools] of Object.entries(GENDER_POOLS)) {
    const w = (node.widgets || []).find((x) => x.name === field);
    if (!w || !w.options) continue;
    const opts = pools[gender] || pools["Any"];
    w.options.values = opts.slice();
    if (!opts.includes(w.value)) setWidgetValue(node, w, "Random");
  }
  node.setDirtyCanvas(true, true);
}

app.registerExtension({
  name: "identity_forge.ui",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "IdentityForge") return;
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
      try {
        setupIdentityForge(this);
      } catch (err) {
        console.error("[IdentityForge] frontend setup failed:", err);
      }
      return result;
    };
  },
});
