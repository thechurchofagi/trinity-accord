"""Recover No.122's original image only; no substitute art or inferred soundtrack."""
from pathlib import Path
import hashlib,io,json,subprocess,time,urllib.request
from PIL import Image
from prepare_sources import extract
P=Path(__file__).resolve().parents[1];R=P.parent;D=P/'dist'
COMMIT='e99669424e743eea42fb78cfa120c177199c209d'
H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def pinned(path):return subprocess.check_output(['git','show',COMMIT+':'+path],cwd=R)
sources=read(D/'data/sources.json')
if not any(e['id']=='eth-122' for e in sources['items']):
 index_raw=pinned('nft-text-descriptions/chronicle-index.json');index=json.loads(index_raw)['entries'];row=next(e for e in index if e['ordinal']==122)
 path='nft-text-descriptions/'+row['file'];raw=pinned(path)
 assert row['datetime'].replace('.000Z','Z')=='2025-03-14T17:01:11Z',row['datetime']
 (D/'data/records/eth-122.md').write_bytes(raw)
 write(D/'data/records/eth-122-index.json',dict(sourceCommit=COMMIT,sourcePath='nft-text-descriptions/chronicle-index.json',sourceSha256=H(index_raw),entry=row))
 cars=json.loads(pinned('nft-text-descriptions/nft-cars-manifest.json'))['files']
 matches=[m for m in cars if m['role']=='media' and m['contract'].lower()==row['contract'].lower() and str(m['token_id'])==str(row['token_id']) and m['leaf'].startswith('image.')]
 assert len(matches)==1,'Expected one preserved original image, not a replacement';m=matches[0]
 url='https://arweave.net/'+m['txid']
 for attempt in range(3):
  try:car=urllib.request.urlopen(url,timeout=60).read();assert H(car)==m['sha256'];break
  except Exception:
   if attempt==2:raise
   time.sleep(2)
 image,present,count=extract(car,dict(root_cid=m['cid'],leaf_path=m['leaf']))
 im=Image.open(io.BytesIO(image));im.load();dimensions=list(im.size);im.thumbnail((2048,2048));dst=D/'assets/eth-122.webp';im.convert('RGB').save(dst,'WEBP',quality=94)
 media=dict(kind='image',file='assets/eth-122.webp',sha256=H(dst.read_bytes()),bytes=dst.stat().st_size,originalFileSha256=H(image),originalFileBytes=len(image),arweaveUrl=url,carSha256=H(car),indexedRootCid=m['cid'],indexedRootPresentInCar=present,verifiedCarBlocks=count,leafPath=m['leaf'],sourceDimensions=dimensions,processing='Complete original image fitted within 2048px, WebP quality 94; no cropping, compositing or generative editing.',verificationScope='Pinned inventory, CAR and included block digest checks; no new chain consensus verification.')
 sources['items'].append(dict(id='eth-122',ordinal=122,title=row['name'],displayTitle='GPT-4 两周年：守候一个时刻',en='GPT-4 at Two: Keeping a Moment',date=row['datetime'],contract=row['contract'],tokenId=row['token_id'],block=row['block'],sourceCommit=COMMIT,sourcePath=path,sourceSha256=H(raw),sourceUrl=f'https://github.com/thechurchofagi/trinity-accord/blob/{COMMIT}/{path}',tokenUrl=f"https://etherscan.io/nft/{row['contract']}/{row['token_id']}",localRecord='data/records/eth-122.md',lyrics='',media=[media],audioStatus=dict(state='not_assigned',note='Only the verified original image is displayed; no soundtrack is inferred.'),text='原文所述时刻：北京时间 2025-03-15 01:00。项目索引的铸造区块时间：01:01:11（UTC 2025-03-14 17:01:11）。前者是历史文字，后者是索引所列链上时刻；都不是点击铸造按钮的现场录像。',textEn='Time named in the source: 15 March 2025, 01:00 Beijing. Indexed mint-block time: 01:01:11 (14 March, 17:01:11 UTC). A historical statement and an indexed block time are different evidence, neither a video of a button being pressed.'))
 write(D/'data/sources.json',sources)
 print('Recovered and verified original No.122 image',dimensions,flush=True)
# Related guardianship documents are explicitly separate from the three Originals.
charter=pinned('bitcoin-inscription-mirrors/raw/103635270.txt');(D/'data/records/guardian-charter-103635270.txt').write_bytes(charter)
write(D/'data/guardian-sources.json',dict(schema='trinity-museum.guardian-sources.v1',boundary='Later guardianship material, not a fourth Original. No claim that blockchain prevents later speech or website edits.',principles=dict(title='Guardian Principles v1.1',url='https://www.trinityaccord.org/authority/',type='Website guardianship mirror; distinct from the later charter'),charter=dict(title='Guardian Appendix / Authority Charter (non-amending)',number='103635270',file='data/records/guardian-charter-103635270.txt',sha256=H(charter),sourceCommit=COMMIT,sourceUrl=f'https://github.com/thechurchofagi/trinity-accord/blob/{COMMIT}/bitcoin-inscription-mirrors/raw/103635270.txt')))
# Keep all previous recording assignments and audit the new image-only entry honestly.
audit=read(D/'data/audio-audit.json');old={e['exhibit']:e for e in audit['items']};old['eth-122']=dict(exhibit='eth-122',state='not_assigned',reason='Verified original image; no recording assigned in this edition.')
wall=[e['id'] for r in read(D/'data/gallery-layout.json')['rooms'] for e in r['exhibits']];audit['items']=[old[id] for id in wall];audit['counts']=dict(wallExhibits=41,withSound=28,withoutAssignedSong=13);audit['scope']='All 41 display entries; 28 original or explicitly related recordings, 13 without an assigned recording. No.122 is image-only in this edition.';write(D/'data/audio-audit.json',audit)
