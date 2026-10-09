#!/usr/bin/env python3
"""Finalize the first coverage release's actual post-probe decision and hashes."""
from pathlib import Path
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE / 'uct/research/uct-agent-consciousness-workspace'
AUDIT = BASE / 'publication_audit_work'
REC = ROOT / 'records/PUB20261009_Publication_Coverage'
PROBE = ROOT / 'records/ONLINE_AC_20261009_Dynamic_Calibration'
OUT = ROOT / 'publication/UCT-PUB-v1.0.0'
VERSION = 'UCT-PUB-v1.0.0'

def read(path): return json.loads(path.read_text())
def write(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
def anchor(path):
    return {'path':str(path.relative_to(ROOT)), 'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    claim_ledger = read(PROBE / 'CLAIM_REUSE_LEDGER.json')
    dynamic = {'coverage_version':VERSION, 'record_id':'ONLINE-AC-PROBE-20261009',
      'result_version':'ONLINE-AC-RESULT-v0.2.0', 'paper_version':'ONLINE-AC-PAPER-v0.1.0',
      'formal_publication':'NOT_FORMALLY_PUBLISHED_IN_VERIFIED_CORPUS',
      'working_disclosure':'Research workspace and complete working manuscript; actual save receipt tracked separately',
      'publication_count_effect':0, 'scope':'Outside current1608-item scientific map; PENDING_MAP',
      'claims':claim_ledger['claims'], 'claim_ledger':anchor(PROBE/'CLAIM_REUSE_LEDGER.json'),
      'manuscript':anchor(PROBE/'PAPER.md'), 'checkpoint':anchor(PROBE/'RESEARCH_CHECKPOINT.md'),
      'new_result_assessment':anchor(REC/'POST_PROBE_REASSESSMENT.md'),
      'do_not_count_as_separate_new_principles':['General dynamic sufficiency/transition closure','Binary-signature identification','Belief-state control or induction'],
      'global_priority':'UNVERIFIED', 'new_full_map_semantic_integration':'NOT_COMPLETED',
      'current_completed_science':'UCT-MAP-v1.1.2'}
    write(OUT/'DYNAMIC_RESULT_COVERAGE.json', dynamic)

    d=read(OUT/'MANUSCRIPT_DECISION.json')
    d['id']='PUB20261009-DECISION-3'
    d['decision_sequence']=[
        {'id':1,'object':'R188 broad standalone manuscript','decision':'HOLD_TECHNICAL_SUPPLEMENT_CANDIDATE'},
        {'id':2,'object':'ONLINE-AC-RESULT-v0.1.0','decision':'PRESERVE_USEFUL_FINITE_RESULT_CONTINUE_AT_N5'},
        {'id':3,'object':'ONLINE-AC-RESULT-v0.2.0','decision':'COMPLETE_FOCUSED_TECHNICAL_WORKING_PAPER'}]
    d['new_probe']='ONLINE-AC-RESULT-v0.2.0: exact n5 two-probe sustained control with closed partial beliefs; matched full-identification budget3; one-probe obstruction and n3 value7/8.'
    d['new_paper']={'version':'ONLINE-AC-PAPER-v0.1.0',
       'title':'Correct Control without Complete Recalibration: Exact bounds and a two-probe five-port controller under transposition drift',
       'decision':'COMPLETE_SCOPED_WORKING_MANUSCRIPT',
       'path':str((PROBE/'PAPER.md').relative_to(ROOT)),
       'pdf':str((PROBE/'Correct_Control_Without_Complete_Recalibration_v0.1.0.pdf').relative_to(ROOT)),
       'publication_status':'NOT_FORMALLY_PUBLISHED','new_publication_count':0,
       'local_scientific_review':'PASS_PROOF_PROTOCOL_WITNESS_AND_FINAL_MANUSCRIPT',
       'map_status':'PENDING_MAP','formal_release_next_requirement':'Complete applicable whole-map semantic integration and affected downstream rederivations; preserve prior attribution and obtain actual publication evidence when an authorized release occurs.',
       'global_priority':'UNVERIFIED'}
    d['assessment_paths'] += [str((REC/'POST_PROBE_REASSESSMENT.md').relative_to(ROOT)),
                              str((OUT/'DYNAMIC_RESULT_COVERAGE.json').relative_to(ROOT))]
    d['assessment_paths']=list(dict.fromkeys(d['assessment_paths']))
    write(OUT/'MANUSCRIPT_DECISION.json',d)

    families=read(OUT/'RESULT_FAMILIES.json')
    families['new_pending_research']={'id':'ONLINE-AC-PROBE-20261009','result_version':'0.2.0',
       'coverage':'DYNAMIC_RESULT_COVERAGE.json','formal_publication':'NOT_FORMALLY_PUBLISHED',
       'scientific_map':'PENDING_MAP','paper_decision':'COMPLETE_SCOPED_WORKING_MANUSCRIPT'}
    write(OUT/'RESULT_FAMILIES.json',families)

    ledger=read(OUT/'COVERAGE_LEDGER.json')
    ledger['manuscript_decision']={k:v for k,v in d.items() if k!='coverage_version'}
    ledger['new_pending_research']='publication/UCT-PUB-v1.0.0/DYNAMIC_RESULT_COVERAGE.json'
    ledger['documents']['DYNAMIC_RESULT_COVERAGE.json']=anchor(OUT/'DYNAMIC_RESULT_COVERAGE.json')
    for name in ledger['documents']:
        ledger['documents'][name]=anchor(OUT/name)
    write(OUT/'COVERAGE_LEDGER.json',ledger)
    entry=read(ROOT/'PUBLICATION_COVERAGE.json')
    entry['ledger']=anchor(OUT/'COVERAGE_LEDGER.json')
    entry['new_pending_research']='publication/UCT-PUB-v1.0.0/DYNAMIC_RESULT_COVERAGE.json'
    write(ROOT/'PUBLICATION_COVERAGE.json',entry)

    index=read(OUT/'CLAIM_ID_INDEX.json')['index']
    reconciliation=read(OUT/'COVERAGE_RECONCILIATION.json')
    partial=[]
    for part in sorted((OUT/'items').glob('*.json')):
        partial.extend(c for c in read(part)['items'] if c['coverage_status']=='covered_partial')
    publications=read(OUT/'PUBLISHED_WORKS_AND_VERSIONS.json')
    update={'record_id':'PUB20261009','date_utc':'2026-10-09',
       'base_research_commit':'310e744f8d0195d05fac4e56e807adc48784f0ca',
       'base_completed_map_version':'UCT-MAP-v1.1.2',
       'publication_coverage_entry':'PUBLICATION_COVERAGE.json','previous_coverage_version':None,
       'new_coverage_version':VERSION,'kind':'FIRST_VERSIONED_COVERAGE_CENSUS_AND_POST_PROBE_REASSESSMENT',
       'checked_publication_sources':'publication/UCT-PUB-v1.0.0/PUBLISHED_WORKS_AND_VERSIONS.json',
       'checked_publication_counts':publications['counts'],
       'changed_claim_ids':[c['claim_id'] for c in claim_ledger['claims']],
       'changed_coverage_metadata_ids':[x['item_id'] for x in reconciliation['explicit_semantic_overrides']],
       'newly_recognized_already_published_exact_claim_ids':[k for k,v in index.items() if v['coverage_status']=='covered_exact'],
       'newly_published_claim_ids':[],
       'partially_covered_claims':partial,
       'uncovered_candidates_within_verified_corpus':{
         'family_scope':'publication/UCT-PUB-v1.0.0/RESULT_FAMILIES.json',
         'late_scope':'publication/UCT-PUB-v1.0.0/PAPER_ARGUMENT_COVERAGE.json',
         'new_dynamic_scope':'publication/UCT-PUB-v1.0.0/DYNAMIC_RESULT_COVERAGE.json'},
       'unverified_scope':ledger['completeness_limits'],
       'remaining_unverified_current_map_ids':reconciliation['remaining_unverified_ids'],
       'unchanged_reason':None,
       'residual_assessment':{
          'precise_problem':'Can a controller sustain one fixed physical action under recurring unknown transpositions without complete current-wiring identification?',
          'net_increment_after_subtraction':'Exact n5 closed partial-belief construction and optimal2-vs3 matched probe comparison, with old-information and two-round lower bounds and n3 value7/8.',
          'closest_internal_and_external_predecessors':['UCT III section6.4 Proposition6','AC-RESULT-v1.0.0','RTTH-v1.0.0','Classical binary signatures and belief control','Feldbaum dual control','Shi/West wiring diagnosis','Konstantinova/Levenshtein/Siemons transposition reconstruction'],
          'reusable_knowledge':'A specified failure of reusing a one-round repair premise and an explicit indefinitely repeatable partial-identification controller.',
          'evidence_and_limits':'General conditional proofs plus exact finite witnesses and independent checks; n5 upper result only, full-vector feedback, physical probes and fixed within-round wiring; global priority and empirical/experiential application open.',
          'decision':'COMPLETE_MANUSCRIPT',
          'r188_separate_decision':'HOLD_STANDALONE_TECHNICAL_SUPPLEMENT_CANDIDATE',
          'next_specific_action':'Before formal map/publication promotion, complete the applicable full-map semantic integration. Remaining mathematical frontier n>=6 under the same contract.'},
       'map_semantics_changed':False,
       'new_scientific_claims_proposed_outside_effective_map':True,
       'whole_map_audit_if_required':{'status':'AUDIT_INCOMPLETE_FOR_NEW_MODULE','effective_review_items_unchanged':1608,
          'new_full_semantic_checks_completed':0,'module':'records/ONLINE_AC_20261009_Dynamic_Calibration/MAP_EXTENSION_PENDING.json',
          'enabled_as_established_premises':False},
       'work_log_path':'records/PUB20261009_Publication_Coverage/WORK_LOG.md',
       'handoff_path':'records/PUB20261009_Publication_Coverage/HANDOFF_ZH.md',
       'persistence_receipt_path':'persistence/UCT-PUB-v1.0.0_RECEIPT.json',
       'publication_action':'No DOI/OTS/Arweave/journal action; working manuscript adds zero formal publications.'}
    write(REC/'COVERAGE_UPDATE.json',update)
    for name in ['write_assessment_report.py','write_current_coverage_pointers.py','finalize_coverage_decision.py']:
        shutil.copyfile(AUDIT/name,REC/name)
    print(json.dumps({'coverage':VERSION,'items':len(index),'dynamic_claims':len(claim_ledger['claims']),
                      'remaining_unverified':len(reconciliation['remaining_unverified_ids']),
                      'paper':'COMPLETE_WORKING_MANUSCRIPT','formal_publication_count_change':0}))

if __name__=='__main__':main()
