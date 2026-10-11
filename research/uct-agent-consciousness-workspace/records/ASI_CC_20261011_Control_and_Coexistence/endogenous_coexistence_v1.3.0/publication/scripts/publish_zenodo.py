#!/usr/bin/env python3
"""RAC13/ASI-CC-v1.3.0: verified one-shot Zenodo preprint publication.

Direct adaptation of repository's successful PR-v6.0.0 Zenodo workflow.
Immutable source assets; exact author/version search including drafts; recover by
record ID after uncertain network errors; strict public readback. No private
credentials printed or recorded; no OTS/Arweave operation in this job.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,time,zipfile
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlencode,quote

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'release'
FREEZE=ROOT/'EXPECTED-PUBLICATION.json'
AUTH=ROOT/'PUBLISH-AUTHORIZATION.json'
ATTEMPT=ROOT/'PUBLICATION-ATTEMPT.json'
RECEIPT=ROOT/'PUBLICATION-RECEIPT.json'
API='https://zenodo.org/api'

def h(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def jread(p:Path):return json.loads(p.read_text(encoding='utf-8'))
def jwrite(p:Path,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()

def verify():
 f=jread(FREEZE);a=jread(AUTH)
 assert f['schema']=='rac13-freeze/1' and f['paper_id']=='ASI-CC-v1.3.0'
 assert a['schema']=='rac13-publication-authorization/1'
 assert a['status']=='AUTHORIZED_FOR_ONE_PUBLIC_ZENODO_PREPRINT'
 assert a['paper_id']==f['paper_id']
 assert a['manifest_sha256']==h(FREEZE.read_bytes()),'Auth manifest hash does not match frozen assets'
 assert a['owner_instruction']=='Publish ASI-CC-v1.3.0 following the repository established paper publication workflow'
 meta=f['metadata']
 assert meta['title']==f['title'] and meta['version']=='1.3.0'
 assert meta['upload_type']=='publication' and meta['publication_type']=='preprint'
 assert meta['creators']==[{'name':'Liu, Hongju','affiliation':'Independent Researcher, Shenzhen, China'}]
 assert meta['license']=='cc-by-4.0' and meta['access_right']=='open'
 declared={x['name'] for x in f['files']}
 assert declared and len(declared)==len(f['files'])==f['file_count']
 assert declared=={x.name for x in ASSETS.iterdir() if x.is_file()},'Unexpected/missing release file'
 for obj in f['files']:
  p=ASSETS/obj['name']; b=p.read_bytes()
  assert len(b)==obj['bytes'] and h(b)==obj['sha256'],('Asset integrity failed',p)
 assert h((ASSETS/'when-revocation-does-not-restore-safety-v1.3.0.pdf').read_bytes())==f['source_pdf_sha256']
 assert h((ASSETS/'reproducibility-v1.3.0.zip').read_bytes())==f['source_reproducibility_sha256']
 with zipfile.ZipFile(ASSETS/'reproducibility-v1.3.0.zip') as z:
  assert z.testzip() is None and 'ASI-CC-v1.3.0/INDEX.json' in z.namelist()
 pdfinfo=subprocess.run(['pdfinfo',str(ASSETS/'when-revocation-does-not-restore-safety-v1.3.0.pdf')],capture_output=True,text=True,check=True).stdout
 assert any(line.startswith('Pages:') and line.split()[-1]=='12' for line in pdfinfo.splitlines())
 return f

def api(session,method,path,**kwargs):
 r=session.request(method,API+path,timeout=kwargs.pop('timeout',60),**kwargs)
 if r.status_code>=400:
  raise RuntimeError(f'Zenodo {method} {path} HTTP {r.status_code}: {r.text[:400]}')
 return r.json() if r.content else {}

def public_duplicates(title,version):
 import requests
 r=api(requests.Session(),'GET','/records?'+urlencode({'q':'title:"'+title+'"','size':25}))
 return [o for o in (r.get('hits') or {}).get('hits',[]) if o.get('metadata',{}).get('title')==title and str(o.get('metadata',{}).get('version',''))==version]

def own_exact(session,title,version):
 r=api(session,'GET','/deposit/depositions?'+urlencode({'q':'"'+title+'"','size':100}))
 if not isinstance(r,list):raise RuntimeError('Owner deposition listing incomplete or unexpected format')
 matches=[x for x in r if x.get('metadata',{}).get('title')==title and str(x.get('metadata',{}).get('version',''))==version]
 if len(matches)>1:raise RuntimeError('More than one exact titled draft/published deposition; manual reconciliation required')
 return matches

def check_deposit_metadata(dep,freeze):
 d=dep.get('metadata') or {};wanted=freeze['metadata']
 for k in ('title','version','upload_type','publication_type'):
  if d.get(k)!=wanted[k]:raise RuntimeError(f'Unexpected owner deposit metadata: {k}')
 creators=d.get('creators') or []
 if len(creators)!=1 or creators[0].get('name')!=wanted['creators'][0]['name']:
  raise RuntimeError('Owner creator mismatch in recovered deposit')

def upload_all(session,dep,freeze,attempt):
 did=dep['id']; bucket=(dep.get('links') or {}).get('bucket')
 if not isinstance(bucket,str) or not bucket.startswith(API+'/'):
  raise RuntimeError('Deposit missing recognized Zenodo bucket URL')
 existing=api(session,'GET',f'/deposit/depositions/{did}/files')
 byname={x.get('filename'):x for x in existing}
 if len(existing)!=len(byname):raise RuntimeError('Ambiguous duplicate file name in draft')
 expected={x['name'] for x in freeze['files']}
 if not set(byname)<=expected:raise RuntimeError('Unexpected file in owner draft')
 for obj in freeze['files']:
  name=obj['name'];content=(ASSETS/name).read_bytes();md5=hashlib.md5(content).hexdigest()
  if name in byname:
   o=byname[name];chk=str(o.get('checksum') or '').replace('md5:','')
   size=o.get('filesize') or o.get('size')
   if (chk and chk!=md5) or (size is not None and int(size)!=obj['bytes']):
    raise RuntimeError('Existing owner draft bytes mismatch '+name)
   attempt.setdefault('already_valid_files',[]).append(name)
   continue
  with (ASSETS/name).open('rb') as input_file:
   r=session.post(f'{API}/deposit/depositions/{did}/files',data={'name':name},files={'file':(name,input_file)},timeout=180)
  if r.status_code>=400:raise RuntimeError(f'Upload {name} HTTP {r.status_code}: {r.text[:400]}')
  o=r.json();chk=str(o.get('checksum') or '').replace('md5:','')
  if chk and chk!=md5:raise RuntimeError('Uploaded file checksum mismatch '+name)
  attempt.setdefault('uploaded_files',[]).append(name);jwrite(ATTEMPT,attempt)
 files=api(session,'GET',f'/deposit/depositions/{did}/files')
 got={o.get('filename'):o for o in files}
 if set(got)!=expected:raise RuntimeError('Remote file set not exact')
 for x in freeze['files']:
  o=got[x['name']];chk=str(o.get('checksum') or '').replace('md5:','')
  if chk and chk!=hashlib.md5((ASSETS/x['name']).read_bytes()).hexdigest():raise RuntimeError('Remote draft differs '+x['name'])
  size=o.get('filesize') or o.get('size')
  if size is not None and int(size)!=x['bytes']:raise RuntimeError('Wrong remote file size '+x['name'])

def verify_public(did,freeze):
 import requests
 s=requests.Session();data=None
 for i in range(8):
  try:
   r=s.get(f'{API}/records/{did}',timeout=35)
   if r.status_code==200:data=r.json();break
  except requests.RequestException:pass
  time.sleep(min(2+i,8))
 if not data:raise RuntimeError('Zenodo record not publicly accessible')
 doi=data.get('doi') or data.get('metadata',{}).get('doi')
 if str(data.get('id'))!=str(did) or doi!=f'10.5281/zenodo.{did}' or data['metadata']['title']!=freeze['title']:
  raise RuntimeError('Published DOI or title does not match frozen record')
 if str(data['metadata'].get('version',''))!='1.3.0':raise RuntimeError('Published version differs')
 got={x.get('key'):x for x in data.get('files',[])}
 if set(got)!={x['name'] for x in freeze['files']}:raise RuntimeError('Published file inventory mismatch')
 files=[]
 for obj in freeze['files']:
  name=obj['name'];link=(got[name].get('links') or {}).get('self')
  if not isinstance(link,str) or not link.startswith('https://zenodo.org/'):
   link=f'{API}/records/{did}/files/{quote(name,safe="")}/content'
  r=s.get(link,timeout=130)
  if r.status_code!=200 or len(r.content)!=obj['bytes'] or h(r.content)!=obj['sha256']:
   raise RuntimeError('Public file readback does not match source: '+name)
  files.append({'name':name,'bytes':len(r.content),'sha256':h(r.content),'url':link})
 return {'doi':doi,'record_id':did,'record_url':f'https://zenodo.org/records/{did}','files':files}

def publish():
 import requests
 freeze=verify();token=os.environ.get('ZENODO_ACCESS_TOKEN')
 if not token:raise RuntimeError('Protected GitHub Action lacks ZENODO_ACCESS_TOKEN; no remote write')
 s=requests.Session();s.headers['Authorization']='Bearer '+token
 attempt={'schema':'rac13-publication-attempt/1','status':'STARTED','paper_id':freeze['paper_id'],'manifest_sha256':h(FREEZE.read_bytes()),'started_at_utc':now(),'run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA')}
 jwrite(ATTEMPT,attempt)
 try:
  title=freeze['title'];version=freeze['metadata']['version']
  own=own_exact(s,title,version)
  if own:
   dep=own[0];check_deposit_metadata(dep,freeze)
   attempt.update({'status':'RECOVERED_EXACT_OWNER_DEPOSIT','record_id':dep['id'],'state':dep.get('state')})
  else:
   if public_duplicates(title,version):raise RuntimeError('Exact same public title and version exists; manual reconcile')
   dep=api(s,'POST','/deposit/depositions',json={'metadata':freeze['metadata']})
   attempt.update({'status':'DRAFT_CREATED','record_id':dep['id'],'state':dep.get('state')})
  jwrite(ATTEMPT,attempt);did=dep['id']
  if dep.get('state')!='done':
   upload_all(s,dep,freeze,attempt)
   attempt['status']='FROZEN_FILES_STAGED';jwrite(ATTEMPT,attempt)
   try:
    dep=api(s,'POST',f'/deposit/depositions/{did}/actions/publish',timeout=120)
   except Exception as ex:
    attempt.update({'status':'PUBLISH_POST_UNCERTAIN','error_type':type(ex).__name__,'error':str(ex)[:500]});jwrite(ATTEMPT,attempt)
    try:check=verify_public(did,freeze)
    except Exception:raise RuntimeError('Ambiguous publish outcome, record_id retained; DO NOT CREATE SECOND DRAFT') from ex
   else:check=verify_public(did,freeze)
  else:check=verify_public(did,freeze)
  receipt={'schema':'rac13-public-readback/1','status':'PUBLISHED_PUBLIC_BYTE_READBACK_PASS','paper_id':freeze['paper_id'],'doi':check['doi'],'record_id':did,'record_url':check['record_url'],'public_files':check['files'],'manifest_sha256':h(FREEZE.read_bytes()),'published_checked_at_utc':now(),'source_commit':os.getenv('GITHUB_SHA'),'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'peer_reviewed':False,'ots':'NOT_PERFORMED_HERE','arweave':'NOT_PERFORMED_HERE'}
  jwrite(RECEIPT,receipt);attempt.update({'status':'PUBLISHED_PUBLIC_BYTE_READBACK_PASS','doi':check['doi']});jwrite(ATTEMPT,attempt)
  print(json.dumps({'status':receipt['status'],'doi':receipt['doi'],'record_url':receipt['record_url'],'public_readback_files':len(receipt['public_files'])},indent=2))
 except Exception as ex:
  attempt.update({'status':'FAILED_OR_UNCERTAIN','error_type':type(ex).__name__,'error':str(ex)[:700],'last_updated':now()});jwrite(ATTEMPT,attempt)
  raise

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['verify','publish']);args=p.parse_args()
 if args.action=='verify':
  f=verify();print('FROZEN PRE-FLIGHT PASS',f['paper_id'],f['file_count'])
 else:publish()
if __name__=='__main__':main()
