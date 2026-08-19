#!/usr/bin/env python3
import importlib.util
import pathlib
from eth_hash.auto import keccak

HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('polygon_eth_settlement', HERE/'capture-chronicle-polygon-ethereum-settlement.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def padded_root(leaves):
    if not leaves: raise ValueError('empty')
    n=1
    while n<len(leaves): n*=2
    layer=list(leaves)+[b'\x00'*32]*(n-len(leaves))
    while len(layer)>1:
        layer=[keccak(layer[i]+layer[i+1]) for i in range(0,len(layer),2)]
    return layer[0]


def run_case(count):
    base=1000
    leaves=[keccak(f'block-{i}'.encode()) for i in range(count)]
    original=mod.bor_root
    def fake_root(start,end):
        assert base<=start<=end<base+count
        return padded_root(leaves[start-base:end-base+1])
    mod.bor_root=fake_root
    try:
        expected=padded_root(leaves)
        for i,leaf in enumerate(leaves):
            proof=mod.polygon_block_proof(base+i,base,base+count-1)
            actual=mod.verify_merkle(leaf,i,proof)
            if actual!=expected:
                raise AssertionError(f'count={count} index={i} root mismatch')
    finally:
        mod.bor_root=original


def main():
    for count in range(1,34): run_case(count)
    topic='0x'+keccak(b'NewHeaderBlock(address,uint256,uint256,uint256,uint256,bytes32)').hex()
    if mod.NEW_HEADER_TOPIC!=topic: raise AssertionError('event topic mismatch')
    if mod.HEADER_STRIDE!=10_000: raise AssertionError('RootChain header stride mismatch')
    # Bor checkpoint leaf formula is keccak(bytes32(number)||bytes32(timestamp)||txRoot||receiptRoot).
    number=54319195; timestamp=1709699000; txroot=keccak(b'txroot'); recroot=keccak(b'recroot')
    expected=keccak(mod.word(number)+mod.word(timestamp)+txroot+recroot)
    if len(expected)!=32: raise AssertionError('checkpoint leaf formula')
    print('PASS: Polygon checkpoint Merkle proof algorithm matches padded keccak tree for counts 1..33')


if __name__=='__main__': main()
