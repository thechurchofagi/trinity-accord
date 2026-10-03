"""Exact sparse-support amplification and paired cyclic minimax audits.

Only Python standard library. Inherited Q1-Q4 chamber representatives are
reused; their previously certified completeness is not inferred from sampling.
"""
from pathlib import Path
import sys,itertools,random,json,time,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent/'dependencies'))
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,positive_chambers

def statistics(values,p):
    signs=[values[b]>values[a] for a,b in zip(p,p[1:])]
    b=values[p[0]]>values[p[-1]]
    B=int(signs[0]!=b)+int(signs[-1]!=b)
    R=1+sum(a!=z for a,z in zip(signs,signs[1:]))
    return R,R-1+B,B

def raw_support(p,n):
    offsets=[(1<<(n-1))-(1<<(n-h-1)) for h in range(n-1)]
    out=set()
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1
        if h<n-1:out.add(offsets[h]+(x>>(h+2)))
    return out

def embedded_values(d,m,coremask,lowmask):
    n=d+m;T=1<<m;D=1<<d;shift=(1<<(n-1))-(1<<(d-1))
    whole=(coremask<<shift)|lowmask
    core=[rank(u,d,coremask) for u in range(D)]
    if m==0:return core,whole
    local=[]
    for u in range(D):
        lm=0;loff=0
        for h in range(m-1):
            width=1<<(m-h-2);goff=(1<<(n-1))-(1<<(n-h-1))
            lm|=((lowmask>>(goff+u*width))&((1<<width)-1))<<loff
            loff+=width
        goff=(1<<(n-1))-(1<<d)
        top=(u&1)^((lowmask>>(goff+(u>>1)))&1)
        local.append([rank(t,m,lm,top) for t in range(T)])
    return [T*core[x>>m]+local[x>>m][x&(T-1)] for x in range(D*T)],whole

def actual_lift(w,m,mask,rng):
    d=len(w);n=d+m;D=1<<d;T=1<<m;H=1+sum(abs(a) for a in w)
    fullw=tuple(H*(1<<j) for j in range(m))+tuple(w)
    cp,cs=order_and_scores(w);p,sc=order_and_scores(fullw)
    assert p==tuple((u<<m)|t for t in range(T) for u in cp)
    shift=(1<<(n-1))-(1<<(d-1));low=rng.getrandbits(shift)
    values,whole=embedded_values(d,m,mask,low)
    assert sorted(values)==list(range(D*T))
    probes=range(D*T) if n<=10 else [rng.randrange(D*T) for _ in range(2048)]
    for x in probes:assert values[x]==rank(x,n,whole)
    cr=[rank(u,d,mask) for u in range(D)]
    R,C,B=statistics(cr,cp);rr,cc,bb=statistics(values,p)
    assert bb==B and cc==T*C and rr==T*C-B+1
    q=raw_support(cp,d);qq=raw_support(p,n)
    assert qq=={u+shift for u in q}
    return {'core_weights':w,'d':d,'m':m,'N':D*T,'q_core':len(q),
      'q_full':len(qq),'core_R':R,'core_C':C,'B':B,'full_R':rr,'full_C':cc,
      'rank_bit_checks':'every vertex' if n<=10 else '2048 seeded vertices',
      'all_score_rank_comparisons_checked':True}

def finite_minimax(n):
    N=1<<n;nr=1<<((1<<(n-1))-1)
    values=[[rank(x,n,mask) for x in range(N)] for mask in range(nr)]
    minima=[N]*nr;witness=[None]*nr;orders=0
    for w in positive_chambers(n):
        pp=order_and_scores(w)[0]
        for z in range(N):
            p=tuple(x^z for x in pp);orders+=1
            for mask,vals in enumerate(values):
                R,C,B=statistics(vals,p)
                if C<minima[mask]:
                    minima[mask]=C;witness[mask]={'weights':[a*(-1 if z>>h&1 else 1) for h,a in enumerate(w)],'C':C,'R':R}
    maximum=max(minima);opts=[i for i,a in enumerate(minima) if a==maximum]
    assert maximum=={1:2,2:2,3:4,4:6}[n]
    return {'n':n,'normalized_masks':nr,'signed_chambers':orders,
      'complete_cyclic_maxmin':maximum,'density':f'{maximum}/{N}',
      'optimal_masks':opts,'minima':minima,'worst_weight_witnesses':witness}

