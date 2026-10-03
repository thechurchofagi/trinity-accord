#!/usr/bin/env python3
"""Exact real insertion slices from newly certified low-DK seed metrics."""
from pathlib import Path
from math import gcd
from functools import reduce
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from probe_paired_weak_dk_budget import exact_witness

def norm(w):
    d=reduce(gcd,w);return tuple(x//d for x in w)

def main():
    start=time.monotonic();parents=[(16,1,6,8,4),(1,6,16,8,4),(1,6,8,16,4)]
    levels=[];digest=hashlib.sha256();total=0
    for n in range(6,9):
        minimum=None;kept={};slices=[]
        for parent in parents:
            p,scores=order_and_scores(parent)
            critical=sorted({0}|{abs(a-b) for a in scores for b in scores if a!=b})
            heights=[a+b for a,b in zip(critical,critical[1:])]+[2*(critical[-1]+1)]
            for bit in range(n):
                best=None
                for H in heights:
                    w=[2*x for x in parent];w.insert(bit,H);w=norm(w)
                    z=order_and_scores(w);assert z is not None
                    g=linear_graph(z[0],n);v=g['D']+g['K'];total+=1
                    digest.update(json.dumps((w,g['D'],g['K'],g['W'])).encode())
                    if best is None or v<best[0]:best=(v,w)
                    if minimum is None or v<minimum:
                        minimum=v;kept={w:None}
                        print(json.dumps({'n':n,'new_DK_min':v,'weights':w,'N_over_16':(1<<n)//16}),flush=True)
                    elif v==minimum and len(kept)<4:kept.setdefault(w,None)
                slices.append({'parent':parent,'inserted_coordinate':bit,'critical_values':critical,
                               'generic_real_intervals':len(heights),'minimum_DK':best[0],'witness':best[1]})
        witnesses=[exact_witness(w) for w in kept]
        levels.append({'n':n,'complete_fixed_metric_slices':slices,'minimum_DK':minimum,'witnesses':witnesses})
        parents=list(kept)
        print(json.dumps({'completed_n':n,'fixed_parents_next':parents,'DK_min':minimum,'total_evaluated':total}),flush=True)
        if minimum==0:break
    out={'levels':levels,'generic_evaluations':total,'seconds':time.monotonic()-start,'evaluated_digest':digest.hexdigest(),
         'scope':'Exact full real insertion parameter for the displayed metrics only. Parent chambers and arbitrary old-coordinate permutations are not covered. Fixed-scan optima in witnesses are exact.'}
    Path(__file__).with_name('paired_weak_dk_extensions.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='levels'}),flush=True)

if __name__=='__main__':main()
