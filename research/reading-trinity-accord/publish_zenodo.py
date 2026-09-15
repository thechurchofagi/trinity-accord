#!/usr/bin/env python3
"""Publish only the already-created TA-TR-2026-03 deposit, then public-readback.
Uses the repository's existing ZENODO_ACCESS_TOKEN for its intended purpose.
Never prints credentials; never creates a replacement/version of older records.
"""
from __future__ import annotations
import argparse,hashlib,html,json,os,time,urllib.parse,urllib.request
from pathlib import Path
RID=22761411
DOI='10.5281/zenodo.22761411'
TITLE='Reading the Trinity Accord: Future Address, Curated Voices, and Non-Amending Stewardship'
def check_url(url:str)->str:
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname!='zenodo.org' or p.username or p.password: raise RuntimeError('Unexpected Zenodo host')
    return url
class Zenodo:
    def __init__(self,token:str):self.token=token
    def request(self,path:str,method='GET',data=None,authenticated=True,binary=False):
        url=check_url(path if path.startswith('https://') else 'https://zenodo.org/api'+path)
        headers={}
        if authenticated:headers['Authorization']='Bearer '+self.token
        if data is not None and not binary:headers['Content-Type']='application/json';data=json.dumps(data).encode()
        elif binary:headers['Content-Type']='application/octet-stream'
        request=urllib.request.Request(url,data=data,headers=headers,method=method)
        with urllib.request.urlopen(request,timeout=120) as response:
            content=response.read()
            if response.status>=300:raise RuntimeError(f'Unexpected response: {response.status}')
            return json.loads(content)
    def download_public(self,url):
        with urllib.request.urlopen(check_url(url),timeout=120) as r:return r.read()
def main():
    p=argparse.ArgumentParser();p.add_argument('--files',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('Publication credential unavailable')
    z=Zenodo(token);expected=json.loads(a.expected.read_text()); files={f['name']:f for f in expected['files']}
    assert expected['doi']==DOI and expected['title']==TITLE and len(files)==6
    for name,f in files.items():
        if Path(name).name!=name:raise RuntimeError('Unsafe filename')
        b=(a.files/name).read_bytes()
        if len(b)!=f['bytes'] or hashlib.sha256(b).hexdigest()!=f['sha256']:raise RuntimeError('Local file mismatch: '+name)
    dep=z.request(f'/deposit/depositions/{RID}'); md=dep['metadata']
    if dep['id']!=RID or md.get('title')!=TITLE or md.get('version')!='1.0':raise RuntimeError('Draft identity mismatch')
    if not any(c.get('name')=='Liu, Hongju' for c in md.get('creators',[])):raise RuntimeError('Draft creator mismatch')
    published_already=bool(dep.get('submitted'))
    if not published_already:
        reserved=md.get('prereserve_doi',{}).get('doi')
        if reserved!=DOI:raise RuntimeError('Reserved DOI changed')
        manuscript=(a.files/'reading-the-trinity-accord-v1.0.md').read_text();abstract=manuscript.split('## Abstract\n\n',1)[1].split('\n\n**Keywords:',1)[0]
        description='<p>'+html.escape(abstract)+'</p><p><strong>Scope and contribution.</strong> This new study extends, and does not independently corroborate, the two cited prior reports. It adds five source-linked creative readings including two countercases, and a reproduced pre/post repair source-fidelity test. The paper contains no letter-grade ranking or global-uniqueness claim.</p><p><strong>AI contribution and review.</strong> Principal substantive analysis, drafting, critical revision, and package preparation: GPT-6 Astra Pro. Hongju Liu commissioned, directed and explicitly authorized revision and submission and is the human author of record/depositor. Not peer reviewed; no separate final human line-by-line verification or journal acceptance is claimed. The author is the project Guardian and has disclosed project-related interests. No OpenAI or repository endorsement is implied.</p><p><strong>Rights.</strong> CC BY 4.0 applies to newly written report and support material to the extent the depositor holds rights; it does not relicense historical songs, images, source texts or third-party work.</p>'
        metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher and project Guardian, Shenzhen, China'}],'description':description,'publication_date':'2026-09-15','version':'1.0','access_right':'open','license':'cc-by-4.0','language':'eng','keywords':['Trinity Accord','human-AI collaboration','archival authenticity','future address','curated voices','source fidelity','stewardship'],'notes':'TA-TR-2026-03. AI-led critical research report / preprint. English full text and Chinese abstract. A separate new record; no prior DOI, Bitcoin Original, or protected institutional dataset is overwritten. Supplement contains source locators, a five-case interpretive matrix, bounded reproduction results and a critical revision log. DOI is a persistent identifier, not peer review or indexing certification.','related_identifiers':[{'identifier':'10.5281/zenodo.21699878','relation':'references','scheme':'doi'},{'identifier':'10.5281/zenodo.21900592','relation':'references','scheme':'doi'}]}
        dep=z.request(f'/deposit/depositions/{RID}','PUT',{'metadata':metadata})
        old=dep.get('files',[])
        if any(f.get('filename',f.get('key')) not in files for f in old):raise RuntimeError('Unexpected pre-existing draft file; no deletion or publish')
        bucket=check_url(dep['links']['bucket'])
        if not urllib.parse.urlsplit(bucket).path.startswith('/api/files/'):raise RuntimeError('Unexpected bucket route')
        for name in sorted(files):
            b=(a.files/name).read_bytes();z.request(bucket+'/'+urllib.parse.quote(name,safe=''),'PUT',b,binary=True)
        listing=z.request(f'/deposit/depositions/{RID}/files')
        if {f.get('filename',f.get('key')) for f in listing}!=set(files):raise RuntimeError('Draft file list mismatch')
        for f in listing:
            name=f.get('filename',f.get('key')); checksum=f.get('checksum','').removeprefix('md5:')
            if checksum!=hashlib.md5((a.files/name).read_bytes()).hexdigest():raise RuntimeError('Draft checksum mismatch: '+name)
        publication=z.request(f'/deposit/depositions/{RID}/actions/publish','POST')
        if not publication.get('submitted'):raise RuntimeError('Publication did not report submitted')
    # Public readback without the publication token: independent of draft access.
    public=None
    for attempt in range(6):
        try:public=z.request(f'/records/{RID}',authenticated=False);break
        except Exception:
            if attempt==5:raise
            time.sleep(5)
    if public['id']!=RID or public.get('doi')!=DOI or public.get('metadata',{}).get('title')!=TITLE:raise RuntimeError('Public record identity mismatch')
    if public.get('metadata',{}).get('version')!='1.0':raise RuntimeError('Public version mismatch')
    if {f['key'] for f in public['files']}!=set(files):raise RuntimeError('Public file list mismatch')
    readback=[]
    for f in public['files']:
        b=z.download_public(f['links']['self']); e=files[f['key']]; h=hashlib.sha256(b).hexdigest()
        if len(b)!=e['bytes'] or h!=e['sha256']:raise RuntimeError('Public byte mismatch: '+f['key'])
        readback.append({'name':f['key'],'bytes':len(b),'sha256':h,'matches_local':True})
    receipt={'status':'PUBLISHED_AND_PUBLIC_READBACK_PASS','record_id':RID,'doi':DOI,'record_url':f'https://zenodo.org/records/{RID}','title':TITLE,'version':'1.0','public_record_created':public.get('created'),'public_record_modified':public.get('modified'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'publication_source_commit':os.environ.get('GITHUB_SHA'),'was_already_published':published_already,'file_count':len(readback),'files':readback,'prior_records_modified':False,'peer_reviewed':False,'separate_final_human_line_by_line_review_claimed':False}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
