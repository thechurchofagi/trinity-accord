#!/usr/bin/env python3
import hashlib, json, pathlib, os, rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

OUT=pathlib.Path(os.getenv('CHRONICLE_OUT','artifacts/chronicle-sidechain-scan')); E=OUT/'evidence-v2'
def sha(b): return hashlib.sha256(b).digest()
def stable(v):
    if isinstance(v,list): return '['+','.join(stable(x) for x in v)+']'
    if isinstance(v,dict): return '{'+','.join(json.dumps(k,separators=(',',':'))+':'+stable(v[k]) for k in sorted(v))+'}'
    if v is True:return 'true'
    if v is False:return 'false'
    if v is None:return 'null'
    return json.dumps(v,separators=(',',':'),ensure_ascii=False)
def varint(buf,o):
    x=0;s=0
    while o<len(buf):
        b=buf[o];o+=1;x|=(b&127)<<s
        if not b&128:return x,o
        s+=7
        if s>63: raise ValueError('varint too long')
    raise ValueError('truncated varint')
def cid_at(buf,o):
    if o+34<=len(buf) and buf[o:o+2]==b'\x12\x20': return buf[o:o+34],o+34,0x70,0x12,buf[o+2:o+34]
    v,o1=varint(buf,o)
    if v!=1: raise ValueError(f'CID version {v}')
    codec,o2=varint(buf,o1);mh,o3=varint(buf,o2);ln,o4=varint(buf,o3);end=o4+ln
    if end>len(buf):raise ValueError('truncated cid')
    return buf[o:end],end,codec,mh,buf[o4:end]
B32='abcdefghijklmnopqrstuvwxyz234567';B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def cid_bytes(s):
    if s.startswith('Qm'):
        n=0
        for ch in s:n=n*58+B58.index(ch)
        h=f'{n:x}';h=('0'+h) if len(h)%2 else h;out=bytes.fromhex(h);z=len(s)-len(s.lstrip('1'));return b'\0'*z+out
    bits=0;value=0;out=[]
    for ch in s.lower().lstrip('b'):
        value=(value<<5)|B32.index(ch);bits+=5
        if bits>=8:out.append((value>>(bits-8))&255);bits-=8
    return bytes(out)
def pb_links(data):
    out=[];o=0
    while o<len(data):
        key,o=varint(data,o);f=key>>3;w=key&7
        if w==2:
            ln,o=varint(data,o);end=o+ln
            if end>len(data):raise ValueError('pb truncated')
            if f==2:
                link=data[o:end];q=0
                while q<len(link):
                    k,q=varint(link,q);f2=k>>3;w2=k&7
                    if w2==2:
                        ln2,q=varint(link,q);e=q+ln2
                        if e>len(link):raise ValueError('pb link truncated')
                        if f2==1:out.append(bytes(link[q:e]))
                        q=e
                    elif w2==0:_,q=varint(link,q)
                    elif w2==1:q+=8
                    elif w2==5:q+=4
                    else:raise ValueError('pb wire')
            o=end
        elif w==0:_,o=varint(data,o)
        elif w==1:o+=8
        elif w==5:o+=4
        else:raise ValueError('pb wire')
    return out
def verify_car(file,root):
    buf=file.read_bytes();hlen,o=varint(buf,0);hend=o+hlen;rb=cid_bytes(root)
    if rb not in buf[o:hend]:raise ValueError('root absent header')
    blocks={};off=hend
    while off<len(buf):
        ln,off=varint(buf,off)
        if ln==0:continue
        end=off+ln;c,next_,codec,mh,digest=cid_at(buf,off);data=buf[next_:end]
        if mh!=0x12 or len(digest)!=32 or sha(data)!=digest:raise ValueError('block cid hash mismatch')
        blocks[c.hex()]=(codec,data);off=end
    rk=rb.hex()
    if rk not in blocks:raise ValueError('root block missing')
    seen=set();stack=[rk]
    while stack:
        k=stack.pop()
        if k in seen:continue
        if k not in blocks:raise ValueError('linked block missing')
        seen.add(k);codec,data=blocks[k]
        if codec==0x70:
            for link in pb_links(data):
                lk=link.hex()
                if lk not in blocks:raise ValueError('linked block missing')
                stack.append(lk)
        elif codec!=0x55:raise ValueError(f'unsupported codec {codec}')
    return {'bytes':len(buf),'sha256':hashlib.sha256(buf).hexdigest(),'blocks':len(blocks),'reachable':len(seen)}
def mth(leaves):
    if not leaves:return sha(b'')
    if len(leaves)==1:return sha(b'\x00'+leaves[0])
    k=1
    while (k<<1)<len(leaves):k<<=1
    return sha(b'\x01'+mth(leaves[:k])+mth(leaves[k:]))
