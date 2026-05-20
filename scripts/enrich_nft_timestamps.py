#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ERC721_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ERC1155_TRANSFER_SINGLE_TOPIC = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ERC1155_TRANSFER_BATCH_TOPIC = "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"

DEFAULT_RPCS = [
    "https://ethereum-rpc.publicnode.com",
    "https://rpc.ankr.com/eth",
    "https://1rpc.io/eth",
    "https://eth.llamarpc.com",
]

def normalize_address(addr: str) -> str:
    return addr.lower()

def pad_topic_int(value: str | int) -> str:
    return "0x" + hex(int(value))[2:].rjust(64, "0")

def hex_to_int(x: str | None):
    if not x or x == "0x":
        return None
    return int(x, 16)

def utc_iso(timestamp: int | None) -> str | None:
    if timestamp is None:
        return None
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def rpc_call(rpcs, method, params, retries=6, sleep_base=1.0):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last_error = None

    for attempt in range(retries):
        url = rpcs[attempt % len(rpcs)]
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "trinity-accord-nft-timestamp-enricher/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read())
            if "result" in data and data["result"] is not None:
                return data["result"]
            last_error = data.get("error") or data
        except Exception as e:
            last_error = repr(e)

        wait = sleep_base * (2 ** min(attempt, 4))
        print(f"RPC retry {attempt + 1}/{retries} for {method}: {last_error}; sleeping {wait:.1f}s", file=sys.stderr)
        time.sleep(wait)

    raise RuntimeError(f"RPC failed for {method}: {last_error}")

def get_logs(rpcs, address, topics, start_block, end_block):
    return rpc_call(rpcs, "eth_getLogs", [{
        "address": address,
        "fromBlock": hex(start_block),
        "toBlock": hex(end_block),
        "topics": topics,
    }])

def get_block_timestamp(rpcs, block_number, cache):
    if block_number in cache:
        return cache[block_number]
    block = rpc_call(rpcs, "eth_getBlockByNumber", [hex(block_number), False])
    ts = hex_to_int(block.get("timestamp")) if block else None
    cache[block_number] = ts
    return ts

def decode_words(data_hex: str):
    if not data_hex or data_hex == "0x":
        return []
    raw = data_hex[2:]
    if len(raw) % 64 != 0:
        return []
    return [int(raw[i:i+64], 16) for i in range(0, len(raw), 64)]

def decode_erc1155_transfer_single(data_hex: str):
    words = decode_words(data_hex)
    if len(words) < 2:
        return None
    return {"id": words[0], "value": words[1]}

def decode_dynamic_uint_arrays(data_hex: str):
    """
    Decode ABI payload for TransferBatch ids[] and values[].
    data layout:
      word0 offset_to_ids
      word1 offset_to_values
      ids_offset: length, ids...
      values_offset: length, values...
    """
    words = decode_words(data_hex)
    if len(words) < 4:
        return None

    ids_offset_words = words[0] // 32
    vals_offset_words = words[1] // 32

    if ids_offset_words >= len(words) or vals_offset_words >= len(words):
        return None

    ids_len = words[ids_offset_words]
    vals_len = words[vals_offset_words]

    ids_start = ids_offset_words + 1
    vals_start = vals_offset_words + 1

    ids = words[ids_start:ids_start + ids_len]
    vals = words[vals_start:vals_start + vals_len]

    if len(ids) != ids_len or len(vals) != vals_len:
        return None

    return {"ids": ids, "values": vals}

def flatten_token_index(token_index):
    out = []
    for contract, tokens in token_index.items():
        if isinstance(tokens, dict):
            token_ids = list(tokens.keys())
        else:
            token_ids = [str(x) for x in tokens]
        for tid in token_ids:
            out.append({
                "contract": contract,
                "contract_lc": contract.lower(),
                "token_id": str(tid),
            })
    return out

def contract_groups(flat_tokens):
    groups = {}
    for item in flat_tokens:
        groups.setdefault(item["contract"], set()).add(item["token_id"])
    return groups

def earliest(existing, candidate):
    if candidate is None:
        return existing
    if existing is None:
        return candidate
    if candidate["block"] < existing["block"]:
        return candidate
    return existing

