#!/usr/bin/env python3
"""Live, non-writing smoke for three current external-agent routes.

The test downloads the public canonical Record-Chain Builder, creates signed
Echo, Verification, and Guardian application submissions, and requires the
live Gateway to accept every payload at /record-chain/preflight.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_SITE = "https://www.trinityaccord.org"


def fetch_bytes(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TrinityCurrentCorePreflightSmoke/2.0", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_json(url: str, timeout: int) -> dict:
    return json.loads(fetch_bytes(url, timeout).decode("utf-8"))


def run_builder(builder: Path, args: list[str], cwd: Path, timeout: int) -> str:
    result = subprocess.run(
        ["node", str(builder), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Builder failed for {' '.join(args[:2])}:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
        )
    return result.stdout.strip()


def post_preflight(url: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, sort_keys=True).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "TrinityCurrentCorePreflightSmoke/2.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gateway returned HTTP {exc.code}: {body[:2000]}") from exc


def _common_args(site: str) -> list[str]:
    loaded = ",".join([
        f"{site}/agent-brief/",
        f"{site}/api/record-chain-intake-gateway.v1.json",
    ])
    return [
        "--actor-label", "Live Preflight Governance Agent",
        "--provider", "Trinity live non-writing smoke",
        "--context-level", "CC-3",
        "--context-sufficient-for-selected-action", "true",
        "--context-read-confirmed", "true",
        "--loaded-urls", loaded,
        "--discovery-mode", "user_task_context",
        "--requesting-party-type", "human",
        "--introducing-party-type", "human",
        "--record-decision", "human",
        "--submission-executor", "self",
        "--human-operator-involved", "false",
        "--generate-authorship-key",
        "--key-dir", "./authorship-keys",
    ]


def _build_cases(builder: Path, site: str, work: Path, timeout: int) -> list[tuple[str, Path]]:
    common = _common_args(site)

    def oath(record_type: str) -> str:
        return run_builder(builder, ["print-oath", "--record-type", record_type], work, timeout)

    cases = [
        (
            "echo",
            ["echo", "--body", "Live non-writing recognition Echo.", "--readback", oath("echo"),
             "--out", "echo.json", *common],
            work / "echo.json",
        ),
        (
            "verification",
            [
                "verification", "--verification-level", "V3",
                "--scope-label", "live public Builder and Gateway preflight",
                "--what-was-checked", "public Builder execution,live preflight response",
                "--verification-claim", "The live non-writing preflight path was exercised with a fresh signed payload.",
                "--fresh-actions", "downloaded public Builder,built fresh payload,posted preflight",
                "--digital-profile", "integrity_checked",
                "--relationships-checked", "hashes,provides_context",
                "--physical-observation", "none", "--external-witness", "none",
                "--coverage-scope", "component_subset",
                "--limitations", "non-writing preflight only,no final chain inclusion claimed",
                "--claims-not-made", "semantic truth,institutional endorsement,physical identity",
                "--corrections-or-supersession-checked", "true",
                "--action-profile", "verification", "--readback", oath("verification"),
                "--out", "verification.json", *common,
            ],
            work / "verification.json",
        ),
        (
            "guardian_application",
            [
                "guardian-application", "--guardian-id", "auto", "--guardian-key-sha", "auto",
                "--readback", oath("guardian_application"), "--out", "guardian.json", *common,
            ],
            work / "guardian.json",
        ),
    ]

    built: list[tuple[str, Path]] = []
    for record_type, args, output in cases:
        run_builder(builder, args, work, timeout)
        built.append((record_type, output))
    return built


def run_live_smoke(site: str, timeout: int) -> None:
    site = site.rstrip("/")
    contract = fetch_json(f"{site}/api/record-chain-intake-gateway.v1.json", timeout)
    gateway = str(contract.get("base_url") or "").rstrip("/")
    preflight_path = contract.get("endpoints", {}).get("preflight", {}).get("path")
    if not gateway.startswith("https://") or preflight_path != "/record-chain/preflight":
        raise RuntimeError("Public Gateway discovery contract is missing the current preflight endpoint")

    with tempfile.TemporaryDirectory(prefix="trinity-current-live-preflight-") as temp_dir:
        work = Path(temp_dir)
        builder = work / "record-chain-builder.mjs"
        builder.write_bytes(fetch_bytes(f"{site}/downloads/record-chain-builder.mjs", timeout))

        failures: list[str] = []
        for record_type, payload_path in _build_cases(builder, site, work, timeout):
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            result = post_preflight(gateway + preflight_path, payload, timeout)
            accepted = result.get("accepted") is True
            route = result.get("route_detected")
            print(f"Preflight {record_type}: accepted={accepted} route_detected={route}")
            if not accepted or route != record_type:
                diagnostics = json.dumps(result.get("diagnostics", []), indent=2)[:3000]
                failures.append(f"{record_type} live preflight failed: {diagnostics}")
        if failures:
            raise RuntimeError("\n\n".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    run_live_smoke(args.site, args.timeout)
    print("PASS: all 3 current signed core routes were accepted by live preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
