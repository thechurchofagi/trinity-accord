#!/usr/bin/env python3
"""A real all-dimensional paired obstruction to R_merge>=2R_upper-1."""
from pathlib import Path
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs,separator_check

BASE=(4,3,2,8)

def gray(x):return x^(x>>1)
def mask(n,core):
    bits=bytearray(((1<<(n-1))-1+7)//8);off=0
    for h in range(n-1):
        for prefix in range(1<<(n-h-2)):
            bit=0
            if h<core-1:
                z=prefix>>(core-h-2);bit=gray(z)&1
            elif h==core-1:bit=prefix&1
            if bit:bits[(off+prefix)//8]|=1<<((off+prefix)%8)
        off+=1<<(n-h-2)
    return int.from_bytes(bits,'little')

def formula(x,core):
    z=x>>core;u=x&((1<<core)-1);upper=gray(z);phase=upper&1
    return (upper<<core)+(gray(u)^(((1<<core)-1)*phase))

def main():
    start=time.monotonic();rng=random.Random(202610031325);rows=[]
    for n in range(4,19):
        m=n-4;T=1<<m;w=BASE+tuple(18*(1<<j) for j in range(m))
        p,scores=order_and_scores(w);core=order_and_scores(BASE)[0]
        assert p==tuple((z<<4)|u for z in range(T) for u in core)
        assert len(set(scores))==1<<n
        rho=[formula(x,4) for x in range(1<<n)];assert len(set(rho))==1<<n
        upperw=w[1:];upperp=order_and_scores(upperw)[0]
        sigma=[formula(y,3) for y in range(1<<(n-1))]
        assert all(rho[x]>>1==sigma[x>>1] for x in range(1<<n))
        assert all(x>>1!=y>>1 for x,y in zip(p,p[1:]))
        R=fast_runs(rho,p);U=fast_runs(sigma,upperp)
        theta=mask(n,4);uppertheta=mask(n-1,3)
        points=range(1<<n) if n<=12 else rng.sample(range(1<<n),1024)
        assert all(rank(x,n,theta)==rho[x] for x in points)
        upperpoints=range(1<<(n-1)) if n<=12 else rng.sample(range(1<<(n-1)),1024)
        assert all(rank(y,n-1,uppertheta)==sigma[y] for y in upperpoints)
        B=0 if T==1 else 3*T//2-1
        assert (R,U)==(9*T+1+B,5*T+1+B)
        gap=2*U-1-R;assert gap==T+B>0
        out={'n':n,'T':T,'weights':w,'R':R,'U':U,'boundary_turn_cost':B,
             'proposed_scalar_lower_bound':2*U-1,'strict_deficit':gap,
             'rank_mask_sha256':hashlib.sha256(theta.to_bytes(((1<<(n-1))-1+7)//8,'little')).hexdigest()}
        if n<=6:out['strict_prefix_separator_checks']=separator_check(rho,n,theta)
        rows.append(out)
    out={'status':'VERIFIED_REAL_ALL_DIMENSION_TWO_COPY_SCALAR_RECURSION_OBSTRUCTION',
         'analytic_statement':'For every n>=5,T=2^(n-4), actual positive generic weights with w0>w1 and admissible paired ranks have R=21T/2,U=13T/2, so (2U-1)-R=5T/2-1=(5/32)2^n-1. At n4 the seed has R10,U6 and deficit1.',
         'scope':'Refutes a scalar factor-two single-coordinate recursion even with actual upper paired structure. Does NOT refute any positive-density main bound or the quarter conjecture.',
         'rank_formula':'rho(x)=16*g(z)+(g(u) XOR(15*(g(z)&1))), z=x>>4,u=x&15. Upper projection uses8 and7 on x>>1.',
         'paired_mask_identity':'Below the core root use phase g(z)&1; at the core root theta is the next outer input bit; higher theta values are0. Thus every rank prefix uses the inherited strict paired separator.',
         'proof':'Both seed row sign words start positive,end negative,with9 and5 turns. Reflecting their full core ranks by the same outer phase preserves row turns and negates endpoint signs. Every boundary has the SAME extra cost in the full and upper words. Binary outer increments at lowest-bit carries flip Gray parity and cost2; all other increments preserve parity and cost1. There are T/2 first-type boundaries and T/2-1 others, giving B=3T/2-1. Hence R=9T+1+B,U=5T+1+B.',
         'actual_dimension_audits':rows,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('paired_two_copy_scalar_obstruction_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('actual_dimension_audits','proof','paired_mask_identity')}),flush=True)

if __name__=='__main__':main()
