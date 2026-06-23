import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

/*
 * IdentityForge Vault frontend extension (Vault Load node).
 *
 * Adds, all degrading gracefully (every entry point is wrapped so the node still
 * works headless / on older frontends):
 *   - An inline thumbnail preview of the currently selected saved character.
 *   - A "🔄 Refresh" button that re-fetches the saved list without restarting
 *     ComfyUI, preserving the current selection when it still exists.
 *   - A "🗂 Manage Vault…" button opening a gallery modal to browse with
 *     thumbnails, pick (Use), rename, delete, and bulk-delete saved characters.
 *
 * Backend (registered in __init__.py):
 *   GET  /identity_forge/vault/characters        -> { characters: [{name, source_label, created, has_preview}] }
 *   GET  /identity_forge/vault/preview/{name}    -> preview.png
 *   POST /identity_forge/vault/delete  {names}   -> { characters: [...] }
 *   POST /identity_forge/vault/rename  {from,to} -> { name } | { error }
 */

const NODE = "IdentityForgeVaultLoad";
const NO_CHARACTERS = "(no characters saved)";

function apiURL(route) {
  try {
    if (typeof api.apiURL === "function") return api.apiURL(route);
  } catch (e) { /* ignore */ }
  return route;
}

function previewURL(name, bust) {
  const q = bust ? `?t=${Date.now()}` : "";
  return apiURL(`/identity_forge/vault/preview/${encodeURIComponent(name)}${q}`);
}

async function fetchCharacters() {
  try {
    const resp = await api.fetchApi("/identity_forge/vault/characters");
    const data = await resp.json();
    return Array.isArray(data.characters) ? data.characters : [];
  } catch (e) {
    console.error("[IdentityForge] vault list failed:", e);
    return [];
  }
}

function getCharacterWidget(node) {
  return (node.widgets || []).find((w) => w.name === "character");
}

function setSelection(node, name) {
  const w = getCharacterWidget(node);
  if (!w) return;
  w.value = name;
  if (typeof w.callback === "function") {
    try { w.callback(name, app.canvas, node); } catch (e) { /* ignore */ }
  }
  updatePreview(node);
  node.setDirtyCanvas(true, true);
}

function updatePreview(node) {
  const el = node.__vaultPreviewEl;
  if (!el) return;
  const w = getCharacterWidget(node);
  const name = w && w.value;
  if (!name || name === NO_CHARACTERS) {
    el.style.display = "none";
    el.removeAttribute("src");
    return;
  }
  el.style.display = "";
  el.src = previewURL(name, true);
}

function applyCharacterList(node, characters) {
  const names = characters.map((c) => (typeof c === "string" ? c : c.name));
  const w = getCharacterWidget(node);
  if (!w) return;
  const list = names.length ? names : [NO_CHARACTERS];
  w.options.values = list;
  if (!list.includes(w.value)) w.value = list[0];
  updatePreview(node);
  node.setDirtyCanvas(true, true);
}

async function refresh(node) {
  applyCharacterList(node, await fetchCharacters());
}

// --------------------------------------------------------------------------
// Manager modal
// --------------------------------------------------------------------------
function styleButton(b, accent) {
  Object.assign(b.style, {
    cursor: "pointer", border: "1px solid #555", borderRadius: "4px",
    padding: "4px 8px", fontSize: "12px", color: "#eee",
    background: accent || "#333",
  });
  return b;
}

