#!/usr/bin/env python3
"""Check paper identity, exact published PDF mirrors and source-role routing."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


class Head(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta = {}
        self.feed(text.split('</head>', 1)[0])

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attrs = dict(attrs)
            if attrs.get('name'):
                self.meta.setdefault(attrs['name'], []).append(attrs.get('content', ''))


def check(site=None):
    receipt = json.loads((ROOT / 'publication-record.json').read_text())
    assert receipt['report_number'] == 'TA-TR-2026-22'
    assert receipt['record_id'] == 23103274 and receipt['doi'] == '10.5281/zenodo.23103274'
    assert receipt['state'] == 'PUBLISHED_AND_PUBLIC_READBACK_PASS'
    assert receipt['public_file_readback_pass'] and receipt['doi_resolution_pass']
    assert receipt['public_readback_authenticated'] is False
    page = yaml.safe_load((ROOT / 'index.md').read_text().split('---', 2)[1])
    assert page['article_identifier'] == page['citation_technical_report_number'] == receipt['report_number']
    assert page['citation_doi'] == receipt['doi'] and page['citation_title'] == receipt['title']
    assert page['citation_language'] == 'en' and str(page['article_version']) == receipt['version']
    assert page['article_record_url'] == receipt['record_url']
    policy = json.loads((REPO / 'api/research-boundary.v1.json').read_text())
    classification = [x for x in policy['first_party_papers'] if x['report'] == receipt['report_number']]
    assert len(classification) == 1 and classification[0]['layer'] == 'L4'
    assert all(classification[0][key] is False for key in ('canonical', 'amends_canon', 'authoritative_interpretation', 'independent_corroboration'))
    targets = json.loads((REPO / 'research/paper-timestamps/2026-10-02-paper22-v10/targets.json').read_text())
    pdfs = {x['name']: x for x in receipt['files'] if x['name'].endswith('.pdf')}
    assert len(pdfs) == 2 and targets['paper_count'] == 1
    target = targets['papers'][0]
    assert target['report'] == receipt['report_number'] and target['doi'] == receipt['doi']
    assert {x['name']: x['sha256'] for x in target['pdfs']} == {name: x['sha256'] for name, x in pdfs.items()}
    for name, item in pdfs.items():
        data = (ROOT / 'published' / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
        if site:
            assert (site / 'research/rlc-prefix-separable/published' / name).read_bytes() == data
    if site:
        html = (site / 'research/rlc-prefix-separable/index.html').read_text()
        head = Head(html)
        assert head.meta['citation_doi'] == [receipt['doi']]
        assert head.meta['citation_title'] == [receipt['title']]
        assert head.meta['citation_pdf_url'] == [page['citation_pdf_url']]
        assert head.meta['trinity-research-relation'] == ['adjacent_first_party_research']
        assert head.meta['trinity-research-canonical'] == ['false']
        graphs = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        articles = [x for graph in graphs for x in graph['@graph'] if x.get('@type') == 'ScholarlyArticle']
        assert len(articles) == 1 and articles[0].get('about') != {'@id': 'https://www.trinityaccord.org/#accord'}
        assert len(re.findall(r'<h1\b', html)) == 1
    print('TA22 publication identity, exact PDF mirror and adjacent-research routing: PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path)
    check(parser.parse_args().site_dir)
