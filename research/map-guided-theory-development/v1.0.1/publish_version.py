#!/usr/bin/env python3
"""Exact-byte linked Zenodo v1.0.1 preprint release. No uncertain POST/PUT replay.
The original v1.0.0 Zenodo record is READ ONLY; this script writes only to the
independent v1.0.1 draft returned by Zenodo's newversion action.
"""
from __future__ import annotations
import argparse, hashlib, html, json, os, pathlib, subprocess, time
import urllib.parse, urllib.request, urllib.error, zipfile
HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[2]
BRANCH='research/mgtd-method-v1-0-1-20261008'
VERSION='1.0.1'
REPORT='METHOD20261008'
TITLE='Map-Guided Theory Development: A Versioned Protocol for Thought Experiments, Semantic Audits, and Human-AI Research'
OLD=23241205
NEW=23241982
CONCEPT='23241204'
DOI=f'10.5281/zenodo.{NEW}'
OLD_DOI=f'10.5281/zenodo.{OLD}'
PDF='MGTD_Method_Paper_v1.0.1.pdf'
MD='MGTD_Method_Paper_v1.0.1.md'
ZIP='MGTD_Method_Paper_v1.0.1_Complete_Package.zip'
EXPECTED={
 PDF:('98abef0e92d0bb599146cdf525d98acb7045a168912ec9e87ba7723bc958097c',138355),
 MD:('0a4b8b47e835f2d0b6c5c584009ed6a9e862ea57a59cd88585ac56aaf9f83515',51242),
 ZIP:('e4899ac0f41e0158c9ab05fbba797addbb9c8aa17346137f6e5992e5561b3ad3',843551),
}
OLD_FILES={
'MGTD_Method_Paper_v1.0.0.pdf','MGTD_Method_Paper_v1.0.0.md',
'MGTD_Method_Paper_v1.0.0_Complete_Package.zip','README-LICENSE.txt','citation.bib'}
PERSIST=('new-version-deposit.json','preparation-status.json','PUBLISH-AUTHORIZATION.json','metadata-updated.json',
         'upload-intents.json','upload-status.json','publication-intent.json','publication-error.json',
         'publication-record.json','publication-checks.json','citation.bib','README-LICENSE.txt')
MAX_READ=8_000_000
MAX_FILE=16_000_000

def sha(b):return hashlib.sha256(b).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf8'))
def save(n,obj):
 p=HERE/n;temp=p.with_name(p.name+'.tmp');temp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf8');temp.replace(p)
def persist():
 if os.environ.get('GITHUB_ACTIONS')!='true':return
 active=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
 if active!=BRANCH:raise RuntimeError('Refusing Git checkpoint outside new-version branch')
 paths=[str((HERE/n).relative_to(REPO)) for n in PERSIST if (HERE/n).exists()]
 if not paths:return
 subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
 subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
 subprocess.run(['git','add','--',*paths],cwd=REPO,check=True)
 if subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():
  subprocess.run(['git','commit','-m','[skip ci] Save exact MGTD v1.0.1 deposit and public readback stage'],cwd=REPO,check=True)
  subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):raise RuntimeError('Zenodo bearer-token redirect refused')

def api(path,method='GET',payload=None,binary=False,auth=True):
 if auth and (os.environ.get('GITHUB_ACTIONS')!='true' or not os.environ.get('ZENODO_ACCESS_TOKEN')):
  raise RuntimeError('Existing Zenodo repository secret inside GitHub Actions required')
 url=path if path.startswith('https://') else ('https://zenodo.org'+path if path.startswith('/api/') else 'https://zenodo.org/api'+path)
 uri=urllib.parse.urlsplit(url)
 if uri.scheme!='https' or uri.netloc!='zenodo.org' or uri.fragment or uri.username or uri.password:
  raise RuntimeError('Zenodo endpoint not authorized')
 headers={'User-Agent':'MGTD-v101-Exact-Version-Publication/1.0'}
 if auth:headers['Authorization']='Bearer '+os.environ['ZENODO_ACCESS_TOKEN']
 if payload is not None:
  data=payload if binary else json.dumps(payload).encode('utf8')
  headers['Content-Type']='application/octet-stream' if binary else 'application/json'
 else:data=None
 request=urllib.request.Request(url,headers=headers,data=data,method=method)
 with urllib.request.build_opener(NoRedirect()).open(request,timeout=110) as response:
  raw=response.read(MAX_READ+1)
 if len(raw)>MAX_READ:raise RuntimeError('API response too large')
 return json.loads(raw) if raw else None

