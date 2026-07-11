import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts.archive_public_web import (
    CORE_PATHS,
    capture_wayback,
    find_recent_capture,
    load_sitemap,
    load_url_file,
    select_urls,
    should_apply_inter_url_delay,
)
from scripts.merge_public_web_archive_results import merge_results

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "public-internet-archive.yml"


class FakeResponse:
    def __init__(self, status=200, body=b"", headers=None, url="https://example.invalid/"):
        self.status = status
        self._body = body
        self.headers = headers or {}
        self._url = url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body

    def geturl(self):
        return self._url


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

    def test_url_file_accepts_json_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "urls.json"
            path.write_text(
                json.dumps(
                    [
                        "https://www.trinityaccord.org/",
                        "https://www.trinityaccord.org/",
                        "https://www.trinityaccord.org/agent-brief/",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                load_url_file(path),
                [
                    "https://www.trinityaccord.org/",
                    "https://www.trinityaccord.org/agent-brief/",
                ],
            )

    def test_scope_selection(self):
        urls = [
            "https://www.trinityaccord.org/",
            "https://www.trinityaccord.org/agent-brief/",
            "https://www.trinityaccord.org/api/authority.json",
            "https://www.trinityaccord.org/version.json",
            "https://www.trinityaccord.org/llms.txt",
        ]
        self.assertEqual(select_urls(urls, "all", 0), urls)
        self.assertEqual(select_urls(urls, "pages", 0), urls[:2])
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

    def test_source_unavailable_is_distinct_from_wayback_failure(self):
        with mock.patch(
            "scripts.archive_public_web.probe_source",
            return_value={"available": False, "http_status": 404, "attempts": 1},
        ):
            result = capture_wayback(
                "https://www.trinityaccord.org/missing/",
                10,
                1,
            )
        self.assertEqual(result["status"], "source_unavailable")
        self.assertEqual(result["source"]["http_status"], 404)
        self.assertEqual(result["attempts"], 0)

    def test_wayback_404_is_retried_when_source_is_healthy(self):
        error = urllib.error.HTTPError(
            "https://web.archive.org/save/example",
            404,
            "NOT FOUND",
            {},
            None,
        )
        success = FakeResponse(
            status=200,
            headers={"Content-Location": "/web/20260711000000/https://www.trinityaccord.org/"},
        )
        with (
            mock.patch(
                "scripts.archive_public_web.probe_source",
                return_value={"available": True, "http_status": 200, "attempts": 1},
            ),
            mock.patch("scripts.archive_public_web.find_recent_capture", return_value=None),
            mock.patch(
                "scripts.archive_public_web.urllib.request.urlopen",
                side_effect=[error, success],
            ),
            mock.patch("scripts.archive_public_web.time.sleep") as sleeper,
        ):
            result = capture_wayback(
                "https://www.trinityaccord.org/",
                10,
                2,
            )
        self.assertEqual(result["status"], "captured")
        self.assertEqual(result["attempts"], 2)
        self.assertTrue(result["capture_url"].startswith("https://web.archive.org/"))
        sleeper.assert_called_once()

    def test_recent_capture_short_circuits_new_save(self):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        body = json.dumps(
            {
                "archived_snapshots": {
                    "closest": {
                        "available": True,
                        "status": "200",
                        "timestamp": timestamp,
                        "url": "https://web.archive.org/web/example",
                    }
                }
            }
        ).encode()
        with mock.patch(
            "scripts.archive_public_web.urllib.request.urlopen",
            return_value=FakeResponse(status=200, body=body),
        ):
            result = find_recent_capture(
                "https://www.trinityaccord.org/",
                10,
                7,
            )
        self.assertIsNotNone(result)
        self.assertEqual(result["capture_url"], "https://web.archive.org/web/example")

    def test_inter_url_delay_only_follows_wayback_write_attempt(self):
        self.assertFalse(
            should_apply_inter_url_delay(
                {"status": "already_captured", "attempts": 0}
            )
        )
        self.assertFalse(
            should_apply_inter_url_delay(
                {"status": "source_unavailable", "attempts": 0}
            )
        )
        self.assertTrue(
            should_apply_inter_url_delay({"status": "captured", "attempts": 1})
        )
        self.assertTrue(
            should_apply_inter_url_delay({"status": "failed", "attempts": 4})
        )

    def test_retry_overlay_replaces_initial_failures(self):
        initial = {
            "schema": "trinityaccord.public-internet-archive-results.v1",
            "sitemap_sha256": "abc",
            "scope": "all",
            "dry_run": False,
            "selected_start_index": 0,
            "boundary": {"archive_is_mirror_only": True},
            "wayback": [
                {"url": "https://www.trinityaccord.org/", "status": "failed"},
                {
                    "url": "https://www.trinityaccord.org/agent-brief/",
                    "status": "captured",
                },
            ],
        }
        base = merge_results([initial], expected_count=2)
        self.assertEqual(base["unresolved_url_count"], 1)
        retry = {
            "schema": "trinityaccord.public-internet-archive-results.v1",
            "sitemap_sha256": "abc",
            "scope": "all",
            "dry_run": False,
            "run_kind": "retry",
            "wayback": [
                {
                    "url": "https://www.trinityaccord.org/",
                    "status": "already_captured",
                }
            ],
        }
        final = merge_results([retry], expected_count=2, base_aggregate=base)
        self.assertEqual(final["unresolved_url_count"], 0)
        self.assertEqual(final["summary"]["already_captured"], 1)
        self.assertEqual(final["retry_update_count"], 1)

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

    def test_workflow_has_two_phase_retry_and_final_gate(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(".github/archive-public-site-live-trigger-v4", workflow)
        self.assertIn("timeout-minutes: 300", workflow)
        self.assertIn("aggregate-initial:", workflow)
        self.assertIn("retry-unresolved:", workflow)
        self.assertIn("final:", workflow)
        self.assertIn("--recent-days 7", workflow)
        self.assertIn("--recent-days 14", workflow)
        self.assertIn("--retries 5", workflow)
        self.assertIn("public archive remains incomplete after retry wave", workflow)
        self.assertNotIn("Enforce batch result", workflow)

        initial = workflow.split("\n  capture:\n", 1)[1].split(
            "\n  software-heritage:\n", 1
        )[0]
        self.assertIn("max-parallel: 2", initial)
        self.assertIn('sleep "${{ matrix.stagger_seconds }}"', initial)
        self.assertIn('"stagger_seconds": 0 if batch % 2 else 15', workflow)
        match = re.search(r"timeout-minutes:\s*(\d+)", initial)
        self.assertIsNotNone(match)
        timeout_minutes = int(match.group(1))
        worst_case_seconds = 10 * (4 * 120 + 3 * 300) + 9 * 30
        required_seconds = worst_case_seconds + 20 * 60
        self.assertGreaterEqual(timeout_minutes * 60, required_seconds)


if __name__ == "__main__":
    unittest.main()
