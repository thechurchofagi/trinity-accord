#!/usr/bin/env python3
import json, os, pathlib, subprocess, tempfile

TARGETS={
 'bafybeieofybnvwz4qkmseon5zhye7fshzqosbsbsvl46buqoxtzzjzbf54':('polygon','0x5ed7eb7b81068ea23bc170be48b4a0e99262aa6d','1'),
 'bafybeihkjhsxzsyx47syfhh5drqhbcsix5qssvyduxyedswed6k3f6lumq':('polygon','0xe0a63a9eb48f2662a429f9f51c6ddbc1a54deb4a','1'),
}

def ordered(m):
 keys=['name','description','external_url','image','animation_url','attributes','properties']
 return {**{k:m[k] for k in keys if k in m},**{k:v for k,v in m.items() if k not in keys}}

def ascii_json(text):
 return ''.join(c if ord(c)<128 else ''.join('\\u%04x'%ord(x) for x in c.encode('utf-16-be').decode('utf-16-be')) for c in text)

def variants(m):
 v=ordered(m); seen=set()
 for ensure_ascii in (False,True):
  specs=[('compact',json.dumps(v,ensure_ascii=ensure_ascii,separators=(',',':'))),('spaced',json.dumps(v,ensure_ascii=ensure_ascii,separators=(', ',': ')))]
  for indent in range(1,9): specs.append((f'pretty{indent}',json.dumps(v,ensure_ascii=ensure_ascii,indent=indent)))
  specs.append(('tabs',json.dumps(v,ensure_ascii=ensure_ascii,indent='\t')))
  for label,text in specs:
   for slash in (False,True):
    body=text.replace('/','\\/') if slash else text
    for endname,end in (('none',''),('lf','\n'),('crlf','\r\n')):
     for bom in (False,True):
      data=(body+end).encode(); data=(b'\xef\xbb\xbf'+data) if bom else data
      if data in seen: continue
      seen.add(data)
      yield f"{'ascii' if ensure_ascii else 'utf8'}_{label}{'_slash' if slash else ''}_{endname}{'_bom' if bom else ''}",data

def root_for(kubo,data,raw_leaves):
 with tempfile.TemporaryDirectory() as td:
  root=pathlib.Path(td)/'root'; root.mkdir(); (root/'token.json').write_bytes(data)
  out=subprocess.check_output([kubo,'add','-Q','--pin=false','--only-hash','--cid-version=1',f'--raw-leaves={str(raw_leaves).lower()}','--chunker=size-262144','-r',str(root)],text=True,stderr=subprocess.STDOUT,timeout=30)
  return out.strip().split()[-1]

def main():
 root=pathlib.Path(os.environ.get('CHRONICLE_OUT','artifacts/chronicle-sidechain-scan'))
 kubo=os.environ['CHRONICLE_KUBO_BIN']
 records=json.loads((root/'recovered-tokens.json').read_text())
 by={(('polygon' if int(r.get('chain_id',0))==137 else 'base'),str(r.get('contract','')).lower(),str(r.get('token_id'))):r for r in records}
 result={}
 for cid,coord in TARGETS.items():
  r=by[coord]; found=None; checked=0
  for label,data in variants(r['metadata']):
   for raw in (False,True):
    checked+=1; got=root_for(kubo,data,raw)
    if got==cid:
     found={'variant':label,'raw_leaves':raw,'bytes':len(data),'checked':checked}; break
   if found: break
  result[cid]={'match':found,'checked':checked,'metadata':r['metadata'],'token_uri':r.get('token_uri')}
 print(json.dumps(result,ensure_ascii=False,indent=2))
 pathlib.Path('directory-root-research.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': main()
