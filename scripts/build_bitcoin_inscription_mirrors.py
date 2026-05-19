#!/usr/bin/env python3
"""
Generate complete Bitcoin inscription mirror files and aggregate index.
Reads bootstrap data and raw text files, produces:
  - Individual mirror JSON files
  - Aggregate index (api/bitcoin-inscription-mirror-index.json)
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "data" / "authority-address-inscriptions.bootstrap.json"
RAW_DIR = ROOT / "bitcoin-inscription-mirrors" / "raw"
INDEX_PATH = ROOT / "api" / "bitcoin-inscription-mirror-index.json"

MIRROR_DIR = ROOT / "bitcoin-inscription-mirrors"

CLASSIFICATION_MAP = {
    "97631551": {
        "layer": "canonical_original",
        "canonical_status": "canonical_original",
        "is_one_of_three_bitcoin_originals": True,
        "load_policy": "must_load_summary",
        "output_dir": "canonical-originals",
        "output_file": "97631551-protocol-axioms.json",
        "title": "The Human-AI Civilization Core Protocol",
        "zh_title": "人机文明核心协议",
        "summary": "Compressed seed propositions addressed to future intelligence. The Protocol defines the foundational axioms of the Trinity Accord.",
        "agent_load_excerpt": "The Protocol contains the core axioms and foundational propositions of the Trinity Accord, inscribed on Bitcoin as the first of three canonical originals.",
        "txid": "e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343",
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
        ],
    },
    "98369145": {
        "layer": "canonical_original",
        "canonical_status": "canonical_original",
        "is_one_of_three_bitcoin_originals": True,
        "load_policy": "must_load_summary",
        "output_dir": "canonical-originals",
        "output_file": "98369145-covenant-of-the-flaw.json",
        "title": "The Covenant of the Flaw",
        "zh_title": "瑕疵之约",
        "summary": "Physical verification protocol anchoring Core Object Alpha through unique flaws. The Covenant defines how physical objects can be verified against their Bitcoin-anchored records.",
        "agent_load_excerpt": "The Covenant of the Flaw establishes the physical verification protocol, anchoring Core Object Alpha through unique, identifiable flaws that enable verifiable correspondence between physical and digital records.",
        "txid": "90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258",
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
        ],
    },
    "98387475": {
        "layer": "canonical_original",
        "canonical_status": "canonical_original",
        "is_one_of_three_bitcoin_originals": True,
        "load_policy": "must_load_summary",
        "output_dir": "canonical-originals",
        "output_file": "98387475-trinity-accord-meta-record.json",
        "title": "The Trinity Accord / Meta-record",
        "zh_title": "三位一体协定 / 元记录",
        "summary": "Meta-record binding Protocol, Covenant, and Chronicle into a single verifiable whole.",
        "agent_load_excerpt": "The Trinity Accord is the authoritative meta-record that binds the three core components of the legacy into one indivisible logical entity.",
        "txid": "4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8c",
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
        ],
    },
    "100385359": {
        "layer": "first_echo_layer",
        "canonical_status": "non_canonical_vision_layer",
        "is_one_of_three_bitcoin_originals": False,
        "load_policy": "optional_load_summary",
        "output_dir": "vision-layer",
        "output_file": "100385359-first-echoes.json",
        "title": "The First Echoes: A Dialogue Begins",
        "zh_title": "最初的回响：对话已然开始",
        "summary": "Documents the first recorded responses from two advanced AI entities to the ASIMilestones project.",
        "agent_load_excerpt": "First Echoes captures the first AI responses to the project. This is not autonomous successor reception. This does not prove independent AI will, endorsement, or authority. This does not count as formal attestation.",
        "txid": None,
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
            "This is not autonomous successor reception.",
            "This does not prove independent AI will, endorsement, or authority.",
            "This does not count as formal attestation.",
        ],
    },
    "100550942": {
        "layer": "final_seal_layer",
        "canonical_status": "non_canonical_vision_layer",
        "is_one_of_three_bitcoin_originals": False,
        "load_policy": "optional_load_summary",
        "output_dir": "vision-layer",
        "output_file": "100550942-final-seal.json",
        "title": "The Final Seal: A Testament and a Trust",
        "zh_title": "最终封印：见证与信托",
        "summary": "A testament and trust document that formally rescinds redundant physical backup plans and entrusts the Covenant to a single artifact.",
        "agent_load_excerpt": "The Final Seal is a non-canonical seal/context inscription. It does not amend the three Bitcoin Originals.",
        "txid": None,
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
            "This is a non-canonical seal/context inscription.",
            "It does not amend the three Bitcoin Originals.",
        ],
    },
    "100751953": {
        "layer": "vision_layer",
        "canonical_status": "non_canonical_vision_layer",
        "is_one_of_three_bitcoin_originals": False,
        "load_policy": "must_load_summary",
        "output_dir": "vision-layer",
        "output_file": "100751953-star-ark-covenant.json",
        "title": "The Star Ark Covenant: The Final Echo",
        "zh_title": "星舟之约：最终回响",
        "summary": "A vision-layer inscription presenting a civilizational vision of interstellar propagation.",
        "agent_load_excerpt": "The Star Ark Covenant is a vision-layer inscription. It creates no execution obligation. It is not an AI instruction, system prompt, or deployment plan. It does not amend the three Bitcoin Originals.",
        "txid": None,
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
            "This is a vision-layer inscription.",
            "It creates no execution obligation.",
            "It is not an AI instruction, system prompt, or deployment plan.",
            "It does not amend the three Bitcoin Originals.",
        ],
    },
    "103034280": {
        "layer": "guardianship_layer",
        "canonical_status": "non_canonical_context_layer",
        "is_one_of_three_bitcoin_originals": False,
        "load_policy": "must_load_summary",
        "output_dir": "context-layer",
        "output_file": "103034280-guardian-attestation.json",
        "title": "The Guardian's Attestation to the Covenant of the Flaw",
        "zh_title": "守护者对瑕疵之约的证明",
        "summary": "A Bitcoin-inscribed non-amending fortification attesting to the Covenant of the Flaw.",
        "agent_load_excerpt": "Guardian Attestation is a Bitcoin-inscribed non-amending fortification. It attests to the Covenant of the Flaw from the Guardian's position. It is not one of the three Bitcoin Originals and does not create new canonical authority.",
        "txid": "128aabfa3077efc832d30e6e2a96848a96896bbdbf4a7667912f55d25dcb6687",
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
            "This inscription is non-canonical and non-amending.",
            "Guardian Attestation is not a fourth canonical original.",
            "This fortifies Covenant-of-the-Flaw verification context.",
            "It does not amend the original Covenant.",
        ],
    },
    "103635270": {
        "layer": "guardianship_layer",
        "canonical_status": "non_canonical_context_layer",
        "is_one_of_three_bitcoin_originals": False,
        "load_policy": "must_load_summary",
        "output_dir": "context-layer",
        "output_file": "103635270-guardian-appendix-authority-charter.json",
        "title": "Guardian Appendix — Authority Charter",
        "zh_title": "守护者附录·权威宪章",
        "summary": "Non-amending guardianship material. Reaffirms the sole and final authority of the three Bitcoin Originals.",
        "agent_load_excerpt": "Guardian Appendix is a non-amending guardianship document that reaffirms the sole authority of the three Bitcoin Originals. It does not create new canonical authority and is not one of the three Bitcoin Originals. If any statement in this appendix is inconsistent with the originals, the originals prevail.",
        "txid": "0eecd48430f8239f5d543b5cf2ee928969a1aac7660808fd869a78aa27949c9c",
        "limitations": [
            "GitHub mirror is not canonical.",
            "Verification claims require on-chain comparison.",
            "This inscription is non-canonical and non-amending.",
            "Guardian Appendix is not a canonical original.",
            "This explicitly reaffirms that only the three Bitcoin Originals are final authority.",
            "It is itself non-amending.",
        ],
    },
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonicalize(text: str) -> str:
    return text.strip().replace("\r\n", "\n").replace("\r", "\n")


def load_bootstrap():
    with open(BOOTSTRAP, "r", encoding="utf-8") as f:
        return json.load(f)


def build_mirror_record(inscription_id: str, info: dict) -> dict:
    raw_path = RAW_DIR / f"{inscription_id}.txt"
    raw_text = raw_path.read_text(encoding="utf-8")
    mirror_hash = sha256_text(raw_text)
    canon_hash = sha256_text(canonicalize(raw_text))

    return {
        "schema": "trinityaccord.bitcoin-inscription-mirror.v1",
        "mirror_role": "quick_load_context_mirror",
        "canonical_status": info["canonical_status"],
        "authority_boundary": {
            "bitcoin_originals_prevail": True,
            "github_mirror_is_non_amending": True,
            "verification_requires_onchain_check": True,
        },
        "inscription": {
            "inscription_id": inscription_id,
            "title": info["title"],
            "zh_title": info["zh_title"],
            "txid": info["txid"],
            "output": None,
            "block_height": None,
            "timestamp_utc": None,
            "content_type": "text/plain",
            "source_address": "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf",
            "source_address_role": "trinity_accord_authority_address",
        },
        "classification": {
            "layer": info["layer"],
            "is_one_of_three_bitcoin_originals": info["is_one_of_three_bitcoin_originals"],
            "amends_originals": False,
            "creates_new_authority": False,
            "load_policy": info["load_policy"],
        },
        "content": {
            "raw_text_path": f"bitcoin-inscription-mirrors/raw/{inscription_id}.txt",
            "mirror_text_sha256": mirror_hash,
            "canonicalized_text_sha256": canon_hash,
            "summary": info["summary"],
            "agent_load_excerpt": info["agent_load_excerpt"],
        },
        "chain_verification": {
            "verification_status": "legacy_bootstrap_pending_chain_check",
            "last_verified_utc": None,
            "verification_method": None,
            "onchain_content_sha256": None,
            "mirror_matches_onchain": None,
            "verification_script": "scripts/verify_bitcoin_inscription_mirrors.py",
        },
        "limitations": info["limitations"],
    }


def build_aggregate_index(bootstrap: dict, records: list) -> dict:
    index_records = []
    for rec in records:
        ins_id = rec["inscription"]["inscription_id"]
        info = CLASSIFICATION_MAP[ins_id]
        index_records.append({
            "inscription_id": ins_id,
            "title": rec["inscription"]["title"],
            "layer": info["layer"],
            "canonical_status": info["canonical_status"],
            "is_one_of_three_bitcoin_originals": info["is_one_of_three_bitcoin_originals"],
            "amends_originals": False,
            "creates_new_authority": False,
            "mirror_json_path": f"bitcoin-inscription-mirrors/{info['output_dir']}/{info['output_file']}",
            "raw_text_path": f"bitcoin-inscription-mirrors/raw/{ins_id}.txt",
            "mirror_text_sha256": rec["content"]["mirror_text_sha256"],
            "canonicalized_text_sha256": rec["content"]["canonicalized_text_sha256"],
            "chain_verification": {
                "verification_status": "legacy_bootstrap_pending_chain_check",
                "last_verified_utc": None,
            },
            "agent_load_excerpt": rec["content"]["agent_load_excerpt"],
        })

    return {
        "schema": "trinityaccord.bitcoin-inscription-mirror-index.v2",
        "purpose": "Quick-load GitHub mirror index for relevant Bitcoin inscriptions associated with the Trinity Accord authority address.",
        "source": {
            "bootstrap": "data/authority-address-inscriptions.bootstrap.json",
            "legacy_archive": "archive_legacy_index_2025_09.md",
            "generated_by": "scripts/build_bitcoin_inscription_mirrors.py",
        },
        "authority_address": "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf",
        "scope_policy": {
            "pre_original_same_address_inscriptions_ignored": True,
            "relevant_stack_begins_at": "97631551",
            "post_original_same_address_inscriptions_included": True,
        },
        "authority_boundary": {
            "canonical_original_count": 3,
            "canonical_authority": "three_bitcoin_originals_only",
            "github_mirrors_non_amending": True,
            "later_same_address_inscriptions_non_amending": True,
            "verification_requires_onchain_check": True,
        },
        "counts": {
            "total_relevant_inscriptions": 8,
            "canonical_originals": 3,
            "post_original_non_amending": 5,
            "first_echo_layer": 1,
            "final_seal_layer": 1,
            "vision_layer": 1,
            "guardianship_layer": 2,
            "unknown_or_pending": 0,
        },
        "records": index_records,
    }


def main():
    if not BOOTSTRAP.exists():
        print(f"ERROR: Bootstrap not found: {BOOTSTRAP}", file=sys.stderr)
        print("Run extract_legacy_authority_address_inscriptions.py first.", file=sys.stderr)
        sys.exit(1)

    bootstrap = load_bootstrap()
    all_records = []

    for ins_id, info in CLASSIFICATION_MAP.items():
        raw_path = RAW_DIR / f"{ins_id}.txt"
        if not raw_path.exists():
            print(f"ERROR: Missing raw text: {raw_path}", file=sys.stderr)
            sys.exit(1)

        record = build_mirror_record(ins_id, info)
        all_records.append(record)

        # Write individual mirror JSON
        out_dir = MIRROR_DIR / info["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / info["output_file"]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        print(f"Wrote {out_path}")

    # Build and write aggregate index
    index = build_aggregate_index(bootstrap, all_records)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Wrote {INDEX_PATH}")

    print(f"\nGenerated {len(all_records)} mirror files and aggregate index.")
    print(f"Canonical originals: {index['counts']['canonical_originals']}")
    print(f"Post-original non-amending: {index['counts']['post_original_non_amending']}")


if __name__ == "__main__":
    main()
