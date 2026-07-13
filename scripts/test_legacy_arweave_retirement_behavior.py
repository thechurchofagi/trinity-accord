#!/usr/bin/env python3
"""Behavioral regression for retired legacy/Phase-5 Arweave paths."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(command: list[str], *, expected: int | None = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if expected is not None and result.returncode != expected:
        raise AssertionError(
            f"command failed ({result.returncode}, expected {expected}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(canonical_dumps(value).encode("utf-8")).hexdigest()


def parse_build_output(result: subprocess.CompletedProcess[str]) -> Path:
    value = json.loads(result.stdout)
    path = Path(value["bundle_file"])
    require(path.is_absolute(), "temporary build output must report an absolute path")
    return path


def test_deterministic_bundle_and_read_only_updater(temp: Path) -> Path:
    out_a = temp / "a"
    out_b = temp / "b"
    command_a = [
        sys.executable,
        str(SCRIPTS / "build_record_chain_data_arweave_bundle.py"),
        "--mode",
        "snapshot",
        "--height",
        "15",
        "--out-dir",
        str(out_a),
    ]
    command_b = command_a[:-1] + [str(out_b)]
    first = parse_build_output(run(command_a))
    second = parse_build_output(run(command_b))
    require(first.name == second.name, "same frozen source must produce the same deterministic filename")
    require(first.read_bytes() == second.read_bytes(), "same frozen source must produce byte-identical bundles")

    bundle = json.loads(first.read_text(encoding="utf-8"))
    require(bundle.get("schema") == "trinityaccord.legacy-hash-chain-data-snapshot-bundle.v2", "new bundle must use explicit legacy v2 schema")
    require(bundle.get("created_at") == "2026-06-14T06:58:35Z", "bundle timestamp must be stable source metadata")
    require("native_chain_tip" not in bundle, "frozen legacy bundle must not include moving native-chain state")
    boundary = bundle.get("boundary") or {}
    require(boundary.get("historical_archive_only") is True, "historical boundary missing")
    require(boundary.get("not_current_native_record_chain") is True, "native-chain rejection boundary missing")

    run([sys.executable, str(SCRIPTS / "verify_record_chain_data_arweave_bundle.py"), "--bundle-file", str(first)])

    registry = ROOT / "record-chain/arweave-data-registry.json"
    api_registry = ROOT / "api/record-chain-arweave-data-registry.json"
    before = (file_sha(registry), file_sha(api_registry))
    preview = run(
        [
            sys.executable,
            str(SCRIPTS / "update_record_chain_data_arweave_registry.py"),
            "--bundle-file",
            str(first),
            "--mode",
            "dry-run",
        ]
    )
    preview_json = json.loads(preview.stdout)
    require(preview_json.get("retired_read_only_preview") is True, "dry-run must be explicitly read-only")
    require(preview_json["candidate"].get("would_write_registry") is False, "dry-run must say it will not write")
    require(before == (file_sha(registry), file_sha(api_registry)), "dry-run changed a historical registry")

    live = run(
        [
            sys.executable,
            str(SCRIPTS / "update_record_chain_data_arweave_registry.py"),
            "--bundle-file",
            str(first),
            "--mode",
            "live",
        ],
        expected=None,
    )
    require(live.returncode != 0, "retired live registry update must fail")
    require("retired" in (live.stdout + live.stderr).lower(), "retired live failure must explain the boundary")
    require(before == (file_sha(registry), file_sha(api_registry)), "failed live attempt changed a historical registry")
    return first


def write_bundle(path: Path, value: dict[str, Any]) -> None:
    path.write_text(canonical_dumps(value), encoding="utf-8")


def test_tamper_detection(temp: Path, source: Path) -> None:
    original = json.loads(source.read_text(encoding="utf-8"))

    bad_self = temp / "bad-self.json"
    value = copy.deepcopy(original)
    value["records"][0]["record_payload"]["tampered"] = True
    write_bundle(bad_self, value)
    result = run(
        [sys.executable, str(SCRIPTS / "verify_record_chain_data_arweave_bundle.py"), "--bundle-file", str(bad_self)],
        expected=None,
    )
    require(result.returncode != 0 and "self-hash" in (result.stdout + result.stderr).lower(), "content tamper must fail the embedded self-hash")

    forbidden = temp / "forbidden.json"
    value = copy.deepcopy(original)
    value["records"][0]["record_payload"]["raw_oath"] = "must not be archived"
    value["bundle_identity_sha256"] = canonical_sha(
        {
            key: item
            for key, item in value.items()
            if key not in {"created_at", "bundle_canonical_sha256", "bundle_identity_sha256", "native_chain_tip"}
        }
    )
    value["bundle_canonical_sha256"] = canonical_sha(
        {key: item for key, item in value.items() if key != "bundle_canonical_sha256"}
    )
    write_bundle(forbidden, value)
    result = run(
        [sys.executable, str(SCRIPTS / "verify_record_chain_data_arweave_bundle.py"), "--bundle-file", str(forbidden)],
        expected=None,
    )
    require(result.returncode != 0 and "forbidden" in (result.stdout + result.stderr).lower(), "actual forbidden content must fail even when flags and hashes are recomputed")


def test_historical_registry_and_readback(temp: Path) -> None:
    verifier = str(SCRIPTS / "verify_record_chain_data_arweave_registry.py")
    strict = run(
        [sys.executable, verifier, "--verify-local-bundles"],
        expected=None,
    )
    require(strict.returncode != 0 and "duplicate live uploads" in (strict.stdout + strict.stderr).lower(), "strict verification must expose historical duplicate paid uploads")

    allowed = run(
        [
            sys.executable,
            verifier,
            "--verify-local-bundles",
            "--allow-known-historical-duplicates",
        ]
    )
    data = json.loads(allowed.stdout)
    warnings = data.get("warnings") or []
    require(len(warnings) == 1, "known duplicate pair must be preserved as one explicit warning")
    require(warnings[0].get("preserved_not_endorsed") is True, "duplicate warning must not endorse the duplicate")

    original = json.loads((ROOT / "record-chain/arweave-data-registry.json").read_text(encoding="utf-8"))
    tampered = copy.deepcopy(original)
    tampered["entries"][0]["arweave_readback_sha256"] = "0" * 64
    path = temp / "tampered-registry.json"
    path.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = run(
        [
            sys.executable,
            verifier,
            "--registry",
            str(path),
            "--verify-local-bundles",
            "--allow-known-historical-duplicates",
        ],
        expected=None,
    )
    require(result.returncode != 0 and "payload/readback" in (result.stdout + result.stderr).lower(), "registry readback tamper must fail")


def test_workflow_retirement() -> None:
    data = (ROOT / ".github/workflows/record-chain-data-arweave-archive.yml").read_text(encoding="utf-8")
    phase5 = (ROOT / ".github/workflows/phase5-ots-arweave-paid-upload.yml").read_text(encoding="utf-8")
    echo = (ROOT / ".github/workflows/paid-echo-arweave-canary.yml").read_text(encoding="utf-8")
    current = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text(encoding="utf-8")

    for name, text in (("legacy data", data), ("phase5", phase5), ("echo", echo)):
        require("contents: write" not in text, f"{name} retired workflow retains write permission")
        require("secrets.ARKEY" not in text, f"{name} retired workflow retains wallet secret access")
        require("git push" not in text, f"{name} retired workflow retains a push path")

    require("upload_mode" not in data and "arweave_upload_payload" not in data, "legacy data workflow retains upload controls")
    require("paid-upload" not in phase5 and "--enable-paid-upload" not in phase5, "Phase 5 workflow retains paid upload")
    require("production" not in echo and "ALLOW_PAID_ARWEAVE_CANARY: \"true\"" not in echo, "echo workflow retains production upload")
    require("secrets.ARKEY" in current and "contents: write" in current, "current native archive route must remain explicit")
    require("build_record_chain_arweave_archive.py" in current, "current native archive builder missing")


def main() -> int:
    test_workflow_retirement()
    with tempfile.TemporaryDirectory(prefix="trinity-legacy-arweave-") as directory:
        temp = Path(directory)
        bundle = test_deterministic_bundle_and_read_only_updater(temp)
        test_tamper_detection(temp, bundle)
        test_historical_registry_and_readback(temp)
    print("PASS: legacy/Phase-5 Arweave upload paths are retired and historical evidence is verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
