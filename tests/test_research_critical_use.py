"""Editorial link/identity checks only; not a test of philosophical truth or reader effects."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOIS = ('21699878', '21900592', '22761411', '22804542', '22809019', '22830239')
GUIDES = ('research-positioning.md', 'research-positioning-zh.md')

def validate_guide(text):
    anchors = re.findall(r'\{: #paper-(\d\d) \}', text)
    expected = [f'{i:02d}' for i in range(1, 7)]
    if anchors != expected:
        raise ValueError('Six unique, ordered paper anchors required')
    for i, record in enumerate(DOIS, 1):
        start = text.index(f'{{: #paper-{i:02d} }}')
        end = text.find('\n### ', start)
        if end < 0:
            end = text.find('\n## ', start)
        if end < 0:
            end = len(text)
        part = text[start:end]
        actual = re.findall(r'10\.5281/zenodo\.(\d+)', part)
        if actual != [record]:
            raise ValueError(f'Paper {i} DOI mismatch: {actual}')
    refs = dict(re.findall(r'^\[([^\]]+)\]: (https://\S+)\s*$', text, re.M))
    for key in ('O1', 'O2', 'O3', 'SA', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'Z'):
        if key not in refs:
            raise ValueError('Missing source reference: ' + key)
    originals = ('97631551', '98369145', '98387475')
    for i, number in enumerate(originals, 1):
        if not refs[f'O{i}'].endswith('/raw/' + number + '.txt'):
            raise ValueError('Original identity mismatch')
    if not refs['SA'].endswith('/raw/100751953.txt'):
        raise ValueError('Later Star Ark identity mismatch')
    return refs

class CriticalUseTests(unittest.TestCase):
    def setUp(self):
        self.texts = [(ROOT / 'research' / p).read_text(encoding='utf-8') for p in GUIDES]
        self.index = (ROOT / 'research/index.md').read_text(encoding='utf-8')
        self.assertIn('ten distinct research papers (TA-TR-2026-01 through TA-TR-2026-10)', self.index)
        self.series_word = 'ten'

    def test_ten_distinct_paper_sections_have_their_own_current_dois(self):
        papers = [
            ('Current technical report', '21699878'),
            ('Historical-position study', '21900592'),
            ('Reading the Trinity Accord', '22761411'),
            ('Beyond Guaranteed Control', '22804542'),
            ('Recovery without Epistemic Monopoly', '22809019'),
            ('Coexistence after Preference Change', '22830239'),
            ('Recoverability and Shared Time', '22840604'),
            ('Evidence for Artificial Self Attribution', '22842789'),
            ('Learning from an AI Claimant', '22846307'),
            ('Endogenous Reference Fields', '22852885'),
        ]
        section_rows = re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', self.index, re.M | re.S)
        sections = dict(section_rows)
        self.assertEqual(len(section_rows), len(sections), 'Duplicate section heading')
        paper_sections = {title: body for title, body in sections.items()
                          if re.search(r'^### ', body, re.M)}
        self.assertEqual(set(paper_sections), {title for title, _ in papers})
        self.assertEqual(len(paper_sections), 10)
        for number, (title, record_id) in enumerate(papers, 1):
            body = paper_sections[title]
            self.assertIn('https://doi.org/10.5281/zenodo.' + record_id, body)
            if number > 1:
                self.assertIsNotNone(re.search(rf'^TA-TR-2026-{number:02d}\b', body, re.M), title)

    def test_six_guided_claims_and_fixed_identities(self):
        for text in self.texts:
            validate_guide(text)

    def test_translation_references_match(self):
        self.assertEqual(validate_guide(self.texts[0]), validate_guide(self.texts[1]))

    def test_index_exposes_each_note_in_both_languages(self):
        for i in range(1, 7):
            for prefix in ('/research/research-positioning/', '/research/research-positioning/zh.html'):
                self.assertEqual(self.index.count(f']({prefix}#paper-{i:02d})'), 1)
        # The dated guide still covers six; later studies do not expand its scope.
        self.assertIn('for the original six papers', self.index)
        self.assertNotIn('six independent research papers', self.index)
        self.assertNotIn(f'{self.series_word} independent research papers', self.index)
        self.assertIn(f'not {self.series_word} independent corroborations', self.index)

    def test_guide_cannot_be_counted_as_paper_seven(self):
        self.assertIn('Not a seventh paper', self.texts[0])
        self.assertIn('不是第七篇论文', self.texts[1])
        self.assertNotIn('scholarly_article: true', '\n'.join(self.texts))
        self.assertIn('not part of the existing DOI deposits', self.texts[0])
        self.assertIn('没有加入既有 OTS／Arweave 证据包', self.texts[1])

    def test_citation_boundary_is_paper_specific(self):
        boundary = self.index.split('## Citation boundary', 1)[1]
        self.assertIn('specific paper and version', boundary)
        self.assertIn('TA-TR-2026-01 v1.1 only', boundary)
        self.assertIn(f'no single paper DOI represents all {self.series_word}', boundary)
        self.assertIn('valid criticisms and negative results remain intact', boundary)

    def test_invalid_mapping_and_missing_entry_are_rejected(self):
        original = self.texts[0]
        variants = (
            original.replace('10.5281/zenodo.22830239', '10.5281/zenodo.22809019', 1),
            original.replace('{: #paper-03 }', '{: #paper-02 }', 1),
            original.replace('[O1]:', '[MISSING]:', 1),
        )
        for text in variants:
            with self.assertRaises(ValueError):
                validate_guide(text)

if __name__ == '__main__':
    unittest.main()