def get(path,auth=True):
 for k in range(3):
  try:return api(path,auth=auth)
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
   if k==2:raise
   time.sleep(3*(k+1))

def verify_local():
 desired={'authorized':True,'record_id':NEW,'doi':DOI,'version':VERSION,
          'previous_record_id':OLD,'previous_doi':OLD_DOI,'arweave_scope':'V101_ONLY_AFTER_OTS_VERIFIED'}
 if load('PUBLISH-AUTHORIZATION.json')!=desired:raise RuntimeError('Exact author-version authorization mismatch')
 d=load('new-version-deposit.json')
 if (d.get('record_id'),d.get('doi'),str(d.get('conceptrecid')),d.get('prior_record_id'))!=(NEW,DOI,CONCEPT,OLD):
  raise RuntimeError('Not the previously linked draft')
 for name,(hexhash,n) in EXPECTED.items():
  p=HERE/name
  if p.stat().st_size!=n or sha(p.read_bytes())!=hexhash:raise RuntimeError('Frozen file changed: '+name)
 md=(HERE/MD).read_text(encoding='utf8')
 if any(x in md for x in ['__MGTD_V101_DOI__','not a DOI registration','prepared for author review']):
  raise RuntimeError('Stale draft wording survived')
 if not all(x in md for x in [DOI,OLD_DOI,'MGTD-PAPER-v1.0.1','not peer reviewed']):
  raise RuntimeError('New-version source missing publication identity')
 if not (HERE/PDF).read_bytes().startswith(b'%PDF-'):raise RuntimeError('Not PDF')
 with zipfile.ZipFile(HERE/ZIP) as z:
  if z.testzip() is not None:raise RuntimeError('ZIP damaged')
  pref='MGTD_Method_Paper_v1.0.1/'
  if sha(z.read(pref+PDF))!=EXPECTED[PDF][0] or sha(z.read(pref+MD))!=EXPECTED[MD][0]:
   raise RuntimeError('Reproduction archive does not bind exact primary files')
 print('MGTD_V101_FROZEN_REVIEW_PASS')

def validate_draft(d):
 if d.get('id')!=NEW or str(d.get('conceptrecid'))!=CONCEPT:
  raise RuntimeError('Draft not linked to original Zenodo record')
 if d.get('submitted'):
  if not (HERE/'publication-intent.json').exists():raise RuntimeError('Published draft without local publish intent')
 m=d.get('metadata',{})
 if m.get('title')!=TITLE:raise RuntimeError('Unexpected version title')
 if d.get('doi') not in (None,DOI):raise RuntimeError('Draft unexpected DOI')
 return d

def metadata(source):
 abstract=source.split('## Abstract {-}',1)[1].split('**Keywords:**',1)[0].strip()
 return {
 'upload_type':'publication','publication_type':'preprint','title':TITLE,
 'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
 'description':'<p>'+html.escape(abstract)+'</p><p>Corrected v1.0.1 Zenodo version of DOI '+OLD_DOI+'. Editorial corrections to title-page and publication-status statements only; theory and reproducibility evidence remain unchanged. Substantial ChatGPT assistance under human direction; not independently peer-reviewed. No measured improvement in scientific productivity is claimed.</p>',
 'publication_date':'2026-10-08','version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
 'keywords':['map-guided theory development','thought experiments','semantic review','version control','human-AI scientific research','reproducibility'],
 'notes':f'MGTD-PAPER-v1.0.1; previous DOI {OLD_DOI}; new PDF SHA256 {EXPECTED[PDF][0]}; exact version linked by Zenodo newversion. NOT externally peer reviewed.',
 'related_identifiers':[{'identifier':'10.5281/zenodo.23206492','relation':'references','scheme':'doi'}]
 }

