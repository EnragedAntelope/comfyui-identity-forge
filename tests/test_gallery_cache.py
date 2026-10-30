"""Tests for the server-side gallery cache behind the picker's previews (2.3.0)."""
from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
import urllib.error
from email.message import Message
from pathlib import Path

from nodes import gallery_cache as gc

_MANIFEST = json.dumps({"entries": [
    {"name": "AKI", "image": "images/AKI.jpeg"},
    {"name": "2-1B Droid", "image": "images/2-1B Droid.jpeg"},
    {"name": "No image", "has_image": False},
]}).encode("utf-8")


class _Response:
    def __init__(self, body: bytes, content_type: str, etag: str = '"v1"') -> None:
        self._body = body
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        self.headers["ETag"] = etag

    def read(self, limit: int = -1) -> bytes:
        return self._body if limit < 0 else self._body[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class _Opener:
    """Answers like GitHub Pages; ``offline`` makes every call fail."""

    def __init__(self) -> None:
        self.calls: "list[tuple[str, str | None]]" = []
        self.offline = False
        self.not_modified = False
        self.image_type = "image/jpeg"
        self.image_body = b"\xff\xd8jpeg"

    def __call__(self, request):
        url = request.full_url
        self.calls.append((url, request.get_header("If-none-match")))
        if self.offline:
            raise urllib.error.URLError("no network")
        if self.not_modified and request.get_header("If-none-match"):
            raise urllib.error.HTTPError(url, 304, "Not Modified", Message(), None)
        if url.endswith("manifest.json"):
            return _Response(_MANIFEST, "application/json")
        return _Response(self.image_body, self.image_type)


class GalleryCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.root = Path(self._dir.name) / "cache"
        self.opener = _Opener()
        gc._LISTED.clear()

    def tearDown(self) -> None:
        gc._LISTED.clear()
        self._dir.cleanup()

    def _age(self, path: Path, seconds: float) -> None:
        then = time.time() - seconds
        os.utime(path, (then, then))

    def test_fetches_once_then_serves_from_disk(self):
        path = gc.manifest_path("cosplay", self.root, self.opener)
        self.assertEqual(path.read_bytes(), _MANIFEST)
        self.assertEqual(self.opener.calls[0][0], gc.GALLERY_ROOT + "cosplay/manifest.json")
        gc.manifest_path("cosplay", self.root, self.opener)
        self.assertEqual(len(self.opener.calls), 1, "a fresh copy must not refetch")

    def test_stale_copy_revalidates_with_its_etag(self):
        path = gc.manifest_path("cosplay", self.root, self.opener)
        self._age(path, gc.MANIFEST_MAX_AGE + 5)
        self.opener.not_modified = True
        gc.manifest_path("cosplay", self.root, self.opener)
        self.assertEqual(self.opener.calls[-1][1], '"v1"')
        self.assertLess(time.time() - path.stat().st_mtime, 60, "a 304 renews freshness")

    def test_offline_serves_what_was_cached(self):
        image = gc.image_path("cosplay", "images/AKI.jpeg", self.root, self.opener)
        self._age(image, gc.IMAGE_MAX_AGE + 5)
        self._age(self.root / "cosplay" / "manifest.json", gc.MANIFEST_MAX_AGE + 5)
        self.opener.offline = True
        self.assertEqual(
            gc.image_path("cosplay", "images/AKI.jpeg", self.root, self.opener), image)

    def test_offline_with_nothing_cached_is_an_error(self):
        self.opener.offline = True
        with self.assertRaises(gc.GalleryError):
            gc.manifest_path("cosplay", self.root, self.opener)

    def test_only_listed_images_on_the_one_host(self):
        path = gc.image_path("cosplay", "images/2-1B Droid.jpeg", self.root, self.opener)
        self.assertEqual(path.name, "2-1B Droid.jpeg")
        self.assertEqual(self.opener.calls[-1][0],
                         gc.GALLERY_ROOT + "cosplay/images/2-1B%20Droid.jpeg")
        for bad in ("images/Unknown.jpeg", "images/../../../secret.txt", "manifest.json"):
            with self.subTest(bad=bad), self.assertRaises(gc.GalleryError):
                gc.image_path("cosplay", bad, self.root, self.opener)
        with self.assertRaises(gc.GalleryError):
            gc.manifest_path("../etc", self.root, self.opener)

    def test_rejected_responses_are_not_cached(self):
        self.opener.image_type = "text/html"
        with self.assertRaises(gc.GalleryError):
            gc.image_path("cosplay", "images/AKI.jpeg", self.root, self.opener)
        self.assertFalse((self.root / "cosplay" / "images" / "AKI.jpeg").exists())
        self.opener.image_type = "image/jpeg"
        self.opener.image_body = b"x" * (gc.MAX_IMAGE_BYTES + 1)
        with self.assertRaises(gc.GalleryError):
            gc.image_path("cosplay", "images/AKI.jpeg", self.root, self.opener)

    def test_size_and_clear(self):
        self.assertEqual(gc.cache_bytes(self.root), 0)
        gc.image_path("cosplay", "images/AKI.jpeg", self.root, self.opener)
        self.assertGreater(gc.cache_bytes(self.root), len(_MANIFEST))
        gc.clear(self.root)
        self.assertEqual(gc.cache_bytes(self.root), 0)


if __name__ == "__main__":
    unittest.main()
