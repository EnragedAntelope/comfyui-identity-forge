/**
 * Entry point for `node --import ./tests/frontend/hooks.mjs --test ...`.
 *
 * Every file under js/ imports ComfyUI's own frontend modules by a fixed
 * relative path -- `import { app } from "../../scripts/app.js"` -- because
 * that is where they genuinely live once ComfyUI serves this pack's
 * WEB_DIRECTORY. Outside a running ComfyUI, that path resolves to nothing,
 * so Node's default resolution would ENOENT on the very first import.
 *
 * `registerHooks` intercepts just those two specifiers, by suffix rather
 * than exact string so it survives js/ files sitting at different relative
 * depths, and redirects them to the stubs in ./stubs/. Every other
 * specifier (local imports, Node built-ins) passes through to nextResolve
 * untouched -- this stubs ComfyUI's frontend API, not the module system, so
 * the real js/*.js files run completely unmodified.
 *
 * `registerHooks` (not the older `module.register`) because it runs
 * synchronously in this same thread rather than a separate loader worker,
 * and `module.register` is deprecated as of this repo's Node version.
 */

import { registerHooks } from "node:module";

const STUB_DIR = new URL("./stubs/", import.meta.url);

registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier.endsWith("/scripts/app.js")) {
      return { url: new URL("app.js", STUB_DIR).href, shortCircuit: true };
    }
    if (specifier.endsWith("/scripts/api.js")) {
      return { url: new URL("api.js", STUB_DIR).href, shortCircuit: true };
    }
    return nextResolve(specifier, context);
  },
});
