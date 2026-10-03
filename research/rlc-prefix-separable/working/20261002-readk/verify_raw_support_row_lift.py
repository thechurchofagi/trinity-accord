#!/usr/bin/env python3
"""Exact genuine additive row lifts: raw support invariance, all low labels.

The analytic theorem is all-dimensional; these finite audits stress its
signed weights, variable relabeling, roots, joins and arbitrary low labels.
This is a quantifier reduction, NOT a proof or refutation of M_n.
"""
from pathlib import Path
import gzip, hashlib, json, random, time
from verify_paired_sibling_ranks import rank, fast_runs

def order(w):
    scores=[sum(c for j,c in enumerate(w) if x>>j&1) for x in range(1<<len(w))]
    if len(set(scores))!=len(scores): return None
    return tuple(sorted(range(len(scores)),key=scores.__getitem__))

def support(p,n):
    return {(h,x>>(h+2)) for x,y in zip(p,p[1:])
            if (h:=(x^y).bit_length()-1)<n-1}

def independent_rank(x,n,mask,top):
    # MSB-first, closed-form offset; no imported rank recursion.
    r=((x>>(n-1))^top)<<(n-1)
    for h in range(n-2,-1,-1):
        index=(1<<(n-1))-(1<<(n-h-1))+(x>>(h+2))
        r|=(((x>>h)^(x>>(h+1))^(mask>>index))&1)<<h
    return r

def audit_core(w,theta,top):
    m=len(w);p=order(w);assert p is not None
    q=support(p,m);r=[rank(x,m,theta,top) for x in range(1<<m)]
    a=[1 if r[y]>r[x] else -1 for x,y in zip(p,p[1:])]
    j=1 if r[p[0]]>r[p[-1]] else -1
    beta=int(a[-1]!=j)+int(j!=a[0]);R=fast_runs(r,p)
    assert R==1+sum(x!=y for x,y in zip(a,a[1:]))
    L=1+sum(abs(c) for c in w);profiles=[]
    for d in range(1,6):
        n=m+d;T=1<<d;delta=(1<<(n-1))-(1<<(m-1))
        W=tuple(L<<h for h in range(d))+w
        P=order(W);expected=tuple((u<<d)|t for t in range(T) for u in p)
        assert P==expected
        assert support(P,n)=={(h+d,z) for h,z in q}
        order_digest=hashlib.sha256(json.dumps(P).encode()).hexdigest()
        for variant in ('zero','ones','alternating'):
            low=0 if variant=='zero' else (1<<delta)-1 if variant=='ones' else sum(1<<h for h in range(0,delta,2))
            fullmask=(theta<<delta)|low
            rr=[independent_rank(x,n,fullmask,top) for x in range(1<<n)]
            assert all((rr[x]>>d)==r[x>>d] for x in range(1<<n))
            assert rr==[rank(x,n,fullmask,top) for x in range(1<<n)]
            signs=[1 if rr[y]>rr[x] else -1 for x,y in zip(P,P[1:])]
            predicted=[]
            for t in range(T):
                predicted.extend(a)
                if t<T-1:predicted.append(j)
            assert signs==predicted
            runs=1+sum(x!=y for x,y in zip(signs,signs[1:]))
            assert runs==1+T*(R-1)+(T-1)*beta
            assert runs==fast_runs(rr,P) and runs<=T*(R+1)-1
            profiles.append({'d':d,'n':n,'low_mask_variant':variant,'q':len(q),
                'runs':runs,'order_sha256':order_digest,
                'rank_word_sha256':hashlib.sha256(json.dumps([rr[x] for x in P]).encode()).hexdigest()})
    return {'core_weights':w,'core_mask_decimal':str(theta),'root':top,'m':m,'q_core':len(q),
        'raw_support_core':sorted(q),'R_core':R,'first_sign':a[0],'last_sign':a[-1],
        'join_sign':j,'beta':beta,'L':L,'profiles':profiles}

def main():
    st=time.monotonic();rng=random.Random(202610031820);rows=[]
    for m in range(2,8):
        for t in range(4):
            while True:
                w=tuple(rng.randrange(1,5001)*(-1 if (j+t)%3==0 else 1) for j in range(m))
                if order(w) is not None:break
            masks=list(range(1<<((1<<(m-1))-1))) if m<=3 else [0]+[rng.getrandbits((1<<(m-1))-1) for _ in range(3)]
            for mask in masks:
                for root in (0,1):rows.append(audit_core(w,mask,root))
    out={'status':'VERIFIED_GENUINE_RAW_SUPPORT_INVARIANT_ROW_LIFT',
        'analytic_scope':'Every signed generic m-dimensional additive scan and every paired rank, arbitrary d lower input coordinates with high score weights L*2^j, L>sum|v|. All arbitrary new lower controller labels. q_lift=q_core; R_lift=1+T*(R_core-1)+(T-1)*beta, beta in {0,1,2}.',
        'consequence':'An eventual universal support-defect inequality R>=a*N-b*q for every paired rank and genuine scan implies R_core>=a*2^m-1 for EVERY paired core rank and EVERY genuine scan. Stronger quantifier than the existential M_n target; neither proved nor refuted here.',
        'seed':202610031820,'core_rank_root_contexts':len(rows),
        'actual_weight_orders':6*4*5,'direct_lifted_rank_audits':sum(len(x['profiles']) for x in rows),
        'beta_values':sorted({x['beta'] for x in rows}),'violations':0,
        'seconds':time.monotonic()-st,'rows':rows}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    b=(json.dumps(out,indent=2)+'\n').encode()
    Path(__file__).with_name('raw_support_row_lift_certificate.json.gz').write_bytes(gzip.compress(b,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)
    print(json.dumps({'uncompressed_bytes':len(b),'uncompressed_sha256':hashlib.sha256(b).hexdigest()}),flush=True)

if __name__=='__main__':main()
