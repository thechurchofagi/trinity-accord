import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.archive_homepage import (
    STATUS_BEGIN,
    STATUS_END,
    archive_homepage,
    capture_arquivo,
    capture_perma,
    find_wayback_capture_since,
    homepage_changed,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "archive-homepage-on-change.yml"


class FakeResponse:
    def __init__(self, *, status=200, body=b"", url="https://example.invalid/"):
        self.status = status
        self._body = body
        self._url = url
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body

    def geturl(self):
        return self._url


class ArchiveHomepageTests(unittest.TestCase):
    def write_homepage(self, directory: str, name: str, status: str, body: str) -> Path:
        path = Path(directory) / name
        path.write_text(
            f"before\n{STATUS_BEGIN}\n{status}\n{STATUS_END}\n{body}\n",
            encoding="utf-8",
        )
        return path

    def test_generated_status_only_change_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = self.write_homepage(directory, "previous.md", "old", "same")
            current = self.write_homepage(directory, "current.md", "new", "same")
            changed, previous_digest, current_digest = homepage_changed(current, previous)
        self.assertFalse(changed)
        self.assertEqual(previous_digest, current_digest)

    def test_substantive_homepage_change_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = self.write_homepage(directory, "previous.md", "old", "before")
            current = self.write_homepage(directory, "current.md", "new", "after")
            changed, previous_digest, current_digest = homepage_changed(current, previous)
        self.assertTrue(changed)
        self.assertNotEqual(previous_digest, current_digest)

    def test_arquivo_submission_is_recorded_without_overclaiming_capture(self):
        response = FakeResponse(
            status=200,
            body=b"request accepted for later integration",
            url="https://arquivo.pt/services/archivepagenow?l=en",
        )
        with mock.patch(
            "scripts.archive_homepage.urllib.request.urlopen", return_value=response
        ):
            result = capture_arquivo("https://www.trinityaccord.org/", 10, 0)
        self.assertEqual(result["status"], "submitted")
        self.assertNotIn("capture_url", result)

    def test_wayback_cdx_confirms_capture_after_save_error(self):
        rows = [
            ["timestamp", "statuscode", "original"],
            ["20260916065313", "200", "https://www.trinityaccord.org/"],
        ]
        with mock.patch(
            "scripts.archive_homepage.urllib.request.urlopen",
            return_value=FakeResponse(body=json.dumps(rows).encode()),
        ):
            result = find_wayback_capture_since(
                "https://www.trinityaccord.org/",
                "2026-09-16T06:53:10+00:00",
                10,
            )
        self.assertEqual(result["capture_timestamp"], "20260916065313")
        self.assertEqual(result["confirmation"], "cdx-after-save-error")

    def test_arquivo_replay_url_is_recorded_as_capture(self):
        body = (
            '<a href="https://arquivo.pt/wayback/20260916120000/'
            'https://www.trinityaccord.org/">saved</a>'
        ).encode()
        with mock.patch(
            "scripts.archive_homepage.urllib.request.urlopen",
            return_value=FakeResponse(status=200, body=body),
        ):
            result = capture_arquivo("https://www.trinityaccord.org/", 10, 0)
        self.assertEqual(result["status"], "captured")
        self.assertTrue(result["capture_url"].startswith("https://arquivo.pt/wayback/"))

    def test_perma_waits_for_primary_capture_success(self):
        created = {
            "guid": "ABCD-1234",
            "captures": [{"role": "primary", "status": "pending"}],
        }
        completed = {
            "guid": "ABCD-1234",
            "warc_download_url": "https://api.perma.cc/example.warc.gz",
            "wacz_download_url": "https://api.perma.cc/example.wacz",
            "captures": [{"role": "primary", "status": "success"}],
        }
        with (
            mock.patch(
                "scripts.archive_homepage.urllib.request.urlopen",
                side_effect=[
                    FakeResponse(body=json.dumps(created).encode()),
                    FakeResponse(body=json.dumps(completed).encode()),
                ],
            ),
            mock.patch("scripts.archive_homepage.time.sleep"),
        ):
            result = capture_perma(
                "https://www.trinityaccord.org/",
                "secret",
                10,
                poll_attempts=1,
                poll_seconds=0,
            )
        self.assertEqual(result["status"], "captured")
        self.assertEqual(result["capture_url"], "https://perma.cc/ABCD-1234")

    def test_dry_run_has_no_external_writes(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            result = archive_homepage(
                "https://www.trinityaccord.org/",
                timeout=10,
                retries=0,
                dry_run=True,
                source_sha="abc",
                trigger="test",
            )
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["services"]["wayback"]["status"], "dry-run")
        self.assertEqual(result["services"]["arquivo_pt"]["status"], "dry-run")
        self.assertEqual(result["services"]["perma_cc"]["status"], "not_configured")

    def test_archive_accepts_cdx_confirmed_wayback_write(self):
        wayback_failure = {
            "url": "https://www.trinityaccord.org/",
            "status": "failed",
            "http_status": 500,
            "error": "HTTP Error 500",
            "started_at": "2026-09-16T06:53:10+00:00",
        }
        confirmed = {
            "capture_timestamp": "20260916065313",
            "capture_url": (
                "https://web.archive.org/web/20260916065313/"
                "https://www.trinityaccord.org/"
            ),
            "confirmation": "cdx-after-save-error",
        }
        with (
            mock.patch(
                "scripts.archive_homepage.capture_wayback",
                return_value=wayback_failure,
            ),
            mock.patch(
                "scripts.archive_homepage.find_wayback_capture_since",
                return_value=confirmed,
            ),
            mock.patch(
                "scripts.archive_homepage.capture_arquivo",
                return_value={"status": "captured"},
            ),
            mock.patch.dict("os.environ", {}, clear=True),
        ):
            result = archive_homepage(
                "https://www.trinityaccord.org/",
                timeout=10,
                retries=0,
                dry_run=False,
                source_sha="abc",
                trigger="test",
            )
        self.assertEqual(result["accepted_service_count"], 2)
        self.assertEqual(
            result["services"]["wayback"]["status"], "captured_after_error"
        )
        self.assertEqual(
            result["services"]["wayback"]["reported_status"], "failed"
        )

    def test_workflow_is_post_deploy_semantic_and_two_archive_gated(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('branches: [main]', workflow)
        self.assertIn('".github/workflows/archive-homepage-on-change.yml"', workflow)
        self.assertIn("reason=workflow-bootstrap-or-change", workflow)
        self.assertIn("github.event_name == 'push'", workflow)
        self.assertIn('workflows: ["Deploy Pages"]', workflow)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)
        self.assertIn("python3 -m scripts.archive_homepage changed", workflow)
        self.assertIn("--required-services 2", workflow)
        self.assertIn("WAYBACK_ACCESS_KEY", workflow)
        self.assertIn("PERMA_API_KEY", workflow)
        self.assertIn("retention-days: 365", workflow)
        self.assertNotIn("sitemap.xml", workflow)


if __name__ == "__main__":
    unittest.main()
