#!/usr/bin/env python3
"""Diagnose a single missing NFT timestamp using ERC-721/ERC-1155 probes."""
import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
INDEX = DIR / "index.json"
DIAGNOSIS_OUT = DIR / "single-token-timestamp-diagnosis.json"

# --- Constants ---
ERC165_SUPPORTS_INTERFACE_SELECTOR = "0x01ffc9a7"
ERC721_INTERFACE_ID = "80ac58cd"
ERC721_METADATA_INTERFACE_ID = "5b5e139f"
ERC1155_INTERFACE_ID = "d9b67a26"
ERC1155_METADATA_URI_INTERFACE_ID = "0e89341c"

SELECTOR_OWNER_OF = "0x6352211e"
SELECTOR_TOKEN_URI = "0xc87b56dd"
SELECTOR_ERC1155_URI = "0x0e89341c"

ERC721_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ERC1155_TRANSFER_SINGLE_TOPIC = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ERC1155_TRANSFER_BATCH_TOPIC = "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"

DEFAULT_CONTRACT = "0x019372bBee377109b8Eae66d7267f5C4EaAdBb79"
DEFAULT_TOKEN_ID = "85210329807936527805363210873332413577559846505703131855064182995898737885245"


DEFAULT_RPCS = [
    "https://ethereum-rpc.publicnode.com",
    "https://rpc.ankr.com/eth",
    "https://1rpc.io/eth",
    "https://eth.llamarpc.com",
]


def get_rpcs():
    # Check ETH_RPC_URLS first, then ETHEREUMMAINNET
    urls = os.environ.get("ETH_RPC_URLS", "") or os.environ.get("ETHEREUMMAINNET", "")
    if urls:
        return [u.strip() for u in urls.split(",") if u.strip()]
    return list(DEFAULT_RPCS)


def rpc_call(rpcs, method, params, retries=6, sleep_base=1.0):
    """Call ETH JSON-RPC with retries and exponential backoff."""
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    last_error = None
    for attempt in range(retries):
        url = rpcs[attempt % len(rpcs)]
        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "trinity-accord-diagnosis/1.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read())
            if "result" in data and data["result"] is not None:
                return data["result"]
            last_error = data.get("error") or data
        except Exception as e:
            last_error = repr(e)
        wait = sleep_base * (2 ** min(attempt, 4))
        print(f"  RPC retry {attempt + 1}/{retries} for {method}: {last_error}; sleeping {wait:.1f}s", file=sys.stderr)
        time.sleep(wait)
    return None


def eth_call(rpcs, to, data):
    return rpc_call(rpcs, "eth_call", [{"to": to, "data": data}, "latest"])


def pad_topic_int(value):
    """Pad an integer to 32 bytes with 0x prefix, for use in eth_getLogs topics."""
    return "0x" + hex(int(value))[2:].rjust(64, "0")


def pad_word_int(value):
    """Pad an integer to 32 bytes without 0x prefix, for use in eth_call calldata."""
    return hex(int(value))[2:].rjust(64, "0")


def supports_interface(rpcs, contract, interface_id_hex):
    data = ERC165_SUPPORTS_INTERFACE_SELECTOR + interface_id_hex.lower().ljust(64, "0")
    result = eth_call(rpcs, contract, data)
    if result is None:
        return None
    # The result is a 32-byte bool; last char '1' = true
    return result.endswith("1")


def compute_target_window(index, contract, token_id, default_start, latest):
    same = [x for x in index if x.get("contract", "").lower() == contract.lower()]
    same.sort(key=lambda x: int(x.get("token_id", "0")))

    target_int = int(token_id)
    prev_items = [x for x in same if int(x.get("token_id", "0")) < target_int and x.get("block")]
    next_items = [x for x in same if int(x.get("token_id", "0")) > target_int and x.get("block")]

    prev_block = prev_items[-1]["block"] if prev_items else None
    next_block = next_items[0]["block"] if next_items else None

    margin = 100000

    if prev_block and next_block:
        return max(default_start, prev_block - margin), min(latest, next_block + margin), "neighbor_bounded"
    if prev_block:
        return max(default_start, prev_block - margin), latest, "prev_bounded_to_latest"
    if next_block:
        return default_start, min(latest, next_block + margin), "start_to_next_bounded"
    return default_start, latest, "full_single_token"


def get_block_number(rpcs):
    result = rpc_call(rpcs, "eth_blockNumber", [])
    if result:
        return int(result, 16)
    return None


