#!/usr/bin/env python3
"""Generic signed non-cardinality scans with disjoint score-window witnesses.

An all-n restricted scan-class theorem, NOT an all-weight RLC bound.
"""
from pathlib import Path
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs

def certify(w,start):
    n=len(w);N=1<<n;C=tuple(range(start,start+4));J=[j for j in range(n) if j not in C]
    A=w[start]-2
    assert A%32==0 and (w[start],w[start+1],w[start+3])==(A+2,A+4,A+16)
    c=w[start+2];assert c%32 in (15,17) and all(w[j]%32==0 for j in J)
    assert order_and_scores(tuple(w[j] for j in J)) is not None
    core=w[start:start+4];residues=[sum(core[j]*((x>>j)&1) for j in range(4))%32 for x in range(16)]
    assert len(set(residues))==16
    p,scores=order_and_scores(w);pos=[0]*N
    for i,x in enumerate(p):pos[x]=i
    chosen=[];owners={};digest=hashlib.sha256();foreign=0
    for f in range(1<<len(J)):
        base=sum(((f>>k)&1)<<j for k,j in enumerate(J));s=sum(w[j]*((base>>j)&1) for j in J)
        t=tuple(base|(x<<start) for x in (1,2,8));q=tuple(x^(4<<start) for x in t)
        ix=[pos[x] for x in t];iy=[pos[x] for x in q]
        assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
        # The proof uses disjoint full-score WINDOWS, not face ownership.
        S=set(range(ix[0]+1,ix[2]))|set(range(iy[0]+1,iy[2]))
        for i in S:
            assert s+A+2<scores[i]<s+A+16 or s+A+c+2<scores[i]<s+A+c+16
            assert i not in owners;owners[i]=f
            foreign+=(p[i]&~(15<<start))!=base
        chosen.append((t,q,S));digest.update(json.dumps((base,t,q,ix,iy,sorted(S))).encode())
    F=1<<(n-4);assert len(chosen)==F
    return p,chosen,{'n':n,'weights':w,'core_start':start,'A':A,'controller_weight':c,
        'core_subset_score_residues':residues,'disjoint_witnesses':F,
        'certified_ALL_paired_lower_bound':1+F,'occupied_turn_positions':len(owners),
        'foreign_face_turn_positions':foreign,'support_sha256':digest.hexdigest()}

def direct_audit(w,p,ws,mask,bound=None):
    n=len(w);v=[rank(x,n,mask) for x in range(1<<n)];word=[v[x] for x in p]
    turns={i for i in range(1,len(p)-1) if (word[i]-word[i-1])*(word[i+1]-word[i])<0}
    for t,q,S in ws:
        old=(v[t[1]]-v[t[0]])*(v[t[2]]-v[t[1]])
        new=(v[q[1]]-v[q[0]])*(v[q[2]]-v[q[1]])
        assert (old>0)!=(new>0) and turns&S
    R=fast_runs(v,p);assert R>= (1+len(ws) if bound is None else bound);return R

