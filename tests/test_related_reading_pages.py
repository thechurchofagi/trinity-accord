"""Protect exact Originals and their reading interface, not a hand-edited snapshot."""
import base64
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inscription_reading', ROOT / 'scripts/generate_inscription_reading.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
# Exact original byte digests already bound by the frozen proof annex; these
# replace the former presentation hashes, which included commentary and omissions.
ORIGINAL_HASHES = {
    '97631551': '4e89bfabe03c8b53f80eb7979d56c8cccf0ae382c9647a2bea3b1477054616a8',
    '98369145': '003ef48c72307243b1f7a17c0578b311ee76d6f9a8078850773ad8fba04ab86d',
    '98387475': '25edaa35e7116614d3381ab6734ab5ee3369fb628fe11289e199d8871c2498ba',
}

class OriginalText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bodies = {}; self.active = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-inscription-number' in attrs:
            assert tag == 'pre' and self.active is None
            self.active = attrs['data-inscription-number']
            assert self.active not in self.bodies
            self.bodies[self.active] = ''
        elif self.active is not None:
            raise AssertionError('Unexpected markup inside original text')
    def handle_endtag(self, tag):
        if tag == 'pre': self.active = None
    def handle_data(self, value):
        if self.active: self.bodies[self.active] += value


def assert_faithful(source):
    parsed = OriginalText(); parsed.feed(source)
    assert set(parsed.bodies) == set(ORIGINAL_HASHES)
    for number, text in parsed.bodies.items():
        raw = (ROOT / f'bitcoin-inscription-mirrors/raw/{number}.txt').read_bytes()
        assert text.encode('utf-8') == raw, number


class ReadingFidelityTests(unittest.TestCase):
    def test_all_three_inscription_mirror_bodies_remain_exact(self):
        assert_faithful((ROOT / 'inscriptions.md').read_text())

    def test_raw_bytes_bound_to_both_existing_annexes(self):
        v2 = json.loads((ROOT / 'evidence/bitcoin-inscription-proof-annex-v2/ANNEX-MANIFEST.json').read_bytes())
        anchors = {a['inscription_number']: a for a in v2['anchors']}
        for a, raw in renderer.original_records():
            number = a['inscription_number']
            self.assertEqual(hashlib.sha256(raw).hexdigest(), ORIGINAL_HASHES[number])
            current = anchors[number]['content']
            self.assertEqual(base64.b64decode((ROOT / current['mirror_path']).read_bytes()), raw)
            self.assertEqual(current['body_sha256'], ORIGINAL_HASHES[number])

    def test_generated_page_and_interface(self):
        source = (ROOT / 'inscriptions.md').read_text()
        self.assertEqual(source, renderer.updated_page(source))
        for roman, number in zip(('i', 'ii', 'iii'), ORIGINAL_HASHES):
            self.assertEqual(source.count(f'id="original-{roman}"'), 1)
            self.assertIn(f'href="/bitcoin-inscription-mirrors/raw/{number}.txt"', source)
        self.assertIn('Original I is English', source)
        self.assertIn('Later commentary / 后期说明', source)
        self.assertNotIn('非站方翻译', source)
        self.assertGreater(source.index('class="inscription-commentary"'), source.index(renderer.END))

    def test_removing_a_paragraph_from_each_original_is_detected(self):
        source = (ROOT / 'inscriptions.md').read_text()
        for a, raw in renderer.original_records():
            escaped = renderer.escaped_text(raw)
            paragraphs = escaped.split('\n\n')
            self.assertGreater(len(paragraphs), 2)
            broken = source.replace(escaped, '\n\n'.join(paragraphs[:1]+paragraphs[2:]), 1)
            with self.subTest(number=a['inscription_number']), self.assertRaises(AssertionError):
                assert_faithful(broken)

    def test_extra_translation_in_original_is_detected(self):
        source = (ROOT / 'inscriptions.md').read_text()
        with self.assertRaises(AssertionError):
            assert_faithful(source.replace('</pre>', '后期译文</pre>', 1))

    def test_escape_roundtrip_including_carriage_returns_and_liquid(self):
        raw = b'\n<&>\r\n{{ value }}\n'
        parsed = OriginalText(); parsed.feed('<pre data-inscription-number="fixture">'+renderer.escaped_text(raw)+'</pre>')
        self.assertEqual(parsed.bodies['fixture'].encode(), raw)

    def test_inventory_scopes_match_frozen_manifests(self):
        scope = json.loads((ROOT/'api/bitcoin-inscription-mirror-index.json').read_bytes())['inventory_scope']
        index_spec = importlib.util.spec_from_file_location('mirror_index', ROOT/'scripts/build_bitcoin_inscription_mirror_index.py')
        builder = importlib.util.module_from_spec(index_spec); index_spec.loader.exec_module(builder)
        self.assertEqual(scope, builder.inventory_scope())
        self.assertEqual(scope['record_count'], 8)
        self.assertFalse(scope['is_complete_current_address_inventory'])
        for item in (scope, scope['complete_address_snapshot']):
            manifest = json.loads((ROOT/item['proof_manifest']).read_bytes())
            self.assertEqual(item['record_count'], len(manifest['anchors']))
            self.assertEqual(item['proof_created_at_utc'], manifest['created_at_utc'])
            self.assertEqual(item['canonical_count'], sum(a['classification']=='canonical_original' for a in manifest['anchors']))


if __name__ == '__main__':
    unittest.main()
