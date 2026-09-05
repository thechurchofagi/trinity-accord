import http.client
import io
import pathlib
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest import mock

from scripts.base_blob_archive_proxy import Archive


class FakeResponse:
    def __init__(self, body: bytes = b"ok"):
        self._body = body
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return self._body


class ArchiveRequestTests(unittest.TestCase):
    def archive(self, root: str) -> Archive:
        return Archive(pathlib.Path(root), "https://archive.invalid", timeout=1)

    def test_retries_timeout_then_succeeds(self):
        with tempfile.TemporaryDirectory() as root:
            archive = self.archive(root)
            urlopen = mock.Mock(side_effect=[TimeoutError("timed out"), FakeResponse(b"payload")])
            with mock.patch.object(urllib.request, "urlopen", urlopen), mock.patch(
                "scripts.base_blob_archive_proxy.time.sleep", return_value=None
            ):
                data, headers = archive.request("https://archive.invalid/blob")

        self.assertEqual(data, b"payload")
        self.assertEqual(headers, {})
        self.assertEqual(urlopen.call_count, 2)

    def test_retries_remote_disconnect_then_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            archive = self.archive(root)
            urlopen = mock.Mock(side_effect=http.client.RemoteDisconnected("closed"))
            with mock.patch.object(urllib.request, "urlopen", urlopen), mock.patch(
                "scripts.base_blob_archive_proxy.time.sleep", return_value=None
            ):
                with self.assertRaises(http.client.RemoteDisconnected):
                    archive.request("https://archive.invalid/blob")

        self.assertEqual(urlopen.call_count, 5)

    def test_nonretryable_http_status_fails_immediately(self):
        with tempfile.TemporaryDirectory() as root:
            archive = self.archive(root)
            error = urllib.error.HTTPError(
                "https://archive.invalid/blob", 404, "not found", {}, io.BytesIO()
            )
            urlopen = mock.Mock(side_effect=error)
            with mock.patch.object(urllib.request, "urlopen", urlopen), mock.patch(
                "scripts.base_blob_archive_proxy.time.sleep", return_value=None
            ):
                with self.assertRaises(urllib.error.HTTPError):
                    archive.request("https://archive.invalid/blob")

        self.assertEqual(urlopen.call_count, 1)


if __name__ == "__main__":
    unittest.main()
