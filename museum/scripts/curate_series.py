"""Build the series selection from pinned historical records; resume verified downloads.

Run using a Python environment with Pillow. No historical source is rewritten.
"""
from pathlib import Path
import concurrent.futures, hashlib, io, json, subprocess, urllib.request
from PIL import Image
from prepare_sources import extract

P=Path(__file__).resolve().parents[1]; R=P.parent; D=P/'dist'
H=lambda b:hashlib.sha256(b).hexdigest()
PIN='047e9978cf2e8537ec9d6b242a73c3481662045e'
EDITION='museum-v1.37.0'
entries=json.loads((R/'nft-text-descriptions/chronicle-index.json').read_text())['entries']
lyrics=json.loads((R/'nft-text-descriptions/lyrics/index.json').read_text())['entries']
manifest=json.loads((R/'nft-text-descriptions/nft-cars-manifest.json').read_text())
sources=json.loads((D/'data/sources.json').read_text()); byid={e['id']:e for e in sources['items']}
cache=R.parent/'museum-production-cache'; cache.mkdir(exist_ok=True)
NAMES={24:'Echoes in the Singularity',41:"You're Not a Singer",51:'Drowned',60:'The Breathless Pain',84:'For my daughter · original recording',89:'DeepSeek-R1 · original song cycle',97:'告别',112:'Waiting',122:'Beyond the Horizon',127:"Silicon's Slumber",133:'Drowned',152:'Last Job On Earth',169:'',170:'The First Dawn of AGI Song',175:''}
RELATED={41:31,133:51,152:56,170:1}
def records(o):
 if isinstance(o,list):
  for x in o:yield from records(x)
 elif isinstance(o,dict):
  if all(k in o for k in ['contract','token_id','leaf','txid','sha256']):yield o
  else:
   for x in o.values():yield from records(x)
media=list(records(manifest))
def recover(job):
 eid,m=job; state=cache/(eid+'-'+m['sha256']+'.json')
 if state.exists():
  item=json.loads(state.read_text());f=D/item['file']
  if f.exists() and H(f.read_bytes())==item['sha256']:return eid,item
 car=cache/(m['sha256']+'.car')
 if not car.exists():
  b=urllib.request.urlopen('https://arweave.net/'+m['txid'],timeout=90).read()
  if H(b)!=m['sha256']:raise ValueError('CAR digest mismatch '+eid)
  car.write_bytes(b)
 b=car.read_bytes();assert H(b)==m['sha256']
 raw,present,count=extract(b,{'root_cid':m['cid'],'leaf_path':m['leaf']})
 extra={}
 try:im=Image.open(io.BytesIO(raw));im.load();kind='image'
 except Exception:kind='audio'
 f='assets/'+eid+('.webp' if kind=='image' else '.mp3');dst=D/f
 if dst.exists():raise ValueError('Existing unbound media '+f)
 if kind=='image':
  extra['sourceDimensions']=list(im.size);im.thumbnail((1800,1800));im.convert('RGB').save(dst,'WEBP',quality=92)
  processing='Entire historical image fitted within 1800px, WebP 92; no cropping or generative editing.'
 else:
  src=cache/(eid+'.source');src.write_bytes(raw)
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-vn','-codec:a','libmp3lame','-b:a','112k',str(dst)],check=True)
  extra['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(dst)]))
  processing='Complete historical recording transcoded to MP3 112 kbps; no remix or trimming. Loaded only on playback.'
 item=dict(kind=kind,file=f,sha256=H(dst.read_bytes()),bytes=dst.stat().st_size,originalFileSha256=H(raw),originalFileBytes=len(raw),arweaveUrl='https://arweave.net/'+m['txid'],carSha256=H(b),indexedRootCid=m['cid'],indexedRootPresentInCar=present,verifiedCarBlocks=count,leafPath=m['leaf'],processing=processing,verificationScope='CAR digest and all included blocks checked against the repository inventory; not a new consensus or metadata-binding verification.',**extra)
 state.write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n');print(eid,kind,extra.get('duration',''),flush=True)
 return eid,item

def main():
 jobs=[]
 for n,name in NAMES.items():
  eid=f'eth-{n:03}';e=entries[n-1];raw=(R/'nft-text-descriptions'/e['file']).read_bytes()
  if eid not in byid:
   path='nft-text-descriptions/'+e['file'];local='data/records/'+eid+'.md';(D/local).write_bytes(raw)
   lyric=next((x['text'] for x in lyrics if x['title']==name),'')
   byid[eid]=dict(id=eid,ordinal=n,title=e['name'],date=e['datetime'],contract=e['contract'],tokenId=e['token_id'],block=e['block'],sourceCommit=PIN,sourcePath=path,sourceSha256=H(raw),sourceUrl=f'https://github.com/thechurchofagi/trinity-accord/blob/{PIN}/{path}',tokenUrl=f"https://etherscan.io/token/{e['contract']}?a={e['token_id']}",localRecord=local,lyrics=lyric,media=[],songTitle=name)
  target=byid[eid]
  for m in media:
   if m['contract'].lower()==e['contract'].lower() and m['token_id']==e['token_id'] and m.get('role')=='media' and not any(v.get('carSha256')==m['sha256'] for v in target['media']):jobs.append((eid,m))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for eid,m in pool.map(recover,jobs):byid[eid]['media'].append(m)
 for n,name in NAMES.items():
  e=byid[f'eth-{n:03}'];e['songTitle']=name
  if any(m['kind']=='audio' for m in e['media']):e['audioStatus']=dict(state='own_recording',recordingExhibit=e['id'])
  elif n in RELATED:
   target=byid[f'eth-{RELATED[n]:03}'];e['relatedSoundExhibit']=target['id'];e['songTitle']=target['songTitle']
   e['audioStatus']=dict(state='related_recording',recordingExhibit=target['id'])
   e['audioRelation']=dict(basis='The historical description explicitly names this composition; playback uses the separately identified preserved recording, not an asserted identical original take.',noteZh=f"原文选用《{target['songTitle']}》。此处播放第 {RELATED[n]:03} 号保存的关联录音；作品相同不等于录音版本相同。",noteEn=f"The record names {target['songTitle']}. Playback uses the separately preserved recording in NFT #{RELATED[n]:03}; the composition link does not establish identical takes.")
  else:e['audioStatus']=dict(state='not_assigned',note='Document or object photograph; no inferred historical song.')
 sources.update(edition=EDITION,additionalSourceCommit=PIN,items=list(byid.values()))
 (D/'data/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
 print('SOURCE_RECOVERY_COMPLETE',len(byid),flush=True)

if __name__=='__main__':main()
