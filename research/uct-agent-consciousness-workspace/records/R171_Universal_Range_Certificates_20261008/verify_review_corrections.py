#!/usr/bin/env python3
"""Focused QC regressions; no global proof or physical certificate is claimed."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = json.loads((HERE / 'REVIEW_AMENDMENTS.json').read_text())
checks = []

def check(name, ok, detail):
    checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

for name, expected in [('Universal_Target_Range_Certificates_v0_1.md', A['provenance']['note_sha256'])]:
    check('frozen_note_unchanged', sha256((HERE / name).read_bytes()).hexdigest() == expected, expected)
check('restored_raw_graph_hash', sha256((ROOT / 'UCT_FORMAL_GRAPH.json').read_bytes()).hexdigest() == A['provenance']['graph_sha256'], A['provenance']['graph_sha256'])

for name in ['RESEARCH_MASTER_GUIDE.md', 'AGENTS.md', 'MEMORY.md', 'HANDOFF.md', 'MASTER_INDEX.md']:
    text = (ROOT / name).read_text()
    first = text.splitlines()[0]
    check('authoritative_entry_' + name, first == '# Authoritative current checkpoint — R171 with review response', first)

# Unrestricted completions on two target points, one observed point.
worlds = list(product((False, True), repeat=2))
unrestricted = [w for w in worlds if w[0]]
constant = [w for w in worlds if w[0] == w[1] and w[0]]
check('unrestricted_H_has_both_completions', (True, True) in unrestricted and (True, False) in unrestricted, unrestricted)
check('constant_H_blocks_hidden_alteration', constant == [(True, True)], constant)

def fires(route, evidence):
    return all(evidence.get(p, False) for p in route['all_of'])

base = dict(R170_application_holds=True, common_target_binding=True, domain_scope_accepted=True, valid=True, not_refuted=True)
route_cases = []
for d, i in product((False, True), repeat=2):
    e = dict(base, D_discharged=d, I_discharged=i)
    fired = [r['id'] for r in A['A2']['effective_instance_routes'] if fires(r, e)]
    route_cases.append({'D_discharged': d, 'I_discharged': i, 'fired': fired})
check('direct_only_accepted', len(route_cases[2]['fired']) == 1 and 'direct' in route_cases[2]['fired'][0], route_cases[2])
check('inductive_only_accepted', len(route_cases[1]['fired']) == 1 and 'reachable' in route_cases[1]['fired'][0], route_cases[1])
check('neither_route_unproved_not_certified', not route_cases[0]['fired'], route_cases[0])
check('both_routes_available_no_joint_requirement', len(route_cases[3]['fired']) == 2, route_cases[3])
for d, i in [(True, False), (False, True)]:
    for omitted in base:
        e = dict(base, D_discharged=d, I_discharged=i)
        e[omitted] = False
        check('all_of_gate_' + ('D' if d else 'I') + '_' + omitted, not any(fires(r, e) for r in A['A2']['effective_instance_routes']), omitted)

counts = {}
for valid, refuted, d, i, spec, empirical in product((False, True), repeat=6):
    e = dict(valid=valid, invalid=not valid, refuted=refuted, not_refuted=not refuted,
             D_discharged=d, I_discharged=i, neither_route_discharged=not (d or i),
             specification_evidence=spec, no_specification_evidence=not spec,
             empirical_evidence=empirical, no_empirical_evidence=not empirical)
    status = next(row['status'] for row in A['A2']['status_priority'] if all(e[p] for p in row['all_of']))
    counts[status] = counts.get(status, 0) + 1
check('seven_statuses_cover_64_assignments', set(counts) == set(A['A3']['states']) and sum(counts.values()) == 64, counts)

# The reviewer's fixed two-bit interface countermodel, not a new theorem.
standalone = (0, 0)
coupled_inputs = (1 - standalone[1], 1 - standalone[0])
check('TE_QC_01_exposes_input_contract_violation', coupled_inputs == (1, 1), {'initial': standalone, 'coupled_successor': coupled_inputs})

# Matched baseline action/report, distinct declared intervention response.
replay_rows = []
for b in (0, 1):
    k = b
    tape = b
    replay_rows.append({'b': b, 'baseline_A': k, 'baseline_B': tape, 'report_A': 0, 'report_B': 0,
                        'do_k_A': 1 - b, 'do_k_B': tape})
check('TE_QC_02_matched_trace_distinct_use', all(x['baseline_A'] == x['baseline_B'] and x['report_A'] == x['report_B'] and x['do_k_A'] != x['do_k_B'] for x in replay_rows), replay_rows)

out = {'schema': 'UCT_REVIEW_CORRECTION_CHECKS/v1', 'status': 'PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL',
       'checks': checks, 'route_cases': route_cases,
       'limits': ['Focused finite regression and exact file integrity only; not general/global semantic proof.', 'No physical live/replay realization or B_min/F_O validation.']}
(HERE / 'REVIEW_CORRECTION_CHECKS.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({'status': out['status'], 'checks': len(checks), 'statuses': counts}))
if out['status'] != 'PASS': raise SystemExit(1)
