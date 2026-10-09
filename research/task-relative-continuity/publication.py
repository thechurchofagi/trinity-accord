#!/usr/bin/env python3
"""RT20261009 exact version publication: reserve DOI, embed DOI in Markdown/PDF, publish, public readback.

One-way state machine with durable create/publish intent and frozen hashes.
No automatic replay after an uncertain POST or paid operations. CI only for token-bearing actions.
"""
from __future__ import annotations
import argparse, hashlib, html, json, os, pathlib, re, shutil, subprocess, tempfile, time, urllib.error, urllib.parse, urllib.request, uuid, zipfile

HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[1]
BRANCH='research/rt-paper-v1-0-0-20261009'
REPORT='RT20261009'
TITLE='Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout'
VERSION='1.0.0'
DATE='2026-10-09'
SOURCE='source-main.md'
PDF='Task_Relative_Continuity_v1.0.0.pdf'
MD='Task_Relative_Continuity_v1.0.0.md'
REPRO='RT_TH_Reproducibility_v1.0.0.zip'
INPUTS={SOURCE:('52f879101be072efd0651a512b03bac27e3dbf5a80facf55aa726b7515f88ed4',37089),
REPRO:('83c0050bfdddff7ac94cf716db107e6f63ef09d9d6b04cd74ead0be4adcb860b',108986)}
MAX_FILE=16*1024*1024
EXPECTED_FILES={PDF,MD,REPRO,'README-LICENSE.txt','REVIEW-AND-SOURCES.md','citation.bib','citation.ris','citation.csl.json','SHA256SUMS.txt'}
STATE_FILES=['create-intent.json','deposit.json','create-uncertain.json','publish-intent.json','publish-uncertain.json','publication-record.json','EXPECTED-PUBLICATION.json','publication-error.json','format-checks.json','published']
USER_AGENT='RT-TH-Zenodo-Publication/1.0'


def sha(data):return hashlib.sha256(data).hexdigest()
def load(p):return json.loads((HERE/p).read_text(encoding='utf-8'))
def save(p,obj):
 dst=HERE/p;tmp=dst.with_name(dst.name+'.tmp')
 tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8');tmp.replace(dst)

def verify_source():
 for name,(digest,length) in INPUTS.items():
  data=(HERE/name).read_bytes()
  if (sha(data),len(data))!=(digest,length):raise RuntimeError('Frozen source mismatch: '+name)
 with zipfile.ZipFile(HERE/REPRO) as z:
  if z.testzip():raise RuntimeError('Repro archive CRC failure')
 text=(HERE/SOURCE).read_text(encoding='utf-8')
 for phrase in ['theoretical preprint','not peer reviewed','The contribution is a task-sensitive theoretical synthesis', 'Grover', 'UCT-MAP-v1.1.0']:
  if phrase.lower() not in text.lower():raise RuntimeError('Source content/academic limits changed: '+phrase)
 if '__DOI_' in text:raise RuntimeError('Source must be pre-DOI frozen, no accidental placeholder')
 print('FROZEN_INPUTS_PASS', INPUTS)
 return text

def ensure_ci():
 if os.environ.get('GITHUB_ACTIONS')!='true' or not os.environ.get('ZENODO_ACCESS_TOKEN'):
  raise RuntimeError('Credential-bearing actions require GitHub Actions with ZENODO_ACCESS_TOKEN')

def persist():
 if os.environ.get('GITHUB_ACTIONS')!='true':return
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
 if branch!=BRANCH:raise RuntimeError('Cannot persist outside exact research branch '+branch)
 paths=[str((HERE/name).relative_to(REPO)) for name in STATE_FILES if (HERE/name).exists()]
 if not paths:return
 subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
 subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
 subprocess.run(['git','add','--',*paths],cwd=REPO,check=True)
 if not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():return
 subprocess.run(['git','diff','--cached','--check'],cwd=REPO,check=True)
 subprocess.run(['git','commit','-m','[skip ci] Preserve RT20261009 exact DOI publication checkpoint'],cwd=REPO,check=True)
 # Do not rebase/replay a workflow after potentially irreversible remote POST.
 subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self, req, fp, code, msg, headers, newurl):
  raise RuntimeError('Never forward publication credential through redirects')

