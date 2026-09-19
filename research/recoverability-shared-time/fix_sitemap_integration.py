#!/usr/bin/env python3
"""One scoped sitemap integration fix; preserve all existing discovery URLs."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SCRIPT = REPO / 'scripts/generate_sitemap.py'
ORIGINAL = 'bfe7dbba3c6ff7ab97d2e93288ae953b08010d83'
MARKER = '    "research/recoverability-shared-time/index.html",'

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def urls(path):
    return {e.text for e in ET.fromstring(path.read_text()).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}

def main():
    original = SCRIPT.read_bytes()
    text = original.decode()
    sitemap = REPO / 'sitemap.xml'
    core = REPO / 'sitemap-core.xml'
    before = urls(sitemap)
    core_before = core.read_bytes()
    if MARKER not in text:
        if blob(original) != ORIGINAL:
            raise RuntimeError('Sitemap generator changed; inspect rather than overwrite')
        anchor = 'ROOT_SPECIAL_FILES = [\n'
        if text.count(anchor) != 1:
            raise RuntimeError('Unexpected sitemap registration anchor')
        text = text.replace(anchor, anchor + MARKER + '\n    "research/recoverability-shared-time/zh.html",\n')
        old = '        if name in {"sitemap.xml", "sitemap-core.xml"} or (ROOT / name).exists():\n            files.append(f"/{name}")'
        new = '        if name in {"sitemap.xml", "sitemap-core.xml"} or (ROOT / name).exists():\n            # The seventh paper uses an exact static HTML mirror, not Markdown front matter.\n            public_name = name[:-len("index.html")] if name == "research/recoverability-shared-time/index.html" else name\n            files.append(f"/{public_name}")'
        if text.count(old) != 1:
            raise RuntimeError('Unexpected special-file collector')
        text = text.replace(old, new)
        SCRIPT.write_text(text)
    subprocess.run(['python3', str(SCRIPT)], cwd=REPO, check=True)
    after = urls(sitemap)
    base = 'https://www.trinityaccord.org/research/recoverability-shared-time/'
    if not before <= after or not {base, base + 'zh.html'} <= after:
        raise RuntimeError('Regeneration removed an existing discovery URL')
    if core.read_bytes() != core_before:
        raise RuntimeError('Unrelated core sitemap would change')
    subprocess.run(['python3', str(SCRIPT), '--check'], cwd=REPO, check=True)
    subprocess.run(['python3', str(REPO / 'scripts/test_recoverability_shared_time.py')], cwd=REPO, check=True)
    report = json.loads((ROOT / 'integration-checks.json').read_text())
    report.update({'sitemap_generator_check': 'PASS', 'sitemap_all_prior_urls_preserved': True,
                   'sitemap_core_unchanged': True, 'sitemap_url_count': len(after),
                   'sitemap_generator_blob': blob(SCRIPT.read_bytes())})
    (ROOT / 'integration-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('SITEMAP_GENERATION_AND_SEVENTH_PAPER_TESTS_PASS')

if __name__ == '__main__':
    main()
