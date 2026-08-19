#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, pathlib
from eth_hash.auto import keccak

P=pathlib.Path(__file__).with_name('capture-chronicle-sidechain-settlement.py')
spec=importlib.util.spec_from_file_location('capture_settlement',P)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

# Polygon/FxPortal tree behavior: pad to next power of two with zero leaves,
# hash ordered pairs with keccak256, and use blockNumber-startBlock as index.
leaves=[keccak(b'a'),keccak(b'b'),keccak(b'c')]
layers=mod.merkle_layers(leaves)
assert len(layers[0])==4 and layers[0][3]==b'\x00'*32
for i,leaf in enumerate(leaves):
    proof=mod.merkle_proof(layers,i)
    assert mod.verify_merkle(leaf,i,layers[-1][0],proof)
    assert not mod.verify_merkle(keccak(leaf),i,layers[-1][0],proof)

# Official checkpoint leaf encoding is 32-byte number || 32-byte timestamp ||
# txRoot || receiptRoot, then keccak256.
block={'number':'0x2a','timestamp':'0x65','transactionsRoot':'0x'+'11'*32,'receiptsRoot':'0x'+'22'*32}
expected=keccak((42).to_bytes(32,'big')+(101).to_bytes(32,'big')+bytes.fromhex('11'*32)+bytes.fromhex('22'*32))
assert mod.polygon_leaf(block)==expected

# ABI selector and endpoint parsing regressions.
assert mod.selector('currentHeaderBlock()').startswith('0x') and len(mod.selector('currentHeaderBlock()'))==10
assert mod.endpoints('https://a.example,https://b.example','https://b.example,https://c.example')==['https://a.example','https://b.example','https://c.example']
print('SETTLEMENT_PROOF_REGRESSION_OK')