def api(path, method='GET', payload=None, authorized=True, binary=False):
 url=(path if path.startswith('https://') else 'https://zenodo.org/api'+path)
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or p.port not in (None,443) or p.fragment:
  raise RuntimeError('Zenodo host validation failed')
 headers={'User-Agent':USER_AGENT,'Accept':'application/json'}
 if authorized:headers['Authorization']='Bearer '+os.environ['ZENODO_ACCESS_TOKEN']
 if payload is None:data=None
 elif binary:data=payload;headers['Content-Type']='application/octet-stream'
 else:data=json.dumps(payload).encode();headers['Content-Type']='application/json'
 request=urllib.request.Request(url,data=data,headers=headers,method=method)
 with urllib.request.build_opener(NoRedirect()).open(request, timeout=120) as response:
  raw=response.read(MAX_FILE+1)
 if len(raw)>MAX_FILE:raise RuntimeError('Zenodo response exceeds bound')
 return json.loads(raw)

def read(path,authorized=True):
 for attempt in range(3):
  try:return api(path,authorized=authorized)
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
   if attempt==2:raise
   time.sleep(3*(attempt+1))

def identity_record():
 sourcehash=INPUTS[SOURCE][0]
 return f'{REPORT}; v{VERSION}; source-sha256={sourcehash}; create-once'

def metadata(source):
 abstract=source.split('## Abstract {-}',1)[1].split('**Keywords:**',1)[0].strip()
 return {'upload_type':'publication','publication_type':'preprint','title':TITLE,
         'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
         'description':'<p>'+html.escape(abstract)+'</p><p>Open-access non-peer-reviewed theoretical preprint. Substantial ChatGPT assistance under the human author\'s direction is disclosed. Finite checks are not empirical validation of consciousness.</p>',
         'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
         'keywords':['task-relative continuity','representational change','readout','group invariance','calibration','relational memory','structural theories of experience'],
         'notes':identity_record()+'; DOI, OTS and Arweave do not certify novelty, truth or peer review.',
         'related_identifiers':[{'identifier':d,'relation':'references','scheme':'doi'} for d in ('10.5281/zenodo.23131575','10.5281/zenodo.23137088','10.5281/zenodo.23002980','10.5281/zenodo.23241982')]}

def validate_deposit(dep):
 rid=dep.get('id'); md=dep.get('metadata') or {}
 if type(rid) is not int or rid<=0 or (md.get('title'),str(md.get('version')))!=(TITLE,VERSION):
  raise RuntimeError('Unexpected Zenodo deposition identity')
 if identity_record() not in md.get('notes',''):raise RuntimeError('New deposition identity token missing')
 doi=dep.get('doi') or md.get('prereserve_doi',{}).get('doi') or md.get('doi')
 if doi and doi!=f'10.5281/zenodo.{rid}':raise RuntimeError('DOI/record collision')
 return rid, doi or f'10.5281/zenodo.{rid}'

def search_existing():
 matches=[]
 for page in range(1,12):
  rows=read(f'/deposit/depositions?page={page}&size=100')
  if not isinstance(rows,list):raise RuntimeError('Zenodo list shape unexpected')
  for row in rows:
   md=row.get('metadata') or {}
   if md.get('title')==TITLE and str(md.get('version'))==VERSION:
    if identity_record() not in md.get('notes',''):raise RuntimeError('Different prior paper collides with title/version')
    matches.append(row)
  if len(rows)<100:break
 if len(matches)>1:raise RuntimeError('Multiple matching Zenodo depositions, human reconcile first')
 return matches[0] if matches else None

def obtain_draft(md):
 if (HERE/'deposit.json').exists():
  stored=load('deposit.json');remote=read('/deposit/depositions/'+str(stored['record_id']))
  rid,doi=validate_deposit(remote)
  if (rid,doi)!=(stored['record_id'],stored['doi']):raise RuntimeError('Saved DOI changed')
  return remote
 found=search_existing()
 if found:
  rid,doi=validate_deposit(found)
  save('deposit.json',{'record_id':rid,'doi':doi,'state':'REUSED_IDENTICAL_DRAFT'});persist()
  return found
 if (HERE/'create-intent.json').exists():raise RuntimeError('Earlier create POST uncertain; refuse second POST')
 intent={'state':'CREATE_ONCE_INTENT','identity':identity_record(),'request_id':str(uuid.uuid4())}
 save('create-intent.json',intent);persist()
 try:
  dep=api('/deposit/depositions',method='POST',payload={'metadata':md})
 except Exception as exc:
  save('create-uncertain.json',{'state':'CREATE_UNKNOWN','reason_class':type(exc).__name__});persist();raise
 rid,doi=validate_deposit(dep)
 save('deposit.json',{'record_id':rid,'doi':doi,'state':'RESERVED_DRAFT'});persist()
 return dep

