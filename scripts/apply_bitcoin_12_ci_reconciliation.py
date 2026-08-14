from __future__ import annotations

import hashlib
import json
from pathlib import Path


def require_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing expected migration marker: {label}")
    return text.replace(old, new, 1)


# Make the canonical final-evidence generator preserve historical v1 validation,
# then project through the already-reviewed v2 parity transform.
p = Path("scripts/build_final_evidence_inventory.py")
text = p.read_text(encoding="utf-8")
text = require_replace(text, "import subprocess\nimport sys\n", "import subprocess\nimport sys\nimport tempfile\n", "generator imports")
text = require_replace(text, "from typing import Any\n", "from typing import Any\n\nimport finalize_bitcoin_12_parity as bitcoin12\n", "generator parity import")
text = require_replace(
    text,
    '    btc_report = verified_report(\n        "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",\n        "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",\n    )\n',
    '    btc_report = verified_report(\n        "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",\n        "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",\n    )\n    btc_v2_manifest, btc_v2_report = bitcoin12.verified_inputs()\n',
    "generator v2 verification inputs",
)
marker = '    inventory["source_digest"] = canonical_digest(inventory)\n    return inventory\n'
projection = '''    with tempfile.TemporaryDirectory() as tmp:\n        tmp_root = Path(tmp)\n        (tmp_root / "api").mkdir(parents=True, exist_ok=True)\n        temp_inventory = tmp_root / "api/final-evidence-inventory.v1.json"\n        temp_inventory.write_text(\n            json.dumps(inventory, ensure_ascii=False, indent=2, allow_nan=False) + "\\n",\n            encoding="utf-8",\n        )\n        original_root = bitcoin12.ROOT\n        try:\n            bitcoin12.ROOT = tmp_root\n            bitcoin12.update_final_inventory(btc_v2_manifest, btc_v2_report)\n            inventory = json.loads(temp_inventory.read_text(encoding="utf-8"))\n        finally:\n            bitcoin12.ROOT = original_root\n\n    inventory["source_digest"] = canonical_digest(inventory)\n    return inventory\n'''
text = require_replace(text, marker, projection, "generator current projection")
text = require_replace(
    text,
    "| Cryptographic evidence | 8 Bitcoin inscriptions, 12 non-NFT Ethereum anchors, 175 Chronicle NFTs |",
    "| Cryptographic evidence | {bitcoin['count']} Bitcoin inscriptions, 12 non-NFT Ethereum anchors, 175 Chronicle NFTs |",
    "markdown bitcoin count",
)
text = require_replace(
    text,
    "All 8 pass exact Ord-body/Taproot/BIP340 verification, txid inclusion, separate",
    "All {bitcoin['count']} pass exact Ord-body/tag-5-metadata-or-verified-absence/Taproot/BIP340 verification, txid inclusion, separate",
    "markdown bitcoin proof wording",
)
p.write_text(text, encoding="utf-8")

# Make the parity projector future-safe: generated verification order and evidence
# manifest digest must stay synchronized after any later regeneration.
p = Path("scripts/finalize_bitcoin_12_parity.py")
text = p.read_text(encoding="utf-8")
text = require_replace(text, "import json\nfrom pathlib import Path\n", "import hashlib\nimport json\nfrom pathlib import Path\n", "finalizer hashlib import")
if "def canonical_source_digest" not in text:
    anchor = "\ndef verified_inputs() -> tuple[dict[str, Any], dict[str, Any]]:\n"
    helper = '''\n\ndef canonical_source_digest(doc: dict[str, Any]) -> str:\n    clone = dict(doc)\n    clone.pop("source_digest", None)\n    raw = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")\n    return hashlib.sha256(raw).hexdigest()[:16]\n'''
    text = require_replace(text, anchor, helper + anchor, "finalizer digest helper")
text = require_replace(
    text,
    '    bitcoin.pop("non_amending_ancillary", None)\n    dump(path, doc)\n\n\ndef update_evidence_manifest',
    '    bitcoin.pop("non_amending_ancillary", None)\n    if doc.get("verification_order"):\n        doc["verification_order"][0] = "verify the complete 12-item current Bitcoin proof annex v2 while preserving the historical v1 eight-item checkpoint"\n    dump(path, doc)\n\n\ndef update_evidence_manifest',
    "finalizer verification order",
)
text = require_replace(
    text,
    '    dump(path, doc)\n\n\ndef update_relationship_map()',
    '    doc["source_digest"] = canonical_source_digest(doc)\n    dump(path, doc)\n\n\ndef update_relationship_map()',
    "finalizer evidence digest",
)
p.write_text(text, encoding="utf-8")