def update_metadata(d):
 if d.get('submitted'):return d
 m=d.get('metadata',{})
 if str(m.get('version'))==VERSION and EXPECTED[PDF][0] in m.get('notes',''):
  return d
 if (HERE/'metadata-updated.json').exists():
  raise RuntimeError('Metadata PUT uncertain or drifted; reconcile prior operation')
 out=api('/deposit/depositions/'+str(NEW),method='PUT',payload={'metadata':metadata((HERE/MD).read_text())})
 if not out or out.get('id')!=NEW:raise RuntimeError('Unexpected metadata response; manual review')
 fresh=validate_draft(get('/deposit/depositions/'+str(NEW)))
 if str(fresh.get('metadata',{}).get('version'))!=VERSION or EXPECTED[PDF][0] not in fresh.get('metadata',{}).get('notes',''):
  raise RuntimeError('Metadata did not persist as intended')
 save('metadata-updated.json',{'state':'VERSION_METADATA_READY','version':VERSION,'record_id':NEW})
 persist()
 return fresh

def names(d):
 rows={}
 for it in d.get('files',[]):
  n=it.get('filename') or it.get('key')
  if n in rows:raise RuntimeError('Duplicate filename in Zenodo draft: '+str(n))
  rows[n]=it
 return rows

def same(row,b):
 checksum=row.get('checksum') or row.get('checksum_md5')
 actualsize=row.get('filesize',row.get('size'))
 expected=hashlib.md5(b).hexdigest()
 return actualsize==len(b) and checksum in (expected,'md5:'+expected)

def delete_inherited(d,desired_files):
 if d.get('submitted'):return d
 current=names(d)
 keep=set(desired_files)
 unknown=set(current)-(OLD_FILES | keep)
 if unknown:raise RuntimeError('Unexpected draft file(s): '+repr(sorted(unknown)))
 for n in sorted(set(current)&OLD_FILES):
  if n in desired_files and same(current[n],desired_files[n]):continue
  f=current[n]
  fid=f.get('id')
  if not fid:raise RuntimeError('Missing inherited draft file id')
  api(f'/deposit/depositions/{NEW}/files/{urllib.parse.quote(str(fid))}',method='DELETE')
  checked=names(get('/deposit/depositions/'+str(NEW)))
  if n in checked:raise RuntimeError('Inherited old file still present')
  persist()
 return get('/deposit/depositions/'+str(NEW))

def make_files():
 bib=f'''@misc{{Liu2026MGTDv101,\n author = {{Liu, Hongju}},\n title = {{{TITLE}}},\n year = {{2026}},\n version = {{{VERSION}}},\n doi = {{{DOI}}},\n url = {{https://doi.org/{DOI}}},\n note = {{Corrected version of {OLD_DOI}; not peer reviewed}}\n}}\n'''
 license_text=f'''MGTD-PAPER-v1.0.1 | METHOD20261008\n{TITLE}\nVersion DOI: {DOI}\nOriginal version DOI: {OLD_DOI}\n\nThe updated version corrects outdated title-page and publication-stage statements only; scientific content, mathematics, source records and empirical limitations are unchanged. Independent review or empirical efficacy is not claimed. Human author of record and responsible depositor: Hongju Liu; substantial ChatGPT assistance was used under human direction.\n\nCC BY 4.0 applies to original material where rights are held. Prior third-party material remains owned by its respective authors. This version is the ONLY version authorized for new OTS and guarded Arweave preservation.\n'''
 (HERE/'citation.bib').write_text(bib,encoding='utf8')
 (HERE/'README-LICENSE.txt').write_text(license_text,encoding='utf8')
 return {n:(HERE/n).read_bytes() for n in list(EXPECTED)+['citation.bib','README-LICENSE.txt']}

