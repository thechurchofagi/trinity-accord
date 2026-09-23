"""Publication regressions: parse HTML, never execute downloaded examples."""
from html import escape
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_deployment_freshness as freshness
import check_deployment_freshness_v2_core as v2


VERIFY = """<main><h2>Current digital profiles</h2><h2>Legacy mapping</h2>
<ul><li><strong>Read only:</strong> <a href="/inscriptions/">Originals</a></li>
<li><strong>Check locally:</strong> <a href="/agent-verify-simple/">local check</a></li>
<li><strong>Publish voluntarily:</strong> <a href="/agent-first-contact/">formal route</a></li></ul>
<p>You can stop with a local result.</p></main>"""


def simple_page():
    source = (ROOT / "agent-verify-simple.md").read_bytes().decode()
    blocks = re.findall(r"^```[^\n]*\n(.*?)^```[ \t]*$", source, re.M | re.S)
    # Deliberately small HTML fixture; the real Jekyll build is tested separately.
    # All code is from reviewed source, not a remote page or a second transcription.
    return """<main><h2>Five questions for any result</h2><h2>Read results without a score</h2>
<p>Stopping does not require a public notice.
No Git, clone, Builder, identity key or Gateway is needed.
Inputs from the same project; this does not verify the Git object chain;
not independent chain verification.</p>
<h4 id="without-a-checkout-fetch-two-fixed-snapshot-inputs">Two files</h4>
<h4 id="with-an-existing-git-snapshot-check-committed-bytes-offline">Git</h4>
<h3 id="existing-offline-proof-route">Annex</h3>
<a href="/agent-verify/">Formal</a><a href="/external-agent-quickstart/">Quickstart</a>
""" + "".join('<details><summary>Example</summary><pre><code>' + escape(block) +
                   '</code></pre></details>' for block in blocks[:2]) + "".join(
        '<pre><code>' + escape(block) + '</code></pre>' for block in blocks[2:]
    ) + '<details><summary>Annex</summary></details><details><summary>Compatibility</summary></details></main>'


def errors(path, page):
    result = []
    freshness.check_static_page(path, page, result)
    return result


def test_current_entries_and_html_encoding_pass():
    assert not errors('/verify/', VERIFY)
    page = simple_page()
    assert not errors('/agent-verify-simple/', page)
    # Highlighting and equivalent entities change markup, not decoded code text.
    page = page.replace('import hashlib', '<span class="k">import</span> hashlib')
    page = page.replace('&lt;', '&#x3c;').replace('&#x27;', '&#39;')
    assert not errors('/agent-verify-simple/', page)


def test_pre_w1_verify_markers_alone_cannot_pass():
    old = '<main><h2>Current digital profiles</h2><h2>Legacy mapping</h2><a href="/agent-first-contact/">Start here</a></main>'
    assert all(marker in old for marker in freshness.STATIC_PAGE_MARKERS['/verify/'])
    assert errors('/verify/', old)


@pytest.mark.parametrize('href', ['/inscriptions/', '/agent-verify-simple/', '/agent-first-contact/'])
def test_missing_choice_link_fails_even_with_navigation_link(href):
    page = '<nav><a href="' + href + '">navigation</a></nav>' + VERIFY.replace(href, '/wrong/')
    assert errors('/verify/', page)


def test_local_stop_boundary_must_be_visible_content():
    page = VERIFY.replace('You can stop with a local result.', '')
    page += '<!-- You can stop with a local result. --><script>You can stop with a local result.</script>'
    assert errors('/verify/', page)


@pytest.mark.parametrize('old,new', [
    ('without-a-checkout-fetch-two-fixed-snapshot-inputs', 'removed'),
    ('/agent-verify/', '/wrong/'),
    ('does not verify the Git object chain', 'proves everything'),
    ('<details>', '<details open>'),
])
def test_missing_route_limit_or_native_closed_panel_fails(old, new):
    assert errors('/agent-verify-simple/', simple_page().replace(old, new))


@pytest.mark.parametrize('mutate', [
    lambda p: p.replace('import hashlib', 'import hashliX', 1),
    lambda p: p.replace('    url = base', 'url = base', 1),
    lambda p: p.replace('PY\n</code>', 'PY</code>', 1),
    lambda p: p.replace('import hashlib\n', 'import hashlib \n', 1),
    lambda p: re.sub(r'<pre><code>.*?</code></pre>', '', p, count=1, flags=re.S),
    lambda p: p.replace('</main>', '<pre>unexpected executable block\n</pre></main>'),
])
def test_code_corruption_not_hidden_by_matching_keywords_or_trimming(mutate):
    assert errors('/agent-verify-simple/', mutate(simple_page()))


@pytest.mark.parametrize('module', [freshness, v2])
@pytest.mark.parametrize('missing', [False, True])
def test_existing_live_commands_include_simple_page_and_fail_when_missing(monkeypatch, module, missing):
    assert '/agent-verify-simple/' in freshness.STATIC_PAGE_MARKERS
    assert 'agent-verify-simple.md' in freshness.STATIC_SOURCE_FILES
    monkeypatch.setattr(freshness, 'STATIC_PAGE_MARKERS', {
        p: freshness.STATIC_PAGE_MARKERS[p] for p in ['/verify/', '/agent-verify-simple/']})
    monkeypatch.setattr(freshness, 'SURFACES', [])
    monkeypatch.setattr(v2, 'DEPLOYMENT_BYTE_SURFACES', [])
    requested = []
    def read_live(site, path, token, timeout):
        requested.append(path)
        if missing and path == '/agent-verify-simple/':
            raise FileNotFoundError('synthetic missing page')
        return (VERIFY if path == '/verify/' else simple_page()).encode()
    monkeypatch.setattr(freshness, 'read_live', read_live)
    monkeypatch.setattr(sys, 'argv', ['check', '--site', 'https://fixture.invalid'])
    assert module.main() == (1 if missing else 0)
    assert requested == ['/verify/', '/agent-verify-simple/']
