"""Shared, narrowly scoped publication checks for TA-TR-2026-09."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = 'research/learning-from-ai-claimant-v1-1-20260919'
TITLE = 'Learning from an AI Claimant: Scientific understanding and the justification of artificial consciousness claims'
REPORT = 'TA-TR-2026-09'
VERSION = '1.1'
DATE = '2026-09-19'
PROTECTED = {21675727, 21699878, 21900592, 22761411, 22804542, 22809019, 22830239, 22839629, 22840604, 22842789}
CLIENT_BLOB = 'a0cbc84cc5fd826c06d16456c4adbaa40dabc788'
STEM = 'learning-from-an-ai-claimant'
ALLOWED_FILES = {f'{STEM}{suffix}-v{VERSION}.{extension}' for suffix in ('', '-zh-guide') for extension in ('pdf', 'docx', 'md', 'html')} | {
    'citation.bib', 'citation.ris', 'citation.csl.json', 'REVIEW-AND-SOURCES.md', 'README-LICENSE.txt', 'SHA256SUMS.txt'
}
STATE_FILES = {'create-intent.json', 'deposit.json', 'preparation-attempt.json', 'publication-attempt.json', 'publication-record.json'}
MAX_FILE_BYTES = 10 * 1024 * 1024
FORMAT_GATES = ('source_docx_pdf_text_equal', 'english_references_preserved_across_formats',
                'guide_explicitly_not_full_translation', 'valid_citation_metadata', 'pdf_text_extractable')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name, root=ROOT):
    return json.loads((root / name).read_text(encoding='utf-8'))


def save(name, value, root=ROOT):
    if name not in STATE_FILES:
        raise RuntimeError('Unexpected publication state filename')
    root.mkdir(parents=True, exist_ok=True)
    target = root / name
    temporary = target.with_suffix(target.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(target)


def persist_states(names):
    """Commit only receipt paths on the dedicated branch; never force-push."""
    if not set(names) <= STATE_FILES:
        raise RuntimeError('Unexpected receipt path')
    allowed = {str((ROOT / name).relative_to(REPO)) for name in names}
    paths = [p for p in sorted(allowed) if (REPO / p).exists()]
    if not paths:
        return
    subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], cwd=REPO, check=True)
    subprocess.run(['git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com'], cwd=REPO, check=True)
    subprocess.run(['git', 'add', '--', *paths], cwd=REPO, check=True)
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=REPO, text=True).splitlines()
    if not set(staged) <= allowed:
        raise RuntimeError('Unexpected staged path; no receipt commit')
    if staged:
        subprocess.run(['git', 'commit', '-m', 'research: preserve ninth-paper publication state [skip ci]'], cwd=REPO, check=True)
        subprocess.run(['git', 'push', 'origin', 'HEAD:' + BRANCH], cwd=REPO, check=True)


def client():
    old = ROOT.parent / 'reading-trinity-accord' / 'publish_zenodo.py'
    data = old.read_bytes()
    actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if actual != CLIENT_BLOB:
        raise RuntimeError('Established Zenodo client changed')
    spec = importlib.util.spec_from_file_location('ta09_verified_zenodo_client', old)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    token = os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:
        raise RuntimeError('Publication credential unavailable')
    return module.Zenodo(token)


def read(z, path, authenticated=True):
    """Retry only reads; creation and publication POSTs are never retried blindly."""
    for attempt, delay in enumerate((0, 3, 8, 15)):
        if delay:
            time.sleep(delay)
        try:
            return z.request(path, authenticated=authenticated)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code not in (404, 408, 429, 500, 502, 503, 504):
                raise
            if attempt == 3:
                raise


def validate_record_id(record_id):
    if type(record_id) is not int or record_id <= 0 or record_id in PROTECTED:
        raise RuntimeError('Invalid or protected prior record ID')
    return record_id


def validate_identity(value):
    rid = validate_record_id(value.get('record_id'))
    wanted = (TITLE, REPORT, VERSION, f'10.5281/zenodo.{rid}')
    found = (value.get('title'), value.get('report_number'), value.get('version'), value.get('doi'))
    if found != wanted:
        raise RuntimeError('Ninth-paper local identity mismatch')
    return rid


def check_deposit(deposit, identity=None):
    rid = validate_record_id(deposit.get('id'))
    metadata = deposit.get('metadata', {})
    if (metadata.get('title'), metadata.get('version')) != (TITLE, VERSION):
        raise RuntimeError('Reserved record title/version mismatch')
    if [c.get('name') for c in metadata.get('creators', [])] != ['Liu, Hongju']:
        raise RuntimeError('Reserved record creator mismatch')
    doi = deposit.get('doi') or metadata.get('prereserve_doi', {}).get('doi') or metadata.get('doi')
    if doi != f'10.5281/zenodo.{rid}':
        raise RuntimeError('Reserved DOI mismatch')
    if identity is not None and (rid, doi) != (identity['record_id'], identity['doi']):
        raise RuntimeError('Reserved record does not match reviewed package')
    return rid, doi


def select_existing(rows):
    if not isinstance(rows, list) or len(rows) >= 100:
        raise RuntimeError('Unbounded or unexpected draft search; no creation')
    matching = [r for r in rows if r.get('metadata', {}).get('title') == TITLE]
    if len(matching) > 1:
        raise RuntimeError('Ambiguous matching records; no creation')
    return matching[0] if matching else None


def validate_local_package(root=ROOT):
    expected_bytes = (root / 'EXPECTED-PUBLICATION.json').read_bytes()
    expected = json.loads(expected_bytes)
    validate_identity(expected)
    deposit = load('deposit.json', root)
    validate_identity(deposit)
    if (expected['record_id'], expected['doi']) != (deposit['record_id'], deposit['doi']):
        raise RuntimeError('Expected package differs from reservation')
    review = load('visual-review.json', root)
    digest = sha(expected_bytes)
    if review.get('state') != 'VISUAL_AND_CONTENT_REVIEW_PASS' or review.get('expected_manifest_sha256') != digest:
        raise RuntimeError('Exact current package has no completed visual/content review')
    formats = load('format-checks.json', root)
    for field in FORMAT_GATES:
        if formats.get(field) is not True:
            raise RuntimeError('Required real format check missing: ' + field)
    rows = expected.get('files', [])
    names = {f.get('name') for f in rows}
    if expected.get('file_count') != 14 or len(rows) != 14 or names != ALLOWED_FILES:
        raise RuntimeError('Reviewed publication inventory must contain the exact fourteen allowed files')
    published = root / 'published'
    if published.is_symlink() or {p.name for p in published.iterdir()} != names:
        raise RuntimeError('Unexpected published-directory inventory')
    for item in rows:
        path = published / item['name']
        if path.is_symlink() or not path.is_file():
            raise RuntimeError('Only regular publication files are permitted')
        data = path.read_bytes()
        if not 0 < len(data) <= MAX_FILE_BYTES or len(data) != item.get('bytes') or sha(data) != item.get('sha256'):
            raise RuntimeError('Unreviewed publication bytes: ' + item['name'])
    return expected, digest


def extract_abstract(markdown):
    match = re.search(r'(?m)^#{2,3}\s+Abstract\s*$', markdown)
    if not match:
        raise RuntimeError('English abstract heading missing')
    remainder = markdown[match.end():]
    keywords = re.search(r'(?im)^\s*(?:\*\*)?Keywords\s*:', remainder)
    if not keywords:
        raise RuntimeError('English abstract keyword boundary missing')
    abstract = remainder[:keywords.start()].strip()
    if not abstract or len(abstract) > 6000 or re.search(r'(?m)^#{1,6}\s', abstract):
        raise RuntimeError('Ambiguous English abstract')
    return abstract


def check_public_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname != 'zenodo.org' or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise RuntimeError('Unexpected public file host')
    if parsed.query or parsed.fragment:
        raise RuntimeError('Unexpected public file URL parameters')
    return url


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        check_public_url(new_url)
        return super().redirect_request(request, fp, code, message, headers, new_url)


def download_public(url):
    request = urllib.request.Request(check_public_url(url), headers={'User-Agent': 'TrinityAccord-TA09-PublicReadback/1.1'})
    with urllib.request.build_opener(SameHostRedirect()).open(request, timeout=120) as response:
        check_public_url(response.url)
        data = response.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise RuntimeError('Unexpected public asset size')
    return data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--persist-states', action='store_true')
    args = parser.parse_args()
    if args.persist_states:
        persist_states(STATE_FILES)
