#!/usr/bin/env python3
"""Bounded structural coverage only. Review prose/receipts remain authoritative."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
GRAPH_SHA = '0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612'
LEDGER_SHA = '0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687'


def digest(data): return hashlib.sha256(data).hexdigest()
def canonical(x): return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline-graph', type=Path, required=True)
    p.add_argument('--review-ledger', type=Path, required=True)
    p.add_argument('--pending-mpc', type=Path, default=HERE.parent / 'MPC20261010_Motor_Proprioceptive_Consumers/MAP_EXTENSION.json')
    a = p.parse_args()
    gb, lb = a.baseline_graph.read_bytes(), a.review_ledger.read_bytes()
    assert digest(gb) == GRAPH_SHA
    assert digest(lb) == LEDGER_SHA
    base, ledger = json.loads(gb), json.loads(lb)
    g = json.loads((HERE / 'MAP_EXTENSION.json').read_text())
    component = json.loads((HERE / 'device_model/MAP_EXTENSION.json').read_text())
    mpc = json.loads(a.pending_mpc.read_text())
    assert [len(base[k]) for k in ['nodes', 'rules', 'context_links']] == [913, 424, 261]
    assert len(base['suspended_historical_rule_ids']) == 10 and len(ledger['items']) == 1608
    assert [len(g[k]) for k in ['nodes', 'rules', 'context_links']] == [24, 6, 15]
    existing = {e['id']: e for k in ['nodes', 'rules', 'context_links'] for e in base[k]}
    current = {e['id']: e for k in ['nodes', 'rules', 'context_links'] for e in g[k]}
    pending = {e['id'] for e in mpc['nodes']}
    assert len(existing) == 1598 and len(current) == 45 and not (existing.keys() & current.keys())
    assert g['enabled_as_established_premise'] is False and g['actual_application_established'] is False
    for e in current.values(): assert e.get('enabled_as_established_premise') is False
    all_ids = set(existing) | set(current) | pending
    external = set()
    for rule in g['rules']:
        assert rule.get('same_instance_required') is True
        assert rule.get('actual_premises_discharged') is False
        for target in rule['all_of'] + [rule['conclusion']]:
            assert target in all_ids, target
            if target not in current: external.add(target)
    for edge in g['context_links']:
        assert edge['deductive'] is False
        for target in [edge['from'], edge['to']]:
            assert target in all_ids, target
            if target not in current: external.add(target)
    for k in ['nodes', 'context_links']:
        for e in component[k]: assert current[e['id']] == e
    for e in component['rules']:
        revised = dict(current[e['id']]); old = dict(e)
        revised.pop('proof_location'); old.pop('proof_location')
        assert revised == old
    evidence = json.loads((HERE / 'EVIDENCE_CANDIDATE_ADDITION.json').read_text())
    assert len(evidence['nodes']) == 3 and len(evidence['context_links']) == 3
    assert evidence['no_new_deductive_rule'] is True
    rows = []
    ledger_ids = set()
    for entry in ledger['items']:
        item_id = entry['item_id']; assert item_id not in ledger_ids; ledger_ids.add(item_id)
        record = existing.get(item_id, entry)
        rows.append({'id': item_id, 'type': entry['item_type'], 'record_sha256': digest(canonical(record)), 'visited_by_structural_code': True, 'semantic_reading_claim_from_this_program': False})
    assert set(existing) <= ledger_ids
    assert set(base['suspended_historical_rule_ids']) <= ledger_ids
    # This computes a syntactic downstream set, not independent proof reconstruction.
    reached = set(external) & set(existing)
    reached_rules = set()
    changed = True
    while changed:
        changed = False
        for rule in base['rules']:
            if any(x in reached for x in rule['all_of']):
                reached_rules.add(rule['id'])
                if rule['conclusion'] not in reached:
                    reached.add(rule['conclusion']); changed = True
    coverage = {'schema': 'uct-structural-coverage/1', 'baseline_graph_sha256': GRAPH_SHA, 'ledger_sha256': LEDGER_SHA, 'items': rows}
    (HERE / 'STRUCTURAL_COVERAGE.json.gz').write_bytes(gzip.compress(canonical(coverage), mtime=0))
    report = {'schema': 'uct-dvc-structural-audit/1', 'status': 'STRUCTURAL_PASS_SEMANTIC_AND_ACTUAL_STATUS_SEPARATE', 'baseline_graph_sha256': GRAPH_SHA, 'review_ledger_sha256': LEDGER_SHA, 'baseline_counts': {'nodes': 913, 'rules': 424, 'contexts': 261, 'suspended': 10, 'ledger_items': 1608}, 'candidate_counts': {'nodes': 24, 'rules': 6, 'contexts': 15}, 'all_references_resolved': True, 'external_references': sorted(external), 'pending_external_references': sorted(external & pending), 'syntactic_downstream': {'rules': sorted(reached_rules), 'conclusion_and_seed_ids': sorted(reached), 'not_a_claim_of_reconstructed_proofs': True}, 'component_semantics_preserved': True, 'candidate_disabled': True, 'completed_graph_changed': False, 'semantic_certification_by_program': False, 'actual_application_established': False, 'open_reviews_closed': False, 'coverage_file': 'STRUCTURAL_COVERAGE.json.gz'}
    (HERE / 'MAP_COMPATIBILITY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'baseline_items': len(rows), 'candidate_items': len(current), 'syntactic_downstream_rules': len(reached_rules), 'candidate_disabled': True}))


if __name__ == '__main__': main()
