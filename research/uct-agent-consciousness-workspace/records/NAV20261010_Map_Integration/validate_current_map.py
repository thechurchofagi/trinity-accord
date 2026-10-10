"""Validate pending membership AND current navigation fields against canonical state."""
import json,pathlib,argparse,importlib.util
p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path('.'));a=p.parse_args();root=a.root
def read(n):return json.loads((root/n).read_text())
c=read('UNIFIED_RESEARCH_INDEX.json');s=read('CURRENT_STATE.json');m=read('UCT_FORMAL_GRAPH_MODULES.json');e=read('FORMAL_MAP_EXTENSION_INDEX.json');l=read('RESEARCH_SESSION_LOG_INDEX.json')
loc=root/'integration'/c['version']/'validate_navigation.py';spec=importlib.util.spec_from_file_location('nav_validation',loc);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);result=mod.check(root)
for k in ['latest_research','latest_activity','latest_pending_research']:assert l[k]==s['latest_research']['id'],k
assert l['latest_work_log']==s['latest_research']['work_log'];assert l['latest_handoff']==s['latest_research']['handoff']
assert e['inherited_reviewed_modules']==m['inherited_modules'];assert e['added_reviewed_modules']==[x['research_id'] for x in m['modules']]
assert e['latest_candidate']==next(x['path'] for x in c['pending_checkpoints'] if x['id']==s['latest_research']['id'])
result.update({'current_scientific_pointer_match':True,'completed_module_index_match':True});print(json.dumps(result,ensure_ascii=False,indent=2))
