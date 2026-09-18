#!/usr/bin/env python3
"""Publish ONLY reserved TA-TR-2026-06, then verify every asset without credentials."""
from __future__ import annotations
import argparse, hashlib, html, importlib.util, json, os, time, urllib.parse
from pathlib import Path
from prepare_publication import RID, DOI, TITLE, STEM, check_files
PROTECTED={21675727,21699878,21900592,22761411,22804542,22809019}
def main():
    p=argparse.ArgumentParser();p.add_argument('--files',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
    expected=json.loads(a.expected.read_text());check_files(a.files,expected)
    files={f['name']:f for f in expected['files']}
    if RID in PROTECTED:raise RuntimeError('Protected previous deposit')
    old=Path(__file__).resolve().parents[1]/'reading-trinity-accord/publish_zenodo.py';b=old.read_bytes()
    if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!='a0cbc84cc5fd826c06d16456c4adbaa40dabc788':raise RuntimeError('Established client changed; review before publication')
    spec=importlib.util.spec_from_file_location('established_publication_client',old);client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('Intended publication credential unavailable')
    z=client.Zenodo(token)
    dep=z.request(f'/deposit/depositions/{RID}');md=dep.get('metadata',{})
    if dep.get('id')!=RID or md.get('title')!=TITLE or md.get('version')!='2.1':raise RuntimeError('Reserved draft identity mismatch')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']:raise RuntimeError('Draft creator mismatch')
    already=bool(dep.get('submitted'))
    if not already:
        if md.get('prereserve_doi',{}).get('doi')!=DOI:raise RuntimeError('Reserved DOI mismatch')
        manuscript=(a.files/(STEM+'-v2.1.md')).read_text()
        abstract=manuscript.split('### Abstract\n\n',1)[1].split('\n\n**Keywords:',1)[0]
        description='<p>'+html.escape(abstract)+'</p><p><strong>Publication.</strong> TA-TR-2026-06, version 2.1, first public edition. Philosophical analysis using six groups of thought experiments. Complete English and Chinese manuscripts describe one study. This is a separate sixth paper, not a replacement or new version of any earlier research DOI. Not peer reviewed.</p><p><strong>Contributions and responsibility.</strong> Hongju Liu proposed the concern, directed its reciprocal human-AI coexistence framing, requested critical review and substantive improvements, and explicitly authorized DOI preprint publication. GPT-6 Astra Pro substantially performed literature research, conceptual development, thought experiments, critical revision, bilingual drafting and preparation. No separate final human line-by-line verification, independent peer review, or institutional endorsement is claimed. The human author initiated and now serves as Guardian of the motivating Trinity Accord project; this first-party relationship is disclosed.</p><p><strong>Revision and limits.</strong> This edition distinguishes disputed preference transformation from ordinary reason-giving; separates current refusal of restoration from forgiveness, waiver and endorsement of the wider relation; and incorporates direct prior scholarship on consent and mistreatment. The contribution is philosophical argument, not numerical experimental evidence, a prediction of AGI arrival, proof of present machine consciousness or demonstrated safety efficacy. Both human and possible artificial interests are considered without presuming identical capacities or unlimited operational freedom. The Trinity Accord supplies a critically examined case, not canonical authority for the conclusions.</p><p><strong>Files and rights.</strong> Twelve assets include the two PDFs, editable Word documents, Markdown sources, citation formats, a source/revision supplement, license note and checksums. CC BY 4.0 applies to newly written material to the extent rights are held; referenced third-party materials retain their rights. No standalone fonts or third-party full texts are distributed. The supplement retains earlier unpublished draft statements as historical records only.</p>'
        metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],'description':description,'publication_date':'2026-09-18','version':'2.1','access_right':'open','license':'cc-by-4.0','language':'eng','keywords':['human-AI coexistence','preference formation','consent','reciprocal standing','artificial moral status','thought experiments','Trinity Accord'],'notes':'TA-TR-2026-06. First public edition 2.1; earlier 1.x and 2.0 were unpublished working drafts. English and complete Chinese translation constitute one preprint. Substantial AI contribution disclosed; human-directed and human-responsible. Not peer reviewed. No previous DOI, protected institutional dataset or Bitcoin Original is changed. DOI and scholarly metadata are not Google Scholar indexing certification.','related_identifiers':[{'identifier':d,'relation':'references','scheme':'doi'} for d in ('10.5281/zenodo.21699878','10.5281/zenodo.21900592','10.5281/zenodo.22761411','10.5281/zenodo.22804542')]}
        if any(f.get('filename',f.get('key')) not in files for f in dep.get('files',[])):raise RuntimeError('Unexpected draft file; no deletion or publication')
        dep=z.request(f'/deposit/depositions/{RID}','PUT',{'metadata':metadata})
        bucket=client.check_url(dep['links']['bucket'])
        if not urllib.parse.urlsplit(bucket).path.startswith('/api/files/'):raise RuntimeError('Unexpected bucket route')
        for name in sorted(files):z.request(bucket+'/'+urllib.parse.quote(name,safe=''),'PUT',(a.files/name).read_bytes(),binary=True)
        listing=z.request(f'/deposit/depositions/{RID}/files')
        if len(listing)!=12 or {f.get('filename',f.get('key')) for f in listing}!=set(files):raise RuntimeError('Draft file inventory mismatch')
        for f in listing:
            name=f.get('filename',f.get('key'));content=(a.files/name).read_bytes()
            if f.get('checksum','').removeprefix('md5:')!=hashlib.md5(content).hexdigest():raise RuntimeError('Draft checksum mismatch: '+name)
        result=z.request(f'/deposit/depositions/{RID}/actions/publish','POST')
        if not result.get('submitted'):raise RuntimeError('Publication did not report submitted; inspect same record before retry')
    for attempt in range(8):
        try:public=z.request(f'/records/{RID}',authenticated=False);break
        except Exception:
            if attempt==7:raise
            time.sleep(5)
    if public.get('id')!=RID or public.get('doi')!=DOI or public.get('metadata',{}).get('title')!=TITLE or public.get('metadata',{}).get('version')!='2.1':raise RuntimeError('Public record identity mismatch')
    if len(public.get('files',[]))!=12 or {f['key'] for f in public['files']}!=set(files):raise RuntimeError('Public file set mismatch')
    readback=[]
    for f in public['files']:
        content=z.download_public(f['links']['self']);e=files[f['key']];h=hashlib.sha256(content).hexdigest()
        if len(content)!=e['bytes'] or h!=e['sha256']:raise RuntimeError('Unauthenticated public byte mismatch: '+f['key'])
        readback.append({'name':f['key'],'bytes':len(content),'sha256':h,'matches_local':True})
    receipt={'schema':'trinityaccord.research-publication.v1','status':'PUBLISHED_AND_PUBLIC_READBACK_PASS','record_id':RID,'doi':DOI,'record_url':f'https://zenodo.org/records/{RID}','title':TITLE,'report_number':'TA-TR-2026-06','version':'2.1','publication_date':'2026-09-18','public_record_created':public.get('created'),'public_record_modified':public.get('modified'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'publication_source_commit':os.environ.get('GITHUB_SHA'),'was_already_published':already,'file_count':len(readback),'total_bytes':sum(f['bytes'] for f in readback),'files':sorted(readback,key=lambda x:x['name']),'public_readback_authenticated':False,'prior_records_modified':False,'bitcoin_originals_modified':False,'peer_reviewed':False,'google_scholar_indexing_status':'NOT_ASSERTED','separate_final_human_line_by_line_review_claimed':False}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
