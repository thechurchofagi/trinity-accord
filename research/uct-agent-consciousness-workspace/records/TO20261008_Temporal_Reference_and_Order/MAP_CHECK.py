"""Usage: python MAP_CHECK.py /path/to/parent_UCT_FORMAL_GRAPH.json.

Obtain the parent graph with git show at the MAP_EXTENSION.json base_commit.
This checks integration, not theorem validity or global semantic consistency.
"""
from pathlib import Path
import hashlib,json,sys

rec=Path(__file__).resolve().parent
root=rec.parents[1]
base=json.loads(Path(sys.argv[1]).read_text())
graph=json.loads((root/'UCT_FORMAL_GRAPH.json').read_text())
ext=json.loads((rec/'MAP_EXTENSION.json').read_text())
checks=[]
def check(name,ok):
    assert ok,name
    checks.append({'name':name,'pass':True})
for key in ['nodes','rules','context_links']:
    check('exact_parent_'+key,graph[key][:len(base[key])]==base[key])
    check('exact_extension_'+key,graph[key][len(base[key]):]==ext[key])
ids=[n['id'] for n in graph['nodes']]
check('unique_node_and_rule_ids',len(set(ids))==len(ids) and len({r['id'] for r in graph['rules']})==len(graph['rules']))
check('new_references_resolve',all(all(x in ids for x in r['all_of']) and r['conclusion'] in ids for r in ext['rules']) and all(c['from'] in ids and c['to'] in ids for c in ext['context_links']))
check('source_hashes_match',all(hashlib.sha256((root/n['formal_contract_TO20261008']['source_anchor']['path']).read_bytes()).hexdigest()==n['formal_contract_TO20261008']['source_anchor']['sha256'] for n in ext['nodes']))
check('semantic_bridge_has_no_deductive_incoming_rule',not any(r['conclusion']=='TO20261008:ORDER_BRIDGE_CANDIDATE' for r in graph['rules']))
check('actual_package_not_inferred_from_abstract_model',not any(r['conclusion']=='TO20261008:ACTUAL_TEMPORAL_INSTANCE' for r in ext['rules']))
check('C1_rule_retains_actuality',any(r['all_of']==['A:C1','TO20261008:ACTUAL_TEMPORAL_INSTANCE'] and r['conclusion']=='TO20261008:EXPERIENTIAL_STRUCTURAL_COUNTERPART' for r in ext['rules']))
result={'status':'SCOPED_INTEGRATION_CHECK_ONLY','base_commit':ext['base_commit'],'parent_graph_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'graph_sha256':hashlib.sha256((root/'UCT_FORMAL_GRAPH.json').read_bytes()).hexdigest(),'counts':{k:len(graph[k]) for k in ['nodes','rules','context_links']},'checks':checks,'not_established':['Global semantic consistency','Actual token grounding','C1 or B_order empirical truth','Independent review closure']}
(rec/'MAP_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks_passed':len(checks),'counts':result['counts']}))
