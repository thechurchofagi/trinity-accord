#!/usr/bin/env python3
"""Publish the exact reviewed TA-TR-2026-10 v1.2 package to reserved Zenodo record 22855837."""
import hashlib, html, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
from publication_common import *

RECORD=22855837
CONCEPT='22852884'
DOI=f'10.5281/zenodo.{RECORD}'
PHASE='local_review_gate'
ALLOWED={
 'endogenous-reference-fields-zh-v1.2.pdf',
 'endogenous-reference-fields-zh-v1.2.md',
 'README.md',
 'METHOD-AND-SOURCES.md',
 'LICENSE.txt',
 'citation.bib',
 'citation.ris',
 'citation.csl.json',
 'SHA256SUMS.txt',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check_identity(dep):
    md=dep.get('metadata',{})
    if (dep.get('id'),str(dep.get('conceptrecid')),md.get('title'),md.get('version'))!=(RECORD,CONCEPT,TITLE,VERSION):
        raise RuntimeError('reserved version/concept identity mismatch')
    if [x.get('name') for x in md.get('creators',[])]!=['Liu, Hongju']:
        raise RuntimeError('creator mismatch')
    doi=dep.get('doi') or md.get('doi') or md.get('prereserve_doi',{}).get('doi')
    if doi!=DOI:
        raise RuntimeError('reserved DOI mismatch')

def validate_package(root=ROOT):
    raw=(root/'EXPECTED-PUBLICATION.json').read_bytes()
    expected=json.loads(raw)
    if (
        expected.get('record_id'),
        str(expected.get('conceptrecid')),
        expected.get('previous_record_id'),
        expected.get('doi'),
        expected.get('version')
    )!=(RECORD,CONCEPT,PREVIOUS_RECORD,DOI,VERSION):
        raise RuntimeError('local identity mismatch')
    files=expected['files']
    names={x['name'] for x in files}
    if names!=ALLOWED or len(files)!=len(names) or expected['file_count']!=len(names):
        raise RuntimeError('unreviewed file inventory')
    directory=root/'published'
    if directory.is_symlink() or {x.name for x in directory.iterdir() if x.is_file()}!=names:
        raise RuntimeError('unexpected package files')
    for row in files:
        p=directory/row['name']
        data=p.read_bytes()
        if p.is_symlink() or len(data)!=row['bytes'] or sha(data)!=row['sha256']:
            raise RuntimeError('unreviewed bytes: '+row['name'])
    review=json.loads((root/'visual-review.json').read_text(encoding='utf-8'))
    if review.get('state')!='VISUAL_AND_CONTENT_REVIEW_PASS' or review.get('expected_manifest_sha256')!=sha(raw):
        raise RuntimeError('exact package review missing')
    gates=json.loads((root/'format-checks.json').read_text(encoding='utf-8'))
    required=(
      'logic_review','citation_claim_review','formal_scope_review','pdf_text_extractable',
      'markdown_pdf_consistency','all_pages_visual_review','historical_versions_preserved',
      'no_small_training_experiment_used_as_consciousness_evidence',
      'twenty_one_thought_experiments_preserved','subject_attribution_framework_preserved'
    )
    for k in required:
        if gates.get(k) is not True:
            raise RuntimeError('quality gate missing: '+k)
    return expected,sha(raw)

def public_download(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password:
        raise RuntimeError('unexpected public file host')
    with urllib.request.urlopen(
        urllib.request.Request(url,headers={'User-Agent':'TA10-v12-public-readback'}),
        timeout=120
    ) as r:
        if urllib.parse.urlsplit(r.url).hostname!='zenodo.org':
            raise RuntimeError('unexpected redirect')
        data=r.read(20*1024*1024+1)
    if len(data)>20*1024*1024:
        raise RuntimeError('asset too large')
    return data

def resolver_matches(status,url):
    p=urllib.parse.urlsplit(url)
    return (
      status==200 and p.scheme=='https' and p.hostname=='zenodo.org'
      and not (p.username or p.password or p.query or p.fragment)
      and p.port in (None,443)
      and p.path.rstrip('/') in (f'/records/{RECORD}',f'/record/{RECORD}')
    )

def resolver_check():
    result={'matches_record':False}
    for delay in (0,3,8):
        if delay:
            time.sleep(delay)
        try:
            with urllib.request.urlopen('https://doi.org/'+DOI,timeout=30) as r:
                result={'matches_record':resolver_matches(r.status,r.url),'http_status':r.status,'final_url':r.url}
            if result['matches_record']:
                break
        except Exception as e:
            result={'matches_record':False,'error_type':type(e).__name__}
    return result

def public_inventory(record):
    return {x['key']:(x['size'],x['checksum']) for x in record.get('files',[])}

def run():
    global PHASE
    expected,digest=validate_package()
    z=client()

    PHASE='read_predecessor_and_existing_draft'
    prev=read(z,f'/records/{PREVIOUS_RECORD}',authenticated=False)
    if (
      prev.get('id'),
      str(prev.get('conceptrecid')),
      prev.get('doi'),
      prev['metadata'].get('version')
    )!=(PREVIOUS_RECORD,CONCEPT,f'10.5281/zenodo.{PREVIOUS_RECORD}',PREVIOUS_VERSION):
        raise RuntimeError('predecessor lineage mismatch')
    prev_inventory=public_inventory(prev)

    dep=read(z,f'/deposit/depositions/{RECORD}')
    check_identity(dep)
    already=bool(dep.get('submitted'))

    if not already:
        PHASE='upload_exact_reviewed_version'
        md=(ROOT/'published/endogenous-reference-fields-zh-v1.2.md').read_text(encoding='utf-8')
        abstract=md.split('# Abstract\n',1)[1].split('**Keywords:**',1)[0].strip()
        metadata=dict(dep['metadata'])
        for key in ('doi','prereserve_doi'):
            metadata.pop(key,None)
        metadata.update({
          'title':TITLE,
          'version':VERSION,
          'publication_date':DATE,
          'upload_type':'publication',
          'publication_type':'preprint',
          'access_right':'open',
          'license':'cc-by-4.0',
          'language':'zho',
          'description':'<p>'+html.escape(abstract)+'</p><p>TA-TR-2026-10 v1.2, the third public version and current final revision, within concept DOI 10.5281/zenodo.22852884. It restores the broad experiential-attribution and subject-boundary theory of v1.0 while retaining the strongest formal and falsifiability improvements of v1.1. The small computational training experiment from v1.1 is not relied upon as evidence in this theoretical revision. v1.0 and v1.1 remain unchanged historical versions. Complete Chinese text with English title and abstract. Not peer reviewed. Substantial OpenAI ChatGPT/Codex assistance; Hongju Liu is the accountable author and depositor.</p>'
        })
        dep=z.request(f'/deposit/depositions/{RECORD}','PUT',{'metadata':metadata})
        check_identity(dep)

        remote=read(z,f'/deposit/depositions/{RECORD}/files')
        if len({x['filename'] for x in remote})!=len(remote):
            raise RuntimeError('duplicate draft files')

        # New-version drafts may inherit v1.1 files. Delete only files that are exact
        # copies of the published predecessor and are not part of the v1.2 package.
        for item in remote:
            name=item['filename']
            if name not in ALLOWED:
                old=prev_inventory.get(name)
                checksum=str(item.get('checksum','')).removeprefix('md5:')
                if not old or item.get('filesize')!=old[0] or checksum!=old[1].removeprefix('md5:'):
                    raise RuntimeError('unrelated draft asset; refusing deletion: '+name)
                fid=str(item['id'])
                if not re.fullmatch(r'[a-zA-Z0-9-]+',fid):
                    raise RuntimeError('bad file id')
                url=f'https://zenodo.org/api/deposit/depositions/{RECORD}/files/{fid}'
                req=urllib.request.Request(url,method='DELETE',headers={'Authorization':'Bearer '+z.token})
                with urllib.request.urlopen(req,timeout=120) as response:
                    if response.status!=204:
                        raise RuntimeError('draft copy deletion failed')

        bucket=dep['links']['bucket']
        parsed=urllib.parse.urlsplit(bucket)
        if parsed.scheme!='https' or parsed.hostname!='zenodo.org' or not parsed.path.startswith('/api/files/') or parsed.query or parsed.fragment:
            raise RuntimeError('unexpected bucket')

        for row in expected['files']:
            data=(ROOT/'published'/row['name']).read_bytes()
            z.request(bucket.rstrip('/')+'/'+urllib.parse.quote(row['name'],safe=''),'PUT',data,binary=True)

        remote=read(z,f'/deposit/depositions/{RECORD}/files')
        inventory={x['filename']:x for x in remote}
        if len(remote)!=len(ALLOWED) or set(inventory)!=ALLOWED:
            raise RuntimeError('draft inventory mismatch')
        for row in expected['files']:
            data=(ROOT/'published'/row['name']).read_bytes()
            rr=inventory[row['name']]
            if rr['filesize']!=len(data) or str(rr['checksum']).removeprefix('md5:')!=hashlib.md5(data).hexdigest():
                raise RuntimeError('draft byte mismatch: '+row['name'])

        PHASE='publish_existing_record'
        save('publication-attempt.json',{
          'state':'PUBLICATION_INTENT_FOR_EXISTING_RECORD',
          'record_id':RECORD,
          'expected_manifest_sha256':digest,
          'new_record_creation':False
        })
        result=z.request(f'/deposit/depositions/{RECORD}/actions/publish','POST')
        check_identity(result)
        if not result.get('submitted'):
            raise RuntimeError('not published')

    PHASE='anonymous_public_readback'
    public=read(z,f'/records/{RECORD}',authenticated=False)
    check_identity(public)
    remote={x['key']:x for x in public.get('files',[])}
    if len(public.get('files',[]))!=len(ALLOWED) or set(remote)!=ALLOWED:
        raise RuntimeError('public inventory mismatch')

    rows=[]
    out=Path('/tmp/ta10-v12-public-readback')
    out.mkdir(exist_ok=True)
    for row in expected['files']:
        url=remote[row['name']]['links']['self']
        data=public_download(url)
        if len(data)!=row['bytes'] or sha(data)!=row['sha256']:
            raise RuntimeError('public byte mismatch: '+row['name'])
        (out/row['name']).write_bytes(data)
        rows.append(dict(row,public_url=url,matches_local=True))

    after=read(z,f'/records/{PREVIOUS_RECORD}',authenticated=False)
    if public_inventory(after)!=prev_inventory or after.get('doi')!=prev.get('doi') or after['metadata'].get('version')!=PREVIOUS_VERSION:
        raise RuntimeError('predecessor inventory changed')

    PHASE='doi_resolution'
    resolver=resolver_check()
    passed=resolver['matches_record']
    receipt={
      'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS' if passed else 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING',
      'report_number':REPORT,
      'title':TITLE,
      'version':VERSION,
      'record_id':RECORD,
      'doi':DOI,
      'conceptrecid':CONCEPT,
      'previous_record_id':PREVIOUS_RECORD,
      'previous_doi':f'10.5281/zenodo.{PREVIOUS_RECORD}',
      'submitted':True,
      'file_count':len(rows),
      'files':rows,
      'expected_manifest_sha256':digest,
      'public_readback_authenticated':False,
      'public_file_readback_pass':True,
      'doi_resolution_pass':passed,
      'doi_resolver':resolver,
      'prior_version_inventory_unchanged':True,
      'v1_0_preserved':True,
      'v1_1_preserved':True,
      'new_research_papers':0,
      'distinct_research_papers':10,
      'was_already_published':already,
      'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
      'source_commit':os.environ.get('GITHUB_SHA'),
      'peer_reviewed':False
    }
    save('publication-record.json',receipt)
    save('publication-attempt.json',{
      'state':receipt['state'],
      'record_id':RECORD,
      'phase':'completed',
      'workflow_run_id':os.environ.get('GITHUB_RUN_ID')
    })
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    if not passed:
        raise RuntimeError('resume same record: DOI resolution pending')

if __name__=='__main__':
    try:
        run()
    except Exception as e:
        save('publication-attempt.json',{
          'state':'INCOMPLETE_REQUIRES_SAME_RECORD_RESUMPTION',
          'record_id':RECORD,
          'phase':PHASE,
          'error_type':type(e).__name__,
          'error':str(e),
          'workflow_run_id':os.environ.get('GITHUB_RUN_ID')
        })
        print(type(e).__name__+': '+str(e),file=sys.stderr)
        sys.exit(1)
