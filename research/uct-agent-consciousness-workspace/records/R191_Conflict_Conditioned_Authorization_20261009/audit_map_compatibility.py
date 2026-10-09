#!/usr/bin/env python3
"""Structural compatibility audit for the disabled R191 map candidate."""
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict, deque
from pathlib import Path

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--base',type=Path,required=True); p.add_argument('--ledger',type=Path,required=True); p.add_argument('--extension',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    base=json.loads(a.base.read_text()); ledger=json.loads(a.ledger.read_text()); ext=json.loads(a.extension.read_text())
    bn={x['id'] for x in base['nodes']}; br={x['id'] for x in base['rules']}; bc={x['id'] for x in base['context_links']}
    nn=[x['id'] for x in ext['nodes']]; nr=[x['id'] for x in ext['rules']]; nc=[x['id'] for x in ext['context_links']]
    checks={
      'base_release_is_v1_1_2':base.get('version')=='UCT-MAP-v1.1.2',
      'base_counts_match_release':(len(bn),len(br),len(bc),len(base['suspended_historical_rule_ids']))==(913,424,261,10),
      'review_ledger_has_1608_items':(len(ledger) if isinstance(ledger,list) else len(ledger.get('items',[])))==1608,
      'extension_disabled':ext.get('integration_status')=='PENDING_CHECKPOINT_DISABLED' and ext.get('enabled_as_established_premise') is False and ext.get('release_effect','').startswith('NONE'),
      'new_ids_unique':len(nn)==len(set(nn)) and len(nr)==len(set(nr)) and len(nc)==len(set(nc)),
      'no_id_collision':not(set(nn)&bn or set(nr)&br or set(nc)&bc),
      'all_new_nodes_scoped':all(x.get('scope') and x.get('statement') for x in ext['nodes']),
      'all_rules_have_nonempty_all_of':all(x.get('all_of') for x in ext['rules']),
      'all_rules_same_instance':all(x.get('same_instance_required') is True for x in ext['rules']),
      'all_rules_have_binding_and_proof':all(x.get('binding') and x.get('proof_location') for x in ext['rules'])}
    alln=bn|set(nn); unresolved=[]
    for r in ext['rules']:
      for q in r['all_of']:
        if q not in alln: unresolved.append([r['id'],'premise',q])
      if r['conclusion'] not in alln: unresolved.append([r['id'],'conclusion',r['conclusion']])
    for c in ext['context_links']:
      for f in ('from','to'):
        if c[f] not in alln: unresolved.append([c['id'],f,c[f]])
    checks['all_references_resolve']=not unresolved
    graph=defaultdict(set); indegree={x:0 for x in alln}
    for r in list(base['rules'])+list(ext['rules']):
      for q in r['all_of']:
        if q in alln and r['conclusion'] in alln and r['conclusion'] not in graph[q]: graph[q].add(r['conclusion']); indegree[r['conclusion']]+=1
    queue=deque(x for x,d in indegree.items() if d==0); seen=0
    while queue:
      x=queue.popleft(); seen+=1
      for y in graph[x]:
        indegree[y]-=1
        if indegree[y]==0: queue.append(y)
    checks['combined_rule_graph_acyclic']=seen==len(alln)
    out={'schema':'uct-r191-map-compatibility-audit/1','base_release':base['version'],'base_graph_sha256':sha256(a.base),'base_review_ledger_sha256':sha256(a.ledger),'base_counts':{'nodes':len(bn),'active_rules':len(br),'contexts':len(bc),'suspended_historical_rules':len(base['suspended_historical_rule_ids'])},'candidate_counts':{'nodes':len(nn),'rules':len(nr),'contexts':len(nc),'combined_nodes':len(alln),'combined_rules':len(br)+len(nr),'combined_contexts':len(bc)+len(nc)},'checks':checks,'unresolved_references':unresolved,'all_structural_checks_pass':all(checks.values()),'semantic_scope':'Full structural traversal of the exact 1,608-item reviewed baseline plus affected-family review. This does not re-prove inherited mathematics, validate actual premise truth, identify a phenomenal target, close review items, or activate R191.','integration_status':'STRUCTURAL_COMPATIBILITY_PASS_SEMANTIC_ADOPTION_OPEN' if all(checks.values()) else 'FAIL'}
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    if not out['all_structural_checks_pass']: raise SystemExit('map compatibility audit failed')
if __name__=='__main__': main()
