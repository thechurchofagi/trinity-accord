#!/usr/bin/env python3
"""Whole frozen-map structural traversal for A3O; not a semantic reproof."""
from pathlib import Path
from collections import defaultdict, deque
import argparse, gzip, hashlib, json

p=argparse.ArgumentParser(); p.add_argument('--base',type=Path,required=True); p.add_argument('--ledger',type=Path,required=True); p.add_argument('--extension',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
g=json.loads(a.base.read_text()); l=json.loads(a.ledger.read_text()); e=json.loads(a.extension.read_text())
sha=lambda x: hashlib.sha256(x.read_bytes()).hexdigest()
ids={n['id'] for n in g['nodes']}; edges=defaultdict(set); indeg=dict.fromkeys(ids,0); unresolved=[]
for r in g['rules']:
    assert isinstance(r['all_of'],list) and r['all_of']
    for x in r['all_of']:
        if x not in ids or r['conclusion'] not in ids: unresolved.append(r['id'])
        elif r['conclusion'] not in edges[x]: edges[x].add(r['conclusion']); indeg[r['conclusion']]+=1
for c in g['context_links']:
    for fld,alt in [('from','source'),('to','target')]:
        ref=c.get(fld,c.get(alt)); typ=c.get(fld+'_type',c.get(alt+'_type','node'))
        external=typ in ('source_reference','module_reference','module','external_source') or (fld=='from' and c.get('external_source'))
        if ref not in ids and not external: unresolved.append(c['id'])
q=deque(x for x,v in indeg.items() if not v); seen=0
while q:
    x=q.popleft(); seen+=1
    for y in edges[x]:
        indeg[y]-=1
        if not indeg[y]: q.append(y)
refs=[z for app in e['applications'] for z in app['completed_node_refs']]
checks={
 'counts':tuple(len(g[k]) for k in ('nodes','rules','context_links'))==(913,424,261),
 'suspended':len(g['suspended_historical_rule_ids'])==10,
 'review_count':len(l['items'])==1608,
 'base_hash':sha(a.base)=='0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612',
 'ledger_hash':sha(a.ledger)=='0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687',
 'all_of_refs_and_context_refs':not unresolved, 'dag':seen==len(ids), 'completed_refs':all(x in ids for x in refs),
 'disabled_zero_graph_delta':not e['enabled'] and not e['nodes'] and not e['rules'] and not e['context_links'],
 'joint_actual_premises_open':all(not x['actual_premises_discharged'] for x in e['applications']), 'foundation_unchanged':e['foundation_effect']=='NONE'}
coverage=[]
for kind in ('nodes','rules','context_links'):
  for item in g[kind]: coverage.append({'id':item['id'],'kind':kind,'sha256':hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest(),'scope':'UNCHANGED_FROZEN_OBJECT_NOT_FRESH_SEMANTIC_REPROOF'})
out={'schema':'uct-a3o-map-audit/1','checks':checks,'all_structural_checks_pass':all(checks.values()),'covered_objects':len(coverage),'review_items':len(l['items']),'candidate_counts':{'nodes':0,'rules':0,'contexts':0},'semantic_status':'AUDIT_INCOMPLETE','affected_contracts':['R173 retentive binding','R175 target separation','R177 source/feature separation','R200 semantic firewall (disabled)','A3M/A3N application contracts'],'inference_effect':'Route grain and selector topology constrain an application; they do not establish route use, H, experience, or a report semantics.','unresolved':unresolved}
a.output.write_text(json.dumps(out,indent=2)+'\n'); a.output.with_name('WHOLE_MAP_COVERAGE.json.gz').write_bytes(gzip.compress(json.dumps({'items':coverage,'review_ids':[x.get('id',x.get('item_id')) for x in l['items']],'semantic_status':'AUDIT_INCOMPLETE'},separators=(',',':')).encode(),mtime=0)); print(json.dumps({'pass':all(checks.values()),'covered':len(coverage),'reviews':len(l['items'])})); assert all(checks.values()),checks
