"""Scoped navigation and admission validation; not a proof of H or C1."""
import json,pathlib,hashlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[2]
ID='A3W20261010'
def read(f):return json.loads((root/f).read_text())
cat=read('UNIFIED_RESEARCH_INDEX.json'); canonical=cat['latest_followup_application']
assert canonical['id']==ID and canonical['enabled_as_established_premises'] is False
for f in ['CURRENT_STATE.json','UCT_FORMAL_GRAPH_MODULES.json','RESEARCH_REGISTRY.json','FORMAL_MAP_EXTENSION_INDEX.json','RESEARCH_SESSION_LOG_INDEX.json']:
 a=read(f);assert a['latest_followup_application']==canonical
 ids=[x['id'] for x in a['followup_applications']];assert len(ids)==len(set(ids)) and 'FAM20261010' in ids and ID in ids
state=read('CURRENT_STATE.json');assert state['release_id']=='UCT-MAP-v1.1.2' and state['counts']['nodes']==913 and state['counts']['active_conditional_rules']==424
assert cat['pending_count']==38 and cat['publication_coverage']==read('PUBLICATION_COVERAGE.json')['coverage_version']=='UCT-PUB-v1.0.33'
app=read(canonical['map_extension']);assert app['enabled'] is False and not any(app[x] for x in ['nodes','rules','context_links'])
assert all(x['actual_premises_discharged'] is False for x in app['applications'])
print(json.dumps({'status':'PASS_SCOPED_NAVIGATION_AND_ADMISSION','followup_ids':[x['id'] for x in cat['followup_applications']],'completed_map_unchanged':True,'pending_count':38,'publication_coverage':'UCT-PUB-v1.0.33','new_nodes':0,'new_rules':0,'new_contexts':0,'actual_h_validation':False,'full_semantic_reproof':False},indent=2))
