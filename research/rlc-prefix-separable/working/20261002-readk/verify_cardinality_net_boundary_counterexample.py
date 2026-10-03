#!/usr/bin/env python3
"""Exact finite counterexample to E_*<=D for coherent cardinality refinements."""
import json,hashlib
from pathlib import Path
from verify_prefix_transport_defect import check,scores
from verify_cardinality_prefix_flux import interior
from verify_gray_reflection_graph import graph,optimize,order_and_scores,counts,gray

def main():
    b=(75,74,7,14,20,60);w=tuple(251+v for v in b)
    p=order_and_scores(w)[0];s=scores((1,)*6);u=scores(b)
    assert len(set(zip(s,u)))==64
    assert p==tuple(sorted(range(64),key=lambda x:(s[x],u[x])))
    g=graph(p,6);E,phi=optimize(g,6)
    assert (g['D'],g['W'],E,phi)==(2,6,6,0)
    assert g['edges']==((1,3,-2),(2,3,2),(3,4,2))
    assert interior(p,s,g)=={}
    transport=check((1,)*6,b,True)
    assert sum(transport['orphans'])==0
    records=[]
    for z in range(64):
        v=tuple(-x if z>>j&1 else x for j,x in enumerate(w))
        pp=order_and_scores(v)[0];R,C,_=counts(tuple(map(gray,pp)))
        records.append({'z':z,'R':R,'C':C})
    assert min(r['R'] for r in records)==min(r['C'] for r in records)==30
    assert records[2]=={'z':2,'R':30,'C':30}
    receipt={'status':'PASS','primary':[1]*6,'secondary':b,'positive_weights':w,
             'witness_signed_weights':[326,-325,258,265,271,311],
             'witness_reflection':2,'witness_R_and_C':30,'q':7,'D':2,'W':6,'E':6,
             'edges':g['edges'],'interior_edges':[],'orphan_count':0,
             'discovery_seed':202610030835,'discovery_trial_index':1023,
             'discovery_domain':'At most 5000 draws of six distinct integers from 1..100; retain first joint-generic C<32.',
             'scope':'Refutes zero-boundary-loss E_*<=D; does not refute E_*<=D+O(n) or the main target.',
             'all_sign_records':records,'violations':0}
    receipt['deterministic_sha256']=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('cardinality_net_boundary_counterexample.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:value for key,value in receipt.items() if key!='all_sign_records'},indent=2))
if __name__=='__main__':main()
