#!/usr/bin/env python3
"""Structural coverage and scoped inheritance audit; never semantic-proof certification."""
import argparse,json,hashlib,gzip
from pathlib import Path
from collections import defaultdict,deque

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--extension',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 b=json.loads(a.base.read_text());l=json.loads(a.ledger.read_text());e=json.loads(a.extension.read_text())
 bn={x['id'] for x in b['nodes']};en={x['id'] for x in e['nodes']};alln=bn|en
 unresolved=[];g=defaultdict(set);degree={x:0 for x in alln}
 for rule in b['rules']+e['rules']:
  if rule['conclusion'] not in alln:unresolved.append(rule['id'])
  for q in rule['all_of']:
   if q not in alln:unresolved.append(rule['id'])
   if q in alln and rule['conclusion'] in alln and rule['conclusion'] not in g[q]:g[q].add(rule['conclusion']);degree[rule['conclusion']]+=1
 for ctx in b['context_links']+e['context_links']:
  for fld in ('from','to'):
   ref=ctx.get(fld,ctx.get({'from':'source','to':'target'}[fld]))
   ref_type=ctx.get(fld+'_type',ctx.get({'from':'source_type','to':'target_type'}[fld],'node'))
   nonnode=ref_type in ('source_reference','module_reference','module','external_source') or (fld=='from' and bool(ctx.get('external_source')))
   if ref not in alln and not nonnode:unresolved.append(ctx['id'])
 queue=deque(k for k,v in degree.items() if v==0);visited=0
 while queue:
  q=queue.popleft();visited+=1
  for z in g[q]:
   degree[z]-=1
   if not degree[z]:queue.append(z)
 checks=dict(base_release=b['version']=='UCT-MAP-v1.1.2',base_counts=tuple(len(b[k]) for k in ('nodes','rules','context_links'))==(913,424,261),suspended_rules=len(b['suspended_historical_rule_ids'])==10,ledger_count=len(l['items'])==1608,base_hash=sha(a.base)=='0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612',ledger_hash=sha(a.ledger)=='0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687',candidate_disabled=e['integration_status']=='PENDING_CHECKPOINT_DISABLED' and not e['enabled_as_established_premise'],no_release_change=e['release_effect'].startswith('NONE'),candidate_counts=tuple(len(e[k]) for k in ('nodes','rules','context_links'))==(11,5,5),unique_new_nodes=len(en)==len(e['nodes']),no_collision=not bn&en,typed_scoped_nodes=all(all(n.get(x) for x in ('kind','statement','scope','quantifier','status')) for n in e['nodes']),joint_premises=all(len(x['all_of'])>=2 for x in e['rules']),same_instance=all(x['same_instance_required'] and x['binding'] for x in e['rules']),proof_and_alternatives=all(x['proof_location'] and x['alternative_route_semantics'] for x in e['rules']),refs_resolve=not unresolved,acyclic=visited==len(alln),c1_preserved=any(x['to']=='A:C1' and x['type']=='AXIOM_STATUS_PRESERVED' for x in e['context_links']),non_gate=any(x['to']=='A:U1' and x['type']=='NON_GATE_CONTEXT' for x in e['context_links']),actual_use_separation=any(x['to']=='R173:RETENTIVE_BINDING_RELATION' for x in e['context_links']),report_limit=any(x['to']=='R157:REPORT_COVERAGE_LIMIT' for x in e['context_links']),empirical_premises_open=all(n['status'].startswith('OPEN') for n in e['nodes'] if n['id'] in ('R204:ACTUAL_APPLICATION','R204:H_BRIDGE')))
 coverage=[]
 for kind in ('nodes','rules','context_links'):
  for item in b[kind]:
   text=json.dumps(item,sort_keys=True,ensure_ascii=False)
   coverage.append(dict(id=item['id'],kind=kind,sha256=hashlib.sha256(text.encode()).hexdigest(),scope='FROZEN_BASE_UNCHANGED; structural references checked; exact prior proof/review inherited',semantic_status='NO_NEW_END_TO_END_SEMANTIC_PROOF',current_effect='NONE_FROM_DISABLED_R204'))
 reviewids=[x.get('id',x.get('item_id')) for x in l['items']]
 result=dict(schema='uct-r204-map-audit/1',base_sha256=sha(a.base),ledger_sha256=sha(a.ledger),counts=dict(nodes=913,rules=424,contexts=261,suspended=10,review_items=len(reviewids)),candidate_counts=dict(nodes=11,rules=5,contexts=5),checks=checks,all_structural_checks_pass=all(checks.values()),unresolved=unresolved,semantic_adoption='OPEN; FULL_NEW_SEMANTIC_REPROOF_NOT_COMPLETED',inherited_coverage='Every base item recorded by stable ID and content hash; base proofs reused, not newly reproved.',affected_rederivation='R173 actual RetBind remains more than current F/use. R199 clones retain matched future traces. R204 success/alignment/use separation and probes do not supply H or an actual complete signature. C1/U1 and R157 transport remain unchanged/open.',integration='PENDING_CHECKPOINT_DISABLED')
 a.output.write_text(json.dumps(result,indent=2)+'\n');a.output.with_name('WHOLE_MAP_COVERAGE.json.gz').write_bytes(gzip.compress((json.dumps(dict(items=coverage,review_item_ids=reviewids,semantic_limit=result['semantic_adoption']),separators=(',',':'))+'\n').encode(),mtime=0))
 print(json.dumps(dict(structural_pass=result['all_structural_checks_pass'],checks=len(checks),covered_objects=len(coverage),review_items=len(reviewids),semantic_adoption='OPEN')))
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
