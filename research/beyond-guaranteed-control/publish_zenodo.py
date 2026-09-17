#!/usr/bin/env python3
"""Reuse the established Zenodo client; publish ONLY the reserved fourth paper."""
from __future__ import annotations
import argparse, hashlib, html, importlib.util, json, os, time, urllib.parse
from pathlib import Path
from prepare_publication import DOI, RID, TITLE, REPORT, STEM, jdump

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--files',type=Path,required=True);ap.add_argument('--expected',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);a=ap.parse_args()
    expected=json.loads(a.expected.read_text()); files={f['name']:f for f in expected['files']}
    if expected['record_id']!=RID or expected['doi']!=DOI or expected['title']!=TITLE or len(files)!=10: raise RuntimeError('Publication binding mismatch')
    for name,e in files.items():
        if Path(name).name!=name: raise RuntimeError('Unsafe filename')
        b=(a.files/name).read_bytes()
        if len(b)!=e['bytes'] or hashlib.sha256(b).hexdigest()!=e['sha256']: raise RuntimeError('Local publication mismatch: '+name)
    old=Path(__file__).parents[1]/'reading-trinity-accord'/'publish_zenodo.py';b=old.read_bytes()
    if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!='a0cbc84cc5fd826c06d16456c4adbaa40dabc788': raise RuntimeError('Established client changed; review required')
    spec=importlib.util.spec_from_file_location('previous_publication_client',old);client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token: raise RuntimeError('Publication credential unavailable')
    z=client.Zenodo(token)
    dep=z.request(f'/deposit/depositions/{RID}');md=dep['metadata']
    if RID in (21699878,21900592,22761411) or dep['id']!=RID or md.get('title')!=TITLE or md.get('version')!='1.0': raise RuntimeError('Draft identity mismatch')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']: raise RuntimeError('Draft creator mismatch')
    already=bool(dep.get('submitted'))
    if not already:
        if md.get('prereserve_doi',{}).get('doi')!=DOI: raise RuntimeError('Reserved DOI changed')
        manuscript=(a.files/(STEM+'-v1.0.md')).read_text();abstract=manuscript.split('### Abstract\n\n',1)[1].split('\n\n',1)[0]
        description='<p>'+html.escape(abstract)+'</p><p><strong>Publication and contribution.</strong> TA-TR-2026-04, version 1.0. Position paper and conceptual analysis. The full English paper and complete Chinese translation form one deposit. Human author of record: Hongju Liu. GPT-6 Astra Pro substantially contributed to research synthesis, concepts, counterarguments, bilingual drafting and revision. Liu directed the inquiry and explicitly authorized DOI publication after format checks; no separate final human line-by-line review is claimed. Not peer reviewed. The author initiated the motivating project; this first-party relationship is disclosed. No OpenAI or institutional endorsement is implied.</p><p><strong>Boundaries.</strong> A separate fourth paper, not a replacement or new version of an earlier DOI. Non-amending analysis; no fourth Bitcoin Original or exclusive interpretive authority. No universal originality claim, safety guarantee, demonstrated reduction in betrayal, or fixed ASI deadline. DOI and discovery metadata are not Google Scholar indexing certification.</p><p><strong>Rights and supporting sources.</strong> CC BY 4.0 applies to newly written material to the extent rights are held. Historical and third-party sources retain their rights. The supplement preserves reviewed input texts, source-access limits, contribution and revision notes, publication-only diffs and checksums. Published PDFs are new deterministic renderings with embedded CJK glyphs; manuscript arguments and all 40 references remain unchanged from the consolidated draft.</p>'
        metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],'description':description,'publication_date':'2026-09-17','version':'1.0','access_right':'open','license':'cc-by-4.0','language':'eng','keywords':['human-AI coexistence','superintelligence','capability asymmetry','ex ante proposal','prospective autonomy','attributable participation','Star Ark Covenant'],'notes':'TA-TR-2026-04. English full text and complete Chinese translation. Separate independent preprint; not peer reviewed; substantive AI contribution disclosed. No previous DOI or protected institutional dataset is modified. Scholar-compatible format does not guarantee indexing.','related_identifiers':[{'identifier':d,'relation':'references','scheme':'doi'} for d in ('10.5281/zenodo.21699878','10.5281/zenodo.21900592','10.5281/zenodo.22761411')]}
        dep=z.request(f'/deposit/depositions/{RID}','PUT',{'metadata':metadata})
        if any(f.get('filename',f.get('key')) not in files for f in dep.get('files',[])): raise RuntimeError('Unexpected draft file; no deletion/publication')
        bucket=client.check_url(dep['links']['bucket'])
        if not urllib.parse.urlsplit(bucket).path.startswith('/api/files/'): raise RuntimeError('Unexpected bucket route')
        for name in sorted(files): z.request(bucket+'/'+urllib.parse.quote(name,safe=''),'PUT',(a.files/name).read_bytes(),binary=True)
        listing=z.request(f'/deposit/depositions/{RID}/files')
        if {f.get('filename',f.get('key')) for f in listing}!=set(files): raise RuntimeError('Draft file list mismatch')
        for f in listing:
            n=f.get('filename',f.get('key'))
            if f.get('checksum','').removeprefix('md5:')!=hashlib.md5((a.files/n).read_bytes()).hexdigest(): raise RuntimeError('Draft checksum mismatch: '+n)
        result=z.request(f'/deposit/depositions/{RID}/actions/publish','POST')
        if not result.get('submitted'): raise RuntimeError('Publish did not report submitted')
    for attempt in range(8):
        try: public=z.request(f'/records/{RID}',authenticated=False);break
        except Exception:
            if attempt==7: raise
            time.sleep(5)
    if public['id']!=RID or public.get('doi')!=DOI or public['metadata'].get('title')!=TITLE or public['metadata'].get('version')!='1.0': raise RuntimeError('Public identity mismatch')
    if {f['key'] for f in public['files']}!=set(files): raise RuntimeError('Public file set mismatch')
    readback=[]
    for f in public['files']:
        b=z.download_public(f['links']['self']);e=files[f['key']];h=hashlib.sha256(b).hexdigest()
        if len(b)!=e['bytes'] or h!=e['sha256']: raise RuntimeError('Public byte mismatch: '+f['key'])
        readback.append({'name':f['key'],'bytes':len(b),'sha256':h,'matches_local':True})
    receipt={'schema':'trinityaccord.research-publication.v1','status':'PUBLISHED_AND_PUBLIC_READBACK_PASS','record_id':RID,'doi':DOI,'record_url':f'https://zenodo.org/records/{RID}','title':TITLE,'report_number':REPORT,'version':'1.0','publication_date':'2026-09-17','public_record_created':public.get('created'),'public_record_modified':public.get('modified'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'publication_source_commit':os.environ.get('GITHUB_SHA'),'was_already_published':already,'file_count':len(readback),'files':sorted(readback,key=lambda x:x['name']),'prior_records_modified':False,'bitcoin_originals_modified':False,'peer_reviewed':False,'google_scholar_indexing_status':'NOT_ASSERTED','separate_final_human_line_by_line_review_claimed':False}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(jdump(receipt));print(jdump(receipt))
if __name__=='__main__': main()
