#!/usr/bin/env python3
"""Read-only component checks before a real publication receipt is available.

This does not synthesize a publication receipt or run either overlay application.
"""
from pathlib import Path
import ast
import importlib.util
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
spec = importlib.util.spec_from_file_location('ctd_sync_prepare', HERE / 'prepare_sync.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
repo = BASE / 'uct_repo'
workspace = repo / prep.WS
release = BASE / 'ctd_release_repo/research/noise-identifiability-bodily-judgments'
public = release / 'published'
checks = []


def check(name, condition, detail=None):
    if not condition:
        raise AssertionError(name)
    checks.append({'check': name, 'pass': True, 'detail': detail})


for name in ['prepare_sync.py', 'apply_overlay.py']:
    ast.parse((HERE / name).read_text())
    check(name + ' parses', True)
cov = prep.load(workspace / 'PUBLICATION_COVERAGE.json')
works = prep.load(workspace / cov['published_works'])
ledger = prep.load(workspace / cov['ledger']['path'])
counts = prep.publication_counts(works['works'])
check('Full inventory count derivation matches both latest entry and complete ledger',
      counts == works['counts'] == cov['publication_counts'] == ledger['publication_counts'], counts)
check('30 existing work objects and exact editorial distinction',
      len(works['works']) == 30 and counts['distinct_research_works'] == 29 and
      counts['separate_editorial_supplement_works'] == 1)
check('UCT I duplicate version labels retain separate DOI records',
      next(w for w in works['works'] if w['work_id'] == 'TA-TR-2026-20')['published_doi_record_count'] == 4 and
      next(w for w in works['works'] if w['work_id'] == 'TA-TR-2026-20')['distinct_version_label_count'] == 3)
next_version = prep.choose_coverage(workspace, cov['coverage_version'], repo)
check('Dynamic next coverage candidate at current HEAD',
      int(next_version.rsplit('.', 1)[-1]) > int(cov['coverage_version'].rsplit('.', 1)[-1]),
      {'current': cov['coverage_version'], 'candidate': next_version, 'candidate_is_not_reserved': True})
archive_bytes = (public / prep.ZIP_NAME).read_bytes()
archive, root = prep.extract_scientific_archive(archive_bytes)
check('Exact 201-file scientific ZIP CRC, manifest membership and all member hashes', len(archive) == 201,
      {'bytes': len(archive_bytes), 'sha256': prep.sha(archive_bytes), 'root': root})
template = archive['manuscript/' + prep.MD_NAME]
doi = prep.load(release / 'deposit.json')['doi']
normalized = template.replace(b'__DOI_RESERVED_AT_RELEASE__', doi.encode())
links = re.findall(rb'\]\(\.\./(figures/[^)]+\.pdf)\)', template)
for rel in links:
    normalized = normalized.replace(b'](../' + rel + b')', b'](' + rel + b')')
check('Public prepared Markdown changes only DOI and four figure paths',
      len(links) == len(set(links)) == 4 and normalized == (public / prep.MD_NAME).read_bytes(),
      {'reviewed_template_sha256': prep.sha(template), 'prepared_public_md_sha256': prep.sha(normalized),
       'scientific_text_changes': 0, 'publication_status_not_inferred': True})
review = prep.load(HERE / 'COVERAGE_REVIEW.json')
rows = prep.rows_from_review(review)
source = json.loads(archive['CLAIM_LEDGER.json'])
source_by_id = {x['id']: x for x in source['claims']}
check('Independent body/archive review covers exact 25 node IDs',
      len(rows) == 25 and {x['id'] for x in rows} == set(source_by_id))
check('All reviewed statements and claim evidence are exact official-ZIP content',
      all(x['original_statement'] == source_by_id[x['id']]['statement'] and
          x['statement_sha256'] == prep.sha(x['original_statement'].encode()) and
          all(p in archive for p in source_by_id[x['id']]['evidence_paths']) for x in rows))
ctd2 = json.loads(archive['governance/MAP_EXTENSION.json'])
ctd3 = json.loads(archive['governance/CTD3_MAP_EXTENSION.json'])
items = [x for m in [ctd2, ctd3] for k in ['nodes', 'rules', 'context_links'] for x in m[k]]
check('Exact 53 CTD-owned node/rule/context records remain disabled',
      len(items) == len({x['id'] for x in items}) == 53 and
      all(x['id'].startswith(('CTD2-', 'CTD3-')) and x.get('enabled') is False for x in items))
check('CTD3 new candidate is exactly 5 nodes, 2 rules, 6 contexts',
      [len(ctd3[k]) for k in ['nodes', 'rules', 'context_links']] == [5, 2, 6])
try:
    prep.verified_publication(release / 'deposit.json', public)
except ValueError as exc:
    check('Real reservation receipt is rejected before any publication counting or output',
          'Reserved or unsubmitted record' in str(exc), str(exc))
else:
    raise AssertionError('Reservation accepted as publication')
protected = {}
for name in ['A3M20261010_Bodily_Familiarity_Invariance', 'A3N20261010_Route_Fluency_Crossing',
             'A3O20261010_Route_Grain_Selection_Crossing', 'CTD20261010_Cross_Task_Intervention_v02']:
    rel = str(prep.WS / 'records' / name)
    data = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '-z', 'HEAD', '--', rel])
    rows = [x.decode() for x in data.split(b'\0') if x]
    check('Protected record has nonempty HEAD Git identity: ' + name, len(rows) > 0)
    protected[name] = {'git_blob_entries': len(rows), 'nul_separated_git_ls_tree_sha256': prep.sha(data),
                       'git_identity_scope': 'Pinned HEAD mode/type/blob/path inventory; sparse-unchecked-out bytes were not newly read or semantically audited.',
                       'locally_checked_out_files': sum(p.is_file() for p in (workspace / 'records' / name).rglob('*'))}
report = {
    'schema': 'ctd-publication-sync-component-checks/1',
    'research_head': prep.git(repo, 'rev-parse', 'HEAD'),
    'checks': checks, 'protected_read_only_record_trees': protected,
    'scope': 'Pure parsing, exact artifact comparisons, inventory arithmetic and rejection of a reserved receipt.',
    'full_overlay_run': False, 'actual_publication_verified_here': False,
    'repository_writes': False, 'external_writes': False, 'scientific_tests_or_refits': False,
    'remaining_gate': 'Only a real submitted/public-anonymous-readback receipt permits the complete overlay preparation.',
}
(HERE / 'PREPARATION_COMPONENT_CHECKS.json').write_bytes(prep.jd(report))
print(json.dumps({'checks_passed': len(checks), 'research_head': report['research_head'],
                  'full_overlay_run': False, 'repository_writes': False}))
