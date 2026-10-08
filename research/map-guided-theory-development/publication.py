#!/usr/bin/env python3
"""One-time, fail-closed Zenodo preprint deposit for MGTD v1.0.0.

Uses only the exact author-reviewed PDF, Markdown and reproduction ZIP.
External POST operations are never retried after an uncertain outcome.
All irreversible stages receive a durable GitHub checkpoint first.
"""
from __future__ import annotations
import argparse, hashlib, html, json, os, pathlib, subprocess, sys, time
import urllib.parse, urllib.request, urllib.error

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
BRANCH = 'research/mgtd-method-v1-0-20261008'
REPORT = 'METHOD20261008'
VERSION = '1.0.0'
TITLE = 'Map-Guided Theory Development: A Versioned Protocol for Thought Experiments, Semantic Audits, and Human-AI Research'
PDF = 'MGTD_Method_Paper_v1.0.0.pdf'
MD = 'MGTD_Method_Paper_v1.0.0.md'
ARCHIVE = 'MGTD_Method_Paper_v1.0.0_Complete_Package.zip'
EXPECTED = {
    PDF: ('ba85c0ff9f2bf4be9e0a29c051c2ad83d1eb72b57e0ca2ba827bd17c28dcc310',138256),
    MD: ('cc57e4c750db767b7320b5c2f3f76dd98d7ab4b01db1d69557c2e2c33de53f47',50855),
    ARCHIVE: ('83f1df8fb4fb63a799152a5ef9dcd3e1c8817b82b72fba61ee9f4f12d4500e2a',871653),
}
# The author-side source Markdown SHA is recorded in earlier publication preflight.
# The exact verified PDF and reproduction archive carry primary immutable identity.
IDENTITY = 'MGTD-PAPER-v1.0.0; sha256='+EXPECTED[PDF][0]
MAX_RESPONSE = 8_000_000
MAX_FILE = 16_000_000
PERSIST = ('create-intent.json','deposit.json','create-uncertain.json','upload-check.json',
           'publication-intent.json','publication-record.json','publication-error.json',
           'doi-resolution.json','citation.bib','README-LICENSE.txt')

def sha(x): return hashlib.sha256(x).hexdigest()
def load(filename): return json.loads((HERE/filename).read_text(encoding='utf8'))
def save(filename, obj):
    path=HERE/filename
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    temp.replace(path)

def verify_local():
    for name,(hash_expected,n) in EXPECTED.items():
        p=HERE/name
        data=p.read_bytes()
        if sha(data)!=hash_expected or len(data)!=n:
            raise RuntimeError('Frozen file identity mismatch: '+name)
    if not (HERE/PDF).read_bytes().startswith(b'%PDF-'):
        raise RuntimeError('Primary artifact is not PDF')
    import zipfile
    with zipfile.ZipFile(HERE/ARCHIVE) as z:
        if z.testzip() is not None: raise RuntimeError('Reproducibility ZIP failed integrity')
        if not any(n.endswith('/code/reference_checks.py') for n in z.namelist()):
            raise RuntimeError('Reproduction checks missing')
    source=(HERE/MD).read_text(encoding='utf8')
    required=['Map-Guided Theory Development','not peer reviewed','XScientist','PEARL',
              'The contribution is an explicit, reusable synthesis']
    if not all(x.lower() in source.lower() for x in required):
        raise RuntimeError('Manuscript publication-scope wording changed')
    import zipfile
    with zipfile.ZipFile(HERE/ARCHIVE) as z:
        inner=z.read('MGTD_Method_Paper_v1.0.0/MGTD_Method_Paper_v1.0.0.pdf')
        if sha(inner)!=EXPECTED[PDF][0]: raise RuntimeError('ZIP includes different PDF')
    print('FROZEN_PACKAGE_PASS: PDF, Markdown, ZIP')
    return source


def ensure_ci():
    if os.environ.get('GITHUB_ACTIONS')!='true' or not os.environ.get('ZENODO_ACCESS_TOKEN'):
        raise RuntimeError('GitHub Actions with existing Zenodo publication secret required')

