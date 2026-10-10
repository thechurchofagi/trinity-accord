"""Validate current UCT navigation. No scientific theorem or empirical proof is claimed."""
import argparse,json,gzip,hashlib,pathlib,collections,sys
def digest(b):return hashlib.sha256(b).hexdigest()
def check(root):
 def read(n):return json.loads((root/n).read_text())
 cat=read('UNIFIED_RESEARCH_INDEX.json');ids=[e['id'] for e in cat['pending_checkpoints']];expected=set(ids)
 assert len(ids)==len(expected),'Duplicate checkpoint identities'
 state=read('CURRENT_STATE.json');mods=read('UCT_FORMAL_GRAPH_MODULES.json');reg=read('RESEARCH_REGISTRY.json');ext=read('FORMAL_MAP_EXTENSION_INDEX.json');log=read('RESEARCH_SESSION_LOG_INDEX.json')
 for name,items in [('state',state['pending_checkpoints_not_promoted']),('modules',[r['id'] for r in mods['pending_checkpoints']]),('registry',[r.get('id',r.get('research_id')) for r in reg['pending_checkpoints']]),('extensions',ext['pending_disabled']),('sessions',log['pending_checkpoints'])]:
  assert len(items)==len(set(items)) and set(items)==expected,(name,'identity drift',expected-set(items),set(items)-expected)
 familyids=[i for g in cat['families'] for i in g['checkpoint_ids']];assert len(familyids)==len(expected) and set(familyids)==expected
 for e in cat['pending_checkpoints']:
  assert e['enabled_as_established_premises'] is False
  assert digest((root/e['path']).read_bytes())==e['source_sha256'],('source changed',e['id'])
 v=root/'integration'/cat['version'];u=json.loads(gzip.decompress((v/'UNIFIED_MAP.json.gz').read_bytes()));g=u['completed_graph']
 assert g['version']==state['release_id']==cat['completed_map']
 assert u['completed_graph_sha256']==state['complete_map_sha256']==mods['effective_graph_sha256']
 assert len(g['nodes'])==state['counts']['nodes'] and len(g['rules'])==state['counts']['active_conditional_rules']
 nodes={n['id'] for n in g['nodes']};assert len(nodes)==len(g['nodes'])
 for r in g['rules']:assert all(x in nodes for x in r['all_of']) and r['conclusion'] in nodes
 assert len({o['key'] for o in u['pending_objects']})==len(u['pending_objects'])
 assert all(o['enabled_as_established_premises'] is False for o in u['pending_objects'])
 bad=[e for e in u['pending_navigation_edges'] if e['resolution'] in ['UNRESOLVED_DEDUCTIVE_REFERENCE','AMBIGUOUS_PENDING']]
 assert not bad,bad
 assert all(f['completed_anchor'] in nodes for f in cat['families'])
 assert cat['publication_coverage']==read('PUBLICATION_COVERAGE.json')['coverage_version']
 result={'status':'PASS_NAVIGATION_AND_DISABLED_ASSEMBLY','version':cat['version'],'pending_checkpoints':len(ids),'families':len(cat['families']),'completed_nodes':len(nodes),'completed_rules':len(g['rules']),'pending_objects':dict(collections.Counter(o['kind'] for o in u['pending_objects'])),'unresolved_deductive_references':len(bad),'declared_external_context_refs':sum(e['resolution']=='DECLARED_CONTEXT_SOURCE_NOT_NODE' for e in u['pending_navigation_edges']),'scientific_promotion':False,'full_semantic_reproof':False}
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=pathlib.Path('.'));a=ap.parse_args()
 try:print(json.dumps(check(a.root),ensure_ascii=False,indent=2))
 except Exception as e:print('VALIDATION_FAILED:',repr(e),file=sys.stderr);raise
