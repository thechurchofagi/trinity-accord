#!/usr/bin/env python3
"""Publish only the two authorized, reviewed v1.1 successors.

Never edits prior published files. Exact authorization binds the manifest and
reviewed PDFs. Checkpoints precede non-idempotent publication. All deposited
files are downloaded anonymously and verified after publication.
"""
from __future__ import annotations
import hashlib,html,json,os,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
import reserve as r

ROOT=r.ROOT
IDENTITIES={'a':(23030207,23005588,'23005587','TA-TR-2026-20'),
            'b':(23030320,23008262,'23008261','TA-TR-2026-21')}
def sha(data):return hashlib.sha256(data).hexdigest()
def require(condition,message):
    if not condition:raise RuntimeError(message)
def files_fingerprint(record):
    return sorted((f.get('key',f.get('filename')),f.get('checksum','').removeprefix('md5:'),
                   int(f.get('size',f.get('filesize',-1)))) for f in record.get('files',[]))
def check_old(z,key):
    original=r.load(f'prior-public-{key}.json');rid=IDENTITIES[key][1]
    now=z.request(f'/records/{rid}',authenticated=False)
    for field in ('id','doi','conceptrecid'):
        require(str(now.get(field))==str(original.get(field)),f'Prior {key} {field} changed')
    for field in ('title','version'):
        require(now['metadata'].get(field)==original['metadata'].get(field),f'Prior {key} {field} changed')
    require(files_fingerprint(now)==files_fingerprint(original),'Prior published file fingerprints changed')
    return {'prior_record_id':rid,'prior_doi':now['doi'],'file_count':len(now['files']),
            'file_fingerprints_unchanged':True,'title_and_version_unchanged':True,
            'scope':'Published file checksums, sizes and names plus title/version/identity; version-family links may change.'}
def delete_draft_file(z,rid,item):
    fid=item.get('id');require(fid is not None,'Draft file ID missing')
    endpoint=f'/deposit/depositions/{rid}/files/{urllib.parse.quote(str(fid),safe="")}'
    try:z.request(endpoint,'DELETE')
    except json.JSONDecodeError:
        # Zenodo can return a successful 204 response with an empty body.
        # Confirm absence in the authoritative draft listing before proceeding.
        listing=z.request(f'/deposit/depositions/{rid}/files')
        require(not any(str(f.get('id'))==str(fid) for f in listing),'Draft deletion not confirmed')
def resolve_doi(doi,rid):
    errors=[]
    for attempt in range(3):
        try:
            req=urllib.request.Request('https://doi.org/'+doi,headers={'User-Agent':'UCT-Release-Readback/1.1'})
            with urllib.request.urlopen(req,timeout=40) as response:
                p=urllib.parse.urlsplit(response.geturl())
                ok=p.scheme=='https' and p.hostname=='zenodo.org' and p.path.rstrip('/') in (f'/records/{rid}',f'/record/{rid}')
                return {'state':'PASS' if ok else 'UNEXPECTED_TARGET','resolved_url':response.geturl(),'pass':ok}
        except Exception as exc:
            errors.append(type(exc).__name__)
            if attempt<2:time.sleep(4)
    return {'state':'RESOLVER_CHECK_UNAVAILABLE','errors':errors,'pass':False}