# Sequence-4 publication is immutable history (8 Bitcoin), while validation of
# the moving current Git inventory must allow the verified v2 12-item state.
p = Path("scripts/current_baseline_publication_v4.py")
text = p.read_text(encoding="utf-8")
text = require_replace(
    text,
    '    require_equal(expected["evidence_sets"]["bitcoin_inscriptions"]["count"], 8, "inventory.bitcoin.count")\n',
    '    require_equal(expected["evidence_sets"]["bitcoin_inscriptions"]["count"], 12, "inventory.bitcoin.count")\n',
    "v4 validator current bitcoin count",
)
p.write_text(text, encoding="utf-8")

# Migrate current-state tests from historical v1 to verified current v2.
p = Path("tests/test_evidence_manifest_current_proof_state.py")
text = p.read_text(encoding="utf-8")
text = require_replace(text, 'bitcoin-inscription-proof-annex-v1" / "reports"', 'bitcoin-inscription-proof-annex-v2" / "reports"', "test BTC report")
text = require_replace(text, '        "offline_verifiable_and_immutable_checkpoint_v4",\n', '        "offline_verifiable_and_immutable_checkpoint_v4",\n        "offline_verifiable_current_bitcoin_v2_plus_published_repository_checkpoint_v4",\n', "test status")
text = require_replace(
    text,
    '    assert bitcoin["inscription_count"] == 8\n    assert bitcoin["canonical_originals"] == 3\n    assert bitcoin["non_amending_ancillary"] == 5\n    assert bitcoin["l1_inscription_content_and_taproot_binding"] == "PASS"\n    assert bitcoin["bip340_tapscript_signatures"] == 8\n',
    '    assert bitcoin["inscription_count"] == 12\n    assert bitcoin["pre_canonical_formation"] == 4\n    assert bitcoin["canonical_originals"] == 3\n    assert bitcoin["post_canonical_non_amending"] == 5\n    assert bitcoin["l1_inscription_content_metadata_and_taproot_binding"] == "PASS"\n    assert bitcoin["tag5_metadata_present"] == 1\n    assert bitcoin["tag5_metadata_absent_verified"] == 11\n    assert bitcoin["bip340_tapscript_signatures"] == 12\n',
    "test bitcoin current scope",
)
text = require_replace(text, '    assert bitcoin["bip141_witness_commitment_proofs"] == 8\n', '    assert bitcoin["bip141_witness_commitment_proofs"] == 12\n', "test BIP141 count")
text = require_replace(text, '    assert bitcoin["valid_pow_headers"] == 1160\n', '    assert bitcoin["valid_pow_headers"] == 1740\n', "test PoW count")
text = require_replace(text, '        assert preservation["live_repository_delta"]["status"] == "incorporated_into_published_checkpoint_v4"\n', '        assert preservation["live_repository_delta"]["status"] == "bitcoin_v2_verified_in_git_pending_next_repository_preservation_version"\n', "test live DOI delta")
text = require_replace(
    text,
    '    assert btc_report["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"]["status"] == bitcoin["l1_inscription_content_and_taproot_binding"]\n    assert btc_report["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"]["inscriptions"] == bitcoin["inscription_count"]\n',
    '    assert btc_report["L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING"]["status"] == bitcoin["l1_inscription_content_metadata_and_taproot_binding"]\n    assert btc_report["L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING"]["inscriptions"] == bitcoin["inscription_count"]\n    assert btc_report["L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING"]["tag5_metadata_present"] == bitcoin["tag5_metadata_present"]\n    assert btc_report["L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING"]["tag5_metadata_absent_verified"] == bitcoin["tag5_metadata_absent_verified"]\n',
    "test L1 v2 report",
)
p.write_text(text, encoding="utf-8")

p = Path("tests/test_evidence_relationship_profiles.py")
text = p.read_text(encoding="utf-8")
old_scope = '''    assert bitcoin_annex["scope"] == {\n        "canonical_originals": 3,\n        "non_amending_ancillary": 5,\n        "total": 8,\n    }\n'''
new_scope = '''    assert bitcoin_annex["scope"] == {\n        "pre_canonical_formation": 4,\n        "canonical_originals": 3,\n        "post_canonical_non_amending": 5,\n        "total": 12,\n    }\n'''
text = require_replace(text, old_scope, new_scope, "relationship proof scope")
text = text.replace("evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json", "evidence/bitcoin-inscription-proof-annex-v2/ANNEX-MANIFEST.json")
text = text.replace("evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json", "evidence/bitcoin-inscription-proof-annex-v2/reports/OFFLINE-VERIFICATION.json")
text = text.replace("evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py", "evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py")
p.write_text(text, encoding="utf-8")

# The current evidence manifest was already projected by PR #993; recompute its
# fail-closed self digest without re-running non-idempotent page migrations.
p = Path("api/evidence-manifest.json")
doc = json.loads(p.read_text(encoding="utf-8"))
clone = dict(doc)
clone.pop("source_digest", None)
raw = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
doc["source_digest"] = hashlib.sha256(raw).hexdigest()[:16]
p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("12-item CI reconciliation patches applied")
