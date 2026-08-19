#!/usr/bin/env python3
"""Offline verifier for the additive Chronicle sidechain settlement witness."""
from __future__ import annotations
import json, os, pathlib
import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

OUT=pathlib.Path(os.getenv('CHRONICLE_OUT','artifacts/chronicle-sidechain-scan'))
ROOT=OUT/'evidence-v2'/'settlement-v1'

def read(name): return json.loads((ROOT/name).read_text())
def h2b(v):
    s=str(v); s=s[2:] if s.startswith('0x') else s
    return bytes.fromhex(s)
def h2i(v): return int(v,16) if isinstance(v,str) and v.startswith('0x') else int(v)

def verify_header(row):
    raw=h2b(row['header_rlp']); actual='0x'+keccak(raw).hex()
    if actual.lower()!=row['hash'].lower() or actual.lower()!=row['computed_hash'].lower():
        raise ValueError(f"header hash mismatch expected={row['hash']} actual={actual}")
    return True

def verify_merkle(member, root):
    h=h2b(member['leaf']); idx=int(member['leaf_index'])
    for phex in member['proof']:
        p=h2b(phex); h=keccak(h+p) if idx%2==0 else keccak(p+h); idx//=2
    if h!=h2b(root): raise ValueError('Polygon checkpoint Merkle proof mismatch')

def verify_receipt_inclusion(inc):
    block=inc['ethereum_block']; verify_header(block)
    root=h2b(block['receipts_root']); key=h2b(inc['mpt_key_rlp']); wanted=h2b(inc['receipt_rlp'])
    nodes=[rlp.decode(h2b(x)) for x in inc['receipt_proof_nodes_rlp']]
    got=HexaryTrie.get_from_proof(root,key,nodes)
    if got!=wanted: raise ValueError('Ethereum receipt MPT proof mismatch')

def verify_polygon(p):
    if not p.get('pass') or p.get('status')!='ethereum_checkpoint_membership_verified': raise ValueError('Polygon settlement not marked pass')
    members=0
    for group in p['groups']:
        cp=group['checkpoint']
        if group['computed_root'].lower()!=cp['root'].lower() or not group['root_match']: raise ValueError('Polygon checkpoint root mismatch')
        for m in group['members']:
            verify_merkle(m,cp['root']); members+=1
        sub=group['ethereum_submission']; log=sub['log']; data=h2b(log['data'])
        if len(data)!=96: raise ValueError('NewHeaderBlock log data length mismatch')
        start=int.from_bytes(data[:32],'big'); end=int.from_bytes(data[32:64],'big'); root='0x'+data[64:].hex()
        if start!=cp['start'] or end!=cp['end'] or root.lower()!=cp['root'].lower(): raise ValueError('NewHeaderBlock log does not bind checkpoint')
        verify_receipt_inclusion(sub['receipt_inclusion'])
        if not group.get('checkpoint_block_finalized_observed'): raise ValueError('Polygon checkpoint Ethereum block not finalized-observed')
    if members!=p['unique_target_blocks']: raise ValueError(f'Polygon target block accounting mismatch {members}!={p["unique_target_blocks"]}')
    return members

def verify_base(b):
    verified=0
    for row in b.get('origins',[]):
        if row.get('verified'):
            verify_header(row['ethereum_l1_block'])
            if row['ethereum_l1_block']['hash'].lower()!=row['hash_call'].lower(): raise ValueError('Base L1-origin Ethereum hash mismatch')
            verified+=1
    if verified!=b.get('l1_origins_verified'): raise ValueError('Base L1-origin verified count mismatch')
    for c in b.get('base_l1_contracts_at_finalized',{}).values():
        if c.get('present') and (not c.get('code_sha256') or c.get('code_bytes',0)<=0): raise ValueError('Base L1 contract code inventory invalid')
    # Deliberately do not require full_settlement_pass: capture currently treats Base
    # L1-origin binding and OP settlement finality as different claims.
    return verified

def main():
    p=read('POLYGON-ETHEREUM-SETTLEMENT.json'); b=read('BASE-ETHEREUM-SETTLEMENT.json'); s=read('SETTLEMENT-SUMMARY.json')
    pm=verify_polygon(p); bv=verify_base(b)
    if s['polygon']['unique_target_blocks']!=pm or s['base']['l1_origins_verified']!=bv: raise SystemExit('summary accounting mismatch')
    report={'schema':'trinity-accord/chronicle-sidechain-settlement-offline-verification/v1','polygon_checkpoint_memberships_verified':pm,'base_l1_origins_verified':bv,'polygon_pass':True,'base_full_settlement_pass':bool(b.get('full_settlement_pass')),'pass':True,'boundary':'PASS means all claims present in the settlement package verify offline; Base is not relabeled full settlement unless its own full_settlement_pass is true.'}
    (ROOT/'OFFLINE-SETTLEMENT-VERIFICATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__': main()
