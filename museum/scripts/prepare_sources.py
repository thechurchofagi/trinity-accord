"""Recover missing exhibition copies using the frozen manifest and exact CAR digests.
Run with: python scripts/prepare_sources.py --recover-missing
This does not rewrite the manifest or claim chain consensus validation.
"""
from pathlib import Path
import argparse, base64, concurrent.futures, hashlib, json, subprocess, urllib.request

P=Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def var(b,p=0):
 n=s=0
 while True:
  x=b[p];p+=1;n|=(x&127)<<s
  if not x&128:return n,p
  s+=7
def cid(b,p=0):
 v,q=var(b,p)
 if v==1:c,q=var(b,q);h,q=var(b,q);n,q=var(b,q)
 else:c=0x70;h=v;n,q=var(b,q)
 if h!=0x12 or n!=32:raise ValueError('Only SHA-256 CAR blocks supported')
 return (c,b[q:q+n]),q+n
def fields(b):
 out=[];p=0
 while p<len(b):
  tag,p=var(b,p);k=tag>>3;t=tag&7
  if t==0:v,p=var(b,p)
  elif t==2:n,p=var(b,p);v=b[p:p+n];p+=n
  else:raise ValueError(t)
  out.append((k,v))
 return out
def extract(b,m):
 size,p=var(b);header=b[p:p+size];p+=size;blocks={}
 while p<len(b):
  size,p=var(b,p);end=p+size;key,q=cid(b,p);data=b[q:end]
  if hashlib.sha256(data).digest()!=key[1]:raise ValueError('CAR block hash mismatch')
  blocks[key]=data;p=end
 root=m['root_cid'];raw=base64.b32decode(root[1:].upper()+'='*((8-len(root[1:])%8)%8));key,_=cid(raw)
 indexed_root_present=key in blocks
 if not indexed_root_present:
  # CAR v1 single root is CBOR tag 42 followed by bytes prefixed by zero.
  marker=header.find(bytes.fromhex('d82a'))
  if marker<0:raise ValueError('CAR root absent')
  q=marker+2;lead=header[q];q+=1
  if lead==0x58:q+=1
  elif lead==0x59:q+=2
  elif not 0x40<=lead<=0x57:raise ValueError('Unsupported CBOR root length')
  if header[q]!=0:raise ValueError('CID prefix')
  key,_=cid(header,q+1)
 def read(k):
  data=blocks[k]
  if k[0]==0x55:return data
  f=fields(data);uf=fields(next((v for t,v in f if t==1),b''));typ=next((v for t,v in uf if t==1),None)
  own=next((v for t,v in uf if t==2),b'');links=[]
  for t,v in f:
   if t==2:
    lf=fields(v);lk,_=cid(next(x for t,x in lf if t==1));name=next((x.decode() for t,x in lf if t==2),'');links.append((name,lk))
  if typ==1:return read(next(k for name,k in links if name==m['leaf_path']))
  return own+b''.join(read(k) for _,k in links)
 return read(key),indexed_root_present,len(blocks)

def main():
 ap=argparse.ArgumentParser(description='Recover missing exhibition media from the frozen source manifest. Existing files are checked, never silently replaced.');ap.add_argument('--recover-missing',action='store_true');args=ap.parse_args()
 import tempfile
 data=json.loads((P/'dist/data/sources.json').read_text())
 for e in data['items']:
  for m in e['media']:
   dst=P/'dist'/m['file']
   if dst.exists():
    if sha(dst.read_bytes())!=m['sha256']:raise ValueError('Existing file differs: '+str(dst))
    continue
   if not args.recover_missing:raise FileNotFoundError(str(dst)+'; rerun with --recover-missing')
   b=urllib.request.urlopen(m['arweaveUrl'],timeout=120).read()
   if sha(b)!=m['carSha256']:raise ValueError('Source CAR differs')
   raw,root_present,block_count=extract(b,{'root_cid':m['indexedRootCid'],'leaf_path':m['leafPath']})
   if sha(raw)!=m['originalFileSha256']:raise ValueError('Decoded source differs')
   with tempfile.TemporaryDirectory() as tmp:
    src=Path(tmp)/'source';src.write_bytes(raw);candidate=Path(tmp)/dst.name
    if m['kind']=='image':
     from PIL import Image
     im=Image.open(src);im.thumbnail((1400,1400));im.convert('RGB').save(candidate,'WEBP',quality=88)
    else:subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-vn','-codec:a','libmp3lame','-b:a','112k',str(candidate)],check=True)
    if sha(candidate.read_bytes())!=m['sha256']:raise ValueError('Encoder output differs from frozen edition; obtain the released file instead, or create a new derivative edition.')
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(candidate.read_bytes())
   print('Recovered',m['file'],flush=True)
 print('Frozen media copies consistent. This is file validation, not chain consensus verification.')
if __name__=='__main__':main()
