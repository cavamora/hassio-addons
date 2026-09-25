#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "rootfs/usr/local/lib/hermes-storage-publisher.py"
spec = importlib.util.spec_from_file_location("publisher", MODULE_PATH)
assert spec is not None
assert spec.loader is not None
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.share = root / "share"
        self.media = root / "media"
        self.share.mkdir()
        self.media.mkdir()
        setattr(publisher, "SHARE_ROOT", self.share)
        setattr(publisher, "MEDIA_ROOT", self.media)

    def tearDown(self):
        self.temp.cleanup()

    def request(self, operation, path, **extra):
        return publisher.handle_request({"id": "a" * 32, "operation": operation, "path": path, **extra})

    def test_move_preserves_relative_path_and_removes_source(self):
        source = self.share / "MEDIA/Audiolivros/test.m4b"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"audio")
        result = self.request("move", "MEDIA/Audiolivros/test.m4b")
        self.assertEqual(result["bytes"], 5)
        self.assertFalse(source.exists())
        self.assertEqual((self.media / "MEDIA/Audiolivros/test.m4b").read_bytes(), b"audio")

    def test_move_requires_explicit_replace(self):
        source = self.share / "MEDIA/a.m4b"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"new")
        destination = self.media / "MEDIA/a.m4b"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"old")
        with self.assertRaisesRegex(publisher.StorageError, "--replace"):
            self.request("move", "MEDIA/a.m4b")
        self.request("move", "MEDIA/a.m4b", replace=True)
        self.assertEqual(destination.read_bytes(), b"new")

    def test_rejects_traversal_and_symlink_source(self):
        with self.assertRaises(publisher.StorageError):
            self.request("move", "../secret")
        target = self.share / "target"
        target.write_text("secret")
        link = self.share / "MEDIA/link"
        link.parent.mkdir()
        link.symlink_to(target)
        with self.assertRaises(publisher.StorageError):
            self.request("move", "MEDIA/link")

    def test_remove_directory_requires_recursive(self):
        target = self.media / "MEDIA/old/file.txt"
        target.parent.mkdir(parents=True)
        target.write_text("x")
        with self.assertRaisesRegex(publisher.StorageError, "--recursive"):
            self.request("remove", "MEDIA/old")
        self.request("remove", "MEDIA/old", recursive=True)
        self.assertFalse((self.media / "MEDIA/old").exists())


if __name__ == "__main__":
    unittest.main()
