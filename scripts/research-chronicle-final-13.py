#!/usr/bin/env python3
import base64, hashlib, itertools, json, os, pathlib, subprocess, sys

TARGETS = {
    'QmNTjiSRWuZfxzjH3QH9j5D3bEB957jS1psMuc9RFqB4QT': ('polygon','0x9a3a7ddde5712b090181937bd7f0a6e2084707e6','0','media:image'),
    'QmPu9KwfdQuF6EyaMPHbaBfNA151dR8WykArAQoZzKc4DW': ('base','0xf616ba3cfab4d17477d7c63d775666dcb1e5542d','0','metadata'),
    'QmRTbRbkfpjnU3cW4p8FW4rjuKjHx7B2MuhE2n8qLZtMah': ('base','0xf616ba3cfab4d17477d7c63d775666dcb1e5542d','0','media:image'),
    'QmRX4GtfNvGrG2FgbtJdhUUx4ocyGk9aEqzgD7zsTEUAva': ('polygon','0x001007e8ab86f6ba6f477712c8b8db84887d0175','0','media:image'),
    'QmS4RcwE3J4JzNRAE1crQXM2Joex53TEgAXtN6nBDkWtRC': ('base','0x1f26a5a197b4bed502e0a5a05d22b625406d05c1','0','media:image'),
    'QmSBMTSNPuPBEQPQyumf44AJ5fSPLVM36xwqQcmPjYGe9h': ('polygon','0x001007e8ab86f6ba6f477712c8b8db84887d0175','0','metadata'),
    'QmUzTNGsxN3TwKgs7cbwzy4cbuwY4uEcF7ESNspZW2nP96': ('base','0x1f26a5a197b4bed502e0a5a05d22b625406d05c1','0','metadata'),
    'QmYxaovCTVY2EiXBWgvBdtpFCKyoom6bYSBTcxJ5UJweJ1': ('base','0x3acfeebf6cd63f61ae6096dafc7dab7675bf7e77','0','media:image'),
    'QmcwViT2rJB74S9ni9K7V76E9Z54X1TEpbMeEEi56jEmRH': ('polygon','0x9a3a7ddde5712b090181937bd7f0a6e2084707e6','0','metadata'),
    'bafkreiddsyhct5vz2ludy2sgmh2hgx3vkk4sno2yaybukrnwrnmo4a6fcy': ('polygon','0xad4bda0b463ace68dd640b14891b00a7fe1caccf','1','metadata'),
    'bafkreiel7mdl7timheywsmexzvnvkupu4jnqksjzh7pjsrn43tscvmoqfa': ('polygon','0xad4bda0b463ace68dd640b14891b00a7fe1caccf','1','media:image'),
    'bafybeieofybnvwz4qkmseon5zhye7fshzqosbsbsvl46buqoxtzzjzbf54': ('polygon','0x5ed7eb7b81068ea23bc170be48b4a0e99262aa6d','1','metadata'),
    'bafybeihkjhsxzsyx47syfhh5drqhbcsix5qssvyduxyedswed6k3f6lumq': ('polygon','0xe0a63a9eb48f2662a429f9f51c6ddbc1a54deb4a','1','metadata'),
}
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
B32='abcdefghijklmnopqrstuvwxyz234567'

def varint(n):
    out=bytearray()
    while True:
        b=n & 0x7f; n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n: return bytes(out)

