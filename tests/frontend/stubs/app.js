/**
 * Stand-in for ComfyUI's `scripts/app.js`, resolved in place of the real
 * module by `hooks.mjs`. Records every `app.registerExtension({...})` call
 * so a test can retrieve the registered extension object and drive its
 * lifecycle hooks (`beforeRegisterNodeDef`, `nodeCreated`) by hand.
 */

export const __extensions = [];

export const app = {
  canvas: {
    setDirty() {},
  },
  graph: null,
  registerExtension(ext) {
    __extensions.push(ext);
  },
};

export function __getExtension(name) {
  return __extensions.find((e) => e.name === name);
}

export function __resetApp() {
  __extensions.length = 0;
  app.graph = null;
}
