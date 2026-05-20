#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "diagnose_single_nft_timestamp.py"
workflow = ROOT / ".github" / "workflows" / "diagnose-single-nft-timestamp.yml"

errors = []

def require(cond, msg):
    if not cond:
        errors.append(msg)

require(script.exists(), "diagnose_single_nft_timestamp.py must exist")
require(workflow.exists(), "diagnose-single-nft-timestamp.yml must exist")

text = script.read_text(encoding="utf-8")
wfy = workflow.read_text(encoding="utf-8")

for marker in [
    "ERC721_INTERFACE_ID",
    "ERC721_METADATA_INTERFACE_ID",
    "ERC1155_INTERFACE_ID",
    "ERC1155_METADATA_URI_INTERFACE_ID",
    "supports_interface",
    "ownerOf",
    "tokenURI",
    "erc1155_uri",
    "erc721_transfer_from_zero_topic3",
    "erc721_transfer_any_topic3",
    "erc1155_transfer_single_from_zero",
    "erc1155_transfer_batch_from_zero",
    "single-token-timestamp-diagnosis.json",
    "85210329807936527805363210873332413577559846505703131855064182995898737885245",
]:
    require(marker in text, f"diagnosis script missing marker: {marker}")

require("scripts/diagnose_single_nft_timestamp.py" in wfy, "workflow must call diagnosis script")
require("actions/upload-artifact@v4" in wfy, "workflow must upload artifact")
require("ETH_RPC_URLS" in wfy, "workflow must use ETH_RPC_URLS")

if errors:
    print("SINGLE_NFT_TIMESTAMP_DIAGNOSIS_STATIC_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("SINGLE_NFT_TIMESTAMP_DIAGNOSIS_STATIC_OK")
