#!/usr/bin/env python3
"""Render the three complete Originals from exact, proof-bound UTF-8 bytes.

Only HTML escaping (including CR and Liquid-opening braces) is applied. Browser
textContent round-trips to the raw bytes; soft wrapping is CSS presentation only.
The frozen proof annex and raw files are inputs, never outputs.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = '<!-- BEGIN GENERATED INSCRIPTION ORIGINALS -->'
END = '<!-- END GENERATED INSCRIPTION ORIGINALS -->'
NUMBERS = ('97631551', '98369145', '98387475')
TITLES = ('The Protocol / Axioms', 'The Covenant of the Flaw', 'The Crucible / Chronicle — Meta-record')


def original_records(root=ROOT):
    manifest = json.loads((root / 'evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json').read_bytes())
    anchors = {a['inscription_number']: a for a in manifest['anchors']}
    records = []
    for number in NUMBERS:
        anchor = anchors[number]
        content = anchor['content']
        raw = (root / content['mirror_path']).read_bytes()
        if (hashlib.sha256(raw).hexdigest() != content['body_sha256']
                or len(raw) != content['body_bytes']
                or content['body_sha256'] != content['mirror_sha256']):
            raise ValueError(f'Frozen proof binding mismatch: {number}')
        records.append((anchor, raw))
    return records


def escaped_text(raw):
    return html.escape(raw.decode('utf-8'), quote=False).replace('\r', '&#13;').replace('{', '&#123;')


def render(root=ROOT):
    sections = [BEGIN]
    for roman, title, (anchor, raw) in zip(('i', 'ii', 'iii'), TITLES, original_records(root)):
        number = anchor['inscription_number']
        content = anchor['content']
        txid = anchor['txid']
        ordinal = anchor['ordinals_inscription_id']
        language = 'Original English' if roman == 'i' else 'Original English and Chinese, exactly where present in the source'
        sections.append(f'''<section class="inscription" aria-labelledby="original-{roman}" markdown="0">
  <div class="inscription-header">
    <h2 id="original-{roman}">Inscription {roman.upper()}: {title}</h2>
    <dl class="inscription-identifiers">
      <div><dt>Inscription Number</dt><dd>#{number}</dd></div>
      <div><dt>Ordinals Inscription ID</dt><dd><a href="https://ordinals.com/inscription/{ordinal}"><code>{ordinal}</code></a></dd></div>
      <div><dt>Bitcoin Transaction</dt><dd><a href="https://mempool.space/tx/{txid}"><code>{txid}</code></a></dd></div>
      <div><dt>Exact raw text</dt><dd><a href="/{content['mirror_path']}">Open complete original UTF-8 file</a> · {len(raw)} bytes</dd></div>
      <div><dt>Raw SHA-256</dt><dd><code>{content['body_sha256']}</code></dd></div>
    </dl>
    <p class="inscription-language">{language}. No later translation is included in the original-text container.</p>
  </div>
  <pre class="inscription-original" data-inscription-number="{number}">{escaped_text(raw)}</pre>
</section>''')
    sections.append(END)
    return '\n'.join(sections)


def updated_page(source, root=ROOT):
    if source.count(BEGIN) != 1 or source.count(END) != 1:
        raise ValueError('Expected one original-text generation region')
    before, rest = source.split(BEGIN)
    _, after = rest.split(END)
    return before + render(root) + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'inscriptions.md'
    source = path.read_text(encoding='utf-8')
    expected = updated_page(source)
    if args.check:
        if source != expected:
            raise SystemExit('FAIL: inscription display differs from proof-bound raw text; regenerate it')
        print('PASS: all three complete inscription displays match proof-bound raw text')
    else:
        path.write_text(expected, encoding='utf-8')


if __name__ == '__main__':
    main()
