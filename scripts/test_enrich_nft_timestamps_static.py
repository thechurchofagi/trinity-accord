#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "enrich_nft_timestamps.py"
workflow = ROOT / ".github" / "workflows" / "enrich-nft-timestamps.yml"

errors = []

def require(cond, msg):
    if not cond:
        errors.append(msg)

require(script.exists(), "scripts/enrich_nft_timestamps.py must exist")
require(workflow.exists(), ".github/workflows/enrich-nft-timestamps.yml must exist")

text = script.read_text(encoding="utf-8")
wfy = workflow.read_text(encoding="utf-8")

for marker in [
    "ERC721_TRANSFER_TOPIC",
    "ERC1155_TRANSFER_SINGLE_TOPIC",
    "ERC1155_TRANSFER_BATCH_TOPIC",
    "find_erc721_mints",
    "find_erc1155_single_mints",
    "find_erc1155_batch_mints",
    "topics[3]",
    "decode_erc1155_transfer_single",
    "decode_dynamic_uint_arrays",
    "missing-timestamps.json",
    "timestamp-enrichment-report.json",
]:
    require(marker in text, f"timestamp script missing marker: {marker}")

require("scripts/enrich_nft_timestamps.py" in wfy, "workflow must call scripts/enrich_nft_timestamps.py")
require("actions/upload-artifact@v4" in wfy, "workflow must upload diagnostics artifact")
require("ETH_RPC_URLS" in wfy, "workflow must support ETH_RPC_URLS secret")

bad_patterns = [
    'tid_hex = lg.get("data","0x")',
    "tid_hex = lg.get(\"data\",\"0x\")",
    "tid = str(int(tid_hex,16))",
]
for bad in bad_patterns:
    require(bad not in text and bad not in wfy, f"old broken tokenId parser still present: {bad}")

if errors:
    print("ENRICH_NFT_TIMESTAMPS_STATIC_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ENRICH_NFT_TIMESTAMPS_STATIC_OK")
