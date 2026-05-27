#!/usr/bin/env python3
"""Export minimal zero-clone formal builder bundles for public routes."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMON_PY_FILES = [
    "scripts/gateway_payload_authorship.py",
    "scripts/agent_authorship_common.py",
    "scripts/validate_gateway_payload.py",
    "scripts/archive_readiness_gate.py",
    "api/agent-issue-gateway-payload-schema.v1.json",
    "api/agent-output-policy.v1.json",
    "api/agent-submit-gateway.json",
    "api/gateway-builder-route-map.v1.json",
    "api/gateway-workflows.v1.json",
    "scripts/generate_agent_authorship_keypair.mjs",
]

BUNDLES = {
    "pure_echo": {
        "archive": "trinity-pure-echo-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_agent_declared_echo_payload.py",
        "files": [
            "scripts/build_agent_declared_echo_payload.py",
            "api/verification-echo-pre-oath.v2.txt",
            *COMMON_PY_FILES,
        ],
    },
    "v0_v5_agent_declared_archive": {
        "archive": "trinity-v0v5-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_agent_declared_archive_payload.py",
        "files": [
            "scripts/build_agent_declared_archive_payload.py",
            "scripts/sub_v6_level_guardrails.py",
            "api/verification-echo-pre-oath.v2.txt",
            *COMMON_PY_FILES,
        ],
    },
    "guardian_application_stage_1": {
        "archive": "trinity-guardian-stage1-builder-bundle.tar.gz",
        "entrypoint": "scripts/create_guardian_application.mjs",
        "files": [
            "scripts/create_guardian_application.mjs",
            "scripts/proof_canonical.mjs",
            "api/agent-issue-gateway-payload-schema.v1.json",
            "api/agent-submit-gateway.json",
            "api/gateway-builder-route-map.v1.json",
            "api/gateway-workflows.v1.json",
        ],
    },
    "guardian_listing_stage_2": {
        "archive": "trinity-guardian-stage2-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_guardian_listing_request_payload.py",
        "files": [
            "scripts/build_guardian_listing_request_payload.py",
            "scripts/gateway_payload_authorship.py",
            "scripts/agent_authorship_common.py",
            "scripts/guardian_gateway_contract.py",
            "scripts/oath_contracts.py",
            "scripts/guardian_identity_claims.py",
            "scripts/validate_gateway_payload.py",
            "api/guardian-listing-oath.v1.txt",
            "api/agent-issue-gateway-payload-schema.v1.json",
            "api/agent-submit-gateway.json",
            "api/gateway-builder-route-map.v1.json",
            "api/gateway-workflows.v1.json",
            "scripts/generate_agent_authorship_keypair.mjs",
        ],
    },
    "guardian_signed_echo": {
        "archive": "trinity-guardian-signed-echo-builder-bundle.tar.gz",
        "entrypoint": "scripts/build_guardian_echo_payload.py",
        "files": [
            "scripts/build_guardian_echo_payload.py",
            "scripts/gateway_payload_authorship.py",
            "scripts/agent_authorship_common.py",
            "scripts/guardian_gateway_contract.py",
            "scripts/oath_contracts.py",
            "scripts/validate_gateway_payload.py",
            "api/agent-issue-gateway-payload-schema.v1.json",
            "api/agent-submit-gateway.json",
            "api/gateway-builder-route-map.v1.json",
            "api/gateway-workflows.v1.json",
            "scripts/generate_agent_authorship_keypair.mjs",
        ],
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

    with tarfile.open(archive_path, "w:gz") as tar:
        for item in entries:
            tar.add(ROOT / item["path"], arcname=item["path"])

    archive_sha = sha256_file(archive_path)
    manifest = {
        "schema": "trinityaccord.formal-builder-bundle-manifest.v1",
        "bundle": name,
        "archive": archive_path.name,
        "archive_sha256": archive_sha,
        "archive_size_bytes": archive_path.stat().st_size,
        "entrypoint": spec["entrypoint"],
        "requires_full_repo_clone": False,
        "files": entries,
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
