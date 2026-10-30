"""Server-side cache of the gh-pages gallery, for the roster picker's preview images (2.3.0).

The picker used to fetch the manifest and every thumbnail straight from GitHub Pages in
the browser. ComfyUI's ``--offline`` flag sends a Content-Security-Policy of
``img-src 'self'; connect-src 'self'``, which blocks exactly that, so previews never
loaded there. Routing them through the pack's own routes puts them on ComfyUI's origin,
and the server keeps what it fetched:

* **Lazy.** An image is downloaded the first time a card scrolls into view, never in
  bulk; the cache holds what this install has looked at (about 100 KiB an image).
* **Revalidated, not trusted forever.** Re-renders keep their filename, so a cached
  file is checked again with its ETag after :data:`MANIFEST_MAX_AGE` (manifest) or
  :data:`IMAGE_MAX_AGE` (image); an unchanged file costs one 304.
* **Offline-tolerant.** Any network failure serves the cached copy if there is one.

Only one host is ever contacted, and an image path is served only if the current
manifest lists it, so a request cannot name an arbitrary URL or escape the cache
directory. Nothing here runs until the user enables previews in the picker.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

GALLERY_ROOT = "https://enragedantelope.github.io/comfyui-identity-forge/gallery/"
#: Gallery folders on gh-pages (js KIND_GALLERY_FOLDER's values).
KINDS: "frozenset[str]" = frozenset({"cosplay", "archetypes", "creatures"})

#: GitHub Pages serves both with ``max-age=600``; an image is re-checked weekly.
MANIFEST_MAX_AGE = 600
IMAGE_MAX_AGE = 7 * 24 * 3600
#: Gallery images are optimized JPEGs of ~100 KiB; refuse anything absurd.
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
TIMEOUT = 15

_ETAG = ".etag"


class GalleryError(Exception):
    """A request that cannot be served: unknown kind/path, or nothing cached offline."""


def default_root() -> Path:
    import folder_paths  # type: ignore[import-not-found]

    return Path(folder_paths.get_user_directory()) / "identity_forge" / "gallery_cache"


def _urlopen(request: urllib.request.Request):  # pragma: no cover - patched in tests
    return urllib.request.urlopen(request, timeout=TIMEOUT)


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _fetch(url: str, path: Path, max_age: float, limit: int,
           check: "Callable[[bytes, str], bool]", opener=None) -> Path:
    """``path``, refreshed from ``url`` when older than ``max_age`` seconds.

    A failed or rejected download keeps the cached copy; with none, GalleryError.
    """
    opener = opener or _urlopen
    etag_path = path.with_name(path.name + _ETAG)
    if path.is_file() and time.time() - path.stat().st_mtime < max_age:
        return path
    request = urllib.request.Request(url, headers={"User-Agent": "comfyui-identity-forge"})
    if path.is_file() and etag_path.is_file():
        request.add_header("If-None-Match", etag_path.read_text(encoding="utf-8").strip())
    try:
        with opener(request) as response:
            data = response.read(limit + 1)
            content_type = response.headers.get("Content-Type", "")
            etag = response.headers.get("ETag", "")
        if len(data) > limit or not check(data, content_type):
            raise GalleryError(f"rejected response from {url}")
        _write_atomic(path, data)
        if etag:
            _write_atomic(etag_path, etag.encode("utf-8"))
        return path
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and path.is_file():
            os.utime(path)  # validated: fresh for another max_age
            return path
        failure: Exception = exc
    except (OSError, GalleryError, ValueError) as exc:  # URLError is an OSError
        failure = exc
    if path.is_file():
        return path  # offline or failing: what we had before
    raise GalleryError(f"{url} unavailable and not cached: {failure}")


def _is_manifest(data: bytes, _content_type: str) -> bool:
    try:
        return isinstance(json.loads(data.decode("utf-8")).get("entries"), list)
    except (ValueError, AttributeError, UnicodeDecodeError):
        return False


def _is_image(data: bytes, content_type: str) -> bool:
    return content_type.startswith("image/") and bool(data)


def _check_kind(kind: str) -> None:
    if kind not in KINDS:
        raise GalleryError(f"unknown gallery {kind!r}")


def manifest_path(kind: str, root: Path, opener=None) -> Path:
    _check_kind(kind)
    return _fetch(GALLERY_ROOT + kind + "/manifest.json", root / kind / "manifest.json",
                  MANIFEST_MAX_AGE, MAX_MANIFEST_BYTES, _is_manifest, opener)


#: kind -> (manifest mtime, image paths it lists); the manifest is ~400 KiB of JSON,
#: too much to re-parse for every thumbnail request.
_LISTED: "dict[tuple[Path, str], tuple[float, frozenset[str]]]" = {}


def _listed_images(kind: str, root: Path, opener=None) -> "frozenset[str]":
    path = manifest_path(kind, root, opener)
    mtime = path.stat().st_mtime
    cached = _LISTED.get((root, kind))
    if cached and cached[0] == mtime:
        return cached[1]
    entries = json.loads(path.read_text(encoding="utf-8")).get("entries") or []
    images = frozenset(e["image"] for e in entries
                       if isinstance(e, dict) and isinstance(e.get("image"), str))
    _LISTED[(root, kind)] = (mtime, images)
    return images


def image_path(kind: str, relative: str, root: Path, opener=None) -> Path:
    """The cached file for one manifest-listed image, downloading it if needed."""
    _check_kind(kind)
    if relative not in _listed_images(kind, root, opener):
        raise GalleryError(f"{relative!r} is not in the {kind} manifest")
    target = (root / kind / relative).resolve()
    if not target.is_relative_to((root / kind).resolve()):  # defence in depth
        raise GalleryError(f"{relative!r} escapes the cache")
    url = GALLERY_ROOT + kind + "/" + urllib.parse.quote(relative)
    return _fetch(url, target, IMAGE_MAX_AGE, MAX_IMAGE_BYTES, _is_image, opener)


def cache_bytes(root: Path) -> int:
    if not root.is_dir():
        return 0
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def clear(root: Path) -> None:
    _LISTED.clear()
    if root.is_dir():
        shutil.rmtree(root)
