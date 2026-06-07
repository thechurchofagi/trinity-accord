#!/usr/bin/env python3
"""Check if current head already has an Arweave tx in the OTS registry."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", required=True)
    parser.add_argument("--registry", required=True)
    args = parser.parse_args()

    head = json.load(open(args.head))
    current_head = head["head_entry_hash"]
    registry_path = Path(args.registry)

    if not registry_path.exists():
        print("skip_ots_upload=false")
        print("reason=registry_file_missing")
        return

    registry = json.load(open(registry_path))
    latest = registry.get("latest_by_head", {}).get(current_head, {})
    has_existing = any(latest.get(k) for k in [
        "latest_pending_tx_id",
        "latest_verified_tx_id",
        "latest_upgraded_tx_id",
        "latest_any_tx_id",
    ])

    if has_existing:
        print("skip_ots_upload=true")
        print("reason=already_uploaded_for_head")
    else:
        print("skip_ots_upload=false")
        print("reason=no_existing_upload_for_head")


if __name__ == "__main__":
    main()
