#!/usr/bin/env python3
"""Single paper Zenodo create-once and exact-byte public-readback publisher.
Run only in pinned Actions branch. External POSTs require durable intent and are not retried blindly.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, subprocess, urllib.request, urllib.parse, urllib.error, html, time, zipfile
HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[1]
BRANCH='research/rt-th-paper-v1-20261009'
VERSION='1.0.0'
TITLE='Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout'
SOURCE='source-main.md'; SUPP='RT_TH_Reproducibility_v1.0.0.zip'
PDF='Task_Relative_Continuity_v1.0.0.pdf'; MD='Task_Relative_Continuity_v1.0.0.md'
SOURCE_SHA='52f879101be072efd0651a512b03bac27e3dbf5a80facf55aa726b7515f88ed4'
SUPP_SHA='83c0050bfdddff7ac94cf716db107e6f63ef09d9d6b04cd74ead0be4adcb860b'
IDENTITY='RT-TH-PAPER-v1.0.0; frozen-source-sha256='+SOURCE_SHA

def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((HERE/n).read_text())
def save(n,obj):
 p=HERE/n; tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');tmp.replace(p)
def cmd(xs):subprocess.run(xs,cwd=REPO,check=True)
def persist():
 if os.getenv('GITHUB_ACTIONS')!='true':raise RuntimeError('GitHub Actions only')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
 if branch!=BRANCH:raise RuntimeError('Wrong branch '+branch)
 names=['create-intent.json','deposit.json','preparation-error.json','draft-adoption.json','publication-intent.json','publish-attempt.json','publication-record.json','upload-check.json','published','build-qa.json','citation.bib','README-LICENSE.txt']
 items=[str((HERE/n).relative_to(REPO)) for n in names if (HERE/n).exists()]
 if not items:return
 cmd(['git','config','user.name','github-actions[bot]']);cmd(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com']);cmd(['git','add','--',*items])
 if not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():return
 cmd(['git','commit','-m','[skip ci] Preserve RT/TH DOI publication checkpoints'])
 cmd(['git','push','origin','HEAD:'+BRANCH])
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*_):raise RuntimeError('Zenodo redirect denied with credential')
def api(path,method='GET',data=None,binary=False,authorized=True):
 url=path if path.startswith('https://') else 'https://zenodo.org/api'+path
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or p.hostname!='zenodo.org' or p.port not in (None,443):raise RuntimeError('Invalid API host')
 headers={'User-Agent':'RTTH-Preprint/1.0'}
 if authorized:
  token=os.getenv('ZENODO_ACCESS_TOKEN')
  if not token:raise RuntimeError('Missing secret')
  headers['Authorization']='Bearer '+token
 if data is not None:
  if not binary:data=json.dumps(data).encode()
  headers['Content-Type']='application/octet-stream' if binary else 'application/json'
 req=urllib.request.Request(url,headers=headers,data=data,method=method)
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=110) as res:
  raw=res.read(10_000_000)
 return json.loads(raw)
def get(path,authorized=True):
 for a in range(3):
  try:return api(path,authorized=authorized)
  except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError):
   if a==2:raise
   time.sleep(3*(a+1))
def verify_source():
 if sha((HERE/SOURCE).read_bytes())!=SOURCE_SHA:raise RuntimeError('Source mutation')
 if sha((HERE/SUPP).read_bytes())!=SUPP_SHA:raise RuntimeError('Supplement mutation')
 with zipfile.ZipFile(HERE/SUPP) as z:
  if z.testzip():raise RuntimeError('Invalid original supplementary ZIP')
 if 'not peer reviewed' not in (HERE/SOURCE).read_text().lower():raise RuntimeError('Missing scientific boundary')
def metadata():
 abstract=(HERE/SOURCE).read_text().split('## Abstract {-}',1)[1].split('**Keywords:**',1)[0].strip()
 return {'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
 'description':'<p>'+html.escape(abstract)+'</p><p>Preprint, not peer reviewed. Substantial ChatGPT assistance was used under human direction. Formal/finite counterexamples are not empirical validation of consciousness.</p>',
 'publication_date':'2026-10-09','version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
 'keywords':['representational continuity','invariance','information recovery','structural theory of experience','thought experiments'],
 'notes':IDENTITY+'; independent non-amending theoretical preprint; no claim of originality for known algebra.',
 'related_identifiers':[{'identifier':x,'relation':'references','scheme':'doi'} for x in ['10.5281/zenodo.23131575','10.5281/zenodo.23137088','10.5281/zenodo.23002980','10.5281/zenodo.23241982']]}
def validate(obj):
 rid=obj.get('id');m=obj.get('metadata') or {}
 if not isinstance(rid,int) or rid<=0 or m.get('title')!=TITLE or str(m.get('version'))!=VERSION or IDENTITY not in m.get('notes',''):raise RuntimeError('Zenodo identity collision')
 doi=obj.get('doi') or m.get('prereserve_doi',{}).get('doi') or m.get('doi') or f'10.5281/zenodo.{rid}'
 if doi!=f'10.5281/zenodo.{rid}':raise RuntimeError('DOI mismatch')
 return rid,doi
def find_existing():
 matches=[]
 for page in range(1,8):
  rows=get(f'/deposit/depositions?page={page}&size=100')
  for row in rows:
   m=row.get('metadata',{})
   if m.get('title')==TITLE and str(m.get('version'))==VERSION:
    if IDENTITY not in m.get('notes',''):
     names=[v.get('name') for v in m.get('creators',[])]
     expected_prefix='RT-TH-PAPER-v1.0.0; source-sha256='
     if row.get('id')!=23251651 or row.get('submitted') or row.get('files') or names!=['Liu, Hongju'] or not m.get('notes','').startswith(expected_prefix):
      raise RuntimeError('Nonempty/published/unrelated Zenodo identity collision')
     # A draft with no files has not yet bound a public PDF. Record explicit replacement.
     save('draft-adoption.json',{'record_id':23251651,'prior_note':m.get('notes'),'new_identity':IDENTITY,'state':'IDENTICAL_AUTHOR_EMPTY_DRAFT_ADOPTION_INTENT'})
     persist()
     api('/deposit/depositions/23251651',method='PUT',data={'metadata':metadata()})
     row=get('/deposit/depositions/23251651')
    validate(row);matches.append(row)
  if len(rows)<100:break
 if len(matches)>1:raise RuntimeError('Multiple matching Zenodo deposits')
 return matches[0] if matches else None
def reserve():
 verify_source()
 if (HERE/'deposit.json').exists():
  r=read('deposit.json');d=get('/deposit/depositions/'+str(r['record_id']));validate(d);return d
 matched=find_existing()
 if matched:pass
 elif (HERE/'create-intent.json').exists():raise RuntimeError('Uncertain previous POST; no repeated create')
 else:
  save('create-intent.json',{'identity':IDENTITY,'state':'CREATE_ONCE_INTENT'});persist()
  try:matched=api('/deposit/depositions',method='POST',data={'metadata':metadata()})
  except Exception as e:
   save('preparation-error.json',{'error':type(e).__name__,'state':'UNCERTAIN_CREATE'});persist();raise
 rid,doi=validate(matched)
 save('deposit.json',{'record_id':rid,'doi':doi,'state':'RESERVED','identity':IDENTITY});persist()
 return matched
def build(doi):
 src=(HERE/SOURCE).read_text();location=src.index('## Abstract {-}')
 # Preserve all scholarly content; only the preprint's metadata block and declaration are updated.
 src=src[:location]+f'**DOI:** [{doi}](https://doi.org/{doi})\\\n\n'+src[location:]
 old='Publication-service identifiers and preservation attestations, when issued, are recorded in accompanying metadata; no DOI or blockchain verification is asserted merely by this text.'
 if old not in src:raise RuntimeError('Publication-status wording not found')
 src=src.replace(old,f'This published preprint has Zenodo DOI {doi}; OTS and Arweave completion must be separately verified from their later receipts.')
 pub=HERE/'published';pub.mkdir(exist_ok=True)
 (pub/MD).write_text(src)
 cmd(['pandoc',str(pub/MD),'-o',str(pub/PDF),'--pdf-engine=xelatex','--from=markdown+tex_math_single_backslash'])
 text=subprocess.check_output(['pdftotext',str(pub/PDF),'-'],cwd=REPO,text=True)
 if doi not in text or len(text)<6000:raise RuntimeError('DOI not embedded or PDF extraction inadequate')
 citation=f'@misc{{Liu2026RTTH,\n author = {{Liu, Hongju}},\n title = {{{TITLE}}},\n year = {{2026}},\n version = {{{VERSION}}},\n doi = {{{doi}}},\n url = {{https://doi.org/{doi}}},\n note = {{Theoretical preprint, not peer reviewed}}\n}}\n'
 license_note=f'{TITLE}\nAuthor: Hongju Liu\nDOI: {doi}\nTheoretical preprint, not peer reviewed; substantial AI assistance under human direction. CC BY 4.0 for original work to the extent rights are held. Existing cited works remain under their rights. Timestamping does not validate claims.\n'
 (pub/'citation.bib').write_text(citation)
 (pub/'README-LICENSE.txt').write_text(license_note)
 import shutil
 shutil.copyfile(HERE/SUPP,pub/SUPP)
 files=sorted(pub.iterdir()); manifest={p.name:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in files}
 save('build-qa.json',{'doi':doi,'files':manifest,'pdf_doi_in_text':True,'source_unchanged':True});persist()
 return files

def uploaded_info(rec):
 return {x.get('filename') or x.get('key'):x for x in rec.get('files',[])}
def present(x,data):
 import hashlib
 return x and x.get('checksum') in ('md5:'+hashlib.md5(data).hexdigest(),hashlib.md5(data).hexdigest()) and x.get('filesize',x.get('size'))==len(data)
def upload(rec,files):
 rid,doi=validate(rec);bucket=rec.get('links',{}).get('bucket')
 if urllib.parse.urlsplit(bucket or '').hostname!='zenodo.org':raise RuntimeError('Bucket host invalid')
 for p in files:
  data=p.read_bytes();existing=uploaded_info(get('/deposit/depositions/'+str(rid))).get(p.name)
  if existing:
   if not present(existing,data):raise RuntimeError('Remote name/hash collision '+p.name)
   continue
  x=api(bucket+'/'+urllib.parse.quote(p.name),method='PUT',data=data,binary=True)
  if not present(x,data):
   check=uploaded_info(get('/deposit/depositions/'+str(rid))).get(p.name)
   if not present(check,data):raise RuntimeError('Upload readback mismatch '+p.name)
 rows=uploaded_info(get('/deposit/depositions/'+str(rid)))
 if set(rows)!=set(p.name for p in files) or any(not present(rows.get(p.name),p.read_bytes()) for p in files):raise RuntimeError('Draft inventory incomplete')
 save('upload-check.json',{'record_id':rid,'doi':doi,'files':{p.name:sha(p.read_bytes()) for p in files},'state':'ALL_DRAFT_FILES_VERIFIED'});persist()

def final_readback(rid,doi,files):
 rec=get('/records/'+str(rid),authorized=False)
 if rec.get('id')!=rid or rec.get('doi')!=doi:raise RuntimeError('Public record mismatch')
 for p in files:
  url=f'https://zenodo.org/records/{rid}/files/{urllib.parse.quote(p.name)}?download=1'
  with urllib.request.urlopen(url,timeout=90) as resp:data=resp.read(15_000_000)
  if sha(data)!=sha(p.read_bytes()):raise RuntimeError('Public bytes mismatch: '+p.name)
 return {'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','submitted':True,'public_file_readback_pass':True,'report_number':'RT-TH-2026-01','record_id':rid,'doi':doi,'version':VERSION,'title':TITLE,'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files]}
def publish():
 verify_source()
 if not os.getenv('ZENODO_ACCESS_TOKEN') or os.getenv('GITHUB_ACTIONS')!='true':raise RuntimeError('Zenodo secret on Actions required')
 rec=reserve();rid,doi=validate(rec);files=build(doi)
 if (HERE/'publication-record.json').exists():
  existing=read('publication-record.json')
  if existing.get('doi')!=doi:raise RuntimeError('Record mismatch')
  print('Already published',doi);return
 rec=get('/deposit/depositions/'+str(rid))
 if not rec.get('submitted'):
  upload(rec,files)
  if not (HERE/'publication-intent.json').exists():
   save('publication-intent.json',{'record_id':rid,'doi':doi,'state':'PUBLISH_ONCE_INTENT'});persist()
   try:api('/deposit/depositions/'+str(rid)+'/actions/publish',method='POST')
   except Exception as e:
    save('publish-attempt.json',{'state':'UNCERTAIN_POST','error':type(e).__name__});persist()
    if not get('/deposit/depositions/'+str(rid)).get('submitted'):raise RuntimeError('Uncertain publish; do not repeat')
  elif not get('/deposit/depositions/'+str(rid)).get('submitted'):raise RuntimeError('Earlier publish intent not completed; no replay')
 if not get('/deposit/depositions/'+str(rid)).get('submitted'):raise RuntimeError('Not yet published')
 receipt=final_readback(rid,doi,files);save('publication-record.json',receipt);persist();print('PUBLISHED',doi)
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('action',choices=['publish','verify']);args=a.parse_args()
 if args.action=='verify':verify_source();print('SOURCE_VERIFIED')
 else:publish()
