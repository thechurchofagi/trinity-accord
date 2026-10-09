#!/usr/bin/env python3
"""Assemble a non-deductive publication overlay from frozen audit inputs.

This copies the reviewers' findings and exposes exact provenance. It does not
infer originality from dates, count graph objects as discoveries, or change the
scientific graph. Run from this directory's parent after the audits are frozen.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import tarfile
import io

BASE = Path(__file__).resolve().parent.parent
AUDIT = BASE / 'publication_audit_work'
ROOT = BASE / 'uct/research/uct-agent-consciousness-workspace'
VERSION = 'UCT-PUB-v1.0.0'
REL = Path('publication') / VERSION
OUT = ROOT / REL
RECORD = ROOT / 'records/PUB20261009_Publication_Coverage'
RESEARCH_HEAD = '310e744f8d0195d05fac4e56e807adc48784f0ca'
MAIN_HEAD = 'fc568e8718e82b3cda6ede0e628aa3342179bebc'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def writej(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def anchor(path):
    path = Path(path)
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
            'sha256': sha(path)}

def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

def main():
    pubs = json.loads((AUDIT/'novelty_inventory.json').read_text())
    inv = json.loads((AUDIT/'map_result_inventory.json').read_text())
    early = json.loads((AUDIT/'early_result_family_inventory.json').read_text())
    assert pubs['counts']['distinct_research_works'] == 28
    assert len(inv['map_items']) == 1608
    assert len({x['item_id'] for x in inv['map_items']}) == 1608
    OUT.mkdir(parents=True, exist_ok=True)

    copy(AUDIT/'novelty_inventory.json', OUT/'PUBLISHED_WORKS_AND_VERSIONS.json')
    copy(AUDIT/'publication_semantic_coverage.json', OUT/'PAPER_ARGUMENT_COVERAGE.json')
    copy(AUDIT/'early_result_family_inventory.json', OUT/'EARLY_RESULT_FAMILIES.json')
    writej(OUT/'RESULT_FAMILIES.json', {'coverage_version': VERSION,
             'family_count_is_not_discovery_count': True, 'families': inv['families'],
             'late_scoped_residual_assessments': pubs['scoped_family_residuals'],
             'outside_current_map_modules': inv['outside_current_map_modules'],
             'early_inventory': 'EARLY_RESULT_FAMILIES.json',
             'other_branch_candidates': pubs['pending_or_source_only_candidates']})
    writej(OUT/'RESEARCH_ARTIFACT_INVENTORY.json', {'coverage_version': VERSION,
             'scope': 'All files in pinned research workspace; inventory is not full-content review.',
             'tree_counts': inv['counts'], 'records': inv['record_inventory'],
             'logs_and_registry_chain': inv['log_and_registry_inventory'],
             'early_library_metadata': json.loads((AUDIT/'early_library_folder_inventory.json').read_text())})

    inherited = {}
    for family in pubs['scoped_family_residuals']:
        for item_id in family.get('inherited_application_ids', []) + family.get('covered_or_specialization_ids', []):
            inherited[item_id] = family
    normalized = {'exact':'covered_exact', 'partial':'covered_partial',
                  'inherited':'inherited', 'not_claim':'not_applicable',
                  'unknown':'unverified', 'not_found_in_verified_corpus':'not_found_in_verified_corpus'}
    items = []
    overrides = []
    for original in inv['map_items']:
        item = json.loads(json.dumps(original))
        item['source_inventory_coverage_status'] = item['coverage_status']
        item['coverage_status'] = normalized[item['coverage_status']]
        item['coverage_version'] = VERSION
        item['publication_is_scientific_validation'] = False
        if item['item_id'] in inherited:
            f = inherited[item['item_id']]
            item['coverage_status'] = 'inherited'
            item['body_semantic_coverage'] = {
                'status':'inherited_application_or_direct_specialization',
                'paper_coverage_ids':f['published_sources'],
                'explanation':f['inherited_or_covered'],
                'limit':'The scoped implication is inherited; no claim that the later full module was deposited.'}
            item['residual_originality'] = 'NOT_A_SEPARATE_NEW_GENERAL_THEOREM'
            overrides.append({'item_id':item['item_id'],
                              'from':original['coverage_status'], 'to':'inherited',
                              'source':'PAPER_ARGUMENT_COVERAGE.json',
                              'paper_coverage_ids':f['published_sources']})
        else:
            item['residual_originality'] = 'NOT_ESTABLISHED_BY_DISCLOSURE_STATUS'
        items.append(item)
    items.sort(key=lambda x:x['item_id'])
    shards, index = [], {}
    for start in range(0, len(items), 100):
        chunk = items[start:start+100]
        path = OUT/'items'/f'part_{start//100+1:02d}.json'
        writej(path, {'coverage_version':VERSION, 'items':chunk})
        a = anchor(path); a.update({'items':len(chunk), 'first_id':chunk[0]['item_id'], 'last_id':chunk[-1]['item_id']})
        shards.append(a)
        for item in chunk:
            index[item['item_id']] = {'path':str(path.relative_to(OUT)),
                                    'coverage_status':item['coverage_status'],
                                    'role':item['role']}
    writej(OUT/'CLAIM_ID_INDEX.json', {'coverage_version':VERSION,
                                    'scope':'All current map review items, including nonclaims.',
                                    'index':index})
    writej(OUT/'COVERAGE_RECONCILIATION.json', {'coverage_version':VERSION,
          'source_inventory_sha256':sha(AUDIT/'map_result_inventory.json'),
          'publication_review_sha256':sha(AUDIT/'novelty_inventory.json'),
          'explicit_semantic_overrides':overrides,
          'remaining_unverified_ids':[x['item_id'] for x in items if x['coverage_status']=='unverified'],
          'remaining_unverified_limit':'Late-family scope and exact candidate objects are assessed in PAPER_ARGUMENT_COVERAGE. A family-level not-found statement is not inflated into universal item-level absence or worldwide novelty.',
          'science_changed':False})

    reports = ['PUBLISHED_COVERAGE_REVIEW.md', 'MAP_RESULT_INVENTORY.md',
               'RESIDUAL_RESEARCH_ASSESSMENT.md']
    for name in reports:
        copy(AUDIT/name, RECORD/name)
    copy(AUDIT/'MAP_RESULT_INVENTORY_VALIDATION.json', RECORD/'MAP_RESULT_INVENTORY_VALIDATION.json')
    copy(Path(__file__), RECORD/'assemble_publication_coverage.py')

    # Only explicit research sources and sanitized discovery evidence are packed.
    # Transfer requests and signed materialization responses are intentionally not inputs.
    sources = [p for p in (AUDIT/'sources').rglob('*') if p.is_file()]
    evidence = ['all_head_refs.json','research_head_refs.json','main_tree_fc568e8.json',
       'research_branch_directory_inventory.json','research_directory_trees.json',
       'all_research_receipt_candidates.json','nonresearch_named_heads_screen.json',
       'github_release_discovery.json','research_workspace_tree_310e744.json',
       'fulltext_download_provenance.json','branch_download_provenance.json',
       'attachment_member_manifest.json','early_library_folder_inventory.json',
       'novelty_inventory.json','publication_semantic_coverage.json',
       'map_result_inventory.json','early_result_family_inventory.json',
       'MAP_RESULT_INVENTORY_VALIDATION.json','build_map_inventory.py',
       'PUBLISHED_COVERAGE_REVIEW.md','MAP_RESULT_INVENTORY.md',
       'RESIDUAL_RESEARCH_ASSESSMENT.md']
    sources += [AUDIT/name for name in evidence]
    assert all(p.is_file() for p in sources)
    members = []
    capsule = OUT/'SOURCE_CAPSULE.tar.xz'
    with tarfile.open(capsule, 'w:xz', preset=6) as tar:
        for p in sorted(set(sources)):
            rel = str(p.relative_to(BASE))
            content = p.read_bytes()
            info = tarfile.TarInfo(rel); info.size=len(content)
            info.mode=0o644; info.mtime=0
            tar.addfile(info, io.BytesIO(content))
            members.append({'member':rel, 'bytes':len(content), 'sha256':hashlib.sha256(content).hexdigest()})
    writej(OUT/'SOURCE_CAPSULE_MANIFEST.json', {'coverage_version':VERSION,
            'capsule':anchor(capsule), 'members':members,
            'scope':'Exact retrieved research sources and audit discovery evidence. Original historical experiments not reread here remain pinned repository/Library references; their absent raw archives are not silently claimed included.',
            'historical_local_paths':'Original reviewer records retain capture paths. On extraction, resolve the publication_audit_work/ suffix inside the chosen destination.'})

    decision = {
       'id':'PUB20261009-DECISION-1',
       'purpose':'Original, inspectable, reusable knowledge serving the UCT program and future AI citation; not paper count or venue status.',
       'r188':'HOLD_STANDALONE_PRESERVE_TECHNICAL_SUPPLEMENT_CANDIDATE',
       'supersedes_readiness_only':'Frozen CER-RESULT-v0.1.0 section 9.3 broad-manuscript readiness judgment. All original mathematical text and evidence remain unchanged.',
       'remaining_increment':'Source-access restricted weighted finite-error recovery and matched benchmark; later intervention/compensation/occurrence/calibration applications and empirical negative-mapping records need exact predecessor-aware assessment.',
       'combined_paper':'NOT_YET_JUSTIFIED_BY_SIMPLY_GROUPING_SEPARATE_MODELS',
       'new_probe':'ONLINE-AC-PROBE-20261009; separate pending research checkpoint and post-probe assessment.',
       'assessment_paths':['records/PUB20261009_Publication_Coverage/RESIDUAL_RESEARCH_ASSESSMENT.md',
                           'records/PUB20261009_Publication_Coverage/PENDING_RESULTS_ASSESSMENT.md',
                           'records/ONLINE_AC_20261009_Dynamic_Calibration/RESEARCH_CHECKPOINT.md'],
       'actual_application_and_named_experience':'OPEN',
       'worldwide_priority':'UNVERIFIED',
       'publication_action':'NO_NEW_DOI_OTS_ARWEAVE_ACTION'}
    writej(OUT/'MANUSCRIPT_DECISION.json', {'coverage_version':VERSION, **decision})

    documents = ['PUBLISHED_WORKS_AND_VERSIONS.json','PAPER_ARGUMENT_COVERAGE.json',
       'RESULT_FAMILIES.json','RESEARCH_ARTIFACT_INVENTORY.json','EARLY_RESULT_FAMILIES.json',
       'CLAIM_ID_INDEX.json','COVERAGE_RECONCILIATION.json','SOURCE_CAPSULE_MANIFEST.json',
       'MANUSCRIPT_DECISION.json']
    ledger = {'schema':'uct-publication-coverage-ledger/1.0',
       'coverage_version':VERSION, 'sequence':1, 'parent_coverage':None,
       'date':'2026-10-09', 'layer':'NONDEDUCTIVE_PUBLICATION_AND_REUSE_METADATA',
       'record_id':'PUB20261009', 'scientific_map':'UCT-MAP-v1.1.2',
       'scientific_map_sha256':inv['pins']['effective_graph']['sha256'],
       'research_base_commit':RESEARCH_HEAD, 'publication_main_commit':MAIN_HEAD,
       'purpose':decision['purpose'], 'publication_counts':pubs['counts'],
       'counting_decisions':pubs['counting_decisions'],
       'map_counts':inv['counts'],
       'current_item_coverage_counts':dict(Counter(x['coverage_status'] for x in items)),
       'explicit_inherited_reconciliations':len(overrides),
       'disclosure_findings':inv['official_attachment_findings'],
       'documents':{name:anchor(OUT/name) for name in documents},
       'item_shards':shards,
       'read_scope':pubs['core_read_scope'],
       'completeness_limits':inv['completeness_limits']+pubs['open_limits'],
       'publication_states':['published_formal_body','published_formal_attachment','cited_source_only','working_checkpoint','reserved_only','unknown'],
       'coverage_states':list(normalized.values()),
       'orthogonal_axes':['formal publication/disclosure','body argument coverage','proof/evidence validity','originality','actual/named-experience application'],
       'claim_count_is_paper_count':False, 'unknown_means_unpublished':False,
       'unpublished_means_original':False, 'publication_means_validated':False,
       'manuscript_decision':decision,
       'update_template':'records/PUB20261009_Publication_Coverage/COVERAGE_UPDATE_TEMPLATE.json',
       'required_update':'Every new work log and map-entry update must point to the same coverage version and provide changed claims/publications or a checked no-change reason. Do not back-edit frozen historical log assertions.',
       'science_promotion':'Any new substantive result remains pending until applicable complete-map semantic integration. Coverage reconciliation itself does not amend science.'}
    writej(OUT/'COVERAGE_LEDGER.json', ledger)
    entry = {'schema':'uct-publication-coverage-entry/1.0',
       'coverage_version':VERSION, 'ledger':anchor(OUT/'COVERAGE_LEDGER.json'),
       'claim_id_index':str(REL/'CLAIM_ID_INDEX.json'),
       'published_works':str(REL/'PUBLISHED_WORKS_AND_VERSIONS.json'),
       'readable_report':'records/PUB20261009_Publication_Coverage/PUBLICATION_COVERAGE_REPORT_ZH.md',
       'current_decision':str(REL/'MANUSCRIPT_DECISION.json'),
       'latest_update':'records/PUB20261009_Publication_Coverage/COVERAGE_UPDATE.json',
       'current_scientific_map':'UCT-MAP-v1.1.2',
       'nondeductive':True, 'unknown_is_unpublished':False,
       'source_capsule':anchor(capsule),
       'source_manifest':str(REL/'SOURCE_CAPSULE_MANIFEST.json')}
    writej(ROOT/'PUBLICATION_COVERAGE.json', entry)
    print(json.dumps({'version':VERSION,'documents':len(documents), 'shards':len(shards),
             'items':len(items),'inherited_overrides':len(overrides),
             'coverage_counts':ledger['current_item_coverage_counts'],
             'source_members':len(members),'capsule_bytes':capsule.stat().st_size,
             'capsule_sha256':sha(capsule)},ensure_ascii=False))

if __name__ == '__main__':
    main()
