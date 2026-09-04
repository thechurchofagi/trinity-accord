#!/usr/bin/env python3
"""Capture independently reproducible Ethereum Beacon finality witnesses.

The input is the immutable Polygon -> Ethereum settlement report.  For every
distinct execution block this collector requires two independently operated
Beacon API implementations to agree on the beacon block root, slot, embedded
execution block hash, finalized=true, and execution_optimistic=false.  It also
stores the canonical SSZ signed beacon block so Lodestar can recompute the
beacon root and the execution-payload binding offline.

This is deliberately not described as Bitcoin-style objective consensus proof:
Ethereum PoS finality retains a weak-subjectivity assumption.  The evidence does
remove ordinary explorer/RPC trust and preserves the exact consensus object.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import time
import urllib.request

GENESIS_TIME = 1606824023
SECONDS_PER_SLOT = 12
DEFAULT_PROVIDERS = (
    ("publicnode", "https://ethereum-beacon-api.publicnode.com"),
    ("chainsafe-lodestar", "https://lodestar-mainnet.chainsafe.io"),
)


def stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def get(url: str, accept: str = "application/json", timeout: int = 60, retries: int = 3) -> tuple[bytes, dict[str, str]]:
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"accept": accept, "user-agent": "trinity-accord-beacon-finality/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read(), {key.lower(): value for key, value in response.headers.items()}
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2**attempt)
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last!r}")


def execution_hash(block: dict) -> str:
    body = block["data"]["message"]["body"]
    payload = body.get("execution_payload") or body.get("executionPayload")
    if not payload:
        raise ValueError("beacon block has no execution payload")
    return str(payload.get("block_hash") or payload.get("blockHash") or "").lower()


def parse_providers(values: list[str]) -> list[tuple[str, str]]:
    if not values:
        return list(DEFAULT_PROVIDERS)
    out = []
    for raw in values:
        name, separator, url = raw.partition("=")
        if not separator or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name) or not url.startswith("https://"):
            raise ValueError("--provider must be name=https://endpoint")
        out.append((name, url.rstrip("/")))
    if len(out) < 2:
        raise ValueError("at least two independent Beacon providers are required")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--polygon-settlement", type=pathlib.Path, required=True)
    parser.add_argument("--base-derivation", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--provider", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    providers = parse_providers(args.provider)
    settlement_raw = args.polygon_settlement.read_bytes()
    settlement = json.loads(settlement_raw)
    if settlement.get("pass") is not True:
        raise SystemExit("Polygon settlement source is not PASS")

    expected: dict[int, dict] = {}
    source_counts = {"polygon_checkpoint_blocks": 0, "base_batch_frame_blocks": 0}

    def add_expected(value: dict, source: str) -> None:
        number = int(value["execution_block_number"])
        normalized = {
            "execution_block_number": number,
            "execution_block_hash": value["execution_block_hash"].lower(),
            "execution_block_timestamp": int(value["execution_block_timestamp"]),
            "sources": [source],
        }
        if number in expected:
            old = {key: expected[number][key] for key in ("execution_block_number", "execution_block_hash", "execution_block_timestamp")}
            new = {key: normalized[key] for key in old}
            if old != new:
                raise SystemExit(f"conflicting execution claim for block {number}")
            if source not in expected[number]["sources"]:
                expected[number]["sources"].append(source)
        else:
            expected[number] = normalized

    for checkpoint in settlement.get("checkpoints", []):
        number = int(checkpoint["ethereum_block_number"])
        add_expected({
            "execution_block_number": number,
            "execution_block_hash": checkpoint["ethereum_block_hash"].lower(),
            "execution_block_timestamp": int(checkpoint["ethereum_block_timestamp"]),
        }, "polygon_checkpoint")
        source_counts["polygon_checkpoint_blocks"] += 1
    if source_counts["polygon_checkpoint_blocks"] != 117:
        raise SystemExit(f"expected 117 Polygon checkpoint blocks, got {source_counts['polygon_checkpoint_blocks']}")

    base_raw = None
    if args.base_derivation:
        base_raw = args.base_derivation.read_bytes()
        base = json.loads(base_raw)
        if base.get("pass") is not True or base.get("summary", {}).get("records") != 61:
            raise SystemExit("Base derivation source is not PASS 61/61")
        base_root = args.base_derivation.parent
        seen_base = set()
        for record in base.get("records", []):
            for frame in record["derivation"]["channel_frames"]:
                proof_path = base_root / frame["l1_transaction_proof_file"]
                proof = json.loads(proof_path.read_text())
                number = int(proof["ethereum_block_number"])
                add_expected(
                    {
                        "execution_block_number": number,
                        "execution_block_hash": proof["ethereum_block_hash"],
                        "execution_block_timestamp": proof["ethereum_block_timestamp"],
                    },
                    "base_batch_frame",
                )
                seen_base.add(number)
        source_counts["base_batch_frame_blocks"] = len(seen_base)

    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    claims = []
    for position, (number, claim) in enumerate(sorted(expected.items()), 1):
        timestamp = claim["execution_block_timestamp"]
        if timestamp < GENESIS_TIME or (timestamp - GENESIS_TIME) % SECONDS_PER_SLOT:
            raise SystemExit(f"execution timestamp does not map exactly to a Beacon slot: block={number} timestamp={timestamp}")
        slot = (timestamp - GENESIS_TIME) // SECONDS_PER_SLOT
        claim_dir = root / "claims" / str(number)
        claim_dir.mkdir(parents=True, exist_ok=True)
        observations = []
        roots = set()
        selected_ssz = None
        selected_fork = None
        for name, endpoint in providers:
            provider_dir = claim_dir / name
            provider_dir.mkdir(parents=True, exist_ok=True)
            header_raw, _ = get(f"{endpoint}/eth/v1/beacon/headers/{slot}", timeout=args.timeout)
            block_raw, _ = get(f"{endpoint}/eth/v2/beacon/blocks/{slot}", timeout=args.timeout)
            header = json.loads(header_raw)
            block = json.loads(block_raw)
            header_slot = int(header["data"]["header"]["message"]["slot"])
            block_slot = int(block["data"]["message"]["slot"])
            root_hash = header["data"]["root"].lower()
            embedded_hash = execution_hash(block)
            if header_slot != slot or block_slot != slot:
                raise SystemExit(f"Beacon slot mismatch provider={name} expected={slot} header={header_slot} block={block_slot}")
            if header.get("finalized") is not True or block.get("finalized") is not True:
                raise SystemExit(f"provider did not mark historical block finalized: {name} slot={slot}")
            if header.get("execution_optimistic") is not False or block.get("execution_optimistic") is not False:
                raise SystemExit(f"provider returned execution_optimistic: {name} slot={slot}")
            if embedded_hash != claim["execution_block_hash"]:
                raise SystemExit(f"execution payload hash mismatch: {name} block={number}")
            (provider_dir / "header.json").write_bytes(header_raw)
            (provider_dir / "block.json").write_bytes(block_raw)
            observation = {
                "provider": name,
                "endpoint": endpoint,
                "beacon_root": root_hash,
                "header_sha256": sha256(header_raw),
                "block_json_sha256": sha256(block_raw),
                "finalized": True,
                "execution_optimistic": False,
                "execution_block_hash": embedded_hash,
            }
            observations.append(observation)
            roots.add(root_hash)
            if selected_ssz is None:
                try:
                    ssz_raw, ssz_headers = get(
                        f"{endpoint}/eth/v2/beacon/blocks/{slot}",
                        accept="application/octet-stream",
                        timeout=args.timeout,
                    )
                    if ssz_headers.get("content-type", "").split(";", 1)[0] != "application/octet-stream":
                        raise ValueError("provider ignored SSZ Accept header")
                    if ssz_headers.get("eth-consensus-finalized", "").lower() != "true":
                        raise ValueError("SSZ response is not marked finalized")
                    fork = ssz_headers.get("eth-consensus-version", "").lower()
                    if not fork:
                        raise ValueError("SSZ response has no Eth-Consensus-Version")
                    selected_ssz = ssz_raw
                    selected_fork = fork
                    (claim_dir / "signed-beacon-block.ssz").write_bytes(ssz_raw)
                    observation["ssz_sha256"] = sha256(ssz_raw)
                    observation["ssz_fork"] = fork
                except Exception as exc:
                    observation["ssz_unavailable"] = repr(exc)
        if len(roots) != 1:
            raise SystemExit(f"Beacon providers disagree on root: block={number} roots={sorted(roots)}")
        if selected_ssz is None or selected_fork is None:
            raise SystemExit(f"no provider supplied canonical SSZ: block={number}")
        row = {
            **claim,
            "beacon_slot": slot,
            "beacon_root": next(iter(roots)),
            "ssz_file": f"claims/{number}/signed-beacon-block.ssz",
            "ssz_sha256": sha256(selected_ssz),
            "ssz_fork": selected_fork,
            "provider_quorum": len(observations),
            "observations": observations,
        }
        (claim_dir / "claim.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
        claims.append(row)
        print(f"[BEACON FINALITY {position}/{len(expected)}] execution={number} slot={slot} root={row['beacon_root']} quorum={len(observations)}", flush=True)

    report = {
        "schema": "trinity-accord/chronicle-ethereum-beacon-finality/v1",
        "pass": True,
        "source_polygon_settlement_sha256": sha256(settlement_raw),
        "source_base_derivation_sha256": sha256(base_raw) if base_raw is not None else None,
        "claims": claims,
        "summary": {
            "execution_blocks": len(claims),
            **source_counts,
            "provider_quorum_per_block": len(providers),
            "ssz_objects": len(claims),
            "finalized_true": len(claims),
            "execution_optimistic_false": len(claims),
        },
        "assurance": {
            "execution_binding": "PASS_OFFLINE_SSZ_ROOT_RECOMPUTATION_REQUIRED",
            "beacon_finality": "PASS_TWO_INDEPENDENT_CONSENSUS_CLIENT_OBSERVATIONS",
            "weak_subjectivity": "Ethereum PoS finality is not Bitcoin-style objective proof. A verifier still needs a recent trusted weak-subjectivity checkpoint or independently synced consensus client.",
        },
    }
    (root / "ETHEREUM-BEACON-FINALITY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