def upload(d):
 if d.get('submitted'):return d
 files=make_files()
 d=delete_inherited(d,files)
 intent=load('upload-intents.json') if (HERE/'upload-intents.json').exists() else {}
 completed=load('upload-status.json') if (HERE/'upload-status.json').exists() else {}
 bucket=d.get('links',{}).get('bucket')
 if not bucket or urllib.parse.urlsplit(bucket).netloc!='zenodo.org':raise RuntimeError('Unsafe/missing Zenodo bucket')
 for n in sorted(files):
  b=files[n]
  latest=names(get('/deposit/depositions/'+str(NEW)))
  if n in latest:
   if not same(latest[n],b):raise RuntimeError('Remote file identity conflict: '+n)
   completed[n]={'bytes':len(b),'sha256':sha(b)}
   save('upload-status.json',completed);persist()
   continue
  if n in intent:
   raise RuntimeError('Ambiguous prior PUT outcome for '+n+'; refuse second transfer')
  intent[n]={'bytes':len(b),'sha256':sha(b),'state':'FILE_TRANSFER_ATTEMPT'}
  save('upload-intents.json',intent);persist()
  try:
   api(bucket.rstrip('/')+'/'+urllib.parse.quote(n),method='PUT',payload=b,binary=True)
  except Exception:
   latest=names(get('/deposit/depositions/'+str(NEW)))
   if n not in latest or not same(latest[n],b):raise
  latest=names(get('/deposit/depositions/'+str(NEW)))
  if n not in latest or not same(latest[n],b):raise RuntimeError('Unverified upload: '+n)
  completed[n]={'bytes':len(b),'sha256':sha(b)}
  save('upload-status.json',completed);persist()
 final=names(get('/deposit/depositions/'+str(NEW)))
 if set(final)!=set(files) or any(not same(final[n],files[n]) for n in files):
  raise RuntimeError('New record has unexpected file list or differing bytes')
 save('publication-checks.json',{'state':'ALL_EXACT_DRAFT_FILES_READBACK','record_id':NEW,'doi':DOI,
  'files':[{'name':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(files.items())]})
 persist()
 return get('/deposit/depositions/'+str(NEW))

def public_bytes(name):
 u=f'https://zenodo.org/records/{NEW}/files/{urllib.parse.quote(name)}?download=1'
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'MGTD-v101-anonymous-readback/1.0'}),timeout=110) as response:
  b=response.read(MAX_FILE+1)
 if len(b)>MAX_FILE:raise RuntimeError('Public file too large')
 return b

def public_verify(d,files):
 public=get(f'/records/{NEW}',auth=False)
 if public.get('id')!=NEW or public.get('doi')!=DOI:raise RuntimeError('Public DOI record mismatch')
 m=public.get('metadata') or {}
 if str(m.get('version'))!=VERSION or m.get('title')!=TITLE:
  raise RuntimeError('Wrong publicly published version metadata')
 for n,b in sorted(files.items()):
  if public_bytes(n)!=b:raise RuntimeError('Public file readback different bytes: '+n)
 return {'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','report_number':REPORT,'version':VERSION,
  'title':TITLE,'record_id':NEW,'doi':DOI,'previous_doi':OLD_DOI,
  'conceptrecid':CONCEPT,'submitted':True,'peer_reviewed':False,'public_file_readback_pass':True,
  'files':[{'name':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(files.items())]}

def publish():
 verify_local()
 d=validate_draft(get('/deposit/depositions/'+str(NEW)))
 if (HERE/'publication-record.json').exists():
  previous=load('publication-record.json')
  if previous.get('doi')!=DOI or previous.get('state')!='PUBLISHED_AND_PUBLIC_READBACK_PASS':
   raise RuntimeError('Existing public result mismatch')
  print('ALREADY_PUBLISHED',DOI);return
 files=make_files()
 if not d.get('submitted'):
  d=update_metadata(d)
  d=upload(d)
  if not (HERE/'publication-intent.json').exists():
   save('publication-intent.json',{'state':'ONE_TIME_PUBLISH_INTENT','record_id':NEW,
      'doi':DOI,'previous_doi':OLD_DOI,'files':load('publication-checks.json')['files']})
   persist()
   try:api(f'/deposit/depositions/{NEW}/actions/publish',method='POST')
   except Exception as exc:
    save('publication-error.json',{'state':'PUBLISH_RESPONSE_UNCERTAIN','exception':type(exc).__name__})
    persist()
    d=validate_draft(get('/deposit/depositions/'+str(NEW)))
    if not d.get('submitted'):raise RuntimeError('Uncertain publish; no repeat POST') from exc
  d=validate_draft(get('/deposit/depositions/'+str(NEW)))
  if not d.get('submitted'):raise RuntimeError('Previous intent not published; no duplicate publish')
 rec=public_verify(d,files)
 save('publication-record.json',rec);persist()
 print('MGTD_V101_PUBLISHED',DOI,'previous',OLD_DOI)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=('verify','publish','persist'));args=ap.parse_args()
 {'verify':verify_local,'publish':publish,'persist':persist}[args.action]()