def patched_source(source, doi):
 if not re.fullmatch(r'10\.5281/zenodo\.\d+',doi):raise RuntimeError('Cannot inject unverified DOI')
 token='\\texttt{RT-TH-PAPER-v1.0.0} / Research record \\texttt{RT20261009}\\\\'
 if source.count(token)!=1:raise RuntimeError('Title page injection anchor mismatch')
 source=source.replace(token,token+'\n'+r'\textbf{Zenodo DOI:} \texttt{'+doi+r'}\\'+'\n',1)
 old=('**Version and publication identity.** This manuscript is version 1.0.0 of the standalone RT/TH theoretical preprint. Its manuscript identifier is separate from research-result and map-release identifiers. Publication-service identifiers and preservation attestations, when issued, are recorded in accompanying metadata; no DOI or blockchain verification is asserted merely by this text. Completed scientific versions are not silently overwritten.')
 new=(f'**Version and publication identity.** This is version 1.0.0 of the standalone RT/TH theoretical preprint, published as Zenodo DOI [{doi}](https://doi.org/{doi}). The scientific manuscript identity is separate from research-result and map-release identifiers. Zenodo publication does not imply peer review, mathematical truth, experimental validation, OTS Bitcoin confirmation, or Arweave archival completion. Completed scientific versions are not silently overwritten.')
 if source.count(old)!=1:raise RuntimeError('Publication status replacement anchor mismatch')
 source=source.replace(old,new,1)
 if source.count(doi)!=3:raise RuntimeError('Issued DOI must appear exactly once in title plus linked declaration')
 return source

