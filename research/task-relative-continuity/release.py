#!/usr/bin/env python3
"""RT20261009: checked source -> reserve DOI -> freeze package -> authorized publish.
Reuses the repository's create-once Zenodo/receipt pattern. Never replay uncertain POSTs.
Credentials remain in GitHub Actions and are sent only to https://zenodo.org/api/.
"""
from __future__ import annotations
import argparse, base64, hashlib, html, io, json, lzma, os, pathlib, shutil
import subprocess, sys, tarfile, tempfile, time, urllib.error, urllib.parse, urllib.request, zipfile

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = 'research/task-relative-continuity-v1-20261009'
REPORT, VERSION, DATE = 'RT20261009', '1.0.0', '2026-10-09'
TITLE = 'Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout'
STEM = 'task-relative-continuity-v1.0.0'
CAPSULE_SHA = 'eb000a31444d9f68161442a381ef9c8ed773981b37b50f62fed69f099400da07'
TEMPLATE_SHA = '6776cd0ffc26465c09bfb81e7b381557848677966503b54dfbc5a554495e1399'
IDENTITY = 'RT-TH-PAPER-v1.0.0; source-sha256='+TEMPLATE_SHA
PRIOR_IDS = {23241205,23241982,23131575,23137088,23002980,23206492}
PERSIST = ('create-intent.json','deposit.json','remote-error.json','BUILD_READY.json',
           'EXPECTED-PUBLICATION.json','publication-intent.json','publication-record.json',
           'upload-check.json','checks','published')

def digest(b): return hashlib.sha256(b).hexdigest()
def readj(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
def save(n,obj):
    p=ROOT/n; p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.tmp'); t.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); t.replace(p)

def persist():
    if os.getenv('GITHUB_ACTIONS')!='true': return
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
    if branch!=BRANCH: raise RuntimeError('Wrong checkpoint branch')
    if subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():
        raise RuntimeError('Refuse pre-existing staged files')
    paths=[str((ROOT/n).relative_to(REPO)) for n in PERSIST if (ROOT/n).exists()]
    if not paths:return
    for k,v in [('user.name','github-actions[bot]'),('user.email','41898282+github-actions[bot]@users.noreply.github.com')]:
        subprocess.run(['git','config',k,v],cwd=REPO,check=True)
    subprocess.run(['git','add','--',*paths],cwd=REPO,check=True)
    if not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():return
    subprocess.run(['git','diff','--cached','--check'],cwd=REPO,check=True)
    subprocess.run(['git','commit','-m','[skip ci] Preserve RT paper exact build or Zenodo stage'],cwd=REPO,check=True)
    # A failed push blocks continuation. Never rebase/replay a remote-publication POST.
    subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

def restore():
    cfg=readj(ROOT/'source/TRANSFER.json'); chunks=[]
    if cfg['compressed_sha256']!=CAPSULE_SHA:raise RuntimeError('Source identity changed')
    for row in cfg['parts']:
        b=(ROOT/'source'/row['name']).read_bytes()
        if len(b)!=row['bytes'] or digest(b)!=row['sha256']:raise RuntimeError('Part mismatch '+row['name'])
        chunks.append(b''.join(b.split()))
    packed=base64.b64decode(b''.join(chunks),validate=True)
    if len(packed)!=cfg['compressed_bytes'] or digest(packed)!=CAPSULE_SHA:raise RuntimeError('Capsule mismatch')
    data=lzma.decompress(packed)
    if len(data)!=cfg['source_tar_bytes']:raise RuntimeError('Source tar size mismatch')
    out=ROOT/'material'
    if not out.exists():
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='restore-') as td:
            tmp=pathlib.Path(td)/'material';tmp.mkdir()
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:') as tar:
                for m in tar.getmembers():
                    q=pathlib.PurePosixPath(m.name)
                    if not m.isfile() or q.is_absolute() or '..' in q.parts or m.size>2_000_000:
                        raise RuntimeError('Unsafe capsule member')
                    p=tmp.joinpath(*q.parts);p.parent.mkdir(parents=True,exist_ok=True)
                    p.write_bytes(tar.extractfile(m).read())
            shutil.move(str(tmp),str(out))
    manifest=readj(out/'SOURCE_MANIFEST.json')
    for row in manifest:
        b=(out/row['path']).read_bytes()
        if len(b)!=row['bytes'] or digest(b)!=row['sha256']:raise RuntimeError('Source member mismatch '+row['path'])
    if digest((out/'manuscript-template.md').read_bytes())!=TEMPLATE_SHA:raise RuntimeError('Template mismatch')
    print('SOURCE_CAPSULE_VERIFIED',len(manifest)+1)
    return out

