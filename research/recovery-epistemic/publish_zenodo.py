#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,time,urllib.parse,urllib.request
from pathlib import Path
RID=22809019
DOI='10.5281/zenodo.22809019'
TITLE='Recovery without Epistemic Monopoly: Historical Evidence under Competing AI Custodians—A Bounded Model and Executable Study'
REPORT='TA-TR-2026-05'

def check_url(url):
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password: raise RuntimeError('Unexpected Zenodo host')
 return url
class Zenodo:
 def __init__(self,token): self.token=token
 def request(self,path,method='GET',data=None,authenticated=True,binary=False):
  url=check_url(path if path.startswith('https://') else 'https://zenodo.org/api'+path); h={}
  if authenticated:h['Authorization']='Bearer '+self.token
  if data is not None and not binary:h['Content-Type']='application/json';data=json.dumps(data).encode()
  elif binary:h['Content-Type']='application/octet-stream'
  q=urllib.request.Request(url,data=data,headers=h,method=method)
  with urllib.request.urlopen(q,timeout=180) as r:return json.loads(r.read())
 def download(self,url):
  with urllib.request.urlopen(check_url(url),timeout=180) as r:return r.read()

def main():
 pub=Path(os.environ['PUB_DIR']); receipt=Path(os.environ['RECEIPT'])
 files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in pub.iterdir() if p.is_file()}
 expected={'README-LICENSE.txt','SHA256SUMS.txt','recovery-without-epistemic-monopoly-v1.0.md','recovery-without-epistemic-monopoly-v1.0.pdf','recovery-without-epistemic-monopoly-zh-v1.0.md','recovery-without-epistemic-monopoly-zh-v1.0.pdf','citation.bib','citation.csl.json','citation.ris','research-supplement-v1.0.zip'}
 if set(files)!=expected: raise RuntimeError('Unexpected publication files: '+str(sorted(files)))
 token=os.environ.get('ZENODO_ACCESS_TOKEN')
 if not token: raise RuntimeError('Publication credential unavailable')
 z=Zenodo(token); dep=z.request(f'/deposit/depositions/{RID}'); md=dep['metadata']
 if dep['id']!=RID or md.get('title')!=TITLE or md.get('version')!='1.0': raise RuntimeError('Draft identity mismatch')
 if not any(c.get('name')=='Liu, Hongju' for c in md.get('creators',[])): raise RuntimeError('Creator mismatch')
 already=bool(dep.get('submitted'))
 if not already:
  if md.get('prereserve_doi',{}).get('doi')!=DOI: raise RuntimeError('Reserved DOI mismatch')
  description='<p>TA-TR-2026-05. A bounded conceptual and executable study of historical evidence recovery when AI-mediated custodians may be untrusted or in conflict. English full text and complete Chinese translation describe one study.</p><p><strong>Methods and limits.</strong> The deposit includes deterministic finite-state studies and reproducibility material. It does not report real autonomous-agent attack rates, production penetration testing, or a demonstrated defense against superintelligence. A conventional pinned-reference baseline ties the proposed scoped reporting layer on byte recovery; the negative result is retained.</p><p><strong>Contribution and responsibility.</strong> Hongju Liu initiated the motivating concern, selected the civilizational relevance and authorized this publication. GPT-6 Astra Pro substantially performed literature synthesis, conceptual development, implementation, execution analysis, bilingual drafting and file preparation. Not peer reviewed; no separate final human line-by-line verification is claimed. No OpenAI, Harvard, Zenodo or institutional endorsement is implied.</p><p><strong>Rights.</strong> CC BY 4.0 applies to newly written text and supporting code to the extent rights are held. Referenced third-party materials retain their own rights.</p>'
  metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],'description':description,'publication_date':'2026-09-17','version':'1.0','access_right':'open','license':'cc-by-4.0','language':'eng','keywords':['digital preservation','archival provenance','adversarial recovery','AI agents','historical evidence','authorization','control domains','civilizational memory'],'notes':'TA-TR-2026-05. Separate fifth preprint; English and Chinese are one study. Deterministic bounded experiments, not real-model attacks. No earlier DOI, Bitcoin Original, or institutional preservation dataset is modified. Google Scholar indexing is not asserted.','related_identifiers':[{'identifier':d,'relation':'references','scheme':'doi'} for d in ('10.5281/zenodo.21699878','10.5281/zenodo.21900592','10.5281/zenodo.22761411','10.5281/zenodo.22804542')]}
  dep=z.request(f'/deposit/depositions/{RID}','PUT',{'metadata':metadata})
  old=dep.get('files',[])
  if any(f.get('filename',f.get('key')) not in expected for f in old): raise RuntimeError('Unexpected pre-existing draft file')
  bucket=check_url(dep['links']['bucket'])
  if not urllib.parse.urlsplit(bucket).path.startswith('/api/files/'): raise RuntimeError('Unexpected bucket route')
  for name in sorted(expected): z.request(bucket+'/'+urllib.parse.quote(name,safe=''),'PUT',(pub/name).read_bytes(),binary=True)
  listing=z.request(f'/deposit/depositions/{RID}/files')
  if {f.get('filename',f.get('key')) for f in listing}!=expected: raise RuntimeError('Draft file set mismatch')
  for f in listing:
   n=f.get('filename',f.get('key'))
   if f.get('checksum','').removeprefix('md5:')!=hashlib.md5((pub/n).read_bytes()).hexdigest(): raise RuntimeError('Draft checksum mismatch '+n)
  out=z.request(f'/deposit/depositions/{RID}/actions/publish','POST')
  if not out.get('submitted'): raise RuntimeError('Publish failed')
 public=None
 for i in range(8):
  try: public=z.request(f'/records/{RID}',authenticated=False); break
  except Exception:
   if i==7: raise
   time.sleep(5)
 if public['id']!=RID or public.get('doi')!=DOI or public.get('metadata',{}).get('title')!=TITLE or public.get('metadata',{}).get('version')!='1.0': raise RuntimeError('Public identity mismatch')
 if {f['key'] for f in public['files']}!=expected: raise RuntimeError('Public file list mismatch')
 rows=[]
 for f in public['files']:
  b=z.download(f['links']['self']); n=f['key']; h=hashlib.sha256(b).hexdigest(); e=files[n]
  if len(b)!=e['bytes'] or h!=e['sha256']: raise RuntimeError('Public byte mismatch '+n)
  rows.append({'name':n,'bytes':len(b),'sha256':h,'matches_local':True})
 r={'schema':'trinityaccord.research-publication.v1','status':'PUBLISHED_AND_PUBLIC_READBACK_PASS','record_id':RID,'doi':DOI,'record_url':f'https://zenodo.org/records/{RID}','title':TITLE,'report_number':REPORT,'version':'1.0','publication_date':'2026-09-17','public_record_created':public.get('created'),'public_record_modified':public.get('modified'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'publication_source_commit':os.environ.get('GITHUB_SHA'),'was_already_published':already,'file_count':len(rows),'files':sorted(rows,key=lambda x:x['name']),'prior_records_modified':False,'bitcoin_originals_modified':False,'peer_reviewed':False,'google_scholar_indexing_status':'NOT_ASSERTED','separate_final_human_line_by_line_review_claimed':False}
 receipt.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(r,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
