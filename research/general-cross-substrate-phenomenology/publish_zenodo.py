#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from publication_common import DATE,REPORT,ROOT,STEM,TITLE,VERSION,check_deposit,client,download_public,read,save,sha,validate_local_package
PHASE='local_review_gate'; IDENTITY={}
def resolver_matches(status,url,rid):
    p=urllib.parse.urlsplit(url)
    return status==200 and p.scheme=='https' and p.hostname=='zenodo.org' and not p.username and not p.password and p.port in (None,443) and not p.query and not p.fragment and p.path.rstrip('/') in (f'/records/{rid}',f'/record/{rid}')
def check_doi(doi,rid):
    out={'state':'RESOLVER_CHECK_UNAVAILABLE','matches_record':False}
    for delay in (0,10,20,30,40):
        if delay: time.sleep(delay)
        try:
            req=urllib.request.Request('https://doi.org/'+doi,headers={'User-Agent':'TrinityAccord-TA16-DOICheck/1.0'})
            with urllib.request.urlopen(req,timeout=20) as r:
                ok=resolver_matches(r.status,r.url,rid); out={'state':'RESOLVER_PASS' if ok else 'RESOLVER_TARGET_MISMATCH','http_status':r.status,'final_url':r.url,'matches_record':ok}
            if ok: return out
        except Exception as e: out={'state':'RESOLVER_CHECK_UNAVAILABLE','error_type':type(e).__name__,'matches_record':False}
    return out
def inventory(x,allowed):
    if not isinstance(x,list): raise RuntimeError('Unexpected draft inventory')
    remote={i['filename']:i for i in x}
    if len(remote)!=len(x) or set(remote)-allowed: raise RuntimeError('Unrelated or duplicate draft files')
    return remote
