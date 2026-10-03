#!/usr/bin/env python3
"""Complete finite class: cardinality first, all binary priority permutations."""
from pathlib import Path
from collections import Counter
import itertools
import hashlib
import json
import time
from verify_face_local_obstruction import subset_scores
from verify_gray_reflection_graph import graph, gray, counts, inverse_gray
from probe_arbitrary_coherent_secondary import exact_gray_spin_optimizer

def main():
    start=time.monotonic();digest=hashlib.sha256();records=[]
    for n in range(2,9):
        N=1<<n;hist=Counter();whist=Counter();best=None;count=0;sign_vectors=0
        for perm in itertools.permutations(range(n)):
            b=tuple(1<<j for j in perm);beta=subset_scores(b)
            p=tuple(sorted(range(N),key=lambda x:(x.bit_count(),beta[x])))
            g=graph(p,n);E,mask=exact_gray_spin_optimizer(g,n)
            net=E-g['D'];hist[net]+=1;whist[g['W']-g['D']]+=1;count+=1
            sign_vectors+=1<<max(0,n-2)
            digest.update(json.dumps((n,perm,g['D'],g['edges'],E,mask)).encode())
            if best is None or net>best['net_E_minus_D']:
                B=N;weights=tuple(B+s for s in b);z=inverse_gray(mask)
                signed=tuple(-v if z>>j&1 else v for j,v in enumerate(weights))
                actual_scores=subset_scores(signed)
                actual=tuple(sorted(range(N),key=actual_scores.__getitem__))
                assert actual==tuple(x^z for x in p)
                R,C,_=counts(tuple(map(gray,actual)))
                assert C==(N+g['D']-E)//2
                best={'secondary':b,'signed_weights':signed,'D':g['D'],'W':g['W'],
                      'edges':g['edges'],'E':E,'net_E_minus_D':net,'R':R,'C':C,'reflection':z}
        assert count==__import__('math').factorial(n)
        record={'n':n,'priority_permutations':count,'sign_vectors_exactly_optimized':sign_vectors,
                'net_energy_histogram':dict(sorted(hist.items())),
                'independent_edge_excess_histogram':dict(sorted(whist.items())),
                'worst_case':best,'minimum_C':(N-best['net_E_minus_D'])//2}
        records.append(record)
        print(json.dumps({'n':n,'permutations':count,'maximum_net_energy':best['net_E_minus_D'],
              'minimum_C':record['minimum_C'],'elapsed':round(time.monotonic()-start,3)}),flush=True)
    out={'state':'COMPLETE_FINITE_BINARY_PRIORITY_SUBCLASS_NOT_ALL_SECONDARIES',
         'dimensions':list(range(2,9)),'records':records,
         'verification_digest':digest.hexdigest(),'violations':0,
         'elapsed_seconds':round(time.monotonic()-start,3),
         'scope':'Every positive binary secondary priority permutation and every optimizing input reflection; no coverage of arbitrary real secondary vectors and no all-dimensional theorem.'}
    Path(__file__).with_name('cardinality_binary_priority_verification.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','verification_digest','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
