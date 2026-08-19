#!/usr/bin/env python3
"""Publish/reconcile the Chronicle sidechain cold-recovery package to Zenodo.

The publisher is fail-closed: a versioned mixed-rights acknowledgement is
required, local package integrity must pass, every uploaded file is checked by
size/MD5 transport checksum and then downloaded in full and checked by SHA-256
before publication and again after publication.
"""
from __future__ import annotations
import argparse, json, os, pathlib, sys, urllib.error, urllib.parse, urllib.request
from typing import Any
from chronicle_sidechain_doi_package import PACKAGE_TITLE, verify_package

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STATE=ROOT/'record-chain'/'chronicle-sidechain-zenodo-state.json'
DEFAULT_API='https://zenodo.org/api'
RIGHTS_ACK='TRINITY_SIDECHAIN_EVIDENCE_RIGHTS_V1_APPROVED'

class Client:
    def __init__(self,token:str,base:str):
        if not token: raise SystemExit('ZENODO_ACCESS_TOKEN is required')
        self.token=token; self.base=base.rstrip('/')
    def url(self,u:str)->str: return self.base+u if u.startswith('/') else u
    def headers(self,ctype:str|None=None)->dict[str,str]:
        h={'Accept':'application/json','Authorization':f'Bearer {self.token}','User-Agent':'trinity-sidechain-preservation/1.0'}
        if ctype: h['Content-Type']=ctype
        return h
    def request(self,method:str,url:str,payload:Any|None=None,data:bytes|None=None,ctype:str='application/json')->Any:
        body=data if data is not None else (json.dumps(payload).encode() if payload is not None else None)
        req=urllib.request.Request(self.url(url),data=body,method=method,headers=self.headers(ctype if body is not None else None))
        try:
            with urllib.request.urlopen(req,timeout=180) as r: raw=r.read()
        except urllib.error.HTTPError as e:
            detail=e.read().decode(errors='replace'); raise SystemExit(f'Zenodo {method} HTTP {e.code}: {detail[:4000]}') from e
        except OSError as e: raise SystemExit(f'Zenodo {method} failed: {e}') from e
        if not raw: return {}
        try: return json.loads(raw)
        except Exception as e: raise SystemExit('Zenodo returned non-JSON response') from e
    def bytes(self,url:str)->bytes:
        req=urllib.request.Request(self.url(url),headers=self.headers())
        try:
            with urllib.request.urlopen(req,timeout=300) as r: return r.read()
        except Exception as e: raise SystemExit(f'Zenodo full-byte readback failed: {e}') from e
    def delete(self,url:str)->None: self.request('DELETE',url)

def rid(r:dict[str,Any])->int: return int(r['id'])
def meta(r): return r.get('metadata') if isinstance(r.get('metadata'),dict) else {}
def published(r): return r.get('submitted') is True or str(r.get('state','')).lower()=='done' or bool(r.get('doi') or meta(r).get('doi'))
def doi(r): return str(r.get('doi') or meta(r).get('doi') or '')
def conceptdoi(r): return str(r.get('conceptdoi') or meta(r).get('conceptdoi') or '')
def download_url(item):
    links=item.get('links') if isinstance(item,dict) else None
    return str((links or {}).get('download') or (links or {}).get('content') or '')
def filename(item): return str(item.get('filename') or item.get('key') or '')
def filesize(item):
    try: return int(item.get('filesize') if item.get('filesize') is not None else item.get('size'))
    except Exception: return None

def list_records(c:Client)->list[dict[str,Any]]:
    out=[]
    for page in range(1,101):
        q=urllib.parse.urlencode({'size':100,'page':page,'sort':'mostrecent'})
        rows=c.request('GET',f'/deposit/depositions?{q}')
        if not isinstance(rows,list): raise SystemExit('Zenodo deposition listing is not a list')
        out.extend(x for x in rows if isinstance(x,dict))
        if len(rows)<100: break
    return [r for r in out if meta(r).get('title')==PACKAGE_TITLE]

def refresh(c:Client,r:dict[str,Any])->dict[str,Any]:
    x=c.request('GET',f'/deposit/depositions/{rid(r)}')
    if not isinstance(x,dict): raise SystemExit('Zenodo deposition readback is not object')
    return x

def verify_remote(c:Client,r:dict[str,Any],package_dir:pathlib.Path,package:dict[str,Any])->None:
    rows=r.get('files'); remote={filename(x):x for x in rows or [] if isinstance(x,dict) and filename(x)}
    expected=set(package['published_file_names'])
    if set(remote)!=expected: raise SystemExit(f'Zenodo file-set mismatch missing={sorted(expected-set(remote))} unexpected={sorted(set(remote)-expected)}')
    for name in sorted(expected):
        local=package['inventory'][name]; item=remote[name]
        if filesize(item)!=local['bytes']: raise SystemExit(f'Zenodo size mismatch: {name}')
        transport=str(item.get('checksum') or '').split(':',1)[-1].lower()
        if transport!=local['md5']: raise SystemExit(f'Zenodo transport checksum mismatch: {name}')
        u=download_url(item)
        if not u: raise SystemExit(f'Zenodo download URL missing: {name}')
        raw=c.bytes(u)
        import hashlib
        actual=hashlib.sha256(raw).hexdigest()
        if len(raw)!=local['bytes'] or actual!=local['sha256']: raise SystemExit(f'Zenodo full-byte SHA-256 mismatch: {name}')
        print(f'[ZENODO READBACK PASS] {name} bytes={len(raw)} sha256={actual}',flush=True)