def checks():
    src=restore();dst=ROOT/'checks';dst.mkdir(exist_ok=True)
    for name in ('check_transport','check_handoff','check_publication'):
        p=dst/(name+'.json')
        subprocess.run([sys.executable,str(src/'code'/(name+'.py')),'--output',str(p)],check=True,
                       env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        if readj(p).get('status')!='PASS':raise RuntimeError('Math check failed '+name)
    save('checks/REVIEW_SCOPE.json',{'status':'FINITE_CHECKS_PASS','source_sha256':TEMPLATE_SHA,
        'semantic_review':'Author-side conditional manuscript review; not independent peer review',
        'full_current_UCT_map_recertified':False,'mathematical_checks_are_not_phenomenal_measurements':True})

def ci():
    if os.getenv('GITHUB_ACTIONS')!='true' or not os.getenv('ZENODO_ACCESS_TOKEN'):
        raise RuntimeError('Existing Zenodo secret required inside GitHub Actions')
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):raise RuntimeError('Authenticated redirect refused')

def api(path,method='GET',data=None,auth=True,binary=False):
    url=path if path.startswith('https://') else 'https://zenodo.org/api'+path
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.netloc!='zenodo.org' or not p.path.startswith('/api/') or p.fragment:
        raise RuntimeError('Unapproved Zenodo API target')
    h={'User-Agent':'RT20261009-Publication/1.0'}
    if auth:h['Authorization']='Bearer '+os.environ['ZENODO_ACCESS_TOKEN']
    if data is not None:
        h['Content-Type']='application/octet-stream' if binary else 'application/json'
        if not binary:data=json.dumps(data).encode()
    req=urllib.request.Request(url,headers=h,method=method,data=data)
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=100) as r:
        b=r.read(8_000_001)
    if len(b)>8_000_000:raise RuntimeError('API response size bound')
    return json.loads(b)

def get(path,auth=True):
    for i in range(3):
        try:return api(path,auth=auth)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
            if i==2:raise
            time.sleep(i+2)

def metadata():
    text=(restore()/'manuscript-template.md').read_text()
    abstract=text.split('## Abstract',1)[1].split('**Keywords:**',1)[0].strip()
    return {'upload_type':'publication','publication_type':'preprint','title':TITLE,
        'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
        'description':'<p>'+html.escape(abstract)+'</p><p>Theoretical preprint; not peer reviewed. Author-directed, substantially AI-assisted synthesis with exact finite checks. No new consciousness axiom, empirical phenomenal validation, or demonstrated preservation of subjective identity is claimed.</p>',
        'version':VERSION,'publication_date':DATE,'language':'eng','access_right':'open','license':'cc-by-4.0',
        'prereserve_doi':True,'notes':IDENTITY+'. DOI and preservation establish artifact identity, not truth, historical originality, or peer review.',
        'keywords':['representational change','relational memory','stable readout','invariance','route ambiguity','theoretical consciousness','reproducibility'],
        'related_identifiers':[{'identifier':v,'relation':'references','scheme':'doi'} for v in
           ('10.5281/zenodo.23131575','10.5281/zenodo.23137088','10.5281/zenodo.23002980','10.5281/zenodo.23241982')]}

