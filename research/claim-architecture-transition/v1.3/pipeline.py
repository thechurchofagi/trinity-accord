#!/usr/bin/env python3
"""v1.3 parameter adapter for the hash-pinned, guarded v1.2 publisher.
Reuse same-concept reservation, review/hash gates, upload and public readback.
Never modify a prior public edition. No standalone workflow is introduced.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
BRANCH='research/claim-architecture-transition-v1-3-20260922'
BASE=ROOT.parent/'v1.2'/'pipeline.py'
raw=BASE.read_bytes()
if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!='aeee6147c7419b86846a0bb20eea9b15029cd1f4':
    raise RuntimeError('Established publisher changed; review before reuse')
spec=importlib.util.spec_from_file_location('ta14_guarded_publisher',BASE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
core.ROOT=ROOT;core.REPO=REPO;core.BRANCH=BRANCH
core.OLD=22885976;core.OLD_DOI='10.5281/zenodo.22885976'
core.OLD_PDF='claim-architecture-transition-v1.2.pdf'
core.OLD_SHA='70c3ecaa00632ee4040abe28c3732d9c2b2230a8f2b112e712bf71f078722bfd'
core.VERSION='1.3';core.DATE='2026-09-22'
core.TITLE='The Claim Architecture Transition: An Inverse Access Frontier Beyond Fixed Expenditure Shares'
core.STEM='claim-architecture-transition-v1.3'
core.INPUTS=('manuscript.md','audit.py','symbolic_check.py','REVISION-AND-SOURCES.md','ORIGIN-AND-FUTURE.md','pipeline.py')

def save(name,value):
    # Do not carry predecessor-specific receipt labels into a new edition.
    if name=='publication-record.json':
        value=dict(value)
        for old,new in [('v12_ots_maturity','v13_ots_maturity'),('v12_arweave_preservation','v13_arweave_preservation')]:
            if old in value: value[new]=value.pop(old)
        value['publication_adapter']='v1.3, reusing hash-pinned v1.2 publisher'
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
core.save=save

def persist(integrated=False):
    paths=[str(p.relative_to(REPO)) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if integrated: paths+=['research/index.md','README.md']
    for k,v in [('user.name','github-actions[bot]'),('user.email','41898282+github-actions[bot]@users.noreply.github.com')]:
        subprocess.run(['git','config',k,v],cwd=REPO,check=True)
    subprocess.run(['git','add','-f','--',*paths],cwd=REPO,check=True)
    staged=core.git('diff','--cached','--name-only').splitlines()
    if not set(staged)<=set(paths): raise RuntimeError('Unexpected staged path')
    if staged:
        subprocess.run(['git','commit','-m','research(TA14): checkpoint v1.3 package and state [skip ci]'],cwd=REPO,check=True)
        subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)
core.persist=persist

def old_identity(z,baseline=None):
    p=core.get(z,f'/records/{core.OLD}',False)
    md=p.get('metadata',{})
    if (p.get('id'),p.get('doi'),md.get('version'),str(p.get('conceptrecid')))!=(22885976,core.OLD_DOI,'1.2','22871208'):
        raise RuntimeError('Predecessor identity mismatch')
    if not md.get('title','').startswith('The Claim Architecture Transition:'): raise RuntimeError('Wrong predecessor title')
    inv=core.inventory(p)
    if len(inv)!=13 or core.OLD_PDF not in inv: raise RuntimeError('Predecessor inventory mismatch')
    if baseline is not None and inv!=baseline: raise RuntimeError('Predecessor inventory changed')
    f=next(f for f in p['files'] if f['key']==core.OLD_PDF)
    if core.digest(core.download_public(f['links'].get('self') or f['links']['download']))!=core.OLD_SHA:
        raise RuntimeError('Predecessor PDF changed')
    return p,inv
core.old_identity=old_identity

def check_child(dep,concept,rid=None,final=False):
    did=dep.get('id');md=dep.get('metadata',{})
    if type(did) is not int or did<=0 or did in (22871209,22885976): raise RuntimeError('Not a separate child')
    if str(concept)!='22871208' or str(dep.get('conceptrecid'))!=str(concept): raise RuntimeError('Wrong concept')
    if rid is not None and did!=rid: raise RuntimeError('Wrong child record')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']: raise RuntimeError('Wrong creator')
    if final:
        if (md.get('title'),md.get('version'))!=(core.TITLE,'1.3'): raise RuntimeError('Wrong child metadata')
    else:
        titles={core.TITLE,'The Claim Architecture Transition: Real Claims, Endogenous Essential Prices, and Budget-Feasible Support'}
        if md.get('title') not in titles or md.get('version') not in (None,'','1.2','1.3'): raise RuntimeError('Ambiguous child')
        if md.get('version') in (None,'') and dep.get('submitted'): raise RuntimeError('Unlabeled public child')
    return did
core.check_child=check_child

def metadata():
    desc=('TA-TR-2026-14 v1.3, a substantive revision in original concept 22871208. '
      'An inverse access frontier for a two-group, two-good homothetic economy gives the disposable-income share needed for a physical service target. '
      'Power-law consumption-ratio tails yield zero, interior or unit limiting shares. '
      'A finite-labor sufficient condition and an exact three-equilibrium counterexample distinguish target implementation from a guarantee. '
      'Candidate incremental contribution using standard methods; not a new general economic paradigm. '
      'Synthetic numerical checks and optional symbolic identities are not empirical validation or independent replication.')
    note=('Hongju Liu initiated the motivating concern, directed the work and authorized open deposit. GPT-6 Astra Pro substantially assisted source comparison, modeling, proofs, counterexamples, code, review and writing. '
      'No final human line-by-line or external peer review is claimed. Earlier editions remain unchanged and newer results are not backdated. '
      'Adjacent first-party research, not Canon, amendment or independent corroboration of the Trinity Accord. DOI registration is not correctness, global priority or guaranteed future importance.')
    return {'upload_type':'publication','publication_type':'preprint','title':core.TITLE,
      'creators':[{'name':'Liu, Hongju'}],'description':'<p>'+html.escape(desc)+'</p><p>'+html.escape(note)+'</p>',
      'publication_date':core.DATE,'version':'1.3','access_right':'open','license':'cc-by-4.0','language':'eng','prereserve_doi':True,
      'keywords':['automation','resource access','homothetic demand','income distribution','equilibrium multiplicity','AI-assisted research'],
      'notes':note}
core.metadata=metadata

def prepare():
    if (ROOT/'review-authorization.json').exists(): raise RuntimeError('Reviewed package locked')
    out=ROOT/'published';out.mkdir(exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'audit.py'),'--out',str(out)],check=True)
    symbolic=subprocess.check_output([sys.executable,str(ROOT/'symbolic_check.py')],text=True)
    if json.loads(symbolic)['status']!='PASS': raise RuntimeError('Symbolic check failed')
    (out/'symbolic-checks.json').write_text(symbolic)
    dep,state=core.reserve(core.client())
    if dep.get('submitted'): raise RuntimeError('Already published; do not rebuild')
    source=(ROOT/'manuscript.md').read_text()
    if source.count('__VERSION_DOI__')!=1: raise RuntimeError('DOI substitution marker mismatch')
    (out/(core.STEM+'.md')).write_text(source.replace('__VERSION_DOI__',state['doi']))
    for n in core.INPUTS:
        if n not in ('pipeline.py','manuscript.md'): shutil.copyfile(ROOT/n,out/n)
    cmd=['pandoc',str(out/(core.STEM+'.md')),'--from=markdown+tex_math_dollars','--pdf-engine=xelatex',
         '-V','mainfont=TeX Gyre Pagella','-V','CJKmainfont=Noto Serif CJK SC','-o',str(out/(core.STEM+'.pdf'))]
    result=subprocess.run(cmd,text=True,capture_output=True,env=dict(os.environ,SOURCE_DATE_EPOCH='1790035200'))
    (ROOT/'typesetting.log').write_text(result.stdout+result.stderr)
    if result.returncode or 'Missing character:' in result.stderr: raise RuntimeError('PDF typesetting failed')
    text=subprocess.check_output(['pdftotext',str(out/(core.STEM+'.pdf')),'-'],text=True)
    if state['doi'] not in text or len(text)<16000 or '__VERSION_DOI__' in text: raise RuntimeError('Searchable PDF gate failed')
    (out/'citation.bib').write_text('@misc{liu2026claimarchitecturev13,\n author={Liu, Hongju},\n title={'+core.TITLE+'},\n year={2026},\n version={1.3},\n doi={'+state['doi']+'},\n publisher={Zenodo},\n note={TA-TR-2026-14. AI-assisted working paper, not peer reviewed.}\n}\n')
    (out/'citation.csl.json').write_text(json.dumps({'type':'report','id':'TA-TR-2026-14-v1.3','title':core.TITLE,'author':[{'family':'Liu','given':'Hongju'}],
      'issued':{'date-parts':[[2026,9,22]]},'version':'1.3','DOI':state['doi'],'publisher':'Zenodo'},indent=2)+'\n')
    (out/'README-LICENSE.txt').write_text('TA-TR-2026-14 v1.3. '+state['doi']+'\nCC BY 4.0 applies to newly written material to the extent rights are held; cited third-party works retain their rights.\nSubstantial GPT-6 Astra Pro assistance; Hongju Liu is the human author of record and responsible depositor. Not peer reviewed. No global priority, empirical validation or universal correctness is claimed. Prior versions and Bitcoin Originals remain unchanged.\n')
    (out/'REPRODUCIBILITY.md').write_text('# Reproduce the bounded study\n\nRun `python3 audit.py --out rerun` with Python 3.10 or later; only the standard library is needed. Run `python3 symbolic_check.py` with SymPy 1.14.0 for optional exact derivative checks. Both are internal checks, not independent replication. Synthetic regimes.csv is not empirical data.\n\nBuild the DOI-bearing Markdown with Pandoc and XeLaTeX using TeX Gyre Pagella and Noto Serif CJK SC. `build.sh` gives the command. Binary identity across toolchains is not promised; cite the deposited exact PDF.\n\nThe repository version directory contains the hash-bound review gate and public-readback receipt. No v1.1/v1.2 timestamp is reused to attest to v1.3.\n')
    (out/'build.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\npython3 audit.py --out rerun\nSOURCE_DATE_EPOCH=1790035200 pandoc '+core.STEM+'.md --from=markdown+tex_math_dollars --pdf-engine=xelatex -V "mainfont=TeX Gyre Pagella" -V "CJKmainfont=Noto Serif CJK SC" -o rebuilt.pdf\n')
    names={core.STEM+'.md',core.STEM+'.pdf','audit.py','symbolic_check.py','checks.json','symbolic-checks.json','regimes.csv',
      'REVISION-AND-SOURCES.md','ORIGIN-AND-FUTURE.md','citation.bib','citation.csl.json','README-LICENSE.txt','REPRODUCIBILITY.md','build.sh','SHA256SUMS.txt'}
    if {p.name for p in out.iterdir()}-names: raise RuntimeError('Unexpected package asset')
    (out/'SHA256SUMS.txt').write_text(''.join(core.digest(p.read_bytes())+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS.txt'))
    rows=[{'name':p.name,'bytes':p.stat().st_size,'sha256':core.digest(p.read_bytes())} for p in sorted(out.iterdir())]
    if {r['name'] for r in rows}!=names: raise RuntimeError('Incomplete package')
    save('manifest.json',{'report_number':'TA-TR-2026-14','version':'1.3','title':core.TITLE,'doi':state['doi'],'record_id':state['record_id'],
      'conceptrecid':'22871208','old_record_id':22885976,'file_count':len(rows),'files':rows,
      'inputs':{n:core.digest((ROOT/n).read_bytes()) for n in core.INPUTS},'prepared_from_commit':core.git('rev-parse','HEAD'),
      'audit_assertions':core.load('published/checks.json')['assertions'],'peer_reviewed':False})
    state['state']='BUILT_AWAITING_EXACT_REVIEW';save('state.json',state);persist()
    print(json.dumps({'state':state['state'],'doi':state['doi'],'manifest_sha256':core.digest((ROOT/'manifest.json').read_bytes())},indent=2))

def integrate(receipt):
    if receipt['state']!='PUBLISHED_AND_PUBLIC_READBACK_PASS': return
    path=REPO/'research/index.md';text=path.read_text()
    start=text.index('## Claim Architecture Transition\n');end=text.index('## Independent External Scholarship\n',start)
    doi=receipt['doi'];rid=receipt['record_id'];base='/research/claim-architecture-transition/v1.3/'
    section=f"""## Claim Architecture Transition
{{: #claim-architecture-transition }}

### {core.TITLE}

TA-TR-2026-14 · Version 1.3 · 22 September 2026. Human originator and responsible depositor: Hongju Liu. Substantial GPT-6 Astra Pro assistance with literature, models, proofs, counterexamples, code, review and writing is disclosed. No external peer review is claimed.

A bounded theoretical working paper deriving an inverse access frontier beyond fixed expenditure shares, a zero/interior/one demand-tail classification, and an explicit finite-labor equilibrium-selection counterexample. It preserves earlier corrections and recovers the v1.2 Cobb–Douglas result as a special case. Candidate incremental originality, not a new general economic paradigm or a claim that future models must cite this work.

**Status:** Published open-access preprint; exact anonymous public-file readback passed. Same paper and original concept: fourteen papers remain fourteen. DOI registration is not correctness, peer review or global priority.

- [Version 1.3 DOI: {doi}](https://doi.org/{doi}) · [Zenodo record](https://zenodo.org/records/{rid})
- [English PDF with Chinese abstract]({base}published/claim-architecture-transition-v1.3.pdf) · [Markdown]({base}published/claim-architecture-transition-v1.3.md)
- [Corrections and source comparison]({base}published/REVISION-AND-SOURCES.md) · [Origin and future revision]({base}published/ORIGIN-AND-FUTURE.md)
- [Executable audit]({base}published/audit.py) · [Actual checks]({base}published/checks.json) · [Publication receipt]({base}publication-record.json)
- [Preserved v1.2 DOI: 10.5281/zenodo.22885976](https://doi.org/10.5281/zenodo.22885976) · [Preserved v1.1 DOI: 10.5281/zenodo.22871209](https://doi.org/10.5281/zenodo.22871209)

Earlier public files and their version-specific proofs are unchanged. No mature v1.3 OTS or Arweave attestation is asserted. This is adjacent first-party research, not Canon, an amendment, or independent corroboration of the Trinity Accord.

"""
    path.write_text(text[:start]+section+text[end:])
    path=REPO/'README.md';text=path.read_text()
    old='[TA-TR-2026-14 v1.2, The Claim Architecture Transition](https://doi.org/10.5281/zenodo.22885976)'
    new='[TA-TR-2026-14 v1.3, The Claim Architecture Transition](https://doi.org/'+doi+')'
    if old in text:text=text.replace(old,new,1)
    elif new not in text:raise RuntimeError('README latest-paper locator changed')
    path.write_text(text)
core.integrate=integrate

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','publish','persist']);a=p.parse_args()
    if a.mode=='prepare':prepare()
    elif a.mode=='publish':core.publish()
    else:persist()
