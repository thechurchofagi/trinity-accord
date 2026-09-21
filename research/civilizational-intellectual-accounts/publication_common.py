"""Shared, narrowly scoped publication checks for TA-TR-2026-13."""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, subprocess, time
import urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = 'research/civilizational-intellectual-accounts-v1-0-20260921'
TITLE = 'Civilizational Intellectual Production Satellite Accounts: A Partial-Identification Framework for Measuring the Human–AI Shift in Intellectual Production and Epistemic Governance'
REPORT = 'TA-TR-2026-13'
VERSION = '1.0'
DATE = '2026-09-21'
PROTECTED = {21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629,22840604,22842789,22844927,22844928,22846307,22852884,22852885,22854705,22865494,22866205}
CLIENT_BLOB = 'a0cbc84cc5fd826c06d16456c4adbaa40dabc788'
STEM = 'civilizational-intellectual-production-accounts'
ALLOWED_FILES = {f'{STEM}-zh-v{VERSION}.{ext}' for ext in ('pdf','md')} | {
    'ta13_civilizational_intellectual_accounts_simulations.py',
    'ta13_civilizational_intellectual_accounts_results.json',
    'REPRODUCIBILITY.md','citation.bib','citation.ris','citation.csl.json',
    'REVIEW-AND-SOURCES.md','README-LICENSE.txt','SHA256SUMS.txt'
}
STATE_FILES = {'create-intent.json','deposit.json','preparation-attempt.json','publication-attempt.json','publication-record.json'}
MAX_FILE_BYTES = 12 * 1024 * 1024
FORMAT_GATES = (
    'source_markdown_preserved','references_preserved','chinese_full_text_with_english_abstract',
    'direct_prior_art_boundaries_preserved','valid_citation_metadata','pdf_text_extractable',
    'design_simulations_preserved','reproducibility_record_preserved'
)

def sha(data): return hashlib.sha256(data).hexdigest()
def load(name, root=ROOT): return json.loads((root/name).read_text(encoding='utf-8'))
def save(name, value, root=ROOT):
    if name not in STATE_FILES: raise RuntimeError('Unexpected publication state filename')
    root.mkdir(parents=True, exist_ok=True)
    target=root/name; tmp=target.with_suffix(target.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(target)

def persist_states(names):
    if not set(names) <= STATE_FILES: raise RuntimeError('Unexpected receipt path')
    allowed={str((ROOT/n).relative_to(REPO)) for n in names}
    paths=[p for p in sorted(allowed) if (REPO/p).exists()]
    if not paths: return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','--',*paths],cwd=REPO,check=True)
    staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).splitlines()
    if not set(staged) <= allowed: raise RuntimeError('Unexpected staged path; no receipt commit')
    if staged:
        subprocess.run(['git','commit','-m','research: preserve TA13 publication state [skip ci]'],cwd=REPO,check=True)
        subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

def client():
    old=ROOT.parent/'reading-trinity-accord'/'publish_zenodo.py'
    data=old.read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual != CLIENT_BLOB: raise RuntimeError('Established Zenodo client changed')
    spec=importlib.util.spec_from_file_location('ta_verified_zenodo_client',old)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token: raise RuntimeError('Publication credential unavailable')
    return module.Zenodo(token)

def read(z,path,authenticated=True):
    for attempt,delay in enumerate((0,3,8,15)):
        if delay: time.sleep(delay)
        try: return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as error:
            if isinstance(error,urllib.error.HTTPError) and error.code not in (404,408,429,500,502,503,504): raise
            if attempt==3: raise

def validate_record_id(record_id):
    if type(record_id) is not int or record_id<=0 or record_id in PROTECTED:
        raise RuntimeError('Invalid or protected prior record ID')
    return record_id

def validate_identity(value):
    rid=validate_record_id(value.get('record_id'))
    wanted=(TITLE,REPORT,VERSION,f'10.5281/zenodo.{rid}')
    found=(value.get('title'),value.get('report_number'),value.get('version'),value.get('doi'))
    if found != wanted: raise RuntimeError('TA13 local identity mismatch')
    return rid

