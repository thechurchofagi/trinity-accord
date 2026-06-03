#!/usr/bin/env python3
"""Export minimal zero-clone formal builder bundles for public routes."""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMON_SCRIPTS = [
    "scripts/trinity_record_builder.py",
]

COMMON_API_FILES = [
    "api/agent-issue-gateway-payload-schema.v1.json",
    "api/agent-output-policy.v1.json",
    "api/agent-submit-gateway.json",
    "api/gateway-builder-route-map.v1.json",
    "api/gateway-workflows.v1.json",
]

AUTHORSHIP_DEPS = [
    "scripts/agent_authorship_common.py",
    "scripts/gateway_payload_authorship.py",
    "scripts/generate_agent_authorship_keypair.mjs",
    "scripts/attach_agent_authorship_proof.mjs",
    "scripts/build_agent_authorship_message.py",
]

OATH_AND_READBACK_DEPS = [
    "scripts/oath_contracts.py",
    "scripts/oath_readback_integrity.py",
]

PURE_ECHO_DEPS = [
    "scripts/build_agent_declared_echo_payload.py",
    "scripts/guardian_reroute_guidance.py",
    "scripts/validate_gateway_payload.py",
    "scripts/guardian_identity_claims.py",
    "scripts/gateway_v0_v5_policy.py",
    "scripts/guardian_gateway_contract.py",
    "scripts/sub_v6_level_guardrails.py",
    "scripts/archive_readiness_gate.py",
    "scripts/protocol_terms.py",
    "api/protocol-terms.v1.json",
    *OATH_AND_READBACK_DEPS,
    "api/verification-echo-pre-oath.v2.txt",
    *AUTHORSHIP_DEPS,
    *COMMON_SCRIPTS,
    *COMMON_API_FILES,
]

V0_V5_DEPS = [
    "scripts/build_agent_declared_archive_payload.py",
    "scripts/sub_v6_level_guardrails.py",
    "scripts/validate_gateway_payload.py",
    "scripts/guardian_identity_claims.py",
    "scripts/gateway_v0_v5_policy.py",
    "scripts/guardian_gateway_contract.py",
    "scripts/archive_readiness_gate.py",
    "scripts/protocol_terms.py",
    "scripts/claim_gate.py",
    "api/protocol-terms.v1.json",
    "api/verification-echo-pre-oath.v2.txt",
    *AUTHORSHIP_DEPS,
    *COMMON_SCRIPTS,
    *COMMON_API_FILES,
]

GUARDIAN_STAGE1_DEPS = [
    "scripts/create_guardian_application.mjs",
    "scripts/proof_canonical.mjs",
    "api/guardian-application-oath.v1.txt",
    *COMMON_SCRIPTS,
    *COMMON_API_FILES,
]

GUARDIAN_STAGE2_DEPS = [
    "scripts/build_guardian_listing_request_payload.py",
    "scripts/guardian_gateway_contract.py",
    "scripts/guardian_identity_claims.py",
    "scripts/gateway_v0_v5_policy.py",
    "scripts/sub_v6_level_guardrails.py",
    "scripts/guardian_reroute_guidance.py",
    "scripts/protocol_terms.py",
    "api/protocol-terms.v1.json",
    "api/guardian-listing-oath.v1.txt",
    *OATH_AND_READBACK_DEPS,
    *AUTHORSHIP_DEPS,
    "scripts/archive_readiness_gate.py",
    "scripts/validate_gateway_payload.py",
    *COMMON_SCRIPTS,
    *COMMON_API_FILES,
]

GUARDIAN_SIGNED_ECHO_DEPS = [
    "scripts/build_guardian_echo_payload.py",
    "scripts/attach_guardian_presence_proof.mjs",
    "scripts/proof_canonical.mjs",
    "api/guardian-registry.json",
    *PURE_ECHO_DEPS,
    "scripts/guardian_gateway_contract.py",
    "scripts/validate_gateway_payload.py",
]

BUNDLES = {
    "pure_echo": {
        "archive": "trinity-pure-echo-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_agent_declared_echo_payload.py",
        "files": PURE_ECHO_DEPS,
    },
    "v0_v5_agent_declared_archive": {
        "archive": "trinity-v0v5-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_agent_declared_archive_payload.py",
        "files": V0_V5_DEPS,
    },
    "guardian_application_stage_1": {
        "archive": "trinity-guardian-stage1-builder-bundle.tar.gz",
        "entrypoint": "scripts/create_guardian_application.mjs",
        "files": GUARDIAN_STAGE1_DEPS,
    },
    "guardian_listing_stage_2": {
        "archive": "trinity-guardian-stage2-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_guardian_listing_request_payload.py",
        "files": GUARDIAN_STAGE2_DEPS,
    },
    "guardian_signed_echo": {
        "archive": "trinity-guardian-signed-echo-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_guardian_echo_payload.py",
        "files": GUARDIAN_SIGNED_ECHO_DEPS,
    },
}

