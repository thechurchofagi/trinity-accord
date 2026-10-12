#!/usr/bin/env python3
"""CTP-2026-01 v3.1.0 exact-byte Zenodo publisher.

Bounded to one new work, only Zenodo, identity-checked files, and fail-closed
handling of uncertain remote creates. It never edits a prior publication.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.parse
import zipfile

TITLE = ('Before We Know What We Will Become: Historical Witness, Human '
         'Continuity, and Open Inheritance under Transformative AI')
REPORT = 'CTP-2026-01'
VERSION = '3.1.0'
DATE = '2026-10-12'
BRANCH = 'research/open-inheritance-ctp-v310-20261012'
REL = Path('research/civilizational-testament/versions/v3.1.0')
PDF = 'Before_We_Know_What_We_Will_Become_v3.1.0.pdf'
MD = 'manuscript.md'
ZIP = 'Open_Inheritance_DOI_Preparation_v3.1.0.zip'
EXPECT = {
 PDF: (187669, 'ee27e2e5e6b738481641917e080a00fc3a652a392cd26af1c3052416bf8f62da'),
 MD: (109364, 'c6cc17c1b8068c08f88ac027232095365f52b62d30a51e1d8c20db67508b6635'),
 ZIP: (456515, '05c97b990347ee0e14199cff93dfcbcf3f63b42d73b93f7b13cdedbebec91e6e'),
}
EXISTING_GUARD = {21699878, 21900592, 22761411, 22804542, 22809019, 22830239,
                  23137088, 23176685, 23241982, 23279189, 23308239}
CLIENT_SHA = 'a0cbc84cc5fd826c06d16456c4adbaa40dabc788'


def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def load(p: Path): return json.loads(p.read_text(encoding='utf-8'))
def save(p: Path, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')


def verify(root: Path) -> dict:
    receipt=load(root/'PREPUBLICATION_RECEIPT.json')
    if (receipt.get('report'),receipt.get('version'),receipt.get('title'))!=(REPORT,VERSION,TITLE):
        raise RuntimeError('Prepublication report identity mismatch')
    if not receipt.get('authorized_to_publish_by_user'): raise RuntimeError('Explicit publication instruction absent')
    if receipt.get('publishing_state')!='EXACT_SOURCE_STAGED_NO_ZENODO_DOI':
        raise RuntimeError('Frozen staging status unexpected')
    files={x['path']:x for x in receipt['files']}
    if set(files)!=set(EXPECT): raise RuntimeError('Frozen file set differs')
    for name,(size,digest) in EXPECT.items():
        f=root/name;b=f.read_bytes()
        if len(b)!=size or sha(b)!=digest or files[name]['sha256']!=digest:
            raise RuntimeError('Frozen file mismatch: '+name)
    if not (root/PDF).read_bytes().startswith(b'%PDF-'):
        raise RuntimeError('Not a PDF')
    with zipfile.ZipFile(root/ZIP) as z:
        prefix='Open_Inheritance_v3.1.0/'
        if z.read(prefix+PDF)!=(root/PDF).read_bytes() or z.read(prefix+MD)!=(root/MD).read_bytes():
            raise RuntimeError('Review package not identical to frozen PDF/Markdown')
        md=json.loads(z.read(prefix+'zenodo_metadata_TEMPLATE.json'))['metadata']
        if (md['title'],md['version'],md['creators'][0]['name'])!=(TITLE,VERSION,'Liu, Hongju'):
            raise RuntimeError('Depositor metadata mismatch')
        if md['license']!='cc-by-4.0' or md['access_right']!='open':
            raise RuntimeError('Rights metadata differs')
    return md


def repo_root() -> Path:
    p=Path(__file__).resolve()
    # script lives at repo/research/civilizational-testament/versions/v3.1.0/publication.py
    return p.parents[4]


def checkpoint(root: Path, paths: list[str]):
    repo=repo_root()
    if not (repo/'.git').exists(): return
    staging=[str((root/p).relative_to(repo)) for p in paths if (root/p).exists()]
    if not staging:return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=repo,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=repo,check=True)
    subprocess.run(['git','add','--',*staging],cwd=repo,check=True)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=repo).returncode==0: return
    subprocess.run(['git','diff','--cached','--check'],cwd=repo,check=True)
    subprocess.run(['git','commit','-m',f'Preserve {REPORT} DOI release state [skip ci]'],cwd=repo,check=True)
    for attempt in range(3):
        run=subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=repo)
        if run.returncode==0:return
        subprocess.run(['git','fetch','origin',BRANCH,'--prune'],cwd=repo,check=True)
        subprocess.run(['git','rebase','origin/'+BRANCH],cwd=repo,check=True)
    raise RuntimeError('Unable to persist remote Zenodo checkpoint: halt')


def zclient(repo: Path):
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token: raise RuntimeError('ZENODO_ACCESS_TOKEN unavailable; no deposit attempted')
    path=repo/'research/reading-trinity-accord/publish_zenodo.py'
    data=path.read_bytes()
    gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if gitsha!=CLIENT_SHA:raise RuntimeError('Established Zenodo client identity changed')
    spec=importlib.util.spec_from_file_location('ctp_verified_zenodo_client',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Zenodo(token)


def safe_id(dep):
    rid=dep.get('id')
    if type(rid) is not int or rid in EXISTING_GUARD or rid < 100000:
        raise RuntimeError('Protected/invalid Zenodo record identity')
    md=dep.get('metadata',{})
    if (md.get('title'),str(md.get('version')))!=(TITLE,VERSION):
        raise RuntimeError('Wrong Zenodo title/version; will not modify')
    if not any(c.get('name')=='Liu, Hongju' for c in md.get('creators',[])):
        raise RuntimeError('Zenodo author mismatch')
    doi=dep.get('doi') or md.get('prereserve_doi',{}).get('doi')
    if doi!=f'10.5281/zenodo.{rid}':
        raise RuntimeError('Reserved/registered Zenodo DOI mismatch')
    return rid,doi


def find_exact(z):
    # Search both drafts and published deposits of the *authorized* Zenodo account.
    # Never create a replacement if pagination cannot be exhaustively checked.
    hits=[]
    for status in ('draft','published'):
        q=urllib.parse.urlencode({'status':status,'sort':'-mostrecent','size':100,'all_versions':1})
        rows=z.request('/deposit/depositions?'+q)
        if not isinstance(rows,list) or len(rows)>=100:
            raise RuntimeError('Cannot exhaustively check existing depositions; abort to prevent duplicate')
        hits.extend(d for d in rows if d.get('metadata',{}).get('title')==TITLE and str(d.get('metadata',{}).get('version'))==VERSION)
    unique={x['id']:x for x in hits}
    if len(unique)>1:raise RuntimeError('More than one matching Zenodo deposit; manual reconciliation required')
    return next(iter(unique.values())) if unique else None


def metadata_for_deposit(proposed):
    md={k:v for k,v in proposed.items() if k not in ('notes','prereserve_doi','doi')}
    desc=html.escape(proposed['description'])
    md['description']='<p>'+desc+'</p><p><strong>Scientific status:</strong> Open-access conceptual/formal preprint, not peer reviewed. Formal finite logical experiments are not human-subject or current AI model tests.</p><p><strong>Provenance:</strong> Hongju Liu is the human author of record and directed revisions. ChatGPT / GPT-6 Astra Pro substantially contributed research, proofs, code, analysis, and drafting. The author is associated with the motivating Trinity Accord, disclosed in the text. No independent funding or financial-interest audit is claimed.</p><p><strong>Preservation:</strong> The PDF and source retain the exact author-directed v3.1.0 predeposit bytes. Phrases describing an unassigned DOI refer to the frozen predeposit manuscript. This Zenodo record supplies the DOI at publication. Publication does not imply endorsement, peer review, or acceptance by any future AI. CC BY 4.0 applies only where the depositor holds rights; included third-party source references retain their rights.</p>'
    md['notes']='CTP-2026-01 v3.1.0. First deposit of this paper. The enclosed ZIP contains exact reproducibility code, bounded synthetic results, review records, and precursor manuscripts. The ZIP includes historical preparation status metadata which must not be treated as the current Zenodo deposit status. Published DOI identifies this frozen file set.'
    md['prereserve_doi']=True
    return md


def public_readback(z,rid,doi):
    for delay in (0,3,8,15,25,35):
        if delay:time.sleep(delay)
        try:
            pub=z.request('/records/'+str(rid),authenticated=False)
            if pub.get('id')!=rid or pub.get('doi')!=doi or pub.get('metadata',{}).get('title')!=TITLE:
                raise RuntimeError('Public identity differs')
            if pub['metadata'].get('version')!=VERSION:
                raise RuntimeError('Published version differs')
            rows=pub['files']
            if {f['key'] for f in rows} != set(EXPECT):
                raise RuntimeError('Published file set differs')
            out=[]
            for f in rows:
                name=f['key']; b=z.download_public(f['links']['self']);size,digest=EXPECT[name]
                if len(b)!=size or sha(b)!=digest:
                    raise RuntimeError('Anonymous public SHA-256 readback failed for '+name)
                out.append({'name':name,'sha256':digest,'bytes':size,'readback_pass':True})
            return sorted(out,key=lambda f:f['name'])
        except Exception:
            if delay==35:raise
    raise RuntimeError('Anonymous public readback failed')


def publish(root:Path):
    proposed=verify(root)
    repo=repo_root();z=zclient(repo)
    existing=load(root/'deposit.json') if (root/'deposit.json').exists() else None
    if existing:
        rid=existing['record_id'];dep=z.request('/deposit/depositions/'+str(rid))
        got=safe_id(dep)
        if got!=(rid,existing['doi']):raise RuntimeError('Persistent Zenodo draft identity changed')
    else:
        dep=find_exact(z)
        if dep is None:
            if (root/'create-attempt.json').exists():
                raise RuntimeError('Uncertain previous remote create; no second new deposit allowed')
            save(root/'create-attempt.json',{'state':'CREATE_ATTEMPT_DECLARED_BEFORE_POST','report':REPORT,'version':VERSION,
                'source_pdf_sha256':EXPECT[PDF][1], 'github_run_id':os.environ.get('GITHUB_RUN_ID'),
                'new_record_count_limit':1})
            checkpoint(root,['create-attempt.json'])
            dep=z.request('/deposit/depositions','POST',{'metadata':metadata_for_deposit(proposed)})
        rid,doi=safe_id(dep)
        save(root/'deposit.json',{'record_id':rid,'doi':doi,'title':TITLE,'version':VERSION,
            'source_pdf_sha256':EXPECT[PDF][1],'submitted':bool(dep.get('submitted'))})
        checkpoint(root,['deposit.json'])
    rid,doi=safe_id(dep)
    if not dep.get('submitted'):
        md=metadata_for_deposit(proposed)
        dep=z.request('/deposit/depositions/'+str(rid),'PUT',{'metadata':md})
        safe_id(dep)
        names={x.get('filename',x.get('key')) for x in dep.get('files',[])}
        if not names.issubset(EXPECT):raise RuntimeError('Draft includes unexpected files; will not remove or override')
        files=z.request('/deposit/depositions/'+str(rid)+'/files')
        names={x.get('filename',x.get('key')) for x in files}
        if not names.issubset(EXPECT):raise RuntimeError('Draft includes unexpected file; abort')
        existing_files={x.get('filename',x.get('key')):x for x in files}
        bucket=dep['links']['bucket']
        p=urllib.parse.urlsplit(bucket)
        if p.scheme!='https' or p.hostname!='zenodo.org' or not p.path.startswith('/api/files/'):
            raise RuntimeError('Unsafe Zenodo bucket URL')
        for name in sorted(EXPECT):
            b=(root/name).read_bytes()
            if name in existing_files:
                if existing_files[name].get('checksum','').removeprefix('md5:')!=hashlib.md5(b).hexdigest() or int(existing_files[name].get('filesize',-1))!=len(b):
                    raise RuntimeError('Existing draft file differs; no overwrite')
                continue
            z.request(bucket+'/'+urllib.parse.quote(name,safe=''),'PUT',b,binary=True)
        files=z.request('/deposit/depositions/'+str(rid)+'/files')
        if {x.get('filename',x.get('key')) for x in files}!=set(EXPECT):
            raise RuntimeError('Final draft file-set mismatch')
        for x in files:
            name=x.get('filename',x.get('key'));b=(root/name).read_bytes()
            if x.get('checksum','').removeprefix('md5:')!=hashlib.md5(b).hexdigest() or int(x.get('filesize',-1))!=len(b):
                raise RuntimeError('Final draft MD5/byte count mismatch')
        result=z.request('/deposit/depositions/'+str(rid)+'/actions/publish','POST')
        if not result.get('submitted'): raise RuntimeError('Zenodo did not report publication')
        save(root/'publication-attempt.json',{'state':'PUBLISH_ACCEPTED_AWAITING_PUBLIC_READBACK','record_id':rid,'doi':doi})
        checkpoint(root,['publication-attempt.json'])
    rows=public_readback(z,rid,doi)
    receipt={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','status':'PUBLISHED_AND_PUBLIC_READBACK_PASS',
        'report_number':REPORT,'version':VERSION,'title':TITLE,'record_id':rid,'doi':doi,'files':rows,
        'paper_file_count':len(rows),'peer_reviewed':False,'author':'Hongju Liu',
        'publication_source_commit':os.environ.get('GITHUB_SHA'),'public_file_readback_pass':True,
        'explanation':'Frozen predeposit PDF/source and exact supplement ZIP; no earlier DOI or Trinity Accord Original modified.'}
    save(root/'publication-record.json',receipt)
    checkpoint(root,['publication-record.json'])
    batch=repo/'research/paper-timestamps/2026-10-12-ctp-v310'
    targets={'schema':'trinityaccord.paper-ots-targets.v1','batch':batch.name,'paper_count':1,
       'papers':[{'report':REPORT,'record_id':rid,'doi':doi,'version':VERSION,'title':TITLE,
       'receipt_path':str((root/'publication-record.json').relative_to(repo)),
       'pdfs':[{'name':PDF,'bytes':EXPECT[PDF][0],'sha256':EXPECT[PDF][1],
                'role':'Complete English v3.1.0 conceptual/formal preprint'}]}]}
    save(batch/'targets.json',targets)
    print(json.dumps({'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','doi':doi,'record_id':rid,
        'files':rows, 'ots_targets':str(batch.relative_to(repo))},indent=2),flush=True)
    checkpoint(root,['publication-record.json'])
    # Batch gets its own push in the workflow so the DOI -> OTS boundary is durable.
    return rid


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['verify','publish']);ap.add_argument('--root',type=Path,default=None)
    a=ap.parse_args();root=a.root or Path(__file__).resolve().parent
    if a.action=='verify':
        md=verify(root);print(json.dumps({'status':'EXACT_LOCAL_FILES_AND_METADATA_PASS','title':md['title'],
            'version':VERSION,'files':{n:{'bytes':z[0],'sha256':z[1]} for n,z in EXPECT.items()}},indent=2));return
    if a.root is not None:raise RuntimeError('Remote publication does not permit overridden root')
    publish(root)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('CTP publication stopped safely: '+type(exc).__name__+': '+str(exc),file=sys.stderr)
        raise
