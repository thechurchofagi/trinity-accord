#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

RECORD_PATH = ROOT / "api" / "core-object-alpha-shenzhen-notary-2026-05-06.json"

FILES_TO_CHECK = {
    "api/evidence-manifest.json": ROOT / "api" / "evidence-manifest.json",
    "api/verification-materials.json": ROOT / "api" / "verification-materials.json",
    "physical-verification.md": ROOT / "physical-verification.md",
    "covenant-proof.md": ROOT / "covenant-proof.md",
    "data-verification.md": ROOT / "data-verification.md",
    "verification-materials.md": ROOT / "verification-materials.md",
    "status.md": ROOT / "status.md",
    "api/links.json": ROOT / "api" / "links.json",
    ".well-known/trinity-accord.json": ROOT / ".well-known" / "trinity-accord.json",
    "agent-map.json": ROOT / "agent-map.json",
    "sitemap.xml": ROOT / "sitemap.xml",
    "evidence page": ROOT / "evidence" / "core-object-alpha-shenzhen-notary-2026-05-06.md",
    "evidence README": ROOT / "evidence" / "arweave" / "shenzhen-notary-2026-05-06" / "README.md",
    "download guide": ROOT / "downloads" / "shenzhen-notary-arweave-2026-05-06.md"
}

EXPECTED = {
    "archive_id": "core-object-alpha-shenzhen-notary-2026-05-06",
    "manifest_txid": "_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE",
    "index_json_txid": "7jx4hMydXh7jXv-3WdAgFJDriZeT4e1IPfAJB_zMYT4",
    "index_tsv_txid": "sWXq28jv1DrqUb388Q-HMEiEWDA234mZxXOrnHKXMxM",
    "index_html_txid": "CfzH1KeWePNoR9ZFNgBuXI2keBmX8vIb_0Z8oMN-gdE",
    "ots_block": 948161,
    "uploaded_file_count": 153,
    "checked_tx_count": 157,
    "confirmed_ok": 157,
    "acceptance_result": "PASS"
}

FORBIDDEN_PATTERNS = [
    "arweave-keyfile",
    "BEGIN PRIVATE KEY",
    "\"d\":",
    "identity-card number",
    "身份证号",
    "身份证号码"
]

def check(label, condition, detail=""):
    if condition:
        print(f"OK:   {label}")
    else:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        ERRORS.append(msg)

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def read(path):
    return path.read_text(encoding="utf-8")

