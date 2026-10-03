#!/usr/bin/env python3
"""Exact dual for interleaved fixed witnesses and adaptive four-block repair.

Analytic results for ALL dimensions in stated classes. Main M_n OPEN.
"""
from pathlib import Path
from math import comb
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs

def positions(p):
    pos=[0]*len(p)
    for i,x in enumerate(p):pos[x]=i
    return pos

def interval_witness(pos,t,q):
    ix=[pos[x] for x in t];iy=[pos[x] for x in q]
    assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
    return set(range(ix[0]+1,ix[2]))|set(range(iy[0]+1,iy[2]))

def fixed_dual(m):
    n=5+m;T=1<<m;b=tuple(T*(1<<j) for j in range(5))+tuple(1<<j for j in range(m))
    B=2*sum(b)+1;w=tuple(B+x for x in b);p,_=order_and_scores(w);pos=positions(p)
    dual=[pos[(((1<<l)-1)<<5)|x] for l in range(m+1) for x in (6,14)]
    assert len(set(dual))==2*(m+1) and all(1<=i<len(p)-1 for i in dual)
    digest=hashlib.sha256();chosen=[]
    # Do NOT materialize huge full interval sets for this audit: membership
    # inequalities suffice to check the scaled dual against every witness.
    for f in range(T):
        t=tuple((f<<5)|x for x in (3,5,17));q=tuple(x^8 for x in t)
        ix=[pos[x] for x in t];iy=[pos[x] for x in q];l=f.bit_count()
        assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
        assert ix[0]<dual[2*l]<ix[2] and iy[0]<dual[2*l+1]<iy[2]
        load=sum(ix[0]<i<ix[2] or iy[0]<i<iy[2] for i in dual)
        assert load>=2
        digest.update(json.dumps((f,ix,iy,load)).encode())
    # Alternating outer cardinalities give disjoint supports, so this exact
    # family's fractional packing is Theta(m), rather than merely <=m+1.
    occupied=set()
    for l in range(0,m+1,2):
        f=(1<<l)-1;t=tuple((f<<5)|x for x in (3,5,17));q=tuple(x^8 for x in t)
        S=interval_witness(pos,t,q);assert not(S&occupied);occupied|=S;chosen.append(f)
    peak=0;peak_vertex=None
    for l in range(1,m+1):
        v=(((1<<(l-1))-1)<<5)|13;i=pos[v];load=0
        for f in range(T):
            a=(f<<5)|3;c=(f<<5)|17;aa=a^8;cc=c^8
            load+=pos[a]<i<pos[c] or pos[aa]<i<pos[cc]
        assert load==comb(m,l)+comb(m,l-1)==comb(m+1,l)
        if load>peak:peak,peak_vertex=load,v
    return {'n':n,'m':m,'secondary':b,'primary_B':B,'weights':w,
        'fixed_witness_count':T,'dual_positions':dual,'dual_scaled_mass_per_position':1,
        'dual_scale':2,'fractional_packing_upper_bound':m+1,
        'disjoint_integer_packing_lower_bound':len(chosen),'chosen_outer_prefixes':chosen,
        'exact_peak_position_load':peak,'peak_vertex':peak_vertex,
        'witness_digest':digest.hexdigest()},w,p