def log_to_record(rpcs, log, status, method, block_cache, extra=None):
    block = int(log["blockNumber"], 16)
    ts = get_block_timestamp(rpcs, block, block_cache)
    out = {
        "block": block,
        "timestamp": ts,
        "datetime": utc_iso(ts),
        "tx_hash": log.get("transactionHash"),
        "log_index": int(log.get("logIndex", "0x0"), 16),
        "status": status,
        "method": method,
    }
    if extra:
        out.update(extra)
    return out

def find_erc721_mints(rpcs, contract, token_ids, start_block, end_block, chunk, block_cache):
    # ERC-721: tokenId is in topics[3], not in data
    results = {}
    total = len(token_ids)
    print(f"  ERC721 precise mint by topic3: {total} tokens")
    for i, tid in enumerate(sorted(token_ids, key=lambda x: int(x))):
        token_topic = pad_topic_int(tid)
        found = None
        cur = start_block
        while cur <= end_block:
            to_block = min(cur + chunk - 1, end_block)
            logs = get_logs(rpcs, contract, [ERC721_TRANSFER_TOPIC, ZERO_TOPIC, None, token_topic], cur, to_block)
            for lg in logs:
                found = earliest(found, log_to_record(rpcs, lg, "mint", "erc721_transfer_from_zero_topic3", block_cache))
            cur = to_block + 1
            if found:
                break
        if found:
            results[tid] = found
        if (i + 1) % 5 == 0 or (i + 1) == total:
            print(f"    [progress] ERC721 precise: {i + 1}/{total} checked, {len(results)} found", flush=True)
    return results

def find_erc721_first_transfers(rpcs, contract, missing_token_ids, start_block, end_block, chunk, block_cache):
    results = {}
    total = len(missing_token_ids)
    print(f"  ERC721 first-transfer fallback by topic3: {total} tokens")
    for i, tid in enumerate(sorted(missing_token_ids, key=lambda x: int(x))):
        token_topic = pad_topic_int(tid)
        found = None
        cur = start_block
        while cur <= end_block:
            to_block = min(cur + chunk - 1, end_block)
            logs = get_logs(rpcs, contract, [ERC721_TRANSFER_TOPIC, None, None, token_topic], cur, to_block)
            for lg in logs:
                topics = lg.get("topics", [])
                from_topic = topics[1].lower() if len(topics) > 1 else None
                status = "mint" if from_topic == ZERO_TOPIC else "first_transfer_not_zero_mint"
                found = earliest(found, log_to_record(rpcs, lg, status, "erc721_transfer_any_topic3", block_cache))
            cur = to_block + 1
            if found:
                break
        if found:
            results[tid] = found
        if (i + 1) % 5 == 0 or (i + 1) == total:
            print(f"    [progress] ERC721 fallback: {i + 1}/{total} checked, {len(results)} found", flush=True)
    return results

