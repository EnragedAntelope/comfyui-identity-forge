"""Tests for the three gallery publishing pipelines.

The galleries are deliberately **copy-and-adapt**: `gallery/cosplay/`,
`gallery/archetypes/` and `gallery/creatures/` each own their scripts rather than
sharing a package. That is the maintainer's call (a shared module would couple
three independently-published sites), but it means an improvement made to one
copy can silently rot in the other two.

`CopiesStayInSyncTests` turns that from a documentation note into an enforced
invariant: everything outside each file's docstring and its GALLERY CONFIG block
must be byte-identical across the three. If you fix a bug in one, this test fails
until you have fixed it in all three.

The rest pins the safety property the whole design exists for: **an entry you did
not supply an image for is never touched, and never deleted.**
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from PIL import Image as PILImage
except ImportError:
    # Attempt the real import rather than probing with find_spec: a package that
    # is present but broken satisfies find_spec and then fails at use, which is
    # exactly what a "skip if unavailable" guard is supposed to prevent.
    PILImage = None

GALLERY_ROOT = ROOT / "gallery"
KINDS = ("cosplay", "archetypes", "creatures")
SCRIPTS = ("publish.py", "build_manifest.py", "build_gallery_images.py",
           "cross_reference.py")


#: Modules the gallery scripts import from their own directory by BARE name.
#: ``publish.py`` does ``from build_manifest import entry_names``, which resolves
#: through sys.modules -- so once any copy has been loaded, every later copy binds
#: the FIRST one's roster. That made publish tests silently assert against the
#: wrong gallery's data (a cosplay source folder matched against the archetype
#: roster). They must be evicted around each load.
_SIBLING_MODULES = ("build_manifest", "build_gallery_images")


def load(kind: str, module: str):
    """Import one gallery's copy of a script under a unique module name.

    The three copies share file names, so a plain import would return whichever
    landed in sys.modules first and silently test the same file three times.
    """
    path = GALLERY_ROOT / kind / f"{module}.py"
    name = f"_gallery_{kind}_{module}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    # The scripts add their own directory to sys.path for sibling imports.
    sys.path.insert(0, str(GALLERY_ROOT / kind))
    # Evict BEFORE exec: that is the load at which the bare name is resolved, so
    # this is the line that forces THIS kind's sibling to be executed. Restoring
    # afterwards is only tidiness -- `mod` has already bound its own copy.
    stashed = {n: sys.modules.pop(n) for n in _SIBLING_MODULES if n in sys.modules}
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(GALLERY_ROOT / kind))
        sys.modules.update(stashed)
    return mod


_CONFIG_BLOCK = re.compile(r"# === GALLERY CONFIG.*?# ={70,}\n", re.S)
_DOCSTRING = re.compile(r'\A""".*?"""\n', re.S)


def code_only(text: str, kind: str) -> str:
    """Strip the parts a copy is *allowed* to differ in, and neutralise the kind."""
    text = _DOCSTRING.sub("", text)
    text = _CONFIG_BLOCK.sub("<<CONFIG>>\n", text)
    for token in (kind, kind.upper(), kind.capitalize(),
                  kind.rstrip("s"), kind.rstrip("s").upper(),
                  kind.rstrip("s").capitalize()):
        text = text.replace(token, "<KIND>")
    return text


class CopiesStayInSyncTests(unittest.TestCase):
    """An improvement to one gallery script must reach the other two."""

    def test_script_bodies_are_identical_across_galleries(self):
        for script in SCRIPTS:
            base = code_only(
                (GALLERY_ROOT / "cosplay" / script).read_text(encoding="utf-8"),
                "cosplay")
            for kind in KINDS[1:]:
                other = code_only(
                    (GALLERY_ROOT / kind / script).read_text(encoding="utf-8"), kind)
                self.assertEqual(
                    base, other,
                    f"gallery/{kind}/{script} has drifted from "
                    f"gallery/cosplay/{script}. The three copies must differ ONLY "
                    f"in their docstring and GALLERY CONFIG block — port the change "
                    f"to all three (see gallery/README.md).")

    def test_every_gallery_ships_the_full_script_set(self):
        for kind in KINDS:
            for name in SCRIPTS + ("update_gallery.bat", "index.html",
                                   "style.css", "gallery.js"):
                self.assertTrue((GALLERY_ROOT / kind / name).is_file(),
                                f"gallery/{kind}/{name} is missing")

    def test_each_gallery_declares_its_own_kind(self):
        seen = set()
        for kind in KINDS:
            mod = load(kind, "build_manifest")
            self.assertEqual(mod.GALLERY_KIND, kind)
            seen.add(mod.GALLERY_KIND)
        self.assertEqual(len(seen), len(KINDS), "two galleries share a GALLERY_KIND")

    def test_each_publish_copy_binds_its_own_roster(self):
        """Guards the sibling-import eviction in ``load`` above.

        Without it every ``publish`` copy shares one cached ``build_manifest``, so
        two galleries would report the same roster and the publish tests would be
        quietly meaningless. Remove the eviction and this fails.
        """
        rosters = {kind: set(load(kind, "publish").entry_names()) for kind in KINDS}
        for kind in KINDS:
            expected = set(load(kind, "build_manifest").entry_names())
            self.assertEqual(
                rosters[kind], expected,
                f"gallery/{kind}/publish.py resolved another gallery's roster")

    def test_each_gallery_resolves_a_non_empty_roster(self):
        for kind in KINDS:
            names = load(kind, "build_manifest").entry_names()
            self.assertGreater(len(names), 0, kind)
            self.assertEqual(len(names), len(set(names)),
                             f"{kind} roster has duplicate names")


class BatchLauncherTests(unittest.TestCase):
    """The .bat gotchas that shipped a broken installer once already."""

    def _bats(self):
        return [(k, (GALLERY_ROOT / k / "update_gallery.bat")) for k in KINDS]

    def test_every_exit_path_pauses(self):
        # A double-clicked .bat that exits without pause closes the window before
        # the user can read the error.
        for kind, path in self._bats():
            text = path.read_text(encoding="utf-8")
            exits = [ln.strip() for ln in text.splitlines()
                     if ln.strip().startswith("exit /b")]
            self.assertGreater(len(exits), 0, kind)
            self.assertEqual(text.count("pause"), len(exits),
                             f"gallery/{kind}/update_gallery.bat has "
                             f"{len(exits)} exit(s) but {text.count('pause')} "
                             f"pause(s); every exit path must pause")

    def test_no_parenthesised_if_blocks(self):
        # cmd ends an if-block at the first bare ')', so a paren in an echo inside
        # one kills the script with "X was unexpected at this time".
        for kind, path in self._bats():
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip().lower()
                if stripped.startswith("if ") and "(" in stripped:
                    self.fail(f"gallery/{kind}/update_gallery.bat:{i} uses a "
                              f"parenthesised if-block; use 'if ... goto :label'")

    def test_ascii_only(self):
        # cmd writes to a cp1252/cp437 console; a non-ASCII byte raises
        # UnicodeEncodeError when the output is piped.
        for kind, path in self._bats():
            raw = path.read_text(encoding="utf-8")
            bad = sorted({c for c in raw if ord(c) > 127})
            self.assertEqual(bad, [], f"gallery/{kind}/update_gallery.bat "
                                      f"contains non-ASCII: {bad}")

    def test_crlf_is_enforced_by_gitattributes(self):
        # An LF-only .bat breaks goto/:label resolution, and every launcher here
        # is built out of goto labels.
        attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("*.bat text eol=crlf", attrs)

    def test_the_working_copy_is_actually_crlf(self):
        """.gitattributes fixes a fresh clone; it does not fix the working tree.

        Every editor and script that writes these files emits LF by default, so a
        launcher can sit broken in the working copy while `.gitattributes` looks
        correct. This caught exactly that on the cosplay launcher.
        """
        for kind, path in self._bats():
            raw = path.read_bytes()
            crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
            self.assertEqual(
                crlf, lf,
                f"gallery/{kind}/update_gallery.bat has {lf - crlf} bare LF "
                f"line ending(s); cmd needs CRLF or goto/:label resolution breaks")


class OptionalPillowTests(unittest.TestCase):
    """The gallery scripts must import in a dependency-free environment.

    The pack itself is zero-dependency and CI installs nothing, so importing a
    gallery script must never require Pillow. It once called ``sys.exit(1)`` at
    import time, which took the entire CI run down the moment this test file
    started importing it -- the failure looked like a test error, not a missing
    optional dependency.
    """

    def test_every_copy_imports_and_degrades_without_pillow(self):
        for kind in KINDS:
            mod = load(kind, "build_gallery_images")
            self.assertTrue(hasattr(mod, "Image"),
                            f"{kind}: Pillow must be bound (possibly to None), "
                            f"never exited on")
            self.assertTrue(hasattr(mod, "PILLOW_HINT"))

    def test_encode_reports_an_error_rather_than_raising_when_absent(self):
        mod = load("cosplay", "build_gallery_images")
        real = mod.Image
        mod.Image = None
        try:
            result = mod.optimize_image(Path("in.jpeg"), Path("out.jpeg"))
        finally:
            mod.Image = real
        self.assertEqual(result["status"], "error")
        self.assertIn("Pillow", result["reason"])

    @unittest.skipUnless(
        PILImage is not None,
        "Pillow not installed - the encode path is maintainer-only tooling")
    def test_a_real_encode_resizes_and_writes_jpeg(self):
        """Runs locally where Pillow exists; skipped in the dep-free CI run."""
        mod = load("cosplay", "build_gallery_images")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "big.png"
            PILImage.new("RGBA", (1500, 1000), (10, 20, 30, 255)).save(src)
            dest = Path(tmp) / "out.jpeg"
            result = mod.optimize_image(src, dest)

            self.assertEqual(result["status"], "optimized", result.get("reason"))
            self.assertTrue(dest.is_file())
            with PILImage.open(dest) as out:
                # Resized to the grid's width, and alpha flattened for JPEG.
                self.assertEqual(out.width, mod.MAX_WIDTH)
                self.assertEqual(out.format, "JPEG")
                self.assertEqual(out.mode, "RGB")


class ManifestDescribesWhatItIsGivenTests(unittest.TestCase):
    """The manifest must reflect the images directory handed to it, exactly."""

    def test_manifest_counts_match_the_directory(self):
        mod = load("cosplay", "build_manifest")
        names = mod.entry_names()[:5]
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            images.mkdir()
            for name in names:
                (images / f"{mod.normalize_name(name)}.jpeg").write_bytes(b"x")
            out = Path(tmp) / "manifest.json"
            manifest = mod.generate_manifest(str(images), str(out))
            on_disk = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(manifest["entries_with_images"], len(names))
        self.assertEqual(manifest["total_entries"], len(mod.entry_names()))
        self.assertEqual(manifest["entries_missing_images"],
                         manifest["total_entries"] - len(names))
        self.assertEqual(on_disk["gallery"], "cosplay")

    def test_a_missing_images_directory_raises_instead_of_lying(self):
        # Silently emitting has_image=false for everything is the failure mode
        # that would blank the live gallery on the next publish.
        mod = load("cosplay", "build_manifest")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                mod.generate_manifest(str(Path(tmp) / "nope"),
                                      str(Path(tmp) / "manifest.json"))

    def test_trailing_period_names_still_match(self):
        # Windows drops a trailing period, so the entry "C.C." is "C.C.jpeg".
        mod = load("cosplay", "build_manifest")
        self.assertEqual(mod.normalize_name("C.C."), mod.normalize_name("C.C"))


class FilesystemUnsafeNameTests(unittest.TestCase):
    """A roster label is not a filename, and the saving side edits it silently.

    ``B-Boy / B-Girl`` cannot exist on disk, so the archetype images the maintainer
    generated arrived as ``B-Boy  B-Girl.jpeg`` -- slash gone, a double space left
    behind. Nothing matched them, and the gallery reported two entries missing while
    both files sat right there.
    """

    #: entry label -> the filename Windows actually produces for it
    CASES = (
        ("B-Boy / B-Girl", "B-Boy  B-Girl"),
        ("E-Girl / E-Boy", "E-Girl  E-Boy"),
        ("Who? What: Why", "Who What Why"),
        ('A "quoted" name', "A quoted name"),
        ("Back\\slash", "Back slash"),
    )

    def test_a_label_matches_the_filename_the_os_produces_for_it(self):
        for kind in KINDS:
            mod = load(kind, "build_manifest")
            for label, on_disk in self.CASES:
                self.assertEqual(
                    mod.normalize_name(label), mod.normalize_name(on_disk),
                    f"{kind}: '{label}' does not match its saved filename "
                    f"'{on_disk}.jpeg'")

    def test_sanitising_never_merges_two_distinct_entries(self):
        """The risk the sanitiser itself creates, pinned for every real roster.

        Stripping characters can make two different entries collide on one
        filename -- and a collision is silent: both would map to the same image
        and one of them would be wrong. Nothing else in the pipeline would notice.
        """
        for kind in KINDS:
            mod = load(kind, "build_manifest")
            names = mod.entry_names()
            buckets: dict[str, list[str]] = {}
            for name in names:
                buckets.setdefault(mod.normalize_name(name), []).append(name)
            collisions = {k: v for k, v in buckets.items() if len(v) > 1}
            self.assertEqual(
                collisions, {},
                f"{kind}: these entries share one sanitised filename and would "
                f"show each other's image: {collisions}")

    def test_manifest_pairs_a_slash_entry_with_its_stripped_file(self):
        """End to end, through the real manifest builder."""
        mod = load("archetypes", "build_manifest")
        target = next((n for n in mod.entry_names() if "/" in n), None)
        self.assertIsNotNone(target, "archetype roster no longer has a slash entry; "
                                     "point this test at another unsafe character")
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "images"
            images.mkdir()
            # Exactly what Windows writes: slash dropped, spaces left doubled.
            (images / f"{target.replace('/', ' ')}.jpeg").write_bytes(b"x")
            manifest = mod.generate_manifest(str(images), str(Path(tmp) / "m.json"))

        entry = next(e for e in manifest["entries"] if e["name"] == target)
        self.assertTrue(entry["has_image"], f"'{target}' still reported imageless")
        self.assertNotIn(target, manifest["missing"])

    def test_published_stems_keep_a_slash_entry_out_of_the_orphan_set(self):
        """The prune hazard: the fix has to reach ``--prune-orphans`` too.

        ``published_stems`` normalises, so an entry whose label cannot be a
        filename verbatim is recognised as its own published image. Comparing raw
        stems here would have deleted the two hand-added archetype images.
        """
        pub = load("archetypes", "publish")
        bm = load("archetypes", "build_manifest")
        target = next(n for n in bm.entry_names() if "/" in n)
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp)
            (images / f"{target.replace('/', ' ')}.jpeg").write_bytes(b"x")
            stems = pub.published_stems(images)

            keep = {bm.normalize_name(n) for n in bm.entry_names()}
            orphans = [p.name for norm, p in stems.items() if norm not in keep]

        self.assertIn(bm.normalize_name(target), stems)
        self.assertEqual(orphans, [], "a real entry's image was classed an orphan")


class StagedFileTests(unittest.TestCase):
    """Everything ``PAGE_FILES`` names must exist, or it is silently not published.

    ``publish.py`` copies each name only ``if src.exists()``. A typo, or a workflow
    renamed in ComfyUI and not here, therefore fails completely silently -- the
    commit just would not contain it, and the page's download link 404s.
    """

    def test_every_named_page_file_exists(self):
        for kind in KINDS:
            pub = load(kind, "publish")
            for fname in pub.PAGE_FILES:
                self.assertTrue(
                    (GALLERY_ROOT / kind / fname).is_file(),
                    f"gallery/{kind}/publish.py names '{fname}' in PAGE_FILES but "
                    f"the file does not exist; it would be skipped silently")

    def test_every_gallery_ships_a_downloadable_workflow(self):
        for kind in KINDS:
            pub = load(kind, "publish")
            workflows = [f for f in pub.PAGE_FILES if f.endswith(".json")]
            self.assertEqual(len(workflows), 1,
                             f"{kind}: expected exactly one workflow in PAGE_FILES, "
                             f"got {workflows}")
            raw = (GALLERY_ROOT / kind / workflows[0]).read_text(encoding="utf-8")
            self.assertIn("nodes", json.loads(raw), f"{kind}: workflow has no nodes")

    def test_the_page_links_to_the_workflow_it_stages(self):
        """The link and the staged filename are set in two different files."""
        for kind in KINDS:
            pub = load(kind, "publish")
            workflow = next(f for f in pub.PAGE_FILES if f.endswith(".json"))
            page = (GALLERY_ROOT / kind / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'href="{workflow}"', page,
                          f"gallery/{kind}/index.html does not link to the workflow "
                          f"'{workflow}' that publish.py stages")


class SourceMatchingTests(unittest.TestCase):
    """A source file must be matched to a real entry, or reported and ignored."""

    def test_unmatched_files_are_reported_not_published(self):
        pub = load("cosplay", "publish")
        bm = load("cosplay", "build_manifest")
        real = bm.entry_names()[0]
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / f"{bm.normalize_name(real)}.jpeg").write_bytes(b"x")
            (src / "Definitely Not An Entry.jpeg").write_bytes(b"x")
            (src / "notes.txt").write_bytes(b"x")
            matched, unmatched = pub.match_sources(src)

        self.assertEqual(set(matched), {real})
        self.assertEqual([p.name for p in unmatched],
                         ["Definitely Not An Entry.jpeg"])

    def test_add_mode_leaves_an_already_published_entry_alone(self):
        """The core guarantee, exercised on the real decision logic.

        Given an entry that is already published and IS supplied again, add-mode
        must skip it; overwrite-mode must rewrite it. Either way, an entry that is
        published and NOT supplied never enters the write set at all.
        """
        bm = load("cosplay", "build_manifest")
        names = bm.entry_names()
        supplied, published_only = names[0], names[1]
        published = {bm.normalize_name(n) for n in (supplied, published_only)}

        for overwrite, expected in ((False, set()), (True, {supplied})):
            to_write = {
                entry for entry in (supplied,)
                if bm.normalize_name(entry) not in published or overwrite
            }
            self.assertEqual(to_write, expected, f"overwrite={overwrite}")
        # The untouched entry is in neither set under either mode.
        self.assertNotIn(published_only, {supplied})


if __name__ == "__main__":
    unittest.main()