def block_packing(b,start):
    n=len(b);C=tuple(range(start,start+4));core=tuple(b[j] for j in C)
    assert core[3]>max(core[:2]) or core[3]<min(core[:2])
    cs=[sum(core[j]*((x>>j)&1) for j in range(4)) for x in range(16)]
    assert all(len({cs[x] for x in range(16) if x.bit_count()==l})==comb(4,l) for l in range(5))
    J=[j for j in range(n) if j not in C];S=sum(abs(x) for x in core)
    op,os=order_and_scores(tuple(b[j] for j in J));assert len(os)==1 or min(y-x for x,y in zip(os,os[1:]))>S
    B=2*sum(abs(x) for x in b)+1;w=tuple(B+x for x in b);p,_=order_and_scores(w);pos=positions(p)
    points=tuple(sorted((1,2,8),key=lambda x:cs[x]));supports=[];occupied=set();digest=hashlib.sha256()
    for f in range(1<<len(J)):
        base=sum(((f>>k)&1)<<j for k,j in enumerate(J));t=tuple(base|(x<<start) for x in points);q=tuple(x^(4<<start) for x in t)
        supp=interval_witness(pos,t,q)
        assert all((p[i]&~(15<<start))==base for i in supp)
        assert not(supp&occupied);occupied|=supp;supports.append((t,q,supp))
        digest.update(json.dumps((base,t,q,sorted(supp))).encode())
    assert len(supports)==1<<(n-4)
    return {'n':n,'core_start':start,'secondary':b,'primary_B':B,'weights':w,
        'disjoint_witnesses':len(supports),'certified_ALL_paired_lower_bound':1+len(supports),
        'occupied_turn_positions':len(occupied),'witness_digest':digest.hexdigest()},w,p,supports

def audit_ranks(w,p,ws,rng,repeats):
    n=len(w);out=[]
    for _ in range(repeats):
        mask=rng.getrandbits((1<<(n-1))-1);v=[rank(x,n,mask) for x in range(1<<n)]
        word=[v[x] for x in p];turns={i for i in range(1,len(p)-1) if (word[i]-word[i-1])*(word[i+1]-word[i])<0}
        for t,q,S in ws:
            old=(v[t[1]]-v[t[0]])*(v[t[2]]-v[t[1]])
            new=(v[q[1]]-v[q[0]])*(v[q[2]]-v[q[1]])
            assert (old>0)!=(new>0) and S&turns
        R=fast_runs(v,p);assert R>=1+len(ws);out.append(R)
    return out

def arbitrary_five_block(b,start):
    n=len(b);core=b[start:start+5];cs=[sum(core[j]*((x>>j)&1) for j in range(5)) for x in range(32)]
    assert all(len({cs[x] for x in range(32) if x.bit_count()==l})==comb(5,l) for l in range(6))
    # Among three distinct numbers at least two lie on the same side of
    # a fourth. This is the entire adaptive-atom existence proof.
    i,j=next((i,j) for i,j in ((0,1),(0,2),(1,2)) if core[4]>max(core[i],core[j]) or core[4]<min(core[i],core[j]))
    assert j+2<=4 and j+1 not in (i,j,4)
    J=[k for k in range(n) if not start<=k<start+5];S=sum(abs(x) for x in core)
    op,os=order_and_scores(tuple(b[k] for k in J));assert len(os)==1 or min(y-x for x,y in zip(os,os[1:]))>S
    B=2*sum(abs(x) for x in b)+1;w=tuple(B+x for x in b);p,_=order_and_scores(w);pos=positions(p)
    points=tuple(sorted((1<<i,1<<j,16),key=lambda x:cs[x]));occupied=set();ws=[];digest=hashlib.sha256()
    for f in range(1<<len(J)):
        base=sum(((f>>k)&1)<<a for k,a in enumerate(J));t=tuple(base|(x<<start) for x in points);q=tuple(x^(1<<(start+j+1)) for x in t)
        supp=interval_witness(pos,t,q)
        assert all((p[k]&~(31<<start))==base for k in supp) and not(supp&occupied)
        occupied|=supp;ws.append((t,q,supp));digest.update(json.dumps((base,t,q,sorted(supp))).encode())
    return {'n':n,'core_start':start,'secondary':b,'weights':w,'primary_B':B,
        'selected_atom_coordinates':[start+i,start+j,start+4],'controller_coordinate':start+j+1,
        'old_fixed_atom_extreme_hypothesis':core[4]>max(core[1:3]) or core[4]<min(core[1:3]),
        'disjoint_witnesses':len(ws),'certified_ALL_paired_lower_bound':1+len(ws),'witness_digest':digest.hexdigest()},w,p,ws

