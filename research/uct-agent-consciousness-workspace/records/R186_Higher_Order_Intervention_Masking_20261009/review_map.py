import json,hashlib,pathlib,collections
out=pathlib.Path(__file__).parent
root=pathlib.Path('/mnt/data/UCT_MGTD_Research_20261009/v11_source')
g=json.load(open(root/'UCT_EFFECTIVE_GRAPH.json'))
ledger=json.load(open(root/'REVIEW_LEDGER.json'))['items']
node_ids={v['id'] for v in g['nodes']}; rule_ids={v['id'] for v in g['rules']}; link_ids={v['id'] for v in g['context_links']}
assert len(node_ids)==len(g['nodes'])==776
assert len(rule_ids)==len(g['rules'])==366
assert len(link_ids)==len(g['context_links'])==221
assert len(ledger)==1373
status=collections.Counter()
rows=[]
for item in ledger:
 key=item['item_id'];typ=item['item_type'];s=item.get('effective_statement','')
 assert s.strip(),(key,'blank')
 if typ=='node':assert key in node_ids
 elif typ=='rule':assert key in rule_ids or key in g['suspended_historical_rule_ids']
 elif typ=='context':assert key in link_ids
 else:raise ValueError((key,typ))
 # Semantic review requires interpretation: machine only issues explicit routing and inherited checks.
 related=any(k in (s+' '+item.get('scope','')).lower() for k in ('interven','update','sequence','independen','commut','local','causal','output','report','experience','token'))
 verdict='REQUIRES_HUMAN_SEMANTIC_REVIEW' if related else 'INHERITED_UNCHANGED_REVIEW_NOT_REPROVED'
 status[verdict]+=1
 rows.append({'id':key,'type':typ,'decision':verdict,'original_review':item.get('this_review_decision') or item.get('parent_decision'),'content_sha256':hashlib.sha256(s.encode()).hexdigest()})
result={'baseline':'UCT-MAP-v1.1.0','source_commit':'e1ceadd3097bec5ac6abb4510ae613ff7e41bbc3','census':len(rows),'nodes':776,'active_rules':366,'context_links':221,'suspended_rules':10,'status_counts':dict(status),'scope':'mechanical full-census and targeted conceptual attack only; full fresh per-item semantic certification NOT COMPLETE','map_status':'PENDING_MAP / AUDIT_INCOMPLETE','policy':'No automatic premise promotion'}
(out/'AUDIT_COVERAGE.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
(out/'ITEM_LEVEL_COVERAGE.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
print(result)
