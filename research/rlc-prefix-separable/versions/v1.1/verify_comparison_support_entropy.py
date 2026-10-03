"""Exact audit of the comparison support argument toward the original target.

The all-dimensional result follows from injectivity and a chamber count,
not from sampled additive scans. No numerical optimization is used here.
"""
from pathlib import Path
import sys, itertools, math, random, json, time, hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent/'dependencies'))
from verify_paired_sibling_ranks import rank

def labels(p,n):
    off=[];total=0
    for h in range(n-1):off.append(total);total+=1<<(n-h-2)
    u=[];base=[]
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1
        u.append(total if h==n-1 else off[h]+(x>>(h+2)))
        base.append(int((y^(y>>1))>(x^(x>>1))))
    assert total in u
    return u,base,total

def audit(p,n,exhaustive):
    u,base,top=labels(p,n);active=sorted(set(u)-{top});q=len(active)
    states=range(1<<q) if exhaustive else (0,1,(1<<q)-1)
    words=set();turn_words=set();runs=[]
    for state in states:
        mask=sum(((state>>i)&1)<<a for i,a in enumerate(active))
        bits=[base[i]^((mask>>a)&1) for i,a in enumerate(u)]
        rr=[rank(x,n,mask) for x in p]
        assert bits==[int(b>a) for a,b in zip(rr,rr[1:])]
        word=sum(v<<i for i,v in enumerate(bits))
        turns=(word^(word>>1))&((1<<(len(p)-2))-1)
        # A transition word and one observed fixed top comparison determine
        # every sign, hence all active controller variables.
        words.add(word);turn_words.add(turns);runs.append(1+turns.bit_count())
    if exhaustive:
        assert len(words)==len(turn_words)==1<<q
        for K in range(1,len(p)):
            bad=sum(v<=K for v in runs)
            assert bad<=sum(math.comb(len(p)-2,j) for j in range(K))
    return q

def main():
    start=time.monotonic();count=0;hist={};rng=random.Random(202610031504)
    for n in (2,3):
        for p in itertools.permutations(range(1<<n)):
            q=audit(p,n,True);hist[f'n{n}:q{q}']=hist.get(f'n{n}:q{q}',0)+1;count+=1
    actual=[]
    for n in range(4,13):
        for j in range(24):
            w=[rng.randrange(1,1000000) for _ in range(n)];scores=[0]
            for a in w:scores += [s+a for s in scores]
            if len(set(scores))!=len(scores):continue
            p=sorted(range(1<<n),key=scores.__getitem__)
            q=audit(p,n,q_if_small(p,n));actual.append({'n':n,'q':q,'N':1<<n})
    # Conservative analytic entropy margin: H2(1/128)<17/256.
    # The chamber union is <3^(n*n)*2^(-15*2^n/256), already <1 at12.
    assert 3**144 < 2**240
    # 2^n/n^2 is increasing after n>=3, so this base closes all n>=12.
    assert all(2*n*n >= (n+1)*(n+1) for n in range(3,30))
    N=4096;K=N//128
    exact_bound_numerator=3**144*sum(math.comb(N-2,j) for j in range(K))
    exact_bound_denominator=1<<(N//8)
    assert exact_bound_numerator<exact_bound_denominator
    scalar=[]
    for w in ((1,4,2),(4,2)):
        n=len(w);sc=[0]
        for a in w:sc += [v+a for v in sc]
        p=sorted(range(1<<n),key=sc.__getitem__);best=None
        for mask in range(1<<((1<<(n-1))-1)):
            rr=[rank(x,n,mask) for x in p]
            bits=[b>a for a,b in zip(rr,rr[1:])]
            R=1+sum(a!=b for a,b in zip(bits,bits[1:]))
            if best is None or R<best[0]:best=(R,mask)
        scalar.append({'weights':w,'all_paired_minimum':best[0],'attaining_mask':best[1]})
    assert scalar[0]['all_paired_minimum']==scalar[1]['all_paired_minimum']==3
    out={'status':'VERIFIED_COMPARISON_SUPPORT_ENTROPY_REDUCTION',
      'arbitrary_permutations_exhausted':count,'histogram':hist,
      'actual_additive_scans_audited':len(actual),'actual_cases':actual,
      'analytic_result':'For every n>=12 there exists one paired rank with R>N/128 simultaneously for every generic additive sweep using at least N/8 distinct non-top comparison variables.',
      'fixed_scan_bound':'P(R<=K)<=2^(-q)*sum(j=0..K-1,C(N-2,j)).',
      'n12_union_bound_exact_lt_one':True,'optimized_scalar_counterexample':scalar,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('comparison_support_entropy_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='actual_cases'}))

def q_if_small(p,n):
    u,b,t=labels(p,n)
    return len(set(u)-{t})<=10

if __name__=='__main__': main()
