#!/usr/bin/env python3
"""All nine coordinate positions over the exact full insertion wedge."""
from pathlib import Path
from fractions import Fraction as F
from math import lcm
from collections import Counter
import hashlib,json,time
from verify_cardinality_wedge_next_insertion import scaled_parent
from verify_cardinality_half_density import primary_order
from verify_face_local_obstruction import subset_scores
from probe_larger_cardinality_cores import analyze
from verify_gray_reflection_graph import gray,counts

ROOT=Path(__file__).parent
def rat(x):return [x.numerator,x.denominator]

def attainer(row):
    b=tuple(row['secondary']);B=sum(b)+1;z=row['input_reflection']
    w=tuple(-(B+x) if z>>j&1 else B+x for j,x in enumerate(b))
    scores=subset_scores(w);p=tuple(sorted(range(512),key=scores.__getitem__))
    assert len(set(scores))==512
    positive=primary_order(b);assert p==tuple(x^z for x in positive)
    # Direct interior change count; no reflection-graph formula here.
    changes=triples=0
    for aa,vv,cc in zip(p,p[1:],p[2:]):
        a,v,c=aa^z,vv^z,cc^z
        if a.bit_count()!=v.bit_count() or v.bit_count()!=c.bit_count():continue
        triples+=1;changes+=(gray(vv)>gray(aa))!=(gray(cc)>gray(vv))
    assert triples==512-18
    assert 2*changes==triples+row['D_int']-row['E_int']
    return {'weights':w,'R_C':counts(tuple(map(gray,p)))[:2],
            'direct_interior_changes':changes,'interior_triples':triples}

def main():
    start=time.monotonic();cover=json.loads((ROOT/'cardinality_wedge_next_insertion_certificate.json').read_text())
    assert cover['cell_count']==16 and cover['total_generic_H_intervals']==6768
    unique={};regions=0
    for cell in cover['records']:
        t,A=(F(*r) for r in cell['representative']);parent,_=scaled_parent(t,A)
        bp=[F(*r) for r in cell['plane_values']]
        reps=[bp[0]-1]+[(a+b)/2 for a,b in zip(bp,bp[1:])]+[bp[-1]+1]
        for interval,H in enumerate(reps):
            raw=tuple(v+H for v in parent)+(F(0),)
            den=lcm(*(x.denominator for x in raw));b=tuple(int(x*den) for x in raw)
            p=primary_order(b);regions+=1
            if p not in unique:
                unique[p]={'raw':b,'cell':cell['cell_id'],'interval':interval,
                           'parameters':[rat(t),rat(A),rat(H)]}
    assert regions==6768 and len(unique)==802
    records=[];best=[None]*9;hist=[Counter() for i in range(9)];digest=hashlib.sha256()
    for index,(original,rep) in enumerate(unique.items()):
        values=[]
        for position in range(9):
            b=rep['raw'][:8];b=b[:position]+(rep['raw'][8],)+b[position:]
            row=analyze(b);assert not row['tie_refined']
            # Verify the complete coordinate permutation of the base order.
            def move(x):
                low=x&((1<<position)-1);high=(x&255)>>position
                return low|(high<<(position+1))|(((x>>8)&1)<<position)
            assert primary_order(b)==tuple(move(x) for x in original)
            vals=[row['D_int'],row['E_int'],row['net']];values.append(vals)
            hist[position][row['net']]+=1
            digest.update(json.dumps((index,position,row['D_int'],row['interior_edges'],row['E_int'])).encode())
            if best[position] is None or row['net']>best[position]['certificate']['net']:
                best[position]={'base_order_index':index,'representative':rep,
                                'position':position,'certificate':row,'actual_scan':attainer(row)}
        records.append({'index':index,'base_order_sha256':hashlib.sha256(json.dumps(original).encode()).hexdigest(),
                        'representative':rep,'D_E_net_by_position':values})
        if index%100==0:print(json.dumps({'orders_done':index+1,'best_net_by_position':[r['certificate']['net'] for r in best],
                                        'elapsed':round(time.monotonic()-start,3)}),flush=True)
    assert [r['certificate']['net'] for r in best]==[70,70,28,10,8,66,58,72,72]
    out={'state':'COMPLETE_ALL_NINE_POSITIONS_OVER_REAL_PARENT_WEDGE',
         'source_covering_digest':cover['verification_digest'],'covered_parameter_regions':regions,
         'distinct_base_orders':len(unique),'position_order_evaluations':9*len(unique),
         'best_by_position':best,'net_histograms_by_position':[dict(sorted(x.items())) for x in hist],
         'records':records,'violations':0,'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'coverage_proof':'The exact three-real-parameter source certificate covers every generic highest-insertion order, including boundary points by continuity. Relabeling the insertion bit to each position while retaining old-coordinate relative order is a bijection on vertices and preserves score comparisons. Thus each base order determines every positioned child order independent of its representative metric. All 802 base orders and all nine positions were checked.',
         'limitations':'Only this two-dimensional parent metric wedge times all real offsets, and nine order-preserving coordinate embeddings. Other parent vectors and arbitrary old-coordinate permutations are not covered. No all-dimensional M_n lower bound follows.'}
    (ROOT/'cardinality_wedge_all_positions_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({'state':out['state'],'regions':regions,'evaluations':9*len(unique),
                      'best_net_by_position':[r['certificate']['net'] for r in best],
                      'best_limit_by_position':[r['certificate']['tail_limit_fraction'] for r in best],
                      'verification_digest':out['verification_digest'],'elapsed_seconds':out['elapsed_seconds']}),flush=True)

if __name__=='__main__':main()