def package_files(doi):
 pub=HERE/'published';expected_path=HERE/'EXPECTED-PUBLICATION.json'
 if expected_path.exists():
  expected=load('EXPECTED-PUBLICATION.json');verify_package(expected,doi)
  return expected
 if pub.exists() and any(pub.iterdir()):raise RuntimeError('Unmanifested existing files; do not overwrite')
 pub.mkdir()
 source=verify_source()
 (pub/MD).write_text(patched_source(source,doi),encoding='utf-8')
 with tempfile.TemporaryDirectory() as tmp:
  temp_pdf=pathlib.Path(tmp)/PDF
  subprocess.run(['pandoc',str(pub/MD),'-o',str(temp_pdf),'--pdf-engine=xelatex','--from=markdown+tex_math_single_backslash'],cwd=HERE,check=True)
  shutil.copyfile(temp_pdf,pub/PDF)
 shutil.copyfile(HERE/REPRO,pub/REPRO)
 shutil.copyfile(HERE/'REVIEW-AND-SOURCES.md',pub/'REVIEW-AND-SOURCES.md')
 (pub/'README-LICENSE.txt').write_text(f'{REPORT} / v{VERSION} / {DATE}\n{TITLE}\nPublished DOI: {doi}\n\nHuman author: Hongju Liu. Substantial ChatGPT assistance was used for literature comparison, finite computations, manuscript preparation and publication under human direction. This is a theoretical preprint without independent peer review. Original material CC BY 4.0 to the extent rights are held; third-party references retain their own rights. The supplementary original reproducibility ZIP preserves reviewed source/history and is not itself reauthored after DOI allocation. The main PDF and accompanying Markdown embed the reserved DOI. DOI, OTS and Arweave signify identity and provenance, not scientific truth.\n',encoding='utf-8')
 (pub/'citation.bib').write_text(f'@misc{{Liu2026RTTH,\n author = {{Liu, Hongju}},\n title = {{{TITLE}}},\n year = {{2026}},\n version = {{{VERSION}}},\n doi = {{{doi}}},\n url = {{https://doi.org/{doi}}},\n note = {{Open-access theoretical preprint; not peer reviewed}}\n}}\n',encoding='utf-8')
 (pub/'citation.ris').write_text(f'TY  - JOUR\nAU  - Liu, Hongju\nTI  - {TITLE}\nPY  - 2026\nDA  - {DATE}\nVL  - {VERSION}\nDO  - {doi}\nUR  - https://doi.org/{doi}\nN1  - Theoretical preprint; not peer reviewed\nER  -\n',encoding='utf-8')
 (pub/'citation.csl.json').write_text(json.dumps({'id':doi,'type':'article','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,10,9]]},'version':VERSION,'DOI':doi,'URL':'https://doi.org/'+doi,'note':'Theoretical preprint; not peer reviewed'},indent=2)+'\n',encoding='utf-8')
 names=sorted(EXPECTED_FILES-{'SHA256SUMS.txt'})
 (pub/'SHA256SUMS.txt').write_text('\n'.join(sha((pub/n).read_bytes())+'  '+n for n in names)+'\n',encoding='utf-8')
 files=[{'name':n,'bytes':(pub/n).stat().st_size,'sha256':sha((pub/n).read_bytes())} for n in sorted(EXPECTED_FILES)]
 info=subprocess.check_output(['pdfinfo',str(pub/PDF)],text=True)
 pages=[x.strip() for x in info.splitlines() if x.startswith('Pages:')]
 if not pages or int(pages[0].split(':',1)[1].strip())<9:raise RuntimeError('PDF page count invalid')
 extracted=subprocess.check_output(['pdftotext',str(pub/PDF),'-'],text=True)
 if doi not in extracted or len(extracted)<12000:raise RuntimeError('Issued DOI missing from searchable PDF text')
 save('format-checks.json',{'state':'PDF_FORMAT_PASS','pages':int(pages[0].split(':',1)[1]),'doi_embedded_and_searchable':True,'new_publication_id':doi,'proof_boundary':'Literature and computations remain author-side, not peer-reviewed'})
 expected={'report_number':REPORT,'doi':doi,'record_id':int(doi.rsplit('.',1)[-1]),'version':VERSION,'title':TITLE,'file_count':len(files),'files':files,'prior_records_modified':False,'source_sha256':INPUTS[SOURCE][0]}
 save('EXPECTED-PUBLICATION.json',expected);verify_package(expected,doi);persist()
 print('DOI_EMBEDDED_PDF_BUILT',doi,'PDF_SHA256',next(x['sha256'] for x in files if x['name']==PDF))
 return expected

def verify_package(expected,doi):
 pub=HERE/'published'
 if (expected.get('doi'),expected.get('version'))!=(doi,VERSION):raise RuntimeError('Expected package identity changed')
 if {x['name'] for x in expected['files']}!=EXPECTED_FILES:raise RuntimeError('Unexpected public file inventory')
 for row in expected['files']:
  p=pub/row['name']
  if not p.exists() or (len(p.read_bytes()),sha(p.read_bytes()))!=(row['bytes'],row['sha256']):raise RuntimeError('Frozen package file mismatch: '+str(p))
 if doi not in (pub/MD).read_text():raise RuntimeError('DOI missing in Markdown')

def remote_files(dep):
 return {x.get('filename') or x.get('key'):x for x in dep.get('files',[])}
def equals_remote(x,data):
 value='md5:'+hashlib.md5(data).hexdigest();got=x.get('checksum') or x.get('checksum_md5')
 return got in (value,value[4:]) and x.get('filesize',x.get('size'))==len(data)

def upload_all(dep,expected):
 rid,doi=validate_deposit(dep)
 if dep.get('submitted'):return dep
 if (HERE/'publish-intent.json').exists():raise RuntimeError('Prior publish intent exists; no further upload')
 bucket=dep.get('links',{}).get('bucket')
 p=urllib.parse.urlsplit(bucket or '')
 if p.scheme!='https' or p.hostname!='zenodo.org':raise RuntimeError('Invalid Zenodo bucket')
 for item in expected['files']:
  name=item['name']; data=(HERE/'published'/name).read_bytes()
  refreshed=read('/deposit/depositions/'+str(rid)); existing=remote_files(refreshed).get(name)
  if existing:
   if not equals_remote(existing,data):raise RuntimeError('Remote same-name file differs: '+name)
   continue
  try:uploaded=api(bucket+'/'+urllib.parse.quote(name),method='PUT',payload=data,binary=True)
  except Exception as exc:
   check=remote_files(read('/deposit/depositions/'+str(rid))).get(name)
   if not check or not equals_remote(check,data):
    save('publication-error.json',{'stage':'UPLOAD_UNKNOWN','file':name,'class':type(exc).__name__});persist();raise RuntimeError('Uncertain file upload; manual reconciliation required') from exc
  else:
   if not equals_remote(uploaded,data):
    check=remote_files(read('/deposit/depositions/'+str(rid))).get(name)
    if not check or not equals_remote(check,data):raise RuntimeError('Zenodo file mismatch after PUT: '+name)
 checked=remote_files(read('/deposit/depositions/'+str(rid)))
 if set(checked)!=EXPECTED_FILES or any(not equals_remote(checked[x['name']],(HERE/'published'/x['name']).read_bytes()) for x in expected['files']):
  raise RuntimeError('Draft publication files incomplete')
 return read('/deposit/depositions/'+str(rid))

def download_public(rid,name):
 url=f'https://zenodo.org/records/{rid}/files/{urllib.parse.quote(name)}?download=1'
 req=urllib.request.Request(url,headers={'User-Agent':'RT-TH-Public-Readback/1.0'})
 with urllib.request.urlopen(req,timeout=100) as response:raw=response.read(MAX_FILE+1)
 if len(raw)>MAX_FILE:raise RuntimeError('Public file above safe size')
 return raw

def public_verify(dep,expected):
 rid,doi=validate_deposit(dep)
 try: pub=read('/records/'+str(rid),authorized=False)
 except Exception as exc:raise RuntimeError('Public Zenodo API readback unavailable') from exc
 if pub.get('id')!=rid or pub.get('doi')!=doi:raise RuntimeError('Anonymous DOI identity mismatch')
 for item in expected['files']:
  b=download_public(rid,item['name'])
  if (len(b),sha(b))!=(item['bytes'],item['sha256']):raise RuntimeError('Published byte readback failed: '+item['name'])
 return {'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','record_id':rid,'doi':doi,'version':VERSION,'report_number':REPORT,'title':TITLE,'files':expected['files'],'submitted':True,'public_file_readback_pass':True,'publication_type':'preprint','peer_reviewed':False}

def publish():
 source=verify_source();ensure_ci();dep=obtain_draft(metadata(source));rid,doi=validate_deposit(dep)
 expected=package_files(doi)
 if (HERE/'publication-record.json').exists():
  old=load('publication-record.json')
  if old.get('doi')!=doi:raise RuntimeError('Publication-record DOI changed')
  print('Already published and recorded',doi);return
 if not dep.get('submitted'):
  dep=upload_all(dep,expected)
  if not (HERE/'publish-intent.json').exists():
   save('publish-intent.json',{'state':'PUBLISH_ONCE_INTENT','doi':doi,'record_id':rid,'published_files_sha256':{x['name']:x['sha256'] for x in expected['files']}})
   persist()
   try: dep=api('/deposit/depositions/'+str(rid)+'/actions/publish',method='POST')
   except Exception as exc:
    save('publish-uncertain.json',{'state':'PUBLISH_UNKNOWN','class':type(exc).__name__});persist()
    dep=read('/deposit/depositions/'+str(rid))
    if not dep.get('submitted'):raise RuntimeError('Publish POST uncertain, no retry') from exc
  else:
   dep=read('/deposit/depositions/'+str(rid))
   if not dep.get('submitted'):raise RuntimeError('Previous publish intent pending, no replay')
 dep=read('/deposit/depositions/'+str(rid))
 if not dep.get('submitted'):raise RuntimeError('Zenodo publication not confirmed')
 rec=public_verify(dep,expected);save('publication-record.json',rec);persist()
 print('RT_PUBLICATION_SUCCESS',doi,'PDF_SHA256',next(x['sha256'] for x in rec['files'] if x['name']==PDF))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['verify','publish','persist','preview']);p.add_argument('--sample-doi',default='10.5281/zenodo.99999999');a=p.parse_args()
 if a.action=='verify':verify_source()
 elif a.action=='publish':publish()
 elif a.action=='persist':persist()
 else:
  verify_source();print('preview source chars',len(patched_source((HERE/SOURCE).read_text(),a.sample_doi)))
