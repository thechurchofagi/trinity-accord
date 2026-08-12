#!/usr/bin/env python3
"""Offline tests for the bounded Zenodo standalone-PDF correction."""
from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import repair_research_preprint_zenodo_files as repairer


class FakeClient:
    def __init__(self, pdf: bytes, *, pdf_state: str = "missing") -> None:
        self.api_base = "https://zenodo.example/api"
        self.pdf = pdf
        self.calls: list[tuple[str, str]] = []
        self.bucket_unlocked = False
        self.record = {
            "id": repairer.RECORD_ID,
            "record_id": repairer.RECORD_ID,
            "doi": repairer.DOI,
            "created": "2026-07-30T08:08:17+00:00",
            "state": "done",
            "submitted": True,
            "metadata": {
                "title": repairer.TITLE,
                "version": repairer.VERSION,
                "doi": repairer.DOI,
            },
            "links": {
                "bucket": "https://zenodo.example/api/files/bucket",
                "file_modification": (
                    "https://zenodo.example/api/records/"
                    f"{repairer.RECORD_ID}/file-modification"
                ),
            },
            "files": [
                {
                    "filename": repairer.ARCHIVE_NAME,
                    "filesize": repairer.ARCHIVE_BYTES,
                    "checksum": f"md5:{repairer.ARCHIVE_MD5}",
                    "links": {"download": "https://zenodo.example/archive"},
                }
            ],
        }
        if pdf_state == "prior":
            self._add_prior_pdf()
        elif pdf_state == "corrected":
            self._add_corrected_pdf()
        elif pdf_state != "missing":
            raise ValueError(f"unsupported fake PDF state: {pdf_state}")

    @staticmethod
    def _pdf_links() -> dict[str, str]:
        return {
            "self": "https://zenodo.example/api/files/bucket/" + repairer.PDF_NAME,
            "download": "https://zenodo.example/pdf",
        }

    def _add_prior_pdf(self) -> None:
        self.record["files"].append(
            {
                "filename": repairer.PDF_NAME,
                "filesize": repairer.PRIOR_PDF_BYTES,
                "checksum": "md5:" + repairer.PRIOR_PDF_MD5,
                "links": self._pdf_links(),
            }
        )

    def _add_corrected_pdf(self) -> None:
        if any(repairer.file_name(item) == repairer.PDF_NAME for item in self.record["files"]):
            return
        self.record["files"].append(
            {
                "filename": repairer.PDF_NAME,
                "filesize": len(self.pdf),
                "checksum": "md5:" + hashlib.md5(self.pdf).hexdigest(),  # nosec B324
                "links": self._pdf_links(),
            }
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: Any | None = None,
        data: bytes | None = None,
        content_type: str = "application/json",
    ) -> Any:
        self.calls.append((method, url))
        if method == "GET" and url in {
            f"/deposit/depositions/{repairer.RECORD_ID}",
            f"/records/{repairer.RECORD_ID}",
        }:
            return copy.deepcopy(self.record)
        if method == "POST" and url.endswith("/actions/edit"):
            self.record["state"] = "inprogress"
            return copy.deepcopy(self.record)
        if method == "POST" and url.endswith("/file-modification"):
            if data is not None or not isinstance(payload, dict):
                raise AssertionError("file-modification action requires JSON")
            if payload.get("comment") != repairer.FILE_MODIFICATION_COMMENT:
                raise AssertionError("file-modification assurance drifted")
            self.bucket_unlocked = True
            return {"status": "accepted"}
        if method == "DELETE" and url.endswith("/" + repairer.PDF_NAME):
            if not self.bucket_unlocked:
                raise AssertionError("published-file bucket was not unlocked")
            self.record["files"] = [
                item
                for item in self.record["files"]
                if repairer.file_name(item) != repairer.PDF_NAME
            ]
            return {}
        if method == "PUT" and url.endswith("/" + repairer.PDF_NAME):
            if not self.bucket_unlocked:
                raise AssertionError("published-file bucket was not unlocked")
            if data != self.pdf:
                raise AssertionError("wrong corrected PDF bytes uploaded")
            if content_type != "application/octet-stream":
                raise AssertionError("Zenodo bucket upload must use octet-stream")
            self._add_corrected_pdf()
            return copy.deepcopy(self.record["files"][-1])
        if method == "POST" and url.endswith("/actions/publish"):
            self.record["state"] = "done"
            return copy.deepcopy(self.record)
        raise AssertionError(f"unexpected request: {method} {url}")

    def request_bytes(self, url: str) -> bytes:
        self.calls.append(("GET_BYTES", url))
        if url == "https://zenodo.example/pdf":
            return self.pdf
        raise AssertionError(f"unexpected download: {url}")

    def delete(self, url: str) -> None:
        self.request("DELETE", url)


