#!/usr/bin/env python3
"""All-n/all-permutation/signed-secondary binary cardinality window bound.

Exact half-weight certificates, actual signed scans via reflection.
Main all-weight M_n target remains OPEN.
"""
from pathlib import Path
from itertools import combinations
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs

def certificate(b,B):
    n=len(b);assert sorted(abs(x) for x in b)==[1<<j for j in range(n)]
    assert B>2*sum(abs(x) for x in b);w=tuple(B+x for x in b)
    low=tuple(sorted(range(n),key=lambda j:abs(b[j]))[:5]);t=tuple(sorted(low));k=t[4]
    i,j=min(((i,j) for i,j in combinations(t[:3],2) if b[k]>max(b[i],b[j]) or b[k]<min(b[i],b[j])),key=lambda z:max(b[z[0]],b[z[1]],b[k])-min(b[z[0]],b[z[1]],b[k]))
    c=j+1;assert i<j and k>=j+2 and c not in (i,j,k)
    C=tuple(sorted(set(low)|{c}));J=tuple(j for j in range(n) if j not in C);assert len(C)<=6
    D=max(b[i],b[j],b[k])-min(b[i],b[j],b[k]);assert D<=24
    op,os=order_and_scores(tuple(w[a] for a in J));gap=min((y-x for x,y in zip(os,os[1:])),default=None)
    assert gap is None or gap>=32>D
    p,ss=order_and_scores(w);pos=[0]*len(p)
    for a,x in enumerate(p):pos[x]=a
    assert all(x.bit_count()<=y.bit_count() for x,y in zip(p,p[1:]))
    pts=tuple(1<<a for a in sorted((i,j,k),key=lambda a:w[a]));ws=[];loads={};digest=hashlib.sha256()
    for f in range(1<<len(J)):
        base=sum(((f>>a)&1)<<x for a,x in enumerate(J));v=tuple(base|x for x in pts);q=tuple(x^(1<<c) for x in v)
        ix=[pos[x] for x in v];iy=[pos[x] for x in q]
        assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
        S=set(range(ix[0]+1,ix[2]))|set(range(iy[0]+1,iy[2]))
        for a in S:loads[a]=loads.get(a,0)+1;assert loads[a]<=2
        ws.append((v,q,S));digest.update(json.dumps((base,v,q,ix,iy,sorted(S))).encode())
    F=len(ws);assert F==1<<(n-len(C));bound=1+(F+1)//2
    universal=1+((1<<n)+127)//128;assert bound>=universal
    return w,p,ws,{'n':n,'secondary':b,'primary_B':B,'positive_weights':w,
        'five_smallest_magnitude_input_coordinates':low,'atomic_coordinates':[i,j,k],
        'controller_coordinate':c,'free_coordinates':C,'outside_coordinates':J,
        'atomic_diameter':D,'outside_score_gap':gap,'witnesses':F,
        'maximum_union_support_load':max(loads.values()),'packing_scale':2,
        'scaled_fractional_packing_objective':F,'instance_ALL_paired_lower_bound':bound,
        'universal_ALL_paired_lower_bound':universal,'support_sha256':digest.hexdigest()}

def direct_audit(p,ws,n,mask,bound,reflection=0):
    values=[rank(x,n,mask) for x in range(1<<n)];pp=tuple(x^reflection for x in p)
    word=[values[x] for x in pp];turns={a for a in range(1,len(pp)-1) if (word[a]-word[a-1])*(word[a+1]-word[a])<0}
    for t,q,S in ws:
        t=tuple(x^reflection for x in t);q=tuple(x^reflection for x in q)
        old=(values[t[1]]-values[t[0]])*(values[t[2]]-values[t[1]])
        new=(values[q[1]]-values[q[0]])*(values[q[2]]-values[q[1]])
        assert (old>0)!=(new>0) and S&turns
    R=fast_runs(values,pp);assert R>=bound;return R