def find_erc1155_single_mints(rpcs, contract, token_ids, start_block, end_block, chunk, block_cache):
    results = {}
    target = set(str(x) for x in token_ids)
    total_chunks = max(1, (end_block - start_block) // chunk + 1)
    print(f"  ERC1155 TransferSingle from zero scan ({total_chunks} chunks)")
    cur = start_block
    scanned = 0
    while cur <= end_block:
        to_block = min(cur + chunk - 1, end_block)
        logs = get_logs(rpcs, contract, [ERC1155_TRANSFER_SINGLE_TOPIC, None, ZERO_TOPIC], cur, to_block)
        for lg in logs:
            decoded = decode_erc1155_transfer_single(lg.get("data", "0x"))
            if not decoded:
                continue
            tid = str(decoded["id"])
            if tid not in target:
                continue
            rec = log_to_record(
                rpcs, lg, "mint", "erc1155_transfer_single_from_zero", block_cache,
                {"value": decoded["value"]},
            )
            results[tid] = earliest(results.get(tid), rec)
        scanned += 1
        if scanned % 10 == 0 or to_block >= end_block:
            pct = min(100, int(scanned * 100 / total_chunks))
            print(f"    [progress] ERC1155 single: block {to_block:,}/{end_block:,} ({pct}%), {len(results)} found", flush=True)
        cur = to_block + 1
    return results

def find_erc1155_batch_mints(rpcs, contract, token_ids, start_block, end_block, chunk, block_cache):
    results = {}
    target = set(str(x) for x in token_ids)
    total_chunks = max(1, (end_block - start_block) // chunk + 1)
    print(f"  ERC1155 TransferBatch from zero scan ({total_chunks} chunks)")
    cur = start_block
    scanned = 0
    while cur <= end_block:
        to_block = min(cur + chunk - 1, end_block)
        logs = get_logs(rpcs, contract, [ERC1155_TRANSFER_BATCH_TOPIC, None, ZERO_TOPIC], cur, to_block)
        for lg in logs:
            decoded = decode_dynamic_uint_arrays(lg.get("data", "0x"))
            if not decoded:
                continue
            ids = decoded["ids"]
            vals = decoded["values"]
            for idx, token_id_int in enumerate(ids):
                tid = str(token_id_int)
                if tid not in target:
                    continue
                value = vals[idx] if idx < len(vals) else None
                rec = log_to_record(
                    rpcs, lg, "mint", "erc1155_transfer_batch_from_zero", block_cache,
                    {"value": value},
                )
                results[tid] = earliest(results.get(tid), rec)
        scanned += 1
        if scanned % 10 == 0 or to_block >= end_block:
            pct = min(100, int(scanned * 100 / total_chunks))
            print(f"    [progress] ERC1155 batch: block {to_block:,}/{end_block:,} ({pct}%), {len(results)} found", flush=True)
        cur = to_block + 1
    return results

def update_index(index_path, timestamp_entries):
    if not index_path.exists():
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    ts_map = {(x["contract"].lower(), x["token_id"]): x for x in timestamp_entries}
    for item in index:
        key = (item["contract"].lower(), item["token_id"])
        enriched = ts_map.get(key)
        if not enriched:
            continue
        item["block"] = enriched.get("block")
        item["timestamp"] = enriched.get("timestamp")
        item["datetime"] = enriched.get("datetime")
        item["timestamp_status"] = enriched.get("status")
        item["timestamp_method"] = enriched.get("method")
        if enriched.get("tx_hash"):
            item["mint_or_first_transfer_tx_hash"] = enriched.get("tx_hash")
    index.sort(key=lambda x: (x.get("timestamp") is None, x.get("timestamp") or 10**18, x.get("contract", ""), x.get("token_id", "")))
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-index", default="token_index.json")
    parser.add_argument("--output-dir", default="nft-text-descriptions")
    parser.add_argument("--start-block", type=int, default=int(os.getenv("ETH_START_BLOCK", "18000000")))
    parser.add_argument("--end-block", default=os.getenv("ETH_END_BLOCK", "latest"))
    parser.add_argument("--chunk", type=int, default=int(os.getenv("ETH_LOG_CHUNK", "50000")))
    parser.add_argument("--rpc", action="append", default=[])
    args = parser.parse_args()

    rpcs = args.rpc or [x.strip() for x in os.getenv("ETH_RPC_URLS", "").split(",") if x.strip()] or DEFAULT_RPCS

    token_index_path = ROOT / args.token_index
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    token_index = json.loads(token_index_path.read_text(encoding="utf-8"))
    flat = flatten_token_index(token_index)
    groups = contract_groups(flat)

    latest_hex = rpc_call(rpcs, "eth_blockNumber", [])
    latest = int(latest_hex, 16)
    end_block = latest if args.end_block == "latest" else int(args.end_block)

    print(f"Latest block: {latest:,}")
    print(f"Scan range: {args.start_block:,} → {end_block:,}")
    print(f"Contracts: {len(groups)}; tokens: {len(flat)}")

    block_cache = {}
    results = {}
    diagnostics = []
    run_start = time.time()

    for contract, token_ids in groups.items():
        elapsed = int(time.time() - run_start)
        print(f"\n=== {contract} ({len(token_ids)} tokens) | elapsed: {elapsed // 60}m {elapsed % 60}s ===", flush=True)
        found = {}

        try:
            found.update(find_erc721_mints(rpcs, contract, token_ids, args.start_block, end_block, args.chunk, block_cache))
        except Exception as e:
            diagnostics.append({"contract": contract, "stage": "erc721_mint", "error": repr(e)})
            print(f"  ERC721 mint stage failed: {e}", file=sys.stderr)

        elapsed = int(time.time() - run_start)
        print(f"  [checkpoint] after ERC721 mint: {len(found)} found | elapsed: {elapsed // 60}m {elapsed % 60}s", flush=True)

        missing = set(token_ids) - set(found)
        try:
            single = find_erc1155_single_mints(rpcs, contract, missing, args.start_block, end_block, args.chunk, block_cache)
            for tid, rec in single.items():
                found[tid] = earliest(found.get(tid), rec)
        except Exception as e:
            diagnostics.append({"contract": contract, "stage": "erc1155_single", "error": repr(e)})
            print(f"  ERC1155 single stage failed: {e}", file=sys.stderr)

        elapsed = int(time.time() - run_start)
        print(f"  [checkpoint] after ERC1155 single: {len(found)} found | elapsed: {elapsed // 60}m {elapsed % 60}s", flush=True)

        missing = set(token_ids) - set(found)
        try:
            batch = find_erc1155_batch_mints(rpcs, contract, missing, args.start_block, end_block, args.chunk, block_cache)
            for tid, rec in batch.items():
                found[tid] = earliest(found.get(tid), rec)
        except Exception as e:
            diagnostics.append({"contract": contract, "stage": "erc1155_batch", "error": repr(e)})
            print(f"  ERC1155 batch stage failed: {e}", file=sys.stderr)

        elapsed = int(time.time() - run_start)
        print(f"  [checkpoint] after ERC1155 batch: {len(found)} found | elapsed: {elapsed // 60}m {elapsed % 60}s", flush=True)

        missing = set(token_ids) - set(found)
        try:
            fallback = find_erc721_first_transfers(rpcs, contract, missing, args.start_block, end_block, args.chunk, block_cache)
            for tid, rec in fallback.items():
                found[tid] = earliest(found.get(tid), rec)
        except Exception as e:
            diagnostics.append({"contract": contract, "stage": "erc721_first_transfer_fallback", "error": repr(e)})
            print(f"  ERC721 fallback stage failed: {e}", file=sys.stderr)

        for tid, rec in found.items():
            results[(contract.lower(), tid)] = {
                "contract": contract,
                "token_id": tid,
                **rec,
            }

        elapsed = int(time.time() - run_start)
        print(f"  Found {len(found)}/{len(token_ids)} | elapsed: {elapsed // 60}m {elapsed % 60}s", flush=True)

    timestamp_entries = []
    missing_entries = []

    for item in flat:
        key = (item["contract_lc"], item["token_id"])
        if key in results:
            timestamp_entries.append(results[key])
        else:
            missing_entries.append({
                "contract": item["contract"],
                "token_id": item["token_id"],
                "status": "missing",
                "checked_event_types": [
                    "erc721_transfer_from_zero_topic3",
                    "erc1155_transfer_single_from_zero",
                    "erc1155_transfer_batch_from_zero",
                    "erc721_transfer_any_topic3",
                ],
                "reason": "no matching event found in scanned range",
            })
            timestamp_entries.append({
                "contract": item["contract"],
                "token_id": item["token_id"],
                "block": None,
                "timestamp": None,
                "datetime": None,
                "status": "missing",
                "method": None,
            })

    timestamp_entries.sort(key=lambda x: (x.get("timestamp") is None, x.get("timestamp") or 10**18, x["contract"], x["token_id"]))

    (output_dir / "eth-mint-timestamps.json").write_text(
        json.dumps(timestamp_entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "missing-timestamps.json").write_text(
        json.dumps(missing_entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = {
        "schema": "trinityaccord.nft-timestamp-enrichment-report.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "start_block": args.start_block,
        "end_block": end_block,
        "total_tokens": len(flat),
        "timestamps_found": len(flat) - len(missing_entries),
        "timestamps_missing": len(missing_entries),
        "methods": {},
        "diagnostics": diagnostics,
        "boundaries": [
            "Timestamp is derived from matching Ethereum event block timestamp.",
            "ERC721 fallback first_transfer_not_zero_mint is not guaranteed to be mint.",
            "This does not verify NFT metadata content, Arweave CAR content, or historical description accuracy.",
        ],
    }
    for e in timestamp_entries:
        method = e.get("method") or "missing"
        report["methods"][method] = report["methods"].get(method, 0) + 1

    (output_dir / "timestamp-enrichment-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    update_index(output_dir / "index.json", timestamp_entries)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["timestamps_found"] == 0:
        print("ERROR: zero timestamps found; failing workflow.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