def run():
    global PHASE,IDENTITY
    expected,manifest_sha=validate_local_package(); rid,doi=expected['record_id'],expected['doi']; files=expected['files']; names={x['name'] for x in files}
    IDENTITY={'record_id':rid,'doi':doi}
    z=client(); PHASE='read_reserved_record'; dep=read(z,f'/deposit/depositions/{rid}'); check_deposit(dep,expected); already=bool(dep.get('submitted'))
    if not already:
        PHASE='update_metadata'
        manuscript=(ROOT/'published'/f'{STEM}-v{VERSION}.md').read_text()
        abstract=manuscript.split('## Abstract\n\n',1)[1].split('\n\n**Keywords:',1)[0]
        desc='<p>'+html.escape(abstract)+'</p><p>TA-TR-2026-16, version 1.0. English-only theoretical and methodological preprint. Human author of record and responsible depositor: Hongju Liu. Substantial ChatGPT assistance in literature retrieval, formalization, checking, drafting, code, and publication preparation. Not peer reviewed; no separate final human line-by-line review or institutional endorsement is claimed.</p><p>This is adjacent, first-party, non-amending scholarship. It neither defines nor validates nor changes the Trinity Accord. The finite checks are constructed mathematical illustrations, not empirical evidence of consciousness or a measured comparison of species. Focused literature review does not certify global originality.</p><p>CC BY 4.0 applies to newly written material to the extent rights are held. Third-party sources retain their rights.</p>'
        metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
          'description':desc,'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
          'keywords':['phenomenal consciousness','comparative consciousness','artificial consciousness','causal abstraction','transportability','measurement invariance','partial identification','coalitional causation','phenomenal structure'], 'related_identifiers':[{'identifier':'10.5281/zenodo.22934654','relation':'references','scheme':'doi'}]}
        dep=z.request(f'/deposit/depositions/{rid}','PUT',{'metadata':metadata}); check_deposit(dep,expected)
        PHASE='upload_exact_files'; remote=inventory(read(z,f'/deposit/depositions/{rid}/files'),names); bucket=dep['links']['bucket']; p=urllib.parse.urlsplit(bucket)
        if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or p.port not in (None,443) or not p.path.startswith('/api/files/'): raise RuntimeError('Unexpected upload bucket')
        for item in files:
            data=(ROOT/'published'/item['name']).read_bytes(); md5=hashlib.md5(data).hexdigest(); prev=remote.get(item['name'])
            if prev and str(prev.get('checksum','')).removeprefix('md5:')==md5 and prev.get('filesize')==len(data): continue
            z.request(bucket.rstrip('/')+'/'+urllib.parse.quote(item['name'],safe=''),'PUT',data,binary=True)
        PHASE='verify_draft'; remote=inventory(read(z,f'/deposit/depositions/{rid}/files'),names)
        if set(remote)!=names: raise RuntimeError('Draft inventory mismatch')
        for item in files:
            data=(ROOT/'published'/item['name']).read_bytes(); a=remote[item['name']]
            if str(a.get('checksum','')).removeprefix('md5:')!=hashlib.md5(data).hexdigest() or a.get('filesize')!=len(data): raise RuntimeError('Draft checksum mismatch: '+item['name'])
        save('publication-attempt.json',{'state':'PUBLICATION_INTENT_FOR_EXISTING_RECORD',**IDENTITY,'expected_manifest_sha256':manifest_sha,'new_record_creation':False,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        PHASE='publish_reserved_record'; result=z.request(f'/deposit/depositions/{rid}/actions/publish','POST'); check_deposit(result,expected)
        if not result.get('submitted'): raise RuntimeError('Publish response not submitted')
    PHASE='anonymous_metadata'; public=read(z,f'/records/{rid}',authenticated=False)
    if (public.get('id'),public.get('doi'),public.get('metadata',{}).get('title'),public.get('metadata',{}).get('version'))!=(rid,doi,TITLE,VERSION): raise RuntimeError('Public identity mismatch')
    remote={x['key']:x for x in public.get('files',[])}
    if len(remote)!=len(files) or set(remote)!=names: raise RuntimeError('Public inventory mismatch')
    PHASE='anonymous_complete_file_readback'; out=Path('/tmp/ta16-public-readback'); out.mkdir(parents=True,exist_ok=True); rows=[]
    for item in files:
        url=remote[item['name']]['links'].get('self') or remote[item['name']]['links'].get('download'); data=download_public(url)
        if len(data)!=item['bytes'] or sha(data)!=item['sha256']: raise RuntimeError('Public exact-byte mismatch: '+item['name'])
        (out/item['name']).write_bytes(data); rows.append(dict(item,public_url=url))
    PHASE='doi_resolver'; resolver=check_doi(doi,rid); complete=resolver.get('matches_record') is True
    receipt={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS' if complete else 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING',
      'report_number':REPORT,'title':TITLE,'version':VERSION,**IDENTITY,'record_url':f'https://zenodo.org/records/{rid}','submitted':True,
      'file_count':len(rows),'files':rows,'expected_manifest_sha256':manifest_sha,'public_readback_authenticated':False,
      'doi_resolver':resolver,'public_file_readback_pass':True,'doi_resolution_pass':complete,
      'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
      'was_already_published':already,'prior_doi_records_modified':False,'bitcoin_originals_modified':False,'new_research_papers':1,
      'peer_reviewed':False,'global_originality_certified':False,'google_scholar_indexing':'NOT_ASSERTED','manuscript_language':'eng'}
    save('publication-record.json',receipt); save('publication-attempt.json',{'state':receipt['state'],**IDENTITY,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    if not complete: raise RuntimeError('Published files passed public readback; DOI resolution still propagating')
if __name__=='__main__':
    try: run()
    except Exception as e:
        save('publication-attempt.json',{'state':'INCOMPLETE_REQUIRES_REVIEW_OR_SAME_RECORD_RESUMPTION',**IDENTITY,'phase':PHASE,'error_type':type(e).__name__,'error':str(e),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'new_record_creation':False})
        print(f'{type(e).__name__}: {e}',file=sys.stderr); sys.exit(1)
