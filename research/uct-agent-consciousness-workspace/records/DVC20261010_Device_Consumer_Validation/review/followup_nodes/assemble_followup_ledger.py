#!/usr/bin/env python3
"""Assemble recorded field inventories after the manual scoped reading.
This script does not conduct semantic review, reconstruct proofs, or promote premises.
"""
import collections, csv, gzip, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
GRAPH=ROOT/'workbench/audit/baseline/UCT_EFFECTIVE_GRAPH.json'
LEDGER=ROOT/'workbench/audit/baseline/REVIEW_LEDGER.json'
PRIOR=ROOT/'workbench/doi20261010/dvc_review/BASELINE_PER_ID_READ_SCOPE.json'
UNREAD=ROOT/'workbench/doi20261010/dvc_review/UNREAD_BASELINE_IDS.json'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x):
 p=OUT/name;p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');return p

def leaves(x,p=''):
 if isinstance(x,dict) and x:
  return {q:v for k,y in x.items() for q,v in leaves(y,p+'/'+k.replace('~','~0').replace('/','~1')).items()}
 if isinstance(x,list) and x:
  return {q:v for k,y in enumerate(x) for q,v in leaves(y,p+'/'+str(k)).items()}
 return {p:x}

g,l,prior,u=map(read,[GRAPH,LEDGER,PRIOR,UNREAD])
gm={n['id']:n for n in g['nodes']};lm={i['item_id']:i for i in l['items']}
extracted=read(OUT/'EXTRACTED_READ_FIELDS.json');adj=read(OUT/'ADJUDICATIONS.json')
ids={i['item_id'] for i in u['items'] if i['item_type']=='node'}
assert len(ids)==599==len(extracted)
assert {i['id'] for i in extracted}==ids
assert not adj['forced_node_revisions']
prior_nodes=[i for i in prior['items'] if i['item_type']=='node' and i['item_id'] not in ids]
assert len(prior_nodes)==314
assert {i['item_id'] for i in prior_nodes}.isdisjoint(ids)
assert {i['item_id'] for i in prior_nodes}|ids==set(gm) and len(gm)==913