def projection(r):
    return {'asset_id':r['asset_id'],'chain_id':r['chain']['chain_id'],'standard':r['standard'],'contract':r['contract'],'token_id':r['token_id'],'origin':({k:r['origin'].get(k) for k in ['kind','mint_observed','transaction_hash','block_hash','block_number','log_index','timestamp','timestamp_unix','from','to','quantity']} if r.get('origin') else None),'content':{'metadata':{'root_cid':r['content']['metadata'].get('root_cid'),'leaf_path':r['content']['metadata'].get('leaf_path'),'payload_sha256':(r['content']['metadata'].get('payload') or {}).get('sha256'),'payload_bytes':(r['content']['metadata'].get('payload') or {}).get('bytes'),'normalized_sha256':r['content']['metadata'].get('normalized_sha256'),'car_sha256':(r['content']['metadata'].get('car') or {}).get('car_sha256'),'car_bytes':(r['content']['metadata'].get('car') or {}).get('car_bytes')},'media':[{'role':m['role'],'root_cid':(m.get('ipfs') or {}).get('root_cid'),'leaf_path':(m.get('ipfs') or {}).get('leaf_path'),'payload_sha256':(m.get('payload') or {}).get('sha256'),'payload_bytes':(m.get('payload') or {}).get('bytes'),'car_sha256':(m.get('car') or {}).get('car_sha256'),'car_bytes':(m.get('car') or {}).get('car_bytes')} for m in r['content']['media']]}}
def verify_l2(r,w):
    header=bytes.fromhex(w['block_header_rlp'][2:]);fields=rlp.decode(header)
    if '0x'+keccak(header).hex()!=w['block_hash'].lower():raise ValueError('header hash')
    txroot=fields[4];recroot=fields[5];ts=int.from_bytes(fields[11],'big') if fields[11] else 0
    if '0x'+txroot.hex()!=w['transactions_root'].lower() or '0x'+recroot.hex()!=w['receipts_root'].lower():raise ValueError('header roots')
    if ts!=int(r['origin']['timestamp_unix']):raise ValueError('timestamp')
    tx=bytes.fromhex(w['transaction_rlp'][2:]);rec=bytes.fromhex(w['receipt_rlp'][2:]);key=bytes.fromhex(w['mpt_key_rlp'][2:])
    tp=[rlp.decode(bytes.fromhex(x[2:])) for x in w['transaction_proof_nodes_rlp']];rp=[rlp.decode(bytes.fromhex(x[2:])) for x in w['receipt_proof_nodes_rlp']]
    if HexaryTrie.get_from_proof(txroot,key,tp)!=tx:raise ValueError('tx mpt')
    if HexaryTrie.get_from_proof(recroot,key,rp)!=rec:raise ValueError('receipt mpt')
    if '0x'+keccak(tx).hex()!=r['origin']['transaction_hash'].lower():raise ValueError('tx hash')
    return True

def main():
    idx=json.loads((E/'SIDECHAIN-NFT-IDENTITY-INDEX.json').read_text());com=json.loads((E/'SIDECHAIN-NFT-COLLECTION-COMMITMENT.json').read_text());records=idx['records']
    projections=sorted([projection(r) for r in records],key=lambda x:x['asset_id']);leaves=[stable(x).encode() for x in projections];root=mth(leaves).hex();errors=[]
    if root!=com['merkle_root_sha256']:errors.append(f'L1 merkle mismatch {root}')
    if len(records)!=com['record_count']:errors.append('L1 record count mismatch')
    car_seen={};car_checked=0;l2_checked=0
    for r in records:
        for c in [r['content']['metadata'].get('car')]+[m.get('car') for m in r['content']['media']]:
            if not c or c.get('status')!='ok':continue
            f=OUT/c['file'];k=str(f)
            if k not in car_seen:
                try:
                    v=verify_car(f,c['root_cid']);car_seen[k]=v;car_checked+=1
                    if v['sha256']!=c['car_sha256'] or v['bytes']!=c['car_bytes']:raise ValueError('CAR declared digest/size mismatch')
                except Exception as e:errors.append(f"CAR {c.get('root_cid')}: {e}")
        wf=E/'l2'/r['chain']['name']/r['contract']/r['token_id']/'witness.json'
        try:verify_l2(r,json.loads(wf.read_text()));l2_checked+=1
        except Exception as e:errors.append(f"L2 {r['asset_id']}: {e}")
    report={'schema':'trinity-accord/chronicle-sidechain-offline-verification/v2','records':len(records),'l1_merkle_root_sha256':root,'car_files_checked':car_checked,'l2_records_checked':l2_checked,'errors':errors,'pass':not errors and l2_checked==len(records)}
    (E/'OFFLINE-VERIFICATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f"[OFFLINE VERIFY] records={len(records)} cars={car_checked} l2={l2_checked} errors={len(errors)} pass={report['pass']}")
    for error in errors[:40]: print(f'[OFFLINE ERROR] {error}', flush=True)
    if len(errors)>40: print(f'[OFFLINE ERROR] ... {len(errors)-40} additional errors persisted in OFFLINE-VERIFICATION.json', flush=True)
    if not report['pass']:raise SystemExit(1)
if __name__=='__main__':main()
