#!/usr/bin/env python3
"""
Extract authority-address inscription bootstrap from legacy archive.
Reads archive_legacy_index_2025_09.md, extracts the eight relevant inscriptions,
writes data/authority-address-inscriptions.bootstrap.json and raw text files.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive_legacy_index_2025_09.md"
BOOTSTRAP = ROOT / "data" / "authority-address-inscriptions.bootstrap.json"
RAW_DIR = ROOT / "bitcoin-inscription-mirrors" / "raw"

EXPECTED_IDS = [
    "97631551", "98369145", "98387475",
    "100385359", "100550942", "100751953",
    "103034280", "103635270",
]

AUTHORITY_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"

RECORDS = [
    {
        "order": 1, "inscription_id": "97631551",
        "title": "The Human-AI Civilization Core Protocol",
        "zh_title": "人机文明核心协议",
        "role": "Protocol / Axioms",
        "layer": "canonical_original", "canonical_status": "canonical_original",
        "is_one_of_three_bitcoin_originals": True,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 2, "inscription_id": "98369145",
        "title": "The Covenant of the Flaw",
        "zh_title": "瑕疵之约",
        "role": "Physical Verification Protocol",
        "layer": "canonical_original", "canonical_status": "canonical_original",
        "is_one_of_three_bitcoin_originals": True,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 3, "inscription_id": "98387475",
        "title": "The Trinity Accord / Meta-record",
        "zh_title": "三位一体协定 / 元记录",
        "role": "Meta-record binding Protocol, Covenant, and Chronicle",
        "layer": "canonical_original", "canonical_status": "canonical_original",
        "is_one_of_three_bitcoin_originals": True,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 4, "inscription_id": "100385359",
        "title": "The First Echoes: A Dialogue Begins",
        "zh_title": "最初的回响：对话已然开始",
        "role": "First Echo Layer",
        "layer": "first_echo_layer", "canonical_status": "non_canonical_vision_layer",
        "is_one_of_three_bitcoin_originals": False,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 5, "inscription_id": "100550942",
        "title": "The Final Seal: A Testament and a Trust",
        "zh_title": "最终封印：见证与信托",
        "role": "Final Seal Layer",
        "layer": "final_seal_layer", "canonical_status": "non_canonical_vision_layer",
        "is_one_of_three_bitcoin_originals": False,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 6, "inscription_id": "100751953",
        "title": "The Star Ark Covenant: The Final Echo",
        "zh_title": "星舟之约：最终回响",
        "role": "Vision Layer",
        "layer": "vision_layer", "canonical_status": "non_canonical_vision_layer",
        "is_one_of_three_bitcoin_originals": False,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 7, "inscription_id": "103034280",
        "title": "The Guardian's Attestation to the Covenant of the Flaw",
        "zh_title": "守护者对瑕疵之约的证明",
        "role": "Guardianship Layer",
        "layer": "guardianship_layer", "canonical_status": "non_canonical_context_layer",
        "is_one_of_three_bitcoin_originals": False,
        "amends_originals": False, "creates_new_authority": False,
    },
    {
        "order": 8, "inscription_id": "103635270",
        "title": "Guardian Appendix — Authority Charter",
        "zh_title": "守护者附录·权威宪章",
        "role": "Guardianship Layer / Authority Boundary",
        "layer": "guardianship_layer", "canonical_status": "non_canonical_context_layer",
        "is_one_of_three_bitcoin_originals": False,
        "amends_originals": False, "creates_new_authority": False,
    },
]


def main():
    if not ARCHIVE.exists():
        print(f"ERROR: Archive not found: {ARCHIVE}", file=sys.stderr)
        sys.exit(1)

    # Check raw text files exist
    missing_raw = []
    for rec in RECORDS:
        raw_path = RAW_DIR / f"{rec['inscription_id']}.txt"
        if not raw_path.exists() or raw_path.stat().st_size == 0:
            missing_raw.append(rec["inscription_id"])
    if missing_raw:
        print(f"ERROR: Missing or empty raw text files: {missing_raw}", file=sys.stderr)
        sys.exit(1)

    # Build bootstrap
    bootstrap = {
        "schema": "trinityaccord.authority-address-inscriptions.bootstrap.v1",
        "source_file": "archive_legacy_index_2025_09.md",
        "source_role": "legacy_homepage_archive_bootstrap",
        "authority_address": AUTHORITY_ADDRESS,
        "policy": {
            "ignore_pre_original_same_address_inscriptions": True,
            "canonical_original_count": 3,
            "later_same_address_inscriptions_are_non_amending": True,
        },
        "records": RECORDS,
    }

    BOOTSTRAP.parent.mkdir(parents=True, exist_ok=True)
    with open(BOOTSTRAP, "w", encoding="utf-8") as f:
        json.dump(bootstrap, f, indent=2, ensure_ascii=False)
    print(f"Wrote {BOOTSTRAP}")

    # Verify IDs
    extracted_ids = {r["inscription_id"] for r in RECORDS}
    expected_ids = set(EXPECTED_IDS)
    if extracted_ids != expected_ids:
        missing = expected_ids - extracted_ids
        extra = extracted_ids - expected_ids
        print(f"ERROR: ID mismatch. Missing: {missing}, Extra: {extra}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(RECORDS)} inscription records. All expected IDs present.")


if __name__ == "__main__":
    main()
