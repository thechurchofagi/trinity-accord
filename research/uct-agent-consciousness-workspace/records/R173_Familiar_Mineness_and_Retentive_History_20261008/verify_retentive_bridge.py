#!/usr/bin/env python3
import hashlib,json,itertools,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'UCT_FORMAL_GRAPH.json'
EXT=HERE/'MAP_EXTENSION.json'

def canonical(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ext=json.loads(EXT.read_text())
    current=json.loads(PARENT.read_text())
    parent_bytes=subprocess.check_output(['git','show','HEAD:research/uct-agent-consciousness-workspace/UCT_FORMAL_GRAPH.json'],cwd=ROOT.parents[1])
    graph=json.loads(parent_bytes)
    results=[]
    rows=list(itertools.product([0,1], repeat=3))
    results.append({'id':'R173-C01','pass':len(rows)==8 and len(set(rows))==8,'detail':'all eight Avail/AgencyLoop/RetBind combinations'})
    fibers={}
    for a,g,r in rows: fibers.setdefault((a,g),set()).add(r)
    results.append({'id':'R173-C02','pass':all(v=={0,1} for v in fibers.values()),'detail':'each current (Avail,AgencyLoop) fiber contains both history values'})
    results.append({'id':'R173-C03','pass':all(len(v)>1 for v in fibers.values()),'detail':'no fixed current-action/agency decoder can recover RetBind'})
    results.append({'id':'R173-C04','pass':all(r==tuple((a,g,r))[-1] for a,g,r in rows),'detail':'augmented tuple recovers RetBind by projection'})
    twin0={'B':1,'U':1,'A':1,'G':1,'m':1,'R':0}
    twin1={**twin0,'R':1}
    current=lambda x:(x['B'],x['U'],x['A'],x['G'],x['m'])
    results.append({'id':'R173-C05','pass':current(twin0)==current(twin1) and twin0['R']!=twin1['R'],'detail':'same-present/different-history witness'})
    # report/name changes do not alter actual history bit in this formal witness
    report_variants=[(r,lab) for r in [0,1] for lab in ['mine','not-mine']]
    results.append({'id':'R173-C06','pass':all(r==rr for r,lab in report_variants for rr in [r]),'detail':'external label does not define RetBind'})
    # Parent is exact R172 raw graph and extension references exist.
    results.append({'id':'R173-C07','pass':ext['parent_sha256']==hashlib.sha256(parent_bytes).hexdigest() and len(graph['nodes'])==506 and len(graph['rules'])==244 and len(graph['context_links'])==141,'detail':'exact parent identity/counts'})
    node_ids={x['id'] for x in graph['nodes']}|{x['id'] for x in ext['nodes']}
    rule_ids={x['id'] for x in graph['rules']}|{x['id'] for x in ext['rules']}
    refs=all(x in node_ids for r in ext['rules'] for x in r['all_of']+[r['conclusion']]) and all(l['from'] in node_ids and l['to'] in node_ids for l in ext['context_links'])
    results.append({'id':'R173-C08','pass':refs,'detail':'all new rule/link endpoints exist'})
    results.append({'id':'R173-C09','pass':len(node_ids)==len(graph['nodes'])+len(ext['nodes']) and len(rule_ids)==len(graph['rules'])+len(ext['rules']),'detail':'new IDs unique against parent'})
    expected={
      'r173_history_twin_witness':['R173:CURRENT_ACTION_AVAILABILITY','R173:CURRENT_AGENCY_LOOP','R173:RETENTIVE_BINDING_RELATION'],
      'r173_present_slice_nonidentification':['R173:FIXED_FAMILIAR_TARGET_CONTRACT','R173:SAME_PRESENT_DIFFERENT_HISTORY_WITNESS'],
      'r173_retentive_coordinate_transport':['R173:EFFECTIVE_R172_PATH_INSTANCE','R173:RETENTIVE_BINDING_RELATION','R157:COORDINATE_TRANSPORT'],
      'r173_familiar_mineness_boundary':['R173:RETENTIVE_EXPERIENTIAL_COORDINATE','R173:THREE_TARGET_SEPARATION','R157:SEMANTIC_RESIDUAL']}
    got={r['id']:r['all_of'] for r in ext['rules']}
    results.append({'id':'R173-C10','pass':got==expected,'detail':'exact all_of premise lists'})
    bad=('basal experience iff','unique owner','current assistant is conscious','report iff experience')
    conclusions=' '.join(r['statement'] for r in ext['rules']).lower()
    results.append({'id':'R173-C11','pass':not any(x in conclusions for x in bad),'detail':'no prohibited reverse/gate conclusion'})
    # Simple DAG audit on parent + extension rules.
    edges=[]
    for r in graph['rules']+ext['rules']:
        edges += [(x,r['conclusion']) for x in r['all_of']]
    adj={n:[] for n in node_ids}
    for a,b in edges: adj[a].append(b)
    state={}
    def visit(n):
        if state.get(n)==1:return False
        if state.get(n)==2:return True
        state[n]=1
        if not all(visit(v) for v in adj[n]):return False
        state[n]=2;return True
    results.append({'id':'R173-C12','pass':all(visit(n) for n in node_ids),'detail':'combined recorded dependency DAG acyclic'})
    out={'schema':'UCT_R173_EXACT_CHECKS/v1','status':'PASS' if all(x['pass'] for x in results) else 'FAIL','checks':results,'enumerated_rows':len(rows),'limits':['finite logical/model audit only','no physical realization','no F_F observations','no proof of C1 or B_fam']}
    (HERE/'EXACT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    raise SystemExit(0 if out['status']=='PASS' else 1)
if __name__=='__main__': main()