def public_readback(z,key,paper,was_published):
    rid=paper['record_id'];expected={x['name']:x for x in paper['files']};public=None
    for attempt in range(8):
        try:public=z.request(f'/records/{rid}',authenticated=False);break
        except Exception:
            if attempt==7:raise
            time.sleep(5)
    require(public.get('id')==rid and public.get('doi')==paper['doi'],'Public identity mismatch')
    require(public['metadata'].get('title')==paper['title'] and str(public['metadata'].get('version'))=='1.1','Public title/version mismatch')
    require(str(public.get('conceptrecid'))==IDENTITIES[key][2],'Public version family mismatch')
    require({f['key'] for f in public['files']}==set(expected),'Public file set differs')
    readback=[]
    for item in public['files']:
        name=item['key'];data=z.download_public(item['links']['self']);e=expected[name]
        require(len(data)==e['bytes'] and sha(data)==e['sha256'],'Public byte mismatch: '+name)
        readback.append({**e,'public_url':item['links']['self'],'matches_local':True})
    previous=check_old(z,key);resolver=resolve_doi(paper['doi'],rid)
    result={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS' if resolver['pass'] else 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING',
            'report_number':paper['report_number'],'record_id':rid,'doi':paper['doi'],
            'title':paper['title'],'version':'1.1','conceptrecid':IDENTITIES[key][2],
            'record_url':f'https://zenodo.org/records/{rid}','submitted':True,
            'public_file_readback_pass':True,'public_readback_authenticated':False,
            'file_count':len(readback),'files':readback,'doi_resolver':resolver,
            'doi_resolution_pass':resolver['pass'],'prior_edition_check':previous,
            'prior_published_files_modified':False,'was_already_published':was_published,
            'publication_source_commit':os.environ.get('GITHUB_SHA'),
            'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
            'public_record_created':public.get('created'),'public_record_modified':public.get('modified'),
            'peer_reviewed':False,'human_data_validation':False,'global_originality_certified':False}
    r.save(f'publication-{key}.json',result);r.persist()
    print(key,paper['doi'],result['state'],len(readback),'verified files',flush=True)
    return result

