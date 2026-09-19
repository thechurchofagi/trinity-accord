#!/usr/bin/env python3
"""Publish only the separately reserved, exact-reviewed TA09 package."""
from __future__ import annotations

import hashlib
import html
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from publication_common import DATE, PREVIOUS_RECORD, REPORT, ROOT, STEM, TITLE, VERSION, check_deposit, client, download_public, extract_abstract, load, persist_states, read, save, sha, validate_local_package, validate_record_id
from prepare_zenodo import validate_descendant, validate_previous

PHASE = 'local_review_gate'
IDENTITY = {}


def resolver_matches_record(status, final_url, record_id):
    final = urllib.parse.urlsplit(final_url)
    return (status == 200 and final.scheme == 'https' and final.hostname == 'zenodo.org'
            and not final.username and not final.password and final.port in (None, 443)
            and not final.query and not final.fragment
            and final.path.rstrip('/') in (f'/records/{record_id}', f'/record/{record_id}'))


def check_doi_resolution(doi, record_id):
    """Retry only the anonymous DOI GET; never reinterpret a pending DOI as success."""
    result = {'state': 'RESOLVER_CHECK_UNAVAILABLE', 'matches_record': False}
    for delay in (0, 3, 8):
        if delay:
            time.sleep(delay)
        try:
            request = urllib.request.Request('https://doi.org/' + doi,
                                             headers={'User-Agent': 'TrinityAccord-TA09-DOICheck/1.1'})
            with urllib.request.urlopen(request, timeout=20) as response:
                matched = resolver_matches_record(response.status, response.url, record_id)
                result = {'state': 'RESOLVER_PASS' if matched else 'RESOLVER_TARGET_MISMATCH',
                          'http_status': response.status, 'final_url': response.url, 'matches_record': matched}
            if matched:
                return result
        except Exception as error:
            result = {'state': 'RESOLVER_CHECK_UNAVAILABLE', 'error_type': type(error).__name__, 'matches_record': False}
    return result


def draft_inventory(listing, allowed):
    if not isinstance(listing, list):
        raise RuntimeError('Unexpected draft inventory response')
    remote = {item['filename']: item for item in listing}
    if len(remote) != len(listing) or set(remote) - allowed:
        raise RuntimeError('Unrelated or duplicate draft files; no deletion or publication')
    return remote


def inherited_deletions(listing, allowed):
    """Only exact inherited v1.1 files with obsolete versioned names may be removed."""
    previous_root = ROOT.parents[1]
    previous = json.loads((previous_root / 'publication-record.json').read_text())
    if previous.get('record_id') != PREVIOUS_RECORD or previous.get('version') != '1.1':
        raise RuntimeError('Previous publication receipt changed')
    old = {row['name']:row for row in previous['files']}
    remote = draft_inventory(listing, allowed | set(old))
    removals = []
    for name,item in remote.items():
        if name in allowed:
            continue
        expected = old[name]
        data = (previous_root / 'published' / name).read_bytes()
        if (sha(data) != expected['sha256'] or len(data) != expected['bytes']
                or str(item.get('checksum','')).removeprefix('md5:') != hashlib.md5(data).hexdigest()
                or item.get('filesize') != len(data)):
            raise RuntimeError('Inherited file is not the exact published predecessor: ' + name)
        file_id = item.get('id','')
        import re
        if not re.fullmatch(r'[0-9a-f-]{36}', file_id):
            raise RuntimeError('Unexpected inherited draft file ID')
        removals.append((name,file_id))
    return removals


