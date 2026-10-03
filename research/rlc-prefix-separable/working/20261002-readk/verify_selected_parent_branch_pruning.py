#!/usr/bin/env python3
"""All-n actual-weight upper certificates for five finite-optimal parents."""
import hashlib,json,random,time
from pathlib import Path
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,counts

SEED=202610031711
def main():
    st=time.monotonic();rng=random.Random(SEED);data=json.loads(Path('selected_parent_signed_random_certificate.json').read_text())
    bad=[r for r in data['rows'] if r['loss_below24']>0];assert len(bad)==5
    rows=[]
    for b in bad:
        m=b['parent_mask'];v=tuple(b['actual_signed_weights']);core,_=order_and_scores(v)
        assert all((x^y)!=1 for x,y in zip(core,core[1:]+core[:1]))
        Rc,Cc,a=counts([rank(x,6,m<<16) for x in core]);assert Cc==22
        beta=Cc-(Rc-1);assert beta in (0,1,2)
        for d in range(0,10):
            T=1<<d;n=6+d;N=1<<n;L=sum(abs(x) for x in v)+1
            w=tuple(L*(1<<j) for j in range(d))+v;p,_=order_and_scores(w)
            assert p==tuple((x<<d)|t for t in range(T) for x in core)
            delta=(1<<(n-1))-16
            for low in [0,rng.getrandbits(delta)]:
                mask=(m<<delta)|low;R,C,_=counts([rank(x,n,mask) for x in p])
                assert C==22*T and R==22*T+1-beta and R<=11*N//32+1
                assert all((x^y).bit_length()-1>=d+1 for x,y in zip(p,p[1:]+p[:1]))
                rows.append({'parent5_mask':m,'n':n,'core_signed_weights':v,'lower_high_score_base':L,
                    'lower_mask_hex':hex(low),
                    'random_lower_mask_sha256':hashlib.sha256(hex(low).encode()).hexdigest(),
                    'R':R,'C':C,'beta':beta})
    # Retain the root-only overclaim found during the positive row audit.
    v=(1,-14,-4,12,-20);p,_=order_and_scores(v)
    R,C,_=counts([rank(x,5,2,1) for x in p]);assert (R,C)==(10,10)
    out={'status':'VERIFIED_ALL_N_SELECTED_PARENT_BRANCH_CAP',
        'analytic_statement':'For each of parents48,100,118,137,155 with root0, EVERY paired extension retaining that fixed upper-five parent in EVERY n>=6 admits an explicit genuine signed additive scan with C=(11/32)N and R<=(11/32)N+1. The first extra low coordinate has no raw leading comparisons, and higher-score new low coordinates only repeat the same cyclic sign word. All lower labels are arbitrary. Consequently these finite-optimal seeds cannot support asymptotic density3/8; the original unspecified positive-density target is NOT refuted.',
        'scope':'Branch-specific upper bound only; not an upper bound on unrestricted M_n or all paired ranks. Inherited row identity is credited, new ingredient is a fixed-parent mean obstruction with ZERO fresh comparisons.',
        'seed':SEED,'five_optimal_parent_masks':[b['parent_mask'] for b in bad],
        'integer_audit_cases':len(rows),'rows':rows,
        'rejected_root_only_extension':{'n':5,'mask':2,'root':1,'actual_signed_weights':v,'R':R,'C':C,
            'correction':'The positive row theorem fixes root0, or globally complements ALL output bits and labels; changing the root alone is not a global rank complement.'},
        'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('selected_parent_branch_pruning_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