def publish_one(z,key,paper,manifest_sha):
    rid,oldid,concept,report=IDENTITIES[key]
    require((paper['record_id'],paper['prior_record_id'],str(paper['conceptrecid']),paper['report_number'])==(rid,oldid,concept,report),'Allowlisted edition identity mismatch')
    require(paper['doi']==f'10.5281/zenodo.{rid}' and paper['version']=='1.1','Allowlisted DOI/version mismatch')
    check_old(z,key)
    expected={f['name']:f for f in paper['files']};dest=ROOT/'release'/key
    require(len(expected)==11 and {p.name for p in dest.iterdir() if p.is_file()}==set(expected),'Unexpected release membership')
    for name,e in expected.items():
        require(Path(name).name==name,'Unsafe filename')
        b=(dest/name).read_bytes();require(len(b)==e['bytes'] and sha(b)==e['sha256'],'Local digest mismatch: '+name)
    dep=z.request(f'/deposit/depositions/{rid}');md=dep['metadata']
    require(dep.get('id')==rid and str(dep.get('conceptrecid'))==concept,'Draft family mismatch')
    require(md.get('title')==paper['title'] and str(md.get('version'))=='1.1','Draft title/version mismatch')
    require(any(c.get('name')=='Liu, Hongju' for c in md.get('creators',[])),'Draft creator mismatch')
    if dep.get('submitted'):return public_readback(z,key,paper,True)
    intent=f'publish-intent-{key}.json'
    if (ROOT/intent).exists():
        # A prior publish request may have succeeded despite a lost response.
        for _ in range(4):
            time.sleep(5);dep=z.request(f'/deposit/depositions/{rid}')
            if dep.get('submitted'):return public_readback(z,key,paper,True)
        raise RuntimeError('Unresolved prior publication intent: no blind POST retry')
    require(md.get('prereserve_doi',{}).get('doi')==paper['doi'],'Reserved DOI changed')
    mainname='unified-consciousness-theory-'+('i' if key=='a' else 'ii')+'-v1.1.md'
    text=(dest/mainname).read_text();require('## Abstract' in text,'Abstract missing')
    abstract=text.split('## Abstract',1)[1].split('**Keywords:',1)[0].strip()
    description='<p>'+html.escape(abstract).replace('\n\n','</p><p>')+'</p><p>Version 1.1; '+report+'. Revised theoretical preprint, not peer reviewed. Human author and responsible depositor: Hongju Liu. Substantial ChatGPT assistance, including GPT-6 Astra Pro for the paired revision, is disclosed. Model checks are not empirical confirmation of experience, A1/A5, or complete intertheory recovery.</p><p>Adjacent non-amending research; not an amendment or independent corroboration of the Trinity Accord or Bitcoin Originals. The prior v1.0 files remain unchanged.</p>'
    metadata={'upload_type':'publication','publication_type':'preprint','title':paper['title'],
              'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
              'description':description,'publication_date':'2026-09-29','version':'1.1',
              'access_right':'open','license':'cc-by-4.0','language':'eng',
              'keywords':['consciousness','structural identity','process ontology','causal organization','theory unification'],
              'related_identifiers':[{'identifier':f'10.5281/zenodo.{oldid}','relation':'isNewVersionOf','scheme':'doi'},
                 {'identifier':f'10.5281/zenodo.{IDENTITIES["b" if key=="a" else "a"][0]}','relation':'references','scheme':'doi'}]}
    dep=z.request(f'/deposit/depositions/{rid}','PUT',{'metadata':metadata})
    original_names={f['key'] for f in r.load(f'prior-public-{key}.json')['files']}
    listing=z.request(f'/deposit/depositions/{rid}/files');deleted=[]
    for item in listing:
        name=item.get('filename',item.get('key'))
        if name not in expected:
            require(name in original_names,'Unrecognized file in new draft; stop rather than delete')
            delete_draft_file(z,rid,item);deleted.append(name)
    r.save(f'draft-cleanup-{key}.json',{'record_id':rid,'removed_inherited_draft_filenames':deleted,'prior_published_files_modified':False})
    r.persist()
    bucket=dep['links']['bucket'];parts=urllib.parse.urlsplit(bucket)
    require(parts.scheme=='https' and parts.hostname=='zenodo.org' and parts.path.startswith('/api/files/') and not parts.username and not parts.password,'Unexpected bucket')
    for name in sorted(expected):
        z.request(bucket+'/'+urllib.parse.quote(name,safe=''),'PUT',(dest/name).read_bytes(),binary=True)
    listing=z.request(f'/deposit/depositions/{rid}/files')
    require({f.get('filename',f.get('key')) for f in listing}==set(expected),'Draft file list mismatch')
    for item in listing:
        name=item.get('filename',item.get('key'));b=(dest/name).read_bytes()
        require(item.get('checksum','').removeprefix('md5:')==hashlib.md5(b).hexdigest(),'Draft checksum mismatch: '+name)
    check_old(z,key)
    r.save(intent,{'state':'PUBLISH_ONCE_INTENT','record_id':rid,'doi':paper['doi'],'version':'1.1',
                   'expected_manifest_sha256':manifest_sha,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    r.persist()
    published=z.request(f'/deposit/depositions/{rid}/actions/publish','POST')
    require(published.get('submitted') is True,'Publication did not report submitted')
    return public_readback(z,key,paper,False)

def main():
    auth=r.load('PUBLISH-AUTHORIZATION.json');mb=(ROOT/'EXPECTED-PUBLICATION.json').read_bytes();mh=sha(mb)
    require(auth.get('authorized') is True and auth.get('visual_review_pass') is True,'Publication/visual authorization missing')
    require(auth.get('expected_manifest_sha256')==mh,'Authorization is not for this exact manifest')
    expected=json.loads(mb);require(len(expected['papers'])==2,'Exactly two revisions required')
    for key,paper in zip(('a','b'),expected['papers']):
        for f in paper['files']:
            if f['name'].endswith('.pdf'):
                require(auth['reviewed_pdf_sha256'].get(f['name'])==f['sha256'],'PDF not visually reviewed at this hash')
    z=r.client();results=[]
    for key,paper in zip(('a','b'),expected['papers']):results.append(publish_one(z,key,paper,mh))
    r.save('publication-summary.json',{'state':'BOTH_PUBLISHED_PUBLIC_FILES_VERIFIED','version':'1.1',
           'papers':[{k:p[k] for k in ('report_number','record_id','doi','state','file_count','doi_resolution_pass')} for p in results],
           'expected_manifest_sha256':mh,'ots_arweave':'Separate preservation lifecycle; not claimed by this worker.'})
    r.persist()
if __name__=='__main__':
    try:main()
    finally:r.persist()
