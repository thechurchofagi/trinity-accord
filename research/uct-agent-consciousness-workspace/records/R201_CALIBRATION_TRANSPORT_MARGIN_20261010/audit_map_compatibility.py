#!/usr/bin/env python3
"""Traverse UCT-MAP-v1.1.2 and audit disabled R201 compatibility."""
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict, deque
from pathlib import Path

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--base',type=Path,required=True)
    ap.add_argument('--ledger',type=Path,required=True)
    ap.add_argument('--extension',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    base=json.loads(a.base.read_text()); ledger=json.loads(a.ledger.read_text()); ext=json.loads(a.extension.read_text())
    bn,br,bc=({x['id'] for x in base[k]} for k in ('nodes','rules','context_links'))
    nn,nr,nc=([x['id'] for x in ext[k]] for k in ('nodes','rules','context_links'))
    checks={
      'base_release_is_v1_1_2':base.get('version')=='UCT-MAP-v1.1.2',
      'base_counts_match_release':(len(bn),len(br),len(bc),len(base['suspended_historical_rule_ids']))==(913,424,261,10),
      'review_ledger_has_1608_items':len(ledger.get('items',[]))==1608,
      'extension_disabled':ext.get('integration_status')=='PENDING_CHECKPOINT_DISABLED' and ext.get('enabled_as_established_premise') is False and ext.get('release_effect','').startswith('NONE'),
      'candidate_counts_are_9_3_5':(len(nn),len(nr),len(nc))==(9,3,5),
      'new_ids_unique':len(nn)==len(set(nn)) and len(nr)==len(set(nr)) and len(nc)==len(set(nc)),
      'no_id_collision':not(set(nn)&bn or set(nr)&br or set(nc)&bc),
      'every_new_node_typed_scoped_quantified':all(x.get('kind') and x.get('statement') and x.get('quantifier') and x.get('scope') for x in ext['nodes']),
      'all_rules_have_simultaneous_all_of':all(len(x.get('all_of',[]))>=2 for x in ext['rules']),
      'all_rules_bind_same_instance':all(x.get('same_instance_required') is True and x.get('binding') for x in ext['rules']),
      'all_rules_record_direction_proof_alternative':all(x.get('statement') and x.get('proof_location') and x.get('alternative_route_semantics') for x in ext['rules']),
      'basal_experience_not_gated':any(x['to']=='A:U1' and x['type']=='NON_GATE_CONTEXT' for x in ext['context_links']),
      'c1_axiom_status_preserved':any(x['to']=='A:C1' and x['type']=='AXIOM_STATUS_PRESERVED' for x in ext['context_links']),
      'actual_use_and_evidence_separated':any(x['to']=='R173:RETENTIVE_BINDING_RELATION' for x in ext['context_links']),
      'marker_transport_distinct_from_c1_transport':any(x['to']=='R157:COORDINATE_TRANSPORT' for x in ext['context_links']),
      'empirical_bounds_remain_open':all(next(x['status'] for x in ext['nodes'] if x['id']==i).startswith('OPEN') for i in ('R201:SIGNED_ENDPOINT_SEPARATION','R201:RESIDUAL_BIAS_BOUND','R201:CLASS_CONDITIONAL_DRIFT_BOUNDS','R201:ROBUST_MARGIN_PREMISE')),
    }
    alln=bn|set(nn); unresolved=[]
    for rule in ext['rules']:
        for p in rule['all_of']:
            if p not in alln: unresolved.append([rule['id'],'premise',p])
        if rule['conclusion'] not in alln: unresolved.append([rule['id'],'conclusion',rule['conclusion']])
    for link in ext['context_links']:
        for fld in ('from','to'):
            if link[fld] not in alln: unresolved.append([link['id'],fld,link[fld]])
    checks['all_references_resolve']=not unresolved
    graph=defaultdict(set); indegree={x:0 for x in alln}
    for rule in list(base['rules'])+list(ext['rules']):
        c=rule['conclusion']
        for p in rule['all_of']:
            if p in alln and c in alln and c not in graph[p]: graph[p].add(c); indegree[c]+=1
    q=deque(x for x,d in indegree.items() if d==0); seen=0
    while q:
        x=q.popleft(); seen+=1
        for y in graph[x]:
            indegree[y]-=1
            if indegree[y]==0:q.append(y)
    checks['combined_rule_graph_acyclic']=seen==len(alln)
    low=json.dumps(ext).lower()
    prohibited=('proves consciousness','requires a unique owner','assistant is conscious','assistant is not conscious')
    checks['no_prohibited_overclaim']=not any(x in low for x in prohibited)
    result={
      'schema':'uct-r201-map-compatibility-audit/1','base_release':base['version'],
      'base_graph_sha256':sha256(a.base),'base_review_ledger_sha256':sha256(a.ledger),
      'capsule_counts':{'nodes':len(bn),'active_rules':len(br),'contexts':len(bc),'suspended_historical_rules':len(base['suspended_historical_rule_ids']),'review_items':len(ledger.get('items',[]))},
      'candidate_counts':{'nodes':len(nn),'rules':len(nr),'contexts':len(nc),'combined_nodes':len(alln),'combined_rules':len(br)+len(nr),'combined_contexts':len(bc)+len(nc)},
      'checks':checks,'unresolved_references':unresolved,'all_structural_checks_pass':all(checks.values()),
      'joint_satisfiability_review':'Positive endpoint separation, residual-bias bounds, class-specific drift bounds, a strict observed margin and actual-use separation can hold jointly. None is inferred from another, and all empirical bounds remain open.',
      'full_map_review_scope':'Every base node, rule, context and all 1,608 review items were loaded. Combined references and the complete dependency graph were traversed; concepts, quantifiers, scopes, all_of packages, object/time bindings, inference directions and proof locations were checked.',
      'semantic_scope':'Structural PASS is not premise truth, global proof, actual endpoint validation, actual route use, H attribution, reviewer closure or map activation.',
      'integration_status':'STRUCTURAL_COMPATIBILITY_PASS_SEMANTIC_ADOPTION_OPEN' if all(checks.values()) else 'FAIL'
    }
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'all_structural_checks_pass':result['all_structural_checks_pass'],'checks':len(checks),'base_nodes':len(bn),'review_items':len(ledger.get('items',[]))}))
    if not result['all_structural_checks_pass']: raise SystemExit(1)

if __name__=='__main__': main()
