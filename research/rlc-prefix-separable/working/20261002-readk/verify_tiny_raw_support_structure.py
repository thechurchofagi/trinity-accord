#!/usr/bin/env python3
"""Universal rank-segment support bound; sharp q=0,1 for genuine scans."""
from collections import Counter
from itertools import permutations
from pathlib import Path
import gzip, hashlib, json, random, time
from verify_paired_sibling_ranks import rank, fast_runs, linear_graph
from verify_gray_reflection_graph import positive_chambers, order_and_scores

def labels(p,n):
    return [(h,x>>(h+2)) if (h:=(x^y).bit_length()-1)<n-1 else (n-1,0)
            for x,y in zip(p,p[1:])]

def opposite(label,n):
    h,z=label
    return label if h==n-1 else (h,z^((1<<(n-h-2))-1))

def segment_check(p,rs,labs,n):
    signs=[rs[y]>rs[x] for x,y in zip(p,p[1:])]
    q=len(set(labs)-{(n-1,0)});R=1;freq=Counter();prev=None
    for label,s in zip(labs,signs):
        if prev is not None and s!=prev:freq.clear();R+=1
        freq[label]+=1
        assert freq[label]<= (1 if label[0]==n-1 else 2)
        prev=s
    assert R>=((len(p)-2)//(2*q+1)+1)
    assert R==fast_runs(rs,p)
    return R

def genuine_audit(w,theta=0,top=0):
    n=len(w);N=1<<n;p,scores=order_and_scores(w);lab=labels(p,n)
    assert all(p[N-1-i]==(p[i]^(N-1)) for i in range(N))
    S=set(lab)-{(n-1,0)};q=len(S)
    assert {opposite(v,n) for v in S}==S
    assert all(opposite(lab[i],n)==lab[N-2-i] for i in range(N-1))
    g=[x^(x>>1) for x in p];sgn=[1 if b>a else -1 for a,b in zip(g,g[1:])]
    J=Counter();D=0
    for i in range(N-2):
        a,b=lab[i:i+2]
        if a==b:assert sgn[i]==-sgn[i+1];D+=1
        else:J[tuple(sorted((a,b)))]+=sgn[i]*sgn[i+1]
    J={k:v for k,v in J.items() if v}
    for (a,b),v in J.items():
        pair=tuple(sorted((opposite(a,n),opposite(b,n))))
        phase=(-1 if a[0]<n-1 else 1)*(-1 if b[0]<n-1 else 1)
        assert J.get(pair,0)==phase*v
        assert not (a[0]==b[0] and a!=b)
    root=(n-1,0);single=(n-2,0)
    assert J.get(tuple(sorted((root,single))),0)==0
    R=segment_check(p,[rank(x,n,theta,top) for x in range(N)],lab,n)
    if q==0:assert R==N-1
    if q==1:
        assert S=={single} and not J
        assert D%2==0 and R==(N+D)//2 and R>=N//2
    return {'weights':w,'n':n,'q':q,'D':D,'R':R,'paired_mask_decimal':str(theta),
            'root':top,'nonzero_couplings':[(a,b,v) for (a,b),v in sorted(J.items())]}

def main():
    st=time.monotonic();rng=random.Random(202610031900);digest=hashlib.sha256()
    allperm=0;allwords=0
    for n in (2,3):
        ranks=[([rank(x,n,k,top) for x in range(1<<n)],k,top)
            for k in range(1<<((1<<(n-1))-1)) for top in (0,1)]
        for p in permutations(range(1<<n)):
            lab=labels(p,n);allperm+=1
            for rs,k,top in ranks:
                R=segment_check(p,rs,lab,n);allwords+=1
                digest.update(bytes((n,k,top,R)))
    rows=[];hist=Counter()
    for n in range(2,5):
        for w in positive_chambers(n):
            for z in range(1<<n):
                signed=tuple(-a if z>>j&1 else a for j,a in enumerate(w))
                r=genuine_audit(signed);hist[(n,r['q'])]+=1;rows.append(r)
    for n in range(5,13):
        for _ in range(12):
            while True:
                w=tuple(rng.randrange(1,1<<18)*rng.choice((-1,1)) for j in range(n))
                if order_and_scores(w):break
            rows.append(genuine_audit(w,rng.getrandbits((1<<(n-1))-1),rng.randrange(2)))
    sharp=[]
    for n in range(2,14):
        for q in (0,1):
            m=q+1;d=n-m
            core=(1,) if q==0 else (1,2)
            w=tuple((1<<m)<<j for j in range(d))+core
            for root in (0,1):
                for variant in range(3):
                    theta=0 if variant==0 else (1<<((1<<(n-1))-1))-1 if variant==1 else rng.getrandbits((1<<(n-1))-1)
                    r=genuine_audit(w,theta,root)
                    assert r['q']==q and r['R']==((1<<n)-1 if q==0 else 1<<(n-1))
                    sharp.append(r)
    out={'status':'VERIFIED_UNIVERSAL_SEGMENT_SUPPORT_AND_SHARP_GENUINE_Q_ZERO_ONE',
        'analytic_theorems':['For every permutation and paired rank, each non-top raw label occurs at most twice within any monotonic rank run, root at most once; R>=ceil((N-1)/(2q+1)).',
        'For every centrally symmetric permutation, non-top support is invariant under complementary-prefix involution and J_Ca,Cb=kappa_a*kappa_b*J_ab. In particular root-to-next-highest coupling vanishes.',
        'For every genuine generic signed additive scan q=0 implies R=N-1; q=1 implies the unique non-top label is (n-2,0), all couplings vanish, R=(N+D)/2>=N/2 for EVERY paired rank. Both are attained in every dimension.'],
        'scope':'Elementary binary-trie accounting is standard, not renamed innovation. The application to exact raw support and sharp q=0,1 classification is the audited increment. General q growing with n and main M_n constant density remain OPEN.',
        'seed':202610031900,'all_arbitrary_permutations_q2_q3':allperm,
        'all_rank_mask_root_words':allwords,'permutation_audit_sha256':digest.hexdigest(),
        'small_dimension_histogram':{str(k):v for k,v in sorted(hist.items())},
        'genuine_scan_contexts':len(rows),'sharp_contexts':len(sharp),
        'rows':rows,'sharp_rows':sharp,'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    b=(json.dumps(out,indent=2)+'\n').encode()
    Path(__file__).with_name('tiny_raw_support_structure_certificate.json.gz').write_bytes(gzip.compress(b,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','sharp_rows')}),flush=True)
    print(json.dumps({'uncompressed_bytes':len(b),'uncompressed_sha256':hashlib.sha256(b).hexdigest()}),flush=True)

if __name__=='__main__':main()