def main():
    st=time.monotonic();rng=random.Random(202610031700);rows=[];checks=0
    for n in range(5,16):
        for trial in range(8):
            secondary=[(1<<a)*(1 if rng.getrandbits(1) else -1) for a in range(n)];rng.shuffle(secondary)
            if trial==0:secondary=[1<<a for a in range(n)]
            if trial==1 and n>=10:
                # Five low-priority coordinates spread out in INPUT space;
                # every adjacent controller lies outside the five.
                low=[0,2,4,6,8];secondary=[0]*n
                for a,j in enumerate(low):secondary[j]=(1<<a)*(1 if rng.getrandbits(1) else -1)
                h=5
                for a in range(n):
                    if not secondary[a]:secondary[a]=1<<h;h+=1
            b=tuple(secondary);B=2*sum(abs(x) for x in b)+1+rng.randrange(0,1000)
            w,p,ws,row=certificate(b,B);runs=[];signed=[]
            for a in range(4):runs.append(direct_audit(p,ws,n,rng.getrandbits((1<<(n-1))-1),row['instance_ALL_paired_lower_bound']));checks+=1
            reflection=rng.randrange(1<<n);actual=tuple(x*(-1 if (reflection>>a)&1 else 1) for a,x in enumerate(w))
            pp,ss=order_and_scores(actual);assert tuple(pp)==tuple(x^reflection for x in p)
            for a in range(4):signed.append(direct_audit(p,ws,n,rng.getrandbits((1<<(n-1))-1),row['instance_ALL_paired_lower_bound'],reflection));checks+=1
            row['positive_scan_rank_audit_runs']=runs;row['actual_input_sign_reflection']=reflection
            row['actual_signed_weights']=actual;row['signed_scan_rank_audit_runs']=signed;rows.append(row)
    out={'status':'VERIFIED_ALL_DIMENSION_PERMUTED_SIGNED_BINARY_CARDINALITY_SCAN_CLASS',
        'analytic_theorem':'For ALL n>=5, secondary b_j=lambda*epsilon_j*2^(pi(j)) with arbitrary permutation pi and arbitrary signs epsilon, lambda>0, and B>2sum|b|, every paired rank on the genuine generic actual scan w_j=B+b_j satisfies R>=1+ceil(2^n/128). Arbitrary signs of the ACTUAL weights also satisfy the same bound by the inherited paired input-reflection closure.',
        'proof':'Take five smallest secondary magnitudes, sort their INPUT positions t0<...<t4, and use highest-input atom t4. Two among t0,t1,t2 lie on the same side of its secondary coefficient. Choose them i<j, and controller j+1. Since t3,t4 remain, t4>=j+2. Free set C contains the five low-priority coordinates plus controller, at most6. Atomic diameter<=24lambda. Outside coefficients have powers>=5; same-cardinality outside score differences are nonzero multiples32lambda. Different cardinalities have gap>B-sum_outside|b|>32lambda when outside is nonempty. Thus same-phase windows are disjoint; union depth<=2, one half-weight witness per outside assignment gives R>=1+ceil(2^(n-|C|)/2)>=1+ceil(2^n/128). Genericity and prefix separation are established analytically; no permutation enumeration is used as proof.',
        'scope':'A broad ALL-permutations/all-secondary-signs/all-dimensions scan-class theorem, but still binary secondary priorities with a cardinality primary. NOT all additive weights, NOT a new M_n general coefficient. Numerical-cardinality and signed-lexicographic quarter results remain prior results.',
        'actual_positive_scan_cases':len(rows),'actual_reflected_signed_scan_cases':len(rows),
        'direct_rank_audits':checks,'cases_requiring_six_free_coordinates':sum(len(r['free_coordinates'])==6 for r in rows),
        'rows':rows,'seed':202610031700,'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('permuted_signed_binary_cardinality_windows_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','proof')}),flush=True)

if __name__=='__main__':main()
