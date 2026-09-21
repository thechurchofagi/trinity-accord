#!/usr/bin/env python3
"""Publish only the separately reserved, exact-reviewed TA13 package."""
from __future__ import annotations
import hashlib, html, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from publication_common import DATE,REPORT,ROOT,STEM,TITLE,VERSION,check_deposit,client,download_public,extract_abstract,read,save,sha,validate_local_package
PHASE='local_review_gate'; IDENTITY={}
def resolver_matches_record(status,final_url,record_id):
    f=urllib.parse.urlsplit(final_url)
    return status==200 and f.scheme=='https' and f.hostname=='zenodo.org' and not f.username and not f.password and f.port in (None,443) and not f.query and not f.fragment and f.path.rstrip('/') in (f'/records/{record_id}',f'/record/{record_id}')
def check_doi_resolution(doi,record_id):
    result={'state':'RESOLVER_CHECK_UNAVAILABLE','matches_record':False}
    for delay in (0,10,30,60,120):
        if delay: time.sleep(delay)
        try:
            req=urllib.request.Request('https://doi.org/'+doi,headers={'User-Agent':'TrinityAccord-TA13-DOICheck/1.0'})
            with urllib.request.urlopen(req,timeout=20) as response:
                ok=resolver_matches_record(response.status,response.url,record_id)
                result={'state':'RESOLVER_PASS' if ok else 'RESOLVER_TARGET_MISMATCH','http_status':response.status,'final_url':response.url,'matches_record':ok}
            if ok: return result
        except Exception as error:
            result={'state':'RESOLVER_CHECK_UNAVAILABLE','error_type':type(error).__name__,'matches_record':False}
    return result
def draft_inventory(listing,allowed):
    if not isinstance(listing,list): raise RuntimeError('Unexpected draft inventory response')
    remote={x['filename']:x for x in listing}
    if len(remote)!=len(listing) or set(remote)-allowed: raise RuntimeError('Unrelated or duplicate draft files; no deletion or publication')
    return remote
