#!/usr/bin/env python3
"""True one-coordinate score-wall pressure near the signed odd-K5 seed.

All coefficients except one are fixed; every generic interval in its
open +/-5% window is visited with an exact rational midpoint represented
by integer doubled weights. Repeated identical signed/capacity graphs
reuse a completed LP audit. This is not full Q10 chamber enumeration.
"""
from pathlib import Path
from itertools import product
from collections import Counter
import gzip,hashlib,json,time,traceback
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from verify_paired_odd_k5_obstruction import BASE
from probe_paired_joint_fractional_packing import solve

def main():
    start=time.monotonic();slices=[];evaluations=[];graphs=[];cache={};counts=Counter();gaps=[];digest=hashlib.sha256()
    def save(status):
        out={'status':status,'base_weights':BASE,'coverage':'All generic intervals in each one-coordinate open +/-5% window, other nine weights fixed; NOT full weight-space coverage.',
             'window_denominator':20,'slices':slices,'evaluations':evaluations,'unique_graph_certificates':graphs,
             'counts':dict(counts),'actual_exactness_gaps':gaps,'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
        raw=(json.dumps(out,indent=2)+'\n').encode();target=Path(__file__).with_name('paired_odd_k5_actual_wall_pressure.json.gz')
        tmp=target.with_suffix('.pending');tmp.write_bytes(gzip.compress(raw,mtime=0));tmp.replace(target)
        return out
    for j in range(10):
        others=[v for h,v in enumerate(BASE) if h!=j];lo=BASE[j]*19//20;hi=BASE[j]*21//20
        criticals=sorted({sum(c*v for c,v in zip(coeff,others)) for coeff in product((-1,0,1),repeat=9)
                          if lo<sum(c*v for c,v in zip(coeff,others))<hi})
        bounds=[lo,*criticals,hi];sl={'coordinate':j,'lo':lo,'hi':hi,'criticals':criticals,'intervals_total':len(bounds)-1,'intervals_completed':0};slices.append(sl)
        for L,R in zip(bounds,bounds[1:]):
            w=[2*v for v in BASE];w[j]=L+R;p=order_and_scores(w);assert p is not None
            g=linear_graph(p[0],10);signature=(g['D'],g['K'],g['edges']);graph_sha=hashlib.sha256(json.dumps(signature).encode()).hexdigest()
            if signature in cache:idx=cache[signature];counts['reused_identical_graph']+=1
            else:
                try:z=solve(w)
                except AssertionError:
                    z={'n':10,'weights':w,'status':'exact_reconstruction_assertion_failure','traceback':traceback.format_exc()}
                z['graph_sha256']=graph_sha;idx=len(graphs);cache[signature]=idx;graphs.append(z);counts[z['status']]+=1
                if z['status']=='exact_rational_optimum' and z['phi_minus_packing'][0]>0:gaps.append(z)
            e={'coordinate':j,'interval':[L,R],'integer_midpoint_weights':w,'graph_certificate_index':idx,'graph_sha256':graph_sha}
            evaluations.append(e);digest.update(json.dumps(e,sort_keys=True).encode());sl['intervals_completed']+=1
            if len(evaluations)%32==0:
                save('RUNNING_EXACT_COORDINATE_WALL_PRESSURE')
                print(json.dumps({'intervals_completed':len(evaluations),'current_coordinate':j,'unique_graphs':len(graphs),'counts':dict(counts),'actual_gaps':len(gaps),'elapsed':time.monotonic()-start}),flush=True)
        save('RUNNING_EXACT_COORDINATE_WALL_PRESSURE')
        print(json.dumps({'coordinate_completed':j,'intervals':sl['intervals_completed'],'total_evaluations':len(evaluations),'unique_graphs':len(graphs),'actual_gaps':len(gaps),'elapsed':time.monotonic()-start}),flush=True)
    out=save('COMPLETED_EXACT_COORDINATE_WALL_PRESSURE')
    print(json.dumps({k:v for k,v in out.items() if k not in ('slices','evaluations','unique_graph_certificates','actual_exactness_gaps')}),flush=True)

if __name__=='__main__':main()