def write_pdf_copy() -> tuple[tempfile.TemporaryDirectory[str], Path, bytes]:
    raw = repairer.DEFAULT_PDF.read_bytes()
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / repairer.PDF_NAME
    path.write_bytes(raw)
    return tmp, path, raw


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def expect_failure(callable_obj, marker: str) -> None:
    try:
        callable_obj()
    except SystemExit as exc:
        require(marker in str(exc), f"unexpected failure: {exc}")
    else:
        raise SystemExit(f"FAIL: expected failure containing {marker!r}")


def main() -> int:
    tmp, pdf_path, raw = write_pdf_copy()
    try:
        already = FakeClient(raw, pdf_state="corrected")
        receipt = repairer.repair(
            already,
            pdf_path,
            acknowledgement=repairer.ACKNOWLEDGEMENT,
            now=datetime(2026, 8, 11, tzinfo=timezone.utc),
        )
        require(receipt["status"] == "already_corrected_verified", "idempotent status")
        require(receipt["mutation_performed"] is False, "idempotent correction mutated")
        require(
            not any(url.endswith("/actions/edit") for _, url in already.calls),
            "idempotent correction unlocked record",
        )

        prior = FakeClient(raw, pdf_state="prior")
        receipt = repairer.repair(
            prior,
            pdf_path,
            acknowledgement=repairer.ACKNOWLEDGEMENT,
            now=datetime(2026, 8, 11, tzinfo=timezone.utc),
        )
        require(receipt["status"] == "corrected_published_verified", "correction status")
        require(receipt["mutation_performed"] is True, "correction mutation receipt")
        methods = [method for method, _ in prior.calls]
        require(methods.count("DELETE") == 1, "correction must delete one known prior PDF")
        require(methods.count("PUT") == 1, "correction must upload one corrected PDF")
        require(
            (
                "POST",
                "https://zenodo.example/api/records/"
                f"{repairer.RECORD_ID}/file-modification",
            )
            in prior.calls,
            "correction did not unlock published-file editing",
        )
        require(
            ("POST", f"/deposit/depositions/{repairer.RECORD_ID}/actions/publish")
            in prior.calls,
            "correction did not republish",
        )
        require(
            set(repairer.files_by_name(prior.record))
            == {repairer.ARCHIVE_NAME, repairer.PDF_NAME},
            "correction changed the bounded file set",
        )
        require(
            repairer.classify_pdf_entry(repairer.files_by_name(prior.record)[repairer.PDF_NAME])
            == "corrected",
            "correction did not leave the corrected PDF",
        )

        missing = FakeClient(raw)
        receipt = repairer.repair(
            missing,
            pdf_path,
            acknowledgement=repairer.ACKNOWLEDGEMENT,
            now=datetime(2026, 8, 11, tzinfo=timezone.utc),
        )
        require(receipt["status"] == "corrected_published_verified", "missing-PDF status")
        require(not any(method == "DELETE" for method, _ in missing.calls), "missing PDF deleted")
        require(sum(method == "PUT" for method, _ in missing.calls) == 1, "missing PDF not added")

        unexpected_pdf = FakeClient(raw, pdf_state="prior")
        item = repairer.files_by_name(unexpected_pdf.record)[repairer.PDF_NAME]
        item["checksum"] = "md5:" + "0" * 32
        expect_failure(
            lambda: repairer.repair(
                unexpected_pdf,
                pdf_path,
                acknowledgement=repairer.ACKNOWLEDGEMENT,
                now=datetime(2026, 8, 11, tzinfo=timezone.utc),
            ),
            "unexpected Zenodo standalone PDF identity",
        )
        require(len(unexpected_pdf.calls) == 1, "unexpected PDF mutated before refusal")

        wrong = FakeClient(raw)
        wrong.record["metadata"]["title"] = "Wrong record"
        expect_failure(
            lambda: repairer.repair(
                wrong,
                pdf_path,
                acknowledgement=repairer.ACKNOWLEDGEMENT,
                now=datetime(2026, 8, 11, tzinfo=timezone.utc),
            ),
            "unexpected title",
        )
        require(len(wrong.calls) == 1, "identity mismatch must fail before mutation")

        late = FakeClient(raw, pdf_state="prior")
        expect_failure(
            lambda: repairer.repair(
                late,
                pdf_path,
                acknowledgement=repairer.ACKNOWLEDGEMENT,
                now=datetime(2026, 9, 15, tzinfo=timezone.utc),
            ),
            "30-day",
        )
        require(
            not any(method in {"PUT", "DELETE", "POST"} for method, _ in late.calls),
            "expired window mutated Zenodo",
        )

        unapproved = FakeClient(raw, pdf_state="prior")
        expect_failure(
            lambda: repairer.repair(
                unapproved,
                pdf_path,
                acknowledgement="",
                now=datetime(2026, 8, 11, tzinfo=timezone.utc),
            ),
            "acknowledgement",
        )
        require(not unapproved.calls, "missing acknowledgement contacted Zenodo")
    finally:
        tmp.cleanup()

    print("PASS: bounded Zenodo standalone-PDF correction contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
