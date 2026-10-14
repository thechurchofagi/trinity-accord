#!/usr/bin/env python3
"""Reconcile an observed pre-existing draft; never silently discard unknown files."""
import hashlib,json,os,urllib.parse,urllib.request
from pathlib import Path
import reserve as r
import publish
from family_check import verify
z=r.client()
try:
    verify(z)
    expected=r.load('EXPECTED-PUBLICATION.json');recoveries=[]
    for key,rid in [('a',23030207),('b',23030320)]:
        dep=z.request(f'/deposit/depositions/{rid}');rows=z.request(f'/deposit/depositions/{rid}/files')
        r.save(f'draft-inventory-{key}.json',{'record_id':rid,'submitted':dep.get('submitted'),'listing_type':type(rows).__name__,'files':rows,'deposition_file_summary':dep.get('files',[])})
        if dep.get('submitted'):continue
        paper=next(p for p in expected['papers'] if p['record_id']==rid)
        desired={f['name'] for f in paper['files']};old={f['key'] for f in r.load(f'prior-public-{key}.json')['files']}
        extras=[f for f in rows if f.get('filename') not in desired|old]
        if not extras:continue
        authpath=r.ROOT/'DRAFT-RECONCILIATION.json'
        if authpath.exists():
            auth=json.loads(authpath.read_text());scope=auth['records'][str(rid)]
            if auth.get('reviewed') is not True or auth['expected_manifest_sha256']!=hashlib.sha256((r.ROOT/'EXPECTED-PUBLICATION.json').read_bytes()).hexdigest():
                raise RuntimeError('Draft reconciliation is not bound to this reviewed release')
            actual={f['filename']:(int(f['filesize']),f['checksum'].removeprefix('md5:')) for f in rows}
            approved={f['name']:(f['bytes'],f['api_checksum'].removeprefix('md5:')) for f in scope['files']}
            if actual!=approved:raise RuntimeError('Draft changed since recovery review; no deletion permitted')
            publish.check_old(z,key)
            for item in extras:publish.delete_draft_file(z,rid,item)
            r.save(f'draft-reconciled-{key}.json',{'state':'REVIEWED_OLDER_DRAFT_SUPERSEDED','record_id':rid,
              'retained_recovery_artifact_id':scope['recovery_artifact_id'],
              'removed_extra_draft_filenames':[f['filename'] for f in extras],
              'reason':scope['reason'],'prior_published_files_modified':False})
            r.persist()
        else:
            out=r.ROOT/'unpublished-recovery'/key;out.mkdir(parents=True,exist_ok=True);manifest=[]
            for item in rows:
                name=item['filename']
                if Path(name).name!=name:raise RuntimeError('Unsafe draft filename')
                url=item['links']['download'];u=urllib.parse.urlsplit(url)
                if u.scheme!='https' or u.hostname!='zenodo.org' or not u.path.startswith(f'/api/records/{rid}/draft/files/'):
                    raise RuntimeError('Unexpected draft download host/path')
                req=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['ZENODO_ACCESS_TOKEN'],'User-Agent':'UCT-Draft-Reconciliation/1.1'})
                with urllib.request.urlopen(req,timeout=120) as resp:data=resp.read(8_000_001)
                if len(data)>8_000_000:raise RuntimeError('Unexpected oversized draft file')
                (out/name).write_bytes(data)
                manifest.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                  'md5':hashlib.md5(data).hexdigest(),'api_checksum':item.get('checksum'),
                  'api_filesize':item.get('filesize')})
            (out/'RECOVERY-MANIFEST.json').write_text(json.dumps({'record_id':rid,'files':manifest},indent=2)+'\n')
            r.save(f'draft-recovery-{key}.json',{'state':'CAPTURED_FOR_REVIEW_NOT_REPLACED','record_id':rid,
              'run_id':os.environ.get('GITHUB_RUN_ID'),'files':manifest,
              'extra_draft_filenames':[f['filename'] for f in extras],
              'recovery_location':'unpublished-recovery/'+key+' in retained workflow artifact; excluded from Git'})
            recoveries.append(rid)
    r.persist()
    if recoveries:raise RuntimeError('Pre-existing draft contents retained for review; no publication or deletion performed: '+str(recoveries))
    publish.main()
finally:r.persist()