def get_logs_chunked(rpcs, address, topics, from_block, to_block, chunk_size=5000):
    """Get logs in chunks to avoid RPC limits."""
    all_logs = []
    start = from_block
    while start <= to_block:
        end = min(start + chunk_size - 1, to_block)
        params = {
            "fromBlock": hex(start),
            "toBlock": hex(end),
            "address": address,
            "topics": topics,
        }
        result = rpc_call(rpcs, "eth_getLogs", [params])
        if result and isinstance(result, list):
            all_logs.extend(result)
        start = end + 1
    return all_logs


def main():
    parser = argparse.ArgumentParser(description="Diagnose single NFT timestamp")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    parser.add_argument("--token-id", default=DEFAULT_TOKEN_ID)
    parser.add_argument("--start-block", type=int, default=18000000)
    parser.add_argument("--end-block", default="latest")
    parser.add_argument("--chunk", type=int, default=5000)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rpcs = get_rpcs()
    if not rpcs:
        print("No RPC endpoints available. Set ETH_RPC_URLS or ETHEREUMMAINNET env var.")
        return 1

    index = json.loads(INDEX.read_text(encoding="utf-8"))

    # Get latest block
    latest = get_block_number(rpcs)
    if latest is None:
        print("Failed to get latest block number")
        return 1

    end_block = latest if args.end_block == "latest" else int(args.end_block)

    # Compute window
    start_block, end_block, mode = compute_target_window(
        index, args.contract, args.token_id, args.start_block, end_block
    )
    print(f"Scan window: {start_block} - {end_block} (mode: {mode})")

    # ERC165 interface probes
    print("Probing ERC165 interfaces...")
    interface_probes = {
        "erc721": supports_interface(rpcs, args.contract, ERC721_INTERFACE_ID),
        "erc721_metadata": supports_interface(rpcs, args.contract, ERC721_METADATA_INTERFACE_ID),
        "erc1155": supports_interface(rpcs, args.contract, ERC1155_INTERFACE_ID),
        "erc1155_metadata_uri": supports_interface(rpcs, args.contract, ERC1155_METADATA_URI_INTERFACE_ID),
    }
    print(f"  Interface probes: {interface_probes}")

    # Token existence probes
    token_existence_probes = []

    # ownerOf
    print("Probing ownerOf...")
    owner_data = SELECTOR_OWNER_OF + pad_word_int(args.token_id)
    owner_result = eth_call(rpcs, args.contract, owner_data)
    token_existence_probes.append({
        "method": "ownerOf",
        "selector": SELECTOR_OWNER_OF,
        "raw_result": owner_result,
        "decoded": "non_zero_address" if owner_result and owner_result != "0x" + "0" * 64 else "zero_or_empty"
    })

    # tokenURI
    print("Probing tokenURI...")
    uri_data = SELECTOR_TOKEN_URI + pad_word_int(args.token_id)
    uri_result = eth_call(rpcs, args.contract, uri_data)
    token_existence_probes.append({
        "method": "tokenURI",
        "selector": SELECTOR_TOKEN_URI,
        "raw_result": uri_result,
        "decoded": "has_uri" if uri_result and uri_result != "0x" and len(uri_result) > 2 else "empty"
    })

    # ERC1155 uri
    print("Probing ERC1155 uri...")
    erc1155_uri_data = SELECTOR_ERC1155_URI + pad_word_int(args.token_id)
    erc1155_uri_result = eth_call(rpcs, args.contract, erc1155_uri_data)
    token_existence_probes.append({
        "method": "erc1155_uri",
        "selector": SELECTOR_ERC1155_URI,
        "raw_result": erc1155_uri_result,
        "decoded": "has_uri" if erc1155_uri_result and erc1155_uri_result != "0x" and len(erc1155_uri_result) > 2 else "empty"
    })

    # Event log searches
    event_attempts = []
    recovered = False
    recovered_record = None
    token_id_padded = pad_topic_int(args.token_id)
    token_id_hex = pad_word_int(args.token_id)  # without 0x, for data field comparison

    # ERC721 Transfer from zero (mint)
    print("Searching ERC721 Transfer from zero (mint)...")
    topics_mint = [ERC721_TRANSFER_TOPIC, ZERO_TOPIC, None, token_id_padded]
    logs_mint = get_logs_chunked(rpcs, args.contract, topics_mint, start_block, end_block, args.chunk)
    event_attempts.append({
        "method": "erc721_transfer_from_zero_topic3",
        "log_count": len(logs_mint),
        "first_log": logs_mint[0] if logs_mint else None
    })
    if logs_mint:
        log = logs_mint[0]
        recovered = True
        recovered_record = {
            "tx_hash": log.get("transactionHash"),
            "block": int(log.get("blockNumber", "0x0"), 16),
            "log_index": int(log.get("logIndex", "0x0"), 16),
            "method": "erc721_transfer_from_zero_topic3",
            "status": "mint"
        }
        print(f"  RECOVERED via erc721_transfer_from_zero_topic3: block {recovered_record['block']}")

    # ERC721 any Transfer (fallback)
    if not recovered:
        print("Searching ERC721 any Transfer...")
        topics_any = [ERC721_TRANSFER_TOPIC, None, None, token_id_padded]
        logs_any = get_logs_chunked(rpcs, args.contract, topics_any, start_block, end_block, args.chunk)
        event_attempts.append({
            "method": "erc721_transfer_any_topic3",
            "log_count": len(logs_any),
            "first_log": logs_any[0] if logs_any else None
        })
        if logs_any:
            log = logs_any[0]
            from_addr = log.get("topics", [""])[1] if len(log.get("topics", [])) > 1 else ""
            is_mint = from_addr == ZERO_TOPIC
            recovered = True
            recovered_record = {
                "tx_hash": log.get("transactionHash"),
                "block": int(log.get("blockNumber", "0x0"), 16),
                "log_index": int(log.get("logIndex", "0x0"), 16),
                "method": "erc721_transfer_any_topic3",
                "status": "mint" if is_mint else "first_transfer_not_zero_mint"
            }
            print(f"  RECOVERED via erc721_transfer_any_topic3: block {recovered_record['block']}")

    # ERC1155 TransferSingle from zero
    if not recovered:
        print("Searching ERC1155 TransferSingle from zero...")
        topics_single = [ERC1155_TRANSFER_SINGLE_TOPIC, None, ZERO_TOPIC]
        logs_single = get_logs_chunked(rpcs, args.contract, topics_single, start_block, end_block, args.chunk)
        # Filter locally for matching id
        matched_single = []
        for log in logs_single:
            data = log.get("data", "0x")
            if len(data) >= 66:  # 0x + 64 hex chars minimum
                word0 = data[2:66]
                if word0 == token_id_hex:
                    matched_single.append(log)
        event_attempts.append({
            "method": "erc1155_transfer_single_from_zero",
            "log_count": len(logs_single),
            "matched_count": len(matched_single),
            "first_log": matched_single[0] if matched_single else None
        })
        if matched_single:
            log = matched_single[0]
            recovered = True
            recovered_record = {
                "tx_hash": log.get("transactionHash"),
                "block": int(log.get("blockNumber", "0x0"), 16),
                "log_index": int(log.get("logIndex", "0x0"), 16),
                "method": "erc1155_transfer_single_from_zero",
                "status": "mint"
            }
            print(f"  RECOVERED via erc1155_transfer_single_from_zero: block {recovered_record['block']}")

    # ERC1155 TransferBatch from zero
    if not recovered:
        print("Searching ERC1155 TransferBatch from zero...")
        topics_batch = [ERC1155_TRANSFER_BATCH_TOPIC, None, ZERO_TOPIC]
        logs_batch = get_logs_chunked(rpcs, args.contract, topics_batch, start_block, end_block, args.chunk)
        matched_batch = []
        for log in logs_batch:
            data = log.get("data", "0x")
            # TransferBatch data: offset, length, ids[], values[]
            # Check if our token_id appears in ids array
            if token_id_hex in data:
                matched_batch.append(log)
        event_attempts.append({
            "method": "erc1155_transfer_batch_from_zero",
            "log_count": len(logs_batch),
            "matched_count": len(matched_batch),
            "first_log": matched_batch[0] if matched_batch else None
        })
        if matched_batch:
            log = matched_batch[0]
            recovered = True
            recovered_record = {
                "tx_hash": log.get("transactionHash"),
                "block": int(log.get("blockNumber", "0x0"), 16),
                "log_index": int(log.get("logIndex", "0x0"), 16),
                "method": "erc1155_transfer_batch_from_zero",
                "status": "mint"
            }
            print(f"  RECOVERED via erc1155_transfer_batch_from_zero: block {recovered_record['block']}")

    # If recovered, fetch block timestamp and populate recovered_record
    if recovered and recovered_record:
        from datetime import datetime, timezone
        block_data = rpc_call(rpcs, "eth_getBlockByNumber", [hex(recovered_record["block"]), False])
        if block_data and "timestamp" in block_data:
            ts = int(block_data["timestamp"], 16)
            recovered_record["timestamp"] = ts
            recovered_record["datetime"] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"  Block timestamp: {ts} ({recovered_record['datetime']})")

    # Determine final status
    if recovered:
        final_status = "recovered"
        if recovered_record and recovered_record.get("status") != "mint":
            final_status = recovered_record["status"]
    else:
        # Check if token exists
        exists = False
        for probe in token_existence_probes:
            if probe["decoded"] in ("non_zero_address", "has_uri"):
                exists = True
                break
        final_status = "token_exists_no_standard_transfer_log_found" if exists else "metadata_mirror_only_or_unconfirmed_onchain_token"

    print(f"Final status: {final_status}")

    # Build report
    report = {
        "schema": "trinityaccord.single-token-timestamp-diagnosis.v1",
        "contract": args.contract,
        "token_id": args.token_id,
        "scan_window": {
            "start_block": start_block,
            "end_block": end_block,
            "mode": mode
        },
        "recovered": recovered,
        "recovered_record": recovered_record,
        "interface_probes": interface_probes,
        "token_existence_probes": token_existence_probes,
        "event_attempts": event_attempts,
        "final_status": final_status,
        "boundary": [
            "Recovered timestamp, if present, is an Ethereum event block timestamp.",
            "Token existence probes do not prove historical metadata truth.",
            "If no standard event is found, no timestamp is fabricated."
        ]
    }

    DIAGNOSIS_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Diagnosis written to {DIAGNOSIS_OUT}")

    # Apply logic
    if args.apply and recovered and recovered_record:
        print("Applying recovered timestamp...")
        # Update eth-mint-timestamps.json
        ts_path = DIR / "eth-mint-timestamps.json"
        ts_data = json.loads(ts_path.read_text(encoding="utf-8"))
        for entry in ts_data:
            if (entry.get("contract", "").lower() == args.contract.lower()
                    and str(entry.get("token_id", "")) == args.token_id):
                from datetime import datetime, timezone
                entry["block"] = recovered_record["block"]
                entry["tx_hash"] = recovered_record["tx_hash"]
                entry["log_index"] = recovered_record["log_index"]
                entry["status"] = recovered_record["status"]
                entry["method"] = recovered_record["method"]
                # Get timestamp from block (use RPC)
                block_data = rpc_call(rpcs, "eth_getBlockByNumber", [hex(recovered_record["block"]), False])
                if block_data and "timestamp" in block_data:
                    ts = int(block_data["timestamp"], 16)
                    entry["timestamp"] = ts
                    entry["datetime"] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                break
        ts_path.write_text(json.dumps(ts_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Update index.json
        idx_data = json.loads(INDEX.read_text(encoding="utf-8"))
        for entry in idx_data:
            if (entry.get("contract", "").lower() == args.contract.lower()
                    and str(entry.get("token_id", "")) == args.token_id):
                entry["block"] = recovered_record["block"]
                entry["timestamp"] = recovered_record.get("timestamp")
                entry["datetime"] = recovered_record.get("datetime")
                entry["timestamp_status"] = recovered_record["status"]
                entry["timestamp_method"] = recovered_record["method"]
                break
        INDEX.write_text(json.dumps(idx_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Update missing-timestamps.json
        missing_path = DIR / "missing-timestamps.json"
        if missing_path.exists():
            missing = json.loads(missing_path.read_text(encoding="utf-8"))
            missing = [m for m in missing if not (
                m.get("contract", "").lower() == args.contract.lower()
                and str(m.get("token_id", "")) == args.token_id
            )]
            missing_path.write_text(json.dumps(missing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        print("Applied. Timestamps should now be 175/175.")

    elif args.apply and not recovered:
        print("Not recovered. Updating missing-timestamps.json with diagnostic status...")
        missing_path = DIR / "missing-timestamps.json"
        if missing_path.exists():
            missing = json.loads(missing_path.read_text(encoding="utf-8"))
            for m in missing:
                if (m.get("contract", "").lower() == args.contract.lower()
                        and str(m.get("token_id", "")) == args.token_id):
                    m["diagnostic_status"] = final_status
                    m["diagnostic_report"] = str(DIAGNOSIS_OUT.relative_to(ROOT))
                    break
            missing_path.write_text(json.dumps(missing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