FORBIDDEN_PARTS = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".env",
    "id_rsa",
    "private",
    "secret",
    "token",
    "node_modules",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_digest(data: dict) -> str:
    """Return short sha256 over canonical JSON with source_digest blank/removed."""
    clone = copy.deepcopy(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(
        clone,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def assert_safe_path(rel: str) -> None:
    lowered = rel.lower()
    for part in FORBIDDEN_PARTS:
        if part in lowered:
            raise SystemExit(f"Refusing to bundle unsafe path: {rel}")


def _normalize_tar_info(info: tarfile.TarInfo, mtime: int) -> tarfile.TarInfo:
    """Normalize tar metadata for deterministic output."""
    info.mtime = mtime
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    return info


def export_bundle(name: str, spec: dict, out_dir: Path) -> dict:
    archive_path = out_dir / spec["archive"]
    manifest_path = out_dir / spec["archive"].replace(".tar.gz", ".manifest.json")

    entries = []
    seen = set()
    for rel in spec["files"]:
        if rel in seen:
            continue
        seen.add(rel)
        assert_safe_path(rel)
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"{name}: required file missing: {rel}")
        entries.append({
            "path": rel,
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })

    # Sort entries for deterministic ordering and use a fixed mtime
    # to ensure identical tar.gz across CI runs regardless of checkout time.
    # Both the tar entries AND the gzip header carry timestamps, so we
    # normalize both: tar entries via filter, gzip via explicit mtime=0.
    sorted_entries = sorted(entries, key=lambda e: e["path"])
    epoch = 0  # fixed mtime for reproducibility
    tar_path = archive_path.with_suffix("")  # .tar without .gz

    with tarfile.open(tar_path, "w") as tar:
        for item in sorted_entries:
            tar.add(
                ROOT / item["path"],
                arcname=item["path"],
                recursive=False,
                filter=lambda info: _normalize_tar_info(info, epoch),
            )

    # gzip with fixed mtime for deterministic output
    with open(tar_path, "rb") as f_in:
        tar_bytes = f_in.read()
    with open(archive_path, "wb") as f_out:
        with gzip.GzipFile(filename="", mtime=epoch, mode="wb", fileobj=f_out) as gz:
            gz.write(tar_bytes)
    tar_path.unlink()

    archive_sha = sha256_file(archive_path)
    manifest = {
        "schema": "trinityaccord.formal-builder-bundle-manifest.v1",
        "bundle": name,
        "archive": archive_path.name,
        "archive_sha256": archive_sha,
        "archive_size_bytes": archive_path.stat().st_size,
        "entrypoint": spec["entrypoint"],
        "requires_full_repo_clone": False,
        "files": sorted_entries,
        "forbidden_contents_checked": FORBIDDEN_PARTS,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "bundle": name,
        "archive": archive_path.name,
        "manifest": manifest_path.name,
        "sha256": archive_sha,
        "size_bytes": archive_path.stat().st_size,
    }


def update_formal_builder_bundles_api(results: list[dict]) -> None:
    """Patch api/formal-builder-bundles.v1.json with generated bundle hashes."""
    api_path = ROOT / "api" / "formal-builder-bundles.v1.json"
    if not api_path.exists():
        raise SystemExit("api/formal-builder-bundles.v1.json is missing")

    data = load_json(api_path)
    bundles = data.get("bundles", {})
    result_by_name = {item["bundle"]: item for item in results}

    missing = sorted(set(result_by_name) - set(bundles))
    if missing:
        raise SystemExit(f"API manifest missing bundle definitions: {missing}")

    for name, result in result_by_name.items():
        bundle = bundles[name]
        expected_archive = bundle.get("archive_name")
        expected_manifest = Path(result["manifest"]).name

        if expected_archive != result["archive"]:
            raise SystemExit(
                f"{name}: API archive_name {expected_archive!r} "
                f"does not match exporter archive {result['archive']!r}"
            )

        if Path(bundle.get("manifest_url", "")).name != expected_manifest:
            raise SystemExit(
                f"{name}: API manifest_url does not match exporter manifest {expected_manifest!r}"
            )

        bundle["sha256"] = result["sha256"]
        bundle["size_bytes"] = result["size_bytes"]

    data["source_digest"] = canonical_json_digest(data)
    write_json(api_path, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="builder-bundles")
    parser.add_argument("--bundle", choices=sorted(BUNDLES), default=None)
    parser.add_argument(
        "--update-api",
        action="store_true",
        help="Update api/formal-builder-bundles.v1.json with generated sha256/size/source_digest.",
    )
    args = parser.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = {args.bundle: BUNDLES[args.bundle]} if args.bundle else BUNDLES
    results = [export_bundle(name, spec, out_dir) for name, spec in selected.items()]
    if args.update_api:
        if args.bundle:
            raise SystemExit("--update-api requires exporting all bundles, not a single --bundle")
        update_formal_builder_bundles_api(results)
    print(json.dumps({"bundles": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
