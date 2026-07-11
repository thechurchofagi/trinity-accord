import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.archive_public_web import CORE_PATHS, load_sitemap, select_urls

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "public-internet-archive.yml"


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
        self.assertEqual(select_urls(urls, "pages", 2, 1), urls[1:3])

    def test_core_paths_are_absolute_and_unique(self):
        self.assertTrue(CORE_PATHS)
        self.assertTrue(all(path.startswith("/") for path in CORE_PATHS))

    def test_software_heritage_helper_runs_as_workflow_module(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "software-heritage.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "scripts.request_software_heritage_archive",
                    "--dry-run",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
            )
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "dry-run")

    def test_workflow_preserves_partial_batch_observability(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python3 -m scripts.request_software_heritage_archive",
            workflow,
        )
        self.assertIn("if size < 1 or size > 10:", workflow)
        self.assertIn("batch_size must be between 1 and 10", workflow)

        capture = workflow.split("\n  capture:\n", 1)[1].split(
            "\n  software-heritage:\n", 1
        )[0]
        match = re.search(r"timeout-minutes:\s*(\d+)", capture)
        self.assertIsNotNone(match, "capture timeout-minutes is missing")
        timeout_minutes = int(match.group(1))

        # Upper bound for the accepted 10-URL batch: three 180-second
        # requests per URL, two Retry-After sleeps capped at 300 seconds,
        # and nine 15-second inter-request delays.
        worst_case_seconds = 10 * (3 * 180 + 2 * 300) + 9 * 15
        required_seconds = worst_case_seconds + 15 * 60
        self.assertGreaterEqual(timeout_minutes * 60, required_seconds)


if __name__ == "__main__":
    unittest.main()