def b58decode(s):
    n=0
    for c in s: n=n*58+B58.index(c)
    raw=n.to_bytes((n.bit_length()+7)//8,'big') if n else b''
    pad=len(s)-len(s.lstrip('1'))
    return b'\0'*pad+raw

def cid_bytes(cid):
    if cid.startswith('Qm'): return b58decode(cid)
    if cid.startswith('b'): return base64.b32decode(cid[1:].upper()+'='*((8-len(cid[1:])%8)%8))
    raise ValueError(cid)

def target_digest(cid):
    raw=cid_bytes(cid)
    if cid.startswith('Qm'):
        assert raw[:2]==b'\x12\x20'; return raw[2:]
    # v1: version, codec, mh code, mh length are all one-byte for targets here
    assert raw[0]==1 and raw[2]==0x12 and raw[3]==0x20
    return raw[4:36]

def unixfs_pbnode(data):
    # UnixFS Data{Type=File(2), Data=<bytes>, filesize=<len>} inside PBNode.Data.
    u=b'\x08\x02'+b'\x12'+varint(len(data))+data+b'\x18'+varint(len(data))
    return b'\x0a'+varint(len(u))+u

def candidate_digest(cid,data):
    if cid.startswith('bafk'): return hashlib.sha256(data).digest()
    return hashlib.sha256(unixfs_pbnode(data)).digest()

def exact(cid,data): return candidate_digest(cid,data)==target_digest(cid)

def reorder_top(obj, keys): return {k:obj[k] for k in keys}

def slash_escape(s): return s.replace('/', '\\/')

def serializations(obj):
    # label,text; Python default compact/spaced/indent cover common JS/Python serializers.
    specs=[]
    for ascii_mode in (False,True):
        p='ascii' if ascii_mode else 'utf8'
        specs.append((f'{p}_compact',json.dumps(obj,ensure_ascii=ascii_mode,separators=(',',':'))))
        specs.append((f'{p}_spaced',json.dumps(obj,ensure_ascii=ascii_mode,separators=(', ',': '))))
        for indent in range(1,9):
            specs.append((f'{p}_pretty{indent}',json.dumps(obj,ensure_ascii=ascii_mode,indent=indent)))
        specs.append((f'{p}_tabs',json.dumps(obj,ensure_ascii=ascii_mode,indent='\t')))
    seen=set()
    for label,text in specs:
        for slash in (False,True):
            body=slash_escape(text) if slash else text
            slabel=label+('_slash' if slash else '')
            for ending_name,ending in (('none',''),('lf','\n'),('crlf','\r\n')):
                raw=(body+ending).encode('utf-8')
                for bom in (False,True):
                    data=(b'\xef\xbb\xbf'+raw) if bom else raw
                    key=hashlib.sha256(data).digest()
                    if key in seen: continue
                    seen.add(key)
                    yield slabel+'_'+ending_name+('_bom' if bom else ''),data

def metadata_search(cid, metadata, limit_permutations=40320):
    keys=list(metadata.keys()) if isinstance(metadata,dict) else []
    orders=[('snapshot',tuple(keys))]
    if len(keys)<=8:
        orders=[]
        for i,p in enumerate(itertools.permutations(keys)):
            if i>=limit_permutations: break
            orders.append((f'perm{i}',p))
    else:
        orders.append(('sorted',tuple(sorted(keys))))
    checked=0
    seen=set()
    for order_name,order in orders:
        value=reorder_top(metadata,order)
        for ser,data in serializations(value):
            h=hashlib.sha256(data).digest()
            if h in seen: continue
            seen.add(h); checked+=1
            if exact(cid,data):
                return {'matched':True,'order':list(order),'order_name':order_name,'serialization':ser,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'candidate_b64':base64.b64encode(data).decode(),'checked':checked}
    return {'matched':False,'checked':checked,'top_keys':keys,'permuted':len(keys)<=8}

def kubo_hash(kubo,file,cid):
    variants=[]
    if cid.startswith('Qm'):
        variants=[(0,False,'size-262144',False),(0,False,'size-1048576',False),(0,False,'size-262144',True)]
    elif cid.startswith('bafk'):
        # exact raw digest is handled without Kubo
        return []
    else:
        variants=[(1,False,'size-262144',False),(1,True,'size-262144',False),(1,False,'size-1048576',False),(1,True,'size-1048576',False),(1,False,'size-262144',True)]
    out=[]
    for ver,raw,chunk,trickle in variants:
        args=[kubo,'add','-Q','--pin=false','--only-hash',f'--cid-version={ver}',f'--raw-leaves={str(raw).lower()}',f'--chunker={chunk}']
        if trickle: args.append('--trickle')
        args.append(str(file))
        try:
            got=subprocess.check_output(args,stderr=subprocess.STDOUT,text=True,timeout=45).strip().split()[-1]
            out.append({'cid':got,'version':ver,'raw':raw,'chunker':chunk,'trickle':trickle,'exact':got==cid})
        except Exception as e:
            out.append({'error':str(e)[:300],'version':ver,'raw':raw,'chunker':chunk,'trickle':trickle})
    return out

def main():
    root=pathlib.Path(os.environ.get('CHRONICLE_OUT','artifacts/chronicle-sidechain-scan'))
    records=json.loads((root/'recovered-tokens.json').read_text())
    kubo=os.environ.get('CHRONICLE_KUBO_BIN','')
    bycoord={}
    for r in records:
        chain='polygon' if int(r.get('chain_id',0))==137 else 'base' if int(r.get('chain_id',0))==8453 else str(r.get('chain'))
        bycoord[(chain,str(r.get('contract','')).lower(),str(r.get('token_id')))]=r
    report={'schema':'trinity-accord/final-13-research/v1','target_count':len(TARGETS),'results':{}}
    for cid,(chain,contract,tid,role) in TARGETS.items():
        rec=bycoord.get((chain,contract.lower(),tid))
        row={'coordinate':[chain,contract,tid],'role':role,'found_record':bool(rec),'cid':cid}
        if not rec:
            report['results'][cid]=row; continue
        row['token_uri']=rec.get('token_uri')
        row['metadata']=rec.get('metadata')
        row['media']=rec.get('media')
        token_dir=root/chain/contract.lower()/tid
        files=[]
        if token_dir.exists():
            for f in sorted(token_dir.rglob('*')):
                if not f.is_file(): continue
                data=f.read_bytes()
                item={'file':str(f.relative_to(root)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
                if exact(cid,data): item['direct_exact']=True
                if kubo:
                    hashes=kubo_hash(kubo,f,cid)
                    if any(h.get('exact') for h in hashes): item['kubo_exact']=hashes
                files.append(item)
        row['local_files']=files
        if role=='metadata' and isinstance(rec.get('metadata'),dict):
            row['serialization_search']=metadata_search(cid,rec['metadata'])
        report['results'][cid]=row
    report['matched_metadata']=[cid for cid,r in report['results'].items() if r.get('serialization_search',{}).get('matched')]
    report['matched_local_files']=[cid for cid,r in report['results'].items() if any(f.get('direct_exact') or f.get('kubo_exact') for f in r.get('local_files',[]))]
    out=pathlib.Path(os.environ.get('RESEARCH_REPORT','final-13-research.json'))
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'matched_metadata':report['matched_metadata'],'matched_local_files':report['matched_local_files'],'report':str(out)},ensure_ascii=False))

if __name__=='__main__': main()
