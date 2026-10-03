"""Exact audit of a conditional, compatible paired rank extension lemma.

All Q2-Q4 signed chambers, every fixed upper mask and every fresh bottom mask
are checked directly. No concentration bound is inferred from enumeration.
"""
from pathlib import Path
from fractions import Fraction
import sys,json,time,hashlib,math
sys.path.insert(0,str(Path(__file__).resolve().parent/'dependencies'))
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import positive_chambers,order_and_scores

def table(p,n,parent):
    fresh=1<<(n-2);mask=parent<<fresh
    values=[rank(x,n,mask) for x in range(1<<n)]
    comps=[];L=0
    for x,y in zip(p,p[1:]):
        sign=int(values[y]>values[x])
        if x^y==1:comps.append((x>>2,sign));L+=1
        else:comps.append((None,sign))
    costs=[[0,0] for _ in range(fresh)];constant=1
    for (u,a),(v,b) in zip(comps,comps[1:]):
        assert u is None or v is None
        if u is None and v is None:constant+=int(a!=b)
        else:
            i=u if u is not None else v
            costs[i][0]+=int(a!=b);costs[i][1]+=int(a==b)
    k=[sum(z) for z in costs]
    e=int(comps[0][0] is not None)+int(comps[-1][0] is not None)
    assert sum(k)==2*L-e and max(k,default=0)<=4
    expectation=Fraction(constant)+sum(Fraction(v,2) for v in k)
    assert expectation>=L
    assert sum((a-b)**2 for a,b in costs)<=4*sum(k)<=8*L
    return L,e,constant,costs

def main():
    start=time.monotonic();cases=0;states=0;hist={};examples=[]
    for n in (2,3,4):
        N=1<<n;fresh=1<<(n-2)
        ranks=[[rank(x,n,mask) for x in range(N)] for mask in range(1<<((1<<(n-1))-1))]
        parent_count=1<<((1<<(n-2))-1)
        for w in positive_chambers(n):
            order=order_and_scores(w)[0]
            for z in range(N):
                p=tuple(x^z for x in order)
                for parent in range(parent_count):
                    L,e,c,costs=table(p,n,parent);runs=[]
                    for low in range(1<<fresh):
                        vals=ranks[(parent<<fresh)|low]
                        signs=[vals[b]>vals[a] for a,b in zip(p,p[1:])]
                        R=1+sum(a!=b for a,b in zip(signs,signs[1:]))
                        predicted=c+sum(costs[i][(low>>i)&1] for i in range(fresh))
                        assert R==predicted;runs.append(R);states+=1
                    assert Fraction(sum(runs),len(runs))==Fraction(c)+sum(Fraction(sum(v),2) for v in costs)
                    cases+=1;hist[str(L)]=hist.get(str(L),0)+1
                    if len(examples)<24:examples.append({'n':n,'weights':w,'reflection':z,'parent_mask':parent,'L':L,'endpoint_occurrences':e,'constant':c,'costs':costs,'R_distribution':runs})
    # ln3<9/8 because the first five positive terms of exp(9/8)>3.
    x=Fraction(9,8);lower=sum(x**i/math.factorial(i) for i in range(5))
    assert lower>3
    assert Fraction(1<<15,128)>Fraction(9*15*15,8)
    assert all(2*n*n>(n+1)*(n+1) for n in range(3,40))
    out={'status':'VERIFIED_COMPATIBLE_BOTTOM_EXTENSION_CONCENTRATION',
      'fixed_upper_chamber_contexts':cases,'all_fresh_states_checked':states,
      'coverage':'ALL signed generic Q2-Q4 chambers, EVERY normalized fixed parent rank and EVERY fresh bottom assignment; completeness inherited from the previously certified chamber generator.',
      'L_histogram':hist,'examples':examples,
      'analytic_identity':'Conditional on ANY parent, R=C0+sum_u Y_u(theta_u),Y_u(0)+Y_u(1)=k_u<=4,sum k=2L-e,E R>=L,sum A_u^2<=8L.',
      'analytic_tail':'For any vertex permutation and ANY fixed parent, P_fresh(R<=L/2)<=exp(-L/16), by cosh(z)<=exp(z^2/2).',
      'simultaneous_extension':'For ALL n>=15 and ANY fixed paired parent, there is a child preserving it with R>N/16 for EVERY generic signed additive sweep having L>=N/8 lowest-input-bit comparisons.',
      'infinite_compatible_family':'Choosing one such extension at each n>=15 gives a single compatible family. Its lifts of ANY d>=15 core with L_core>=2^d/8 have R>=2^n/16-1 even when q(lift)/2^n tends to0.',
      'original_target':'OPEN; scans with few fresh bottom edges and arbitrary multilevel interleavings are not covered.',
      'n15_chamber_union_margin_positive':True,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('bottom_extension_concentration_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('examples','L_histogram')}))

if __name__=='__main__':main()
