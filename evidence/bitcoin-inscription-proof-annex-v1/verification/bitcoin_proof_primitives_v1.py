#!/usr/bin/env python3
"""Frozen, dependency-free Bitcoin proof primitives for the inscription annex.

The module deliberately implements only the consensus/data structures needed by
the checked-in v1 witnesses: Bitcoin transaction/block decoding, txid/wtxid
Merkle proofs, BIP141 witness commitments, BIP340 Schnorr validation,
BIP341/BIP342 Taproot script-path signature validation, Taproot script
commitments, Ord inscription envelope extraction, Bech32m addresses, and
header PoW checks.
It is not a general Bitcoin consensus implementation.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
MAINNET_POW_LIMIT = 0x00000000FFFF0000000000000000000000000000000000000000000000000000
BECH32M_CONST = 0x2BC830A3
BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def dsha256(data: bytes) -> bytes:
    return sha256(sha256(data))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def display_hash(raw_digest: bytes) -> str:
    if len(raw_digest) != 32:
        raise ValueError("hash digest must be 32 bytes")
    return raw_digest[::-1].hex()


def internal_hash(value: str) -> bytes:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("display hash must be 64 hex characters")
    try:
        return bytes.fromhex(value)[::-1]
    except ValueError as exc:
        raise ValueError("display hash is not hexadecimal") from exc


def encode_compact_size(value: int) -> bytes:
    if value < 0:
        raise ValueError("compact size cannot be negative")
    if value < 0xFD:
        return bytes([value])
    if value <= 0xFFFF:
        return b"\xfd" + value.to_bytes(2, "little")
    if value <= 0xFFFFFFFF:
        return b"\xfe" + value.to_bytes(4, "little")
    if value <= 0xFFFFFFFFFFFFFFFF:
        return b"\xff" + value.to_bytes(8, "little")
    raise ValueError("compact size exceeds uint64")


@dataclass
class Reader:
    data: bytes
    offset: int = 0

    def read(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            raise ValueError("truncated binary data")
        value = self.data[self.offset : self.offset + size]
        self.offset += size
        return value

    def read_uint(self, size: int) -> int:
        return int.from_bytes(self.read(size), "little")

    def read_compact_size(self) -> int:
        prefix = self.read(1)[0]
        if prefix < 0xFD:
            return prefix
        if prefix == 0xFD:
            value = self.read_uint(2)
            if value < 0xFD:
                raise ValueError("non-minimal compact size")
            return value
        if prefix == 0xFE:
            value = self.read_uint(4)
            if value <= 0xFFFF:
                raise ValueError("non-minimal compact size")
            return value
        value = self.read_uint(8)
        if value <= 0xFFFFFFFF:
            raise ValueError("non-minimal compact size")
        return value

    def read_varbytes(self) -> bytes:
        return self.read(self.read_compact_size())

    def eof(self) -> bool:
        return self.offset == len(self.data)


def _serialize_input(txin: dict[str, Any]) -> bytes:
    return (
        txin["prev_txid_internal"]
        + int(txin["prev_vout"]).to_bytes(4, "little")
        + encode_compact_size(len(txin["script_sig"]))
        + txin["script_sig"]
        + int(txin["sequence"]).to_bytes(4, "little")
    )


def _serialize_output(txout: dict[str, Any]) -> bytes:
    return (
        int(txout["value"]).to_bytes(8, "little")
        + encode_compact_size(len(txout["script_pubkey"]))
        + txout["script_pubkey"]
    )


def read_transaction(reader: Reader) -> dict[str, Any]:
    start = reader.offset
    version = reader.read_uint(4)
    segwit = False
    if reader.offset + 2 <= len(reader.data) and reader.data[reader.offset] == 0:
        marker = reader.read(1)[0]
        flag = reader.read(1)[0]
        if marker != 0 or flag != 1:
            raise ValueError("unsupported SegWit marker/flag")
        segwit = True

    input_count = reader.read_compact_size()
    if input_count < 1:
        raise ValueError("transaction has no inputs")
    inputs: list[dict[str, Any]] = []
    for _ in range(input_count):
        prev_internal = reader.read(32)
        prev_vout = reader.read_uint(4)
        script_sig = reader.read_varbytes()
        sequence = reader.read_uint(4)
        inputs.append(
            {
                "prev_txid_internal": prev_internal,
                "prev_txid": prev_internal[::-1].hex(),
                "prev_vout": prev_vout,
                "script_sig": script_sig,
                "sequence": sequence,
                "witness": [],
            }
        )

    output_count = reader.read_compact_size()
    outputs: list[dict[str, Any]] = []
    for index in range(output_count):
        outputs.append(
            {
                "index": index,
                "value": reader.read_uint(8),
                "script_pubkey": reader.read_varbytes(),
            }
        )

    if segwit:
        any_witness = False
        for txin in inputs:
            item_count = reader.read_compact_size()
            witness = [reader.read_varbytes() for _ in range(item_count)]
            txin["witness"] = witness
            any_witness = any_witness or bool(witness)
        if not any_witness:
            raise ValueError("superfluous SegWit serialization")

    locktime = reader.read_uint(4)
    raw = reader.data[start : reader.offset]
    stripped = (
        version.to_bytes(4, "little")
        + encode_compact_size(len(inputs))
        + b"".join(_serialize_input(item) for item in inputs)
        + encode_compact_size(len(outputs))
        + b"".join(_serialize_output(item) for item in outputs)
        + locktime.to_bytes(4, "little")
    )
    txid = display_hash(dsha256(stripped))
    wtxid = display_hash(dsha256(raw))
    return {
        "version": version,
        "segwit": segwit,
        "inputs": inputs,
        "outputs": outputs,
        "locktime": locktime,
        "raw": raw,
        "stripped": stripped,
        "txid": txid,
        "wtxid": wtxid,
    }


def parse_transaction(raw: bytes) -> dict[str, Any]:
    reader = Reader(raw)
    tx = read_transaction(reader)
    if not reader.eof():
        raise ValueError("trailing transaction bytes")
    return tx


def parse_transaction_hex(raw_hex: str) -> dict[str, Any]:
    if not isinstance(raw_hex, str) or len(raw_hex) % 2:
        raise ValueError("transaction hex is invalid")
    try:
        return parse_transaction(bytes.fromhex(raw_hex))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("transaction hex is invalid") from exc


def parse_block(raw: bytes) -> dict[str, Any]:
    reader = Reader(raw)
    header = reader.read(80)
    count = reader.read_compact_size()
    if count < 1:
        raise ValueError("block has no transactions")
    transactions = [read_transaction(reader) for _ in range(count)]
    if not reader.eof():
        raise ValueError("trailing block bytes")
    return {"header": header, "transactions": transactions}


def parse_header(header: bytes) -> dict[str, Any]:
    if len(header) != 80:
        raise ValueError("Bitcoin header must be 80 bytes")
    return {
        "version": int.from_bytes(header[0:4], "little"),
        "previous_block_hash": header[4:36][::-1].hex(),
        "merkle_root": header[36:68][::-1].hex(),
        "timestamp": int.from_bytes(header[68:72], "little"),
        "bits": int.from_bytes(header[72:76], "little"),
        "nonce": int.from_bytes(header[76:80], "little"),
        "hash": display_hash(dsha256(header)),
        "header_hex": header.hex(),
    }


def header_from_fields(block: dict[str, Any]) -> bytes:
    required = ["version", "previousblockhash", "merkle_root", "timestamp", "bits", "nonce"]
    if any(key not in block for key in required):
        raise ValueError("block metadata is missing header fields")
    header = (
        int(block["version"]).to_bytes(4, "little", signed=False)
        + internal_hash(str(block["previousblockhash"]))
        + internal_hash(str(block["merkle_root"]))
        + int(block["timestamp"]).to_bytes(4, "little")
        + int(block["bits"]).to_bytes(4, "little")
        + int(block["nonce"]).to_bytes(4, "little")
    )
    observed = parse_header(header)
    if observed["hash"] != str(block.get("id", "")).lower():
        raise ValueError("reconstructed header hash does not match provider block id")
    return header


def target_from_bits(bits: int) -> int:
    exponent = bits >> 24
    mantissa = bits & 0x007FFFFF
    if bits & 0x00800000 or mantissa == 0:
        raise ValueError("invalid compact PoW target")
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    if target <= 0 or target > MAINNET_POW_LIMIT:
        raise ValueError("PoW target exceeds Bitcoin mainnet limit")
    return target


def verify_header_pow(header: bytes) -> dict[str, Any]:
    parsed = parse_header(header)
    target = target_from_bits(parsed["bits"])
    value = int.from_bytes(dsha256(header), "little")
    if value > target:
        raise ValueError("block header does not satisfy declared PoW target")
    return {
        **parsed,
        "target_hex": f"{target:064x}",
        "work": (1 << 256) // (target + 1),
    }


def merkle_root(hashes: list[str]) -> str:
    if not hashes:
        raise ValueError("empty Merkle tree")
    nodes = [internal_hash(value) for value in hashes]
    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        nodes = [dsha256(nodes[i] + nodes[i + 1]) for i in range(0, len(nodes), 2)]
    return display_hash(nodes[0])


def merkle_branch(hashes: list[str], position: int) -> list[str]:
    if not hashes or position < 0 or position >= len(hashes):
        raise ValueError("invalid Merkle branch position")
    nodes = [internal_hash(value) for value in hashes]
    index = position
    branch: list[str] = []
    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        sibling = index ^ 1
        branch.append(display_hash(nodes[sibling]))
        nodes = [dsha256(nodes[i] + nodes[i + 1]) for i in range(0, len(nodes), 2)]
        index //= 2
    return branch


def verify_merkle_branch(
    leaf: str,
    siblings: list[str],
    position: int,
    total_leaves: int,
    expected_root: str,
) -> None:
    if total_leaves < 1 or position < 0 or position >= total_leaves:
        raise ValueError("invalid Merkle proof position/count")
    node = internal_hash(leaf)
    index = position
    width = total_leaves
    used = 0
    while width > 1:
        if used >= len(siblings):
            raise ValueError("truncated Merkle branch")
        sibling = internal_hash(siblings[used])
        if index ^ 1 >= width and sibling != node:
            raise ValueError("invalid duplicated odd Merkle sibling")
        node = dsha256(sibling + node) if index & 1 else dsha256(node + sibling)
        index //= 2
        width = (width + 1) // 2
        used += 1
    if used != len(siblings):
        raise ValueError("overlong Merkle branch")
    if display_hash(node) != expected_root.lower():
        raise ValueError("Merkle root mismatch")


def witness_commitment(coinbase: dict[str, Any]) -> dict[str, Any]:
    if len(coinbase["inputs"]) != 1:
        raise ValueError("coinbase transaction must have one input")
    txin = coinbase["inputs"][0]
    if txin["prev_txid"] != "00" * 32 or txin["prev_vout"] != 0xFFFFFFFF:
        raise ValueError("transaction is not coinbase")
    witness = txin["witness"]
    if len(witness) != 1 or len(witness[0]) != 32:
        raise ValueError("coinbase witness reserved value must be one 32-byte item")
    found: tuple[int, bytes] | None = None
    prefix = bytes.fromhex("6a24aa21a9ed")
    for output in coinbase["outputs"]:
        script = output["script_pubkey"]
        if len(script) >= 38 and script.startswith(prefix):
            found = (int(output["index"]), script[6:38])
    if found is None:
        raise ValueError("coinbase witness commitment output is missing")
    return {
        "output_index": found[0],
        "commitment": found[1],
        "reserved_value": witness[0],
    }


def verify_witness_commitment(
    witness_root: str, coinbase: dict[str, Any]
) -> dict[str, Any]:
    record = witness_commitment(coinbase)
    computed = dsha256(internal_hash(witness_root) + record["reserved_value"])
    if computed != record["commitment"]:
        raise ValueError("coinbase witness commitment mismatch")
    return {
        "witness_root": witness_root.lower(),
        "coinbase_commitment": record["commitment"].hex(),
        "coinbase_reserved_value": record["reserved_value"].hex(),
        "coinbase_commitment_output_index": record["output_index"],
    }


def parse_script(script: bytes) -> list[dict[str, Any]]:
    reader = Reader(script)
    tokens: list[dict[str, Any]] = []
    while not reader.eof():
        start = reader.offset
        opcode = reader.read(1)[0]
        data: bytes | None = None
        if opcode <= 75:
            data = reader.read(opcode)
        elif opcode == 76:
            size = reader.read_uint(1)
            if size < 76:
                raise ValueError("non-minimal OP_PUSHDATA1")
            data = reader.read(size)
        elif opcode == 77:
            size = reader.read_uint(2)
            if size <= 0xFF:
                raise ValueError("non-minimal OP_PUSHDATA2")
            data = reader.read(size)
        elif opcode == 78:
            size = reader.read_uint(4)
            if size <= 0xFFFF:
                raise ValueError("non-minimal OP_PUSHDATA4")
            data = reader.read(size)
        tokens.append({"opcode": opcode, "data": data, "start": start, "end": reader.offset})
    return tokens


def extract_inscription_envelopes(tx: dict[str, Any]) -> list[dict[str, Any]]:
    envelopes: list[dict[str, Any]] = []
    for input_index, txin in enumerate(tx["inputs"]):
        witness = list(txin["witness"])
        if len(witness) >= 2 and witness[-1].startswith(b"\x50"):
            witness.pop()
        if len(witness) < 2:
            continue
        tapscript = witness[-2]
        control_block = witness[-1]
        tokens = parse_script(tapscript)
        cursor = 0
        while cursor + 2 < len(tokens):
            first, second, third = tokens[cursor : cursor + 3]
            if first["opcode"] != 0x00 or second["opcode"] != 0x63 or third["data"] != b"ord":
                cursor += 1
                continue
            pushes: list[bytes] = []
            end_index: int | None = None
            for index in range(cursor + 3, len(tokens)):
                token = tokens[index]
                if token["opcode"] == 0x68:
                    end_index = index
                    break
                if token["opcode"] in {0x63, 0x64, 0x67} or token["data"] is None:
                    raise ValueError("inscription envelope contains non-push control opcode")
                pushes.append(token["data"])
            if end_index is None:
                raise ValueError("unterminated inscription envelope")

            fields: list[tuple[bytes, bytes]] = []
            body_parts: list[bytes] = []
            field_cursor = 0
            body_found = False
            while field_cursor < len(pushes):
                tag = pushes[field_cursor]
                field_cursor += 1
                if tag == b"":
                    body_parts = pushes[field_cursor:]
                    body_found = True
                    break
                if field_cursor >= len(pushes):
                    raise ValueError("inscription field has no value")
                fields.append((tag, pushes[field_cursor]))
                field_cursor += 1

            content_types = [value for tag, value in fields if tag == b"\x01"]
            if len(content_types) != 1:
                raise ValueError("inscription must contain exactly one content-type field")
            envelopes.append(
                {
                    "inscription_index": len(envelopes),
                    "input_index": input_index,
                    "tapscript": tapscript,
                    "control_block": control_block,
                    "fields": fields,
                    "content_type": content_types[0],
                    "body_present": body_found,
                    "body": b"".join(body_parts),
                    "script_start": first["start"],
                    "script_end": tokens[end_index]["end"],
                }
            )
            cursor = end_index + 1
    return envelopes


def tagged_hash(tag: str, message: bytes) -> bytes:
    tag_hash = sha256(tag.encode("ascii"))
    return sha256(tag_hash + tag_hash + message)


def _point_add(
    left: tuple[int, int] | None, right: tuple[int, int] | None
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 != y2 or y1 == 0):
        return None
    if x1 == x2:
        slope = (3 * x1 * x1) * pow(2 * y1, -1, SECP256K1_P) % SECP256K1_P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % SECP256K1_P, -1, SECP256K1_P) % SECP256K1_P
    x3 = (slope * slope - x1 - x2) % SECP256K1_P
    y3 = (slope * (x1 - x3) - y1) % SECP256K1_P
    return x3, y3


def _scalar_multiply(value: int, point: tuple[int, int]) -> tuple[int, int] | None:
    if value < 0 or value >= SECP256K1_N:
        raise ValueError("invalid secp256k1 scalar")
    result: tuple[int, int] | None = None
    addend: tuple[int, int] | None = point
    while value:
        if value & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        value >>= 1
    return result


def _lift_x(raw_x: bytes) -> tuple[int, int]:
    if len(raw_x) != 32:
        raise ValueError("x-only public key must be 32 bytes")
    x = int.from_bytes(raw_x, "big")
    if x >= SECP256K1_P:
        raise ValueError("x-only public key is out of range")
    y2 = (pow(x, 3, SECP256K1_P) + 7) % SECP256K1_P
    y = pow(y2, (SECP256K1_P + 1) // 4, SECP256K1_P)
    if pow(y, 2, SECP256K1_P) != y2:
        raise ValueError("x-only public key is not on secp256k1")
    if y & 1:
        y = SECP256K1_P - y
    return x, y


def verify_bip340_signature(public_key: bytes, message: bytes, signature: bytes) -> None:
    """Verify one BIP340 x-only Schnorr signature."""
    if len(public_key) != 32 or len(message) != 32 or len(signature) != 64:
        raise ValueError("invalid BIP340 public key, message, or signature length")
    point = _lift_x(public_key)
    r = int.from_bytes(signature[:32], "big")
    s = int.from_bytes(signature[32:], "big")
    if r >= SECP256K1_P or s >= SECP256K1_N:
        raise ValueError("BIP340 signature scalar is out of range")
    challenge = int.from_bytes(
        tagged_hash("BIP0340/challenge", signature[:32] + public_key + message),
        "big",
    ) % SECP256K1_N
    negated = (point[0], (-point[1]) % SECP256K1_P)
    reconstructed = _point_add(
        _scalar_multiply(s, SECP256K1_G),
        _scalar_multiply(challenge, negated),
    )
    if reconstructed is None or reconstructed[1] & 1 or reconstructed[0] != r:
        raise ValueError("BIP340 Schnorr signature verification failed")


def _serialize_outpoint(txin: dict[str, Any]) -> bytes:
    return txin["prev_txid_internal"] + int(txin["prev_vout"]).to_bytes(4, "little")


def _taproot_default_script_path_sighash(
    reveal: dict[str, Any],
    prevout_tx: dict[str, Any],
    input_index: int,
    tapleaf_hash: bytes,
) -> bytes:
    """BIP341 SigMsg(0x00, 1) plus the BIP342 tapscript extension.

    The v1 closed set deliberately supports only its observed one-input,
    SIGHASH_DEFAULT, no-annex, no-OP_CODESEPARATOR inscription reveals. Keeping
    this surface narrow makes unsupported semantics fail closed.
    """
    if len(reveal["inputs"]) != 1 or input_index != 0:
        raise ValueError("v1 signature verifier requires one input at index zero")
    txin = reveal["inputs"][input_index]
    if prevout_tx["txid"] != txin["prev_txid"]:
        raise ValueError("signature prevout transaction mismatch")
    vout = int(txin["prev_vout"])
    if vout < 0 or vout >= len(prevout_tx["outputs"]):
        raise ValueError("signature prevout index is invalid")
    spent_output = prevout_tx["outputs"][vout]

    sigmsg = (
        b"\x00"  # SIGHASH_DEFAULT
        + int(reveal["version"]).to_bytes(4, "little")
        + int(reveal["locktime"]).to_bytes(4, "little")
        + sha256(_serialize_outpoint(txin))
        + sha256(int(spent_output["value"]).to_bytes(8, "little"))
        + sha256(
            encode_compact_size(len(spent_output["script_pubkey"]))
            + spent_output["script_pubkey"]
        )
        + sha256(int(txin["sequence"]).to_bytes(4, "little"))
        + sha256(b"".join(_serialize_output(output) for output in reveal["outputs"]))
        + b"\x02"  # ext_flag=1, annex_present=0
        + input_index.to_bytes(4, "little")
    )
    extension = tapleaf_hash + b"\x00" + (0xFFFFFFFF).to_bytes(4, "little")
    return tagged_hash("TapSighash", b"\x00" + sigmsg + extension)


def verify_simple_inscription_tapscript_spend(
    reveal: dict[str, Any], envelope: dict[str, Any], prevout_tx: dict[str, Any]
) -> dict[str, Any]:
    """Validate the exact BIP342 script shape and signature used by all v1 anchors."""
    input_index = int(envelope["input_index"])
    txin = reveal["inputs"][input_index]
    witness = list(txin["witness"])
    if len(witness) != 3:
        raise ValueError("v1 inscription reveal requires signature, tapscript, and control block only")
    signature, tapscript, control_block = witness
    if tapscript != envelope["tapscript"] or control_block != envelope["control_block"]:
        raise ValueError("inscription witness script/control-block mismatch")
    if len(signature) != 64:
        raise ValueError("v1 inscription reveal requires a 64-byte SIGHASH_DEFAULT signature")

    tokens = parse_script(tapscript)
    if (
        len(tokens) < 5
        or tokens[0]["data"] is None
        or len(tokens[0]["data"]) != 32
        or tokens[1]["opcode"] != 0xAC
        or tokens[2]["opcode"] != 0x00
        or tokens[3]["opcode"] != 0x63
        or tokens[-1]["opcode"] != 0x68
        or envelope["script_start"] != tokens[2]["start"]
        or envelope["script_end"] != len(tapscript)
    ):
        raise ValueError("unsupported v1 inscription tapscript execution shape")

    public_key = tokens[0]["data"]
    leaf_version = control_block[0] & 0xFE
    tapleaf = tagged_hash(
        "TapLeaf",
        bytes([leaf_version]) + encode_compact_size(len(tapscript)) + tapscript,
    )
    sighash = _taproot_default_script_path_sighash(
        reveal, prevout_tx, input_index, tapleaf
    )
    verify_bip340_signature(public_key, sighash, signature)
    return {
        "signature_status": "PASS",
        "sighash_type": "SIGHASH_DEFAULT",
        "tapscript_public_key": public_key.hex(),
        "tapscript_signature": signature.hex(),
        "taproot_sighash": sighash.hex(),
    }


def verify_taproot_reveal_binding(
    reveal: dict[str, Any], envelope: dict[str, Any], prevout_tx: dict[str, Any]
) -> dict[str, Any]:
    input_index = int(envelope["input_index"])
    if input_index < 0 or input_index >= len(reveal["inputs"]):
        raise ValueError("inscription input index is invalid")
    txin = reveal["inputs"][input_index]
    if prevout_tx["txid"] != txin["prev_txid"]:
        raise ValueError("prevout transaction hash mismatch")
    vout = int(txin["prev_vout"])
    if vout < 0 or vout >= len(prevout_tx["outputs"]):
        raise ValueError("prevout index is invalid")
    script_pubkey = prevout_tx["outputs"][vout]["script_pubkey"]
    if len(script_pubkey) != 34 or script_pubkey[:2] != b"\x51\x20":
        raise ValueError("inscription prevout is not native P2TR")

    control = envelope["control_block"]
    if len(control) < 33 or (len(control) - 33) % 32 or (len(control) - 33) // 32 > 128:
        raise ValueError("invalid Taproot control block length")
    leaf_version = control[0] & 0xFE
    if leaf_version != 0xC0:
        raise ValueError("inscription reveal is not a tapscript leaf")
    internal_key = control[1:33]
    tapleaf = tagged_hash(
        "TapLeaf", bytes([leaf_version]) + encode_compact_size(len(envelope["tapscript"])) + envelope["tapscript"]
    )
    root = tapleaf
    for offset in range(33, len(control), 32):
        sibling = control[offset : offset + 32]
        root = tagged_hash("TapBranch", min(root, sibling) + max(root, sibling))
    tweak = int.from_bytes(tagged_hash("TapTweak", internal_key + root), "big")
    if tweak >= SECP256K1_N:
        raise ValueError("Taproot tweak is out of range")
    point = _point_add(_lift_x(internal_key), _scalar_multiply(tweak, SECP256K1_G))
    if point is None:
        raise ValueError("Taproot output point is infinity")
    output_key = point[0].to_bytes(32, "big")
    if output_key != script_pubkey[2:]:
        raise ValueError("tapscript/control block does not commit to prevout P2TR key")
    if point[1] & 1 != control[0] & 1:
        raise ValueError("Taproot control-block parity mismatch")
    return {
        "input_index": input_index,
        "prevout_txid": prevout_tx["txid"],
        "prevout_vout": vout,
        "tapleaf_hash": tapleaf.hex(),
        "taproot_merkle_root": root.hex(),
        "taproot_output_key": output_key.hex(),
        "leaf_version": leaf_version,
        "control_path_nodes": (len(control) - 33) // 32,
    }


def _bech32_polymod(values: list[int]) -> int:
    generators = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ value
        for index, generator in enumerate(generators):
            if (top >> index) & 1:
                chk ^= generator
    return chk


def _bech32_hrp_expand(hrp: str) -> list[int]:
    return [ord(char) >> 5 for char in hrp] + [0] + [ord(char) & 31 for char in hrp]


def _convertbits(data: bytes, from_bits: int, to_bits: int) -> list[int]:
    acc = 0
    bits = 0
    output: list[int] = []
    maxv = (1 << to_bits) - 1
    for value in data:
        if value < 0 or value >> from_bits:
            raise ValueError("invalid convertbits input")
        acc = (acc << from_bits) | value
        bits += from_bits
        while bits >= to_bits:
            bits -= to_bits
            output.append((acc >> bits) & maxv)
    if bits:
        output.append((acc << (to_bits - bits)) & maxv)
    return output


def segwit_address(script_pubkey: bytes, hrp: str = "bc") -> str:
    if len(script_pubkey) != 34 or script_pubkey[:2] != b"\x51\x20":
        raise ValueError("only mainnet P2TR outputs are supported")
    values = [1] + _convertbits(script_pubkey[2:], 8, 5)
    polymod_values = _bech32_hrp_expand(hrp) + values + [0] * 6
    polymod = _bech32_polymod(polymod_values) ^ BECH32M_CONST
    checksum = [(polymod >> (5 * (5 - index))) & 31 for index in range(6)]
    return hrp + "1" + "".join(BECH32_CHARSET[value] for value in values + checksum)


def canonicalize_text_bytes(value: bytes) -> bytes:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("inscription/mirror text is not UTF-8") from exc
    return text.strip().replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
