import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.archive_public_web import CORE_PATHS, load_sitemap, select_urls


class ArchivePublicWebTests(unittest.TestCase):
    def write_sitemap(self, urls):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "sitemap.xml"
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"<url><loc>{url}</loc></url>\n" for url in urls)
            + "</urlset>\n"
        )
        path.write_text(body, encoding="utf-8")
        return path, body.encode()

    def test_loads_deduplicated_canonical_urls_and_digest(self):
        urls = [
            "https://www.trinityaccord.org/",
            "https://www.trinityaccord.org/api/authority.json",
            "https://www.trinityaccord.org/",
        ]
        path, raw = self.write_sitemap(urls)
        loaded, digest = load_sitemap(path)
        self.assertEqual(loaded, urls[:2])
        self.assertEqual(digest, hashlib.sha256(raw).hexdigest())

    def test_rejects_noncanonical_origin(self):
        path, _ = self.write_sitemap(["https://example.com/"])
        with self.assertRaisesRegex(ValueError, "non-canonical"):
            load_sitemap(path)

    def test_scope_selection(self):
        urls = [
            "https://www.trinityaccord.org/",
            "https://www.trinityaccord.org/agent-brief/",
            "https://www.trinityaccord.org/api/authority.json",
            "https://www.trinityaccord.org/version.json",
            "https://www.trinityaccord.org/llms.txt",
        ]
        self.assertEqual(select_urls(urls, "all", 0), urls)
        self.assertEqual(
            select_urls(urls, "pages", 0),
            urls[:2],
        )
        core = select_urls(urls, "core", 0)
        self.assertIn("https://www.trinityaccord.org/", core)
        self.assertIn("https://www.trinityaccord.org/api/authority.json", core)
        self.assertIn("https://www.trinityaccord.org/llms.txt", core)
        self.assertNotIn("https://www.trinityaccord.org/version.json", core)

    def test_maximum_is_applied_after_scope(self):
        urls = [
            "https://www.trinityaccord.org/",
            "https://www.trinityaccord.org/agent-brief/",
            "https://www.trinityaccord.org/authority/",
        ]
        self.assertEqual(select_urls(urls, "pages", 2), urls[:2])

    def test_core_paths_are_absolute_and_unique(self):
        self.assertTrue(CORE_PATHS)
        self.assertTrue(all(path.startswith("/") for path in CORE_PATHS))


if __name__ == "__main__":
    unittest.main()
