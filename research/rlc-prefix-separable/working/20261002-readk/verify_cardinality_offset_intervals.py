#!/usr/bin/env python3
"""Complete real offset intervals for four fixed coherent secondary cores."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib
import json
import time
from probe_larger_cardinality_cores import analyze
from verify_face_local_obstruction import subset_scores
from verify_gray_reflection_graph import gray, counts

CORES=((4,6,3,0,8,16,28),
       (4,6,3,0,8,24,36),
       (76,74,73,70,78,94,0,138),
       (108,106,105,102,110,126,32,170,0))

def main():
    start=time.monotonic();digest=hashlib.sha256();records=[]
    for b in CORES:
        k=len(b);N=1<<k;s=subset_scores(b);base=analyze(b)
        assert not base['tie_refined']
        layers=[tuple(x for x in range(N) if x.bit_count()==j) for j in range(k+1)]
        bp=sorted({s[y]-s[x] for j in range(1,k+1) for y in layers[j-1] for x in layers[j]})
        reps=[Fraction(bp[0]-1)]+[Fraction(lo+hi,2) for lo,hi in zip(bp,bp[1:])]+[Fraction(bp[-1]+1)]
        bounds=[(None,bp[0])]+list(zip(bp,bp[1:]))+[(bp[-1],None)]
        values=[];hist=Counter();best=None;seen=set()
        for index,(A,interval) in enumerate(zip(reps,bounds)):
            den=A.denominator;num=A.numerator
            secondary=tuple(den*v+num for v in b)+(0,)
            r=analyze(secondary)
            assert not r['tie_refined']
            assert r['core_order_sha256'] not in seen;seen.add(r['core_order_sha256'])
            hist[r['net']]+=1;values.append(r['net'])
            if index in (0,len(reps)-1):
                assert r['D_int']==2*base['D_int']
                assert r['E_int']==2*base['E_int']
                assert r['interior_edges']==tuple((h,j,2*v) for h,j,v in base['interior_edges'])
            digest.update(json.dumps((b,interval,str(A),r['D_int'],r['interior_edges'],r['E_int'])).encode())
            if best is None or r['net']>best['certificate']['net']:
                # Independent actual signed scan of the parent class.
                raw=tuple(r['secondary']);B=sum(raw)+1;weights=tuple(B+v for v in raw)
                z=r['input_reflection']
                signed=tuple(-v if z>>j&1 else v for j,v in enumerate(weights))
                score=subset_scores(signed)
                actual=tuple(sorted(range(1<<(k+1)),key=score.__getitem__))
                assert len(set(score))==1<<(k+1)
                R,C,_=counts(tuple(map(gray,actual)))
                best={'interval_index':index,'open_interval':interval,
                      'representative_offset':[num,den],'certificate':r,
                      'actual_signed_weights':signed,'actual_R_C':[R,C]}
        record={'parent_core':b,'parent_interior':base,
                'all_breakpoints':bp,'open_interval_count':len(reps),
                'interval_net_energies':values,'net_histogram':dict(sorted(hist.items())),
                'best':best,'separated_net_energy':2*base['net'],
                'maximum_net_energy':best['certificate']['net'],
                'improvement_over_separated':best['certificate']['net']-2*base['net']}
        records.append(record)
        print(json.dumps({'k':k,'intervals':len(reps),'best_net':record['maximum_net_energy'],
              'separated_net':record['separated_net_energy'],'best_offset':best['representative_offset'],
              'limit_fraction':best['certificate']['tail_limit_fraction'],
              'elapsed':round(time.monotonic()-start,3)}),flush=True)
    same_order=records[0]['parent_interior']['core_order_sha256']==records[1]['parent_interior']['core_order_sha256']
    out={'state':'COMPLETE_REAL_OFFSET_INTERVALS_FOR_FOUR_FIXED_PARENTS',
         'records':records,'violations':0,
         'verification_digest':digest.hexdigest(),'elapsed_seconds':round(time.monotonic()-start,3),
         'first_two_parents_have_same_cardinality_order':same_order,
         'coverage_proof':'Within an extended cardinality layer, cross-face scores differ by A-(b dot y-b dot x) for |y|=|x|-1. All breakpoints are listed; exact rational representatives cover every generic real A interval. Same-face orders never change.',
         'limitations':'All offsets for these four parents are classified. Other parents, arbitrary coordinate insertions, and all dimensions are not classified. No primary M_n result follows.'}
    Path(__file__).with_name('cardinality_offset_interval_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'}),flush=True)

if __name__=='__main__':main()
