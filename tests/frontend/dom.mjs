/**
 * Minimal jsdom bootstrap shared by every frontend test.
 *
 * Honest limits (also documented in docs/architecture.md and the worklog):
 * jsdom has no layout engine, so `clientWidth`/`clientHeight` read 0 and
 * anything that depends on real layout (CSS, drag/drop, DOM-widget pixel
 * positions) cannot be exercised here. This catches wiring, visibility,
 * serialization and dialog logic -- the class of bug that has actually
 * shipped -- not painting. It does not replace opening the page in a real
 * browser before a release.
 */

import { JSDOM } from "jsdom";

let dom = null;

// jsdom doesn't implement these (calling them logs a "Not implemented"
// error and returns undefined); the vault manager dialog calls all three as
// bare globals (window.confirm(...) / alert(...) / prompt(...)), so a test
// exercising delete/rename needs deterministic defaults it can override.
function defaultDialogStubs() {
  globalThis.alert = () => {};
  globalThis.confirm = () => true;
  globalThis.prompt = (_message, defaultValue) => defaultValue;
}

export function installDom() {
  dom = new JSDOM("<!doctype html><html><body></body></html>", {
    url: "http://localhost/",
  });
  const { window } = dom;
  globalThis.window = window;
  globalThis.document = window.document;
  globalThis.HTMLElement = window.HTMLElement;
  globalThis.Node = window.Node;
  globalThis.CustomEvent = window.CustomEvent;
  globalThis.DocumentFragment = window.DocumentFragment;
  // Node itself defines a read-only `navigator` getter (since Node 21), so
  // a plain assignment throws. Redefine the property instead.
  Object.defineProperty(globalThis, "navigator", {
    value: window.navigator,
    configurable: true,
    writable: true,
  });
  globalThis.requestAnimationFrame = (callback) => setTimeout(callback, 0);
  defaultDialogStubs();
  return dom;
}

export function resetDom() {
  if (document?.body) document.body.replaceChildren();
  if (document?.head) {
    for (const link of Array.from(document.head.querySelectorAll("link"))) {
      link.remove();
    }
  }
  defaultDialogStubs();
}
