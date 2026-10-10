#!/usr/bin/env python3
"""Prepare a guarded CTD publication overlay; NEVER write the source repository.

Input receipt schema is the actual CTD publication.py output. A reservation fails
the first gate. No network requests, Git mutations, fitting or simulation occur.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
WS = Path('research/uct-agent-consciousness-workspace')
RECORD = 'records/CTD20261010_Noise_Identifiability_v10'
WORK = 'TA-TR-2026-26'
VERSION = '1.0.0'
MAP = 'UCT-MAP-v1.1.2'
GRAPH_SHA = '0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612'
REVIEW_SHA = '0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687'
MD_NAME = 'noise-identifiability-bodily-judgments-v1.0.0.md'
PDF_NAME = 'noise-identifiability-bodily-judgments-v1.0.0.pdf'
ZIP_NAME = 'reproducibility-v1.0.0.zip'
PUBLIC_NAMES = {MD_NAME, PDF_NAME, ZIP_NAME, 'README-LICENSE.txt', 'REVIEW-AND-SOURCES.md',
                'SHA256SUMS.txt', 'citation.bib', 'citation.csl.json', 'citation.ris'}
NAV_JSON = ['PUBLICATION_COVERAGE.json', 'CURRENT_STATE.json', 'RESEARCH_REGISTRY.json',
            'RESEARCH_SESSION_LOG_INDEX.json', 'UCT_FORMAL_GRAPH_MODULES.json']
NAV_MD = ['AGENTS.md', 'MEMORY.md', 'HANDOFF.md', 'MASTER_INDEX.md', 'CHANGELOG.md']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def jd(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def git_file(repo, rel):
    return subprocess.check_output(['git', '-C', str(repo), 'show', 'HEAD:' + safe_rel(rel)])


def git_path_present(repo, rel):
    return bool(git(repo, 'ls-tree', '-r', '--name-only', 'HEAD', '--', safe_rel(rel)))


def current_id(item):
    return item.get('id', item.get('research_id')) if isinstance(item, dict) else item


def safe_rel(text):
    p = PurePosixPath(text)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in text,
            'Unsafe relative path')
    require(str(p) not in ('', '.'), 'Empty relative path')
    return str(p)


def metadata(path):
    b = Path(path).read_bytes()
    return {'bytes': len(b), 'sha256': sha(b)}


def publication_counts(works):
    """Recompute, preserving multiple DOI records with one version label."""
    seen_work, doi_owner = set(), {}
    research_works, editorial_works, research_pairs = set(), set(), set()
    research_dois, editorial_dois = set(), set()
    for work in works:
        wid = work['work_id']
        require(wid not in seen_work, f'Duplicate work ID: {wid}')
        seen_work.add(wid)
        require(work['work_type'] in ('research_preprint', 'editorial_supplement'),
                f'Unrecognized publication work type: {wid}')
        included_dois, included_labels = set(), set()
        for version in work['versions']:
            if version.get('reserved_only') is True:
                continue
            require(version.get('reserved_only') is False,
                    f'Publication reservation state must be explicit: {wid}')
            require(str(version.get('publication_status', '')).startswith('PUBLISHED'),
                    f'Non-published version in published inventory: {wid}')
            doi = version['doi'].lower()
            require(doi not in doi_owner, f'DOI counted twice: {doi}')
            doi_owner[doi] = wid
            label = version['version_label']
            included_dois.add(doi)
            included_labels.add(label)
            if work['work_type'] == 'editorial_supplement':
                editorial_works.add(wid)
                editorial_dois.add(doi)
            else:
                research_works.add(wid)
                research_pairs.add((wid, label))
                research_dois.add(doi)
        require(work['published_doi_record_count'] == len(included_dois),
                f'Work DOI subtotal mismatch: {wid}')
        require(work['distinct_version_label_count'] == len(included_labels),
                f'Work version-label subtotal mismatch: {wid}')
    return {
        'distinct_research_works': len(research_works),
        'distinct_research_work_version_label_pairs': len(research_pairs),
        'distinct_published_research_doi_records': len(research_dois),
        'separate_editorial_supplement_works': len(editorial_works),
        'separate_editorial_doi_records': len(editorial_dois),
        'all_verified_publication_doi_records_including_editorial': len(doi_owner),
        'uninspected_live_account_drafts': 'NOT_ENUMERATED',
        'reserved_only_records_within_verified_publication_records': 0,
    }


def choose_coverage(workspace, current, repo=None):
    pat = re.compile(r'^UCT-PUB-v(\d+)\.(\d+)\.(\d+)$')
    m = pat.fullmatch(current)
    require(m is not None, 'Unknown coverage version format')
    major, minor, patch = map(int, m.groups())
    names = {p.name for p in (workspace / 'publication').iterdir()}
    if repo is not None:
        names.update(git(repo, 'ls-tree', '-d', '--name-only', 'HEAD:' + str(WS / 'publication')).splitlines())
    for name in names:
        m = pat.fullmatch(name)
        if m and tuple(map(int, m.groups()[:2])) == (major, minor):
            patch = max(patch, int(m.group(3)))
    return f'UCT-PUB-v{major}.{minor}.{patch + 1}'


def verified_publication(receipt_path, public_dir):
    r = load(receipt_path)
    require(r.get('submitted') is True, 'Reserved or unsubmitted record is not publication')
    require(str(r.get('state', '')).startswith('PUBLISHED'), 'Receipt is not a publication receipt')
    require(r.get('public_file_readback_pass') is True and
            r.get('public_readback_authenticated') is False,
            'Anonymous exact public-file readback is required')
    require(r.get('version') == VERSION and r.get('report_number') == WORK,
            'Wrong CTD work/version')
    require(r.get('peer_reviewed') is False and r.get('c1_empirically_validated') is False,
            'Publication receipt changes a prohibited scientific claim')
    require(r.get('prior_records_modified') is False, 'Prior-record mutation needs separate review')
    rid = str(r['record_id'])
    require(rid.isdigit() and r['doi'] == '10.5281/zenodo.' + rid, 'Wrong version DOI identity')
    require(r['record_url'] == 'https://zenodo.org/records/' + rid, 'Wrong record URL')
    files = r['files']
    require(len(files) == r['file_count'] and len({f['name'] for f in files}) == len(files),
            'Public inventory count/uniqueness failure')
    require({f['name'] for f in files} == PUBLIC_NAMES,
            'Public receipt differs from the publisher\'s exact nine-file inventory')
    for f in files:
        require(safe_rel(f['name']) == Path(f['name']).name, 'Public filename is not a basename')
        require(f.get('public_url', '').startswith(('https://zenodo.org/', 'https://zenodo.org:443/')),
                'Missing authoritative anonymous public-file URL')
        b = (public_dir / f['name']).read_bytes()
        require((len(b), sha(b)) == (f['bytes'], f['sha256']),
                'Local public asset differs from actual readback receipt: ' + f['name'])
    manifest = receipt_path.parent / 'EXPECTED-PUBLICATION.json'
    if manifest.exists():
        require(sha(manifest.read_bytes()) == r['expected_manifest_sha256'],
                'Expected-publication manifest differs from actual receipt')
    return r


def extract_scientific_archive(archive_bytes):
    archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    require(archive.testzip() is None, 'Public ZIP CRC failure')
    rows = [i for i in archive.infolist() if not i.is_dir()]
    require(len({i.filename for i in rows}) == len(rows), 'Duplicate ZIP file')
    roots = {PurePosixPath(safe_rel(i.filename)).parts[0] for i in rows}
    require(len(roots) == 1, 'ZIP must have one scientific-record root')
    root = roots.pop()
    result = {}
    for i in rows:
        require((i.external_attr >> 16) & 0o170000 != 0o120000, 'ZIP contains a symlink')
        rel = safe_rel(str(PurePosixPath(i.filename).relative_to(root)))
        result[rel] = archive.read(i.filename)
    manifest = json.loads(result['FILE_MANIFEST.json'])
    require(manifest['version'] == VERSION and manifest['report_number'] == WORK,
            'Archive scientific identity mismatch')
    expected = {x['path']: x for x in manifest['files']}
    require(len(expected) == manifest['file_count_excluding_manifest'], 'Manifest count failure')
    require(set(result) == set(expected) | {'FILE_MANIFEST.json'}, 'ZIP/manifest membership mismatch')
    for rel, item in expected.items():
        b = result[rel]
        require((len(b), sha(b)) == (item['bytes'], item['sha256']), 'ZIP manifest hash mismatch: ' + rel)
    for stale in ['PUBLICATION_COVERAGE_UPDATE.json', 'PERSISTENCE_RECEIPT.json', 'HANDOFF_ZH.md']:
        require(stale not in result, 'Operational filename unexpectedly inside frozen scientific ZIP')
    return result, root


def append_unique(items, value, key=None):
    identity = current_id if key == 'id' else (lambda x: x.get(key)) if key else (lambda x: x)
    ident = identity(value)
    require(not any(identity(x) == ident for x in items),
            'Entry already present; reconcile rather than duplicate: ' + str(ident))
    items.append(value)


def rows_from_review(review):
    for key in ('entries', 'claims', 'coverage', 'items', 'claim_coverage'):
        if isinstance(review.get(key), list):
            return review[key]
    raise ValueError('Unrecognized independent coverage review schema')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--expected-head', required=True)
    p.add_argument('--publication-receipt', type=Path, required=True)
    p.add_argument('--doi-resolution-receipt', type=Path,
                   help='Optional independent resolver receipt; the original workflow snapshot remains unchanged')
    p.add_argument('--public-dir', type=Path, required=True)
    p.add_argument('--coverage-review', type=Path, default=HERE / 'COVERAGE_REVIEW.json')
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    repo, output = args.repo.resolve(), args.output_dir.resolve()
    require(output != repo and repo not in output.parents, 'Overlay must be outside repository')
    require(not output.exists(), 'Use a new output directory; no overwrite of old plan')
    require(git(repo, 'rev-parse', 'HEAD') == args.expected_head, 'Research HEAD changed; reprepare')
    require(not git(repo, 'status', '--porcelain'), 'Research working tree must be clean')
    workspace = repo / WS
    before = {n: load(workspace / n) for n in NAV_JSON}
    current, oldcov = before['CURRENT_STATE.json'], before['PUBLICATION_COVERAGE.json']
    require(current['release_id'] == MAP and current['complete_map_sha256'] == GRAPH_SHA and
            current['review_ledger_sha256'] == REVIEW_SHA, 'Completed-map baseline changed; review required')
    require(not (workspace / RECORD).exists() and not git_path_present(repo, str(WS / RECORD)),
            'CTD v1.0 record already exists locally or in the sparse Git tree; reconcile, do not overwrite')
    mainline = deepcopy(current['latest_research'])
    mainline_id = current_id(mainline)
    require(isinstance(mainline, dict) and mainline_id, 'Current mainline navigation is not explicit')
    concurrent_ids = [x for x in current['pending_checkpoints_not_promoted']
                      if not x.startswith(('CTD',))]
    mainline_dir = str(PurePosixPath(mainline['source']).parent)
    mainline_module = mainline_dir + '/MAP_EXTENSION.json'
    require(git_path_present(repo, str(WS / mainline_module)),
            'Current mainline extension cannot be anchored in execution-time Git HEAD')
    mainline_module_bytes = git_file(repo, str(WS / mainline_module))
    mainline_map = json.loads(mainline_module_bytes)
    require(mainline_map.get('enabled') is False,
            'Concurrent mainline status requires manual reconciliation')
    mainline_pending = {
        'research_id': mainline_id, 'result_version': mainline['result_version'],
        'source': mainline_module, 'sha256': sha(mainline_module_bytes),
        'status': mainline['status'], 'enabled_as_established_premises': False,
        'actual_application': 'OPEN', 'publication_coverage_version': oldcov['coverage_version'],
        'compatibility_audit': mainline_dir + '/MAP_AUDIT.md',
        'handoff': mainline['handoff'], 'manuscript_status': mainline['manuscript_status'],
        'candidate_counts': {k: len(mainline_map.get(k, [])) for k in ['nodes', 'rules', 'context_links']},
        'preservation_scope': 'Execution-time concurrent research navigation; not republished as a CTD claim.',
    }
    inherited_update_chain = deepcopy(oldcov.get('pending_research_updates', []))
    current_update = oldcov.get('latest_update')
    if current_update and current_update not in inherited_update_chain:
        require(git_path_present(repo, str(WS / current_update)), 'Current concurrent update path is not in HEAD')
        inherited_update_chain.append(current_update)
    receipt = verified_publication(args.publication_receipt, args.public_dir)
    doi, date = receipt['doi'], datetime.now(timezone.utc).isoformat()
    resolver = None
    if args.doi_resolution_receipt:
        resolver = load(args.doi_resolution_receipt)
        require(resolver.get('doi') == doi and str(resolver.get('record_id')) == str(receipt['record_id']) and
                resolver.get('authenticated') is False and resolver.get('state') == 'RESOLVER_PASS' and
                resolver.get('matches_record') is True and resolver.get('http_status') == 200 and
                resolver.get('final_url') == receipt['record_url'],
                'Independent DOI resolver receipt is not a verified match for this record')
    archive, ziproot = extract_scientific_archive((args.public_dir / ZIP_NAME).read_bytes())
    template = archive['manuscript/' + MD_NAME]
    public_md = (args.public_dir / MD_NAME).read_bytes()
    require(template.count(b'__DOI_RESERVED_AT_RELEASE__') == 1, 'Unexpected reviewed DOI-template occurrences')
    normalized_template = template.replace(b'__DOI_RESERVED_AT_RELEASE__', doi.encode())
    # The actual publication builder moves four figure links up one directory.
    # Bind the allowed changes to the links that are truly present in this source.
    source_figure_links = re.findall(rb'\]\(\.\./(figures/[^)]+\.pdf)\)', template)
    require(len(source_figure_links) == 4 and len(set(source_figure_links)) == 4,
            'Unexpected scientific figure-link inventory')
    figure_paths = [x.decode() for x in source_figure_links]
    for rel in figure_paths:
        require(rel in archive, 'Figure named by the public manuscript is absent from the ZIP')
        normalized_template = normalized_template.replace(b'](../' + rel.encode() + b')',
                                                          b'](' + rel.encode() + b')')
    require(normalized_template == public_md,
            'Public manuscript differs from reviewed template beyond the DOI and four figure-path substitutions')
    claims_source = json.loads(archive['CLAIM_LEDGER.json'])
    ctd2 = json.loads(archive['governance/MAP_EXTENSION.json'])
    ctd3 = json.loads(archive['governance/CTD3_MAP_EXTENSION.json'])
    require(ctd3['base_release'] == MAP and ctd3['baseline_graph_sha256'] == GRAPH_SHA,
            'CTD3 candidate baseline mismatch')
    require(ctd3['enabled'] is False and ctd3['enabled_as_established_premise'] is False,
            'Candidate cannot be active')
    for key, n in [('nodes', 5), ('rules', 2), ('context_links', 6)]:
        require(len(ctd3[key]) == n and all(x.get('enabled') is False for x in ctd3[key]),
                'CTD3 candidate counts/disabled state mismatch')
    review = load(args.coverage_review)
    reviewed_rows = rows_from_review(review)
    claim_ids = {c['id'] for c in claims_source['claims']}
    row_ids = {c.get('id', c.get('claim_id')) for c in reviewed_rows}
    require(claim_ids == row_ids and len(row_ids) == 25, 'Incomplete independent 25-node coverage review')
    source_by_id = {c['id']: c for c in claims_source['claims']}
    for r in reviewed_rows:
        c = source_by_id[r.get('id', r.get('claim_id'))]
        require(r['original_statement'] == c['statement'] and
                r['statement_sha256'] == sha(c['statement'].encode()),
                'Independent coverage row does not match the actual source statement')
        require(all(rel in archive for rel in c['evidence_paths']),
                'A claim evidence path is not part of the formal archive')
    # The independent review must name the exact frozen archive and manuscript.
    require(review['manuscript']['sha256'] == sha(template) and
            review['release_attachment']['sha256'] == sha((args.public_dir / ZIP_NAME).read_bytes()) and
            review['source_ledger']['sha256'] == sha(archive['CLAIM_LEDGER.json']),
            'Coverage review is not bound to this exact formal archive/template')

    version = choose_coverage(workspace, oldcov['coverage_version'], repo)
    pubdir = 'publication/' + version
    require(not git_path_present(repo, str(WS / pubdir)),
            'Coverage version exists in sparse Git HEAD; use a newer current coverage entry')
    old_works_path = oldcov['published_works']
    old_ledger_path = oldcov['ledger']['path']
    old_index_path = oldcov['claim_id_index']
    works = load(workspace / old_works_path)
    ledger = load(workspace / old_ledger_path)
    index = load(workspace / old_index_path)
    before_counts = publication_counts(works['works'])
    require(before_counts == works['counts'] == oldcov['publication_counts'] == ledger['publication_counts'],
            'Latest entry and referenced complete inventory/ledger counts disagree')
    require(all(w['work_id'] != WORK for w in works['works']), 'Work already published; review version lineage')
    old_works = deepcopy(works['works'])
    public_files = deepcopy(receipt['files'])
    resolution_pass = receipt.get('doi_resolution_pass') is True or resolver is not None
    status = ('PUBLISHED_PREPRINT_PUBLIC_READBACK_AND_DOI_RESOLUTION_VERIFIED'
              if resolution_pass
              else 'PUBLISHED_PREPRINT_PUBLIC_READBACK_VERIFIED_DOI_RESOLUTION_PENDING')
    pub = {
        'research_id': 'CTD20261010', 'report': WORK, 'version': VERSION,
        'status': status, 'doi': doi, 'doi_url': 'https://doi.org/' + doi,
        'record_url': receipt['record_url'], 'manuscript': RECORD + '/release/' + MD_NAME,
        'pdf': RECORD + '/release/' + PDF_NAME,
        'reproduction': RECORD + '/release/' + ZIP_NAME,
        'receipt': RECORD + '/publication-record.json', 'peer_reviewed': False,
        'scientific_map_admission_changed': False, 'new_human_data': False,
        'doi_resolution_pass': resolution_pass,
        'doi_resolution_source': (RECORD + '/DOI_RESOLUTION.json' if resolver else
                                  RECORD + '/publication-record.json'),
        'publication_workflow_snapshot_unmodified': True,
    }
    version_obj = {
        'work_id': WORK, 'report_labels': [WORK, 'CTD20261010'],
        'title': receipt['title'], 'version_label': VERSION, 'doi': doi,
        'doi_url': pub['doi_url'], 'record_url': receipt['record_url'],
        'work_type': 'research_preprint', 'publication_status': status, 'reserved_only': False,
        'current_audit_live_public_endpoint_recheck': 'Actual workflow anonymous exact-byte readback receipt; this sync makes no additional remote request.',
        'source_commit': receipt.get('source_commit'), 'public_files': public_files,
        'publication_receipt': pub['receipt'], 'journal_peer_reviewed': False,
        'doi_resolution_receipt': pub['doi_resolution_source'],
        'ots_status': receipt.get('ots_status', 'NOT_REPORTED'),
        'arweave_status': receipt.get('arweave_status', 'NOT_REPORTED'),
        'preservation_scope': 'States copied from this publication receipt only; later preservation receipts remain separate.',
    }
    works['works'].append({'work_id': WORK, 'work_type': 'research_preprint',
                          'latest_title': receipt['title'], 'preferred_current_doi': doi,
                          'published_doi_record_count': 1, 'distinct_version_label_count': 1,
                          'versions': [version_obj]})
    after_counts = publication_counts(works['works'])
    for k in ['distinct_research_works', 'distinct_research_work_version_label_pairs',
              'distinct_published_research_doi_records', 'all_verified_publication_doi_records_including_editorial']:
        require(after_counts[k] == before_counts[k] + 1, 'Unexpected publication increment: ' + k)
    require(works['works'][:-1] == old_works, 'Old work objects were modified')
    works['counts'], works['coverage_version'] = after_counts, version
    works['audit_date_utc'] = date
    works['incremental_audit_scope'] = {
        'base_inventory': {'path': old_works_path, **metadata(workspace / old_works_path)},
        'research_head_at_preparation': args.expected_head,
        'counts_are': 'Inherited verified corpus plus this one anonymously verified publication; not a new global census.',
        'prior_read_scope_preserved': True,
    }
    works['receipt_sources'].append({'source': pub['receipt'], 'doi': doi,
                                    'role': 'CTD v1.0 submitted public deposit and anonymous exact readback'})
    zip_meta = next(f for f in public_files if f['name'] == ZIP_NAME)
    works['formal_supplement_packages'].append({
        'doi': doi, 'version': VERSION,
        'zip': {'path': pub['reproduction'], 'bytes': zip_meta['bytes'], 'sha256': zip_meta['sha256']},
        'member_count': len(archive), 'role': 'Explicit CTD-owned claims only; cited prior works are not republished by reference.'})
    works['CTD_v1_0_disclosure_scope'] = {
        'doi': doi, 'claim_node_review': RECORD + '/publication_review/COVERAGE_REVIEW.json',
        'scientific_claim_nodes': 25, 'disabled_rule_records': 9, 'disabled_context_records': 19,
        'completed_graph_or_other_research_republished': False,
        'main_text_and_formal_attachment_scope_are_separate': True,
    }

    # Explicit allow-list: 25 scientific nodes + 9 rules + 19 contexts.
    coverage_rows = []
    for r in reviewed_rows:
        cid = r.get('id', r.get('claim_id'))
        coverage_rows.append({
            'id': cid, 'role': 'disabled_scientific_candidate_node', 'published': True,
            'doi': doi, 'coverage_status': 'covered_exact',
            'coverage_axis': 'Formal disclosure in the official archive; body scope remains separately stated.',
            'independent_scope_review': deepcopy(r),
            'formal_attachment': {'file': ZIP_NAME, 'sha256': zip_meta['sha256'],
                                  'candidate_statement': 'CLAIM_LEDGER.json',
                                  'all_listed_evidence_paths_present': True},
            'enabled_as_established_premise': False, 'actual_application': 'OPEN',
            'publication_implies_validity': False,
        })
    for module_name, module in [('governance/MAP_EXTENSION.json', ctd2),
                                ('governance/CTD3_MAP_EXTENSION.json', ctd3)]:
        for kind in ['rules', 'context_links']:
            for item in module[kind]:
                cid = item['id']
                require(cid.startswith(('CTD2-', 'CTD3-')) and item.get('enabled') is False,
                        'Unexpected non-CTD or active metadata record')
                coverage_rows.append({
                    'id': cid, 'role': 'disabled_' + kind, 'published': True,
                    'doi': doi, 'coverage_status': 'covered_exact',
                    'main_text_coverage': 'NOT_ASSERTED_AS_COMPLETE_FORMAL_RULE_OR_CONTEXT_RECORD',
                    'formal_attachment_coverage': 'EXACT_DISABLED_RECORD_IN_OFFICIAL_ZIP',
                    'formal_attachment': {'file': ZIP_NAME, 'sha256': zip_meta['sha256'], 'member': module_name},
                    'enabled_as_established_premise': False,
                    'publication_implies_validity': False,
                })
    require(len(coverage_rows) == 53 and len({x['id'] for x in coverage_rows}) == 53,
            'Wrong CTD publication coverage allow-list')
    for n, row in enumerate(coverage_rows):
        require(row['id'] not in index['index'], 'Existing claim ID requires explicit reconciliation')
        index['index'][row['id']] = {'path': pubdir + '/CLAIM_COVERAGE_DELTA.json',
                                    'json_pointer': '/claims/' + str(n),
                                    'coverage_status': 'covered_exact', 'role': row['role']}
    index['coverage_version'] = version
    index['scope'] = 'Inherited complete-map and earlier pending/publication entries plus exactly 53 CTD-owned disclosed records. Formal disclosure does not admit a scientific premise.'
    index.setdefault('separate_inherited_pending_indices', []).append(oldcov['claim_delta'])
    if current_update and current_update not in index['separate_inherited_pending_indices']:
        index['separate_inherited_pending_indices'].append(current_update)
    delta = {
        'schema': 'uct-claim-coverage-delta/1', 'coverage_version': version,
        'parent_coverage_version': oldcov['coverage_version'], 'research_id': 'CTD20261010',
        'result_version': 'CTD-RESULT-v1.0.0', 'publication_evidence': pub,
        'scientific_map': MAP, 'nondeductive': True, 'publication_implies_validity': False,
        'unknown_is_unpublished': False, 'claims': coverage_rows,
        'counts': {'scientific_claim_nodes': 25, 'disabled_rules': 9, 'disabled_contexts': 19, 'total': 53},
        'cited_other_research_is_not_automatically_disclosed': True,
        'formal_publication_counts_changed': True, 'publication_counts': after_counts,
    }
    ledger['coverage_version'] = version
    ledger['sequence'] = int(version.rsplit('.', 1)[1]) + 1
    ledger['parent_coverage'] = oldcov['coverage_version']
    ledger['date'] = date[:10]
    ledger['record_id'] = 'CTD20261010_PUBLICATION_V1_0_0'
    ledger['research_base_commit'] = args.expected_head
    ledger['publication_counts'] = after_counts
    ledger['latest_claim_delta'] = pubdir + '/CLAIM_COVERAGE_DELTA.json'
    ledger['documents']['current_publication_inventory'] = pubdir + '/PUBLISHED_WORKS_AND_VERSIONS.json'
    ledger['documents']['current_claim_delta'] = pubdir + '/CLAIM_COVERAGE_DELTA.json'
    ledger['documents']['current_claim_id_index'] = pubdir + '/CLAIM_ID_INDEX.json'
    ledger['publication_increment'] = pub
    ledger['parent_complete_ledger'] = {'path': old_ledger_path, **metadata(workspace / old_ledger_path)}
    ledger['historical_pending_update_chain'] = deepcopy(inherited_update_chain)
    ledger['historical_pending_update_chain'].append(RECORD + '/PUBLICATION_COVERAGE_UPDATE.json')
    ledger['counting_decisions'].append('This actual CTD public readback adds one research work, one version-label pair and one version DOI to the execution-time base; no reservation, concept DOI or older unpublished CTD draft is counted.')
    ledger['manuscript_decision'] = deepcopy(ledger.get('manuscript_decision', {}))
    ledger['manuscript_decision']['CTD'] = status
    ledger['manuscript_decision']['CTD_pre_release_scientific_decision'] = RECORD + '/MANUSCRIPT_DECISION.json'
    ledger['manuscript_decision']['CTD_actual_publication_receipt'] = pub['receipt']
    ledger['new_pending_research'] = RECORD + '/PUBLICATION_COVERAGE_UPDATE.json'
    ledger['inherited_map_item_coverage_scope'] = 'All prior completed-map item classifications and their historical audit scope remain unchanged; the 53-row CTD delta concerns disabled candidates only.'
    ledger['read_scope']['CTD_v1_0'] = 'Independent per-node body/official-ZIP coverage review for 25 nodes, exact archive member checking, and 28 disabled formal metadata records; no new empirical fitting or historical proof audit.'
    ledger['completeness_limits'].append('CTD source/code references to prior work do not confer publication coverage on those works; DOI publication does not close actual-instance, calibration, neural or phenomenal obligations.')

    changes = {}
    def put(rel, data):
        rel = safe_rel(rel)
        require(rel not in changes, 'Duplicate staged path: ' + rel)
        changes[rel] = data if isinstance(data, bytes) else jd(data)

    for rel, b in archive.items():
        put(RECORD + '/' + rel, b)
    for f in public_files:
        put(RECORD + '/release/' + f['name'], (args.public_dir / f['name']).read_bytes())
    for rel in figure_paths:
        put(RECORD + '/release/' + rel, archive[rel])
    put(RECORD + '/publication-record.json', args.publication_receipt.read_bytes())
    if resolver is not None:
        put(RECORD + '/DOI_RESOLUTION.json', args.doi_resolution_receipt.read_bytes())
    put(RECORD + '/publication_review/COVERAGE_REVIEW.json', args.coverage_review.read_bytes())
    review_md = args.coverage_review.with_suffix('.md')
    if review_md.exists():
        put(RECORD + '/publication_review/COVERAGE_REVIEW.md', review_md.read_bytes())
    for rel, obj in [('PUBLISHED_WORKS_AND_VERSIONS.json', works), ('COVERAGE_LEDGER.json', ledger),
                     ('CLAIM_ID_INDEX.json', index), ('CLAIM_COVERAGE_DELTA.json', delta)]:
        put(pubdir + '/' + rel, obj)

    update_path = RECORD + '/PUBLICATION_COVERAGE_UPDATE.json'
    update = {
        'schema': 'uct-publication-coverage-update/1', 'coverage_version': version,
        'prior_coverage_version': oldcov['coverage_version'],
        'research_id': 'CTD20261010', 'candidate_ids': ['CTD2-20261010', 'CTD3-20261010'],
        'result_version': 'CTD-RESULT-v1.0.0', 'created_utc': date,
        'decision': status, 'publication': pub, 'claim_delta': pubdir + '/CLAIM_COVERAGE_DELTA.json',
        'publication_counts': after_counts, 'formal_publication_counts_unchanged': False,
        'nondeductive': True, 'candidate_enabled': False, 'current_scientific_map': MAP,
        'candidate_counts_new': {'nodes': 5, 'rules': 2, 'contexts': 6, 'total': 13},
        'inherited_ctd2_counts': {'nodes': 20, 'rules': 7, 'contexts': 13, 'total': 40},
        'prior_current_decision': oldcov['current_decision'],
        'preserved_concurrent_records': concurrent_ids,
        'preserved_current_scientific_mainline': mainline_id,
        'new_human_data': False, 'c1_empirically_validated': False,
        'priority_status': 'No universal first-discovery claim; classical ingredients and predecessor results remain credited.',
    }
    put(update_path, update)
    cov = deepcopy(oldcov)
    cov['previous_entry_before_CTD_v10_publication'] = {
        'path': RECORD + '/history/before_publication_sync/PUBLICATION_COVERAGE.json',
        **metadata(workspace / 'PUBLICATION_COVERAGE.json')}
    cov['coverage_version'] = version
    cov['ledger'] = {'path': pubdir + '/COVERAGE_LEDGER.json',
                     'bytes': len(changes[pubdir + '/COVERAGE_LEDGER.json']),
                     'sha256': sha(changes[pubdir + '/COVERAGE_LEDGER.json'])}
    for key, name in [('published_works', 'PUBLISHED_WORKS_AND_VERSIONS.json'),
                      ('claim_id_index', 'CLAIM_ID_INDEX.json'), ('claim_delta', 'CLAIM_COVERAGE_DELTA.json'),
                      ('readable_report', 'COVERAGE_REPORT_ZH.md')]:
        cov[key] = pubdir + '/' + name
    cov['current_decision'] = cov['latest_update'] = update_path
    cov['publication_counts'] = after_counts
    cov['formal_publication_counts_unchanged'] = False
    cov['previous_latest_publication_before_CTD_v10'] = deepcopy(oldcov.get('latest_publication'))
    cov['latest_publication'] = pub
    cov['latest_manuscript_status'] = status
    cov['latest_working_manuscript_before_CTD_v10'] = deepcopy(oldcov.get('latest_working_manuscript'))
    cov['latest_working_manuscript'] = {
        'research_id': 'CTD20261010', 'result_version': 'CTD-RESULT-v1.0.0',
        'status': status, 'source': pub['manuscript'], 'pdf': pub['pdf'],
        'enabled_as_established_premises': False,
        'evidence': 'PUBLIC_DATA_SECONDARY_ANALYSIS_AND_CONDITIONAL_FINITE_SAMPLE_METHOD;NO_NEW_PAIRED_HUMAN_OR_PHENOMENAL_DATA'}
    cov['coverage_review'] = RECORD + '/publication_review/COVERAGE_REVIEW.md'
    cov['pending_research_updates'] = deepcopy(inherited_update_chain)
    append_unique(cov['pending_research_updates'], update_path)
    cov['published_candidate_decision'] = 'CTD3_PENDING_CHECKPOINT_DISABLED;ALL_ACTUAL_APPLICATION_AND_HISTORICAL_OPEN_RETAINED'
    put('PUBLICATION_COVERAGE.json', cov)

    candidate = {
        'id': 'CTD3-20261010', 'research_id': 'CTD20261010',
        'result_version': 'CTD-RESULT-v1.0.0', 'base_release': MAP,
        'path': RECORD + '/governance/CTD3_MAP_EXTENSION.json',
        'sha256': sha(archive['governance/CTD3_MAP_EXTENSION.json']),
        'status': 'PENDING_CHECKPOINT_DISABLED', 'enabled_as_established_premises': False,
        'candidate_counts': {'nodes': 5, 'active_conditional_rules': 2, 'nondeductive_context_links': 6},
        'publication_coverage_version': version,
        'compatibility_audit': RECORD + '/governance/CTD3_MAP_AUDIT.md',
        'handoff': RECORD + '/HANDOFF_ZH.md',
        'instruction': 'Finite-sample projection is conditional on the full paired-binomial and calibration contracts. Public disclosure does not enable a premise or establish an actual experiment.',
        'publication': pub, 'actual_application_status': 'OPEN',
    }
    scoped = {
        'audit': RECORD + '/governance/CTD3_MAP_AUDIT.md',
        'per_id_structure': RECORD + '/governance/CTD3_BASELINE_PER_ID_REVIEW.json.gz',
        'receipt': RECORD + '/governance/CTD3_MAP_REVIEW_RECEIPT.json',
        'status': 'SCOPED_DISABLED_CANDIDATE_REVIEW;FULL_HISTORICAL_DEPTH_OPEN',
        'core_layer_item_ids_structurally_visited': 1608, 'candidate_items_locally_reviewed': 13,
        'full_map_semantic_completion': False, 'inherited_unclosed_depth_ledger': ctd3['inherited_open_debt'],
        'qc_open': ctd3['inherited_open_obligations'] + ctd3['new_open_obligations'],
    }
    state = deepcopy(current)
    state['previous_navigation_before_CTD_v10_publication'] = {
        k: deepcopy(current.get(k)) for k in ['latest_research', 'latest_activity', 'latest_pending_research',
                                             'latest_publication', 'latest_scoped_review', 'next_priority',
                                             'latest_activity_persistence', 'latest_persistence_receipt']}
    result = {
        'id': 'CTD20261010', 'research_id': 'CTD20261010', 'result_version': 'CTD-RESULT-v1.0.0',
        'status': 'PUBLISHED_PREPRINT_CANDIDATES_DISABLED',
        'source': RECORD + '/RESEARCH_NOTE.md', 'handoff': RECORD + '/HANDOFF_ZH.md',
        'work_log': RECORD + '/WORK_LOG.md', 'publication_sync_log': RECORD + '/POST_PUBLICATION_SYNC.md',
        'enabled_as_established_premises': False, 'manuscript_status': status,
        'evidence_status': 'RETROSPECTIVE_PUBLIC_DATA_AND_CONDITIONAL_IDENTIFICATION_WITH_EXACT_SYNTHETIC_BINOMIAL_OPERATING_CHARACTERISTICS',
    }
    state['latest_published_research_result'] = result
    state['latest_publication_activity'] = {**result, 'activity': 'VERIFIED_PREPRINT_PUBLICATION_AND_NAVIGATION_SYNC', 'publication': pub}
    state['latest_published_candidate'] = deepcopy(candidate)
    state['latest_publication'] = pub
    state['latest_publication_scoped_review'] = scoped
    state['publication_coverage'] = {'version': version, 'entry': 'PUBLICATION_COVERAGE.json', 'latest_update': update_path, 'nondeductive': True}
    append_unique(state['pending_checkpoints_not_promoted'], 'CTD3-20261010')
    state['pending_note_before_CTD_v10_publication'] = state.get('pending_note')
    state['pending_note'] = f"All {len(state['pending_checkpoints_not_promoted'])} pending identities remain unpromoted. CTD3 adds 13 disabled records; every execution-time prior identity and the current {mainline_id} scientific mainline remain. DOI disclosure does not change the completed map or actual-premise truth."
    state['latest_publication_activity_persistence_status'] = 'PENDING_ACTUAL_GIT_AND_LIBRARY_SAVE_RECEIPTS;PUBLICATION_RECEIPT_IS_NOT_A_SAVE_RECEIPT'
    require(state.get('next_priority') == current.get('next_priority'), 'Scientific priority changed')
    put('CURRENT_STATE.json', state)
    registry = deepcopy(before['RESEARCH_REGISTRY.json'])
    if not any(current_id(x) == mainline_id for x in registry['pending_checkpoints']):
        registry['pending_checkpoints'].append(mainline_pending)
    registry['results'].append({
        'research_id': 'CTD20261010', 'result_version': '1.0.0', 'base_map_release': MAP, 'first_map_release': None,
        'title': receipt['title'], 'source': pub['manuscript'], 'pdf': pub['pdf'],
        'work_log': RECORD + '/WORK_LOG.md', 'handoff': RECORD + '/HANDOFF_ZH.md',
        'module': candidate['path'], 'claim_ledger': RECORD + '/CLAIM_LEDGER.json',
        'review': RECORD + '/governance/CTD3_MAP_AUDIT.md',
        'status': 'PUBLISHED_PREPRINT_CANDIDATES_DISABLED', 'publication': pub,
        'enabled_as_established_premises': False, 'actual_application_status': 'OPEN',
        'publication_coverage_version': version,
    })
    append_unique(registry['pending_checkpoints'], deepcopy(candidate), 'id')
    registry['publication_coverage'] = {'version': version, 'entry': 'PUBLICATION_COVERAGE.json', 'nondeductive': True}
    put('RESEARCH_REGISTRY.json', registry)
    modules = deepcopy(before['UCT_FORMAL_GRAPH_MODULES.json'])
    append_unique(modules['pending_checkpoints'], deepcopy(candidate), 'id')
    modules['publication_coverage'] = {'version': version, 'entry': 'PUBLICATION_COVERAGE.json', 'nondeductive': True}
    modules['previous_scoped_review_before_CTD_v10_publication'] = deepcopy(modules.get('latest_scoped_review'))
    modules['latest_scoped_review'] = scoped
    put('UCT_FORMAL_GRAPH_MODULES.json', modules)
    sessions = deepcopy(before['RESEARCH_SESSION_LOG_INDEX.json'])
    sessions['previous_navigation_before_CTD_v10_publication'] = deepcopy(sessions)
    sessions['latest_research'] = mainline_id
    sessions['latest_activity'] = current_id(current['latest_activity'])
    sessions['latest_pending_research'] = current_id(current['latest_pending_research'])
    sessions['latest_work_log'] = mainline['work_log']
    sessions['latest_handoff'] = mainline['handoff']
    sessions['latest_publication_activity'] = 'CTD20261010_PUBLICATION_V1_0_0'
    sessions['latest_publication_work_log'] = RECORD + '/POST_PUBLICATION_SYNC.md'
    sessions['latest_published_scientific_work_log'] = RECORD + '/WORK_LOG.md'
    sessions['latest_publication_handoff'] = RECORD + '/HANDOFF_ZH.md'
    sessions['latest_manuscript'] = pub['pdf']
    sessions['current_manuscript_decision'] = RECORD + '/MANUSCRIPT_DECISION.json'
    sessions['current_manuscript_decision_scope'] = 'Frozen scientific pre-release decision; actual publication state comes from latest_publication.receipt.'
    sessions['latest_publication'] = pub
    sessions['latest_publication_activity_persistence_status'] = 'PENDING_ACTUAL_SAVE_RECEIPTS'
    sessions['publication_coverage'] = {'version': version, 'entry': 'PUBLICATION_COVERAGE.json', 'nondeductive': True}
    for ident in current['pending_checkpoints_not_promoted']:
        if ident not in sessions['pending_checkpoints']:
            sessions['pending_checkpoints'].append(ident)
    append_unique(sessions['pending_checkpoints'], 'CTD3-20261010')
    put('RESEARCH_SESSION_LOG_INDEX.json', sessions)

    note = f'''<!-- CTD_V10_PUBLICATION:{doi} -->
# 最新发表：CTD v1.0.0；科学主线保留 {mainline_id}

[正式论文]({pub['pdf']}) · [DOI]({pub['doi_url']}) · [真实公开回读收据]({pub['receipt']}) · [中文交接]({RECORD}/HANDOFF_ZH.md) · [逐项发表覆盖]({pubdir}/CLAIM_COVERAGE_DELTA.json)。

本稿为公开数据二次分析与条件识别方法预印本：含响应概率等价反例、30人既有数据审计、配对读数识别边界及480个合成二项场景的有限样本计算。没有新增配对人体数据、已识别神经中介、体验测量或外部同行评议通过。CTD2的40项与CTD3的13项均停用；完成图913/424/261、10暂停、1608审查项、C1/U1与全部OPEN不变。发表覆盖{version}，研究作品{after_counts['distinct_research_works']}、研究版本标签对{after_counts['distinct_research_work_version_label_pairs']}、研究DOI记录{after_counts['distinct_published_research_doi_records']}，含独立编辑补充共{after_counts['all_verified_publication_doi_records_including_editorial']}个DOI记录。

执行时当前科学接续 {mainline_id} 及全部并发/旧记录完整保留；既定下一科学问题仍以 CURRENT_STATE.json 的 next_priority 为准。此次只新增发表导航，不把CTD设为替代当前科学主线。DOI公开、OTS、Arweave、Git及文件保存分别按真实收据记录，不互相代替。以下科学接续标签及历史记录均原样保留。

---

'''
    for rel in NAV_MD:
        put(rel, note.encode() + (workspace / rel).read_bytes())
    guide_path = workspace / 'RESEARCH_MASTER_GUIDE.md'
    guide = guide_path.read_text(encoding='utf-8')
    policy = re.search(r'^\*\*政策 ID：[^\n]+\n', guide, flags=re.M)
    require(policy is not None, 'Guide policy heading changed; review insertion manually')
    guide_note = f'\n**CTD v1.0.0 发表导航：** [DOI]({pub["doi_url"]})、[真实公开回读收据]({pub["receipt"]})与[交接]({RECORD}/HANDOFF_ZH.md)。覆盖{version}；这是方法与既有数据二次分析预印本。CTD2/CTD3候选均停用，完成图、C1/U1、全部OPEN及当前{mainline_id}科学主线和下一问题不变。本条只同步发表导航，不修改最高研究政策。\n'
    put('RESEARCH_MASTER_GUIDE.md', (guide[:policy.end()] + guide_note + guide[policy.end():]).encode())
    report = f'''# CTD v1.0.0 发表覆盖增量 — {version}

真实版本 DOI：[{doi}]({pub['doi_url']})。匿名公开文件回读已通过；工作流原始状态见[原始收据](../../{pub['receipt']})，最新解析证据见[解析来源](../../{pub['doi_resolution_source']})。独立解析收据不改写原工作流快照。预留记录没有计入此次更新。

执行时基础覆盖版本：{oldcov['coverage_version']}；基础研究HEAD：`{args.expected_head}`。新完整总台账沿用旧完整清单，追加一个CTD工作/版本/DOI，而非重新宣称全面账户普查。

计数：研究作品{after_counts['distinct_research_works']}，研究作品/版本标签对{after_counts['distinct_research_work_version_label_pairs']}，研究DOI{after_counts['distinct_published_research_doi_records']}；另有编辑补充作品和DOI各1个，全部DOI共{after_counts['all_verified_publication_doi_records_including_editorial']}。

25个科学节点分别记录正文论证与正式ZIP细节；9条规则及19条上下文仅按ZIP中的停用候选记录披露。N016完整copula反例、N017完整UCT治理限定、不等方差与连续校准union细节不冒称已在正文完全展开。引用其他研究ID不自动重发表那些研究。

完成图{MAP}及全部OPEN不变；CTD2的40项和CTD3的13项仍停用。数学/代码审查、合成运行、正式披露、实际神经实现和体验解释是不同证据层。没有新增人体实验、UCT实际验证或外部同行评议通过。
'''
    put(pubdir + '/COVERAGE_REPORT_ZH.md', report.encode())
    local_note = note.replace(RECORD + '/', '').replace(pubdir + '/', '../../' + pubdir + '/')
    put(RECORD + '/HANDOFF_ZH.md', local_note.encode())
    sync_log = f'''# Post-publication synchronization record

Prepared at {date} from research HEAD `{args.expected_head}`.

The actual publication receipt is [publication-record.json](publication-record.json); DOI [{doi}]({pub['doi_url']}). The exact public files are preserved under `release/`. The 201 scientific-archive files remain byte-identical to the formal ZIP; its historical pre-reservation template remains under `manuscript/`. The separate DOI-bound file is the public citing edition.

Coverage advances from {oldcov['coverage_version']} to {version}. All earlier complete-ledger work/version objects, earlier pending candidates, every concurrent record, the current {mainline_id} scientific mainline, completed-map artifacts and OPEN obligations are retained. CTD3 is registered as 5/2/6 disabled candidate records. Formal publication does not enable a scientific premise or replace the current research priority.

This file records preparation of the repository update from actual publication evidence. It does not claim that the planned commit, remote Git readback, Library save, OTS or Arweave operation has occurred. Root must attach actual persistence receipts separately. Frozen WORK_LOG.md, MANUSCRIPT_DECISION.json and FILE_MANIFEST.json describe the scientific pre-release record and are unchanged.
'''
    put(RECORD + '/POST_PUBLICATION_SYNC.md', sync_log.encode())

    for rel in NAV_JSON + NAV_MD + ['RESEARCH_MASTER_GUIDE.md']:
        put(RECORD + '/history/before_publication_sync/' + rel, (workspace / rel).read_bytes())
    # Exact preservation checks, not a new scientific test.
    require(registry['results'][:-1] == before['RESEARCH_REGISTRY.json']['results'], 'Result prefix changed')
    for obj, old, field in [(registry, before['RESEARCH_REGISTRY.json'], 'pending_checkpoints'),
                             (modules, before['UCT_FORMAL_GRAPH_MODULES.json'], 'pending_checkpoints'),
                             (sessions, before['RESEARCH_SESSION_LOG_INDEX.json'], 'pending_checkpoints'),
                             (state, current, 'pending_checkpoints_not_promoted')]:
        require(obj[field][:len(old[field])] == old[field], 'Pending prefix changed: ' + field)
    for k in ['release_id', 'complete_map_sha256', 'review_ledger_sha256', 'counts', 'qc_open', 'next_priority',
              'latest_research', 'latest_activity', 'latest_pending_research', 'latest_scoped_review']:
        require(state[k] == current[k], 'Protected current state changed: ' + k)
    for k, value in before['UCT_FORMAL_GRAPH_MODULES.json'].items():
        if k not in ['pending_checkpoints', 'publication_coverage', 'latest_scoped_review']:
            require(modules[k] == value, 'Protected effective module field changed: ' + k)
    require(cov['pending_research_updates'][:len(oldcov['pending_research_updates'])] == oldcov['pending_research_updates'], 'Coverage history prefix changed')
    for rel in NAV_MD:
        require(changes[rel].endswith((workspace / rel).read_bytes()), 'Historical Markdown text changed')
    require(git(repo, 'rev-parse', 'HEAD') == args.expected_head and not git(repo, 'status', '--porcelain'),
            'Repository changed during preparation; reprepare')

    # Every output is outside the source repository. Apply is a separate command.
    output.mkdir(parents=True)
    overlay = output / 'overlay'
    manifest_files = []
    for rel, b in sorted(changes.items()):
        dst = overlay / WS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(b)
        old = workspace / rel
        manifest_files.append({'path': str(WS / rel), 'before': metadata(old) if old.exists() else None,
                               'after': {'bytes': len(b), 'sha256': sha(b)}})
    manifest = {
        'schema': 'ctd-research-sync-overlay/1', 'prepared_utc': date, 'expected_research_head': args.expected_head,
        'source_repository_at_preparation': str(repo), 'workspace': str(WS), 'record': RECORD,
        'coverage_version': version, 'parent_coverage_version': oldcov['coverage_version'],
        'publication_doi': doi, 'publication_receipt_input': str(args.publication_receipt.resolve()),
        'publication_receipt_sha256': sha(args.publication_receipt.read_bytes()),
        'public_archive_root': ziproot, 'public_archive_members': len(archive),
        'scientific_archive_unchanged': True, 'claim_node_count': 25, 'formal_metadata_count': 28,
        'reviewed_to_public_manuscript_changes': {'doi_substitutions': 1, 'figure_path_substitutions': 4,
                                                'scientific_text_changes': 0},
        'before_counts': before_counts, 'after_counts': after_counts,
        'files': manifest_files, 'repository_writes_performed': False,
        'git_or_external_mutations_performed': False, 'scientific_testing_performed': False,
        'completed_map_unchanged': MAP, 'all_old_pending_entries_preserved': True,
        'current_scientific_mainline_preserved': mainline_id,
        'application_open_unchanged': True,
    }
    (output / 'OVERLAY_MANIFEST.json').write_bytes(jd(manifest))
    print(json.dumps({'output': str(output), 'coverage_version': version, 'files': len(manifest_files),
                      'doi': doi, 'counts': after_counts, 'source_repository_written': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