function openManager(node) {
  const overlay = document.createElement("div");
  Object.assign(overlay.style, {
    position: "fixed", inset: "0", background: "rgba(0,0,0,0.6)",
    zIndex: "10000", display: "flex", alignItems: "center", justifyContent: "center",
  });
  const panel = document.createElement("div");
  Object.assign(panel.style, {
    background: "#222", color: "#eee", width: "min(900px, 92vw)",
    maxHeight: "85vh", borderRadius: "8px", display: "flex", flexDirection: "column",
    boxShadow: "0 10px 40px rgba(0,0,0,0.5)", font: "13px sans-serif",
  });

  const header = document.createElement("div");
  Object.assign(header.style, {
    display: "flex", alignItems: "center", gap: "8px", padding: "12px 16px",
    borderBottom: "1px solid #444",
  });
  const title = document.createElement("div");
  title.textContent = "🗂 Identity Forge — Vault";
  title.style.fontWeight = "bold";
  title.style.flex = "1";
  const bulkDelete = styleButton(document.createElement("button"), "#5a2222");
  bulkDelete.textContent = "🗑 Delete selected";
  const refreshBtn = styleButton(document.createElement("button"));
  refreshBtn.textContent = "🔄 Refresh";
  const closeBtn = styleButton(document.createElement("button"));
  closeBtn.textContent = "✕ Close";
  header.append(title, bulkDelete, refreshBtn, closeBtn);

  const grid = document.createElement("div");
  Object.assign(grid.style, {
    display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
    gap: "12px", padding: "16px", overflowY: "auto",
  });

  panel.append(header, grid);
  overlay.append(panel);
  document.body.append(overlay);

  const close = () => overlay.remove();
  overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });
  closeBtn.onclick = close;

  const selected = new Set();

  async function reload() {
    grid.replaceChildren();
    selected.clear();
    const characters = await fetchCharacters();
    applyCharacterList(node, characters);
    if (!characters.length) {
      const empty = document.createElement("div");
      empty.textContent = "No saved characters yet.";
      empty.style.opacity = "0.7";
      grid.append(empty);
      return;
    }
    for (const c of characters) grid.append(makeCard(c));
  }

  function makeCard(c) {
    const card = document.createElement("div");
    Object.assign(card.style, {
      border: "1px solid #444", borderRadius: "6px", padding: "8px",
      display: "flex", flexDirection: "column", gap: "6px", background: "#2a2a2a",
    });

    const top = document.createElement("label");
    Object.assign(top.style, { display: "flex", alignItems: "center", gap: "6px" });
    const check = document.createElement("input");
    check.type = "checkbox";
    check.onchange = () => check.checked ? selected.add(c.name) : selected.delete(c.name);
    const nm = document.createElement("span");
    nm.textContent = c.name;
    nm.style.fontWeight = "bold";
    nm.style.overflow = "hidden";
    nm.style.textOverflow = "ellipsis";
    nm.style.whiteSpace = "nowrap";
    top.append(check, nm);

    const thumb = document.createElement("div");
    Object.assign(thumb.style, {
      width: "100%", aspectRatio: "1 / 1", background: "#1a1a1a",
      borderRadius: "4px", overflow: "hidden", display: "flex",
      alignItems: "center", justifyContent: "center", fontSize: "11px", opacity: "0.8",
    });
    if (c.has_preview) {
      const img = document.createElement("img");
      img.src = previewURL(c.name, false);
      Object.assign(img.style, { width: "100%", height: "100%", objectFit: "cover" });
      img.onerror = () => { thumb.textContent = "no preview"; };
      thumb.append(img);
    } else {
      thumb.textContent = "no preview";
    }

    const meta = document.createElement("div");
    meta.style.fontSize = "11px";
    meta.style.opacity = "0.75";
    meta.textContent = [c.source_label, (c.created || "").replace("T", " ")]
      .filter(Boolean).join(" · ");

    const actions = document.createElement("div");
    Object.assign(actions.style, { display: "flex", gap: "6px" });
    const useBtn = styleButton(document.createElement("button"), "#234a23");
    useBtn.textContent = "Use";
    useBtn.style.flex = "1";
    useBtn.onclick = () => { setSelection(node, c.name); close(); };
    const renameBtn = styleButton(document.createElement("button"));
    renameBtn.textContent = "✏";
    renameBtn.title = "Rename";
    renameBtn.onclick = () => doRename(c.name);
    const delBtn = styleButton(document.createElement("button"), "#5a2222");
    delBtn.textContent = "🗑";
    delBtn.title = "Delete";
    delBtn.onclick = () => doDelete([c.name]);
    actions.append(useBtn, renameBtn, delBtn);

    card.append(top, thumb, meta, actions);
    return card;
  }

  async function doDelete(names) {
    if (!names.length) { alert("Select at least one character first."); return; }
    if (!confirm(`Delete ${names.length} character(s)? This cannot be undone.`)) return;
    try {
      await api.fetchApi("/identity_forge/vault/delete", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ names }),
      });
    } catch (e) {
      console.error("[IdentityForge] delete failed:", e);
      alert("Delete failed — see console.");
    }
    await reload();
  }

  async function doRename(from) {
    const to = prompt(`Rename "${from}" to:`, from);
    if (!to || to === from) return;
    try {
      const resp = await api.fetchApi("/identity_forge/vault/rename", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from, to }),
      });
      const data = await resp.json();
      if (!resp.ok) { alert(data.error || "Rename failed."); return; }
    } catch (e) {
      console.error("[IdentityForge] rename failed:", e);
      alert("Rename failed — see console.");
    }
    await reload();
  }

  bulkDelete.onclick = () => doDelete([...selected]);
  refreshBtn.onclick = reload;
  reload();
}

// --------------------------------------------------------------------------
// Node wiring
// --------------------------------------------------------------------------
function setupVaultLoad(node) {
  const refreshW = node.addWidget("button", "🔄 Refresh", null, () => refresh(node), { serialize: false });
  const manageW = node.addWidget("button", "🗂 Manage Vault…", null, () => {
    try { openManager(node); } catch (err) { console.error("[IdentityForge] manager failed:", err); }
  }, { serialize: false });

  // Inline preview of the current selection (best-effort DOM widget).
  try {
    const img = document.createElement("img");
    Object.assign(img.style, {
      width: "100%", objectFit: "contain", borderRadius: "4px", display: "none",
    });
    img.onerror = () => { img.style.display = "none"; };
    node.__vaultPreviewEl = img;
    node.addDOMWidget("vault_preview", "img", img, { serialize: false });
  } catch (e) {
    // Older frontend without addDOMWidget — preview simply isn't shown.
  }

  const charW = getCharacterWidget(node);
  if (charW) {
    const prev = charW.callback;
    charW.callback = function (value) {
      const r = typeof prev === "function" ? prev.apply(this, arguments) : undefined;
      updatePreview(node);
      return r;
    };
  }

  // Refresh once on creation so a freshly-loaded graph reflects the live vault.
  refresh(node).catch(() => { /* ignore */ });
}

app.registerExtension({
  name: "identity_forge.vault",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== NODE) return;
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
      try {
        setupVaultLoad(this);
      } catch (err) {
        console.error("[IdentityForge] vault load setup failed:", err);
      }
      return result;
    };
  },
});
