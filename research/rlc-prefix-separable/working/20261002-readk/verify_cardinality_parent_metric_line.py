#!/usr/bin/env python3
"""Complete two-parameter (t, insertion A) classification inside one parent chamber."""
from fractions import Fraction
from pathlib import Path
from collections import Counter
import hashlib
import json
import time
from verify_face_local_obstruction import subset_scores
from verify_cardinality_half_density import primary_order
from probe_larger_cardinality_cores import analyze

BASE=(4,6,3,0,8,16,28)
DELTA=(0,0,0,0,0,8,8)

def rat(x):
    return None if x is None else [x.numerator,x.denominator]

def main():
    start=time.monotonic();N=128
    sb=subset_scores(BASE);sd=subset_scores(DELTA)
    p=primary_order(BASE)
    endpoint=tuple(a+c for a,c in zip(BASE,DELTA))
    assert primary_order(endpoint)==p
    adjacent=[tuple(((y>>j)&1)-((x>>j)&1) for j in range(7))
              for x,y in zip(p,p[1:]) if x.bit_count()==y.bit_count()]
    assert len(adjacent)==120
    # Strict positive endpoint margins prove constancy on the WHOLE segment.
    for row in adjacent:
        assert sum(a*b for a,b in zip(row,BASE))>0
        assert sum(a*b for a,b in zip(row,endpoint))>0
    layers=[tuple(x for x in range(N) if x.bit_count()==k) for k in range(8)]
    lines=sorted({(sb[y]-sb[x],sd[y]-sd[x])
                  for k in range(1,8) for y in layers[k-1] for x in layers[k]})
    critical={Fraction(0),Fraction(1)}
    for i,(a,c) in enumerate(lines):
        for aa,cc in lines[i+1:]:
            if c!=cc:
                t=Fraction(aa-a,c-cc)
                if 0<t<1:critical.add(t)
    critical=sorted(critical)
    strips=[{'kind':'open_strip','t_bounds':[rat(lo),rat(hi)],'t':(lo+hi)/2}
             for lo,hi in zip(critical,critical[1:])]
    sections=[{'kind':'critical_section','t_bounds':[rat(t),rat(t)],'t':t} for t in critical]
    records=[];digest=hashlib.sha256();total_intervals=0;all_orders=set()
    for item in strips+sections:
        t=item['t'];den=t.denominator;num=t.numerator
        b=tuple(den*a+num*c for a,c in zip(BASE,DELTA))
        assert primary_order(b)==p
        bp=sorted({Fraction(den*a+num*c) for a,c in lines})
        offsets=[bp[0]-1]+[(lo+hi)/2 for lo,hi in zip(bp,bp[1:])]+[bp[-1]+1]
        intervals=[(None,bp[0])]+list(zip(bp,bp[1:]))+[(bp[-1],None)]
        best=None;hist=Counter();vectors=[];hashes=[]
        for i,(A,interval) in enumerate(zip(offsets,intervals)):
            raw=tuple(A.denominator*v+A.numerator for v in b)+(0,)
            r=analyze(raw);assert not r['tie_refined']
            all_orders.add(r['core_order_sha256']);total_intervals+=1
            hist[r['net']]+=1
            vectors.append([r['D_int'],r['E_int'],r['net']])
            hashes.append(r['core_order_sha256'])
            digest.update(json.dumps((item['kind'],rat(t),i,r['D_int'],r['interior_edges'],r['E_int'])).encode())
            if best is None or r['net']>best['certificate']['net']:
                best={'offset_original_units':rat(A/den),
                      'offset_interval_original_units':[rat(x/den) if x is not None else None for x in interval],
                      'certificate':r}
        record={'kind':item['kind'],'t_bounds':item['t_bounds'],'representative_t':rat(t),
                'insertion_line_values_at_representative':[rat(x/den) for x in bp],
                'interval_count':len(offsets),'D_E_net':vectors,
                'order_hash_chain_sha256':hashlib.sha256(''.join(hashes).encode()).hexdigest(),
                'net_histogram':dict(sorted(hist.items())),'best':best}
        records.append(record)
        print(json.dumps({'kind':item['kind'],'t':str(t),'t_bounds':item['t_bounds'],
              'intervals':len(offsets),'max_net':best['certificate']['net'],
              'elapsed':round(time.monotonic()-start,3)}),flush=True)
    # Exhaustively verified analytic wedge: the only improvement occurs
    # when the two displayed moving breakpoints have this strict order.
    for r in records:
        t=Fraction(*r['representative_t'])
        bp=[Fraction(*x) for x in r['insertion_line_values_at_representative']]
        good=[i for i,vals in enumerate(r['D_E_net']) if vals[2]>32]
        if t<=Fraction(3,4):
            assert not good and r['best']['certificate']['net']==32
        else:
            assert len(good)==1
            i=good[0]
            assert r['D_E_net'][i]==[18,54,36]
            assert bp[i-1]==29+8*t and bp[i]==23+16*t
            assert r['best']['certificate']['core_order_sha256']=='f234e0f6ee0a3a420eb3d37bd22277f7e43c143ca1aae8bedac8d3b62ec8f597'
        assert all(vals[2]<=32 for i,vals in enumerate(r['D_E_net']) if i not in good)
    out={'state':'COMPLETE_REAL_TWO_PARAMETER_PARENT_CHAMBER_LINE',
         'parent_base':BASE,'parent_delta':DELTA,'parent_adjacent_rows':adjacent,
         'distinct_cross_face_breakpoint_lines':lines,'critical_t':[rat(t) for t in critical],
         'records':records,'generic_insertion_intervals_evaluated':total_intervals,
         'distinct_child_orders':len(all_orders),'violations':0,
         'exact_improvement_region':'3/4<t<=1 AND 29+8t<A<23+16t; there D_int=18,E_int=54,net=36. Every other generic pair has net<=32.',
         'optimal_tail_limit_by_t':'7/16 for 0<=t<=3/4; 55/128 for 3/4<t<=1.',
         'verification_digest':digest.hexdigest(),'elapsed_seconds':round(time.monotonic()-start,3),
         'coverage_proof':'Endpoint strict rows prove constant parent order on [0,1]. Every cross-face breakpoint is affine in t. All pairwise line intersections are listed. Within each open strip the line order is fixed; every exact A interval is covered. Critical sections are checked independently. Thus every generic real pair (t,A) is covered.',
         'limitations':'Complete only on this one parent metric segment times all real insertion offsets. No all-parent or dimension-uniform M_n claim.'}
    Path(__file__).with_name('cardinality_parent_metric_line_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','generic_insertion_intervals_evaluated','distinct_child_orders','verification_digest','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
