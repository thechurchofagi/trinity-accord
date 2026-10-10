import json,pathlib
P=pathlib.Path(__file__).parent;O=P/'output';S=P/'source';R='records/NAV20261010_Map_Integration'
def read(n):return json.loads((O/n).read_text())
def put(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=read('CURRENT_STATE.json');m=read('UCT_FORMAL_GRAPH_MODULES.json');e=read('FORMAL_MAP_EXTENSION_INDEX.json');l=read('RESEARCH_SESSION_LOG_INDEX.json');latest=s['latest_research']
e['previous_module_navigation_before_NAV20261010']={'inherited_reviewed_modules':e['inherited_reviewed_modules'],'added_reviewed_modules':e['added_reviewed_modules'],'navigation_reconciliation':e['navigation_reconciliation']}
e['inherited_reviewed_modules']=m['inherited_modules'];e['added_reviewed_modules']=[x['research_id'] for x in m['modules']]
e['navigation_reconciliation']={'source':'UNIFIED_RESEARCH_INDEX.json; UCT_FORMAL_GRAPH_MODULES.json','record':R+'/CURRENT_POINTER_RECONCILIATION.json','scope':'Pending identity sets AND current scientific pointers AND completed module names reconciled; no scientific promotion.'}
fields=['latest_research','latest_activity','latest_pending_research','latest_work_log','latest_handoff','latest_persistence_receipt']
l['previous_scientific_navigation_before_NAV20261010']={k:l.get(k) for k in fields}
for k in ['latest_research','latest_activity','latest_pending_research']:l[k]=latest['id']
l['latest_work_log']=latest['work_log'];l['latest_handoff']=latest['handoff'];l['latest_persistence_receipt']=latest['source'].rsplit('/',1)[0]+'/PERSISTENCE_RECEIPT.json';l['latest_navigation_persistence_receipt']=R+'/PERSISTENCE_RECEIPT.json'
s['latest_navigation_activity']['persistence_receipt']=R+'/PERSISTENCE_RECEIPT.json'
put('FORMAL_MAP_EXTENSION_INDEX.json',e);put('RESEARCH_SESSION_LOG_INDEX.json',l);put('CURRENT_STATE.json',s)
put(R+'/CURRENT_POINTER_RECONCILIATION.json',{'reason':'Final cross-field validation found stale latest-scientific A3O pointers and old inherited-module lists despite matching pending identity sets. Reconciled to canonical A3V and completed module descriptor.','latest_scientific':latest['id'],'old_session_pointers':l['previous_scientific_navigation_before_NAV20261010'],'old_extension_module_lists':e['previous_module_navigation_before_NAV20261010'],'canonical_identity_and_scientific_graph_unchanged':True})
for n in ['START_HERE.md','AGENTS.md']:
 p=O/n;t=p.read_text().replace('integration/UCT-INTEGRATION-v1.0.0/validate_navigation.py','records/NAV20261010_Map_Integration/validate_current_map.py');p.write_text(t)
print('Current pointers synchronized to',latest['id'])
