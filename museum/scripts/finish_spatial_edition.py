"""Prepare viewing positions, or refresh only permitted exhibition provenance."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');a=p.parse_args()
P=Path(__file__).resolve().parents[1];D=P/'dist';H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if a.prepare:
 layout=read(D/'data/gallery-layout.json');layout['rooms'][0]['entryZ']=-4.4
 for path in [D/'data/gallery-layout.json',P/'scene/gallery-layout.json']:write(path,layout)
 path=D/'museum.js';s=path.read_text().replace('galleryLayout.endZ+2.8','galleryLayout.endZ+4.5')
 s=s.replace("function updateUI(){document.body.dataset.reducedMotion", "function updateUI(){document.body.dataset.presentation=String(touring);document.body.dataset.reducedMotion")
 s=s.replace("const active=touring;if(active)guideResume=", "const active=touring,hadEnded=tourElapsed>=tourDuration;if(hadEnded){tourElapsed=0;guideResume=null;}if(active)guideResume=")
 s=s.replace('if(roomData&&active)updateUI();','if(roomData&&(active||hadEnded))updateUI();')
 # Transparent presentation controls preserve the main pause and room navigation.
 path.write_text(s)
 path=D/'museum.css';s=path.read_text();s+='\nbody[data-presentation="true"] #exhibit-strip,body[data-presentation="true"] #focus-tools,body[data-presentation="true"] #walk-controls,body[data-presentation="true"] #look-controls{display:none!important}\n';path.write_text(s)
 print('Presentation framing prepared',flush=True)
else:
 # Hash checks validate identity, not philosophical claims or new chain consensus.
 for e in read(D/'data/sources.json')['items']:
  if e.get('localRecord'):assert H((D/e['localRecord']).read_bytes())==e['sourceSha256'],e['id']
  for m in e['media']:assert H((D/m['file']).read_bytes())==m['sha256'],m['file']
 for e in read(D/'data/curation.json')['items']:
  if e.get('originalText'):assert H((D/e['localRecord']).read_bytes())==e['originalSha256'],e['id']
 for f in read(D/'data/public-flaws.json')['items']:assert H((D/f['file']).read_bytes())==f['sha256'],f['file']
 path=D/'data/crystal-model.json';data=read(path)
 for f in data['files']:
  content=(P/f['path']).read_bytes()
  if f['path'].endswith(('.glb','.blend','.png','.jpg')):assert H(content)==f['sha256'],'Original crystal asset changed'
  f.update(bytes=len(content),sha256=H(content))
 write(path,data)
 print('All historical texts, images, songs, microscope evidence and crystal assets retain their recorded digests',flush=True)
