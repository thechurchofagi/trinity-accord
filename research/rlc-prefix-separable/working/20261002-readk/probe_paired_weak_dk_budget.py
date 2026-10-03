#!/usr/bin/env python3
"""Exact new-coordinate slices and fresh weak-budget counterexample pressure.

No absence-to-proof inference. Slices cover all generic real new weights
only at their fixed parent metrics, never a whole parent chamber.
"""
from pathlib import Path
import gzip,hashlib,json,random,time
from verify_gray_reflection_graph import positive_chambers,order_and_scores
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_sibling_ancestor_optimizer import optimize

def exact_witness(w):
    n=len(w);p=order_and_scores(w)[0];g=linear_graph(p,n);z=optimize(g,n)
    R=fast_runs([rank(x,n,z['mask']) for x in range(1<<n)],p)
    assert R==((1<<n)+g['D']-z['E_max'])//2
    return {'weights':w,'n':n,**g,'optimum':z,'R_min':R,'order':p}

def main():
    start=time.monotonic();rng=random.Random(202610031124);digest=hashlib.sha256();slices=[];minima={};counters=[];total=0;rejected=0
    def evaluate(w,tag):
        nonlocal total,rejected
        result=order_and_scores(w)
        if result is None:rejected+=1;return None
        n=len(w);g=linear_graph(result[0],n);value=g['D']+g['K'];total+=1
        digest.update(json.dumps((w,g['D'],g['K'],g['W'],tag),sort_keys=True).encode())
        if n not in minima or value<minima[n]['D']+minima[n]['K']:
            minima[n]=exact_witness(w);minima[n]['tag']=tag
            print(json.dumps({'new_min_n':n,'D_plus_K':value,'N_over_8':(1<<n)//8,'weights':w,'R_min':minima[n]['R_min'],'tag':tag}),flush=True)
        if 8*value<(1<<n):counters.append({'weights':w,'D':g['D'],'K':g['K'],'tag':tag})
        return value
    for parent in positive_chambers(4):
        p,scores=order_and_scores(parent);critical=sorted({0}|{abs(a-b) for a in scores for b in scores if a!=b})
        heights=[a+b for a,b in zip(critical,critical[1:])]+[2*(critical[-1]+1)]
        for bit in range(5):
            best=None
            for H in heights:
                w=[2*z for z in parent];w.insert(bit,H)
                v=evaluate(w,['exact_real_new_weight_slice',parent,bit,H])
                assert v is not None
                if best is None or v<best['D_plus_K']:best={'D_plus_K':v,'integer_weights':w,'scaled_new_weight':H}
            slices.append({'parent':parent,'inserted_coordinate':bit,'twice_real_critical_values':[2*x for x in critical],
                           'generic_intervals':len(heights),'minimum':best})
    print(json.dumps({'completed_exact_slices':len(slices),'evaluated_so_far':total,'counterexamples_so_far':len(counters)}),flush=True)
    for n,budget in ((6,1200),(7,1200),(8,1200),(9,1000),(10,800),(11,500),(12,300)):
        w=[1,6,8,4]
        while len(w)<n:w.append(sum(w)+1)
        current=list(w);value=evaluate(current,['sharp_seed',n]);best=current[:]
        for trial in range(budget):
            if trial%5==0:
                proposal=rng.sample(range(1,1000001),n)
            else:
                proposal=current[:];j=rng.randrange(n)
                scale=max(2,max(proposal)//(1+trial%7))
                proposal[j]=max(1,proposal[j]+rng.randint(-scale,scale))
            v=evaluate(proposal,['random_or_local',n,trial])
            if v is None:continue
            if v<value or (v==value and rng.random()<0.25):current=proposal;value=v
            if trial%99==98:current=list(minima[n]['weights']);value=minima[n]['D']+minima[n]['K']
        print(json.dumps({'completed_dimension':n,'best_D_plus_K':minima[n]['D']+minima[n]['K'],'counterexamples_total':len(counters)}),flush=True)
    out={'seed':202610031124,'total_generic_evaluations':total,'nongeneric_rejections':rejected,
         'exact_fixed_parent_slices':slices,'dimension_minimum_witnesses':minima,
         'counterexamples_to_DK_N_over_8':counters,'evaluated_digest':digest.hexdigest(),
         'seconds':time.monotonic()-start,
         'scope':'Complete generic real insertion parameter only for the listed fixed four-dimensional integer parent vectors and each insertion position. Fresh higher-dimensional samples/local moves do not cover chambers. All claimed fixed-scan rank optima are exact.'}
    encoded=(json.dumps(out,indent=2)+'\n').encode()
    Path(__file__).with_name('paired_weak_dk_pressure.json').write_bytes(encoded)
    Path(__file__).with_name('paired_weak_dk_pressure.json.gz').write_bytes(gzip.compress(encoded,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ('exact_fixed_parent_slices','dimension_minimum_witnesses','counterexamples_to_DK_N_over_8')}),flush=True)

if __name__=='__main__':main()
