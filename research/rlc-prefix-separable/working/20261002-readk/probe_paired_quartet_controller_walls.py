#!/usr/bin/env python3
"""Exact fixed-upper-metric two-parameter walls with restored controller phase.

For each fixed genuine upper vector, visits ALL generic cells in positive
(w0,w1), including both priority cones, and every paired upper-rank mask.
This is NOT all full-dimensional weight chambers: upper weights are fixed.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from math import lcm
import gzip,hashlib,json,time
from verify_gray_reflection_graph import order_and_scores,positive_chambers
from verify_paired_sibling_ranks import rank,fast_runs

def cells(scores):
    ds=sorted({abs(s-t) for s in scores for t in scores if s!=t})
    lines=[(m,Fraction(d)) for m in (-1,0,1) for d in ds]+[(1,Fraction(0))]
    acut={Fraction(0),*(Fraction(d) for d in ds)}
    for m,c in lines:
        for mm,cc in lines:
            if m!=mm:
                v=(cc-c)/(m-mm)
                if v>0:acut.add(v)
    aa=sorted(acut);aa.append(aa[-1]+2)
    for lo,hi in zip(aa,aa[1:]):
        a=(lo+hi)/2;bb=sorted({a}|{m*a+c for m,c in lines if m*a+c>a});bb.append(bb[-1]+2)
        for ll,hh in zip(bb,bb[1:]):yield a,(ll+hh)/2

def costs(offsets,a,b,block,return_costs=False):
    F=len(offsets);rows=sorted((s+c,f,x) for f,s in enumerate(offsets) for x,c in enumerate((0,a,b,a+b)))
    assert len({s for s,f,x in rows})==4*F
    signs=[]
    for (_,f,x),(_,g,y) in zip(rows,rows[1:]):
        if f!=g:signs.append((None,0,1 if block[g]>block[f] else -1))
        else:signs.append((f,(x^y).bit_length()-1,1 if (y^(y>>1))>(x^(x>>1)) else -1))
    local=[[0]*4 for f in range(F)];constant=1
    for d,e in zip(signs,signs[1:]):
        free={z[0] for z in (d,e) if z[0] is not None};assert len(free)<=1
        if not free:constant+=int(d[2]!=e[2])
        else:
            f=next(iter(free))
            for mask in range(4):
                def sg(z):return z[2] if z[0] is None else z[2]*(-1 if mask>>z[1]&1 else 1)
                local[f][mask]+=int(sg(d)!=sg(e))
    relaxed=constant+sum(min(z) for z in local);masks=[0]*F
    paired=constant
    for prefix in range(F//2):
        opt=[]
        for theta in (0,1):
            chosen=[];total=0
            for f in (2*prefix,2*prefix+1):
                phase=(f&1)^theta;candidates=[low+2*phase for low in (0,1)]
                mask=min(candidates,key=local[f].__getitem__);chosen.append(mask);total+=local[f][mask]
            opt.append((total,chosen))
        val,chosen=min(opt);paired+=val;masks[2*prefix:2*prefix+2]=chosen
    values=[4*block[f]+((x^(x>>1))^masks[f]) for s,f,x in rows]
    ss=[1 if y>x else -1 for x,y in zip(values,values[1:])]
    assert paired==1+sum(x!=y for x,y in zip(ss,ss[1:]))
    if return_costs:return relaxed,paired,masks,rows,constant,local
    return relaxed,paired,masks,rows

def main():
    start=time.monotonic();rows=[];failures=[];counts=Counter();digest=hashlib.sha256();overall=10**9
    upper_metrics=list(positive_chambers(3))
    for wi,w in enumerate(upper_metrics):
        d=len(w);F=1<<d;offsets=[sum(w[j]*((f>>j)&1) for j in range(d)) for f in range(F)]
        upper_order=order_and_scores(w)[0];cases=0;minimum=10**9;relaxed_min=10**9;paired_bad=[];relaxed_bad=[]
        blocks=[tuple(rank(f,d,mask) for f in range(F)) for mask in range(1<<((1<<(d-1))-1))]
        for aa,bb in cells(offsets):
            scale=lcm(aa.denominator,bb.denominator)
            for a,b in ((int(aa*scale),int(bb*scale)),(int(bb*scale),int(aa*scale))):
                off=[s*scale for s in offsets]
                for mask,block in enumerate(blocks):
                    r,p,local,word=costs(off,a,b,block);cases+=1;minimum=min(minimum,p);relaxed_min=min(relaxed_min,r);overall=min(overall,p)
                    U=fast_runs(block,upper_order);bound=min(F+1,4*U-3)
                    if r<bound or p<F+1:
                        z={'upper_weights':w,'upper_metric_index':wi,'upper_mask':mask,'upper_rank':block,
                           'weights':(a,b)+tuple(scale*x for x in w),'rank_dimension':d+2,'local_masks':local,
                           'relaxed_minimum':r,'paired_minimum':p,'upper_runs':U,'scalar_target':bound,'quarter_target':F+1}
                        if r<bound:relaxed_bad.append(z)
                        if p<F+1:paired_bad.append(z)
                    digest.update(json.dumps((wi,a,b,scale,mask,r,p)).encode())
        row={'upper_weights':w,'complete_fixed_upper_wall_rank_cases':cases,'paired_minimum':minimum,
             'relaxed_minimum':relaxed_min,'relaxed_scalar_failures':len(relaxed_bad),'paired_quarter_failures':len(paired_bad)}
        rows.append(row);failures+=relaxed_bad+paired_bad;counts['fixed_upper_metrics']+=1;counts['wall_rank_cases']+=cases
        print(json.dumps(row|{'elapsed':time.monotonic()-start}),flush=True)
    out={'status':'EXACT_PAIRED_CONTROLLER_FIXED_UPPER_WALL_AUDIT','coverage':'All positive two-parameter generic (w0,w1) cells and paired upper masks for EACH of12 fixed Q3 upper metric representatives. NOT all Q5 weight-space chambers; no all-dimensional theorem.',
         'analytic_controller_identity':'local bit1 phase(f)=(f&1) XOR theta1(f>>1), while local bit0 phase is independent per face.',
         'counts':dict(counts),'rows':rows,'all_failures':failures,'overall_paired_minimum':overall,'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('paired_quartet_controller_wall_pressure.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','all_failures')}|{'failures':len(failures)}),flush=True)

if __name__=='__main__':main()