def persist():
    if os.environ.get('GITHUB_ACTIONS')!='true': return
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
    if branch!=BRANCH:
        raise RuntimeError('Refuse preservation outside approved branch: '+branch)
    paths=[str((HERE/name).relative_to(REPO)) for name in PERSIST if (HERE/name).exists()]
    if not paths: return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','--',*paths],cwd=REPO,check=True)
    if not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip(): return
    subprocess.run(['git','commit','-m','[skip ci] Preserve MGTD DOI stage and public receipts'],cwd=REPO,check=True)
    # No automatic rebase of a run with potentially irreversible Zenodo POSTs.
    subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Zenodo API credential must never traverse redirect')

def api(path, method='GET', payload=None, binary=False, authorized=True):
    if path.startswith('https://'):
        url=path
    else:
        url='https://zenodo.org/api'+path
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' or parsed.netloc!='zenodo.org' or parsed.username or parsed.password:
        raise RuntimeError('Zenodo API host mismatch')
    headers={'User-Agent':'MGTD-Verified-Publication/1.0'}
    if authorized: headers['Authorization']='Bearer '+os.environ['ZENODO_ACCESS_TOKEN']
    if payload is None: data=None
    elif binary:
        data=payload;headers['Content-Type']='application/octet-stream'
    else:
        data=json.dumps(payload).encode('utf8'); headers['Content-Type']='application/json'
    req=urllib.request.Request(url,headers=headers,method=method,data=data)
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=100) as resp:
        raw=resp.read(MAX_RESPONSE+1)
        if len(raw)>MAX_RESPONSE: raise RuntimeError('Zenodo response exceeded bound')
        return json.loads(raw)

def read(path, authorized=True):
    for i in range(3):
        try: return api(path,authorized=authorized)
        except (urllib.error.URLError,TimeoutError,urllib.error.HTTPError):
            if i==2: raise
            time.sleep(3*(i+1))

def metadata(abstract):
    return {'upload_type':'publication','publication_type':'preprint','title':TITLE,
        'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
        'description':'<p>'+html.escape(abstract)+'</p><p>Methods preprint, not peer reviewed. Human author of record and responsible depositor: Hongju Liu. Substantial AI assistance was used in the research synthesis, finite-model verification, draft, editing and publication preparation. This is not a validation of a consciousness theory or a measured improvement in research productivity.</p>',
        'publication_date':'2026-10-08','version':VERSION,'access_right':'open','license':'cc-by-4.0',
        'keywords':['theory development','thought experiments','semantic audit','research provenance',
                    'human-AI research','versioned research maps','argument hypergraphs'],
        'language':'eng','notes':IDENTITY+'. Standalone methodological preprint; publication and timestamps establish identity and persistence, not novelty or peer review.',
        'related_identifiers':[{'identifier':'10.5281/zenodo.23206492','relation':'references','scheme':'doi'}]}

def extract_abstract(source):
    return source.split('## Abstract {-}',1)[1].split('**Keywords:**',1)[0].strip()

def locate_existing():
    """Only reuse an exact identity match; no collision with old unrelated records."""
    matches=[]
    for page in range(1,8):
        listing=read(f'/deposit/depositions?page={page}&size=100')
        if not isinstance(listing,list): raise RuntimeError('Zenodo draft listing shape changed')
        for row in listing:
            m=row.get('metadata',{})
            if m.get('title')==TITLE and str(m.get('version'))==VERSION:
                if IDENTITY not in m.get('notes',''):
                    raise RuntimeError('Title/version collision with unrelated deposit')
                matches.append(row)
        if len(listing)<100:break
    if len(matches)>1: raise RuntimeError('Multiple candidate Zenodo deposits; reconciliation required')
    return matches[0] if matches else None

def validate_deposit(dep):
    rid=dep.get('id')
    if not isinstance(rid,int) or rid<=0: raise RuntimeError('Invalid record id')
    m=dep.get('metadata') or {}
    doi=dep.get('doi') or m.get('prereserve_doi',{}).get('doi') or m.get('doi')
    if (m.get('title'),str(m.get('version')))!=(TITLE,VERSION):raise RuntimeError('Title/version mismatch')
    if IDENTITY not in m.get('notes',''):raise RuntimeError('Identity marker missing')
    if doi and doi != f'10.5281/zenodo.{rid}':raise RuntimeError('Reserved DOI mismatch')
    return rid, doi or f'10.5281/zenodo.{rid}'

