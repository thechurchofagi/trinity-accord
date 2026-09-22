#!/usr/bin/env python3
"""Narrow TA14 v1.2 pipeline. Never edits/deletes a published record.
prepare: audit, reserve ONE new version of 22871209, build and checkpoint.
publish: require an exact package review gate, publish that version, read back.
No root POST creating an unrelated Zenodo concept is implemented.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
BRANCH='research/claim-architecture-transition-v1-2-20260922'
OLD=22871209
OLD_DOI='10.5281/zenodo.22871209'
OLD_PDF='claim-architecture-transition-v1.1.pdf'
OLD_SHA='9d3fec11bb4113daee10969de782faecf56cd8ca79448cd8552103094d1147ec'
TITLE='The Claim Architecture Transition: Real Claims, Endogenous Essential Prices, and Budget-Feasible Support'
VERSION='1.2'
DATE='2026-09-22'
STEM='claim-architecture-transition-v1.2'
INPUTS=('manuscript.md','audit.py','REVISION-AND-SOURCES.md','ORIGIN-AND-FUTURE.md','pipeline.py')
sys.path.insert(0,str(ROOT.parent))
from publication_common import client, download_public

def digest(data): return hashlib.sha256(data).hexdigest()
def load(name): return json.loads((ROOT/name).read_text())
def save(name,value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def persist(integrated=False):
    paths=[str(p.relative_to(REPO)) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if integrated: paths += ['research/index.md','README.md']
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','-f','--',*paths],cwd=REPO,check=True)
    staged=git('diff','--cached','--name-only').splitlines()
    if not set(staged)<=set(paths): raise RuntimeError('Unexpected staged path')
    if staged:
        subprocess.run(['git','commit','-m','research(ta14): checkpoint v1.2 exact package and state [skip ci]'],cwd=REPO,check=True)
        subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

def get(z,path,authenticated=True):
    for delay in (0,3,8,15):
        if delay: time.sleep(delay)
        try: return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
            if delay==15: raise

def inventory(public):
    return {f['key']:{'size':f.get('size'),'checksum':f.get('checksum')} for f in public.get('files',[])}

def old_identity(z,baseline=None):
    p=get(z,f'/records/{OLD}',False)
    if p.get('id')!=OLD or p.get('doi')!=OLD_DOI or p.get('metadata',{}).get('version')!='1.1':
        raise RuntimeError('Predecessor identity mismatch')
    if not p.get('metadata',{}).get('title','').startswith('The Claim Architecture Transition:'):
        raise RuntimeError('Predecessor title mismatch')
    inv=inventory(p)
    if len(inv)!=15 or OLD_PDF not in inv: raise RuntimeError('Predecessor inventory mismatch')
    if baseline is not None and inv!=baseline: raise RuntimeError('Predecessor files changed')
    f=next(f for f in p['files'] if f['key']==OLD_PDF)
    if digest(download_public(f['links'].get('self') or f['links']['download']))!=OLD_SHA:
        raise RuntimeError('Predecessor PDF bytes changed')
    if not p.get('conceptrecid'): raise RuntimeError('Missing predecessor concept identity')
    return p,inv

def check_child(dep,concept,rid=None,final=False):
    did=dep.get('id')
    if type(did) is not int or did<=0 or did==OLD: raise RuntimeError('Not a separate child version')
    if str(dep.get('conceptrecid'))!=str(concept): raise RuntimeError('New version left the original concept')
    if rid is not None and did!=rid: raise RuntimeError('Unexpected child ID')
    md=dep.get('metadata',{})
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']:
        raise RuntimeError('Unexpected author identity')
    if final:
        if (md.get('title'),md.get('version'))!=(TITLE,VERSION): raise RuntimeError('Child metadata mismatch')
    else:
        # A newly created Zenodo version can intentionally have no version label.
        # This exception is restricted to the verified same-concept child obtained
        # from the preserved parent's latest_draft, never an unrelated deposit.
        titles={TITLE,'The Claim Architecture Transition: Transformative AI, Real Claim Closure, and General Equilibrium Beyond Wage-Based Distribution'}
        if md.get('title') not in titles or md.get('version') not in (None,'','1.1','1.2'):
            raise RuntimeError('Ambiguous child metadata: '+json.dumps({'id':did,'title':md.get('title'),'version':md.get('version')}))
        if md.get('version') in (None,'') and dep.get('submitted'):
            raise RuntimeError('An unlabeled published child cannot be reused')
    return did

def metadata():
    desc=('TA-TR-2026-14 v1.2, a substantive corrective new version of DOI '+OLD_DOI+'. '
          'A bounded theoretical working paper comparing household affordability, financing balance and physical allocation. '
          'It retains a conditional CES diagnostic and adds an endogenous essential-price equilibrium with different worker and owner expenditure shares. '
          'An exact minimum nonlabor-income tax for a service floor is distinguished from basket affordability and compensated utility. '
          'The revision corrects the predecessor aggregate-gap population condition and narrows the originality claim. '
          'Proofs, counterexamples and deterministic internal design checks are included; these are not empirical calibration or independent replication.')
    disclosure=('Hongju Liu initiated the motivating concern, directed the work and authorized open deposit. '
                'GPT-6 Astra Pro substantially assisted source comparison, problem identification, model development, derivation, code, checks, drafting and packaging. '
                'The predecessor discloses GPT-5.6 Sol. No separate final human line-by-line review or external peer review is claimed. '
                'The work is adjacent first-party research, not Canon, not an amendment and not independent validation of the Trinity Accord. '
                'A dated research coordinate is not a claim to global priority. CC BY 4.0 applies to newly written material to the extent rights are held; third-party works retain their rights.')
    return {'upload_type':'publication','publication_type':'preprint','title':TITLE,
            'creators':[{'name':'Liu, Hongju'}],'description':'<p>'+html.escape(desc)+'</p><p>'+html.escape(disclosure)+'</p>',
            'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
            'prereserve_doi':True,'keywords':['automation','claim architecture','essential resources','general equilibrium','AI-assisted research','income distribution'],
            'notes':'Same paper and original Zenodo concept; fourteen papers remain fourteen. Predecessor files and version-specific proofs are preserved. DOI registration is not peer review, correctness or a priority certificate.'}

def reserve(z):
    old,inv=old_identity(z)
    concept=str(old['conceptrecid'])
    if (ROOT/'state.json').exists():
        state=load('state.json')
        if state['old_record_id']!=OLD or str(state['conceptrecid'])!=concept: raise RuntimeError('Checkpoint identity mismatch')
        dep=get(z,f"/deposit/depositions/{state['record_id']}")
        check_child(dep,concept,state['record_id'])
        return dep,state
    parent=get(z,f'/deposit/depositions/{OLD}')
    if not parent.get('submitted'): raise RuntimeError('Predecessor is not published')
    dep=None
    url=parent.get('links',{}).get('latest_draft')
    if url:
        candidate=get(z,url)
        if candidate.get('id')!=OLD:
            check_child(candidate,concept)
            if candidate.get('submitted'): raise RuntimeError('Unexpected already-published successor')
            dep=candidate
    if dep is None:
        if (ROOT/'creation-intent.json').exists():
            raise RuntimeError('Creation intent exists: reconcile same concept; never blindly create again')
        save('creation-intent.json',{'action':'newversion','parent_record_id':OLD,'conceptrecid':concept,'date':DATE,'run_id':os.environ.get('GITHUB_RUN_ID')})
        persist()
        answer=z.request(f'/deposit/depositions/{OLD}/actions/newversion','POST')
        url=answer.get('links',{}).get('latest_draft')
        if not url: raise RuntimeError('New-version response has no draft locator')
        dep=get(z,url)
    rid=check_child(dep,concept)
    if dep.get('submitted'): raise RuntimeError('Will not modify a published child')
    dep=z.request(f'/deposit/depositions/{rid}','PUT',{'metadata':metadata()})
    check_child(dep,concept,rid,True)
    doi=dep.get('metadata',{}).get('prereserve_doi',{}).get('doi')
    if doi!=f'10.5281/zenodo.{rid}': raise RuntimeError('Unconfirmed child DOI reservation')
    state={'state':'RESERVED_NOT_PUBLISHED','record_id':rid,'doi':doi,'version':VERSION,'title':TITLE,
           'old_record_id':OLD,'old_doi':OLD_DOI,'conceptrecid':concept,'old_inventory':inv,
           'old_pdf_sha256':OLD_SHA,'same_concept':True,'old_files_modified':False,'date':DATE}
    save('state.json',state); persist()
    return dep,state

def prepare():
    if (ROOT/'review-authorization.json').exists(): raise RuntimeError('Reviewed package is locked; remove gate explicitly before rebuilding')
    out=ROOT/'published'
    out.mkdir(exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'audit.py'),'--out',str(out)],check=True)
    z=client(); dep,state=reserve(z)
    if dep.get('submitted'): raise RuntimeError('Already public: use publish mode only to read back')
    doi=state['doi']
    source=(ROOT/'manuscript.md').read_text()
    if source.count('__VERSION_DOI__')!=1: raise RuntimeError('Unexpected DOI substitution marker')
    manuscript=source.replace('__VERSION_DOI__',doi)
    (out/(STEM+'.md')).write_text(manuscript)
    for name in ('audit.py','REVISION-AND-SOURCES.md','ORIGIN-AND-FUTURE.md'):
        shutil.copyfile(ROOT/name,out/name)
    command=['pandoc',str(out/(STEM+'.md')),'--from=markdown+tex_math_dollars','--pdf-engine=xelatex',
             '-V','mainfont=TeX Gyre Pagella','-V','CJKmainfont=Noto Serif CJK SC','-o',str(out/(STEM+'.pdf'))]
    env=dict(os.environ,SOURCE_DATE_EPOCH='1790035200')
    result=subprocess.run(command,env=env,text=True,capture_output=True)
    (ROOT/'typesetting.log').write_text(result.stdout+result.stderr)
    if result.returncode: raise RuntimeError('PDF typesetting failed; inspect typesetting.log')
    extracted=subprocess.check_output(['pdftotext',str(out/(STEM+'.pdf')),'-'],text=True)
    if len(extracted)<14000 or doi not in extracted or '__VERSION_DOI__' in extracted:
        raise RuntimeError('Searchable PDF content gate failed')
    if 'Missing character:' in result.stderr: raise RuntimeError('Missing glyph reported')
    (out/'citation.bib').write_text('@misc{liu2026claimarchitecturev12,\n  author = {Liu, Hongju},\n  title = {'+TITLE+'},\n  year = {2026},\n  version = {1.2},\n  doi = {'+doi+'},\n  publisher = {Zenodo},\n  note = {TA-TR-2026-14. AI-assisted working paper; not peer reviewed.}\n}\n')
    (out/'citation.csl.json').write_text(json.dumps({'type':'report','id':'TA-TR-2026-14-v1.2','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],
                                                   'issued':{'date-parts':[[2026,9,22]]},'version':'1.2','DOI':doi,'publisher':'Zenodo'},indent=2)+'\n')
    (out/'README-LICENSE.txt').write_text('TA-TR-2026-14 v1.2. '+doi+'\nCC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their rights.\nNot peer reviewed. No global priority or empirical validation is claimed. Substantial GPT-6 Astra Pro assistance is disclosed; Hongju Liu is the human author of record and responsible depositor.\nOld v1.1 DOI '+OLD_DOI+' is preserved. This is a new version, not a new numbered paper and not an amendment to the Trinity Accord.\n')
    build='#!/usr/bin/env bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\npython3 audit.py --out audit-rerun\nSOURCE_DATE_EPOCH=1790035200 pandoc '+STEM+'.md --from=markdown+tex_math_dollars --pdf-engine=xelatex -V "mainfont=TeX Gyre Pagella" -V "CJKmainfont=Noto Serif CJK SC" -o rebuilt.pdf\n'
    (out/'build.sh').write_text(build)
    tools={name:subprocess.check_output([name,'--version'],text=True).splitlines()[0] for name in ('pandoc','xelatex')}
    (out/'REPRODUCIBILITY.md').write_text('# Reproducing the bounded study\n\nRun `python3 audit.py --out audit-rerun` using Python 3.10 or later. No third-party Python packages are required. `checks.json` reports the actual run and `illustration.csv` contains stipulated, uncalibrated examples. Numeric checks are not empirical data or independent peer review.\n\nThe audit uses independently evaluated factor derivatives and numerical market roots in addition to algebraic checks. It does not formally verify the full manuscript.\n\nRun `bash build.sh` with Pandoc, XeLaTeX, TeX Gyre Pagella and Noto Serif CJK SC available to rebuild a searchable PDF from the DOI-bearing Markdown. Binary identity across different toolchains is not promised. Review and cite the deposited exact PDF, not a locally rebuilt file.\n\nObserved build tools:\n\n'+json.dumps(tools,indent=2)+'\n\nThe source Markdown carries the full mathematical equations. No revised file inherits the old v1.1 timestamp. Source and publication receipts remain in the repository version directory.\n')
    names={STEM+'.pdf',STEM+'.md','audit.py','checks.json','illustration.csv','REVISION-AND-SOURCES.md','ORIGIN-AND-FUTURE.md','citation.bib','citation.csl.json','README-LICENSE.txt','REPRODUCIBILITY.md','build.sh','SHA256SUMS.txt'}
    actual={p.name for p in out.iterdir()}
    if actual- names: raise RuntimeError('Unexpected package files')
    (out/'SHA256SUMS.txt').write_text(''.join(digest(p.read_bytes())+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS.txt'))
    rows=[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in sorted(out.iterdir())]
    if {r['name'] for r in rows}!=names: raise RuntimeError('Incomplete package')
    manifest={'report_number':'TA-TR-2026-14','version':VERSION,'title':TITLE,'doi':doi,'record_id':state['record_id'],
              'conceptrecid':state['conceptrecid'],'old_record_id':OLD,'file_count':len(rows),'files':rows,
              'inputs':{n:digest((ROOT/n).read_bytes()) for n in INPUTS},'prepared_from_commit':git('rev-parse','HEAD'),
              'audit_assertions':load('published/checks.json')['assertions'],'peer_reviewed':False}
    save('manifest.json',manifest)
    state['state']='BUILT_AWAITING_EXACT_REVIEW';save('state.json',state);persist()
    print(json.dumps({'state':state['state'],'record_id':state['record_id'],'doi':doi,'conceptrecid':state['conceptrecid'],
                      'manifest_sha256':digest((ROOT/'manifest.json').read_bytes()),'assertions':manifest['audit_assertions']},indent=2))

def validate():
    state=load('state.json'); m=load('manifest.json'); gate=load('review-authorization.json')
    if (state['record_id'],state['doi'],state['version'])!=(m['record_id'],m['doi'],VERSION): raise RuntimeError('State/manifest mismatch')
    if (gate.get('state'),gate.get('record_id'),gate.get('manifest_sha256'))!=('EXACT_PACKAGE_REVIEWED_AND_PUBLICATION_AUTHORIZED',m['record_id'],digest((ROOT/'manifest.json').read_bytes())):
        raise RuntimeError('No exact publication authorization')
    if gate.get('reviewer')!='GPT-6 Astra Pro' or gate.get('independent_peer_review') is not False:
        raise RuntimeError('Review attribution mismatch')
    for n,h in m['inputs'].items():
        if digest((ROOT/n).read_bytes())!=h: raise RuntimeError('Input changed after package build: '+n)
    rows=m['files']; out=ROOT/'published'
    if {p.name for p in out.iterdir()}!={r['name'] for r in rows}: raise RuntimeError('Package inventory changed')
    for row in rows:
        data=(out/row['name']).read_bytes()
        if len(data)!=row['bytes'] or digest(data)!=row['sha256']: raise RuntimeError('Reviewed file changed: '+row['name'])
    if load('published/checks.json')['status']!='PASS': raise RuntimeError('Audit not passed')
    return state,m

def integrate(receipt):
    doi=receipt['doi'];rid=receipt['record_id']
    path=REPO/'research/index.md';text=path.read_text()
    start=text.index('## Claim Architecture Transition\n')
    end=text.index('## Independent External Scholarship\n',start)
    section=f'''## Claim Architecture Transition
{{: #claim-architecture-transition }}

### {TITLE}

TA-TR-2026-14 · Version 1.2 · 22 September 2026. Human originator and responsible depositor: Hongju Liu. Substantial GPT-6 Astra Pro assistance in source comparison, critical revision, modeling, proofs, code and drafting is disclosed. No independent peer review is claimed.

A corrective theoretical working paper comparing household affordability, financing and physical allocation. The new heterogeneous-demand equilibrium solves essential-price feedback and a minimum-support frontier; reference-basket affordability, a chosen service floor and compensated utility remain distinct criteria. The revision corrects v1.1's aggregate-gap population condition and reduces the maximum-exponent result to an elementary lemma. It does not claim to invent entitlements, scarcity-based purchasing-power loss, ownership effects or rent redistribution.

**Status:** Published open-access preprint; exact anonymous public-file readback passed. Same paper and original Zenodo concept, not a fifteenth study. DOI registration is not correctness, peer review or global priority.

- [Version 1.2 DOI: {doi}](https://doi.org/{doi}) · [Zenodo record](https://zenodo.org/records/{rid})
- [English PDF with Chinese abstract](/research/claim-architecture-transition/v1.2/published/{STEM}.pdf) · [Markdown source](/research/claim-architecture-transition/v1.2/published/{STEM}.md)
- [Corrections and primary-source comparison](/research/claim-architecture-transition/v1.2/published/REVISION-AND-SOURCES.md) · [Origin and future revision record](/research/claim-architecture-transition/v1.2/published/ORIGIN-AND-FUTURE.md)
- [Executable audit](/research/claim-architecture-transition/v1.2/published/audit.py) · [Actual check results](/research/claim-architecture-transition/v1.2/published/checks.json) · [Publication receipt](/research/claim-architecture-transition/v1.2/publication-record.json)
- [Preserved v1.1 DOI: {OLD_DOI}](https://doi.org/{OLD_DOI}) · [Unchanged v1.1 PDF](/research/claim-architecture-transition/published/{OLD_PDF})

The prior v1.1 files and timestamp bindings are preserved. A v1.1 OTS proof does not attest to the revised v1.2 bytes; no mature v1.2 Bitcoin/Arweave proof is asserted by this publication entry. The paper remains adjacent first-party, non-amending research and is not independent corroboration of the Trinity Accord.

'''
    path.write_text(text[:start]+section+text[end:])
    path=REPO/'README.md';text=path.read_text()
    old=f'[TA-TR-2026-14 v1.1, The Claim Architecture Transition](https://doi.org/{OLD_DOI})'
    new=f'[TA-TR-2026-14 v1.2, The Claim Architecture Transition](https://doi.org/{doi})'
    if old in text: text=text.replace(old,new,1)
    elif new not in text: raise RuntimeError('README latest-paper locator changed; reconcile')
    path.write_text(text)


def publish():
    state,m=validate();z=client();rid=m['record_id'];doi=m['doi'];names={r['name'] for r in m['files']}
    old_identity(z,state['old_inventory'])
    dep=get(z,f'/deposit/depositions/{rid}');check_child(dep,state['conceptrecid'],rid,True)
    already=bool(dep.get('submitted'))
    if not already:
        existing=get(z,f'/deposit/depositions/{rid}/files')
        old_names=set(state['old_inventory'])
        if any(f.get('filename') not in names|old_names for f in existing): raise RuntimeError('Unexpected child-draft file')
        # Only remove inherited files from the explicitly verified UNPUBLISHED child.
        for f in existing:
            if f['filename'] not in names:
                endpoint=f'https://zenodo.org/api/deposit/depositions/{rid}/files/'+urllib.parse.quote(str(f['id']),safe='')
                request=urllib.request.Request(endpoint,method='DELETE',headers={'Authorization':'Bearer '+z.token})
                with urllib.request.urlopen(request,timeout=120) as answer:
                    if answer.status!=204: raise RuntimeError('Draft-file removal did not confirm 204')
        bucket=dep['links']['bucket']
        p=urllib.parse.urlsplit(bucket)
        if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password or not p.path.startswith('/api/files/'):
            raise RuntimeError('Unexpected child bucket')
        current={f['filename']:f for f in get(z,f'/deposit/depositions/{rid}/files')}
        for row in m['files']:
            data=(ROOT/'published'/row['name']).read_bytes();prev=current.get(row['name'])
            if prev and str(prev.get('checksum','')).removeprefix('md5:')==hashlib.md5(data).hexdigest() and int(prev['filesize'])==len(data): continue
            z.request(bucket+'/'+urllib.parse.quote(row['name'],safe=''),'PUT',data,binary=True)
        remote={f['filename']:f for f in get(z,f'/deposit/depositions/{rid}/files')}
        if set(remote)!=names: raise RuntimeError('Draft inventory differs')
        for row in m['files']:
            data=(ROOT/'published'/row['name']).read_bytes();f=remote[row['name']]
            if int(f['filesize'])!=len(data) or str(f['checksum']).removeprefix('md5:')!=hashlib.md5(data).hexdigest(): raise RuntimeError('Draft bytes differ')
        save('publication-intent.json',{'record_id':rid,'manifest_sha256':digest((ROOT/'manifest.json').read_bytes()),'same_concept':True})
        persist()
        dep=z.request(f'/deposit/depositions/{rid}/actions/publish','POST')
        check_child(dep,state['conceptrecid'],rid,True)
        if not dep.get('submitted'): raise RuntimeError('Submission not confirmed')
    public=get(z,f'/records/{rid}',False)
    if (public.get('id'),public.get('doi'),public.get('metadata',{}).get('version'),public.get('metadata',{}).get('title'))!=(rid,doi,VERSION,TITLE): raise RuntimeError('Public identity differs')
    if str(public.get('conceptrecid'))!=str(state['conceptrecid']): raise RuntimeError('Public concept differs')
    remote={f['key']:f for f in public.get('files',[])}
    if set(remote)!=names: raise RuntimeError('Public inventory differs')
    rows=[]
    for row in m['files']:
        f=remote[row['name']];data=download_public(f['links'].get('self') or f['links']['download'])
        if len(data)!=row['bytes'] or digest(data)!=row['sha256']: raise RuntimeError('Anonymous bytes differ: '+row['name'])
        rows.append(dict(row,anonymous_readback_pass=True))
    old_identity(z,state['old_inventory'])
    resolver={'matches_record':False,'state':'PENDING_OR_UNAVAILABLE'}
    for delay in (0,5,15,30):
        if delay: time.sleep(delay)
        try:
            with urllib.request.urlopen('https://doi.org/'+doi,timeout=20) as r:
                p=urllib.parse.urlsplit(r.url)
                good=r.status==200 and p.hostname=='zenodo.org' and p.path.rstrip('/') in (f'/records/{rid}',f'/record/{rid}')
                resolver={'matches_record':good,'state':'PASS' if good else 'TARGET_MISMATCH','http_status':r.status,'final_url':r.url}
                if good:break
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):pass
    receipt={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS' if resolver['matches_record'] else 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING',
             'report_number':'TA-TR-2026-14','version':VERSION,'title':TITLE,'record_id':rid,'doi':doi,
             'conceptrecid':state['conceptrecid'],'same_concept':True,'prior_doi':OLD_DOI,'prior_public_files_unchanged':True,
             'prior_pdf_sha256_verified':OLD_SHA,'file_count':len(rows),'files':rows,'anonymous_readback':True,
             'doi_resolver':resolver,'was_already_published':already,'manifest_sha256':digest((ROOT/'manifest.json').read_bytes()),
             'source_commit':git('rev-parse','HEAD'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'new_numbered_papers':0,
             'peer_reviewed':False,'global_priority_certified':False,'bitcoin_originals_modified':False,
             'v12_ots_maturity':'NOT_ASSERTED','v12_arweave_preservation':'NOT_ASSERTED'}
    save('publication-record.json',receipt);state['state']=receipt['state'];save('state.json',state)
    integrate(receipt);persist(integrated=True)
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','publish','persist']);args=parser.parse_args()
    if args.mode=='persist': persist()
    elif args.mode=='prepare': prepare()
    else: publish()
