"""Guard the complete reading object, English output, and navigable chapters."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.text = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
    def handle_data(self, data):
        self.text.append(data)

def test_chapters_resolve_once_and_in_reading_order():
    home = Elements(); home.feed((ROOT / 'index.md').read_text())
    toc = Elements(); toc.feed((ROOT / '_includes/home-page-toc.html').read_text())
    chapters = [href[1:] for href in toc.links]
    assert len(chapters) == 9
    assert all(home.ids.count(chapter) == 1 for chapter in chapters)
    assert [home.ids.index(chapter) for chapter in chapters] == sorted(home.ids.index(chapter) for chapter in chapters)

def test_english_homepage_keeps_full_reading_and_verification_boundaries():
    source = (ROOT / 'index.md').read_text()
    home = Elements(); home.feed(source)
    assert not re.search(r'[\u4e00-\u9fff]', ''.join(home.text))
    assert 'Each Original remains independently citable and verifiable' in source
    assert 'every proposition remains open to individual analysis and criticism' in source
    assert 'Context clarifies meaning; it does not guarantee that an argument is valid' in source
    assert 'Homepage-only context remains' in source
    assert 'legacy freshness compatibility' not in source
    assert source.count('class="home-object-number"') == 3
    for route in ['/research/', '/technical-historical-reference/', '/archive_legacy_index_2025_09/', '/seed-map/', '/llms.txt', '/api/recovery-index.json']:
        assert route in home.links

def test_generated_status_stays_english_and_runtime_is_restored():
    source = (ROOT / 'index.md').read_text()
    generated = source.split('<!-- BEGIN GENERATED PUBLIC STATUS -->')[1].split('<!-- END GENERATED PUBLIC STATUS -->')[0]
    assert not re.search(r'[\u4e00-\u9fff]', generated)
    runtime = source.split('<script>', 1)[1]
    assert "fetch('/api/public-home-status.json'" in runtime
    assert "fetch('/api/waiting-heartbeat-status.json'" in runtime
