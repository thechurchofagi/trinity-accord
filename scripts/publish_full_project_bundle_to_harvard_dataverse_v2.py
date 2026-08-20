#!/usr/bin/env python3
"""Compatibility-fixed Harvard Dataverse publisher entry point.

The full-project verifier emits `result: pass`; the original Harvard publisher
incorrectly required `status: PASS`.  This wrapper patches only that validation
boundary and delegates every upload/public-readback step to the reviewed v1
publisher unchanged.
"""
from __future__ import annotations

import json
import zipfile

import publish_full_project_bundle_to_harvard_dataverse as impl


def verify_embedded_bundle(archive, source_sha):
    with zipfile.ZipFile(archive, "r") as zf:
        manifest_name = impl.find_zip_member(zf, "full-project-manifest.json")
        report_name = impl.find_zip_member(zf, "verification-report.json")
        impl.find_zip_member(zf, "SHA256SUMS")
        impl.find_zip_member(zf, "verify-and-restore-full-project.py")
        manifest = json.loads(zf.read(manifest_name).decode("utf-8"))
        report = json.loads(zf.read(report_name).decode("utf-8"))

    report_ok = report.get("result") == "pass" or report.get("status") == "PASS"
    if not report_ok:
        raise impl.PublishError(
            "embedded verification report is not PASS: "
            f"result={report.get('result')!r} status={report.get('status')!r}"
        )
    if manifest.get("source_git_commit_sha") != source_sha:
        raise impl.PublishError(
            "bundle manifest source_git_commit_sha does not match the successful Actions run"
        )
    identity = manifest.get("bundle_identity_sha256")
    if not isinstance(identity, str) or len(identity) != 64:
        raise impl.PublishError("bundle manifest has no valid bundle_identity_sha256")
    return manifest


impl.verify_embedded_bundle = verify_embedded_bundle


if __name__ == "__main__":
    try:
        raise SystemExit(impl.main())
    except Exception as exc:
        impl.log(f"FAIL {type(exc).__name__}: {exc}")
        raise