def validate(dep):
    rid=dep.get('id');m=dep.get('metadata',{})
    if type(rid)!=int or rid<=0 or rid in PRIOR_IDS:raise RuntimeError('Protected/invalid record')
    doi=dep.get('doi') or m.get('prereserve_doi',{}).get('doi') or m.get('doi')
    if (m.get('title'),str(m.get('version')))!=(TITLE,VERSION) or IDENTITY not in m.get('notes',''):
        raise RuntimeError('Deposit does not belong to this version')
    if doi!=f'10.5281/zenodo.{rid}':raise RuntimeError('DOI identity mismatch')
    if not any(x.get('name')=='Liu, Hongju' for x in m.get('creators',[])):raise RuntimeError('Creator mismatch')
    if (ROOT/'deposit.json').exists():
        old=readj(ROOT/'deposit.json')
        if (rid,doi)!=(old['record_id'],old['doi']):raise RuntimeError('Reserved identity changed')
    return rid,doi

def reserve():
    src=restore();ci()
    a=readj(ROOT/'PREPARE-AUTHORIZATION.json')
    if a.get('authorized') is not True or a.get('source_sha256')!=TEMPLATE_SHA or a.get('version')!=VERSION:
        raise RuntimeError('Invalid author preparation instruction')
    if (ROOT/'deposit.json').exists():
        old=readj(ROOT/'deposit.json');d=get('/deposit/depositions/'+str(old['record_id']));validate(d);return
    hits=[]
    for page in range(1,11):
        rows=get(f'/deposit/depositions?page={page}&size=100')
        if not isinstance(rows,list):raise RuntimeError('Unexpected draft listing')
        for row in rows:
            m=row.get('metadata',{})
            if m.get('title')==TITLE and str(m.get('version'))==VERSION:
                validate(row);hits.append(row)
        if len(rows)<100:break
    else:raise RuntimeError('Search incomplete; refuse duplicate create')
    if len(hits)>1:raise RuntimeError('Multiple same-title deposits require reconciliation')
    if hits:d=hits[0]
    else:
        if (ROOT/'create-intent.json').exists():raise RuntimeError('Uncertain prior create; do not replay')
        save('create-intent.json',{'identity':IDENTITY,'state':'CREATE_ONCE_INTENT','source_sha256':TEMPLATE_SHA});persist()
        try:d=api('/deposit/depositions','POST',{'metadata':metadata()})
        except Exception as e:
            save('remote-error.json',{'stage':'CREATE_UNCERTAIN','error_type':type(e).__name__});persist();raise
    rid,doi=validate(d)
    save('deposit.json',{'record_id':rid,'doi':doi,'title':TITLE,'version':VERSION,'identity':IDENTITY,'state':'RESERVED_NOT_PUBLISHED'})
    persist();print('DOI_RESERVED_NOT_PUBLISHED',doi)

def verify_package():
    e=readj(ROOT/'EXPECTED-PUBLICATION.json');dep=readj(ROOT/'deposit.json')
    if e['doi']!=dep['doi'] or e['source_sha256']!=TEMPLATE_SHA or e['version']!=VERSION:raise RuntimeError('Manifest identity mismatch')
    for r in e['files']:
        b=(ROOT/'published'/r['name']).read_bytes()
        if digest(b)!=r['sha256'] or len(b)!=r['bytes']:raise RuntimeError('Frozen publication changed '+r['name'])
    if {p.name for p in (ROOT/'published').iterdir() if p.is_file()}!={r['name'] for r in e['files']}:
        raise RuntimeError('Publication inventory changed')
    return e

