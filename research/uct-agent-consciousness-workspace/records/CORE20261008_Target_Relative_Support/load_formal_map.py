#!/usr/bin/env python3
"""Explicit additive UCT map loader. No network, CI, or repository writes.
Run from research/uct-agent-consciousness-workspace:
 python records/CORE20261008_Target_Relative_Support/load_formal_map.py --root .
Use --slice only for the imported-ID slice; it is NOT a full-base audit.
"""
import argparse, json, hashlib
from pathlib import Path
from copy import deepcopy
from collections import deque

def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def index(rows,name):
    out={}
    for x in rows:
        i=x.get('id')
        if not i or i in out:raise ValueError('Missing/duplicate '+name+': '+str(i))
        out[i]=x
    return out

def load(root,sliced):
    manifest=json.loads((root/'UCT_FORMAL_GRAPH_MODULES.json').read_text())
    modules=[]
    for item in manifest['modules']:
        raw=(root/item['path']).read_bytes()
        if blob_sha(raw)!=item['git_blob_sha']:raise ValueError('Module hash mismatch')
        m=json.loads(raw)
        for i,n in enumerate(m['nodes']):
            row={**m.get('node_defaults',{}),**n}
            row.setdefault('status',m.get('kind_status',{}).get(row['kind'],'UNCLASSIFIED'))
            m['nodes'][i]=row
        m['rules']=[{**m.get('rule_defaults',{}),**r} for r in m['rules']]
        modules.append(m)
    if sliced:
        base={'nodes':[{'id':i} for i in sorted({i for m in modules for i in m['imports']})], 'rules':[], 'revision':'ANCHOR_SLICE_ONLY'}
    else:
        raw=(root/manifest['base']['path']).read_bytes()
        if blob_sha(raw)!=manifest['base']['git_blob_sha']:
            raise ValueError('Base changed: reconcile manifest and re-audit; never overwrite newer base')
        base=json.loads(raw)
    graph=deepcopy(base)
    nodes=index(graph['nodes'],'base node'); rules=index(graph['rules'],'base rule')
    old_nodes=set(nodes); old_rules=set(rules); fresh=set(); imports=set(); contexts=[]
    for m in modules:
        if set(m['imports'])-set(nodes):raise ValueError('Missing imported ID')
        imports.update(m['imports'])
        for n in m['nodes']:
            if n['id'] in nodes:raise ValueError('Node overwrite prohibited')
            if not all(n.get(k) for k in ('id','kind','statement','status','source','scope')):raise ValueError('Incomplete node')
            nodes[n['id']]=n;fresh.add(n['id']);graph['nodes'].append(n)
        for r in m['rules']:
            if r['id'] in rules:raise ValueError('Rule overwrite prohibited')
            if not isinstance(r.get('all_of'),list) or not r.get('proof_sketch'):raise ValueError('Incomplete rule')
            if len(r['all_of'])!=len(set(r['all_of'])):raise ValueError('Repeated premise')
            if r['conclusion'] in old_nodes:raise ValueError('New rule cannot derive an old node in this conservative layer')
            rules[r['id']]=r;graph['rules'].append(r)
        contexts.extend(m.get('context_links',[]))
    adj={i:set() for i in nodes};degree={i:0 for i in nodes}
    for r in rules.values():
        if (set(r['all_of'])|{r['conclusion']})-set(nodes):raise ValueError('Dangling rule')
        for a in r['all_of']:
            b=r['conclusion']
            if b not in adj[a]:adj[a].add(b);degree[b]+=1
    todo=deque(i for i in nodes if not degree[i]); order=[]
    while todo:
        i=todo.popleft();order.append(i)
        for j in adj[i]:
            degree[j]-=1
            if not degree[j]:todo.append(j)
    if len(order)!=len(nodes):raise ValueError('Premise dependency cycle')
    index(contexts,'context')
    for c in contexts:
        if c['from'] not in nodes or c['to'] not in nodes:raise ValueError('Dangling context')
    target='CORE20261008:EXPERIENTIAL_APPLICATION'
    nr=[r for m in modules for r in m['rules']]
    known={i for i in fresh if not nodes[i]['status'].startswith('OPEN')}|imports
    known.discard(target)
    def close(supplied):
        k=set(supplied)
        while True:
            out=k|{r['conclusion'] for r in nr if set(r['all_of'])<=k}
            if out==k:return k
            k=out
    assert target not in close(known)
    assert target in close(known|{'CORE20261008:ACTUAL_BRIDGE'})
    assert not any(r['conclusion']=='CORE20261008:HUMAN_CORE' for r in nr)
    graph['effective_module_context_links']=contexts
    graph['effective_modules']=[m['module_id'] for m in modules]
    graph['revision']=str(base.get('revision'))+'+CORE20261008'
    audit={'status':'AUDIT_INCOMPLETE','structural_checks':'PASS_FOR_LOADED_OBJECTS','full_base_loaded':not sliced,'full_semantic_audit':False,'loaded_nodes':len(nodes),'loaded_rules':len(rules),'new_nodes':len(fresh),'new_rules':len(set(rules)-old_rules),'new_context_ids':[c['id'] for c in contexts],'actual_bridge_gate':'PASS_WITHOUT_HUMAN_INSTANTIATION','node_coverage':[{'id':i,'structural':'CHECKED','semantic':'SCOPED_NEW_ARGUMENT' if i in fresh else 'IMPORTED_CONTRACT_ONLY' if i in imports else 'NOT_REVIEWED_THIS_ROUND'} for i in sorted(nodes)],'rule_coverage':[{'id':i,'structural':'CHECKED','semantic':'SCOPED_NEW_ARGUMENT' if i not in old_rules else 'NOT_REVIEWED_THIS_ROUND'} for i in sorted(rules)],'unreviewed':'All unlisted base semantics and historical contextual relations; in slice mode all base items beyond imported anchors.'}
    return graph,audit

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--slice',action='store_true');p.add_argument('--out',type=Path,default=Path('CORE_MAP_AUDIT.json'));a=p.parse_args()
    graph,audit=load(a.root,a.slice)
    a.out.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    if not a.slice:a.out.with_name('UCT_EFFECTIVE_FORMAL_GRAPH.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if not isinstance(v,list)},ensure_ascii=False,indent=2))
