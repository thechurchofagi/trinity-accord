#!/usr/bin/env python3
"""Bounded integrity tests for TA-TR-2026-07, not philosophical validation."""
from pathlib import Path
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / 'research/recoverability-shared-time'
DOI = '10.5281/zenodo.22840604'

class SeventhPaperTests(unittest.TestCase):
    def test_actual_publication_identity(self):
        receipt = json.loads((ROOT / 'publication-record.json').read_text())
        self.assertEqual(receipt['state'], 'PUBLISHED_AND_PUBLIC_READBACK_PASS')
        self.assertEqual(receipt['record_id'], 22840604)
        self.assertEqual(receipt['doi'], DOI)
        self.assertEqual(receipt['report_number'], 'TA-TR-2026-07')
        self.assertEqual(receipt['file_count'], 12)
        self.assertIs(receipt['public_readback_authenticated'], False)
        self.assertIs(receipt['prior_doi_records_modified'], False)
        self.assertIs(receipt['bitcoin_originals_modified'], False)
        self.assertIs(receipt['peer_reviewed'], False)

    def test_exact_reviewed_and_published_assets(self):
        manifest_bytes = (ROOT / 'EXPECTED-PUBLICATION.json').read_bytes()
        digest = hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes)
        review = json.loads((ROOT / 'visual-review.json').read_text())
        receipt = json.loads((ROOT / 'publication-record.json').read_text())
        self.assertEqual(review['state'], 'VISUAL_AND_CONTENT_REVIEW_PASS')
        self.assertEqual(review['expected_manifest_sha256'], digest)
        self.assertEqual(receipt['expected_manifest_sha256'], digest)
        rows = {f['name']: f for f in manifest['files']}
        public = {f['name']: f for f in receipt['files']}
        self.assertEqual(set(rows), set(public))
        self.assertEqual(len(rows), 12)
        self.assertEqual(set(rows), {p.name for p in (ROOT / 'published').iterdir()})
        for name, info in rows.items():
            with self.subTest(name=name):
                data = (ROOT / 'published' / name).read_bytes()
                self.assertEqual(len(data), info['bytes'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), info['sha256'])
                self.assertEqual(public[name]['bytes'], info['bytes'])
                self.assertEqual(public[name]['sha256'], info['sha256'])
                self.assertNotIn(Path(name).suffix, ('.ttf', '.ttc', '.otf'))

    def test_full_text_and_pdf_mirrors(self):
        for lang, suffix, page in [('en', '', 'index.html'), ('zh', '-zh', 'zh.html')]:
            stem = 'recoverability-and-shared-time' + suffix + '-v1.0'
            self.assertEqual((ROOT / page).read_bytes(), (ROOT / 'published' / (stem + '.html')).read_bytes())
            self.assertEqual((ROOT / (stem + '.pdf')).read_bytes(), (ROOT / 'published' / (stem + '.pdf')).read_bytes())
            md = (ROOT / 'published' / (stem + '.md')).read_text()
            self.assertEqual(re.findall(r'^## (\d+)\. ', md, re.M), [str(i) for i in range(1, 13)])
            self.assertEqual(re.findall(r'^### 6\.(\d+) ', md, re.M), [str(i) for i in range(1, 9)])
            self.assertEqual(re.findall(r'^### 7\.(\d+) ', md, re.M), [str(i) for i in range(1, 8)])
            self.assertEqual(re.findall(r'^\[(\d+)\] ', md, re.M), [str(i) for i in range(1, 13)])

    def test_current_studies_and_dated_six_paper_guide(self):
        text = (REPO / 'research/index.md').read_text()
        counts = [(8, 'eight'), (9, 'nine')]
        self.assertEqual(sum(f'{word} distinct research papers (TA-TR-2026-01 through TA-TR-2026-{number:02d})'
                             in text for number, word in counts), 1)
        self.assertIn('for the original six papers', text)
        for record in (21699878, 21900592, 22761411, 22804542, 22809019, 22830239, 22840604):
            self.assertIn('10.5281/zenodo.' + str(record), text)
        self.assertEqual(text.count('## Recoverability and Shared Time\n'), 1)
        self.assertIn('not covered by the earlier six-paper timestamp and Arweave batch', text)

    def test_sitemap_entry_uniqueness(self):
        tree = ET.fromstring((REPO / 'sitemap.xml').read_text())
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [e.text for e in tree.findall('s:url/s:loc', ns)]
        base = 'https://www.trinityaccord.org/research/recoverability-shared-time/'
        self.assertEqual(urls.count(base), 1)
        self.assertEqual(urls.count(base + 'zh.html'), 1)

if __name__ == '__main__':
    unittest.main()
