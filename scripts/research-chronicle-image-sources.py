#!/usr/bin/env python3
import base64, hashlib, json, os, pathlib, re, subprocess, tempfile, urllib.request

TARGETS={
 'QmNTjiSRWuZfxzjH3QH9j5D3bEB957jS1psMuc9RFqB4QT':('polygon','0x9a3a7ddde5712b090181937bd7f0a6e2084707e6','0'),
 'QmRTbRbkfpjnU3cW4p8FW4rjuKjHx7B2MuhE2n8qLZtMah':('base','0xf616ba3cfab4d17477d7c63d775666dcb1e5542d','0'),
 'QmRX4GtfNvGrG2FgbtJdhUUx4ocyGk9aEqzgD7zsTEUAva':('polygon','0x001007e8ab86f6ba6f477712c8b8db84887d0175','0'),
 'QmS4RcwE3J4JzNRAE1crQXM2Joex53TEgAXtN6nBDkWtRC':('base','0x1f26a5a197b4bed502e0a5a05d22b625406d05c1','0'),
 'QmYxaovCTVY2EiXBWgvBdtpFCKyoom6bYSBTcxJ5UJweJ1':('base','0x3acfeebf6cd63f61ae6096dafc7dab7675bf7e77','0'),
 'bafkreiel7mdl7timheywsmexzvnvkupu4jnqksjzh7pjsrn43tscvmoqfa':('polygon','0xad4bda0b463ace68dd640b14891b00a7fe1caccf','1'),
}
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58decode(s):
 n=0
 for c in s:n=n*58+B58.index(c)
 raw=n.to_bytes((n.bit_length()+7)//8,'big') if n else b''
 return b'\0'*(len(s)-len(s.lstrip('1')))+raw

def digest(cid):
 if cid.startswith('Qm'): return b58decode(cid)[2:34]
 raw=base64.b32decode(cid[1:].upper()+'='*((8-len(cid[1:])%8)%8)); return raw[4:36]

def urls_in(v,out):
 if isinstance(v,str):
  if v.startswith(('http://','https://','ipfs://')):out.add(v)
 elif isinstance(v,list):
  for x in v:urls_in(x,out)
 elif isinstance(v,dict):
  for x in v.values():urls_in(x,out)

def fetch(url,timeout=12):
 req=urllib.request.Request(url,headers={'User-Agent':'trinity-accord-historical-image-recovery/1.0','Accept':'*/*'})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  if getattr(r,'status',200)!=200:raise RuntimeError(f'HTTP {getattr(r,"status",None)}')
  data=r.read(50*1024*1024+1)
  if len(data)>50*1024*1024:raise RuntimeError('too large')
  return data,r.geturl(),r.headers.get('Content-Type')

def verify(cid,data,kubo):
 if cid.startswith('bafk'):
  return {'exact':hashlib.sha256(data).digest()==digest(cid),'method':'raw-sha256'}
 with tempfile.NamedTemporaryFile(delete=False) as f:
  f.write(data); name=f.name
 try:
  attempts=[]
  for chunk in ('size-262144','size-1048576'):
   for trickle in (False,True):
    args=[kubo,'add','-Q','--pin=false','--only-hash','--cid-version=0','--raw-leaves=false',f'--chunker={chunk}']
    if trickle:args.append('--trickle')
    args.append(name)
    try:
     got=subprocess.check_output(args,text=True,stderr=subprocess.STDOUT,timeout=30).strip().split()[-1]
     attempts.append({'computed':got,'chunker':chunk,'trickle':trickle})
     if got==cid:return {'exact':True,'method':'kubo-unixfs','attempts':attempts}
    except Exception as e:attempts.append({'error':str(e)[:200],'chunker':chunk,'trickle':trickle})
  return {'exact':False,'method':'kubo-unixfs','attempts':attempts}
 finally:pathlib.Path(name).unlink(missing_ok=True)

def normalize_url(u):
 if u.startswith('ipfs://'):
  return 'https://ipfs.io/ipfs/'+u[7:].replace('ipfs/','',1)
 return u

def main():
 root=pathlib.Path(os.environ.get('CHRONICLE_OUT','artifacts/chronicle-sidechain-scan')); kubo=os.environ['CHRONICLE_KUBO_BIN']
 report={}
 for cid,(chain,contract,tid) in TARGETS.items():
  d=root/chain/contract/tid; src=set()
  historical={}
  for fn in ('blockscout-instance.json','record.json','recovery-diagnostic.json','metadata.normalized.json'):
   p=d/fn
   if p.exists():
    try:
     obj=json.loads(p.read_text()); historical[fn]=obj; urls_in(obj,src)
    except Exception:pass
  # Remove the exact dead IPFS target from source-only probes; normal recovery already exhausts it.
  probes=[]
  for u in sorted(src):
   n=normalize_url(u)
   if cid in n:continue
   if any(x in n for x in ('polygon.drpc.org','base.drpc.org')):continue
   probes.append(n)
  results=[]; exact=[]
  for u in probes[:60]:
   try:
    data,final,ctype=fetch(u); v=verify(cid,data,kubo)
    row={'url':u,'final_url':final,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':ctype,**v}
    results.append(row)
    if v['exact']:exact.append(row)
   except Exception as e:results.append({'url':u,'error':str(e)[:400]})
  report[cid]={'coordinate':[chain,contract,tid],'historical_json':historical,'source_urls':sorted(src),'probes':results,'exact_sources':exact}
 pathlib.Path('image-source-research.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({cid:{'urls':len(r['source_urls']),'exact':len(r['exact_sources'])} for cid,r in report.items()},indent=2))

if __name__=='__main__':main()
