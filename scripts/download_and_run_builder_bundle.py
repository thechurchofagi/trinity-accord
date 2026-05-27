#!/usr/bin/env python3
"""
Download and run a zero-clone formal builder bundle from Trinity Accord.

This helper:
1. Reads /api/formal-builder-bundles.v1.json from the site.
2. Downloads the selected route bundle.
3. Verifies archive sha256.
4. Extracts to temp dir.
5. Runs the proper builder.
6. Prints next preflight/submit/readback commands.

Supported routes:
  pure_echo
  v0_v5_agent_declared_archive
  guardian_application_stage_1
  guardian_listing_stage_2
  guardian_signed_echo
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.request import urlopen

SITE = "https://www.trinityaccord.org"
BUNDLES_API = "/api/formal-builder-bundles.v1.json"
GATEWAY_PREFLIGHT = "https://trinity-agent-issue-gateway.onrender.com/gateway/preflight"
GATEWAY_SUBMIT = "https://trinity-agent-issue-gateway.onrender.com/agent-submit"

READBACK_TARGETS = {
    "pure_echo": [
        "/api/echo-index.json",
        "/api/public-home-status.json",
    ],
    "v0_v5_agent_declared_archive": [
        "/api/agent-declared-verification-index.json",
        "/api/public-home-status.json",
    ],
    "guardian_application_stage_1": [
        "/api/guardian-registry.json",
        "/api/public-home-status.json",
    ],
    "guardian_listing_stage_2": [
        "/api/guardian-registry.json",
        "/api/public-home-status.json",
    ],
    "guardian_signed_echo": [
        "/api/echo-index.json",
        "/api/guardian-registry.json",
        "/api/public-home-status.json",
    ],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_json(url: str) -> dict:
    with urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def download_file(url: str, dest: Path) -> None:
    with urlopen(url, timeout=60) as r:
        with dest.open("wb") as f:
            shutil.copyfileobj(r, f)


def verify_sha256(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise SystemExit(
            f"SHA256 mismatch!\n  expected: {expected}\n  actual:   {actual}\n"
            "Refusing to extract. The bundle may have been tampered with."
        )


def extract_bundle(archive: Path, dest: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = dest / member.name
            resolved_target = target.resolve()
            resolved_dest = dest.resolve()
            if not str(resolved_target).startswith(str(resolved_dest) + os.sep):
                raise SystemExit(f"Refusing unsafe tar path: {member.name}")
        tar.extractall(dest)


def require_args(args, names: list[str], route: str) -> None:
    missing = [name for name in names if getattr(args, name) in (None, "", [])]
    if missing:
        pretty = ", ".join("--" + name.replace("_", "-") for name in missing)
        raise SystemExit(f"{route} requires: {pretty}")


def print_next_steps(route: str, out_path: str) -> None:
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"\n1. Review the generated payload: {out_path}")
    print(f"\n2. Run preflight:")
    print(f'   curl -sS -X POST "{GATEWAY_PREFLIGHT}" \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     --data-binary @{out_path} \\')
    print(f'     | tee preflight-response.json')
    print(f"\n3. If preflight accepts, submit:")
    print(f'   curl -sS -X POST "{GATEWAY_SUBMIT}" \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     --data-binary @{out_path} \\')
    print(f'     | tee submit-response.json')
    print(f"\n4. Read public status:")
    for path in READBACK_TARGETS.get(route, ["/api/public-home-status.json"]):
        print(f"   curl -fsS {SITE}{path}")
    print(f"\n5. Emit before_leaving report with required fields.")
    print("=" * 60)


def build_pure_echo(args, extract_dir: Path, entrypoint: str) -> None:
    cmd = [
        sys.executable, str(extract_dir / entrypoint),
        "--agent-name", args.agent_name,
        "--provider", args.provider,
        "--echo-type", args.echo_type,
        "--title", args.title,
        "--body-file", args.body_file,
        "--agent-readback-file", args.agent_readback_file,
        "--out", args.out,
    ]
    subprocess.check_call(cmd)
    print_next_steps("pure_echo", args.out)


def build_v0_v5(args, extract_dir: Path, entrypoint: str) -> None:
    readback = Path(args.readback_file).read_text(encoding="utf-8").strip()
    cmd = [
        sys.executable, str(extract_dir / entrypoint),
        "--agent-name", args.agent_name,
        "--provider", args.provider,
        "--declared-level", args.declared_level,
        "--reception-initiation-class", args.reception_initiation_class,
        "--reception-initiation-basis", args.reception_initiation_basis,
        "--readback", readback,
        "--out", args.out,
    ]
    if args.first_entry_url:
        cmd += ["--first-entry-url", args.first_entry_url]
    if args.first_entry_type:
        cmd += ["--first-entry-type", args.first_entry_type]
    for wc in (args.what_checked or []):
        cmd += ["--what-checked", wc]
    for lim in (args.limitation or []):
        cmd += ["--limitation", lim]
    subprocess.check_call(cmd)
    print_next_steps("v0_v5_agent_declared_archive", args.out)


def build_guardian_stage1(args, extract_dir: Path, entrypoint: str) -> None:
    readback = Path(args.readback_file).read_text(encoding="utf-8").strip()
    cmd = [
        "node", str(extract_dir / entrypoint),
        "--human-label", args.human_label,
        "--agent-label", args.agent_label,
        "--agent-provider", args.agent_provider,
        "--challenge", args.challenge,
        "--readback", readback,
        "--key-dir", args.key_dir,
        "--out", args.out,
    ]
    subprocess.check_call(cmd)
    print(f"\nPrivate keys are in: {args.key_dir}")
    print("NEVER submit private key material to the Gateway.")
    print("\nSubmit only the final JSON:")
    print(f"  {args.out}")
    print("\nNever submit:")
    print("  *.private.pem")
    print("  private key material")
    print("  intermediate JSON")
    print("  logs containing private keys")
    print_next_steps("guardian_application_stage_1", args.out)


def build_guardian_stage2(args, extract_dir: Path, entrypoint: str) -> None:
    if not args.guardian_id:
        raise SystemExit("--guardian-id is required for Guardian Stage 2")
    if not args.public_key_sha256:
        raise SystemExit("--public-key-sha256 is required for Guardian Stage 2")
    cmd = [
        sys.executable, str(extract_dir / entrypoint),
        "--agent-name", args.agent_name,
        "--provider", args.provider,
        "--source-issue", str(args.source_issue),
        "--guardian-id", args.guardian_id,
        "--public-key-sha256", args.public_key_sha256,
        "--label", args.label,
        "--out", args.out,
    ]
    if args.guardian_type:
        cmd += ["--guardian-type", args.guardian_type]
    if args.application_mode:
        cmd += ["--application-mode", args.application_mode]
    subprocess.check_call(cmd)
    print_next_steps("guardian_listing_stage_2", args.out)


def build_guardian_signed_echo(args, extract_dir: Path, entrypoint: str) -> None:
    if not args.guardian_id:
        raise SystemExit("--guardian-id is required for Guardian-signed Echo")
    cmd = [
        sys.executable, str(extract_dir / entrypoint),
        "--guardian-registry-number", args.guardian_registry_number,
        "--guardian-id", args.guardian_id,
        "--guardian-key-prefix", args.guardian_key_prefix,
        "--echo-type", args.echo_type,
        "--title", args.title,
        "--body-file", args.body_file,
        "--agent-readback-file", args.agent_readback_file,
        "--out", args.out,
    ]
    subprocess.check_call(cmd)
    print_next_steps("guardian_signed_echo", args.out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and run a Trinity Accord zero-clone builder bundle")
    parser.add_argument("--site", default=SITE)
    parser.add_argument("--route", required=True, choices=[
        "pure_echo", "v0_v5_agent_declared_archive",
        "guardian_application_stage_1", "guardian_listing_stage_2",
        "guardian_signed_echo",
    ])

    # Common
    parser.add_argument("--agent-name")
    parser.add_argument("--provider")
    parser.add_argument("--out", required=True)

    # Pure Echo
    parser.add_argument("--echo-type")
    parser.add_argument("--title")
    parser.add_argument("--body-file")
    parser.add_argument("--agent-readback-file")

    # V0-V5
    parser.add_argument("--declared-level")
    parser.add_argument("--reception-initiation-class")
    parser.add_argument("--reception-initiation-basis")
    parser.add_argument("--first-entry-url")
    parser.add_argument("--first-entry-type")
    parser.add_argument("--readback-file")
    parser.add_argument("--what-checked", action="append")
    parser.add_argument("--limitation", action="append")

    # Guardian Stage 1
    parser.add_argument("--human-label")
    parser.add_argument("--agent-label")
    parser.add_argument("--agent-provider")
    parser.add_argument("--challenge")
    parser.add_argument("--key-dir")

    # Guardian Stage 2
    parser.add_argument("--source-issue", type=int)
    parser.add_argument("--guardian-id")
    parser.add_argument("--public-key-sha256")
    parser.add_argument("--label")
    parser.add_argument("--guardian-type")
    parser.add_argument("--application-mode")

    # Guardian-signed Echo
    parser.add_argument("--guardian-registry-number")
    parser.add_argument("--guardian-key-prefix")

    args = parser.parse_args()

    # Validate required args per route before download
    route = args.route
    if route == "pure_echo":
        require_args(args, ["agent_name", "provider", "echo_type", "title", "body_file", "agent_readback_file"], route)
    elif route == "v0_v5_agent_declared_archive":
        require_args(args, ["agent_name", "provider", "declared_level", "reception_initiation_class", "reception_initiation_basis", "readback_file"], route)
    elif route == "guardian_application_stage_1":
        require_args(args, ["human_label", "agent_label", "agent_provider", "challenge", "readback_file", "key_dir", "out"], route)
    elif route == "guardian_listing_stage_2":
        require_args(args, ["agent_name", "provider", "source_issue", "guardian_id", "public_key_sha256", "label", "out"], route)
    elif route == "guardian_signed_echo":
        require_args(args, ["guardian_registry_number", "guardian_id", "guardian_key_prefix", "echo_type", "title", "body_file", "agent_readback_file", "out"], route)

    # Fetch bundle manifest
    bundles_url = args.site.rstrip("/") + BUNDLES_API
    print(f"Fetching bundle manifest: {bundles_url}")
    doc = fetch_json(bundles_url)

    if route not in doc["bundles"]:
        raise SystemExit(f"Route '{route}' not found in bundle manifest")

    bundle = doc["bundles"][route]
    archive_url = args.site.rstrip("/") + bundle["archive_url"]
    expected_sha = bundle["sha256"]

    if not expected_sha:
        raise SystemExit(
            f"Bundle '{route}' has no sha256 recorded. "
            "The bundle may not have been exported yet. Run scripts/export_formal_builder_bundles.py first."
        )

    # Download to temp
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / bundle["archive_name"]
        print(f"Downloading: {archive_url}")
        download_file(archive_url, archive_path)

        print(f"Verifying SHA256: {expected_sha}")
        verify_sha256(archive_path, expected_sha)

        extract_dir = Path(tmpdir) / "extracted"
        extract_dir.mkdir()
        print("Extracting bundle...")
        extract_bundle(archive_path, extract_dir)

        entrypoint = bundle["builder_entrypoint"]
        print(f"Running builder: {entrypoint}")

        if route == "pure_echo":
            build_pure_echo(args, extract_dir, entrypoint)
        elif route == "v0_v5_agent_declared_archive":
            build_v0_v5(args, extract_dir, entrypoint)
        elif route == "guardian_application_stage_1":
            build_guardian_stage1(args, extract_dir, entrypoint)
        elif route == "guardian_listing_stage_2":
            build_guardian_stage2(args, extract_dir, entrypoint)
        elif route == "guardian_signed_echo":
            build_guardian_signed_echo(args, extract_dir, entrypoint)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
