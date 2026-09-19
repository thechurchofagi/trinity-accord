#!/usr/bin/env python3
"""Publish only the separately reserved, exact-reviewed TA08 package."""
from __future__ import annotations

import hashlib
import html
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from publication_common import DATE, REPORT, ROOT, STEM, TITLE, VERSION, check_deposit, client, download_public, extract_abstract, read, save, sha, validate_local_package

PHASE = 'local_review_gate'
IDENTITY = {}


def draft_inventory(listing, allowed):
    if not isinstance(listing, list):
        raise RuntimeError('Unexpected draft inventory response')
    remote = {item['filename']: item for item in listing}
    if len(remote) != len(listing) or set(remote) - allowed:
        raise RuntimeError('Unrelated or duplicate draft files; no deletion or publication')
    return remote


def run():
    global PHASE, IDENTITY
    expected, manifest_sha = validate_local_package()
    IDENTITY = {key: expected[key] for key in ('record_id', 'doi')}
    rid, doi = expected['record_id'], expected['doi']
    files = expected['files']
    names = {item['name'] for item in files}
    abstract = extract_abstract((ROOT / 'published' / f'{STEM}-v{VERSION}.md').read_text(encoding='utf-8'))
    z = client()
    PHASE = 'read_reserved_record'
    deposit = read(z, f'/deposit/depositions/{rid}')
    check_deposit(deposit, expected)
    already_published = bool(deposit.get('submitted'))
    if not already_published:
        PHASE = 'update_eighth_record_metadata'
        description = '<p>' + html.escape(abstract) + '</p><p>TA-TR-2026-08, version 1.1. English and complete Chinese texts constitute one philosophical study using conceptual analysis and thought experiments. Fourteen assets include both PDF, DOCX, Markdown and HTML full texts, three citation formats, source/review notes, license and checksums. No computer experiment or demonstrated effect on model behavior is claimed.</p><p>Human author of record and responsible depositor: Hongju Liu. Substantial literature research, conceptual development, critical revision, drafting, translation and package preparation: OpenAI ChatGPT and Codex systems under human direction. Not peer reviewed; no separate final human line-by-line review is claimed. The first-party relationship to the Trinity Accord is disclosed. This is a separate non-amending paper, not a replacement of any previous DOI or a Bitcoin Original. This first DOI edition is version 1.1; version 1.0 was an unpublished working draft.</p><p>CC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works and embedded font software retain their own rights. DOI registration and file-format checks do not establish philosophical truth, exhaustive originality, peer review or Google Scholar indexing.</p>'
        metadata = {'upload_type': 'publication', 'publication_type': 'preprint', 'title': TITLE,
                    'creators': [{'name': 'Liu, Hongju', 'affiliation': 'Independent researcher, Shenzhen, China'}],
                    'description': description, 'publication_date': DATE, 'version': VERSION,
                    'access_right': 'open', 'license': 'cc-by-4.0', 'language': 'eng',
                    'keywords': ['AI self reports', 'AI consciousness', 'epistemology', 'language training', 'thought experiments', 'AI ethics']}
        deposit = z.request(f'/deposit/depositions/{rid}', 'PUT', {'metadata': metadata})
        check_deposit(deposit, expected)
        PHASE = 'upload_exact_reviewed_files'
        remote = draft_inventory(read(z, f'/deposit/depositions/{rid}/files'), names)
        bucket = deposit['links']['bucket']
        parsed = urllib.parse.urlsplit(bucket)
        if parsed.scheme != 'https' or parsed.hostname != 'zenodo.org' or parsed.username or parsed.password or parsed.port not in (None, 443) or parsed.query or parsed.fragment or not parsed.path.startswith('/api/files/'):
            raise RuntimeError('Unexpected draft upload bucket')
        for item in files:
            data = (ROOT / 'published' / item['name']).read_bytes()
            checksum = hashlib.md5(data).hexdigest()
            previous = remote.get(item['name'])
            if previous and str(previous.get('checksum', '')).removeprefix('md5:') == checksum and previous.get('filesize') == len(data):
                continue
            z.request(bucket.rstrip('/') + '/' + urllib.parse.quote(item['name'], safe=''), 'PUT', data, binary=True)
        PHASE = 'verify_complete_draft'
        remote = draft_inventory(read(z, f'/deposit/depositions/{rid}/files'), names)
        if set(remote) != names:
            raise RuntimeError('Draft inventory differs from reviewed package')
        for item in files:
            data = (ROOT / 'published' / item['name']).read_bytes()
            actual = remote[item['name']]
            if str(actual.get('checksum', '')).removeprefix('md5:') != hashlib.md5(data).hexdigest() or actual.get('filesize') != len(data):
                raise RuntimeError('Draft checksum/size mismatch: ' + item['name'])
        # A resume never creates or edits a published record; the initial publication is explicit.
        PHASE = 'publish_reserved_record'
        save('publication-attempt.json', {'state': 'PUBLICATION_INTENT_FOR_EXISTING_RECORD', **IDENTITY, 'expected_manifest_sha256': manifest_sha, 'new_record_creation': False, 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')})
        result = z.request(f'/deposit/depositions/{rid}/actions/publish', 'POST')
        check_deposit(result, expected)
        if not result.get('submitted'):
            raise RuntimeError('Publication response is not submitted')
    PHASE = 'anonymous_public_metadata_readback'
    public = read(z, f'/records/{rid}', authenticated=False)
    if (public.get('id'), public.get('doi'), public.get('metadata', {}).get('title'), public.get('metadata', {}).get('version')) != (rid, doi, TITLE, VERSION):
        raise RuntimeError('Public record identity mismatch')
    remote = {item['key']: item for item in public.get('files', [])}
    if len(remote) != 14 or set(remote) != names or len(public.get('files', [])) != 14:
        raise RuntimeError('Public file inventory mismatch')
    PHASE = 'anonymous_complete_file_readback'
    output = Path('/tmp/ta08-public-readback')
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in files:
        url = remote[item['name']]['links'].get('self') or remote[item['name']]['links'].get('download')
        data = download_public(url)
        if len(data) != item['bytes'] or sha(data) != item['sha256']:
            raise RuntimeError('Public exact-byte mismatch: ' + item['name'])
        (output / item['name']).write_bytes(data)
        rows.append(dict(item, public_url=url))
    PHASE = 'doi_resolver_check'
    try:
        request = urllib.request.Request('https://doi.org/' + doi, headers={'User-Agent': 'TrinityAccord-TA08-DOICheck/1.1'})
        with urllib.request.urlopen(request, timeout=30) as response:
            final = urllib.parse.urlsplit(response.url)
            resolver = {'http_status': response.status, 'final_url': response.url, 'matches_record': final.hostname == 'zenodo.org' and final.path.rstrip('/') in (f'/records/{rid}', f'/record/{rid}')}
    except Exception as error:
        resolver = {'state': 'RESOLVER_CHECK_UNAVAILABLE', 'error_type': type(error).__name__}
    receipt = {'state': 'PUBLISHED_AND_PUBLIC_READBACK_PASS', 'report_number': REPORT, 'title': TITLE, 'version': VERSION,
               **IDENTITY, 'record_url': f'https://zenodo.org/records/{rid}', 'submitted': True, 'file_count': len(rows), 'files': rows,
               'expected_manifest_sha256': manifest_sha, 'public_readback_authenticated': False, 'doi_resolver': resolver,
               'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'was_already_published': already_published,
               'prior_doi_records_modified': False, 'bitcoin_originals_modified': False, 'new_research_papers': 1,
               'peer_reviewed': False, 'global_originality_certified': False, 'google_scholar_indexing': 'NOT_ASSERTED'}
    save('publication-record.json', receipt)
    save('publication-attempt.json', {'state': receipt['state'], **IDENTITY, 'phase': 'completed', 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')})
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        save('publication-attempt.json', {'state': 'INCOMPLETE_REQUIRES_REVIEW_OR_SAME_RECORD_RESUMPTION', **IDENTITY, 'phase': PHASE, 'error_type': type(error).__name__, 'error': str(error), 'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'new_record_creation': False})
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
