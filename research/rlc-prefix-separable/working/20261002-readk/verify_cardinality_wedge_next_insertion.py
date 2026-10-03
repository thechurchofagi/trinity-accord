#!/usr/bin/env python3
"""Exact full three-parameter insertion audit over an improving parent wedge.

All polygon arithmetic, score comparisons and spin optimization are exact.
This is a restricted-family classification, never an all-weight lower bound.
"""
from fractions import Fraction as F
from pathlib import Path
from math import gcd,lcm
from collections import Counter
import hashlib,json,time
from verify_face_local_obstruction import subset_scores
from probe_larger_cardinality_cores import analyze
from verify_gray_reflection_graph import gray,counts

BASE=(4,6,3,0,8,16,28,0)
TCOEF=(0,0,0,0,0,8,8,0)
ACOEF=(1,1,1,1,1,1,1,0)
TRIANGLE=((F(3,4),F(35)),(F(1),F(37)),(F(1),F(39)))

def rat(x):return [x.numerator,x.denominator]
def value(row,p):return row[0]+row[1]*p[0]+row[2]*p[1]
def canonical(row):
    g=gcd(*row);row=tuple(x//g for x in row)
    return row if next(x for x in row if x)>0 else tuple(-x for x in row)

def area(p):
    return abs(sum(x[0]*y[1]-x[1]*y[0] for x,y in zip(p,p[1:]+p[:1])))/2 if len(p)>=3 else F(0)

def clip(poly,row,sign):
    out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        a=sign*value(row,p);b=sign*value(row,q)
        if a>=0:out.append(p)
        if (a<0<b) or (b<0<a):
            z=a/(a-b)
            out.append(tuple(x+z*(y-x) for x,y in zip(p,q)))
    cleaned=[]
    for p in out:
        if not cleaned or p!=cleaned[-1]:cleaned.append(p)
    if len(cleaned)>1 and cleaned[0]==cleaned[-1]:cleaned.pop()
    return tuple(cleaned)

def scaled_parent(t,A):
    raw=tuple(F(x)+t*y+A*z for x,y,z in zip(BASE,TCOEF,ACOEF))
    den=lcm(*(x.denominator for x in raw))
    return raw,tuple(int(x*den) for x in raw)

def main():
    start=time.monotonic();N=256
    s0,st,sa=map(subset_scores,(BASE,TCOEF,ACOEF))
    layers=[tuple(x for x in range(N) if x.bit_count()==k) for k in range(9)]
    planes=sorted({(s0[y]-s0[x],st[y]-st[x],sa[y]-sa[x])
                   for k in range(1,9) for y in layers[k-1] for x in layers[k]})
    assert len(planes)==422
    lines=set()
    for i,g in enumerate(planes):
        for h in planes[i+1:]:
            diff=tuple(x-y for x,y in zip(g,h))
            vals=[value(diff,p) for p in TRIANGLE]
            if min(vals)<0<max(vals):lines.add(canonical(diff))
    lines=sorted(lines)
    assert len(lines)==9
    cells=[(TRIANGLE,())]
    for row in lines:
        new=[]
        for p,signs in cells:
            for sign in (-1,1):
                q=clip(p,row,sign)
                if area(q)>0:new.append((q,signs+(sign,)))
        cells=new
    assert sum(area(p) for p,sgn in cells)==area(TRIANGLE)
    records=[];orders=set();digest=hashlib.sha256();best_global=None;total=0
    for cell_id,(poly,signs) in enumerate(cells):
        center=tuple(sum(p[j] for p in poly)/len(poly) for j in range(2))
        assert all(sign*value(row,center)>0 for row,sign in zip(lines,signs))
        t,A=center;assert F(3,4)<t<1 and 29+8*t<A<23+16*t
        parent,pint=scaled_parent(t,A);pr=analyze(pint)
        assert not pr['tie_refined'] and pr['net']==36
        bp=sorted(value(g,center) for g in planes)
        assert len(set(bp))==422
        reps=[bp[0]-1]+[(x+y)/2 for x,y in zip(bp,bp[1:])]+[bp[-1]+1]
        vals=[];hist=Counter();hashes=[];best=None
        for interval,H in enumerate(reps):
            child=tuple(x+H for x in parent)+(F(0),)
            den=lcm(*(x.denominator for x in child))
            integer=tuple(int(x*den) for x in child)
            r=analyze(integer);assert not r['tie_refined']
            if interval in (0,len(reps)-1):
                assert r['D_int']==2*pr['D_int'] and r['E_int']==2*pr['E_int']
                assert r['interior_edges']==tuple((h,k,2*v) for h,k,v in pr['interior_edges'])
            vals.append([r['D_int'],r['E_int'],r['net']]);hist[r['net']]+=1
            hashes.append(r['core_order_sha256']);orders.add(r['core_order_sha256']);total+=1
            digest.update(json.dumps((cell_id,interval,r['D_int'],r['interior_edges'],r['E_int'])).encode())
            if best is None or r['net']>best['certificate']['net']:
                best={'H':rat(H),'interval_index':interval,
                      'H_bounds':[rat(bp[interval-1]) if interval else None,
                                  rat(bp[interval]) if interval<len(bp) else None],
                      'certificate':r}
        # Independent actual integer score sort and rank-run count of each optimum.
        b=tuple(best['certificate']['secondary']);B=sum(b)+1;z=best['certificate']['input_reflection']
        w=tuple(-(B+x) if z>>j&1 else B+x for j,x in enumerate(b))
        scores=subset_scores(w);assert len(set(scores))==512
        actual=tuple(sorted(range(512),key=scores.__getitem__))
        best['actual_signed_weights']=w;best['actual_R_C']=counts(tuple(map(gray,actual)))[:2]
        record={'cell_id':cell_id,'vertices':[[rat(x),rat(y)] for x,y in poly],
                'refinement_signs':signs,'representative':[rat(t),rat(A)],
                'parent_order_sha256':pr['core_order_sha256'],
                'plane_values':[rat(x) for x in bp], 'interval_count':len(reps),
                'D_E_net':vals,'net_histogram':dict(sorted(hist.items())),
                'order_hash_chain_sha256':hashlib.sha256(''.join(hashes).encode()).hexdigest(),
                'best':best}
        records.append(record)
        if best_global is None or best['certificate']['net']>best_global['best']['certificate']['net']:
            best_global=record
        print(json.dumps({'cell':cell_id,'representative':record['representative'],
              'intervals':len(reps),'max_net':best['certificate']['net'],
              'elapsed':round(time.monotonic()-start,3)}),flush=True)
    assert len(cells)==16 and total==6768 and len(orders)==802
    assert all(r['best']['certificate']['net']==72 for r in records)
    out={'state':'COMPLETE_THREE_REAL_PARAMETER_INSERTION_OVER_PARENT_WEDGE',
         'parent_basis':[BASE,TCOEF,ACOEF],
         'parent_domain':'3/4<t<=1,29+8t<A<23+16t; ninth insertion H arbitrary generic real',
         'triangle_closure':[[rat(x),rat(y)] for x,y in TRIANGLE],
         'cross_face_planes':planes,'refinement_lines':lines,
         'cell_count':len(cells),'records':records,'best_global':best_global,
         'total_generic_H_intervals':total,'distinct_child_orders':len(orders),
         'global_maximum_net':best_global['best']['certificate']['net'],
         'violations':0,'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'coverage_proof':'Every within-parent-layer order is fixed. The 422 planes are all cross-face ties. Only the listed nine pairwise comparison lines cross the triangle interior. Exact clipping covers the entire triangle by positive-area cells. Every H interval is tested in each cell. On refinement boundaries, any generic child has strict finite comparisons; the same child order therefore persists at a nearby interior point, so no extra generic boundary order exists. This also covers t=1.',
         'limitations':'Only this explicitly parametrized parent wedge and highest-coordinate insertion. No all-parent, all-coordinate or dimension-uniform M_n conclusion.'}
    Path(__file__).with_name('cardinality_wedge_next_insertion_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','cell_count','total_generic_H_intervals','distinct_child_orders','global_maximum_net','verification_digest','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
