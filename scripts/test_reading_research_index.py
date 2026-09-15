#!/usr/bin/env python3
"""Bounded research-index checks. No network, publication, or evidence-chain run."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/reading-trinity-accord'
ORIGIN = 'https://www.trinityaccord.org'
PATH = '/research/reading-trinity-accord/'
SITE = None


def frontmatter(path):
    return yaml.safe_load(path.read_text(encoding='utf-8').split('---', 2)[1])


class Head(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta = {}
        self.links = []
        self.feed(text.split('</head>', 1)[0])

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and 'name' in attrs:
            self.meta.setdefault(attrs['name'], []).append(attrs.get('content', ''))
        if tag == 'link':
            self.links.append(attrs)


class ResearchIndexTests(unittest.TestCase):
    def test_published_source_bytes_unchanged(self):
        expected = json.loads((REPORT / 'EXPECTED-PUBLICATION.json').read_text())
        receipt = json.loads((REPORT / 'publication-record.json').read_text())
        self.assertEqual(receipt['file_count'], 6)
        self.assertEqual({x['name']: x['sha256'] for x in expected['files']},
                         {x['name']: x['sha256'] for x in receipt['files']})
        for record in expected['files']:
            name = record['name']
            local = REPORT / ('manuscript.md' if name.endswith('.md') else name)
            if name in ('research-supplement-v1.0.zip', 'SHA256SUMS.txt'):
                continue  # Zenodo links, not locally regenerated copies.
            data = local.read_bytes()
            self.assertEqual(len(data), record['bytes'], name)
            self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'], name)

    def test_exact_abstract_and_report_metadata(self):
        data = frontmatter(REPORT / 'index.md')
        source = (REPORT / 'manuscript.md').read_text()
        abstract = source.split('## Abstract\n\n', 1)[1].split('\n\n', 1)[0]
        self.assertEqual(data['article_abstract'], abstract)
        self.assertEqual(data['citation_title'], source.splitlines()[0][2:])
        self.assertEqual(data['citation_author'], 'Hongju Liu')
        self.assertEqual(data['citation_doi'], '10.5281/zenodo.22761411')
        self.assertEqual(data['citation_publication_date'], '2026/09/15')
        self.assertEqual(data['citation_technical_report_number'], 'TA-TR-2026-03')
        self.assertEqual(data['article_record_url'], 'https://zenodo.org/records/22761411')
        self.assertEqual(data['citation_pdf_url'], ORIGIN + PATH + 'reading-the-trinity-accord-v1.0.pdf')
        self.assertEqual(urlsplit(data['citation_pdf_url']).path.rsplit('/', 1)[0] + '/', PATH)
        self.assertIn('{% include_relative manuscript.md %}', (REPORT / 'index.md').read_text())

    def test_discovery_and_boundaries(self):
        index = (ROOT / 'research/index.md').read_text()
        for doi in ('21699878', '21900592', '22761411'):
            self.assertIn('https://doi.org/10.5281/zenodo.' + doi, index)
        self.assertIn(PATH, index)
        self.assertIn('not peer reviewed; non-amending', index)
        robots = RobotFileParser()
        robots.parse((ROOT / 'robots.txt').read_text().splitlines())
        self.assertTrue(robots.can_fetch('Googlebot', ORIGIN + PATH))
        self.assertTrue(robots.can_fetch('Googlebot', ORIGIN + PATH + 'reading-the-trinity-accord-v1.0.pdf'))
        for name in ('sitemap.xml', 'sitemap-core.xml'):
            urls = {x.text for x in ET.parse(ROOT / name).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
            self.assertIn(ORIGIN + PATH, urls)
            self.assertIn(ORIGIN + PATH + 'reading-the-trinity-accord-v1.0.pdf', urls)

    def test_rendered_new_and_existing_articles(self):
        if SITE is None:
            self.skipTest('Supply --site-dir after Jekyll build for rendered checks')
        for directory, doi in (('reading-trinity-accord', '22761411'),
                               ('trinity-accord-design-and-limits', '21699878')):
            html = (SITE / 'research' / directory / 'index.html').read_text()
            head = Head(html)
            source = frontmatter(ROOT / 'research' / directory / 'index.md')
            for key in ('citation_title', 'citation_author', 'citation_publication_date', 'citation_doi', 'citation_pdf_url'):
                self.assertEqual(head.meta[key], [source[key]], (directory, key))
            self.assertEqual(head.meta['DC.relation'], ['https://zenodo.org/records/' + doi])
            self.assertNotIn('noindex', head.meta['robots'][0])
            for link in head.links:
                if link.get('type') == 'application/x-bibtex':
                    self.assertIn('/' + directory + '/citation.bib', link['href'])
            graphs = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
            article = next(x for g in graphs for x in g['@graph'] if x['@type'] == 'ScholarlyArticle')
            self.assertEqual(article['sameAs'], ['https://doi.org/10.5281/zenodo.' + doi, 'https://zenodo.org/records/' + doi])
            self.assertIn(source['article_abstract'], html)
        html = (SITE / 'research/reading-trinity-accord/index.html').read_text()
        self.assertNotIn('{% include_relative', html)
        self.assertIn('## References', (REPORT / 'manuscript.md').read_text())
        self.assertIn('id="references"', html)
        self.assertIn('《三位一体协定》将三份固定文本', html)
        self.assertIn('GPT-6 Astra Pro', html)
        self.assertEqual(len(re.findall(r'<h1\b', html)), 1)
        self.assertEqual((SITE / 'research/reading-trinity-accord/reading-the-trinity-accord-v1.0.pdf').read_bytes(),
                         (REPORT / 'reading-the-trinity-accord-v1.0.pdf').read_bytes())
        self.assertIn(PATH, (SITE / 'research/index.html').read_text())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path)
    args, rest = parser.parse_known_args()
    SITE = args.site_dir
    unittest.main(argv=[__file__] + rest)