def check_deposit(deposit,identity=None):
    rid=validate_record_id(deposit.get('id'))
    md=deposit.get('metadata',{})
    if (md.get('title'),md.get('version')) != (TITLE,VERSION): raise RuntimeError('Reserved record title/version mismatch')
    if [c.get('name') for c in md.get('creators',[])] != ['Liu, Hongju']: raise RuntimeError('Reserved record creator mismatch')
    doi=deposit.get('doi') or md.get('prereserve_doi',{}).get('doi') or md.get('doi')
    if doi != f'10.5281/zenodo.{rid}': raise RuntimeError('Reserved DOI mismatch')
    if identity is not None and (rid,doi)!=(identity['record_id'],identity['doi']):
        raise RuntimeError('Reserved record does not match reviewed package')
    return rid,doi

def select_existing(rows):
    if not isinstance(rows,list) or len(rows)>=100: raise RuntimeError('Unbounded or unexpected draft search; no creation')
    matching=[r for r in rows if r.get('metadata',{}).get('title')==TITLE]
    if len(matching)>1: raise RuntimeError('Ambiguous matching records; no creation')
    return matching[0] if matching else None

def validate_local_package(root=ROOT):
    raw=(root/'EXPECTED-PUBLICATION.json').read_bytes(); expected=json.loads(raw)
    validate_identity(expected)
    dep=load('deposit.json',root); validate_identity(dep)
    if (expected['record_id'],expected['doi']) != (dep['record_id'],dep['doi']): raise RuntimeError('Expected package differs from reservation')
    review=load('visual-review.json',root); digest=sha(raw)
    if review.get('state')!='CONTENT_AND_RENDER_PIPELINE_REVIEW_PASS' or review.get('expected_manifest_sha256')!=digest:
        raise RuntimeError('Exact current package has no completed review')
    checks=load('format-checks.json',root)
    for f in FORMAT_GATES:
        if checks.get(f) is not True: raise RuntimeError('Required format/source gate missing: '+f)
    rows=expected.get('files',[]); names={x.get('name') for x in rows}
    if expected.get('file_count')!=len(ALLOWED_FILES) or len(rows)!=len(ALLOWED_FILES) or names!=ALLOWED_FILES:
        raise RuntimeError('Reviewed inventory differs from exact allowed inventory')
    pub=root/'published'
    if pub.is_symlink() or {p.name for p in pub.iterdir()}!=names: raise RuntimeError('Unexpected published-directory inventory')
    for item in rows:
        p=pub/item['name']
        if p.is_symlink() or not p.is_file(): raise RuntimeError('Only regular publication files are permitted')
        b=p.read_bytes()
        if not 0<len(b)<=MAX_FILE_BYTES or len(b)!=item['bytes'] or sha(b)!=item['sha256']:
            raise RuntimeError('Unreviewed publication bytes: '+item['name'])
    return expected,digest

def extract_abstract(markdown):
    m=re.search(r'(?m)^#{2,3}\s+Abstract\s*$',markdown)
    if not m: raise RuntimeError('English abstract heading missing')
    rest=markdown[m.end():]
    k=re.search(r'(?im)^\s*(?:\*\*)?Keywords\s*:',rest)
    if not k: raise RuntimeError('English abstract keyword boundary missing')
    abstract=rest[:k.start()].strip()
    if not abstract or len(abstract)>7000 or re.search(r'(?m)^#{1,6}\s',abstract): raise RuntimeError('Ambiguous English abstract')
    return abstract

def check_public_url(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or p.port not in (None,443):
        raise RuntimeError('Unexpected public file host')
    if p.query or p.fragment: raise RuntimeError('Unexpected public file URL parameters')
    return url

class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,message,headers,new_url):
        check_public_url(new_url)
        return super().redirect_request(request,fp,code,message,headers,new_url)

def download_public(url):
    req=urllib.request.Request(check_public_url(url),headers={'User-Agent':'TrinityAccord-TA13-PublicReadback/1.0'})
    with urllib.request.build_opener(SameHostRedirect()).open(req,timeout=120) as response:
        check_public_url(response.url); data=response.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES: raise RuntimeError('Unexpected public asset size')
    return data

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--persist-states',action='store_true'); args=p.parse_args()
    if args.persist_states: persist_states(STATE_FILES)
