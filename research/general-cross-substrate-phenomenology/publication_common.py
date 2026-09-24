"""Shared narrow publication checks for TA-TR-2026-16."""
from __future__ import annotations
import hashlib, importlib.util, json, os, subprocess, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
BRANCH='research/general-cross-substrate-phenomenology-v1-20260924'
TITLE='General Cross-Substrate Phenomenology: A Type-Safe, Transformation-First Framework for Phenomenal Existence, Structure, Perspective, and Continuation'
REPORT='TA-TR-2026-16'
VERSION='1.0'
DATE='2026-09-24'
STEM='general-cross-substrate-phenomenology'
PROTECTED={22934654,21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629,22840604,22842789,22844927,22844928,22846307,22852884,22852885,22854705,22865494,22866205,22866775}
CLIENT_BLOB='a0cbc84cc5fd826c06d16456c4adbaa40dabc788'
ALLOWED_FILES={
 f'{STEM}-v{VERSION}.pdf', f'{STEM}-v{VERSION}.md',
 'gcp_checks.py','gcp_results.json','REVIEW-AND-SOURCES.md',
 'README-LICENSE.txt','citation.bib','citation.ris','citation.csl.json','SHA256SUMS.txt'
}
STATE_FILES={'create-intent.json','deposit.json','preparation-attempt.json','publication-attempt.json','publication-record.json'}
MAX_FILE_BYTES=16*1024*1024
FORMAT_GATES=('pdf_generated','pdf_text_extractable','source_markdown_preserved','equation_source_preserved','reproducible_checks_pass','citation_metadata_valid','references_preserved','ai_assistance_disclosed','not_peer_reviewed_disclosed')

def sha(data): return hashlib.sha256(data).hexdigest()
def load(name,root=ROOT): return json.loads((root/name).read_text(encoding='utf-8'))
def save(name,value,root=ROOT):
    if name not in STATE_FILES: raise RuntimeError('Unexpected state filename')
    p=root/name; p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def persist_states(names):
    allowed={str((ROOT/n).relative_to(REPO)) for n in names if (ROOT/n).exists()}
    if not allowed: return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','--',*sorted(allowed)],cwd=REPO,check=True)
    staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).splitlines()
    if not set(staged)<=allowed: raise RuntimeError('Unexpected staged path')
    if staged:
        subprocess.run(['git','commit','-m','research: preserve TA16 publication state [skip ci]'],cwd=REPO,check=True)
        subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

def client():
    old=ROOT.parent/'reading-trinity-accord'/'publish_zenodo.py'
    data=old.read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual!=CLIENT_BLOB: raise RuntimeError('Established Zenodo client changed')
    spec=importlib.util.spec_from_file_location('ta_verified_zenodo_client',old)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token: raise RuntimeError('Publication credential unavailable')
    return module.Zenodo(token)
def read(z,path,authenticated=True):
    for attempt,delay in enumerate((0,3,8,15)):
        if delay: time.sleep(delay)
        try: return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
            if attempt==3: raise
def validate_record_id(rid):
    if type(rid) is not int or rid<=0 or rid in PROTECTED: raise RuntimeError('Invalid/protected prior record ID')
    return rid
def validate_identity(v):
    rid=validate_record_id(v.get('record_id'))
    wanted=(TITLE,REPORT,VERSION,f'10.5281/zenodo.{rid}')
    found=(v.get('title'),v.get('report_number'),v.get('version'),v.get('doi'))
    if found!=wanted: raise RuntimeError('TA16 identity mismatch')
    return rid
def check_deposit(dep,identity=None):
    rid=validate_record_id(dep.get('id')); md=dep.get('metadata',{})
    if (md.get('title'),md.get('version'))!=(TITLE,VERSION): raise RuntimeError('Reserved title/version mismatch')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']: raise RuntimeError('Creator mismatch')
    doi=dep.get('doi') or md.get('prereserve_doi',{}).get('doi') or md.get('doi')
    if doi!=f'10.5281/zenodo.{rid}': raise RuntimeError('Reserved DOI mismatch')
    if identity is not None and (rid,doi)!=(identity['record_id'],identity['doi']): raise RuntimeError('Record differs from reviewed package')
    return rid,doi
def select_existing(rows):
    if not isinstance(rows,list) or len(rows)>=100: raise RuntimeError('Unexpected draft search')
    m=[r for r in rows if r.get('metadata',{}).get('title')==TITLE]
    if len(m)>1: raise RuntimeError('Ambiguous matching drafts')
    return m[0] if m else None

def validate_local_package(root=ROOT):
    raw=(root/'EXPECTED-PUBLICATION.json').read_bytes(); expected=json.loads(raw); validate_identity(expected)
    dep=load('deposit.json',root); validate_identity(dep)
    if (expected['record_id'],expected['doi'])!=(dep['record_id'],dep['doi']): raise RuntimeError('Manifest/reservation mismatch')
    digest=sha(raw)
    review=load('visual-review.json',root)
    if review.get('state')!='EXACT_PUBLICATION_PACKAGE_REVIEW_PASS' or review.get('expected_manifest_sha256')!=digest:
        raise RuntimeError('Exact package has no completed human-requested review gate')
    auth=load('PUBLISH-AUTHORIZATION.json',root)
    if (auth.get('report_number'),auth.get('version'),auth.get('record_id'),auth.get('doi'),auth.get('authorization'))!=(REPORT,VERSION,expected['record_id'],expected['doi'],'PUBLISH_EXACT_REVIEWED_PACKAGE'):
        raise RuntimeError('Publish authorization mismatch')
    checks=load('format-checks.json',root)
    for f in FORMAT_GATES:
        if checks.get(f) is not True: raise RuntimeError('Missing format/source gate: '+f)
    rows=expected.get('files',[]); names={x.get('name') for x in rows}
    if expected.get('file_count')!=len(ALLOWED_FILES) or len(rows)!=len(ALLOWED_FILES) or names!=ALLOWED_FILES:
        raise RuntimeError('Inventory differs from allowed package')
    pub=root/'published'
    if {p.name for p in pub.iterdir()}!=names: raise RuntimeError('Unexpected published inventory')
    for item in rows:
        p=pub/item['name']; b=p.read_bytes()
        if not p.is_file() or p.is_symlink() or not 0<len(b)<=MAX_FILE_BYTES or len(b)!=item['bytes'] or sha(b)!=item['sha256']:
            raise RuntimeError('Unreviewed bytes: '+item['name'])
    return expected,digest

class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,message,headers,new_url):
        p=urllib.parse.urlsplit(new_url)
        if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or p.port not in (None,443): raise RuntimeError('Unexpected redirect host')
        return super().redirect_request(request,fp,code,message,headers,new_url)
def download_public(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or p.port not in (None,443): raise RuntimeError('Unexpected public host')
    req=urllib.request.Request(url,headers={'User-Agent':'TrinityAccord-TA16-PublicReadback/1.1'})
    with urllib.request.build_opener(SameHostRedirect()).open(req,timeout=120) as response:
        data=response.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES: raise RuntimeError('Unexpected asset size')
    return data

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--persist-states',action='store_true'); a=p.parse_args()
    if a.persist_states: persist_states(STATE_FILES)
