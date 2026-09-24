#!/usr/bin/env python3
"""Verify the current edition and the unchanged published v1.1 assets."""
import argparse
import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from publication_common import ROOT, REPO, VERSION, STEM, TITLE, REPORT, PREVIOUS_RECORD, sha, validate_local_package

SITE_ROOT = ROOT.parents[1]
SITE_PATH = '/research/learning-from-an-ai-claimant/'
BASE = 'https://www.trinityaccord.org' + SITE_PATH

class HeadMetadata(HTMLParser):
    def __init__(self):
        super().__init__();self.meta={};self.canonicals=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='meta' and attrs.get('name'):
            self.meta.setdefault(attrs['name'].lower(),[]).append(attrs.get('content',''))
        if tag=='link' and attrs.get('rel')=='canonical':self.canonicals.append(attrs.get('href'))

def verified():
    expected,digest=validate_local_package()
    rec=json.loads((ROOT/'publication-record.json').read_text())
    assert rec['state']=='PUBLISHED_AND_PUBLIC_READBACK_PASS'
    assert rec['expected_manifest_sha256']==digest
    assert rec['record_id']==expected['record_id'] and rec['doi']==expected['doi']
    assert rec['previous_record_id']==PREVIOUS_RECORD and rec['new_research_papers']==0
    assert rec['public_readback_authenticated'] is False and rec['peer_reviewed'] is False
    assert str(rec['conceptrecid'])==str(expected['conceptrecid'])
    public={f['name']:f for f in rec['files']}
    assert set(public)=={f['name'] for f in expected['files']}
    for f in expected['files']:
        assert public[f['name']]['sha256']==f['sha256'] and public[f['name']]['bytes']==f['bytes']
    return rec,expected

def check_directory(directory, rec, expected):
    for row in expected['files']:
        target=directory/row['name'];data=target.read_bytes()
        assert len(data)==row['bytes'] and sha(data)==row['sha256'],target
    for alias, source in [('index.html',f'{STEM}-v{VERSION}.html'),('zh-guide.html',f'{STEM}-zh-guide-v{VERSION}.html')]:
        assert (directory/alias).read_bytes()==(ROOT/'published'/source).read_bytes()
    head=HeadMetadata();head.feed((directory/'index.html').read_text())
    assert head.canonicals==[BASE]
    for key,value in {'citation_title':TITLE,'citation_author':'Hongju Liu','citation_doi':rec['doi'],
        'citation_technical_report_number':REPORT,'citation_pdf_url':BASE+f'{STEM}-v{VERSION}.pdf','citation_language':'en'}.items():
        assert head.meta.get(key)==[value],key
    guide=HeadMetadata();guide.feed((directory/'zh-guide.html').read_text())
    assert guide.canonicals==[BASE+'zh-guide.html']
    assert guide.meta.get('robots')==['noindex,follow']
    assert not any(k.startswith('citation_') for k in guide.meta)
    assert json.loads((directory/'citation.csl.json').read_text())['DOI']==rec['doi']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--site-dir',type=Path);args=parser.parse_args()
    rec,expected=verified()
    pointer=json.loads((SITE_ROOT/'current-version.json').read_text())
    assert (pointer['version'],pointer['doi'],pointer['receipt_path'])==(VERSION,rec['doi'],'versions/v1.2/publication-record.json')
    check_directory(SITE_ROOT,rec,expected)
    old=json.loads((SITE_ROOT/'publication-record.json').read_text())
    assert old['record_id']==PREVIOUS_RECORD and old['version']=='1.1'
    for f in old['files']:
        data=(SITE_ROOT/'published'/f['name']).read_bytes()
        assert len(data)==f['bytes'] and sha(data)==f['sha256'],'Old published asset changed: '+f['name']
    index=(REPO/'research/index.md').read_text()
    counts = ((13, 'thirteen'), (14, 'fourteen'), (15, 'fifteen'), (16, 'sixteen'))
    assert sum(f'{word} distinct research papers (TA-TR-2026-01 through TA-TR-2026-{number:02d})' in index
               for number, word in counts) == 1, 'Series count differs'
    assert index.count('  - id: "learning-from-an-ai-claimant"')==1
    assert rec['doi'] in index and f'10.5281/zenodo.{PREVIOUS_RECORD}' in index
    urls=[e.text for e in ET.parse(REPO/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert urls.count(BASE)==1 and not any(u.startswith(BASE) and u!=BASE for u in urls)
    if args.site_dir:check_directory(args.site_dir/SITE_PATH.strip('/'),rec,expected)
    print('TA09_V12_PUBLICATION_VERSION_LINEAGE_MIRRORS_AND_V11_PRESERVATION_PASS')

if __name__=='__main__':main()
