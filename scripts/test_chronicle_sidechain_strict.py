#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

SCRIPT = pathlib.Path(__file__).with_name("verify-chronicle-sidechain-strict.py")
SPEC = importlib.util.spec_from_file_location("strict", SCRIPT)
strict = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(strict)


class StrictPrimitives(unittest.TestCase):
    def test_merkle_proof_is_order_sensitive(self):
        leaves = [keccak(bytes([i])) for i in range(4)]
        left = keccak(leaves[0] + leaves[1])
        right = keccak(leaves[2] + leaves[3])
        root = keccak(left + right)
        self.assertEqual(strict.merkle_root(leaves[2], 2, [leaves[3], left]), root)
        self.assertNotEqual(strict.merkle_root(leaves[2], 2, [leaves[1], left]), root)

    def test_legacy_and_typed_receipts(self):
        fields = [b"\x01", b"\x02", b"\x00" * 256, []]
        legacy = rlp.encode(fields)
        typed = b"\x02" + legacy
        self.assertEqual(strict.receipt_payload(legacy), fields)
        self.assertEqual(strict.receipt_payload(typed), fields)

    def test_receipt_mpt_proof_tamper_fails(self):
        trie = HexaryTrie(db={})
        trie[rlp.encode(0)] = rlp.encode([b"\x01", b"", b"\x00" * 256, []])
        proof = trie.get_proof(rlp.encode(0))
        self.assertEqual(HexaryTrie.get_from_proof(trie.root_hash, rlp.encode(0), proof), trie[rlp.encode(0)])
        with self.assertRaises(Exception):
            HexaryTrie.get_from_proof(b"\xff" * 32, rlp.encode(0), proof)

    def test_not_applicable_layer_is_terminal_not_missing(self):
        self.assertTrue(strict.strict_layer_complete({"status": "NOT_APPLICABLE"}))
        self.assertTrue(strict.strict_layer_complete({"status": "PASS"}))
        self.assertFalse(strict.strict_layer_complete({"status": "NOT_CAPTURED"}))
        self.assertFalse(strict.strict_layer_complete({"status": "INCOMPLETE"}))


if __name__ == "__main__":
    unittest.main()
