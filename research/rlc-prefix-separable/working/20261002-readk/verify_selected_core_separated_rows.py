#!/usr/bin/env python3
"""Selected five-bit core: exact all-dimensional row theorem stress checks."""
import hashlib,json,random,time
from pathlib import Path
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,counts
from verify_small_support_poset_obstruction import raw_support

SEED=202610031658
def check(v,u,nlowmask,root=0):
    assert root==0  # Complementing only the root is not a global rank complement.
    d=len(u);n=5+d;T=1<<d;N=1<<n
    core,vs=order_and_scores(v);outside,us=order_and_scores(u) if u else ((0,),(0,))
    S=sum(abs(a) for a in v)
    assert all(b-a>S for a,b in zip(us,us[1:]))
    w=u+v;p,scores=order_and_scores(w)
    expected=tuple((x<<d)|t for t in outside for x in core);assert p==expected
    delta=(1<<(n-1))-16;mask=(2<<delta)|nlowmask
    rr=[rank(x,n,mask,root) for x in p];R,C,a=counts(rr)
    crr=[rank(x,5,2,root) for x in core];Rc,Cc,ac=counts(crr)
    beta=int(ac[-2]!=ac[-1])+int(ac[-1]!=ac[0])
    assert Cc>=12 and C==T*Cc and R==T*Cc+1-beta and R>=12*T-1
    q,_=raw_support(p,n);qc,_=raw_support(core,5);assert len(q)==len(qc)<=15
    return {'n':n,'core_weights':v,'outside_weights':u,'lower_mask_hex':hex(nlowmask),
        'root':root,'core_cyclic':Cc,'core_linear':Rc,'beta':beta,'full_cyclic':C,'full_linear':R,
        'raw_q':len(q),'full_word_sha256':hashlib.sha256(json.dumps(rr).encode()).hexdigest()}

def main():
    st=time.monotonic();rng=random.Random(SEED);rows=[]
    cores=[(-1,12,-16,20,6),(1,6,-4,12,20),(8,1,16,6,20),(3,22,2,12,6)]
    while len(cores)<20:
        v=tuple(rng.choice((-1,1))*rng.randint(1,300) for _ in range(5))
        if order_and_scores(v):cores.append(v)
    for v in cores:
        L=sum(abs(a) for a in v)+1
        for d in range(0,8):
            if d:
                while True:
                    a=tuple(rng.choice((-1,1))*rng.randint(1,2000) for _ in range(d))
                    if order_and_scores(a):break
                u=tuple(L*x for x in a)
            else:u=()
            delta=(1<<(4+d))-16
            for low in [0,rng.getrandbits(delta)]:rows.append(check(v,u,low))
    sharp=[];v=(-1,12,-16,20,6);L=56
    for d in range(0,11):
        u=tuple(L*(1<<j) for j in range(d));delta=(1<<(4+d))-16
        r=check(v,u,rng.getrandbits(delta));assert r['full_linear']==12*(1<<d)-1
        sharp.append(r)
    out={'status':'VERIFIED_SELECTED_CORE_ROW_THEOREM',
        'analytic_statement':'Every normalized-root0 paired rank retaining upper five-bit core mask2 and arbitrary lower labels has C>=3N/8 and R>=3N/8-1 on every signed additive scan whose lower-coordinate subset-score gaps exceed the full signed five-core score diameter. Core weights are ANY generic signed weights, not a fixed example. Exact q is retained and at most15. The R lower bound is attained in every n>=5 by core(-1,12,-16,20,6) and lower binary score powers56*2^j. Global complementation of the entire rank also preserves the theorem; changing the root alone is excluded.',
        'scope':'Restricted scan class, not a lower bound on full all-scan RLC_n or M_n. Integer checks supplement the analytic inherited row identity and complete Q5 core certificate.',
        'seed':SEED,'cases':len(rows),'general_row_cases':rows,'all_n_sharp_audits':sharp,
        'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('selected_core_separated_rows_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('general_row_cases','all_n_sharp_audits')}),flush=True)

if __name__=='__main__':main()
