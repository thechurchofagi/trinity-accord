#!/usr/bin/env python3
"""Publish only the already-reserved TA-TR-2026-07 record after explicit review."""
from __future__ import annotations
import hashlib,html,importlib.util,json,os,subprocess,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RID=22840604; DOI='10.5281/zenodo.22840604'
TITLE='Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence'
PROTECTED={21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629}
PHASE='local_gate'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def load(name):return json.loads((ROOT/name).read_text())
def check_identity(dep):
    md=dep.get('metadata',{})
    if dep.get('id')!=RID or RID in PROTECTED or md.get('title')!=TITLE or md.get('version')!='1.0':raise RuntimeError('Seventh-paper record identity mismatch')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']:raise RuntimeError('Creator identity mismatch')
    if (dep.get('doi') or md.get('prereserve_doi',{}).get('doi') or md.get('doi'))!=DOI:raise RuntimeError('Unexpected DOI')
def safe_public_download(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password:raise RuntimeError('Untrusted public file URL')
    request=urllib.request.Request(url,headers={'User-Agent':'TrinityAccord-TA07-PublicReadback/1.0'})
    with urllib.request.urlopen(request,timeout=120) as response:
        if urllib.parse.urlsplit(response.url).hostname!='zenodo.org':raise RuntimeError('Unexpected public redirect')
        data=response.read(5*1024*1024+1)
        if len(data)>5*1024*1024:raise RuntimeError('Unexpected publication asset size')
        return data

def run():
    global PHASE
    expected=load('EXPECTED-PUBLICATION.json');review=load('visual-review.json');formats=load('format-checks.json')
    if (expected.get('record_id'),expected.get('doi'),expected.get('title'),expected.get('version'),expected.get('file_count'))!=(RID,DOI,TITLE,'1.0',12):raise RuntimeError('Local publication identity mismatch')
    manifest_sha=sha((ROOT/'EXPECTED-PUBLICATION.json').read_bytes())
    if review.get('state')!='VISUAL_AND_CONTENT_REVIEW_PASS' or review.get('expected_manifest_sha256')!=manifest_sha:raise RuntimeError('Exact current package has no explicit completed review')
    if not formats.get('independent_rebuild_same_bytes') or not formats.get('reference_lists_identical'):raise RuntimeError('Build gate not passed')
    files=expected['files'];names={f['name'] for f in files}
    if len(files)!=12 or len(names)!=12 or {p.name for p in (ROOT/'published').iterdir()}!=names:raise RuntimeError('Unexpected local file inventory')
    for f in files:
        p=ROOT/'published'/f['name'];b=p.read_bytes()
        if p.name!=f['name'] or p.name.endswith(('.ttf','.otf','.ttc')) or len(b)!=f['bytes'] or sha(b)!=f['sha256']:raise RuntimeError('Unreviewed local bytes: '+f['name'])
    old=ROOT.parent/'reading-trinity-accord'/'publish_zenodo.py';b=old.read_bytes()
    if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!='a0cbc84cc5fd826c06d16456c4adbaa40dabc788':raise RuntimeError('Established client has changed')
    spec=importlib.util.spec_from_file_location('verified_zenodo_client',old);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('Publication credential unavailable')
    z=m.Zenodo(token)
    def read(path,authenticated=True):
        error=None
        for delay in (0,3,8,15):
            if delay:time.sleep(delay)
            try:return z.request(path,authenticated=authenticated)
            except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
                error=e
                if isinstance(e,urllib.error.HTTPError) and e.code not in (404,408,429,500,502,503,504):raise
        raise error
    PHASE='read_reserved_record'
    dep=read('/deposit/depositions/'+str(RID));check_identity(dep)
    if not dep.get('submitted'):
        PHASE='update_seventh_record_metadata'
        en=(ROOT/'published'/'recoverability-and-shared-time-v1.0.md').read_text()
        abstract=en.split('## Abstract\n\n',1)[1].split('\n\n**Keywords:',1)[0]
        description='<p>'+html.escape(abstract)+'</p><p>TA-TR-2026-07, version 1.0. English full text and complete Chinese translation are one philosophical study. Twelve assets include both PDFs, Markdown and HTML full texts, citation formats, a source/review note, license and checksums. Not peer reviewed; no empirical safety efficacy, present AI consciousness, exhaustive originality certification or Google Scholar indexing is asserted.</p><p>Human author of record and responsible depositor: Hongju Liu. Substantial literature research, conceptual development, thought experiments, critical revision, drafting, translation and package preparation: GPT-6 Astra Pro under human direction. No separate final human line-by-line review is claimed. First-party relationship to the Trinity Accord is disclosed. This is non-amending research, not the six-paper editorial supplement and not a new Bitcoin Original.</p>'
        md={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],'description':description,'publication_date':'2026-09-19','version':'1.0','access_right':'open','license':'cc-by-4.0','language':'eng','keywords':['AI suspension','recoverability','participation','shared time','AI ethics','human-AI coexistence','moral uncertainty'],'related_identifiers':[{'identifier':'10.5281/zenodo.22804542','relation':'references','scheme':'doi'},{'identifier':'10.5281/zenodo.22830239','relation':'references','scheme':'doi'}]}
        dep=z.request('/deposit/depositions/'+str(RID),'PUT',{'metadata':md});check_identity(dep)
        PHASE='upload_reviewed_files'
        listing=read('/deposit/depositions/'+str(RID)+'/files')
        if not isinstance(listing,list):raise RuntimeError('Unexpected draft-file response')
        remote={f['filename']:f for f in listing}
        if set(remote)-names:raise RuntimeError('Unrelated files on seventh draft; do not delete automatically')
        bucket=m.check_url(dep['links']['bucket'])
        if not urllib.parse.urlsplit(bucket).path.startswith('/api/files/'):raise RuntimeError('Unexpected upload bucket')
        for f in files:
            b=(ROOT/'published'/f['name']).read_bytes();md5=hashlib.md5(b).hexdigest();previous=remote.get(f['name'])
            checksum=str(previous.get('checksum','')).removeprefix('md5:') if previous else ''
            if previous and checksum==md5 and previous.get('filesize')==len(b):continue
            z.request(bucket+'/'+urllib.parse.quote(f['name'],safe=''),'PUT',b,binary=True)
        listing=read('/deposit/depositions/'+str(RID)+'/files');remote={f['filename']:f for f in listing}
        if set(remote)!=names:raise RuntimeError('Draft file inventory differs')
        for f in files:
            b=(ROOT/'published'/f['name']).read_bytes();r=remote[f['name']]
            if str(r.get('checksum','')).removeprefix('md5:')!=hashlib.md5(b).hexdigest() or r.get('filesize')!=len(b):raise RuntimeError('Draft bytes not verified: '+f['name'])
        PHASE='publish_existing_record'
        save('publication-attempt.json',{'state':'PUBLICATION_INTENT_FOR_EXISTING_RECORD','record_id':RID,'doi':DOI,'expected_manifest_sha256':manifest_sha,'new_record_creation':False})
        result=z.request('/deposit/depositions/'+str(RID)+'/actions/publish','POST')
        check_identity(result)
        if not result.get('submitted'):raise RuntimeError('Publish response is not submitted')
    PHASE='anonymous_public_metadata_readback'
    public=read('/records/'+str(RID),authenticated=False)
    if public.get('id')!=RID or public.get('doi')!=DOI or public.get('metadata',{}).get('title')!=TITLE or public.get('metadata',{}).get('version')!='1.0':raise RuntimeError('Public record identity differs')
    remote={f['key']:f for f in public.get('files',[])}
    if set(remote)!=names:raise RuntimeError('Public inventory mismatch')
    PHASE='anonymous_full_file_readback'
    readback=Path('/tmp/ta07-public-readback');readback.mkdir(parents=True,exist_ok=True)
    rows=[]
    for f in files:
        r=remote[f['name']];url=r['links'].get('self') or r['links'].get('download')
        b=safe_public_download(url)
        if len(b)!=f['bytes'] or sha(b)!=f['sha256']:raise RuntimeError('Public exact-byte mismatch '+f['name'])
        (readback/f['name']).write_bytes(b);rows.append(dict(f,public_url=url))
    PHASE='doi_resolver_check'
    resolver={}
    try:
        req=urllib.request.Request('https://doi.org/'+DOI,headers={'User-Agent':'TrinityAccord-TA07-DOICheck/1.0'})
        with urllib.request.urlopen(req,timeout=30) as response:
            resolver={'http_status':response.status,'final_url':response.url,'matches_record':urllib.parse.urlsplit(response.url).hostname=='zenodo.org' and str(RID) in urllib.parse.urlsplit(response.url).path}
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:resolver={'state':'RESOLVER_CHECK_UNAVAILABLE','error':str(e)}
    receipt={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','report_number':'TA-TR-2026-07','title':TITLE,'version':'1.0','record_id':RID,'doi':DOI,'record_url':'https://zenodo.org/records/'+str(RID),'submitted':True,'file_count':len(rows),'files':rows,'expected_manifest_sha256':manifest_sha,'public_readback_authenticated':False,'doi_resolver':resolver,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'prior_doi_records_modified':False,'bitcoin_originals_modified':False,'new_research_papers':1,'peer_reviewed':False,'global_originality_certified':False,'google_scholar_indexing':'NOT_ASSERTED'}
    save('publication-record.json',receipt);save('publication-attempt.json',{'state':receipt['state'],'record_id':RID,'doi':DOI,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:run()
    except Exception as e:
        save('publication-attempt.json',{'state':'INCOMPLETE_REQUIRES_REVIEW_OR_SAME_RECORD_RESUMPTION','record_id':RID,'doi':DOI,'phase':PHASE,'error_type':type(e).__name__,'error':str(e),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'new_record_creation':False})
        raise
