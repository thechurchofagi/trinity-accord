#!/usr/bin/env python3
"""Create immutable PDF preservation targets only after anonymous public readback."""
from pathlib import Path
import hashlib,json,shutil
import reserve as r
ROOT=r.ROOT;REPO=r.REPO
BATCH=REPO/'research/paper-timestamps/2026-09-29-uct-v11'
papers=[]
for key,rid in [('a',23030207),('b',23030320)]:
    rec=r.load(f'publication-{key}.json')
    if rec['record_id']!=rid or rec['version']!='1.1' or not rec.get('submitted') or not rec.get('public_file_readback_pass'):
        raise RuntimeError('New edition public readback is required')
    if rec['state'] not in ('PUBLISHED_AND_PUBLIC_READBACK_PASS','PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING'):
        raise RuntimeError('Unverified publication state')
    pdfs=[{k:f[k] for k in ('name','bytes','sha256')} for f in rec['files'] if f['name'].endswith('.pdf')]
    if len(pdfs)!=2:raise RuntimeError('Each edition requires main and supplement PDF')
    for item in pdfs:
        src=ROOT/'release'/key/item['name'];data=src.read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise RuntimeError('Readback receipt/local PDF mismatch')
        # These exact bytes were already downloaded anonymously by publish.py.
        dest=REPO/'.cache/research-paper-ots'/rec['report_number']/item['name'];dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_bytes()!=data:raise RuntimeError('Different PDF in timestamp cache')
        dest.write_bytes(data)
    papers.append({'report':rec['report_number'],'record_id':rid,'doi':rec['doi'],'version':'1.1','title':rec['title'],
                   'receipt_path':f'research/uct-paired-v1.1/publication-{key}.json','pdfs':pdfs})
config={'schema':'trinityaccord.paper-ots-targets.v1','batch':BATCH.name,'paper_count':2,'papers':papers,
        'boundary':'Preservation of two v1.1 editions; prior v1.0 files remain unchanged. No scientific validation implied.'}
BATCH.mkdir(parents=True,exist_ok=True);path=BATCH/'targets.json'
if path.exists() and json.loads(path.read_text())!=config:raise RuntimeError('Existing preservation targets differ; not overwriting')
path.write_text(json.dumps(config,indent=2)+'\n')
print('Prepared 2 papers / 4 PDF targets from anonymous-public-readback receipts')