def obtain_deposit(md):
    if (HERE/'deposit.json').exists():
        item=load('deposit.json')
        obj=read('/deposit/depositions/'+str(item['record_id']))
        rid,doi=validate_deposit(obj)
        if rid!=item['record_id'] or doi!=item['doi']:raise RuntimeError('Checkpoint identity changed')
        return obj
    hit=locate_existing()
    if hit:
        rid,doi=validate_deposit(hit)
        save('deposit.json',{'record_id':rid,'doi':doi,'identity':IDENTITY});persist()
        return hit
    if (HERE/'create-intent.json').exists():
        raise RuntimeError('Earlier create intent with no visible deposit: do not duplicate uncertain POST')
    save('create-intent.json',{'identity':IDENTITY,'pdf_sha256':EXPECTED[PDF][0],'state':'CREATE_ONCE_INTENT'})
    persist()  # survives if Zenodo POST response is lost
    try:
        obj=api('/deposit/depositions',method='POST',payload={'metadata':md})
    except Exception as exc:
        save('create-uncertain.json',{'state':'CREATE_RESPONSE_UNCERTAIN','exception':type(exc).__name__})
        persist();raise
    rid,doi=validate_deposit(obj)
    save('deposit.json',{'record_id':rid,'doi':doi,'identity':IDENTITY})
    persist()
    return obj

def file_identities_from_deposit(dep):
    rows={}
    for x in dep.get('files',[]):
        name=x.get('filename') or x.get('key')
        rows[name]=x
    return rows

def matches_remote_file(x,content):
    # Zenodo legacy files use md5:<hex> and filesize; some newer APIs supply size.
    import hashlib
    wanted='md5:'+hashlib.md5(content).hexdigest()
    chk=x.get('checksum') or x.get('checksum_md5')
    n=x.get('filesize',x.get('size'))
    return chk in (wanted,wanted[4:]) and n==len(content)

