#!/usr/bin/env python3
"""Build and validate fail-closed Bitcoin Core checkpoint manifests.

The checkpoint is persistence only. Bitcoin consensus validation is performed by
Bitcoin Core in the GitHub-hosted workflow.  A checkpoint may be restored only
after this module has validated its immutable manifest and every archive part.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_V1 = "trinity-accord.bitcoin-consensus-checkpoint.v1"
SCHEMA_V2 = "trinity-accord.bitcoin-consensus-checkpoint.v2"
SCHEMA = SCHEMA_V2
PROFILE = "github_hosted_pruned_full_node"
NETWORK = "main"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
TAG_RE = re.compile(r"^bitcoin-consensus-checkpoint-(\d{6})$")
ASSET_RE = re.compile(r"^bitcoin-datadir\.tar\.zst\.part-\d{4}$")


class CheckpointError(ValueError):
    pass


def sha256_file(path: os.PathLike[str] | str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_manifest(manifest: dict[str, Any]) -> None:
    common_required = {
        "schema",
        "profile",
        "network",
        "bitcoin_core_version",
        "bitcoin_core_archive_sha256",
        "assumevalid",
        "prune_mib",
        "clean_shutdown",
        "initialblockdownload",
        "height",
        "best_block_hash",
        "verification_progress",
        "workflow",
        "checkpoint",
        "previous_checkpoint",
        "assets",
    }
    schema = manifest.get("schema")
    _require(schema in {SCHEMA_V1, SCHEMA_V2}, "unexpected checkpoint schema")
    required = set(common_required)
    if schema == SCHEMA_V2:
        required.update({"state_source_checkpoint", "quarantined_checkpoints"})
    _require(set(manifest) == required, f"manifest fields do not match the {schema.rsplit('.', 1)[-1]} schema")
    _require(manifest["profile"] == PROFILE, "unexpected verification profile")
    _require(manifest["network"] == NETWORK, "checkpoint is not Bitcoin mainnet")
    _require(
        isinstance(manifest["bitcoin_core_version"], str)
        and re.fullmatch(r"\d+\.\d+(?:\.\d+)?", manifest["bitcoin_core_version"]),
        "invalid Bitcoin Core version",
    )
    _require(
        isinstance(manifest["bitcoin_core_archive_sha256"], str)
        and bool(HEX64.fullmatch(manifest["bitcoin_core_archive_sha256"])),
        "invalid Bitcoin Core archive SHA-256",
    )
    _require(str(manifest["assumevalid"]) == "0", "assumevalid must be 0")
    _require(_is_int(manifest["prune_mib"]) and manifest["prune_mib"] >= 550, "prune_mib must be >= 550")
    _require(manifest["clean_shutdown"] is True, "checkpoint must come from a clean Bitcoin Core shutdown")
    _require(isinstance(manifest["initialblockdownload"], bool), "initialblockdownload must be boolean")
    _require(_is_int(manifest["height"]) and manifest["height"] >= 0, "height must be a non-negative integer")
    _require(
        isinstance(manifest["best_block_hash"], str) and bool(HEX64.fullmatch(manifest["best_block_hash"])),
        "invalid best block hash",
    )
    progress = manifest["verification_progress"]
    _require(
        isinstance(progress, (int, float)) and not isinstance(progress, bool) and 0.0 <= float(progress) <= 1.0,
        "verification_progress must be in [0, 1]",
    )

    workflow = manifest["workflow"]
    _require(isinstance(workflow, dict), "workflow must be an object")
    _require(set(workflow) == {"repository", "run_id", "run_attempt", "sha"}, "invalid workflow fields")
    _require(
        isinstance(workflow["repository"], str) and workflow["repository"].count("/") == 1,
        "invalid workflow repository",
    )
    _require(str(workflow["run_id"]).isdigit() and int(workflow["run_id"]) > 0, "invalid workflow run_id")
    _require(str(workflow["run_attempt"]).isdigit() and int(workflow["run_attempt"]) > 0, "invalid run_attempt")
    _require(isinstance(workflow["sha"], str) and bool(HEX40.fullmatch(workflow["sha"])), "invalid workflow SHA")

    checkpoint = manifest["checkpoint"]
    _require(isinstance(checkpoint, dict), "checkpoint must be an object")
    _require(set(checkpoint) == {"sequence", "tag", "created_at"}, "invalid checkpoint fields")
    _require(_is_int(checkpoint["sequence"]) and checkpoint["sequence"] >= 1, "invalid checkpoint sequence")
    match = TAG_RE.fullmatch(str(checkpoint["tag"]))
    _require(match is not None, "invalid checkpoint tag")
    _require(int(match.group(1)) == checkpoint["sequence"], "checkpoint tag/sequence mismatch")
    _require(
        isinstance(checkpoint["created_at"], str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", checkpoint["created_at"]),
        "created_at must be UTC RFC3339 without fractional seconds",
    )

    previous = manifest["previous_checkpoint"]
    if checkpoint["sequence"] == 1:
        _require(previous is None, "first checkpoint must not have a predecessor")
    else:
        _require(isinstance(previous, dict), "successor checkpoint requires a predecessor")
        _require(set(previous) == {"tag", "manifest_sha256"}, "invalid predecessor fields")
        previous_match = TAG_RE.fullmatch(str(previous["tag"]))
        _require(previous_match is not None, "invalid predecessor tag")
        _require(int(previous_match.group(1)) == checkpoint["sequence"] - 1, "predecessor must be the prior sequence")
        _require(
            isinstance(previous["manifest_sha256"], str)
            and bool(HEX64.fullmatch(previous["manifest_sha256"])),
            "invalid predecessor manifest SHA-256",
        )

    if schema == SCHEMA_V2:
        state_source = manifest["state_source_checkpoint"]
        quarantined = manifest["quarantined_checkpoints"]
        _require(isinstance(quarantined, list), "quarantined_checkpoints must be a list")
        if checkpoint["sequence"] == 1:
            _require(state_source is None, "first checkpoint must not have a state source")
            _require(not quarantined, "first checkpoint cannot quarantine predecessors")
        else:
            _require(isinstance(state_source, dict), "successor requires a state source")
            _require(set(state_source) == {"tag", "manifest_sha256"}, "invalid state source fields")
            source_match = TAG_RE.fullmatch(str(state_source["tag"]))
            _require(source_match is not None, "invalid state source tag")
            source_sequence = int(source_match.group(1))
            _require(source_sequence < checkpoint["sequence"], "state source must precede the checkpoint")
            _require(
                isinstance(state_source["manifest_sha256"], str)
                and bool(HEX64.fullmatch(state_source["manifest_sha256"])),
                "invalid state source manifest SHA-256",
            )

            if not quarantined:
                _require(state_source == previous, "normal successor must restore its immediate predecessor")
            else:
                expected_sequence = source_sequence + 1
                seen_tags: set[str] = set()
                for item in quarantined:
                    _require(isinstance(item, dict), "quarantined checkpoint entry must be an object")
                    _require(
                        set(item) == {"tag", "manifest_sha256", "reason"},
                        "invalid quarantined checkpoint fields",
                    )
                    quarantine_match = TAG_RE.fullmatch(str(item["tag"]))
                    _require(quarantine_match is not None, "invalid quarantined checkpoint tag")
                    _require(
                        int(quarantine_match.group(1)) == expected_sequence,
                        "quarantined checkpoints must form a contiguous sequence after the state source",
                    )
                    _require(item["tag"] not in seen_tags, "duplicate quarantined checkpoint tag")
                    _require(
                        isinstance(item["manifest_sha256"], str)
                        and bool(HEX64.fullmatch(item["manifest_sha256"])),
                        "invalid quarantined checkpoint manifest SHA-256",
                    )
                    _require(item["reason"] == "remote_restore_failed", "unsupported quarantine reason")
                    seen_tags.add(item["tag"])
                    expected_sequence += 1
                _require(
                    quarantined[-1]["tag"] == previous["tag"]
                    and quarantined[-1]["manifest_sha256"] == previous["manifest_sha256"],
                    "quarantine chain must end at the immediate published predecessor",
                )

    assets = manifest["assets"]
    _require(isinstance(assets, list) and assets, "checkpoint must have at least one archive asset")
    names: list[str] = []
    for asset in assets:
        _require(isinstance(asset, dict), "asset entry must be an object")
        _require(set(asset) == {"name", "size", "sha256"}, "invalid asset fields")
        _require(isinstance(asset["name"], str) and bool(ASSET_RE.fullmatch(asset["name"])), "invalid asset name")
        _require(_is_int(asset["size"]) and asset["size"] > 0, "asset size must be positive")
        _require(isinstance(asset["sha256"], str) and bool(HEX64.fullmatch(asset["sha256"])), "invalid asset SHA-256")
        names.append(asset["name"])
    _require(len(names) == len(set(names)), "duplicate archive asset name")
    _require(names == sorted(names), "archive assets must be lexicographically ordered")


def load_manifest(path: os.PathLike[str] | str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    _require(isinstance(data, dict), "manifest root must be an object")
    validate_manifest(data)
    return data


def verify_asset(manifest: dict[str, Any], asset_name: str, path: os.PathLike[str] | str) -> None:
    matches = [item for item in manifest["assets"] if item["name"] == asset_name]
    _require(len(matches) == 1, f"asset {asset_name!r} not declared exactly once")
    expected = matches[0]
    actual_size = Path(path).stat().st_size
    _require(actual_size == expected["size"], f"asset size mismatch for {asset_name}")
    actual_sha = sha256_file(path)
    _require(actual_sha == expected["sha256"], f"asset SHA-256 mismatch for {asset_name}")


def read_catalog(path: os.PathLike[str] | str) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            _require(len(parts) == 3, f"invalid catalog line {lineno}")
            name, size_text, digest = parts
            _require(size_text.isdigit(), f"invalid catalog size on line {lineno}")
            assets.append({"name": name, "size": int(size_text), "sha256": digest})
    assets.sort(key=lambda item: item["name"])
    return assets


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    with open(args.chain_info, "r", encoding="utf-8") as handle:
        chain = json.load(handle)
    _require(isinstance(chain, dict), "chain-info root must be an object")
    _require("blocks" in chain and "bestblockhash" in chain, "chain-info is missing required fields")
    previous = None
    if args.sequence > 1:
        _require(bool(args.previous_tag) and bool(args.previous_manifest_sha256), "successor requires predecessor metadata")
        previous = {
            "tag": args.previous_tag,
            "manifest_sha256": args.previous_manifest_sha256,
        }
    else:
        _require(not args.previous_tag and not args.previous_manifest_sha256, "first checkpoint cannot have predecessor metadata")

    state_source = None
    quarantined: list[dict[str, Any]] = []
    if args.sequence > 1:
        source_tag = args.state_source_tag or args.previous_tag
        source_sha = args.state_source_manifest_sha256 or args.previous_manifest_sha256
        _require(bool(source_tag) and bool(source_sha), "successor requires state source metadata")
        state_source = {"tag": source_tag, "manifest_sha256": source_sha}
        quarantine_values = (
            args.quarantined_tag,
            args.quarantined_manifest_sha256,
            args.quarantine_reason,
        )
        if any(quarantine_values):
            _require(all(quarantine_values), "quarantine metadata must be supplied together")
            quarantined.append(
                {
                    "tag": args.quarantined_tag,
                    "manifest_sha256": args.quarantined_manifest_sha256,
                    "reason": args.quarantine_reason,
                }
            )
    else:
        _require(
            not any(
                (
                    args.state_source_tag,
                    args.state_source_manifest_sha256,
                    args.quarantined_tag,
                    args.quarantined_manifest_sha256,
                    args.quarantine_reason,
                )
            ),
            "first checkpoint cannot have recovery metadata",
        )

    manifest = {
        "schema": SCHEMA,
        "profile": PROFILE,
        "network": NETWORK,
        "bitcoin_core_version": args.bitcoin_core_version,
        "bitcoin_core_archive_sha256": args.bitcoin_core_archive_sha256,
        "assumevalid": "0",
        "prune_mib": args.prune_mib,
        "clean_shutdown": True,
        "initialblockdownload": bool(chain.get("initialblockdownload", True)),
        "height": int(chain["blocks"]),
        "best_block_hash": str(chain["bestblockhash"]),
        "verification_progress": float(chain.get("verificationprogress", 0.0)),
        "workflow": {
            "repository": args.repository,
            "run_id": str(args.run_id),
            "run_attempt": str(args.run_attempt),
            "sha": args.workflow_sha,
        },
        "checkpoint": {
            "sequence": args.sequence,
            "tag": f"bitcoin-consensus-checkpoint-{args.sequence:06d}",
            "created_at": args.created_at,
        },
        "previous_checkpoint": previous,
        "state_source_checkpoint": state_source,
        "quarantined_checkpoints": quarantined,
        "assets": read_catalog(args.catalog),
    }
    validate_manifest(manifest)
    return manifest


def write_canonical_json(data: Any, path: os.PathLike[str] | str) -> None:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    Path(path).write_text(payload, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-manifest")
    validate.add_argument("manifest")

    verify = sub.add_parser("verify-asset")
    verify.add_argument("manifest")
    verify.add_argument("asset_name")
    verify.add_argument("path")

    digest = sub.add_parser("manifest-sha256")
    digest.add_argument("manifest")

    build = sub.add_parser("build-manifest")
    build.add_argument("--catalog", required=True)
    build.add_argument("--chain-info", required=True)
    build.add_argument("--sequence", type=int, required=True)
    build.add_argument("--previous-tag")
    build.add_argument("--previous-manifest-sha256")
    build.add_argument("--state-source-tag")
    build.add_argument("--state-source-manifest-sha256")
    build.add_argument("--quarantined-tag")
    build.add_argument("--quarantined-manifest-sha256")
    build.add_argument("--quarantine-reason", choices=("remote_restore_failed",))
    build.add_argument("--bitcoin-core-version", required=True)
    build.add_argument("--bitcoin-core-archive-sha256", required=True)
    build.add_argument("--prune-mib", type=int, required=True)
    build.add_argument("--repository", required=True)
    build.add_argument("--run-id", required=True)
    build.add_argument("--run-attempt", required=True)
    build.add_argument("--workflow-sha", required=True)
    build.add_argument("--created-at", required=True)
    build.add_argument("--output", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "validate-manifest":
            load_manifest(args.manifest)
        elif args.command == "verify-asset":
            manifest = load_manifest(args.manifest)
            verify_asset(manifest, args.asset_name, args.path)
        elif args.command == "manifest-sha256":
            load_manifest(args.manifest)
            print(sha256_file(args.manifest))
        elif args.command == "build-manifest":
            write_canonical_json(build_manifest(args), args.output)
        else:
            raise AssertionError(args.command)
    except (CheckpointError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"checkpoint validation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