def build():
    src=restore();dep=readj(ROOT/'deposit.json');doi=dep['doi']
    if doi!=f"10.5281/zenodo.{dep['record_id']}":raise RuntimeError('Invalid reserved DOI')
    if (ROOT/'EXPECTED-PUBLICATION.json').exists():verify_package();return
    if (ROOT/'PUBLISH-AUTHORIZATION.json').exists():raise RuntimeError('Do not rebuild authorized bytes')
    dst=ROOT/'published';dst.mkdir(exist_ok=True)
    if any(dst.iterdir()):raise RuntimeError('Unmanifested build output: reconcile first')
    md=(src/'manuscript-template.md').read_text().replace('__RESERVED_DOI__',doi)
    # Presentation-only reference repair before DOI publication.
    # Keep the complete historical commit identity inside the clickable URL while
    # shortening its printed label, so LaTeX does not extend beyond page 11.
    long_ref='release commit `f6445052acb1644fcdd7b2adcdda2307f7b98bc7`'
    short_ref='release commit [f6445052](https://github.com/thechurchofagi/trinity-accord/commit/f6445052acb1644fcdd7b2adcdda2307f7b98bc7)'
    if md.count(long_ref)!=1: raise RuntimeError('Reference [9] layout contract changed')
    md=md.replace(long_ref,short_ref,1)
    if '__RESERVED_DOI__' in md or doi not in md:raise RuntimeError('DOI injection failed')
    (dst/(STEM+'.md')).write_text(md,encoding='utf-8')
    cmd=['pandoc',str(dst/(STEM+'.md')),'--from=markdown+tex_math_single_backslash','--pdf-engine=xelatex','-o',str(dst/(STEM+'.pdf'))]
    p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (ROOT/'checks/build.log').write_text(p.stdout)
    if p.returncode:raise RuntimeError('PDF build failed; inspect build.log')
    txt=subprocess.check_output(['pdftotext',str(dst/(STEM+'.pdf')),'-'],text=True)
    info=subprocess.check_output(['pdfinfo',str(dst/(STEM+'.pdf'))],text=True)
    pages=int(next(x.split(':',1)[1] for x in info.splitlines() if x.startswith('Pages:')))
    if pages<8 or pages>25 or doi not in txt or 'Proposition 5' not in txt or len(txt)<20000:
        raise RuntimeError('PDF text/content preflight failed')
    save('checks/PDF_PREFLIGHT.json',{'pages':pages,'doi_present':True,'text_extractable':True,'visual_review':'AWAITING_DOWNLOADED_PDF_REVIEW','text_chars':len(txt)})
    note='Theoretical preprint; not peer reviewed. Author: Hongju Liu. Substantial AI assistance under human direction. Mathematical models and tests do not validate phenomenal experience. CC BY 4.0 for original material to the extent rights are held; third-party sources retain their rights.'
    (dst/'README-LICENSE.txt').write_text(TITLE+'\nVersion '+VERSION+' | '+doi+'\n\n'+note+'\n')
    (dst/'citation.bib').write_text('@misc{Liu2026TaskContinuity,\n  author={Liu, Hongju},\n  title={'+TITLE+'},\n  year={2026},\n  version={1.0.0},\n  doi={'+doi+'},\n  note={Theoretical preprint; not peer reviewed}\n}\n')
    shutil.copyfile(src/'REVIEW_REPORT.md',dst/'REVIEW-AND-SOURCES.md')
    arch=dst/(STEM+'-supplement.zip')
    with zipfile.ZipFile(arch,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        members=[]
        for p in sorted(src.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:members.append(('source/'+str(p.relative_to(src)),p.read_bytes()))
        for p in sorted((ROOT/'checks').rglob('*')):
            if p.is_file():members.append(('executed_checks/'+str(p.relative_to(ROOT/'checks')),p.read_bytes()))
        for p in sorted(dst.iterdir()):
            if p.is_file() and p!=arch:members.append(('publication/'+p.name,p.read_bytes()))
        members.append(('RELEASE_ID.json',(json.dumps({'report':REPORT,'version':VERSION,'doi':doi,'source_sha256':TEMPLATE_SHA,'preprint':True,'peer_reviewed':False},indent=2)+'\n').encode()))
        for name,b in members:
            zi=zipfile.ZipInfo('RT-TH-PAPER-v1.0.0/'+name,(2026,10,9,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,b)
    with zipfile.ZipFile(arch) as z:
        if z.testzip() is not None:raise RuntimeError('Supplement ZIP corrupt')
    rows=[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in sorted(dst.iterdir()) if p.is_file()]
    save('EXPECTED-PUBLICATION.json',{'report_number':REPORT,'title':TITLE,'version':VERSION,'record_id':dep['record_id'],'doi':doi,'source_sha256':TEMPLATE_SHA,'files':rows})
    save('BUILD_READY.json',{'state':'EXACT_PACKAGE_FROZEN_PENDING_VISUAL_AUTHORIZATION','doi':doi,'pdf_sha256':digest((dst/(STEM+'.pdf')).read_bytes()),'pages':pages})
    persist();print('BUILD_READY',doi,pages)

def download(url):
    # Public no-credential readback; normal public CDN redirects are allowed.
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'RT20261009-Public-Readback/1.0'}),timeout=90) as r:b=r.read(16_000_001)
    if len(b)>16_000_000:raise RuntimeError('File download bound')
    return b