def upload_exact(dep):
    rid,doi=validate_deposit(dep)
    if dep.get('submitted'):
        return dep
    files={name:(HERE/name).read_bytes() for name in EXPECTED}
    citation=f'@misc{{Liu2026MGTD,\n author = {{Liu, Hongju}},\n title = {{{TITLE}}},\n year = {{2026}},\n version = {{{VERSION}}},\n doi = {{{doi}}},\n url = {{https://doi.org/{doi}}},\n note = {{Preprint; not peer reviewed}}\n}}\n'
    license_note=(f'{REPORT} | MGTD-PAPER-v{VERSION}\n{TITLE}\nDOI: {doi}\n\n'
       'Author of record: Hongju Liu. Substantial ChatGPT assistance was used under human direction for literature comparison, formalization, checking, drafting, and release preparation. The manuscript is a methods preprint and has not undergone independent peer review. Theoretical and software artifacts are not empirical evidence of consciousness. CC BY 4.0 applies to original material to the extent rights are held; cited third-party works retain their own rights. The PDF is the primary scholarly item. The reproducibility ZIP includes source and audit artifacts.\n')
    (HERE/'citation.bib').write_text(citation,encoding='utf8')
    (HERE/'README-LICENSE.txt').write_text(license_note,encoding='utf8')
    files.update({'citation.bib':citation.encode(), 'README-LICENSE.txt':license_note.encode()})
    # Upload only after metadata bound to exact identity; file retry is prohibited on
    # unknown outcomes unless new GET proves the exact same object already exists.
    bucket=dep.get('links',{}).get('bucket')
    if not bucket: raise RuntimeError('No Zenodo bucket link')
    if urllib.parse.urlsplit(bucket).netloc!='zenodo.org':raise RuntimeError('Untrusted upload bucket')
    for name,content in sorted(files.items()):
        latest=read('/deposit/depositions/'+str(rid))
        existing=file_identities_from_deposit(latest).get(name)
        if existing:
            if not matches_remote_file(existing,content):raise RuntimeError('Remote filename conflict: '+name)
            continue
        obj=api(bucket+'/'+urllib.parse.quote(name),method='PUT',payload=content,binary=True)
        if not matches_remote_file(obj,content):
            # if API structure differs, fresh GET is authoritative
            refreshed=file_identities_from_deposit(read('/deposit/depositions/'+str(rid))).get(name)
            if not refreshed or not matches_remote_file(refreshed,content):raise RuntimeError('Uploaded file identity not verified: '+name)
    latest=read('/deposit/depositions/'+str(rid))
    rows=file_identities_from_deposit(latest)
    if set(rows)!=set(files) or any(not matches_remote_file(rows[n],v) for n,v in files.items()):
        raise RuntimeError('Remote exact inventory check failed')
    save('upload-check.json',{'record_id':rid,'doi':doi,'state':'ALL_FILES_EXACT_UPLOADED',
          'files':[{'name':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(files.items())]})
    persist()
    return latest

def download_public(record_id,name):
    # Never forward credentials to a download CDN.
    url=f'https://zenodo.org/records/{record_id}/files/{urllib.parse.quote(name)}?download=1'
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MGTD-Public-Readback/1.0'}),timeout=80) as resp:
        data=resp.read(MAX_FILE+1)
    if len(data)>MAX_FILE:raise RuntimeError('Public download exceeds limit')
    return data

def public_verify(dep):
    rid,doi=validate_deposit(dep)
    public=read('/records/'+str(rid),authorized=False)
    if public.get('id')!=rid or public.get('doi')!=doi:
        raise RuntimeError('Anonymous public record identity mismatch')
    files=load('upload-check.json')['files']
    for item in files:
        data=download_public(rid,item['name'])
        if sha(data)!=item['sha256'] or len(data)!=item['bytes']:
            raise RuntimeError('Public exact file bytes mismatch: '+item['name'])
    return {'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','record_id':rid,'doi':doi,'title':TITLE,
            'version':VERSION,'report_number':REPORT,'files':files,'submitted':True,
            'public_file_readback_pass':True,'publication_type':'preprint','peer_reviewed':False}

def publish():
    verify_local();ensure_ci()
    source=(HERE/MD).read_text(encoding='utf8')
    md=metadata(extract_abstract(source))
    dep=obtain_deposit(md)
    rid,doi=validate_deposit(dep)
    if (HERE/'publication-record.json').exists():
        rec=load('publication-record.json')
        if rec.get('doi')!=doi:raise RuntimeError('Existing result DOI mismatch')
        print('Already published:',doi,'state:',rec.get('state'))
        return
    # Metadata is idempotent PUT; for matching existing exact draft, no third-party record mutation.
    if not dep.get('submitted'):
        if IDENTITY not in dep['metadata'].get('notes',''):
            raise RuntimeError('Existing metadata mismatch')
        dep=upload_exact(dep)
        if not (HERE/'publication-intent.json').exists():
            save('publication-intent.json',{'record_id':rid,'doi':doi,'identity':IDENTITY,
                                          'files':load('upload-check.json')['files'],
                                          'state':'PUBLISH_ONCE_INTENT'})
            persist()
            try:
                dep=api('/deposit/depositions/'+str(rid)+'/actions/publish',method='POST')
            except Exception as exc:
                save('publication-error.json',{'state':'PUBLISH_RESPONSE_UNCERTAIN','error_type':type(exc).__name__})
                persist()
                dep=read('/deposit/depositions/'+str(rid))
                if not dep.get('submitted'):
                    raise RuntimeError('Publish response uncertain; no automatic second POST') from exc
        else:
            # Previous uncertain publish attempt must be reconciled by readback, never replayed.
            dep=read('/deposit/depositions/'+str(rid))
            if not dep.get('submitted'):
                raise RuntimeError('Previous publish intent not confirmed; refuse duplicate publish POST')
    dep=read('/deposit/depositions/'+str(rid))
    if not dep.get('submitted'):raise RuntimeError('Zenodo record not published')
    rec=public_verify(dep)
    save('publication-record.json',rec)
    persist()
    print('ZENODO_PUBLICATION_SUCCESS',rec['doi'],'record:',rec['record_id'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['verify','publish','persist']);args=parser.parse_args()
    {'verify':verify_local,'publish':publish,'persist':persist}[args.action]()
