#!/usr/bin/env python3
"""Check the linked revision's public identity, metadata and exact PDF mirrors."""
import argparse, hashlib, json, re
from pathlib import Path
from html.parser import HTMLParser
import yaml

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
PREFIX='research/rlc-prefix-separable/versions/v1.1'

class Head(HTMLParser):
    def __init__(self,text):
        super().__init__();self.meta={};self.feed(text.split('</head>',1)[0])
    def handle_starttag(self,tag,attrs):
        if tag=='meta':
            attrs=dict(attrs)
            if attrs.get('name'):self.meta.setdefault(attrs['name'],[]).append(attrs.get('content',''))

def check(site=None):
    receipt=json.loads((ROOT/'publication-record.json').read_text())
    assert (receipt['report_number'],receipt['version'],receipt['record_id'],receipt['doi'])==('TA-TR-2026-22','1.1',23118189,'10.5281/zenodo.23118189')
    assert receipt['submitted'] and receipt['public_file_readback_pass']
    assert receipt['public_readback_authenticated'] is False
    assert receipt['previous_record_id']==23103274 and receipt['conceptrecid']=='23103273'
    page=yaml.safe_load((ROOT/'index.md').read_text().split('---',2)[1])
    assert page['citation_doi']==receipt['doi'] and page['citation_title']==receipt['title']
    assert str(page['article_version'])=='1.1' and page['citation_language']=='en'
    assert page['article_identifier']==page['citation_technical_report_number']==receipt['report_number']
    assert page['article_record_url']==receipt['record_url']
    expected=json.loads((ROOT/'EXPECTED-PUBLICATION.json').read_text())
    assert expected['record_id']==receipt['record_id'] and expected['files']==[{k:f[k] for k in ('name','bytes','sha256')} for f in receipt['files']]
    targets=json.loads((REPO/'research/paper-timestamps/2026-10-03-paper22-v11/targets.json').read_text())
    assert targets['paper_count']==1 and targets['papers'][0]['doi']==receipt['doi']
    pdfs={f['name']:f for f in receipt['files'] if f['name'].endswith('.pdf')}
    assert len(pdfs)==2
    assert {f['name']:f['sha256'] for f in targets['papers'][0]['pdfs']}=={name:f['sha256'] for name,f in pdfs.items()}
    for name,f in pdfs.items():
        data=(ROOT/'published'/name).read_bytes()
        assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256']
        if site:assert (site/PREFIX/'published'/name).read_bytes()==data
    policy=json.loads((REPO/'api/research-boundary.v1.json').read_text())
    classified=[p for p in policy['first_party_papers'] if p['report']==receipt['report_number']]
    assert len(classified)==1 and classified[0]['layer']=='L4'
    assert all(classified[0][k] is False for k in ('canonical','amends_canon','authoritative_interpretation','independent_corroboration'))
    if site:
        html=(site/PREFIX/'index.html').read_text();head=Head(html)
        assert head.meta['citation_doi']==[receipt['doi']]
        assert head.meta['citation_title']==[receipt['title']]
        assert head.meta['citation_pdf_url']==[page['citation_pdf_url']]
        assert head.meta['trinity-research-relation']==['adjacent_first_party_research']
        assert head.meta['trinity-research-canonical']==['false']
        assert len(re.findall(r'<h1\b',html))==1
    print('TA22 v1.1 linked identity, metadata, preservation targets and exact PDF mirrors: PASS')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--site-dir',type=Path)
    check(parser.parse_args().site_dir)
