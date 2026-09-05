#!/usr/bin/env python3
import json
import pathlib
import tempfile

from eth_hash.auto import keccak

from capture_chronicle_base_derivation import (
    BASE_GENESIS_TIME,
    find_targets,
    merge_windows,
    parse_l1_info,
)


def main():
    selector = keccak(b"setL1BlockValuesEcotone()")[:4]
    data = bytearray(164)
    data[:4] = selector
    data[12:20] = (7).to_bytes(8, "big")
    data[20:28] = (1234).to_bytes(8, "big")
    data[28:36] = (5678).to_bytes(8, "big")
    data[100:132] = b"\x44" * 32
    data[144:164] = b"\x55" * 20
    info = parse_l1_info("0x" + data.hex())
    assert info["sequence_number"] == 7 and info["l1_timestamp"] == 1234 and info["l1_block_number"] == 5678
    assert info["l1_block_hash"] == "0x" + "44" * 32
    assert info["batcher_address"] == "0x" + "55" * 20
    assert merge_windows([100, 105, 1000], 10, 20) == [(90, 126), (990, 1021)]

    raw_tx = "0x02c0"
    digest = "0x" + keccak(bytes.fromhex(raw_tx[2:])).hex()
    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        channel = {
            "id": "0xabc",
            "is_ready": True,
            "invalid_frames": False,
            "invalid_batches": False,
            "frames": [{"transaction_hash": "0x" + "11" * 32, "inclusion_block": 9, "block_hash": "0x" + "22" * 32, "frame": {"frame_number": 0, "is_last": True}}],
            "batches": [{"span_batch_elements": [{"EpochNum": 8, "Timestamp": BASE_GENESIS_TIME + 20, "Transactions": [raw_tx]}]}],
        }
        (root / "one.json").write_text(json.dumps(channel))
        target = {digest: {"block_number": 10, "timestamp_unix": BASE_GENESIS_TIME + 20}}
        match = find_targets(root, target)[digest]
        assert match["derived_l2_block_number"] == 10
        assert match["l1_origin_number"] == 8
    print("base derivation capture tests: PASS")


if __name__ == "__main__":
    main()