items=[]
for a in extracted:
 ident=a['id'];n=gm[ident];old=lm[ident];prefix=ident.split(':')[0]
 assert prefix in adj['family_assessments']
 gf=a['graph_fields'];lf=dict(a['ledger_fields'])
 lf.update({('/'+k):old[k] for k in ['source_review','review_outcome','actual_premise_discharged_by_review']})
 gl={q:v for p,v in gf.items() for q,v in leaves(v,p).items()}
 ll={q:v for p,v in lf.items() for q,v in leaves(v,p).items()}
 allg,alll=leaves(n),leaves(old)
 assert all(allg[p]==v for p,v in gl.items())
 assert all(alll[p]==v for p,v in ll.items())
 graph_remaining=sorted(set(allg)-set(gl));ledger_remaining=sorted(set(alll)-set(ll))
 pointer_limits=[p for p,v in gf.items() if isinstance(v,str) and v.startswith('See explicit general or finite statement')]
 items.append({'item_id':ident,'item_type':'node','status':'SCOPED_CORE_READ_COMPATIBLE_NO_DVC_FORCED_REVISION','scope_of_conclusion':'Compatibility with DVC within the actually read fields; not full contract completeness, proof reconstruction or actual premise truth.','dvc_forces_revision':False,'reviewed_statement':n['statement'],'reviewed_scope':n['scope'],'read_graph_fields':gf,'read_ledger_fields':lf,'exact_graph_leaf_paths_read':sorted(gl),'exact_graph_leaf_paths_not_read':graph_remaining,'exact_ledger_leaf_paths_read':sorted(ll),'exact_ledger_leaf_paths_not_read':ledger_remaining,'graph_top_level_paths_not_read_at_all':sorted('/'+k for k in n if not any(p=='/'+k or p.startswith('/'+k+'/') for p in gl)),'external_quantifier_locator_paths_not_resolved':pointer_limits,'semantic_assessment':adj['family_assessments'][prefix],'targeted_assessment':adj['targeted_assessments'].get(ident),'source_record_sha256':hashlib.sha256(json.dumps(n,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'record_hash_scheme':'sha256 UTF-8 JSON ensure_ascii=False sort_keys=True separators=(comma,colon)','historical_source_proof_independently_reconstructed':False,'actual_or_named_phenomenal_premise_discharged':False,'governance_items_closed':[]})

counts={'new_nodes_read':len(items),'prior_nodes_with_scoped_reading':len(prior_nodes),'combined_nodes':len(gm),'new_nodes_without_scoped_reading':0,'forced_node_revisions':0,'new_graph_leaf_fields_read':sum(len(i['exact_graph_leaf_paths_read']) for i in items),'new_graph_leaf_fields_not_read':sum(len(i['exact_graph_leaf_paths_not_read']) for i in items),'new_ledger_leaf_fields_read':sum(len(i['exact_ledger_leaf_paths_read']) for i in items),'new_ledger_leaf_fields_not_read':sum(len(i['exact_ledger_leaf_paths_not_read']) for i in items),'new_nodes_with_graph_omissions':sum(bool(i['exact_graph_leaf_paths_not_read']) for i in items),'nodes_with_unresolved_external_quantifier_locator':sum(bool(i['external_quantifier_locator_paths_not_resolved']) for i in items),'manual_family_assessments':len(adj['family_assessments']),'manual_targeted_assessments':sum(i['targeted_assessment'] is not None for i in items)}
common={'schema':'uct-dvc-node-followup-scoped-review/1','recorded_finish_utc':datetime.now(timezone.utc).isoformat(),'map_version':g['version'],'source_graph_sha256':sha(GRAPH),'source_ledger_sha256':sha(LEDGER),'prior_scoped_review_sha256':sha(PRIOR),'prior_unread_list_sha256':sha(UNREAD),'counts':counts,'all_913_nodes_scoped_across_two_review_records':True,'all_913_freshly_reread_by_this_worker':False,'whole_map_deep_semantic_completion':False,'independent_historical_proof_completion':False,'program_is_semantic_review':False,'actual_premises_discharged':False,'historical_depth_gaps_kept_open':prior['historical_depth_gaps_kept_open'],'concurrent_CBI_read_scope':'Not read in this node follow-up; parent manages concurrent CBI integration separately. Completed-map version unchanged.'}
p=dump('PER_ID_NODE_REVIEW.json',dict(common,items=items))
with p.open('rb') as f: data=f.read()
(OUT/'PER_ID_NODE_REVIEW.json.gz').write_bytes(gzip.compress(data,mtime=0))
assert gzip.decompress((OUT/'PER_ID_NODE_REVIEW.json.gz').read_bytes())==data

with (OUT/'PER_ID_NODE_REVIEW.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['item_id','status','dvc_forces_revision','graph_leaf_fields_read','graph_leaf_fields_not_read','ledger_leaf_fields_read','ledger_leaf_fields_not_read','reviewed_statement','reviewed_scope','semantic_assessment','targeted_assessment']);w.writeheader()
 for i in items:w.writerow({**{k:i[k] for k in ['item_id','status','dvc_forces_revision','reviewed_statement','reviewed_scope','semantic_assessment','targeted_assessment']},'graph_leaf_fields_read':len(i['exact_graph_leaf_paths_read']),'graph_leaf_fields_not_read':len(i['exact_graph_leaf_paths_not_read']),'ledger_leaf_fields_read':len(i['exact_ledger_leaf_paths_read']),'ledger_leaf_fields_not_read':len(i['exact_ledger_leaf_paths_not_read'])})

dump('COMBINED_NODE_COVERAGE.json',dict(common,prior_314_nodes=[{'item_id':i['item_id'],'review_source':'../dvc_review/BASELINE_PER_ID_READ_SCOPE.json','reading_status':i['reading_status'],'scope_expanded_by_this_worker':False} for i in prior_nodes],new_599_nodes=[{'item_id':i['item_id'],'review_source':'PER_ID_NODE_REVIEW.json (also preserved byte-exact as .json.gz)','reading_status':i['status']} for i in items],all_node_ids=sorted(gm),combined_unread_node_ids=[]))
dump('EXACT_REMAINING_NODE_FIELDS.json',{'status':'OPEN_FIELDS_AND_PROOFS_RETAINED','source_graph_sha256':sha(GRAPH),'source_ledger_sha256':sha(LEDGER),'historical_depth_gaps_kept_open':prior['historical_depth_gaps_kept_open'],'note':'The new field counts below are a different explicit leaf-path inventory, including metadata and repeated ledger copies. Do not add them to or subtract them from the inherited 1034-ID/1828-field depth inventory. No inherited deep-proof item is closed here.','items':[{'item_id':i['item_id'],'graph_leaf_paths_not_read':i['exact_graph_leaf_paths_not_read'],'ledger_leaf_paths_not_read':i['exact_ledger_leaf_paths_not_read'],'external_quantifier_locators_unresolved':i['external_quantifier_locator_paths_not_resolved']} for i in items]})
index=read(OUT/'READING_PACK_INDEX.json')
for q in index:q['status']='EXACT_CORE_TEXT_ACTUALLY_READ';q['review_method']='Full displayed statements plus exact shared field values; no program verdict used.'
index[1]['truncation_recovery']='Dictionary V94-V97 explicitly read in the next call.'
index[2]['truncation_recovery']='Dictionary V261-V299 and first20 nodes (TA16:RRH_HISTORY through R149:SELF_APPLICATION) explicitly reread in a separate bounded call.'
index[3]['display_split']='Two complete contiguous parts, newline offset27883.'
index[7]['display_split']='Two complete contiguous parts, newline offset21816.'
dump('READING_PACK_INDEX.json',index)
groups=collections.defaultdict(list)
for i in items:
 f={k:lm[i['item_id']][k] for k in ['source_review','review_outcome','actual_premise_discharged_by_review']};groups[json.dumps(f,ensure_ascii=False,sort_keys=True)].append(i['item_id'])
dump('LEDGER_STATUS_GROUP_READ.json',{'status':'GROUPED_EXACT_VALUES_AND_EVERY_LISTED_ID_READ','items':[{'fields':json.loads(k),'ids':v} for k,v in groups.items()]})
dump('SUMMARY.json',common)
print(json.dumps(counts,indent=2))