def same_phase_certify(w,start,size=4):
    n=len(w);C=tuple(range(start,start+size));J=[j for j in range(n) if j not in C]
    if size==4:i,j,k,controller=0,1,3,2
    else:
        assert size==5
        i,j=min(((i,j) for i,j in ((0,1),(0,2),(1,2)) if w[start+4]>max(w[start+i],w[start+j]) or w[start+4]<min(w[start+i],w[start+j])),key=lambda z:max(w[start+z[0]],w[start+z[1]],w[start+4])-min(w[start+z[0]],w[start+z[1]],w[start+4]))
        k=4;controller=j+1
    atomic=(w[start+i],w[start+j],w[start+k]);assert atomic[2]>max(atomic[:2]) or atomic[2]<min(atomic[:2])
    lo,hi=min(atomic),max(atomic);D=hi-lo
    op,os=order_and_scores(tuple(w[j] for j in J));assert len(os)==1 or min(y-x for x,y in zip(os,os[1:]))>D
    p,scores=order_and_scores(w);pos=[0]*len(p)
    for idx,x in enumerate(p):pos[x]=idx
    points=tuple(sorted((1<<i,1<<j,1<<k),key=lambda x:sum(w[start+t]*((x>>t)&1) for t in range(size))))
    ws=[];load={};digest=hashlib.sha256()
    for f in range(1<<len(J)):
        base=sum(((f>>k)&1)<<j for k,j in enumerate(J));s=sum(w[j]*((base>>j)&1) for j in J)
        t=tuple(base|(x<<start) for x in points);q=tuple(x^(1<<(start+controller)) for x in t)
        ix=[pos[x] for x in t];iy=[pos[x] for x in q]
        assert ix[0]<ix[1]<ix[2] and iy[0]<iy[1]<iy[2]
        S=set(range(ix[0]+1,ix[2]))|set(range(iy[0]+1,iy[2]))
        for idx in S:
            assert s+lo<scores[idx]<s+hi or s+w[start+controller]+lo<scores[idx]<s+w[start+controller]+hi
            load[idx]=load.get(idx,0)+1;assert load[idx]<=2
        ws.append((t,q,S));digest.update(json.dumps((base,t,q,ix,iy,sorted(S))).encode())
    F=len(ws);bound=1+(F+1)//2
    return p,ws,{'n':n,'weights':w,'core_start':start,'core_size':size,'atomic_coordinates':[start+i,start+j,start+k],'controller_coordinate':start+controller,'atomic_diameter':D,
        'outside_minimum_score_gap':min((y-x for x,y in zip(os,os[1:])),default=None),
        'witnesses':F,'maximum_union_support_load':max(load.values()),
        'half_weight_fractional_packing_scaled_objective':F,'packing_scale':2,
        'certified_ALL_paired_lower_bound':bound,'support_sha256':digest.hexdigest()}

