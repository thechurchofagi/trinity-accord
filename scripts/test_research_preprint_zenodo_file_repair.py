#!/usr/bin/env python3
"""Offline tests for the bounded Zenodo standalone-PDF repair."""
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
    def __init__(self, pdf: bytes, *, include_pdf: bool = False) -> None:
        self.pdf = pdf
        self.calls: list[tuple[str, str]] = []
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
            "links": {"bucket": "https://zenodo.example/api/files/bucket"},
            "files": [
                {
                    "filename": repairer.ARCHIVE_NAME,
                    "filesize": repairer.ARCHIVE_BYTES,
                    "checksum": f"md5:{repairer.ARCHIVE_MD5}",
                    "links": {"download": "https://zenodo.example/archive"},
                }
            ],
        }
        if include_pdf:
            self._add_pdf()

    def _add_pdf(self) -> None:
        if any(repairer.file_name(item) == repairer.PDF_NAME for item in self.record["files"]):
            return
        self.record["files"].append(
            {
                "filename": repairer.PDF_NAME,
                "filesize": len(self.pdf),
                "checksum": "md5:" + hashlib.md5(self.pdf).hexdigest(),  # nosec B324
                "links": {"download": "https://zenodo.example/pdf"},
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
        del payload, content_type
        self.calls.append((method, url))
        if method == "GET" and url in {
            f"/deposit/depositions/{repairer.RECORD_ID}",
            f"/records/{repairer.RECORD_ID}",
        }:
            return copy.deepcopy(self.record)
        if method == "POST" and url.endswith("/actions/edit"):
            self.record["state"] = "inprogress"
            return copy.deepcopy(self.record)
        if method == "PUT" and url.endswith("/" + repairer.PDF_NAME):
            if data != self.pdf:
                raise AssertionError("wrong PDF bytes uploaded")
            self._add_pdf()
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
        already = FakeClient(raw, include_pdf=True)
        receipt = repairer.repair(
            already,
            pdf_path,
            acknowledgement=repairer.ACKNOWLEDGEMENT,
            now=datetime(2026, 8, 11, tzinfo=timezone.utc),
        )
        require(receipt["status"] == "already_present_verified", "idempotent status")
        require(receipt["mutation_performed"] is False, "idempotent repair mutated")
        require(
            not any(url.endswith("/actions/edit") for _, url in already.calls),
            "idempotent repair unlocked record",
        )

        missing = FakeClient(raw)
        receipt = repairer.repair(
            missing,
            pdf_path,
            acknowledgement=repairer.ACKNOWLEDGEMENT,
            now=datetime(2026, 8, 11, tzinfo=timezone.utc),
        )
        require(receipt["status"] == "published_verified", "repair status")
        require(receipt["mutation_performed"] is True, "repair mutation receipt")
        methods = [method for method, _ in missing.calls]
        require(methods.count("PUT") == 1, "repair must upload exactly one file")
        require(
            ("POST", f"/deposit/depositions/{repairer.RECORD_ID}/actions/publish")
            in missing.calls,
            "repair did not republish",
        )
        require(
            set(repairer.files_by_name(missing.record))
            == {repairer.ARCHIVE_NAME, repairer.PDF_NAME},
            "repair changed the bounded file set",
        )

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

        late = FakeClient(raw)
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
            not any(method in {"PUT", "POST"} for method, _ in late.calls),
            "expired window must fail before mutation",
        )

        unapproved = FakeClient(raw)
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

    print("PASS: bounded Zenodo standalone-PDF repair contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