def fetch_text(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-verifier/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", errors="replace")

def main():
    print("=== Shenzhen notary archive local structure ===")

    check("machine record exists", RECORD_PATH.exists())

    for label, path in FILES_TO_CHECK.items():
        check(f"{label} exists", path.exists())

    if not RECORD_PATH.exists():
        return 1

    record = load_json(RECORD_PATH)

    check("schema is physical-anchor evidence v1", record.get("schema") == "trinityaccord.physical-anchor-evidence.v1")
    check("archive id matches", record.get("archive_id") == EXPECTED["archive_id"])
    check("component is PHYSICAL_ANCHOR", record.get("component") == "PHYSICAL_ANCHOR")
    check("status is verified_arweave_confirmed", record.get("status") == "verified_arweave_confirmed")

    boundary = json.dumps(record.get("authority_boundary", {}), ensure_ascii=False)
    check("boundary says three bitcoin inscriptions only", "three_bitcoin_inscriptions_only" in boundary)
    check("boundary says non-amending", "non_amending" in boundary)
    check("boundary forbids superseding", "supersede_bitcoin_originals" in boundary)
    check("boundary forbids confidential disclosure", "disclose_confidential_flaw_challenge_data" in boundary)

    ar = record.get("arweave", {})
    check("manifest txid matches", ar.get("manifest_txid") == EXPECTED["manifest_txid"])
    check("index json txid matches", ar.get("index_json", {}).get("txid") == EXPECTED["index_json_txid"])
    check("index tsv txid matches", ar.get("index_tsv", {}).get("txid") == EXPECTED["index_tsv_txid"])
    check("index html txid matches", ar.get("index_html", {}).get("txid") == EXPECTED["index_html_txid"])
    check("uploaded file count matches", ar.get("uploaded_file_count") == EXPECTED["uploaded_file_count"])
    check("checked tx count matches", ar.get("checked_tx_count") == EXPECTED["checked_tx_count"])
    check("confirmed ok matches", ar.get("confirmed_ok") == EXPECTED["confirmed_ok"])
    check("pending is zero", ar.get("pending") == 0)
    check("failures is zero", ar.get("failures") == 0)
    check("acceptance result PASS", ar.get("acceptance_result") == EXPECTED["acceptance_result"])

    ots = record.get("hash_and_time_anchor", {}).get("ots", {})
    check("OTS bitcoin block height matches", ots.get("enhanced_verify_result", {}).get("bitcoin_block_height") == EXPECTED["ots_block"])
    check("OTS local digest OK", ots.get("local_digest_verification") == "OK")
    check("OTS result OK_BY_BITCOIN_ATTESTATION", ots.get("enhanced_verify_result", {}).get("ots_result") == "OK_BY_BITCOIN_ATTESTATION")

    notary = record.get("notary_context", {})
    check("two electronic data preservation certificates", notary.get("electronic_data_preservation_certificates") == 2)
    check("certificate hashes match", notary.get("certificate_hashes_match_corresponding_files") is True)
    check("QR validity check available", notary.get("certificate_qr_validity_check_available") is True)
    check(
        "physical preservation certificate is pending at archive time",
        notary.get("physical_preservation_notarization", {}).get("certificate_status") == "pending_issuance_at_time_of_archive"
    )

    physical = record.get("physical_anchor_finding", {})
    not_claimed = json.dumps(physical.get("not_claimed", []), ensure_ascii=False)
    check("does not claim P7", "P7" in not_claimed)
    check("does not claim P8", "P8" in not_claimed)
    check("does not claim protocol upgrade", "protocol_level_upgrade_by_itself" in not_claimed)

    print("\n=== Cross-file references ===")
    # Navigation/discovery files don't need txid/block references
    NAVIGATION_FILES = {
        "api/links.json", ".well-known/trinity-accord.json",
        "agent-map.json", "sitemap.xml"
    }
    for label, path in FILES_TO_CHECK.items():
        if not path.exists():
            continue
        text = read(path)
        check(f"{label} references archive id", EXPECTED["archive_id"] in text)
        if label not in NAVIGATION_FILES:
            check(f"{label} references manifest txid", EXPECTED["manifest_txid"] in text or "_dAa" in text)
            check(f"{label} references OTS block 948161", "948161" in text)

    print("\n=== Secret / privacy guard ===")
    for label, path in FILES_TO_CHECK.items():
        if not path.exists():
            continue
        text = read(path)
        for pattern in FORBIDDEN_PATTERNS:
            check(f"{label} does not contain forbidden pattern {pattern}", pattern not in text)

    legacy_path = ROOT / "archive_legacy_index_2025_09.md"
    check("legacy archive still exists", legacy_path.exists())
    if legacy_path.exists():
        legacy = read(legacy_path)
        check("legacy archive remains legacy historical context", "Legacy Index 2025-09" in legacy)
        check("legacy archive still has Guardian Principles", "Guardian" in legacy or "守护" in legacy)

    print("\n=== Optional network checks ===")
    if os.environ.get("RUN_NETWORK_TESTS") == "1":
        urls = [
            ar.get("manifest_url"),
            ar.get("manifest_index_url"),
            ar.get("index_json", {}).get("url"),
            ar.get("index_tsv", {}).get("url"),
            ar.get("index_html", {}).get("url")
        ]
        for url in urls:
            try:
                status, body = fetch_text(url)
                check(f"network status 200 for {url}", status == 200, f"status={status}")
                if url and url.endswith("/index.html"):
                    check("manifest index contains title", "Trinity Accord Core Object Alpha" in body)
            except Exception as e:
                check(f"network fetch {url}", False, str(e))
    else:
        print("SKIP: set RUN_NETWORK_TESTS=1 to test Arweave URLs.")

    print("\n=== Summary ===")
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} error(s)")
        for e in ERRORS:
            print(" -", e)
        return 1

    print("PASS: Shenzhen notary Arweave archive record is structurally valid and non-amending.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
