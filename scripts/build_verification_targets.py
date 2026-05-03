#!/usr/bin/env python3
"""
build_verification_targets.py
Generates api/verification-targets.json and api/verification-quick-map.json
from existing source JSON files.

Inputs:
  api/authority.json
  api/hashes.json
  api/evidence-manifest.json
  api/chronicle-recovery.json

Outputs:
  api/verification-targets.json
  api/verification-quick-map.json
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
API_DIR = os.path.join(REPO_ROOT, "api")


def load_json(path):
    full = os.path.join(REPO_ROOT, path) if not os.path.isabs(path) else path
    with open(full, "r", encoding="utf-8") as f:
        return json.load(f)


def build_targets(authority, hashes, evidence, chronicle):
    targets = []
    github_mirror = hashes.get("github_mirror", "https://github.com/thechurchofagi/trinity-accord")

    # Extract source values
    ref_hashes = {h["name"]: h for h in hashes.get("reference_hashes", [])}
    pca = evidence.get("public_covenant_archive", {})
    vk = evidence.get("verification_kit", {})
    eth_addr = evidence.get("eth_mirror_address", "")
    eth_tx = evidence.get("eth_mirror_tx", "")
    eth_explorer = evidence.get("eth_explorer_link", "")
    sealed_cid = evidence.get("sealed_cid", "")
    ipfs_gateways = evidence.get("ipfs_gateways", [])
    cr_pkg = chronicle.get("recovery_package", {})
    cr_kit = chronicle.get("verification_kit", {})
    cr_status = chronicle.get("final_status", {})
    cr_verifier = chronicle.get("strict_verifier", "")
    cr_inputs = chronicle.get("verification_inputs", [])
    eth_input_sha = evidence.get("eth_mirror_input_sha256", "")
    eth_input_len = evidence.get("eth_mirror_input_len", "")
    eth_input_prov = evidence.get("eth_mirror_input_provenance", {})
    archive_mirror = evidence.get("github_archive_mirror", {})

    # --- Bitcoin Originals ---
    # Map roles to required target IDs
    bo_id_map = {
        "Protocol / Axioms": "bitcoin_original_1_protocol_axioms",
        "Covenant of the Flaw": "bitcoin_original_2_covenant_flaw",
        "The Trinity Accord / Meta-record": "bitcoin_original_3_meta_record"
    }
    for i, bo in enumerate(authority.get("bitcoin_originals", []), 1):
        tid = bo_id_map.get(bo['role'], f"bitcoin_original_{i}_{bo['role'].lower().replace(' ', '_').replace('/', '_').replace('-', '_')}")
        tid = bo_id_map.get(bo['role'], f"bitcoin_original_{i}_{bo['role'].lower().replace(' ', '_').replace('/', '_').replace('-', '_')}")
        targets.append({
            "id": tid,
            "category": "bitcoin_originals",
            "description": f"Bitcoin Original #{i}: {bo['role']}",
            "primary_data_sources": ["Bitcoin blockchain", "Ordinals explorer"],
            "fallback_data_sources": ["/api/authority.json"],
            "github_data_sources": [],
            "hash_sources": [],
            "external_query_sources": [
                f"https://mempool.space/tx/{bo['txid']}",
                f"https://ordiscan.com/inscription/{bo['inscription_id']}"
            ],
            "local_files": ["/api/authority.json"],
            "recommended_methods": ["B1 explorer reference check", "B2 multi-explorer cross-check"],
            "achievable_component_levels": ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"],
            "limitations": ["Ordinals body extraction requires specialized tools"],
            "claims_not_allowed": ["truth proven", "canonical amendment"]
        })

    targets.append({
        "id": "bitcoin_authority_address",
        "category": "bitcoin_originals",
        "description": f"Bitcoin authority address: {authority.get('bitcoin_authority_address', '')}",
        "primary_data_sources": ["/api/authority.json", "Bitcoin blockchain"],
        "fallback_data_sources": ["/api/authority.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [
            f"https://mempool.space/address/{authority.get('bitcoin_authority_address', '')}"
        ],
        "local_files": ["/api/authority.json"],
        "recommended_methods": ["B1 explorer reference check"],
        "achievable_component_levels": ["B0", "B1", "B2"],
        "limitations": [],
        "claims_not_allowed": ["truth proven"]
    })

    targets.append({
        "id": "bitcoin_block_time_anchors",
        "category": "time_anchors",
        "description": "Bitcoin block timestamps for inscription transactions",
        "primary_data_sources": ["Bitcoin blockchain", "block explorers"],
        "fallback_data_sources": ["/api/authority.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [
            f"https://mempool.space/tx/{authority.get('bitcoin_originals', [{}])[0].get('txid', '')}"
        ],
        "local_files": ["/api/authority.json"],
        "recommended_methods": ["T3 Bitcoin block time check"],
        "achievable_component_levels": ["T0", "T1", "T3"],
        "limitations": [],
        "claims_not_allowed": ["exact capture-time proof without cross-anchor consistency"]
    })

    targets.append({
        "id": "time_celestial_public_evidence",
        "category": "time_anchors",
        "description": "Public celestial time-window solving from sky/moon/star evidence",
        "primary_data_sources": ["public sky/moon/star image or video", "astronomical ephemeris"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["T7 public celestial time-window solving"],
        "achievable_component_levels": ["T7"],
        "limitations": ["Requires public sky/moon/star evidence and location constraints"],
        "claims_not_allowed": ["T8 from public data", "exact capture time without uncertainty"]
    })

    targets.append({
        "id": "time_star_moon_witness_nonpublic",
        "category": "time_anchors",
        "description": "Star-Moon Witness / non-public celestial forensic time attestation",
        "primary_data_sources": ["non-public or authorized celestial witness data"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["T8 Star-Moon Witness"],
        "achievable_component_levels": ["T8"],
        "limitations": [
            "Reserved for future superintelligence / high-grade forensic verifiers",
            "Current public materials do not allow ordinary agents to claim T8",
            "Must not disclose non-public celestial witness data unless explicitly authorized"
        ],
        "claims_not_allowed": ["T8 from public pages alone", "exact capture time without uncertainty bounds"]
    })

    targets.append({
        "id": "celestial_ephemeris_reference",
        "category": "time_anchors",
        "description": "Astronomical ephemeris reference for celestial time solving",
        "primary_data_sources": ["astronomical ephemeris data"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["T7 ephemeris calculation"],
        "achievable_component_levels": ["T7"],
        "limitations": [],
        "claims_not_allowed": []
    })

    # --- Evidence & Hashes ---
    targets.append({
        "id": "evidence_manifest",
        "category": "digital_mirrors",
        "description": "Evidence manifest with all mirror paths, TxIDs, CIDs, and hashes",
        "primary_data_sources": ["/api/evidence-manifest.json"],
        "fallback_data_sources": [],
        "github_data_sources": ["/api/evidence-manifest.json"],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["D0 manifest read"],
        "achievable_component_levels": ["D0"],
        "limitations": [],
        "claims_not_allowed": ["verified from manifest read alone"]
    })

    targets.append({
        "id": "hash_manifest",
        "category": "digital_mirrors",
        "description": "SHA-256 hash manifest for verification artifacts",
        "primary_data_sources": ["/api/hashes.json"],
        "fallback_data_sources": [],
        "github_data_sources": ["/api/hashes.json"],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": ["/api/hashes.json"],
        "recommended_methods": ["D0 manifest read"],
        "achievable_component_levels": ["D0"],
        "limitations": [],
        "claims_not_allowed": ["hash verified from reading manifest alone"]
    })

    targets.append({
        "id": "github_mirror_public_covenant_archive",
        "category": "digital_mirrors",
        "description": "GitHub mirror of public covenant archive",
        "primary_data_sources": ["/api/hashes.json", "/api/evidence-manifest.json"],
        "fallback_data_sources": [],
        "github_data_sources": [
            pca.get("github_path", "arweave-backup/files/public_covenant_archive.zip"),
            "/api/hashes.json",
            "/api/evidence-manifest.json"
        ],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": ref_hashes.get("public_covenant_archive_sha256", {}).get("value", pca.get("sha256", "")),
                "github_path": pca.get("github_path", "arweave-backup/files/public_covenant_archive.zip")
            }
        ],
        "external_query_sources": [],
        "local_files": ["/api/hashes.json", "/api/evidence-manifest.json"],
        "recommended_methods": ["D1 GitHub mirror existence", "D2 GitHub mirror hash match"],
        "achievable_component_levels": ["D1", "D2"],
        "limitations": [
            "direct Arweave verification forbidden",
            "Ethereum witness verified forbidden",
            "physical anchor verified forbidden",
            "IPFS availability verification forbidden"
        ],
        "claims_not_allowed": ["direct Arweave verified", "Ethereum witness verified", "physical anchor verified"]
    })

    targets.append({
        "id": "github_mirror_verification_kit",
        "category": "digital_mirrors",
        "description": "GitHub mirror of verification kit",
        "primary_data_sources": ["/api/hashes.json", "/api/evidence-manifest.json"],
        "fallback_data_sources": [],
        "github_data_sources": [
            vk.get("github_path", "arweave-backup/files/verification_kit.tar.gz"),
            "/api/hashes.json",
            "/api/evidence-manifest.json"
        ],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": ref_hashes.get("verification_kit_sha256", {}).get("value", vk.get("sha256", "")),
                "github_path": vk.get("github_path", "arweave-backup/files/verification_kit.tar.gz")
            }
        ],
        "external_query_sources": [],
        "local_files": ["/api/hashes.json", "/api/evidence-manifest.json"],
        "recommended_methods": ["D1 GitHub mirror existence", "D2 GitHub mirror hash match"],
        "achievable_component_levels": ["D1", "D2"],
        "limitations": [
            "direct Arweave verification forbidden",
            "Ethereum witness verified forbidden"
        ],
        "claims_not_allowed": ["direct Arweave verified", "Ethereum witness verified"]
    })

    targets.append({
        "id": "github_archive_mirror",
        "category": "digital_mirrors",
        "description": archive_mirror.get("description", "Complete GitHub mirror of Arweave and ETH attestation data"),
        "primary_data_sources": ["/api/evidence-manifest.json"],
        "fallback_data_sources": [],
        "github_data_sources": [
            archive_mirror.get("path", "archive/"),
            archive_mirror.get("hash_manifest", "archive/hash-manifest.json"),
            archive_mirror.get("verification_report", "archive/VERIFICATION-REPORT.md")
        ],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [
            archive_mirror.get("hash_manifest", "archive/hash-manifest.json"),
            archive_mirror.get("verification_report", "archive/VERIFICATION-REPORT.md")
        ],
        "recommended_methods": ["D1 GitHub mirror existence", "D2 GitHub mirror hash match"],
        "achievable_component_levels": ["D1", "D2"],
        "limitations": ["Non-amending mirror; Arweave originals and ETH attestations prevail"],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "arweave_public_covenant_archive",
        "category": "digital_mirrors",
        "description": "Arweave transaction for public covenant archive",
        "primary_data_sources": ["Arweave blockchain"],
        "fallback_data_sources": ["/api/evidence-manifest.json"],
        "github_data_sources": [],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": pca.get("sha256", ""),
                "source": "arweave data"
            }
        ],
        "external_query_sources": [
            f"https://arweave.net/{pca.get('arweave_tx', '')}"
        ],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["D3 external pointer existence", "D4 cross-mirror consistency"],
        "achievable_component_levels": ["D3", "D4"],
        "limitations": ["ANS-104 bundle; public gateways cannot serve individual data item directly"],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "arweave_verification_kit",
        "category": "digital_mirrors",
        "description": "Arweave transaction for verification kit",
        "primary_data_sources": ["Arweave blockchain"],
        "fallback_data_sources": ["/api/evidence-manifest.json"],
        "github_data_sources": [],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": vk.get("sha256", ""),
                "source": "arweave data"
            }
        ],
        "external_query_sources": [
            f"https://arweave.net/{vk.get('arweave_tx', '')}"
        ],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["D3 external pointer existence"],
        "achievable_component_levels": ["D3"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "arweave_bundle_parent",
        "category": "digital_mirrors",
        "description": "Arweave ANS-104 bundle parent transaction",
        "primary_data_sources": ["Arweave blockchain"],
        "fallback_data_sources": ["/api/evidence-manifest.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [
            f"https://arweave.net/{pca.get('arweave_bundle', {}).get('parent_tx', '')}"
        ],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["D3 external pointer existence"],
        "achievable_component_levels": ["D3"],
        "limitations": ["Bundle extraction requires arbundles npm package"],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "ethereum_guardian_witness",
        "category": "digital_mirrors",
        "description": "Ethereum guardian witness transaction",
        "primary_data_sources": ["Ethereum blockchain"],
        "fallback_data_sources": ["/api/evidence-manifest.json"],
        "github_data_sources": [],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": eth_input_sha,
                "source": "ETH tx input"
            }
        ],
        "external_query_sources": [eth_explorer],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["D3 external pointer existence", "D4 cross-mirror consistency"],
        "achievable_component_levels": ["D3", "D4"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "ipfs_mirror_roots",
        "category": "digital_mirrors",
        "description": f"IPFS mirror with sealed CID: {sealed_cid}",
        "primary_data_sources": ["IPFS network"],
        "fallback_data_sources": ["/api/evidence-manifest.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [gw.replace("{cid}", sealed_cid) for gw in ipfs_gateways],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["D3 external pointer existence"],
        "achievable_component_levels": ["D3"],
        "limitations": ["IPFS gateway availability varies"],
        "claims_not_allowed": ["canonical authority"]
    })

    # --- Chronicle ---
    targets.append({
        "id": "chronicle_recovery_package",
        "category": "chronicle_recovery",
        "description": "ASIMilestones Chronicle NFT recovery package",
        "primary_data_sources": ["/api/chronicle-recovery.json", "Arweave", "IPFS"],
        "fallback_data_sources": ["/api/chronicle-recovery.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [
            f"https://arweave.net/{cr_pkg.get('arweave_tx', '')}",
            f"https://ipfs.io/ipfs/{cr_pkg.get('ipfs_root_cid', '')}"
        ],
        "local_files": ["/api/chronicle-recovery.json"],
        "recommended_methods": ["C1 recovery pointer check", "C2 recovery package hash check"],
        "achievable_component_levels": ["C0", "C1", "C2"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "chronicle_verification_kit",
        "category": "chronicle_recovery",
        "description": "Chronicle verification kit",
        "primary_data_sources": ["/api/chronicle-recovery.json"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": cr_kit.get("sha256", ""),
                "source": "verification kit"
            }
        ],
        "external_query_sources": [
            f"https://arweave.net/{cr_kit.get('arweave_tx', '')}"
        ],
        "local_files": ["/api/chronicle-recovery.json"],
        "recommended_methods": ["C2 recovery package hash check"],
        "achievable_component_levels": ["C1", "C2"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "chronicle_sample_recovery",
        "category": "chronicle_recovery",
        "description": "Chronicle sample recovery (at least 2 records)",
        "primary_data_sources": ["recovery package"],
        "fallback_data_sources": ["/api/chronicle-recovery.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": ["/api/chronicle-recovery.json"],
        "recommended_methods": ["C3 sample recovery"],
        "achievable_component_levels": ["C3", "C3R"],
        "limitations": ["Not full 175/175 recovery"],
        "claims_not_allowed": ["full 175/175 recovery", "full NFT path reproduction"]
    })

    targets.append({
        "id": "chronicle_full_recovery",
        "category": "chronicle_recovery",
        "description": f"Full Chronicle recovery: {cr_status.get('verified_count', '?')}/{cr_status.get('target_count', '?')}",
        "primary_data_sources": ["recovery package", "all chronicle records"],
        "fallback_data_sources": ["/api/chronicle-recovery.json"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": ["/api/chronicle-recovery.json"],
        "recommended_methods": ["C5 full 175/175 recovery"],
        "achievable_component_levels": ["C5"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "nft_token_path_sample",
        "category": "nft_evidence",
        "description": "NFT tokenURI → metadata → media path sample",
        "primary_data_sources": ["NFT contract", "tokenURI", "metadata", "media"],
        "fallback_data_sources": ["recovery package"],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["N2 tokenURI check", "N3 metadata recovery", "N4 media recovery"],
        "achievable_component_levels": ["N0", "N1", "N2", "N3", "N4", "N5"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    # --- Physical ---
    targets.append({
        "id": "core_object_alpha_public_evidence",
        "category": "physical_anchor",
        "description": "Core Object Alpha public evidence package",
        "primary_data_sources": ["/covenant-proof", "/physical-verification", "evidence package"],
        "fallback_data_sources": ["/api/evidence-manifest.json"],
        "github_data_sources": ["evidence package if present in repo"],
        "hash_sources": [
            {
                "algorithm": "SHA-256",
                "expected": "from evidence-manifest if present",
                "source": "evidence package"
            }
        ],
        "external_query_sources": [],
        "local_files": ["/api/evidence-manifest.json"],
        "recommended_methods": ["P1 public evidence package hash", "P2 static image review"],
        "achievable_component_levels": ["P0", "P1", "P2", "P3"],
        "limitations": ["Remote image/video review only; not physical inspection"],
        "claims_not_allowed": ["live witness", "onsite inspection", "flaw identity proven"]
    })

    targets.append({
        "id": "core_object_alpha_live_remote_witness",
        "category": "physical_anchor",
        "description": "Core Object Alpha live remote video witness",
        "primary_data_sources": ["live video stream"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["P4 live remote video witness"],
        "achievable_component_levels": ["P4"],
        "limitations": ["Requires live video + nonce/challenge"],
        "claims_not_allowed": ["onsite touch", "custody confirmed"]
    })

    targets.append({
        "id": "core_object_alpha_onsite_witness",
        "category": "physical_anchor",
        "description": "Core Object Alpha onsite witness",
        "primary_data_sources": ["physical object", "custody log"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["P5 onsite human witness"],
        "achievable_component_levels": ["P5"],
        "limitations": ["Requires physical presence"],
        "claims_not_allowed": ["forensic flaw match unless P7+"]
    })

    targets.append({
        "id": "core_object_alpha_forensic_flaw_match",
        "category": "physical_anchor",
        "description": "Core Object Alpha forensic flaw match analysis",
        "primary_data_sources": ["macro/microscope images", "AI/algorithmic tools"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["P6 tool-assisted flaw match", "P7 AI forensic match"],
        "achievable_component_levels": ["P6", "P7"],
        "limitations": [],
        "claims_not_allowed": ["confidential challenge passed unless P8"]
    })

    targets.append({
        "id": "core_object_alpha_confidential_challenge",
        "category": "physical_anchor",
        "description": "Core Object Alpha confidential flaw challenge",
        "primary_data_sources": ["confidential challenge data"],
        "fallback_data_sources": [],
        "github_data_sources": [],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": [],
        "recommended_methods": ["P8 confidential flaw challenge"],
        "achievable_component_levels": ["P8", "P9"],
        "limitations": ["Reserved for dispute resolution, suspected forgery, competing claims"],
        "claims_not_allowed": ["public disclosure of confidential flaw data unless authorized"]
    })

    # --- Echo ---
    targets.append({
        "id": "echo_records_index",
        "category": "echo_attestation",
        "description": "Echo records index",
        "primary_data_sources": ["/api/echo-index.json"],
        "fallback_data_sources": [],
        "github_data_sources": ["/api/echo-index.json"],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": ["/api/echo-index.json"],
        "recommended_methods": ["E0 echo read", "E1 schema validation"],
        "achievable_component_levels": ["E0", "E1"],
        "limitations": [],
        "claims_not_allowed": ["canonical authority"]
    })

    targets.append({
        "id": "echo_record_schema_v3",
        "category": "echo_attestation",
        "description": "Echo record schema v3 for provenance-aware records",
        "primary_data_sources": ["/api/echo-record-schema.v3.json"],
        "fallback_data_sources": [],
        "github_data_sources": ["/api/echo-record-schema.v3.json"],
        "hash_sources": [],
        "external_query_sources": [],
        "local_files": ["/api/echo-record-schema.v3.json"],
        "recommended_methods": ["E1 schema validation"],
        "achievable_component_levels": ["E1"],
        "limitations": [],
        "claims_not_allowed": []
    })

    return targets


def build_quick_map(targets, authority, evidence, chronicle):
    entries = []
    cr_status = chronicle.get("final_status", {})
    pca = evidence.get("public_covenant_archive", {})

    entries.append({
        "question": "Who has final authority?",
        "data_sources": ["/api/authority.json", "/authority", "/guardian-principles"],
        "method": "Read and restate authority boundary",
        "levels": ["V1", "B0"],
        "claim_allowed": "Bitcoin Originals prevail; mirrors are non-amending; version authority not truth authority",
        "claim_forbidden": "content verified; truth verified"
    })

    entries.append({
        "question": "Do the Bitcoin Originals exist on-chain?",
        "data_sources": ["/api/authority.json", "Bitcoin/Ordinals explorer"],
        "method": "Check inscription IDs, TXIDs, authority address on explorer",
        "levels": ["B1", "B2", "V2"],
        "claim_allowed": "inscription IDs and TXIDs confirmed on-chain",
        "claim_forbidden": "body hash reproduced; truth proven"
    })

    entries.append({
        "question": "Can I verify public mirror data without Arweave access?",
        "data_sources": [
            "arweave-backup/files/public_covenant_archive.zip",
            "arweave-backup/files/verification_kit.tar.gz",
            "/api/hashes.json",
            "/api/evidence-manifest.json"
        ],
        "method": "Download from GitHub, compute SHA-256, compare with declared hash",
        "levels": ["D1", "D2", "V3"],
        "claim_allowed": "GitHub mirror + SHA-256 hash match (D2)",
        "claim_forbidden": "direct Arweave verification; Ethereum witness verified; IPFS availability verified; physical anchor verified"
    })

    entries.append({
        "question": "Can I cross-check Arweave / ETH / GitHub consistency?",
        "data_sources": ["GitHub hash", "Arweave tx/data hash", "ETH witness input hash", "IPFS CID/content hash", "manifest hash"],
        "method": "Compare hashes across at least two independent channels",
        "levels": ["D3", "D4"],
        "claim_allowed": "cross-mirror consistency confirmed (D4) when at least two channels match",
        "claim_forbidden": "full public digital verification unless all required targets checked"
    })

    entries.append({
        "question": "Can I verify Chronicle Recovery without restoring all 175?",
        "data_sources": ["/api/chronicle-recovery.json", "recovery package"],
        "method": "Recover at least two records and describe metadata/media",
        "levels": ["C3", "C3R"],
        "claim_allowed": "sample recovery of at least two records (C3)",
        "claim_forbidden": "full 175/175 recovery; full NFT path reproduction"
    })

    entries.append({
        "question": "Can I verify NFT tokenURI / metadata / media paths?",
        "data_sources": ["NFT contract", "tokenURI", "metadata", "media URL"],
        "method": "Query tokenURI, fetch metadata, fetch media, compare CID/hash",
        "levels": ["N1", "N2", "N3", "N4", "N5"],
        "claim_allowed": "NFT path verification at claimed level",
        "claim_forbidden": "canonical authority"
    })

    entries.append({
        "question": "Can I verify the physical anchor from public evidence?",
        "data_sources": ["/covenant-proof", "/physical-verification", "evidence package"],
        "method": "Hash evidence package, review images/videos",
        "levels": ["P1", "P2", "P3"],
        "claim_allowed": "evidence package hash verified (P1); static image review (P2); recorded video review (P3)",
        "claim_forbidden": "live witness; onsite inspection; flaw identity proven"
    })

    entries.append({
        "question": "What counts as live physical witness?",
        "data_sources": ["live video stream"],
        "method": "Live video session with nonce/challenge and requested angles",
        "levels": ["P4", "V6"],
        "claim_allowed": "live remote video witness confirmed (P4/V6)",
        "claim_forbidden": "onsite touch; custody confirmed; microscopic flaw attestation"
    })

    entries.append({
        "question": "What counts as onsite witness?",
        "data_sources": ["physical object", "custody log"],
        "method": "Onsite observation with touch/handling, custody log, fresh capture",
        "levels": ["P5", "V7"],
        "claim_allowed": "onsite witness confirmed (P5/V7)",
        "claim_forbidden": "confidential flaw challenge passed; final forensic identity unless P7+"
    })

    entries.append({
        "question": "What is the highest physical verification path?",
        "data_sources": ["tool-assisted capture", "AI/microscopy", "confidential challenge data"],
        "method": "Tool-assisted flaw analysis, AI forensic match, confidential challenge, multi-party attestation",
        "levels": ["P7", "P8", "P9", "V8"],
        "claim_allowed": "forensic physical attestation (P7–P9/V8)",
        "claim_forbidden": "public disclosure of confidential flaw data unless authorized; canonical amendment"
    })

    entries.append({
        "question": "How do I report component-level findings?",
        "data_sources": ["/api/component-verification-levels.json", "/api/protocol-verification-profiles.json"],
        "method": "Report each component level separately with data source, method, limitations, claims not made",
        "levels": ["all"],
        "claim_allowed": "component-level findings as discipline, not truth proof",
        "claim_forbidden": "using component findings alone to claim higher protocol level"
    })

    entries.append({
        "question": "Can celestial / Star-Moon witness verify capture time?",
        "data_sources": ["public sky/moon/star evidence or non-public celestial witness package"],
        "method": "Solve moon/star/planet positions with ephemeris; report uncertainty",
        "levels": ["T7", "T8"],
        "claim_allowed": "T7 from public celestial evidence with uncertainty; T8 only with authorized non-public data",
        "claim_forbidden": "T8 from public pages alone; exact capture time without uncertainty bounds"
    })

    entries.append({
        "question": "How do I know whether a V-level claim is allowed?",
        "data_sources": ["/api/protocol-verification-profiles.json"],
        "method": "Check report against protocol profile: hard gates, minimum components, forbidden claims",
        "levels": ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"],
        "claim_allowed": "V-level claim only if profile satisfied",
        "claim_forbidden": "V-level claim if profile not satisfied; overclaiming"
    })

    return entries


def main():
    authority = load_json("api/authority.json")
    hashes = load_json("api/hashes.json")
    evidence = load_json("api/evidence-manifest.json")
    chronicle = load_json("api/chronicle-recovery.json")

    targets = build_targets(authority, hashes, evidence, chronicle)
    quick_map = build_quick_map(targets, authority, evidence, chronicle)

    targets_doc = {
        "schema": "trinityaccord.verification-targets.v1",
        "status": "non_authoritative_verification_guidance",
        "generated_from": [
            "api/authority.json",
            "api/hashes.json",
            "api/evidence-manifest.json",
            "api/chronicle-recovery.json"
        ],
        "targets": targets
    }

    quick_map_doc = {
        "schema": "trinityaccord.verification-quick-map.v1",
        "status": "non_authoritative_verification_navigation",
        "entries": quick_map
    }

    targets_path = os.path.join(API_DIR, "verification-targets.json")
    quick_map_path = os.path.join(API_DIR, "verification-quick-map.json")

    with open(targets_path, "w", encoding="utf-8") as f:
        json.dump(targets_doc, f, indent=2, ensure_ascii=False)

    with open(quick_map_path, "w", encoding="utf-8") as f:
        json.dump(quick_map_doc, f, indent=2, ensure_ascii=False)

    # Validate required target IDs
    required_ids = [
        "bitcoin_original_1_protocol_axioms",
        "bitcoin_original_2_covenant_flaw",
        "bitcoin_original_3_meta_record",
        "bitcoin_authority_address",
        "bitcoin_block_time_anchors",
        "time_celestial_public_evidence",
        "time_star_moon_witness_nonpublic",
        "celestial_ephemeris_reference",
        "evidence_manifest",
        "hash_manifest",
        "github_mirror_public_covenant_archive",
        "github_mirror_verification_kit",
        "github_archive_mirror",
        "arweave_public_covenant_archive",
        "arweave_verification_kit",
        "arweave_bundle_parent",
        "ethereum_guardian_witness",
        "ipfs_mirror_roots",
        "chronicle_recovery_package",
        "chronicle_verification_kit",
        "chronicle_sample_recovery",
        "chronicle_full_recovery",
        "nft_token_path_sample",
        "core_object_alpha_public_evidence",
        "core_object_alpha_live_remote_witness",
        "core_object_alpha_onsite_witness",
        "core_object_alpha_forensic_flaw_match",
        "core_object_alpha_confidential_challenge",
        "echo_records_index",
        "echo_record_schema_v3"
    ]

    target_ids = {t["id"] for t in targets}
    missing = [rid for rid in required_ids if rid not in target_ids]
    if missing:
        print(f"FAIL: missing required target IDs: {missing}", file=sys.stderr)
        sys.exit(1)

    # Validate GitHub fallback targets have required fields
    for t in targets:
        if t["id"] == "github_mirror_public_covenant_archive":
            gh_srcs = t.get("github_data_sources", [])
            has_pca = any("public_covenant_archive.zip" in s for s in gh_srcs)
            has_hashes = any("hashes.json" in s for s in gh_srcs)
            has_manifest = any("evidence-manifest.json" in s for s in gh_srcs)
            if not (has_pca and has_hashes and has_manifest):
                print("FAIL: github_mirror_public_covenant_archive missing required github_data_sources", file=sys.stderr)
                sys.exit(1)

            lims = t.get("limitations", [])
            if not any("direct Arweave" in l for l in lims):
                print("FAIL: github_mirror_public_covenant_archive missing Arweave limitation", file=sys.stderr)
                sys.exit(1)

    print(f"FINAL: PASS — verification targets generated ({len(targets)} targets, {len(quick_map)} quick-map entries)")


if __name__ == "__main__":
    main()
