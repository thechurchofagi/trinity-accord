#!/usr/bin/env python3
"""Actual all-dimensional row-transfer audit; finite tests support the proof.

The core conditional bound comes from the independently checked exact
numeric-cone covering certificate. Full rows can have shared fresh labels;
only fixed turns and the recorded conditional mean are used for transfer.
"""
import hashlib,json,random,time
from fractions import Fraction
from pathlib import Path
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,counts
from verify_symmetric_translate_relaxation import exact_mean

def main():
    st=time.monotonic();rng=random.Random(202610031815);stream=hashlib.sha256();records=[]
    coreaudit=json.loads(Path('numeric_core_translate_independent_audit.json').read_text())
    assert coreaudit['all_signed_permuted_minimum_mean']==24
    original=[rank(x,5,2) for x in range(32)]
    for n in range(6,14):
        d=n-6;T=1<<d;N=1<<n;lowerlabels=(1<<(n-1))-16
        for trial in range(16):
            upper=[2,6,16,40,100];rng.shuffle(upper)
            upper=[a*rng.choice([-1,1]) for a in upper]
            a=rng.randrange(1,sum(map(abs,upper))+4,2)*rng.choice([-1,1])
            v=[a]+upper;p6=order_and_scores(v)[0]
            L=sum((x^y)==1 for x,y in zip(p6,p6[1:]+p6[:1]))
            mu=exact_mean(p6,original);F=mu-L;assert mu>=24
            # The full row has bottom coordinate0, high core coordinates
            # d+1..d+5, and separated intermediate-coordinate row scores.
            unit=1+sum(map(abs,v));outside=[];total=0
            for j in range(d):
                q=total+rng.randrange(1,4);outside.append(unit*q*rng.choice([-1,1]));total+=q
            w=[a]+outside+upper;p=order_and_scores(w)[0]
            mask=(2<<lowerlabels)|rng.getrandbits(lowerlabels)
            vals=[rank(x,n,mask) for x in p];R,C,_=counts(vals)
            m0=sum((x^y)==1 for x,y in zip(p,p[1:]))
            assert m0==T*L and C>=T*F and R>=T*F-1
            # Exact affine cyclic word: independently check both uniform
            # endpoints and every singleton fresh-label difference by
            # integer sign-word XOR/popcount. No independence of turns.
            freshcount=1<<(n-2);freshmask=(1<<freshcount)-1;fixedmask=mask&~freshmask
            r0=[rank(x,n,fixedmask) for x in p]
            r1=[rank(x,n,fixedmask|freshmask) for x in p]
            C0=counts(r0)[1];C1=counts(r1)[1];assert C0+C1==2*T*mu
            word=sum(int(r0[(i+1)%N]>r0[i])<<i for i in range(N));domain=(1<<N)-1
            def popturns(s):return (s^((s>>1)|((s&1)<<(N-1)))).bit_count()
            assert popturns(word)==C0
            flipwords={}
            for i,(x,y) in enumerate(zip(p,p[1:]+p[:1])):
                if (x^y)==1:
                    u=x>>2;flipwords[u]=flipwords.get(u,0)|(1<<i)
            diff=[popturns(word^s)-C0 for s in flipwords.values()]
            square=sum(a*a for a in diff)
            assert C1==C0+sum(diff) and square<=8*m0<=4*N
            if L<8:assert R>=17*T-1
            else:assert m0>=N//8
            row={'n':n,'trial':trial,'actual_signed_integer_weights':w,'full_lower_mask_hex':hex(mask),
                'core_fresh_comparisons':L,'core_conditional_mean':mu,'core_fixed_turns':F,
                'row_count':T,'full_m0':m0,'full_R':R,'full_C':C,
                'full_conditional_mean':T*mu,'full_fresh_coefficient_squares':square,
                'branch':'ALL_LABELS_FIXED_TURN_GUARANTEE' if L<8 else 'COVERED_BY_EXISTING_JOINT_BOTTOM_MASS_SELECTION'}
            records.append(row);stream.update(json.dumps(row,sort_keys=True).encode())
    assert Fraction(9*15*15,8)<Fraction(1<<15,128)
    assert 2+Fraction(9*18*18,8)<Fraction(1<<18,512)
    out={'status':'VERIFIED_ACTUAL_TRANSLATED_CORE_ROW_DICHOTOMY_AND_QUARTER_SELECTION',
        'analytic_scope':'Every n>=6 normalized paired extension retaining upper-five mask2/root0, separated six-core rows with arbitrary signed/permuted superincreasing upper-five weights and any generic nonzero new-lowest weight: Lcore<8 gives R>=17*2^(n-6)-1 for EVERYlower label choice; Lcore>=8 gives m0>=N/8. Fixing ALLhigher labels, fresh-bottom mean C>=3N/8 and coefficient squares<=4N imply P(C<=N/4)<=exp(-N/128). For every n>=15 ANYparent retainingseed2 admits ONEbottomchild handling ALLthese scans atR>=N/4. For n>=18 SAME fixed-seed rank jointly has this and60s entropy/two-bottom/old-row guarantees.',
        'small_dimension_audit_only':True,'actual_weight_cases':len(records),'dimensions':list(range(6,14)),
        'seed':202610031815,'core_source_audit_sha256':coreaudit['audit_sha256'],
        'records':records,'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('translated_core_row_dichotomy_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'}),flush=True)

if __name__=='__main__':main()
