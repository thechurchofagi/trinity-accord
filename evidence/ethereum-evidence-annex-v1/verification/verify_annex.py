#!/usr/bin/env python3
"""Fail-closed offline verifier for Ethereum Proof-Carrying Evidence Annex v1."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

ANNEX_DIR = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
GENESIS_TIME = 1606824023
SECONDS_PER_SLOT = 12
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def h2b(value: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"not hex: {value!r}")
    raw = value[2:]
    if len(raw) % 2:
        raw = "0" + raw
    return bytes.fromhex(raw)


def q(value: str | None) -> int:
    return 0 if value is None else int(value, 16)


def rlp_int(value: object, field: str) -> int:
    if not isinstance(value, bytes):
        raise ValueError(f"signed transaction {field} is not an RLP byte string")
    if len(value) > 1 and value[0] == 0:
        raise ValueError(f"signed transaction {field} is not minimally encoded")
    return int.from_bytes(value, "big")


def point_add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % SECP256K1_P == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = (3 * x1 * x1) * pow(2 * y1, -1, SECP256K1_P)
    else:
        slope = (y2 - y1) * pow((x2 - x1) % SECP256K1_P, -1, SECP256K1_P)
    slope %= SECP256K1_P
    x3 = (slope * slope - x1 - x2) % SECP256K1_P
    y3 = (slope * (x1 - x3) - y1) % SECP256K1_P
    return x3, y3


def point_mul(scalar: int, point):
    scalar %= SECP256K1_N
    result = None
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        scalar >>= 1
    return result


def recover_eth_address(message_hash: bytes, y_parity: int, r: int, s: int) -> str:
    if len(message_hash) != 32:
        raise ValueError("Ethereum signing hash must be 32 bytes")
    if y_parity not in (0, 1):
        raise ValueError("Ethereum signature yParity must be 0 or 1")
    if not (1 <= r < SECP256K1_N and 1 <= s <= SECP256K1_N // 2):
        raise ValueError("Ethereum signature r/s is out of range or not low-s")
    x = r
    alpha = (pow(x, 3, SECP256K1_P) + 7) % SECP256K1_P
    beta = pow(alpha, (SECP256K1_P + 1) // 4, SECP256K1_P)
    if pow(beta, 2, SECP256K1_P) != alpha:
        raise ValueError("Ethereum signature recovery point is not on secp256k1")
    y = beta if beta % 2 == y_parity else SECP256K1_P - beta
    recovery_point = (x, y)
    z = int.from_bytes(message_hash, "big")
    inverse_r = pow(r, -1, SECP256K1_N)
    public_key = point_mul(
        inverse_r,
        point_add(point_mul(s, recovery_point), point_mul(-z, SECP256K1_G)),
    )
    if public_key is None:
        raise ValueError("Ethereum signature recovered the point at infinity")
    # Verify the recovered key instead of treating recovery as sufficient.
    inverse_s = pow(s, -1, SECP256K1_N)
    check = point_add(
        point_mul((z * inverse_s) % SECP256K1_N, SECP256K1_G),
        point_mul((r * inverse_s) % SECP256K1_N, public_key),
    )
    if check is None or check[0] % SECP256K1_N != r:
        raise ValueError("Ethereum ECDSA signature verification failed")
    encoded = public_key[0].to_bytes(32, "big") + public_key[1].to_bytes(32, "big")
    return "0x" + keccak(encoded)[-20:].hex()


def decode_type2_transaction(raw: bytes) -> dict:
    if not raw or raw[0] != 2:
        raise ValueError("only an EIP-1559 type-2 signed transaction is accepted")
    decoded = rlp.decode(raw[1:], strict=True)
    if not isinstance(decoded, list) or len(decoded) != 12:
        raise ValueError("type-2 signed transaction must contain exactly 12 fields")
    chain_id = rlp_int(decoded[0], "chainId")
    to = decoded[5]
    data = decoded[7]
    if not isinstance(to, bytes) or len(to) != 20:
        raise ValueError("evidence transaction destination must be a 20-byte address")
    if not isinstance(data, bytes):
        raise ValueError("evidence transaction input is not bytes")
    y_parity = rlp_int(decoded[9], "yParity")
    r_value = rlp_int(decoded[10], "r")
    s_value = rlp_int(decoded[11], "s")
    signing_hash = keccak(b"\x02" + rlp.encode(decoded[:9]))
    return {
        "chain_id": chain_id,
        "to": "0x" + to.hex(),
        "value": rlp_int(decoded[6], "value"),
        "data": data,
        "y_parity": y_parity,
        "r": r_value,
        "s": s_value,
        "sender": recover_eth_address(signing_hash, y_parity, r_value, s_value),
        "signing_hash": "0x" + signing_hash.hex(),
    }


def receipt_status(encoded: bytes) -> int:
    if not encoded:
        raise ValueError("empty encoded receipt")
    payload = encoded[1:] if encoded[0] <= 0x7F else encoded
    decoded = rlp.decode(payload, strict=True)
    if not isinstance(decoded, list) or len(decoded) != 4:
        raise ValueError("receipt must contain exactly four fields")
    status = decoded[0]
    if not isinstance(status, bytes) or len(status) > 1:
        raise ValueError("receipt status is not an EIP-658 scalar")
    return int.from_bytes(status, "big")


def uint256(value: int) -> bytes:
    if value < 0 or value >= 1 << 256:
        raise ValueError("EIP-712 uint256 value is out of range")
    return value.to_bytes(32, "big")


def address_word(value: str) -> bytes:
    raw = h2b(value)
    if len(raw) != 20:
        raise ValueError("EIP-712 address must be 20 bytes")
    return b"\x00" * 12 + raw


def verify_eip712_authority_signature(
    authority_bytes: bytes, signature_record: dict, expected_signer: str
) -> dict:
    typed = signature_record.get("typedData")
    if not isinstance(typed, dict):
        raise ValueError("EIP-712 signature record lacks typedData")
    domain = typed.get("domain")
    expected_domain = {
        "name": "TrinityAccord",
        "version": "1",
        "chainId": 1,
        "verifyingContract": "0x0000000000000000000000000000000000000000",
    }
    if domain != expected_domain:
        raise ValueError("unexpected EIP-712 domain")
    expected_fields = [
        {"name": "sha256", "type": "bytes32"},
        {"name": "sha3_256", "type": "bytes32"},
        {"name": "version", "type": "string"},
        {"name": "createdAt", "type": "string"},
    ]
    if typed.get("types") != {"Attestation": expected_fields}:
        raise ValueError("unexpected EIP-712 Attestation type")
    if typed.get("primaryType") != "Attestation":
        raise ValueError("unexpected EIP-712 primary type")
    authority = json.loads(authority_bytes.decode("utf-8"))
    sha256 = hashlib.sha256(authority_bytes).hexdigest()
    sha3_256 = hashlib.sha3_256(authority_bytes).hexdigest()
    message = typed.get("message")
    expected_message = {
        "sha256": "0x" + sha256,
        "sha3_256": "0x" + sha3_256,
        "version": authority.get("version"),
        "createdAt": authority.get("created_at"),
    }
    if message != expected_message:
        raise ValueError("EIP-712 message is not the exact Authority Manifest digest tuple")
    domain_typehash = keccak(
        b"EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    )
    domain_hash = keccak(
        domain_typehash
        + keccak(domain["name"].encode())
        + keccak(domain["version"].encode())
        + uint256(domain["chainId"])
        + address_word(domain["verifyingContract"])
    )
    message_typehash = keccak(
        b"Attestation(bytes32 sha256,bytes32 sha3_256,string version,string createdAt)"
    )
    message_hash = keccak(
        message_typehash
        + h2b(message["sha256"])
        + h2b(message["sha3_256"])
        + keccak(message["version"].encode())
        + keccak(message["createdAt"].encode())
    )
    digest = keccak(b"\x19\x01" + domain_hash + message_hash)
    signature = h2b(signature_record.get("signature", ""))
    if len(signature) != 65:
        raise ValueError("EIP-712 signature must be 65 bytes")
    v = signature[64]
    y_parity = v - 27 if v in (27, 28) else v
    recovered = recover_eth_address(
        digest,
        y_parity,
        int.from_bytes(signature[:32], "big"),
        int.from_bytes(signature[32:64], "big"),
    )
    expected = expected_signer.lower()
    declared = [
        signature_record.get("signer"),
        signature_record.get("recovered"),
        signature_record.get("manifest_eth_address"),
    ]
    if recovered != expected or any(str(value).lower() != expected for value in declared):
        raise ValueError("EIP-712 signer does not match the declared Ethereum guardian")
    return {
        "recovered_signer": recovered,
        "typed_data_digest": "0x" + digest.hex(),
        "authority_sha256": sha256,
        "authority_sha3_256": sha3_256,
        "authority": authority,
    }


def verify_payload_binding(anchor: dict, tx_input: bytes) -> str:
    payloads = anchor.get("payloads", [])
    binding = anchor.get("payload_binding")
    files = [(REPO_ROOT / item["path"]).read_bytes() for item in payloads]
    if binding in {
        "exact_transaction_input_bytes",
        "exact_transaction_input_bytes_reused_from_bitcoin_mirror",
    }:
        if len(files) != 1 or tx_input != files[0]:
            raise ValueError("transaction input is not the exact declared payload bytes")
        return "exact_payload_bytes"
    if binding == "transaction_input_is_sha256_digest_of_declared_payload":
        if len(files) != 1 or tx_input != hashlib.sha256(files[0]).digest():
            raise ValueError("transaction input is not SHA-256(declared Authority Manifest)")
        return "sha256_of_declared_payload"
    if binding == "transaction_input_contains_verified_eip712_authority_binding":
        by_path = {item["path"]: data for item, data in zip(payloads, files)}
        authority_bytes = by_path.get("archive/authority-manifest/authority.jcs.json")
        signature_bytes = by_path.get("archive/authority-manifest/signature.json")
        if authority_bytes is None or signature_bytes is None:
            raise ValueError("EIP-712 binding payload set is incomplete")
        signature_record = json.loads(signature_bytes.decode("utf-8"))
        result = verify_eip712_authority_signature(
            authority_bytes, signature_record, anchor["expected_from"]
        )
        try:
            text = tx_input.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("EIP-712 record transaction input is not UTF-8") from exc
        required_values = [
            result["authority_sha256"],
            result["authority_sha3_256"],
            signature_record["signature"],
            signature_record["signer"],
        ]
        authority = result["authority"]
        for record in authority.get("arweave", {}).get("documents", []):
            required_values.extend([record["txid"], record["ar_sha256"]])
        for record in authority.get("ethereum", {}).get("attestations", []):
            required_values.extend([record["tx_hash"], record["input_sha256"]])
        lowered = text.lower()
        missing = [value for value in required_values if str(value).lower() not in lowered]
        if missing:
            raise ValueError(f"EIP-712 on-chain record omits {len(missing)} Authority Manifest value(s)")
        return "verified_eip712_authority_and_cross-system_record"
    if binding == "witness_metadata_and_referenced_signed_object_not_raw_transaction_input":
        by_path = {item["path"]: data for item, data in zip(payloads, files)}
        witness_bytes = by_path.get("archive/eth-witness/eth-witness.json")
        signature_bytes = by_path.get("archive/btc-signature/btc-signature.json")
        if witness_bytes is None or signature_bytes is None:
            raise ValueError("BTC signature witness payload set is incomplete")
        witness = json.loads(witness_bytes.decode("utf-8"))
        signature = json.loads(signature_bytes.decode("utf-8"))["bitcoin_signature"]
        if witness.get("tx_hash", "").lower() != anchor["tx_hash"].lower():
            raise ValueError("ETH witness transaction hash mismatch")
        if str(witness.get("chainId")) != "1":
            raise ValueError("ETH witness chainId mismatch")
        if str(witness.get("from", "")).lower() != anchor["expected_from"].lower():
            raise ValueError("ETH witness sender mismatch")
        if str(witness.get("to", "")).lower() != anchor["expected_to"].lower():
            raise ValueError("ETH witness destination mismatch")
        try:
            text = tx_input.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("BTC signature witness transaction input is not UTF-8") from exc
        required = {
            "file_sha256": hashlib.sha256(signature_bytes).hexdigest(),
            "address": signature["address"],
            "pubkey_xonly": signature["pubkey_xonly"],
            "message_sha256": signature["message_sha256"],
            "signature": signature["signature"],
            "boundary": signature["boundary"],
        }
        expected_ar = anchor.get("semantic_binding", {}).get("arweave_txid")
        if not expected_ar:
            raise ValueError("BTC signature witness lacks a manifest-bound Arweave TxID")
        required["AR TxID"] = expected_ar
        if any(f"{key}={value}" not in text for key, value in required.items()):
            raise ValueError("BTC signature witness transaction input field mismatch")
        return "btc_signature_object_and_arweave_pointer_record"
    raise ValueError(f"unsupported payload binding: {binding!r}")


def execution_header_hash(block: dict) -> bytes:
    fields = [
        h2b(block["parentHash"]), h2b(block["sha3Uncles"]), h2b(block["miner"]),
        h2b(block["stateRoot"]), h2b(block["transactionsRoot"]), h2b(block["receiptsRoot"]),
        h2b(block["logsBloom"]), q(block["difficulty"]), q(block["number"]), q(block["gasLimit"]),
        q(block["gasUsed"]), q(block["timestamp"]), h2b(block["extraData"]), h2b(block["mixHash"]), h2b(block["nonce"]),
    ]
    for name, conv in [
        ("baseFeePerGas", q), ("withdrawalsRoot", h2b), ("blobGasUsed", q), ("excessBlobGas", q),
        ("parentBeaconBlockRoot", h2b), ("requestsHash", h2b),
    ]:
        if block.get(name) is not None:
            fields.append(conv(block[name]))
    return keccak(rlp.encode(fields))


def build_root(values: list[bytes]) -> bytes:
    trie = HexaryTrie(db={})
    for i, value in enumerate(values):
        trie[rlp.encode(i)] = value
    return trie.root_hash


def merkleize_chunks(chunks: list[bytes]) -> bytes:
    if any(len(x) != 32 for x in chunks):
        raise ValueError("SSZ chunk must be 32 bytes")
    n = 1
    while n < len(chunks):
        n *= 2
    nodes = chunks + [b"\x00" * 32] * (n - len(chunks))
    while len(nodes) > 1:
        nodes = [hashlib.sha256(nodes[i] + nodes[i + 1]).digest() for i in range(0, len(nodes), 2)]
    return nodes[0]


def beacon_header_root(message: dict) -> str:
    fields = [
        int(message["slot"]).to_bytes(8, "little") + b"\x00" * 24,
        int(message["proposer_index"]).to_bytes(8, "little") + b"\x00" * 24,
        h2b(message["parent_root"]), h2b(message["state_root"]), h2b(message["body_root"]),
    ]
    return "0x" + merkleize_chunks(fields).hex()


def verify_single_ssz_proof(proof: dict, expected_root: str) -> None:
    node = h2b(proof["leaf"])
    gindex = int(proof["gindex"])
    if gindex <= 1:
        raise ValueError("invalid SSZ generalized index")
    for witness_hex in proof["witnesses"]:
        witness = h2b(witness_hex)
        if len(witness) != 32:
            raise ValueError("invalid SSZ witness length")
        node = hashlib.sha256((witness + node) if (gindex & 1) else (node + witness)).digest()
        gindex //= 2
    if gindex != 1:
        raise ValueError("SSZ proof depth does not terminate at root")
    if "0x" + node.hex() != expected_root.lower():
        raise ValueError("SSZ proof root mismatch")


def verify_checkpoint_provider_quorum(
    checkpoint: dict, observations: object
) -> tuple[int, int]:
    """Require declared quorum counts to represent distinct matching providers."""
    if not isinstance(observations, list):
        raise ValueError("trusted finalized root observations are not a list")
    checkpoint_root = str(checkpoint.get("root", "")).lower()
    checkpoint_slot = int(checkpoint.get("slot", -1))
    votes = int(checkpoint.get("matching_provider_votes", 0))
    finalized_votes = int(checkpoint.get("finalized_provider_votes", 0))
    matching_providers: set[str] = set()
    finalized_providers: set[str] = set()
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("trusted finalized root observation is not an object")
        provider = str(observation.get("provider", "")).strip()
        if not provider:
            raise ValueError("trusted finalized root observation provider is missing")
        matches = (
            str(observation.get("root", "")).lower() == checkpoint_root
            and int(observation.get("observed_slot", -1)) == checkpoint_slot
            and observation.get("canonical") is True
        )
        if matches:
            matching_providers.add(provider)
            if (
                observation.get("finalized") is True
                and observation.get("execution_optimistic") is False
            ):
                finalized_providers.add(provider)
    if votes < 2 or len(matching_providers) < votes:
        raise ValueError("trusted finalized root provenance quorum mismatch")
    if (
        finalized_votes < 1
        or finalized_votes > votes
        or len(finalized_providers) < finalized_votes
    ):
        raise ValueError("trusted finalized root finalized-provenance mismatch")
    return votes, finalized_votes


def bound_proof_path(anchor: dict, key: str, filename: str) -> tuple[pathlib.Path, dict]:
    txh = anchor["tx_hash"].lower()
    expected_rel = f"evidence/ethereum-evidence-annex-v1/proof-material/{txh}/{filename}"
    record = anchor.get("proof_material", {}).get(key)
    if not isinstance(record, dict):
        raise ValueError(f"missing manifest proof binding {key}")
    if record.get("path") != expected_rel:
        raise ValueError(f"unexpected {key} path")
    path = REPO_ROOT / expected_rel
    if not path.is_file():
        raise ValueError(f"missing {key} file")
    size = path.stat().st_size
    digest = sha256_file(path)
    if size != record.get("size") or digest != record.get("sha256"):
        raise ValueError(f"{key} size/SHA-256 binding mismatch")
    return path, {"path": expected_rel, "size": size, "sha256": digest, "status": "PASS"}


def verify_l2(anchor: dict) -> tuple[dict, dict]:
    txh = anchor["tx_hash"].lower()
    path, byte_check = bound_proof_path(anchor, "l2_execution_witness", "L2-execution-witness.json")
    witness = json.loads(path.read_text(encoding="utf-8"))
    if witness.get("schema") != "trinityaccord.ethereum-execution-inclusion-witness.v1":
        raise ValueError("unexpected L2 witness schema")
    if witness.get("target_tx_hash", "").lower() != txh:
        raise ValueError("L2 target transaction mismatch")
    block = witness["block"]
    if block["hash"].lower() != anchor["execution_reference"]["block_hash"].lower():
        raise ValueError("L2 execution block hash mismatch")
    if execution_header_hash(block) != h2b(block["hash"]):
        raise ValueError("execution header hash mismatch")
    reference = anchor["execution_reference"]
    if q(block["number"]) != int(reference["block_number"]):
        raise ValueError("L2 execution block number mismatch")
    if q(block["timestamp"]) != int(reference["block_timestamp_unix"]):
        raise ValueError("L2 execution block timestamp mismatch")
    raw_txs = [h2b(x) for x in witness["raw_transactions"]]
    encoded_receipts = [h2b(x) for x in witness["encoded_receipts"]]
    tx_hashes = [x.lower() for x in block["transactions"]]
    if len(raw_txs) != len(tx_hashes) or len(encoded_receipts) != len(tx_hashes):
        raise ValueError("L2 witness list length mismatch")
    for expected, raw in zip(tx_hashes, raw_txs):
        if "0x" + keccak(raw).hex() != expected:
            raise ValueError(f"raw transaction hash mismatch: {expected}")
    if "0x" + build_root(raw_txs).hex() != block["transactionsRoot"].lower():
        raise ValueError("transactions trie root mismatch")
    if "0x" + build_root(encoded_receipts).hex() != block["receiptsRoot"].lower():
        raise ValueError("receipts trie root mismatch")
    idx = int(witness["target_transaction_index"])
    if idx < 0 or idx >= len(tx_hashes) or tx_hashes[idx] != txh:
        raise ValueError("target transaction index mismatch")
    if idx != int(reference["transaction_index"]):
        raise ValueError("target transaction index differs from execution reference")
    decoded = decode_type2_transaction(raw_txs[idx])
    expected_chain_id = int(anchor.get("chain_id", -1))
    if expected_chain_id != 1 or decoded["chain_id"] != expected_chain_id:
        raise ValueError("signed transaction chainId mismatch")
    if decoded["sender"] != str(anchor.get("expected_from", "")).lower():
        raise ValueError("signed transaction sender mismatch")
    if decoded["to"] != str(anchor.get("expected_to", "")).lower():
        raise ValueError("signed transaction destination mismatch")
    if decoded["value"] != int(anchor.get("expected_value_wei", "-1")):
        raise ValueError("signed transaction value mismatch")
    tx_input = decoded["data"]
    if len(tx_input) != int(anchor.get("input_len", -1)):
        raise ValueError("signed transaction input length mismatch")
    input_sha256 = hashlib.sha256(tx_input).hexdigest()
    if input_sha256 != anchor.get("input_sha256"):
        raise ValueError("signed transaction input SHA-256 mismatch")
    declared_receipt_status = q(reference.get("receipt_status"))
    actual_receipt_status = receipt_status(encoded_receipts[idx])
    if declared_receipt_status != 1 or actual_receipt_status != declared_receipt_status:
        raise ValueError("target receipt does not prove successful execution")
    payload_binding = verify_payload_binding(anchor, tx_input)
    return ({
        "tx_hash": txh,
        "status": "PASS",
        "block_hash": block["hash"].lower(),
        "block_number": q(block["number"]),
        "block_timestamp_unix": q(block["timestamp"]),
        "transaction_index": idx,
        "chain_id": decoded["chain_id"],
        "sender": decoded["sender"],
        "destination": decoded["to"],
        "value_wei": str(decoded["value"]),
        "input_len": len(tx_input),
        "input_sha256": input_sha256,
        "receipt_status": actual_receipt_status,
        "payload_binding": payload_binding,
        "transactions": len(tx_hashes),
        "transactions_root": block["transactionsRoot"].lower(),
        "receipts_root": block["receiptsRoot"].lower(),
    }, byte_check)


def verify_l3(anchor: dict, l2: dict) -> tuple[dict, dict]:
    txh = anchor["tx_hash"].lower()
    path, byte_check = bound_proof_path(anchor, "l3_consensus_witness", "L3-consensus-witness.json")
    witness = json.loads(path.read_text(encoding="utf-8"))
    if witness.get("schema") != "trinityaccord.ethereum-consensus-finality-witness.v1":
        raise ValueError("unexpected L3 witness schema")
    if witness.get("target_tx_hash", "").lower() != txh:
        raise ValueError("L3 target transaction mismatch")
    if witness.get("execution_block_hash", "").lower() != l2["block_hash"]:
        raise ValueError("L3 execution block hash mismatch")
    target = witness["target_beacon_header"]
    target_root = beacon_header_root(target["message"]).lower()
    if target_root != target["root"].lower():
        raise ValueError("target beacon header root mismatch")
    timestamp = int(anchor["execution_reference"]["block_timestamp_unix"])
    if timestamp < GENESIS_TIME or (timestamp - GENESIS_TIME) % SECONDS_PER_SLOT:
        raise ValueError("execution timestamp does not map to an exact Beacon slot")
    expected_slot = (timestamp - GENESIS_TIME) // SECONDS_PER_SLOT
    if int(target["message"]["slot"]) != expected_slot or int(witness["target_beacon_slot"]) != expected_slot:
        raise ValueError("target beacon slot mismatch")
    leaf_proof = witness["execution_block_hash_to_body_root"]
    if leaf_proof["leaf"].lower() != l2["block_hash"]:
        raise ValueError("SSZ execution block-hash leaf mismatch")
    body_root = target["message"]["body_root"].lower()
    if leaf_proof["body_root"].lower() != body_root:
        raise ValueError("SSZ proof body root declaration mismatch")
    verify_single_ssz_proof(leaf_proof, body_root)

    checkpoint = witness["trusted_finalized_beacon_root"]
    trust_model = checkpoint.get("trust_model", "")
    if checkpoint.get("schema") != "trinityaccord.ethereum-trusted-finalized-beacon-root.v1":
        raise ValueError("unexpected trusted finalized Beacon-root schema")
    if "weak-subjectivity" not in trust_model or "explicit" not in trust_model:
        raise ValueError("trusted finalized root assumption is not explicit")
    if "provenance only" not in trust_model:
        raise ValueError("provider provenance boundary is not explicit")
    checkpoint_root = checkpoint["root"].lower()
    checkpoint_slot = int(checkpoint["slot"])
    if checkpoint_slot <= expected_slot:
        raise ValueError("trusted finalized root must descend from target slot")
    observations = witness.get("checkpoint_observations", [])
    votes, finalized_votes = verify_checkpoint_provider_quorum(checkpoint, observations)

    expected = checkpoint_root
    chain = witness.get("checkpoint_to_target_parent_chain", [])
    if not chain:
        raise ValueError("empty checkpoint ancestry chain")
    for item in chain:
        computed = beacon_header_root(item["message"]).lower()
        if computed != item["root"].lower() or computed != expected:
            raise ValueError("checkpoint ancestry header root mismatch")
        expected = item["message"]["parent_root"].lower()
    if expected != target_root:
        raise ValueError("trusted finalized Beacon root is not linked to target Beacon block")
    return ({
        "tx_hash": txh,
        "status": "PASS",
        "target_beacon_root": target_root,
        "trusted_finalized_beacon_root": checkpoint_root,
        "trusted_finalized_slot": checkpoint_slot,
        "trusted_finalized_epoch": int(checkpoint["epoch"]),
        "ancestor_headers": len(chain),
        "matching_provider_votes": votes,
        "finalized_provider_votes": finalized_votes,
        "trust_boundary": "PASS is conditional on the explicitly declared weak-subjectivity trusted finalized Beacon root; provider agreement/finalized fields are provenance only.",
    }, byte_check)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        help="Also write the canonical JSON report to this path (used to refresh the checked-in report).",
    )
    args = parser.parse_args(argv)
    failures: list[str] = []
    checks: list[dict] = []
    proof_byte_checks: list[dict] = []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "failures": [f"manifest parse: {exc}"]}, indent=2))
        return 1

    if data.get("schema") != "trinityaccord.ethereum-proof-carrying-evidence-annex.v1":
        failures.append("unexpected schema")
    if data.get("network", {}).get("chain_id") != 1:
        failures.append("network chain_id must be 1")
    boundary = data.get("authority_boundary", {})
    if boundary.get("canonical_authority") != "three Bitcoin Originals only":
        failures.append("canonical authority boundary changed")
    if boundary.get("no_authority_escalation") is not True:
        failures.append("no_authority_escalation must be true")

    anchors = data.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        failures.append("anchors missing")
        anchors = []
    txs = [a.get("tx_hash") for a in anchors]
    if len(txs) != len(set(txs)):
        failures.append("duplicate transaction hash")
    if len(anchors) != 12:
        failures.append(f"expected 12 audited non-NFT evidence anchors, found {len(anchors)}")

    byte_pass = True
    l2_pass = True
    l3_pass = True
    l2_checks = []
    l3_checks = []
    for a in anchors:
        tx = a.get("tx_hash", "")
        if not (isinstance(tx, str) and tx.startswith("0x") and len(tx) == 66):
            failures.append(f"{a.get('id')}: invalid tx hash")
        payloads = a.get("payloads", [])
        if not payloads:
            failures.append(f"{tx}: no preserved payload mapping")
            byte_pass = False
        for p in payloads:
            rel = p.get("path")
            fp = REPO_ROOT / rel if rel else None
            result = {"tx_hash": tx, "path": rel}
            if not fp or not fp.is_file():
                result.update({"status": "FAIL", "reason": "missing"})
                failures.append(f"{tx}: missing {rel}")
                byte_pass = False
            else:
                size = fp.stat().st_size
                digest = sha256_file(fp)
                result.update({"size": size, "sha256": digest})
                if size != p.get("size") or digest != p.get("sha256"):
                    result.update({"status": "FAIL", "reason": "size_or_sha256_mismatch"})
                    failures.append(f"{tx}: byte mismatch {rel}")
                    byte_pass = False
                else:
                    result["status"] = "PASS"
            checks.append(result)
        try:
            if a.get("proof_status", {}).get("L2_EXECUTION_INCLUSION") != "PASS":
                raise ValueError("manifest does not declare L2 PASS")
            l2, l2_bytes = verify_l2(a)
            l2_checks.append(l2)
            proof_byte_checks.append({"tx_hash": tx, "level": "L2", **l2_bytes})
        except Exception as exc:
            l2_pass = False
            failures.append(f"{tx}: L2 {exc}")
            continue
        try:
            if a.get("proof_status", {}).get("L3_CONSENSUS_FINALITY") != "PASS":
                raise ValueError("manifest does not declare L3 PASS")
            l3, l3_bytes = verify_l3(a, l2)
            l3_checks.append(l3)
            proof_byte_checks.append({"tx_hash": tx, "level": "L3", **l3_bytes})
        except Exception as exc:
            l3_pass = False
            failures.append(f"{tx}: L3 {exc}")

    summary = {
        "schema": "trinityaccord.ethereum-annex-offline-verification.v3",
        "result": "PASS" if not failures else "FAIL",
        "L1_BYTE_INTEGRITY": "PASS" if byte_pass else "FAIL",
        "L2_EXECUTION_INCLUSION": "PASS" if l2_pass and len(l2_checks) == len(anchors) else "FAIL",
        "L3_CONSENSUS_FINALITY": "PASS" if l3_pass and len(l3_checks) == len(anchors) else "FAIL",
        "anchors": len(anchors),
        "payload_checks": len(checks),
        "proof_byte_checks": proof_byte_checks,
        "checks": checks,
        "l2_checks": l2_checks,
        "l3_checks": l3_checks,
        "failures": failures,
        "claim_boundary": "L2 PASS is offline execution inclusion bound to the execution block hash. L3 PASS links that execution block hash through an SSZ Beacon-body proof and Beacon parent-root ancestry to an explicit weak-subjectivity trusted finalized Beacon root. Provider agreement/finalized fields are provenance only; the trusted-root finality assumption is explicit, and the result is not a trust-free real-world clock attestation.",
    }
    rendered = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = pathlib.Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
