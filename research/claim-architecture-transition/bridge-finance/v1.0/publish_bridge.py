#!/usr/bin/env python3
"""Publish this authorized Parts I-II release only. No old records are edited.
Uses the repository's existing Zenodo client and paper OTS lifecycle.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time, urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
BRANCH='research/intelligence-explosion-economy-20260922'
BASE='f4c11376c3b84d4e4990ec29228f5c5888c7cf82'
REL=str(ROOT.relative_to(REPO))
PUB=ROOT/'published'
TITLE='Financing the Automation Transition Without Pledging Subsistence: Public Upside Claims, Prosperity Tiers, and Bounded Real Returns'
REPORT='TA-TR-2026-14-BRIDGE'
VERSION='1.0'
BATCH=REPO/'research/paper-timestamps/2026-09-22-abundance-bridge-v10'
SOURCE1='research/claim-architecture-transition/bridge-finance/v1.0-rc1/manuscript.md'
SOURCE2='research/claim-architecture-transition/bridge-finance/part-ii/PROSPERITY-TIERS-AND-BOUNDED-REAL-CLAIMS-20260922.md'
VERIFY='research/claim-architecture-transition/bridge-finance/v1.0-rc1/verify.py'
EXPECTED_BLOBS={SOURCE1:'b103b7c2e380bfecc45771b560dc7f5f049d964f',SOURCE2:'f900eafac2f9f6aed1f61eb7f5710a66d2942181',VERIFY:'0a10767113a591c2b875b58fa961bc340fc2727c'}


def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def checkpoint(message,paths=None):
    if os.environ.get('GITHUB_ACTIONS')!='true': return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    allowed=paths or [REL]
    subprocess.run(['git','add','--',*allowed],cwd=REPO,check=True)
    staged=git('diff','--cached','--name-only').splitlines()
    if any(not any(p==a or p.startswith(a+'/') for a in allowed) for p in staged):raise RuntimeError('Unexpected staged file')
    if staged:
        subprocess.run(['git','commit','-m',message+' [skip ci]'],cwd=REPO,check=True)
        for _ in range(3):
            if subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO).returncode==0:return
            subprocess.run(['git','fetch','origin',BRANCH],cwd=REPO,check=True)
            if subprocess.run(['git','rebase','origin/'+BRANCH],cwd=REPO).returncode:
                subprocess.run(['git','rebase','--abort'],cwd=REPO)
                raise RuntimeError('Concurrent change requires reconciliation; artifacts retained')
        raise RuntimeError('Checkpoint push failed; reconcile exact artifacts before retry')
def zclient():
    sys.path.insert(0,str(REPO/'research/claim-architecture-transition'))
    from publication_common import client
    return client()
def get(z,path,public=False):
    for n,delay in enumerate([0,3,8,15]):
        if delay:time.sleep(delay)
        try:return z.request(path,authenticated=not public)
        except Exception:
            if n==3:raise

def metadata():
    return {'upload_type':'publication','publication_type':'preprint','title':TITLE,
      'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher'}],
      'description':'<p>This working-paper release contains two parts. Part I derives conditional public-upside financing prices, least-cost payout schedules and investment-preserving bounds. Part II develops prosperity-contingent tiers and bounded real-resource or service claims, with explicit protection of funded basic uses.</p><p>Hongju Liu proposed borrowing against a potentially abundant future to support present basic needs, and requested prosperity-dependent repayments and analysis of future real returns. AI materially assisted with research, formalization, proofs, deterministic checks and drafting. The release is not externally peer reviewed, does not certify foundational priority or top-journal acceptance, and is not a securities offering, investment recommendation or proof that issuance reverses contraction.</p><p>This is a separate bridge-finance extension of TA-TR-2026-14, not a replacement of any earlier DOI edition. Part I and Part II retain distinct scopes: the second part is a design proposal with bounded examples, not a solved economy-wide equilibrium. Sources and verification materials are included. No Trinity Accord canonical text is amended.</p>',
      'publication_date':'2026-09-22','version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
      'keywords':['automation transition','public finance','state-contingent claims','subsistence protection','prosperity','real-resource claims','AI-assisted research'],
      'notes':'TA-TR-2026-14-BRIDGE, v1.0. English Part I and Chinese Part II; mathematical and synthetic examples, not empirical policy estimates. DOI, timestamps and archival receipts are provenance, not truth, authorship or peer-review certifications.'}

def identity(dep):
    md=dep.get('metadata',{});rid=dep.get('id')
    if type(rid)is not int or rid<=0 or (md.get('title'),str(md.get('version')))!=(TITLE,VERSION):raise RuntimeError('Unrelated record identity')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']:raise RuntimeError('Creator mismatch')
    doi=dep.get('doi') or md.get('prereserve_doi',{}).get('doi') or md.get('doi')
    if doi!=f'10.5281/zenodo.{rid}':raise RuntimeError('Unexpected DOI')
    return rid,doi

def reserve():
    z=zclient();p=ROOT/'deposit.json'
    if p.exists():
        saved=read(p);dep=get(z,f"/deposit/depositions/{saved['record_id']}")
        rid,doi=identity(dep)
        if (rid,doi)!=(saved['record_id'],saved['doi']):raise RuntimeError('Reservation mismatch')
    else:
        rows=get(z,'/deposit/depositions?'+urllib.parse.urlencode({'q':'"Financing the Automation Transition"','size':100}))
        if not isinstance(rows,list) or len(rows)>=100:raise RuntimeError('Ambiguous deposit search')
        matches=[d for d in rows if d.get('metadata',{}).get('title','').startswith('Financing the Automation Transition Without Pledging Subsistence')]
        if len(matches)>1:raise RuntimeError('Multiple bridge records; reconcile without creating another')
        if matches:dep=matches[0];identity(dep)
        else:
            if (ROOT/'create-intent.json').exists():raise RuntimeError('Unresolved creation intent: do not create again')
            write(ROOT/'create-intent.json',{'state':'CREATE_ONCE_INTENT','title':TITLE,'version':VERSION,'run_id':os.environ.get('GITHUB_RUN_ID')})
            checkpoint('release: preserve bridge creation intent before Zenodo POST')
            dep=z.request('/deposit/depositions','POST',{'metadata':metadata()})
        rid,doi=identity(dep)
        write(p,{'record_id':rid,'doi':doi,'title':TITLE,'version':VERSION,'report_number':REPORT,'concept_record_id':dep.get('conceptrecid'),'submitted':bool(dep.get('submitted'))})
        checkpoint('release: preserve single reserved bridge DOI')
    print(json.dumps(read(p),ensure_ascii=False,indent=2))

def source(path):
    b=subprocess.check_output(['git','show',BASE+':'+path],cwd=REPO)
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if blob!=EXPECTED_BLOBS[path]:raise RuntimeError('Reviewed source changed: '+path)
    return b

def build():
    dep=read(ROOT/'deposit.json');doi=dep['doi']
    if (ROOT/'EXPECTED-PUBLICATION.json').exists():
        validate();print('Using frozen package; no PDF rebuild');return
    PUB.mkdir(parents=True,exist_ok=True)
    first=source(SOURCE1).decode().replace('v1.0-rc1','v1.0')
    old=first.split('**Status.** ',1)[1].split('\n\n',1)[0]
    first=first.replace(old,'Part I of working-paper release v1.0. Not externally peer reviewed. DOI: '+doi+'. No journal acceptance, foundational-priority certification or securities offering is claimed. This release does not replace earlier TA-TR-2026-14 publications.',1)
    (PUB/'Part-I-Financing-Automation-v1.0.md').write_text(first)
    second=source(SOURCE2).decode()
    second='## 1. 第一、二部分的分工'+second.split('## 1. 第一、二部分的分工',1)[1]
    second=second.split('## 执行事实',1)[0]
    second=second.replace('第一部分复核见PART-I-PRESERVATION-AUDIT-20260922.md。','第一部分已作最终条件性复核；原v1.0-rc1保留，正式发布版仅更新版本和出处标识。')
    # xeCJK supplies Chinese layout. Legacy Pandoc 2.9 does not map zh-CN
    # to a valid polyglossia language; omit that optional LaTeX metadata.
    header='''---
title: "第二部分：丰裕分层与有限真实收益权"
subtitle: "自动化转型融资的制度设计与条件性扩展"
author: "Hongju Liu（刘烘炬）"
date: "2026年9月22日 · 工作论文 v1.0"
mainfont: Liberation Serif
CJKmainfont: Noto Serif CJK SC
fontsize: 11pt
geometry: margin=23mm
linestretch: 1.15
header-includes:
  - '\\usepackage{amsmath,amssymb,booktabs}'
  - '\\setlength{\\emergencystretch}{3em}'
---

'''
    notice='**出版说明。** 本文与英文第一部分作为同一工作论文v1.0发布。DOI：`'+doi+'`。原始方向由刘烘炬提出，研究、论证、核查及文字由AI实质协助。第二部分是制度设计与条件性扩展，不是已证实的宏观政策；无独立同行评审，不声称奠基性优先权，也不是证券或投资建议。旧稿不覆盖，三位一体协定正典不修改。\n\n'
    (PUB/'Part-II-Prosperity-Real-Claims-zh-v1.0.md').write_text(header+notice+second)
    (PUB/'verify.py').write_bytes(source(VERIFY))
    subprocess.run([sys.executable,str(PUB/'verify.py')],cwd=PUB,check=True)
    (PUB/'requirements.txt').write_text('numpy==2.2.6\nscipy==1.15.3\n')
    for stem in ['Part-I-Financing-Automation-v1.0','Part-II-Prosperity-Real-Claims-zh-v1.0']:
        subprocess.run(['pandoc',str(PUB/(stem+'.md')),'--standalone','--pdf-engine=xelatex','-o',str(PUB/(stem+'.pdf'))],cwd=PUB,check=True)
    (PUB/'README.txt').write_text(TITLE+'\nHongju Liu | v1.0 | 2026-09-22\nDOI: '+doi+'\n\nPart I is the conditional financial benchmark. Part II is a Chinese design extension with bounded real-resource examples. Sources are included. Not peer reviewed; not an investment instrument. Prior reports and canonical works are not amended.\n\nThe reviewed rc1 and research-v0.1 remain in repository history. Final PDFs are typeset from the reviewed frozen repository sources; only release metadata and historical-status wording are editorially updated.\n\nLicense: CC BY 4.0 for newly authored text and verification materials to the extent held by the depositor; third-party works are not relicensed.\n\nOTS and Arweave evidence are generated after anonymous Zenodo readback and are kept separately so published payload bytes do not change. Timestamp receipt acceptance is not Bitcoin confirmation.\n')
    (PUB/'citation.bib').write_text('@misc{liu2026abundancebridge,\n author={Liu, Hongju},\n title={'+TITLE+'},\n year={2026},\n publisher={Zenodo},\n doi={'+doi+'},\n version={1.0}\n}\n')
    write(PUB/'PROVENANCE.json',{'reviewed_source_commit':BASE,'source_git_blobs':EXPECTED_BLOBS,'report_number':REPORT,'doi':doi,'version':VERSION,'external_peer_review':False,'canonical':False,'source_of_original_proposal':'Hongju Liu','substantial_ai_assistance':True,'prior_records_modified':False})
    write(PUB/'FINAL-REVIEW.json',{'state':'CONDITIONAL_WORKING_PAPER_REVIEW_PASS','local_review':'74 original plus 13 extension checks passed; original archive hashes matched','runner_original_checks':read(PUB/'checks.json')['counts'],'not_empirical_validation':True,'not_external_peer_review':True})
    files=[]
    for p in sorted(PUB.iterdir()):
        if p.is_file():files.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
    (PUB/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['name']}\n" for f in files))
    p=PUB/'SHA256SUMS.txt';files.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
    write(ROOT/'EXPECTED-PUBLICATION.json',{**dep,'file_count':len(files),'files':files})
    checkpoint('release: freeze reviewed-source bridge v1.0 files and exact hashes')
    print('FROZEN_MANIFEST_SHA256',sha((ROOT/'EXPECTED-PUBLICATION.json').read_bytes()))

def validate():
    e=read(ROOT/'EXPECTED-PUBLICATION.json');d=read(ROOT/'deposit.json')
    if (e['title'],e['version'],e['record_id'],e['doi'])!=(TITLE,VERSION,d['record_id'],d['doi']):raise RuntimeError('Package identity')
    if {p.name for p in PUB.iterdir() if p.is_file()}!={f['name'] for f in e['files']}:raise RuntimeError('Package inventory')
    for f in e['files']:
        p=PUB/f['name'];b=p.read_bytes()
        if p.name!=f['name'] or p.is_symlink() or len(b)!=f['bytes'] or sha(b)!=f['sha256']:raise RuntimeError('Frozen bytes changed')
    return e

def publish():
    e=validate();auth=read(ROOT/'PUBLISH-AUTHORIZATION.json')
    if auth.get('expected_manifest_sha256')!=sha((ROOT/'EXPECTED-PUBLICATION.json').read_bytes()) or auth.get('authorization')!='PUBLISH_EXACT_REVIEWED_PACKAGE':raise RuntimeError('Missing exact-byte authorization')
    z=zclient();rid=e['record_id'];dep=get(z,f'/deposit/depositions/{rid}');identity(dep)
    if not dep.get('submitted'):
        remote=get(z,f'/deposit/depositions/{rid}/files')
        if any(f.get('filename',f.get('key')) not in {r['name'] for r in e['files']} for f in remote):raise RuntimeError('Unexpected draft assets; no deletion permitted')
        for f in e['files']:
            b=(PUB/f['name']).read_bytes()
            z.request(dep['links']['bucket']+'/'+urllib.parse.quote(f['name'],safe=''),'PUT',b,binary=True)
        listing=get(z,f'/deposit/depositions/{rid}/files')
        if {f.get('filename',f.get('key')) for f in listing}!={f['name'] for f in e['files']}:raise RuntimeError('Draft inventory mismatch')
        for f in listing:
            name=f.get('filename',f.get('key'));md5=hashlib.md5((PUB/name).read_bytes()).hexdigest()
            if f.get('checksum','').removeprefix('md5:')!=md5:raise RuntimeError('Draft checksum mismatch')
        write(ROOT/'publish-intent.json',{'state':'EXACT_PACKAGE_UPLOAD_VERIFIED_PUBLISH_INTENT','record_id':rid,'manifest_sha256':sha((ROOT/'EXPECTED-PUBLICATION.json').read_bytes())})
        checkpoint('release: checkpoint verified bridge uploads before public publication')
        result=z.request(f'/deposit/depositions/{rid}/actions/publish','POST')
        if not result.get('submitted'):raise RuntimeError('No submitted confirmation')
    public=get(z,f'/records/{rid}',public=True)
    if public.get('doi')!=e['doi'] or public.get('metadata',{}).get('title')!=TITLE or str(public.get('metadata',{}).get('version'))!=VERSION:raise RuntimeError('Public metadata mismatch')
    if {f['key'] for f in public['files']}!={f['name'] for f in e['files']}:raise RuntimeError('Public inventory mismatch')
    expected={f['name']:f for f in e['files']};verified=[]
    sys.path.insert(0,str(REPO/'research/claim-architecture-transition'))
    from publication_common import download_public
    for f in public['files']:
        b=download_public(f['links']['self']);v=expected[f['key']]
        if len(b)!=v['bytes'] or sha(b)!=v['sha256']:raise RuntimeError('Anonymous public byte mismatch')
        verified.append({**v,'matches_local':True,'url':f['links']['self']})
    receipt={'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS','report_number':REPORT,'record_id':rid,'doi':e['doi'],'concept_doi':public.get('conceptdoi'),'title':TITLE,'version':VERSION,'submitted':True,'public_file_readback_pass':True,'files':verified,'file_count':len(verified),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'prior_records_modified':False,'peer_reviewed':False}
    write(ROOT/'publication-record.json',receipt)
    paper={'report':REPORT,'record_id':rid,'doi':e['doi'],'version':VERSION,'title':TITLE,'receipt_path':REL+'/publication-record.json','pdfs':[{k:f[k] for k in ('name','bytes','sha256')} for f in verified if f['name'].endswith('.pdf')]}
    write(BATCH/'targets.json',{'batch':BATCH.name,'paper_count':1,'papers':[paper]})
    checkpoint('release: confirm public bridge DOI bytes and create isolated OTS targets',[REL,str(BATCH.relative_to(REPO))])
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','publish','validate']);a=p.parse_args()
    try:
        if a.action=='prepare':reserve();build()
        elif a.action=='publish':publish()
        else:print(json.dumps(validate(),indent=2))
    except Exception as exc:
        write(ROOT/'last-attempt.json',{'action':a.action,'state':'INCOMPLETE_RECONCILE_SAME_RECORD','error_type':type(exc).__name__,'error':str(exc),'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        raise
