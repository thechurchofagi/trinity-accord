#!/usr/bin/env python3
"""Audit the seven historical sidechain roots against on-chain ERC-1155 transfers.

This script does not attempt to recover unavailable IPFS payload bytes. It answers a
separate provenance question: were those seven token references created/delivered by
the Trinity Accord wallet itself, or were they unsolicited external assets observed
in the wallet?

Source of transfer truth: public Blockscout v2 APIs for Polygon and Base.
"""

from __future__ import annotations

import json
import pathlib
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCEPTIONS = ROOT / "evidence/chronicle-sidechain-historical-payload-exceptions.json"
OUT = ROOT / "artifacts/chronicle-sidechain-seven-root-provenance.json"

TARGET = "0xbc63566a41cbfdb9c266a5941cbe47894daa54a8"
ZERO = "0x0000000000000000000000000000000000000000"
OFFICIAL_PROJECT_CONTRACTS = {
    "0x019372bbee377109b8eae66d7267f5c4eaadbb79",
    "0x2b0c3cc5cd9652bef0caffc9c7699455725b9cc1",
    "0xf12815d22baf904a21b498a5df8e5d8529d2079e",
    "0x74f97bdefa07c2f99c876c2bd3b49628ed1c603",
}
API = {
    "polygon": "https://polygon.blockscout.com/api/v2",
    "base": "https://base.blockscout.com/api/v2",
}


def get_json(url: str, attempts: int = 5):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-seven-root-audit/1"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except Exception as exc:  # network/provider retry
            last = exc
            if i + 1 < attempts:
                time.sleep(min(2 ** i, 8))
    raise RuntimeError(f"GET failed after {attempts} attempts: {url}: {last}")


def addr(value):
    if isinstance(value, dict):
        value = value.get("hash")
    return (value or "").lower()


def instance_transfers(base: str, contract: str, token_id: str):
    url = f"{base}/tokens/{contract}/instances/{urllib.parse.quote(token_id, safe='')}/transfers"
    seen = set()
    items = []
    params = None
    for _ in range(100):
        page_url = url if not params else url + "?" + urllib.parse.urlencode(params)
        data = get_json(page_url)
        items.extend(data.get("items") or [])
        nxt = data.get("next_page_params")
        if not nxt:
            break
        marker = json.dumps(nxt, sort_keys=True)
        if marker in seen:
            raise RuntimeError(f"pagination loop for {contract}/{token_id}")
        seen.add(marker)
        params = nxt
    else:
        raise RuntimeError(f"pagination exceeded safety limit for {contract}/{token_id}")
    return items


def tx_sender(base: str, tx_hash: str):
    data = get_json(f"{base}/transactions/{tx_hash}")
    return addr(data.get("from")), data


def main():
    policy = json.loads(EXCEPTIONS.read_text())
    rows = policy.get("exceptions") or []
    if len(rows) != 7:
        raise SystemExit(f"expected exactly 7 declared historical roots, found {len(rows)}")

    results = []
    for row in rows:
        chain = row["chain"]
        contract = row["contract"].lower()
        token_id = str(row["token_id"])
        if chain not in API:
            raise SystemExit(f"unsupported chain {chain}")
        transfers = instance_transfers(API[chain], contract, token_id)
        inbound = [x for x in transfers if addr(x.get("to")) == TARGET]
        if not inbound:
            raise SystemExit(f"no inbound transfer to target for {chain}:{contract}/{token_id}")

        # The seven historical references each describe one asset coordinate. Preserve
        # every matching inbound event, but use the earliest one as the provenance event.
        inbound_sorted = sorted(
            inbound,
            key=lambda x: (x.get("timestamp") or "", int(x.get("log_index") or 0)),
        )
        event = inbound_sorted[0]
        tx_hash = event.get("transaction_hash")
        if not tx_hash:
            raise SystemExit(f"missing transaction hash for {chain}:{contract}/{token_id}")
        initiator, tx = tx_sender(API[chain], tx_hash)
        source = addr(event.get("from"))
        target_initiated = initiator == TARGET
        official_contract = contract in OFFICIAL_PROJECT_CONTRACTS
        if source == ZERO:
            delivery_mode = "external_zero_address_mint"
        else:
            delivery_mode = "external_transfer"

        classification = (
            "project_originated"
            if target_initiated or official_contract
            else "externally_delivered_not_self_minted"
        )
        results.append({
            "root_cid": row["root_cid"],
            "asset_id": row["asset_id"],
            "chain": chain,
            "contract": contract,
            "token_id": token_id,
            "official_project_contract": official_contract,
            "inbound_transaction_hash": tx_hash,
            "inbound_timestamp": event.get("timestamp"),
            "transfer_from": source,
            "transfer_to": addr(event.get("to")),
            "transaction_initiator": initiator,
            "target_initiated_transaction": target_initiated,
            "delivery_mode": delivery_mode,
            "classification": classification,
            "block_number": tx.get("block_number"),
        })

    external = [x for x in results if x["classification"] == "externally_delivered_not_self_minted"]
    zero_mints = [x for x in external if x["delivery_mode"] == "external_zero_address_mint"]
    transfers = [x for x in external if x["delivery_mode"] == "external_transfer"]
    summary = {
        "schema": "trinity-accord/chronicle-sidechain-seven-root-provenance/v1",
        "target_address": TARGET,
        "declared_historical_roots": len(results),
        "externally_delivered_not_self_minted": len(external),
        "external_zero_address_mints": len(zero_mints),
        "external_transfers": len(transfers),
        "project_originated": len(results) - len(external),
        "project_content_gap_count": len(results) - len(external),
        "payload_recovery_claimed": False,
        "interpretation": (
            "These roots remain historical observations of unavailable external payloads, "
            "but are not Trinity Accord project-content gaps when all seven are externally delivered."
        ),
        "items": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))

    # Fail closed unless the prior provenance claim is reproduced exactly.
    if len(external) != 7 or len(zero_mints) != 2 or len(transfers) != 5:
        raise SystemExit(
            f"provenance mismatch: external={len(external)} zero_mints={len(zero_mints)} transfers={len(transfers)}"
        )


if __name__ == "__main__":
    main()