def main():
    st=time.monotonic();rng=random.Random(202610031535);negative=[];repair=[];cases=[];checks=0
    for m in range(0,12):
        row,w,p=fixed_dual(m);negative.append(row)
        if m>=4:
            rr,ww,pp,ws=block_packing(row['secondary'],5);assert pp==p and ww==w
            rr['rank_audit_runs']=audit_ranks(ww,pp,ws,rng,4);checks+=4;repair.append(rr)
    for n in range(4,13):
        for trial in range(4):
            start=rng.randrange(n-3)
            while True:
                core=tuple(rng.randrange(-100,101) for _ in range(4))
                cs=[sum(core[j]*((x>>j)&1) for j in range(4)) for x in range(16)]
                if (core[3]>max(core[:2]) or core[3]<min(core[:2])) and all(len({cs[x] for x in range(16) if x.bit_count()==l})==comb(4,l) for l in range(5)):break
            L=sum(abs(x) for x in core)+1;tail=[L*(1<<j)*(1 if rng.getrandbits(1) else -1) for j in range(n-4)];rng.shuffle(tail)
            b=tuple(tail[:start])+core+tuple(tail[start:]);rr,w,p,ws=block_packing(b,start)
            rr['rank_audit_runs']=audit_ranks(w,p,ws,rng,4);checks+=4;cases.append(rr)
    general5=[]
    for n in range(5,14):
        for trial in range(4):
            start=rng.randrange(n-4)
            while True:
                core=tuple(rng.randrange(-100,101) for _ in range(5));cs=[sum(core[j]*((x>>j)&1) for j in range(5)) for x in range(32)]
                if all(len({cs[x] for x in range(32) if x.bit_count()==l})==comb(5,l) for l in range(6)) and (trial%2==0 or min(core[1:3])<core[4]<max(core[1:3])):break
            L=sum(abs(x) for x in core)+1;tail=[L*(1<<j)*(1 if rng.getrandbits(1) else -1) for j in range(n-5)];rng.shuffle(tail)
            b=tuple(tail[:start])+core+tuple(tail[start:]);row,w,p,ws=arbitrary_five_block(b,start)
            row['rank_audit_runs']=audit_ranks(w,p,ws,rng,4);checks+=4;general5.append(row)
    out={'status':'VERIFIED_INTERLEAVED_FIXED_WITNESS_OBSTRUCTION_AND_ADAPTIVE_FOUR_BLOCK_REPAIR',
        'fixed_family_theorem':'For n=5+m, secondary b=(2^m,2^(m+1),...,2^(m+4),1,2,...,2^(m-1)) and primary B>2sum|b|, the per-prefix(3,5,17)/(11,13,25) interval-witness family has optimum fractional packing between ceil((m+1)/2) and m+1. Exact dual half mass at core6 and14 with each canonical outer cardinality. Some single-position load equals binomial(m+1,l), excluding bounded overlap. No all-weight RLC or M_n upper bound follows.',
        'repair_theorem':'For ANY contiguous four-input-coordinate block with generic within-cardinality secondary scores and last secondary coefficient extreme among the first, second and last, and outer secondary subset gaps exceeding sum absolute core coefficients, cardinality-primary actual scans have R>=1+2^(n-4) for EVERY paired rank, ALL n>=4. In the adverse fixed-family examples use block5..8 for n>=9; the SAME scan order thus has a different integer witness packing of size2^(n-4).',
        'arbitrary_five_core_theorem':'For ANY contiguous five-input-coordinate block with generic within-cardinality secondary scores, at least two of b0,b1,b2 lie on the same side of b4. Choose those atoms i<j and atom4, and toggle controller j+1. With outer secondary subset gaps exceeding sum absolute core coefficients, this gives R>=1+2^(n-5) for EVERY paired rank, ALL n>=5. No fixed atom-extreme hypothesis remains.',
        'scope':'Analytic restricted scan-class results. No finite dimension extrapolation; main constant-density all-weight problem remains OPEN.',
        'negative_rows':negative,'adverse_scan_repairs':repair,'arbitrary_block_cases':cases,'arbitrary_five_core_cases':general5,
        'direct_rank_audits':checks,'seed':202610031535,'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('interleaved_exchange_adaptive_blocks_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('negative_rows','adverse_scan_repairs','arbitrary_block_cases','arbitrary_five_core_cases')}),flush=True)

if __name__=='__main__':main()
