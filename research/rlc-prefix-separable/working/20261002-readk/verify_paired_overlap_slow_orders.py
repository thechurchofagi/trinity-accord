#!/usr/bin/env python3
"""Audit a conditional all-dimensional overlap theorem with genuine signed slow orders."""
from pathlib import Path
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores,counts
from verify_paired_sibling_ranks import linear_graph,rank
from paired_sibling_ancestor_optimizer import optimize
from paired_periodic_overlap import explicit_order,normal_graph,packing_certificate,attaining_mask


def main():
    rng=random.Random(202610031155);start=time.monotonic();digest=hashlib.sha256();samples=[];total=0
    scale=1000
    for ell in range(1,9):
        n=ell+5;N=1<<n;T=1<<ell;example=None
        for i in range(12):
            perm=list(range(ell));rng.shuffle(perm)
            tail=[(1 if rng.randrange(2) else -1)*56000*(1<<perm[j])+rng.randrange(-max(1,250//ell),max(2,250//ell)) for j in range(ell)]
            slow=[sum(tail[j] for j in range(ell) if t>>j&1) for t in range(T)]
            rows=sorted(range(T),key=slow.__getitem__);gaps=[slow[y]-slow[x] for x,y in zip(rows,rows[1:])]
            assert min(gaps)>55000 and max(gaps)<61000
            w=(1000,10000,28000,16000)+tuple(tail)+(8000,)
            actual=order_and_scores(w);assert actual is not None
            p=explicit_order(n,rows);assert actual[0]==p
            graph=normal_graph(n,rows);assert linear_graph(p,n)==graph
            packing=packing_certificate(graph,n,tail_order=rows)
            mask,E,field=attaining_mask(graph,n);assert E==N//2-2
            phi=(graph['W']-E)//2;assert phi==packing['value']==N//4-2
            R,C,_=counts([rank(x,n,mask) for x in p]);assert (R,C)==(N//4+1,N//4+2)
            if n<=11:assert optimize(graph,n)['E_max']==E
            row={'n':n,'weights':w,'slow_gap_min':min(gaps),'slow_gap_max':max(gaps),'D':0,'K':2,
                 'W':N-6,'phi':phi,'R_min':R,'C_at_witness':C,
                 'slow_order_sha256':hashlib.sha256(json.dumps(rows).encode()).hexdigest(),
                 'graph_sha256':hashlib.sha256(json.dumps(graph,sort_keys=True).encode()).hexdigest()}
            digest.update(json.dumps(row,sort_keys=True).encode());total+=1
            if example is None:example=row
        samples.append({'n':n,'genuine_signed_or_permuted_perturbed_orders':12,'representative':example})
        print(json.dumps({'n':n,'checked':12,'R_min':N//4+1}),flush=True)
    receipt={'seed':202610031155,'checked':total,'summaries':samples,'audit_digest':digest.hexdigest(),
             'seconds':time.monotonic()-start,'scope':'General theorem assumes consecutive slow-score gaps in (55,61) after scaling. Listed fresh signed/perturbed sweeps are implementation audits, not chamber coverage.'}
    Path(__file__).with_name('paired_overlap_slow_orders_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='summaries'}),flush=True)

if __name__=='__main__':main()
