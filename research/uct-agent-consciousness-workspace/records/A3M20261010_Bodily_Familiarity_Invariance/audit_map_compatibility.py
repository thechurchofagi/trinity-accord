"""Traverse frozen map and disabled A3M application overlay; no semantic proof claim."""
from pathlib import Path
from collections import defaultdict, deque
import argparse
import gzip
import hashlib
import json

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

a = argparse.ArgumentParser()
a.add_argument('--base', type=Path, required=True)
a.add_argument('--ledger', type=Path, required=True)
a.add_argument('--extension', type=Path, required=True)
a.add_argument('--output', type=Path, required=True)
args = a.parse_args()
g = json.loads(args.base.read_text())
l = json.loads(args.ledger.read_text())
e = json.loads(args.extension.read_text())
ids = {n['id'] for n in g['nodes']}
edges = defaultdict(set)
degree = dict.fromkeys(ids, 0)
unresolved = []
for r in g['rules']:
    assert isinstance(r['all_of'], list) and r['all_of']
    for p in r['all_of']:
        if p not in ids or r['conclusion'] not in ids:
            unresolved.append(r['id'])
        elif r['conclusion'] not in edges[p]:
            edges[p].add(r['conclusion'])
            degree[r['conclusion']] += 1
for c in g['context_links']:
    for field in ('from', 'to'):
        ref = c.get(field, c.get({'from':'source','to':'target'}[field]))
        typ = c.get(field+'_type', c.get({'from':'source_type','to':'target_type'}[field], 'node'))
        external = typ in ('source_reference','module_reference','module','external_source') or (field == 'from' and c.get('external_source'))
        if ref not in ids and not external:
            unresolved.append(c['id'])
q = deque(n for n in degree if not degree[n])
visited = 0
while q:
    n = q.popleft()
    visited += 1
    for child in edges[n]:
        degree[child] -= 1
        if degree[child] == 0:
            q.append(child)
bindings = [x for app in e['applications'] for x in app.get('completed_node_refs', [])]
checks = dict(
    base_counts=tuple(len(g[k]) for k in ('nodes','rules','context_links')) == (913,424,261),
    suspended=len(g['suspended_historical_rule_ids']) == 10,
    review_count=len(l['items']) == 1608,
    base_hash=sha(args.base) == '0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612',
    ledger_hash=sha(args.ledger) == '0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687',
    no_new_deductions=not e['nodes'] and not e['rules'] and not e['context_links'],
    disabled=not e['enabled'] and not e['enabled_as_established_premise'],
    refs_resolve=not unresolved and all(x in ids for x in bindings),
    dag=visited == len(ids),
    c1_u1_preserved=e['foundation_effect'] == 'NONE',
    application_not_premise_truth=all(not x['actual_premises_discharged'] for x in e['applications']),
)
coverage = []
for kind in ('nodes','rules','context_links'):
    for item in g[kind]:
        coverage.append(dict(id=item['id'],kind=kind,
            sha256=hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            current_semantic_scope='UNCHANGED_FROZEN_OBJECT; NOT_NEW_END_TO_END_REPROOF',
            current_effect='NO_DEDUCTIVE_CHANGE_FROM_A3M_APPLICATION_AMENDMENT'))
result = dict(schema='uct-a3m-compatibility-audit/1',checks=checks,
    all_structural_checks_pass=all(checks.values()),base_sha256=sha(args.base),ledger_sha256=sha(args.ledger),
    covered_objects=len(coverage),review_items=len(l['items']),candidate_counts=dict(nodes=0,rules=0,contexts=0),
    unresolved=unresolved,semantic_status='AUDIT_INCOMPLETE: inherited deep contracts/source proofs not freshly reconstructed',
    manually_reviewed_affected_contracts=['r173_retentive_coordinate_transport','r175_r173_target_boundary_effective',
        'r176_present_slice_effective','r177_source_feature_separation',
        'R199:LINEAGE_PROBE_CEILING (disabled candidate)','R200:SEMANTIC_CALIBRATION_FIREWALL (disabled candidate)',
        'A3M-C1..C5 disabled application contracts'],
    inference_effect='Off-diagonal support and independent endpoint orientation are application guards; no H assignment follows.',
    foundation_changed=False)
args.output.write_text(json.dumps(result,indent=2)+'\n')
args.output.with_name('WHOLE_MAP_COVERAGE.json.gz').write_bytes(gzip.compress(json.dumps(dict(
    items=coverage,review_ids=[x.get('id',x.get('item_id')) for x in l['items']],
    semantic_status=result['semantic_status']),separators=(',',':')).encode(),mtime=0))
print(json.dumps(dict(structural_pass=all(checks.values()),covered_objects=len(coverage),semantic_status=result['semantic_status'])))
assert all(checks.values()), checks
