/**
 * Stand-in for ComfyUI's `scripts/api.js`. The vault frontend (js/identity_forge_vault.js)
 * is the only consumer -- `apiURL` for building preview <img> src attributes and
 * `fetchApi` for the vault's list/delete/rename routes. A test points
 * `__setFetchApiHandler` at a function returning whatever response shape
 * that call needs; every call is also recorded for assertions (e.g. the
 * delete route's `Content-Type: application/json` header).
 */

function defaultHandler() {
  return { ok: true, json: async () => ({ characters: [] }) };
}

let _handler = defaultHandler;
const _calls = [];

export const api = {
  apiURL(route) {
    return route;
  },
  async fetchApi(route, opts) {
    _calls.push({ route, opts });
    return _handler(route, opts);
  },
};

export function __setFetchApiHandler(handler) {
  _handler = handler;
}

export function __getFetchApiCalls() {
  return _calls;
}

export function __resetApi() {
  _handler = defaultHandler;
  _calls.length = 0;
}