def publish():
    ci();e=verify_package();a=readj(ROOT/'PUBLISH-AUTHORIZATION.json')
    pdf=next(r for r in e['files'] if r['name']==STEM+'.pdf')
    if a.get('authorized') is not True or a.get('doi')!=e['doi'] or a.get('pdf_sha256')!=pdf['sha256'] or a.get('visual_review_pass') is not True:
        raise RuntimeError('Exact build not authorized')
    dep=get('/deposit/depositions/'+str(e['record_id']));rid,doi=validate(dep)
    if not dep.get('submitted'):
        bucket=dep.get('links',{}).get('bucket')
        if not bucket:raise RuntimeError('Missing upload bucket')
        for row in e['files']:
            live=get('/deposit/depositions/'+str(rid))
            files={x.get('filename') or x.get('key'):x for x in live.get('files',[])}
            b=(ROOT/'published'/row['name']).read_bytes();old=files.get(row['name'])
            if old:
                chk=old.get('checksum','').removeprefix('md5:')
                if chk!=hashlib.md5(b).hexdigest() or old.get('filesize',old.get('size'))!=len(b):raise RuntimeError('Remote file conflict')
            else:api(bucket+'/'+urllib.parse.quote(row['name']),'PUT',b,binary=True)
        live=get('/deposit/depositions/'+str(rid))
        files={x.get('filename') or x.get('key'):x for x in live.get('files',[])}
        if set(files)!={r['name'] for r in e['files']}:raise RuntimeError('Remote inventory differs')
        for row in e['files']:
            x=files[row['name']];b=(ROOT/'published'/row['name']).read_bytes()
            if x.get('checksum','').removeprefix('md5:')!=hashlib.md5(b).hexdigest() or x.get('filesize',x.get('size'))!=len(b):raise RuntimeError('Upload check failed')
        save('upload-check.json',{'state':'EXACT_DRAFT_FILES_VERIFIED','doi':doi,'files':e['files']});persist()
        if (ROOT/'publication-intent.json').exists():
            dep=get('/deposit/depositions/'+str(rid))
            if not dep.get('submitted'):raise RuntimeError('Prior uncertain publish: do not replay')
        else:
            save('publication-intent.json',{'state':'PUBLISH_ONCE_INTENT','record_id':rid,'doi':doi,'files':e['files']});persist()
            try:dep=api('/deposit/depositions/'+str(rid)+'/actions/publish','POST')
            except Exception as ex:
                save('remote-error.json',{'stage':'PUBLISH_UNCERTAIN','error_type':type(ex).__name__});persist()
                dep=get('/deposit/depositions/'+str(rid))
                if not dep.get('submitted'):raise RuntimeError('Unconfirmed publication; no automatic replay') from ex
    dep=get('/deposit/depositions/'+str(rid));validate(dep)
    if not dep.get('submitted'):raise RuntimeError('Not published')
    public=get('/records/'+str(rid),auth=False)
    if public.get('id')!=rid or public.get('doi')!=doi:raise RuntimeError('Public identity mismatch')
    for row in e['files']:
        b=download(f'https://zenodo.org/records/{rid}/files/'+urllib.parse.quote(row['name'])+'?download=1')
        if len(b)!=row['bytes'] or digest(b)!=row['sha256']:raise RuntimeError('Public byte mismatch '+row['name'])
    save('publication-record.json',{'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','report_number':REPORT,'title':TITLE,'version':VERSION,'record_id':rid,'doi':doi,'conceptrecid':public.get('conceptrecid'),'submitted':True,'public_file_readback_pass':True,'peer_reviewed':False,'files':e['files']})
    persist();print('PUBLISHED_AND_PUBLIC_READBACK_PASS',doi)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('restore','checks','reserve','build','persist','verify','publish'));a=p.parse_args()
    {'restore':restore,'checks':checks,'reserve':reserve,'build':build,'persist':persist,'verify':verify_package,'publish':publish}[a.action]()