def run():
    global PHASE,IDENTITY
    expected,manifest_sha=validate_local_package(); IDENTITY={k:expected[k] for k in ('record_id','doi')}
    rid,doi=expected['record_id'],expected['doi']; files=expected['files']; names={x['name'] for x in files}
    abstract=extract_abstract((ROOT/'published'/f'{STEM}-zh-v{VERSION}.md').read_text(encoding='utf-8'))
    z=client(); PHASE='read_reserved_record'
    deposit=read(z,f'/deposit/depositions/{rid}'); check_deposit(deposit,expected)
    already=bool(deposit.get('submitted'))
    if not already:
        PHASE='update_ta13_record_metadata'
        desc='<p>'+html.escape(abstract)+'</p><p>TA-TR-2026-13, version 1.0. A theory-method paper on civilizational-level accounting of new intellectual production and epistemic governance across humans, AI systems, and their interaction. The paper uses domain-first satellite accounts, partial identification, vintage quality revision, and a conservative robust-crossover criterion. The complete paper is in Chinese with an English title and abstract. Eleven assets include the PDF and Markdown manuscripts, simulation source/results, reproducibility record, citation metadata, source-boundary note, license note, and checksums. The three deterministic simulations are synthetic design checks and are not empirical estimates of real-world Human/AI intellectual shares.</p><p>Human author of record and responsible depositor: Hongju Liu. OpenAI GPT-5.6 Sol provided substantial literature research, originality stress-testing, formalization, simulation implementation, critical revision, drafting, and packaging under human direction. Not externally peer reviewed. The targeted search does not certify global priority. This first public edition is separate and non-amending; it does not replace any prior DOI or Bitcoin Original.</p><p>CC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their own rights. DOI registration, checksums, timestamps, and public readback do not establish truth, peer review, exhaustive originality, AGI status, consciousness, or moral credit.</p>'
        metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju'}],
                  'description':desc,'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'zho',
                  'keywords':['civilizational intellectual production','human-AI contribution','epistemic governance','partial identification','satellite accounts','AI measurement','AGI measurement']}
        deposit=z.request(f'/deposit/depositions/{rid}','PUT',{'metadata':metadata}); check_deposit(deposit,expected)
        PHASE='upload_exact_reviewed_files'
        remote=draft_inventory(read(z,f'/deposit/depositions/{rid}/files'),names)
        bucket=deposit['links']['bucket']; p=urllib.parse.urlsplit(bucket)
        if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or p.port not in (None,443) or p.query or p.fragment or not p.path.startswith('/api/files/'):
            raise RuntimeError('Unexpected draft upload bucket')
        for item in files:
            data=(ROOT/'published'/item['name']).read_bytes(); md5=hashlib.md5(data).hexdigest(); prev=remote.get(item['name'])
            if prev and str(prev.get('checksum','')).removeprefix('md5:')==md5 and prev.get('filesize')==len(data): continue
            z.request(bucket.rstrip('/')+'/'+urllib.parse.quote(item['name'],safe=''),'PUT',data,binary=True)
        PHASE='verify_complete_draft'; remote=draft_inventory(read(z,f'/deposit/depositions/{rid}/files'),names)
        if set(remote)!=names: raise RuntimeError('Draft inventory differs from reviewed package')
        for item in files:
            data=(ROOT/'published'/item['name']).read_bytes(); a=remote[item['name']]
            if str(a.get('checksum','')).removeprefix('md5:')!=hashlib.md5(data).hexdigest() or a.get('filesize')!=len(data):
                raise RuntimeError('Draft checksum/size mismatch: '+item['name'])
        PHASE='publish_reserved_record'
        save('publication-attempt.json',{'state':'PUBLICATION_INTENT_FOR_EXISTING_RECORD',**IDENTITY,'expected_manifest_sha256':manifest_sha,'new_record_creation':False,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        result=z.request(f'/deposit/depositions/{rid}/actions/publish','POST'); check_deposit(result,expected)
        if not result.get('submitted'): raise RuntimeError('Publication response is not submitted')
    PHASE='anonymous_public_metadata_readback'
    public=read(z,f'/records/{rid}',authenticated=False)
    if (public.get('id'),public.get('doi'),public.get('metadata',{}).get('title'),public.get('metadata',{}).get('version'))!=(rid,doi,TITLE,VERSION):
        raise RuntimeError('Public record identity mismatch')
    remote={x['key']:x for x in public.get('files',[])}
    if len(remote)!=len(files) or set(remote)!=names or len(public.get('files',[]))!=len(files): raise RuntimeError('Public file inventory mismatch')
    PHASE='anonymous_complete_file_readback'
    out=Path('/tmp/ta13-public-readback'); out.mkdir(parents=True,exist_ok=True); rows=[]
    for item in files:
        url=remote[item['name']]['links'].get('self') or remote[item['name']]['links'].get('download')
        data=download_public(url)
        if len(data)!=item['bytes'] or sha(data)!=item['sha256']: raise RuntimeError('Public exact-byte mismatch: '+item['name'])
        (out/item['name']).write_bytes(data); rows.append(dict(item,public_url=url))
    PHASE='doi_resolver_check'; resolver=check_doi_resolution(doi,rid); completed=resolver.get('matches_record') is True
    receipt={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS' if completed else 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING',
             'report_number':REPORT,'title':TITLE,'version':VERSION,**IDENTITY,'record_url':f'https://zenodo.org/records/{rid}',
             'submitted':True,'file_count':len(rows),'files':rows,'expected_manifest_sha256':manifest_sha,
             'public_readback_authenticated':False,'doi_resolver':resolver,'public_file_readback_pass':True,'doi_resolution_pass':completed,
             'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
             'was_already_published':already,'prior_doi_records_modified':False,'bitcoin_originals_modified':False,'new_research_papers':1,
             'peer_reviewed':False,'global_originality_certified':False,'google_scholar_indexing':'NOT_ASSERTED',
             'manuscript_language':'zho','english_text_role':'TITLE_AND_ABSTRACT_ONLY'}
    save('publication-record.json',receipt)
    save('publication-attempt.json',{'state':receipt['state'],**IDENTITY,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    if not completed: raise RuntimeError('Published files passed anonymous readback, but DOI resolution is pending; resume same record')
if __name__=='__main__':
    try: run()
    except Exception as error:
        save('publication-attempt.json',{'state':'INCOMPLETE_REQUIRES_REVIEW_OR_SAME_RECORD_RESUMPTION',**IDENTITY,'phase':PHASE,'error_type':type(error).__name__,'error':str(error),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'new_record_creation':False})
        print(f'{type(error).__name__}: {error}',file=sys.stderr); sys.exit(1)
