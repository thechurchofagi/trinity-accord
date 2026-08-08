from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "evidence/bitcoin-inscription-proof-annex-v1"
VERIFIER = ANNEX / "verification/verify_annex.py"
REPORT = ANNEX / "reports/OFFLINE-VERIFICATION.json"


def load_verifier():
    spec = importlib.util.spec_from_file_location("bitcoin_inscription_annex_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(VERIFIER.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def load_primitives():
    path = ANNEX / "verification/bitcoin_proof_primitives_v1.py"
    spec = importlib.util.spec_from_file_location("bitcoin_inscription_annex_primitives", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def load_cases():
    module = load_verifier()
    manifest = json.loads((ANNEX / "ANNEX-MANIFEST.json").read_text(encoding="utf-8"))
    cases = []
    for anchor in manifest["anchors"]:
        proof = json.loads((ROOT / anchor["proof_material"]["path"]).read_text(encoding="utf-8"))
        cases.append((module, anchor, proof))
    return cases


def test_checked_in_offline_report_is_current_and_passes_without_network():
    completed = subprocess.run(
        [sys.executable, str(VERIFIER)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={"PATH": str(Path(sys.executable).parent)},
    )
    generated = json.loads(completed.stdout)
    checked = json.loads(REPORT.read_text(encoding="utf-8"))
    assert generated == checked
    assert generated["result"] == "PASS"
    assert generated["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"] == {
        "status": "PASS",
        "inscriptions": 8,
        "canonical_originals": 3,
        "non_amending_ancillary": 5,
    }
    assert generated["L2_BLOCK_AND_WITNESS_INCLUSION"]["txid_merkle_proofs"] == 8
    assert generated["L2_BLOCK_AND_WITNESS_INCLUSION"]["bip141_witness_commitment_proofs"] == 8
    assert generated["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]["anchors"] == 8
    assert generated["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]["valid_pow_headers"] == 1160


def test_frozen_bip340_primitive_matches_official_vector_zero():
    primitives = load_primitives()
    public_key = bytes.fromhex(
        "F9308A019258C31049344F85F89D5229B531C845836F99B08601F113BCE036F9"
    )
    message = bytes(32)
    signature = bytes.fromhex(
        "E907831F80848D1069A5371B402410364BDF1C5F8307B0084C55F1CE2DCA8215"
        "25F66A4A85EA8B71E482A74F382D2CE5EBEEE8FDB2172F477DF4900D310536C0"
    )
    primitives.verify_bip340_signature(public_key, message, signature)
    with pytest.raises(ValueError, match="Schnorr signature"):
        primitives.verify_bip340_signature(
            public_key, message, signature[:-1] + bytes([signature[-1] ^ 1])
        )


def test_all_eight_real_witnesses_recompute_l1_l2_l3():
    cases = load_cases()
    assert len(cases) == 8
    for module, anchor, proof in cases:
        l1 = module.verify_l1(anchor, proof)
        assert l1["status"] == "PASS"
        assert l1["tapscript_signature_status"] == "PASS"
        assert len(l1["tapscript_public_key"]) == 64
        assert len(l1["taproot_sighash"]) == 64
        l2 = module.verify_l2(anchor, proof, l1)
        assert l2["status"] == "PASS"
        l3 = module.verify_l3(anchor, proof, l2)
        assert l3["status"] == "PASS"
        assert l3["descendant_confirmation_depth"] == 144
        assert l3["valid_pow_headers"] == 145


def test_exact_closed_set_and_authority_boundary():
    manifest = json.loads((ANNEX / "ANNEX-MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["closed_set"] == {
        "inscription_count": 8,
        "canonical_originals": 3,
        "non_amending_ancillary": 5,
        "source": "archive/authority-manifest/authority.jcs.json",
    }
    assert manifest["authority_boundary"]["canonical_authority"] == "three Bitcoin Originals only"
    assert manifest["authority_boundary"]["proof_annex_is_non_amending"] is True
    assert manifest["verification_implementation"]["network_required_for_verification"] is False
    assert manifest["verification_implementation"]["runtime"] == "Python 3 standard library only"
    assert manifest["preservation_policy"]["proof_material_git_tracked"] is True
    assert "must not" in manifest["preservation_policy"]["current_published_repository_doi_boundary"]


def test_all_reveal_bodies_are_exactly_bound_to_mirrors_and_one_destination():
    for module, anchor, proof in load_cases():
        l1 = module.verify_l1(anchor, proof)
        assert l1["mirror_binding_method"] == "exact_bytes"
        assert l1["destination_address"] == "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"
        assert l1["content_type"] == "text/plain;charset=utf-8"


def test_legacy_node_entrypoint_uses_same_offline_proof_without_fetch():
    program = """
      globalThis.fetch = () => { throw new Error('network access is forbidden'); };
      const { runBitcoinInscriptionOfflineVerification } = await import(
        './scripts/bitcoin-inscription-offline-adapter.mjs'
      );
      process.stdout.write(JSON.stringify(runBitcoinInscriptionOfflineVerification()));
    """
    node = shutil.which("node")
    assert node
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", program],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHON": sys.executable},
    )
    result = json.loads(completed.stdout)
    assert result["bitcoin_tx_anchor_pass"] is True
    assert result["bitcoin_time_anchor_pass"] is True
    assert result["verification_mode"] == "offline_proof_carrying_annex"
    assert result["network_required_for_verification"] is False
    assert result["bitcoin_anchors_pass"] == 8
    assert result["bip340_tapscript_signatures"] == 8
    assert result["witness_commitment_verified_count"] == 8
    assert result["valid_pow_headers"] == 1160


def test_public_mirror_index_exposes_same_offline_annex_state():
    index = json.loads((ROOT / "api/bitcoin-inscription-mirror-index.json").read_text(encoding="utf-8"))
    proof = index["cryptographic_proof_annex"]
    assert proof["status"] == "PASS"
    assert proof["inscription_count"] == 8
    assert proof["network_required_for_verification"] is False
    assert proof["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"] == "PASS"
    assert proof["bip340_tapscript_signatures"] == 8
    assert proof["L2_BLOCK_AND_WITNESS_INCLUSION"] == "PASS"
    assert proof["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"] == "PASS"
    assert len(index["records"]) == 8
    for record in index["records"]:
        assert record["inscription"]["source_address_role"] == "reveal_destination_p2tr_address"
        chain = record["chain_verification"]
        assert chain["verification_method"] == "offline_proof_carrying_annex_v1"
        assert chain["network_required_for_verification"] is False
        assert set(chain["proof_status"].values()) == {"PASS"}