def run():
    global PHASE, IDENTITY
    expected, manifest_sha = validate_local_package()
    IDENTITY = {key: expected[key] for key in ('record_id', 'doi')}
    rid, doi = expected['record_id'], expected['doi']
    files = expected['files']
    names = {item['name'] for item in files}
    abstract = extract_abstract((ROOT / 'published' / f'{STEM}-v{VERSION}.md').read_text(encoding='utf-8'))
    z = client()
    lineage = load('deposit.json')
    previous = read(z, f'/deposit/depositions/{PREVIOUS_RECORD}')
    concept = validate_previous(previous)
    if str(lineage.get('conceptrecid')) != concept:
        raise RuntimeError('Reserved version lineage differs from predecessor')
    PHASE = 'read_reserved_record'
    deposit = read(z, f'/deposit/depositions/{rid}')
    validate_descendant(deposit, concept)
    check_deposit(deposit, expected)
    already_published = bool(deposit.get('submitted'))
    if not already_published:
        PHASE = 'update_ninth_record_metadata'
        description = '<p>' + html.escape(abstract) + '</p><p>TA-TR-2026-09, version 1.2. A revised version of the same ninth paper, linked to the published v1.1 predecessor (10.5281/zenodo.22844928). It develops a case of AI-taught changes in assessment standards, narrows the claim about selected consensus, and distinguishes conditional mastery, categorical belief, and qualified expert reliance. Method: conceptual analysis and stipulated thought experiments, with no empirical or computational experiment. The English text is the full paper; the Chinese companion is an argument guide, not a full translation or another paper. Fourteen assets comprise both texts in PDF, DOCX, Markdown and HTML, three citation formats, review notes, license and checksums.</p><p>Human author of record and responsible depositor: Hongju Liu. Generative AI substantially assisted literature research, conceptual development, drafting, counterargument generation, critical revision and document preparation under human direction. Not peer reviewed; no separate final human line-by-line review is claimed. The author\'s Trinity Accord project relationship is disclosed. This revision does not amend the three Bitcoin Originals. Prior version files are preserved.</p><p>CC BY 4.0 applies to newly written material to the extent rights are held; third-party works and embedded font software retain their own rights. DOI registration does not certify philosophical truth, exhaustive originality, peer review or Google Scholar indexing. OTS and Arweave preservation are separate, version-specific operations.</p>'
        metadata = {'upload_type': 'publication', 'publication_type': 'preprint', 'title': TITLE,
                    'creators': [{'name': 'Liu, Hongju', 'affiliation': 'Independent researcher, Shenzhen, China'}],
                    'description': description, 'publication_date': DATE, 'version': VERSION,
                    'access_right': 'open', 'license': 'cc-by-4.0', 'language': 'eng',
                    'keywords': ['AI consciousness', 'scientific understanding', 'epistemic dependence', 'epistemology', 'thought experiments', 'AI ethics']}
        deposit = z.request(f'/deposit/depositions/{rid}', 'PUT', {'metadata': metadata})
        validate_descendant(deposit, concept)
        check_deposit(deposit, expected)
        PHASE = 'remove_only_exact_inherited_obsolete_files_from_new_draft'
        validate_record_id(rid)
        if deposit.get('submitted'):
            raise RuntimeError('Never delete files from a submitted record')
        removals = inherited_deletions(read(z, f'/deposit/depositions/{rid}/files'), names)
        for name,file_id in removals:
            try:
                z.request(f'/deposit/depositions/{rid}/files/{file_id}', 'DELETE')
            except json.JSONDecodeError:
                # The established client expects JSON; a successful DELETE returns an empty 204.
                pass
        if any(item['filename'] not in names for item in read(z, f'/deposit/depositions/{rid}/files')):
            raise RuntimeError('Inherited obsolete files remain; publication blocked')
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
        persist_states({'publication-attempt.json'})
        result = z.request(f'/deposit/depositions/{rid}/actions/publish', 'POST')
        check_deposit(result, expected)
        if not result.get('submitted'):
            raise RuntimeError('Publication response is not submitted')
    PHASE = 'anonymous_public_metadata_readback'
    public = read(z, f'/records/{rid}', authenticated=False)
    if str(public.get('conceptrecid')) != concept:
        raise RuntimeError('Public version lineage mismatch')
    if (public.get('id'), public.get('doi'), public.get('metadata', {}).get('title'), public.get('metadata', {}).get('version')) != (rid, doi, TITLE, VERSION):
        raise RuntimeError('Public record identity mismatch')
    remote = {item['key']: item for item in public.get('files', [])}
    if len(remote) != 14 or set(remote) != names or len(public.get('files', [])) != 14:
        raise RuntimeError('Public file inventory mismatch')
    PHASE = 'anonymous_complete_file_readback'
    output = Path('/tmp/ta09-public-readback')
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
    resolver = check_doi_resolution(doi, rid)
    completed = resolver.get('matches_record') is True
    receipt = {'state': 'PUBLISHED_AND_PUBLIC_READBACK_PASS' if completed else 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING',
               'report_number': REPORT, 'title': TITLE, 'version': VERSION,
               **IDENTITY, 'record_url': f'https://zenodo.org/records/{rid}', 'submitted': True, 'file_count': len(rows), 'files': rows,
               'expected_manifest_sha256': manifest_sha, 'public_readback_authenticated': False, 'doi_resolver': resolver,
               'public_file_readback_pass': True, 'doi_resolution_pass': completed,
               'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'was_already_published': already_published,
               'conceptrecid':concept, 'conceptdoi':f'10.5281/zenodo.{concept}',
               'previous_record_id':PREVIOUS_RECORD, 'previous_doi':f'10.5281/zenodo.{PREVIOUS_RECORD}',
               'prior_doi_records_modified': False, 'prior_version_files_modified':False,
               'version_relationship': 'NEW_VERSION_OF_SAME_PAPER', 'bitcoin_originals_modified': False, 'new_research_papers': 0,
               'peer_reviewed': False, 'global_originality_certified': False, 'google_scholar_indexing': 'NOT_ASSERTED',
               'chinese_companion_role': 'ARGUMENT_GUIDE_NOT_FULL_TRANSLATION'}
    save('publication-record.json', receipt)
    save('publication-attempt.json', {'state': receipt['state'], **IDENTITY, 'phase': 'completed', 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')})
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    if not completed:
        raise RuntimeError('Published files passed anonymous readback, but DOI resolution is pending; resume the same record without republishing')


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        save('publication-attempt.json', {'state': 'INCOMPLETE_REQUIRES_REVIEW_OR_SAME_RECORD_RESUMPTION', **IDENTITY, 'phase': PHASE, 'error_type': type(error).__name__, 'error': str(error), 'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'new_record_creation': False})
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
