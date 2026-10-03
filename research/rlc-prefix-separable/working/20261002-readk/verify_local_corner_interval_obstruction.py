#!/usr/bin/env python3
"""Exact all-n dual defeats the local-corner translation packing shortcut.

All four triples of each two-free-coordinate face, all nonadjacent h,k and
every base face are covered. Within-layer exchange witnesses are NOT excluded.
"""
from pathlib import Path
from itertools import combinations
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs

def main():
    start=time.monotonic();rows=[];digest=hashlib.sha256()
    for n in range(3,15):
        N=1<<n;B=N;w=tuple(B+(1<<j) for j in range(n));p,s=order_and_scores(w)
        assert p==tuple(sorted(range(N),key=lambda x:(x.bit_count(),x)))
        pos=[0]*N
        for i,x in enumerate(p):pos[x]=i
        first={r:next(i for i,x in enumerate(p) if x.bit_count()==r) for r in range(1,n)}
        last={r:max(i for i,x in enumerate(p) if x.bit_count()==r) for r in range(1,n)}
        dual=sorted(set(first.values())|set(last.values()))
        assert len(dual)==2*(n-1) and all(1<=i<=N-2 for i in dual)
        counts=0;coverage_by_layer=[0]*(n-1)
        for h in range(n-2):
            for k in range(h+2,n):
                free=(1<<h)|(1<<(h+1))|(1<<k)
                for a in range(N):
                    if a&free:continue
                    corners=(a,a|(1<<h),a|(1<<k),a|(1<<h)|(1<<k))
                    for triple in combinations(corners,3):
                        mirror=tuple(x|(1<<(h+1)) for x in triple)
                        ix=tuple(pos[x] for x in triple);iy=tuple(pos[x] for x in mirror)
                        assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
                        r=a.bit_count();cuts=first if triple[0]==a else last
                        c1,c2=cuts[r+1],cuts[r+2]
                        assert ix[0]<c1<ix[2] and iy[0]<c2<iy[2]
                        # Dual1/2 at first AND last of each intermediate layer.
                        twice_load=sum(ix[0]<t<ix[2] or iy[0]<t<iy[2] for t in dual)
                        assert twice_load>=2
                        coverage_by_layer[r]+=1;coverage_by_layer[r+1]+=1;counts+=1
                        if n<=6:
                            values=[rank(x,n,0) for x in triple+mirror]
                            products=[(z[1]-z[0])*(z[2]-z[1]) for z in (values[:3],values[3:])]
                            assert (products[0]>0)!=(products[1]>0)
                        digest.update(json.dumps((n,h,k,a,ix,iy,r,twice_load)).encode())
        assert counts==4*((n-1)*(n-2)//2)*(1<<(n-3))
        gray=[x^(x>>1) for x in range(N)]
        rows.append({'n':n,'actual_positive_generic_weights':w,'all_local_corner_witnesses':counts,
                     'dual_turn_positions':dual,'each_dual_mass':[1,2],
                     'exact_fractional_packing_upper_bound':[n-1,1],
                     'layer_coverage_counts':coverage_by_layer,'actual_Gray_runs':fast_runs(gray,p),
                     'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()})
    out={'status':'VERIFIED_ALL_DIMENSION_LOCAL_CORNER_TRANSLATION_PACKING_OBSTRUCTION',
         'analytic_statement':'For every n>=3, actual cardinality-then-numeric weights w_j=2^n+2^j admit ALL local nonadjacent-two-coordinate translation witnesses using ANY3of4corners, but their best possible fractional turn-position packing is at most n-1. Mass1/2 at first AND last of each intermediate cardinality layer is a feasible exact dual. Thus the ENTIRE face-local corner-witness subfamily cannot prove positive density.',
         'scope':'Excludes all4triples of everylocal two-coordinate face across all h,k,bases, not arbitrary ordered triples spanning different such faces, within-layer witnesses, existing raw cancellation/cycle certificates, or the main M_n target. Audits n3..14 stress the analytic all-n dual.',
         'proof':'If the triple contains its lowest corner, its interval contains the first-of-layer(r+1) position and its translated interval contains first-of-layer(r+2). This holds even when the last corner has cardinalityr+2; if it has cardinalityr+1 it cannot be first in that layer because the middle vertex precedes it. If the triple omits its lowest corner, its first/middle vertices share cardinalityr+1, so its interval contains the LAST position of that layer; the translated interval contains LASToflayerr+2. Since r<=n-3 both points are valid. Each union contains two distinct dual points. Half mass at2(n-1)points totalsn-1 and covers all4corner triples. Summing primal capacities against this exact dual bounds every fractional packing.',
         'actual_dimension_audits':rows,'violations':0,'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    Path(__file__).with_name('local_corner_interval_obstruction_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('actual_dimension_audits','proof')}),flush=True)

if __name__=='__main__':main()
