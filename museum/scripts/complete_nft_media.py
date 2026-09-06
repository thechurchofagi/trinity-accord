"""Recover each omitted media leaf of an exhibited NFT as a bound work component."""
from pathlib import Path
import sys,json,hashlib,urllib.request,concurrent.futures,io,subprocess,tempfile
from PIL import Image
from prepare_sources import extract
P=Path(__file__).resolve().parents[1];D=P/'dist'
H=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads((P/'scene/media-completion-plan.json').read_text())
def recover(job):
 m=job['source'];eid=job['exhibit']
 try:
  b=urllib.request.urlopen('https://arweave.net/'+m['txid'],timeout=45).read()
  if H(b)!=m['sha256']:raise ValueError('CAR digest mismatch')
  raw,present,count=extract(b,{'root_cid':m['cid'],'leaf_path':m['leaf']})
  extra={}
  try:
   im=Image.open(io.BytesIO(raw));im.load();kind='image'
  except Exception:kind='audio'
  f='assets/'+eid+('.webp' if kind=='image' else '.mp3');dst=D/f
  if dst.exists():raise ValueError('Refusing to replace existing '+f)
  if kind=='image':
   extra['sourceDimensions']=list(im.size);im.thumbnail((2048,2048));im.convert('RGB').save(dst,'WEBP',quality=94);processing='Complete source image, fit within 2048px, WebP quality 94; no generative editing.'
  else:
   with tempfile.NamedTemporaryFile() as t:
    t.write(raw);t.flush();subprocess.run(['ffmpeg','-v','error','-i',t.name,'-vn','-codec:a','libmp3lame','-b:a','128k',str(dst)],check=True)
   extra['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(dst)]));processing='Full original track transcoded to MP3 128 kbps without trimming.'
  return {'exhibit':eid,'media':{'kind':kind,'file':f,'sha256':H(dst.read_bytes()),'bytes':dst.stat().st_size,'originalFileSha256':H(raw),'originalFileBytes':len(raw),'arweaveUrl':'https://arweave.net/'+m['txid'],'carSha256':H(b),'indexedRootCid':m['cid'],'indexedRootPresentInCar':present,'verifiedCarBlocks':count,'leafPath':m['leaf'],'processing':processing,'verificationScope':'CAR and included block digests checked; no fresh chain consensus or metadata-binding claim.',**extra}}
 except Exception as e:return {'exhibit':eid,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(recover,plan['jobs']))
sources=json.loads((D/'data/sources.json').read_text())
for r in results:
 if 'media' in r:next(e for e in sources['items'] if e['id']==r['exhibit'])['media'].append(r['media'])
 print(r['exhibit'],r.get('media',{}).get('kind'),r.get('error','OK'),flush=True)
(D/'data/sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
(P/'scene/media-completion-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