def clear_files(c:Client,r:dict[str,Any])->None:
    for item in r.get('files') or []:
        links=item.get('links') if isinstance(item,dict) else None
        u=(links or {}).get('self')
        if u: c.delete(u)

def upload(c:Client,r:dict[str,Any],package_dir:pathlib.Path,names:list[str])->None:
    bucket=((r.get('links') or {}).get('bucket'))
    if not bucket: raise SystemExit('Zenodo draft missing bucket')
    for name in names:
        p=package_dir/name
        print(f'[ZENODO UPLOAD] {name} bytes={p.stat().st_size}',flush=True)
        c.request('PUT',bucket.rstrip('/')+'/'+urllib.parse.quote(name),data=p.read_bytes(),ctype='application/octet-stream')

def create_draft(c:Client,latest:dict[str,Any]|None,metadata:dict[str,Any])->dict[str,Any]:
    if latest is None:
        r=c.request('POST','/deposit/depositions',payload={'metadata':metadata})
        if not isinstance(r,dict): raise SystemExit('Zenodo create response invalid')
        return r
    response=c.request('POST',f'/deposit/depositions/{rid(latest)}/actions/newversion',payload={})
    u=((response.get('links') or {}).get('latest_draft')) if isinstance(response,dict) else None
    if not u: raise SystemExit('Zenodo new-version response missing latest_draft')
    r=c.request('GET',u)
    if not isinstance(r,dict): raise SystemExit('Zenodo latest draft invalid')
    return r

def write_state(path:pathlib.Path,r:dict[str,Any],package:dict[str,Any],api:str)->dict[str,Any]:
    links=r.get('links') or {}; d=doi(r)
    if not d: raise SystemExit('published Zenodo record has no DOI')
    state={'schema':'trinityaccord.chronicle-sidechain-zenodo-state.v1','latest_archive_id':package['archive_id'],'latest_deposition_id':rid(r),'latest_record_id':r.get('record_id') or rid(r),'latest_doi':d,'latest_doi_url':str(r.get('doi_url') or links.get('doi') or f'https://doi.org/{d}'),'concept_doi':conceptdoi(r) or None,'latest_package_identity_sha256':package['package_identity_sha256'],'latest_files':package['inventory'],'api_base':api,'rights_acknowledgement':RIGHTS_ACK}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n')
    return state

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--package-dir',required=True); ap.add_argument('--state',default=str(DEFAULT_STATE.relative_to(ROOT))); ap.add_argument('--api-base',default=os.getenv('ZENODO_API_BASE',DEFAULT_API)); ap.add_argument('--rights-boundary-ack',default=os.getenv('SIDECHAIN_EVIDENCE_ZENODO_RIGHTS_ACK','')); args=ap.parse_args()
    package_dir=(ROOT/args.package_dir).resolve()
    if ROOT not in package_dir.parents: raise SystemExit('package dir must be inside repo')
    package=verify_package(package_dir)
    if args.rights_boundary_ack!=RIGHTS_ACK: raise SystemExit('sidechain DOI publication disabled until versioned mixed-rights boundary is explicitly approved')
    c=Client(os.getenv('ZENODO_ACCESS_TOKEN','').strip(),args.api_base)
    records=list_records(c); same=[r for r in records if str(meta(r).get('version') or '')==package['archive_id']]
    pubs=[r for r in same if published(r)]; drafts=[r for r in same if not published(r)]
    if len(pubs)>1 or len(drafts)>1: raise SystemExit('duplicate sidechain Zenodo version/draft detected')
    if pubs:
        final=refresh(c,pubs[0]); verify_remote(c,final,package_dir,package)
        print(f'[ZENODO RECONCILED] archive={package["archive_id"]} doi={doi(final)}')
    else:
        if drafts: draft=refresh(c,drafts[0])
        else:
            published_series=sorted([r for r in records if published(r)],key=rid)
            unfinished=[r for r in records if not published(r)]
            if len(unfinished)>1: raise SystemExit('multiple orphan sidechain Zenodo drafts require manual reconciliation')
            draft=refresh(c,unfinished[0]) if unfinished else create_draft(c,published_series[-1] if published_series else None,package['metadata'])
        updated=c.request('PUT',f'/deposit/depositions/{rid(draft)}',payload={'metadata':package['metadata']})
        draft=refresh(c,updated); clear_files(c,draft); draft=refresh(c,draft)
        upload(c,draft,package_dir,package['published_file_names']); draft=refresh(c,draft)
        verify_remote(c,draft,package_dir,package)
        final=c.request('POST',f'/deposit/depositions/{rid(draft)}/actions/publish',payload={})
        final=refresh(c,final); verify_remote(c,final,package_dir,package)
        print(f'[ZENODO PUBLISHED] archive={package["archive_id"]} doi={doi(final)}')
    state_path=(ROOT/args.state).resolve()
    if ROOT not in state_path.parents: raise SystemExit('state path must be inside repo')
    state=write_state(state_path,final,package,args.api_base)
    print(json.dumps(state,indent=2,sort_keys=True))
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as h:
            h.write(f"doi={state['latest_doi']}\nconcept_doi={state.get('concept_doi') or ''}\nstate={args.state}\n")
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except KeyboardInterrupt: raise SystemExit(130)