def gray_poset_core(d):
    """Prior antipodal core, reused only for the sparse-support diagnostic."""
    D=1<<d;gray=lambda x:x^(x>>1);first=[]
    for weight in range(d-2):
        prefix=[];suffix=[]
        for y in range(1<<(d-3)):
            if y.bit_count()!=weight:continue
            v=[(y<<2)|j for j in range(4)]
            sg=[gray(v[i+1])>gray(v[i]) for i in range(3)]
            j=next(i for i in (1,2) if sg[i]!=sg[0])
            assert sg[0] and not sg[-1]
            prefix+=v[:j+1];suffix+=v[j+1:]
        first+=sorted(prefix,key=gray)+sorted(suffix,key=gray,reverse=True)
    p=tuple(first+[x^(D-1) for x in reversed(first)])
    vals=[gray(x) for x in range(D)];R,C,B=statistics(vals,p)
    assert R==C==4*d-8 and B==1
    pos={x:i for i,x in enumerate(p)}
    assert pos[4]<pos[8] and pos[11]<pos[7]
    return p

def fake_lift(d,m,rng):
    n=d+m;D=1<<d;T=1<<m;cp=gray_poset_core(d)
    p=tuple((u<<m)|t for t in range(T) for u in cp)
    shift=(1<<(n-1))-(1<<(d-1));values,whole=embedded_values(d,m,0,rng.getrandbits(shift))
    R,C,B=statistics(values,p)
    assert R==C==T*(4*d-8)
    assert all(p[i]^p[-1-i]==(1<<n)-1 for i in range(1<<n))
    pos=[0]*(1<<n)
    for i,x in enumerate(p):pos[x]=i
    for x in range(1<<n):
        for j in range(n):
            if not(x>>j&1):assert pos[x]<pos[x|(1<<j)]
    q=raw_support(cp,d);qq=raw_support(p,n);assert qq=={x+shift for x in q}
    for a,b in ((4,8),(11,7)):assert pos[a<<m]<pos[b<<m]
    return {'d':d,'m':m,'N':D*T,'q':len(qq),'R':R,'C':C,
      'antipodal':True,'all_positive_coordinate_edges_checked':n*D*T//2,
      'nonadditive_requirements':[f'w_{m+2}<w_{m+3}',f'w_{m+3}<w_{m+2}']}

def main():
    start=time.monotonic();rng=random.Random(202610031545)
    cores=[]
    for d in range(2,10):
        for k in range(3):
            while True:
                w=tuple(rng.randrange(1,100000)*rng.choice((-1,1)) for _ in range(d))
                if order_and_scores(w) is not None:break
            cores.append((w,rng.getrandbits((1<<(d-1))-1)))
    cores += [((1,2,4),0),((1,6,8,4),8),((65,66,68,72,80),0)]
    lifted=[actual_lift(w,m,mask,rng) for w,mask in cores for m in (0,1,3,6)]
    minimax=[finite_minimax(n) for n in range(1,5)]
    fake=[fake_lift(d,m,rng) for d in range(5,11) for m in (1,4)]
    out={'status':'VERIFIED_SPARSE_SUPPORT_AMPLIFICATION_AND_QUANTIFIER_REDUCTION',
      'seed':202610031545,'actual_lift_cases':len(lifted),'actual_lifts':lifted,
      'finite_complete_cyclic_minimax':minimax,'nonadditive_diagnostics':fake,
      'analytic_identity':'q(lift)=q(core),C(lift)=2^m*C(core),R(lift)=2^m*C(core)-B+1;B in{0,1,2}. Every lower paired completion allowed.',
      'scope':'Original all-weight M_n target remains OPEN. Support-defect inequality for EVERY paired rank is equivalent up to constants to a universal paired constant-density theorem, not merely a sparse easy case. The poset diagnostics are explicitly NONADDITIVE.',
      'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('sparse_support_amplification_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('actual_lifts','finite_complete_cyclic_minimax','nonadditive_diagnostics')}))

if __name__=='__main__':main()