def main():
    st=time.monotonic();rng=random.Random(202610031620);rows=[];checks=0;perturbations=0
    for n in range(4,14):
        for trial in range(6):
            start=rng.randrange(n-3);A=32*rng.randrange(-1000,1001);c=32*rng.randrange(-1000,1001)+(15 if trial%2 else 17)
            if trial==0:
                start=0;A=32;c=17;tail=tuple(32*(1<<j) for j in range(n-4))
            else:
                while True:
                    tail=tuple(32*rng.randrange(-100000,100001) for j in range(n-4))
                    if order_and_scores(tail) is not None:break
            w=tuple(tail[:start])+(A+2,A+4,c,A+16)+tuple(tail[start:]);p,ws,row=certify(w,start)
            masks=range(128) if n==4 else [rng.getrandbits((1<<(n-1))-1) for j in range(6)]
            runs=[]
            for mask in masks:runs.append(direct_audit(w,p,ws,mask));checks+=1
            row['rank_audit_minimum']=min(runs);row['rank_audits']=len(runs)
            # EXACT rational perturbation, with denominator larger than total
            # absolute numerators. All integer-base scan gaps are >=1.
            delta=[rng.randrange(-10,11) for j in range(n)];den=sum(abs(x) for x in delta)+1
            ww=tuple(den*x+d for x,d in zip(w,delta));pp,ss=order_and_scores(ww)
            assert tuple(pp)==tuple(p);perturbations+=1
            row['perturbation_numerators']=delta;row['perturbation_denominator']=den
            row['cardinality_primary_order']=all(x.bit_count()<=y.bit_count() for x,y in zip(p,p[1:]))
            rows.append(row)
    samephase=[];samechecks=0
    for n in range(4,14):
        for trial in range(4):
            if trial==0:
                start=0;core=(34,36,33,48);tail=tuple(32*(1<<j) for j in range(n-4))
            else:
                start=rng.randrange(n-3)
                while True:
                    atoms=tuple(2*rng.randrange(-7,8) for j in range(3));D=max(atoms)-min(atoms)
                    rr=[sum(atoms[j]*((x>>j)&1) for j in range(3))%32 for x in range(8)]
                    if len(set(rr))==8 and 0<D<32 and (atoms[2]>max(atoms[:2]) or atoms[2]<min(atoms[:2])):break
                c=32*rng.randrange(-1000,1001)+1;core=(atoms[0],atoms[1],c,atoms[2])
                while True:
                    tail=tuple(32*rng.randrange(-100000,100001) for j in range(n-4))
                    if order_and_scores(tail) is not None:break
            w=tuple(tail[:start])+core+tuple(tail[start:]);p,ws,row=same_phase_certify(w,start)
            if trial==0 and n>=5:assert row['maximum_union_support_load']==2
            row['rank_audit_runs']=[direct_audit(w,p,ws,rng.getrandbits((1<<(n-1))-1),row['certified_ALL_paired_lower_bound']) for j in range(6)]
            samechecks+=6;samephase.append(row)
    fivecases=[]
    for n in range(5,14):
        for trial in range(4):
            start=rng.randrange(n-4)
            while True:
                atoms=[r*(1 if rng.getrandbits(1) else -1) for r in (2,4,8,32)];rng.shuffle(atoms)
                if trial%2==0 or min(atoms[1:3])<atoms[3]<max(atoms[1:3]):break
            ctrl_unused=64*rng.randrange(-1000,1001)+16*(1 if rng.getrandbits(1) else -1)
            core=tuple(atoms[:3])+(ctrl_unused,atoms[3])
            while True:
                tail=tuple(64*rng.randrange(-100000,100001) for j in range(n-5))
                if order_and_scores(tail) is not None:break
            w=tuple(tail[:start])+core+tuple(tail[start:]);p,ws,row=same_phase_certify(w,start,5)
            row['rank_audit_runs']=[direct_audit(w,p,ws,rng.getrandbits((1<<(n-1))-1),row['certified_ALL_paired_lower_bound']) for j in range(6)]
            samechecks+=6;fivecases.append(row)
    out={'status':'VERIFIED_ALL_DIMENSION_SIGNED_SCORE_WINDOW_GRID_SCAN_CLASS',
        'analytic_theorem':'For ANY contiguous four INPUT coordinates a..a+3, actual atom weights(A+2,A+4,A+16), A divisible by32, controller weight congruent to15 or17 modulo32, and ANY signed outside weights divisible by32 with distinct outside subset scores, the whole scan is generic and EVERY paired rank has R>=1+2^(n-4), ALL n>=4. There is no cardinality-primary hypothesis or outside whole-face range separation. The same order and theorem hold under ANY weight perturbation of l1 norm<1.',
        'proof':'Each outside assignment supplies the ordered atomic triple(1,2,8)<<a and toggle(4<<a); leading comparison bits a+1,a+3 give opposite restricted turn products. Their full score windows have width14. Original window starts lie on32Z plus A+2; translated window starts lie on32Z plus A+c+2. Distinct same-phase starts differ by>=32; different-phase starts differ by>=15>14. Hence all2F windows are disjoint and supply F independent full turns. All16 core subset residues are distinct modulo32; outside subset offsets are distinct grid points, proving genericity. Full scan integer gaps>=1, so l1 perturbations<1 preserve the complete order.',
        'scope':'All-dimensional restricted arithmetic scan class and open neighborhoods, including negative weights, arbitrary outside priority, foreign-face interval vertices, and non-cardinality scans. NOT an all-weight RLC/M_n lower bound; known lexicographic and numerical-cardinality quarter theorems are not reclaimed.',
        'same_phase_theorem':'For ANY contiguous four input coordinates, highest atom weight extreme among the first, second and last, a generic actual signed complete scan, and outside subset-score gaps greater than the atomic diameter D, the original window family and the controller-translated window family are separately disjoint. No cross-phase gap or controller residue condition is needed. Union-support depth<=2 gives EVERY paired rank R>=1+ceil(2^(n-4)/2). The controller may be any weight consistent with full genericity. The explicit generic core(34,36,33,48) with outside32,64,... attains support depth2 for ALL n>=5, so the stronger disjoint-union assertion is false.',
        'five_core_corollary':'For ANY contiguous five input coordinates in a generic actual signed scan, choose a pair i<j among0,1,2 lying on the same side of atom4, with minimal valid three-atom diameter D. If outside subset-score gaps>D, original and translated window families are separately disjoint. EVERY paired rank has R>=1+ceil(2^(n-5)/2), ALL n>=5. No cardinality primary, fixed extreme-atom, controller range, or whole-face separation is assumed.',
        'actual_scan_cases':len(rows),'direct_rank_audits':checks,'exact_perturbation_order_audits':perturbations,
        'non_cardinality_scan_cases':sum(not r['cardinality_primary_order'] for r in rows),
        'cases_with_foreign_face_support':sum(bool(r['foreign_face_turn_positions']) for r in rows),
        'same_phase_cases':samephase,'five_core_cases':fivecases,'same_phase_direct_rank_audits':samechecks,
        'rows':rows,'seed':202610031620,'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('paired_score_window_grid_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','same_phase_cases','five_core_cases','proof')}),flush=True)

if __name__=='__main__':main()
