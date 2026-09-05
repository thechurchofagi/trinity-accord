"""Validate a frozen edition; no source downloads, network access, or manifest rewriting."""
from pathlib import Path
import hashlib,json,re,sys
from html.parser import HTMLParser
P=Path(__file__).resolve().parents[1];D=P/'dist';errors=[]
def check(ok,what):
 if not ok:errors.append(what)
def read(n):return json.loads((D/'data'/n).read_text())
rooms=read('rooms.json');sources=read('sources.json');guides=read('narration.json');release=read('release-manifest.json')
check(rooms['edition']==sources['edition']==release['edition'],'Edition mismatch')
ids=[e['id'] for e in sources['items']];check(len(ids)==len(set(ids)),'Duplicate source ID')
extra={'canon-1','canon-2','canon-3','physical-alpha','evidence-path','authority-boundary','museum-history','first-contact','current-status'}
for r in rooms['rooms']:
 for id in r['exhibits']:check(id in ids or id in extra,'Missing exhibit '+id)
 check(any(t['room']==r['id'] for t in guides['tracks']),'Missing narration '+r['id'])
for e in sources['items']:
 check('/blob/'+sources['sourceCommit']+'/' in e['sourceUrl'],'Unpinned source '+e['id'])
 for m in e['media']:
  f=D/m['file'];check(f.exists(),'Missing media '+m['file'])
  if f.exists():check(hashlib.sha256(f.read_bytes()).hexdigest()==m['sha256'],'Wrong media digest '+m['file'])
  check(bool(m.get('processing')) and bool(m.get('originalFileSha256')),'Missing derivative provenance '+m['file'])
for t in guides['tracks']:
 f=D/t['file'];check(f.exists(),'Missing guide file '+t['file'])
 if f.exists():check(hashlib.sha256(f.read_bytes()).hexdigest()==t['sha256'],'Wrong guide digest '+t['file'])
 r=next(r for r in rooms['rooms'] if r['id']==t['room']);check(r['narration']==t['text'],'Guide text drift '+t['room'])
listed=set()
for f in release['files']:
 path=D/f['path'];listed.add(f['path']);check(path.exists(),'Missing released file '+f['path'])
 if path.exists():
  b=path.read_bytes();check(hashlib.sha256(b).hexdigest()==f['sha256'] and len(b)==f['bytes'],'Release digest mismatch '+f['path'])
actual={p.relative_to(D).as_posix() for p in D.rglob('*') if p.is_file() and p.name!='release-manifest.json'}
check(actual==listed,'Release inventory drift')
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k not in ['src','href'] or not v or v.startswith(('http:','https:','data:','#','mailto:')):continue
   check((D/v.split('#')[0].split('?')[0]).exists(),'Broken local HTML reference '+v)
for f in ['index.html','archive.html']:Links().feed((D/f).read_text())
for js in ['museum.js','vendor/three.module.js','vendor/three.core.js']:
 for dep in re.findall(r'(?:from|import)\s*[\'"]([^\'"]+)[\'"]',(D/js).read_text()):
  if dep.startswith('.'):check((D/js).parent.joinpath(dep).exists(),'Missing module '+dep)
check((D/'assets/core-object-alpha.jpg').exists(),'Missing physical photograph')
check(hashlib.sha256((D/'assets/core-object-alpha.jpg').read_bytes()).hexdigest()=='40eddec02dce4958d28aff94496923983e870346ce98c1cb16181012545475b6','Physical photograph changed')
if errors:
 print('\n'.join(errors));sys.exit(1)
print('PASS: source identities, derivative digests, guide text/audio bindings, release inventory, HTML references and vendored imports.')
print(len(rooms['rooms']),'rooms;',len(ids),'Ethereum exhibits;',len(release['files']),'distribution files.')
