#!/usr/bin/env python3
"""Exact audit of coherent prefix transport and capacity-qualified defects."""
import itertools,json,random,time,hashlib
from collections import defaultdict,Counter
from pathlib import Path
from verify_gray_face_merge_dp import signed_chambers
from verify_gray_reflection_graph import gray,graph,optimize,order_and_scores,counts

def scores(w):
    r=[0]
    for v in w:r += [s+v for s in r]
    return r

def check(a,b,full=False):
    n=len(a);N=1<<n;s=scores(a);u=scores(b)
    if len(set(zip(s,u)))<N:return None
    p=tuple(sorted(range(N),key=lambda x:(s[x],u[x])))
    L=1+sum(abs(v) for v in b);w=tuple(L*x+y for x,y in zip(a,b))
    assert order_and_scores(w)[0]==p
    pos={x:i for i,x in enumerate(p)}
    buckets=defaultdict(list)
    for x in p:buckets[s[x]].append(x)
    q=len(buckets);F=[];eligible_F=[];active=[]
    for m in range(n-1):
        f=0;qualified=0;cap=0
        for group in buckets.values():
            labels=[x>>(m+1) for x in group]
            frequency=Counter(labels)
            visits=Counter(x for j,x in enumerate(labels) if j==0 or x!=labels[j-1])
            f += sum(visits[x]-1 for x in frequency)
            qualified += sum(visits[x]-1 for x in frequency if frequency[x]>=3)
            cap=max(cap,max(frequency.values()))
        F.append(f);eligible_F.append(qualified);active.append(cap>=3)
    g=graph(p,n);O=[0]*(n-1);protected=defaultdict(int)
    orphans=defaultdict(int);boundary=defaultdict(int)
    for i in range(N):
        x,y,z=(p[(i+j)%N] for j in range(3))
        h,k=g['labels'][i],g['labels'][(i+1)%N]
        if h==k:continue
        key=tuple(sorted((h,k)));v=g['signs'][i]*g['signs'][(i+1)%N]
        interior=i<N-2 and s[x]==s[y]==s[z]
        if not interior:
            boundary[key]+=v;continue
        m=max(h,k)
        if m==n-1:
            translated=tuple(vv^(N-1) for vv in (z,y,x))
        else:
            translated=tuple(vv^(1<<(m+1)) for vv in (x,y,z))
        at=pos[translated[0]]
        kept=p[at:at+3]==translated
        assert len(set(s[vv] for vv in translated))==1
        e1=1 if gray(translated[1])>gray(translated[0]) else -1
        e2=1 if gray(translated[2])>gray(translated[1]) else -1
        assert e1*e2==-v
        if m==n-1:assert kept
        if kept:protected[key]+=v
        else:
            O[m]+=1;orphans[key]+=v
    assert all(v==0 for v in protected.values())
    assert all(o<=2*f for o,f in zip(O,eligible_F))
    assert all(flag or o==0 for flag,o in zip(active,O))
    qualified_F=sum(eligible_F)
    J={key:boundary[key]+orphans[key] for key in set(boundary)|set(orphans)}
    assert tuple((h,k,v) for (h,k),v in sorted(J.items()) if v)==g['edges']
    assert g['W']<=2*q+sum(O)<=2*q+2*qualified_F
    E,phi=optimize(g,n);minimum=(N+g['D']-E)//2
    assert 2*minimum>=N+g['D']-2*q-sum(O)
    if full:
        assert min(counts(tuple(gray(x^z) for x in p))[1] for z in range(N))==minimum
    return {'n':n,'q':q,'F':F,'eligible_F':eligible_F,'active':active,'orphans':O,
            'D':g['D'],'W':g['W'],'minimum_C':minimum}

def main():
    start=time.monotonic();records=[]
    # Every signed chamber of Q4, using zero primary scores. Completeness
    # is inherited from the previously audited Maclagan region count.
    _, chambers=signed_chambers(4)
    for b in chambers.values():records.append(check((0,)*4,b,True))
    for n in (2,3):
        for a in itertools.product(range(3),repeat=n):
            for base in itertools.permutations(1<<j for j in range(n)):
                for z in range(1<<n):
                    b=tuple(-v if z>>j&1 else v for j,v in enumerate(base))
                    records.append(check(a,b,True))
    rng=random.Random(202610030809)
    for n in range(5,11):
        for draw in range(40):
            a=tuple(rng.randrange(-2,4) for j in range(n))
            b=tuple(rng.randrange(-30,31)*(1<<(n+2))+(1<<j) for j in range(n))
            records.append(check(a,b,False))
    family=[]
    for n in range(3,15):
        b=(1,4,2)+tuple(1<<j for j in range(3,n))
        r=check((1,)*n,b,False)
        assert sum(r['orphans'])==0 and sum(r['eligible_F'])==0
        assert r['F'][1]==1<<(n-2)
        assert r['minimum_C']>=(1<<(n-1))-n-1
        family.append(r)
    broad=[]
    for n in range(5,13):
        for r in range(1,min(4,n-3)):
            d=n-r;m=d-1
            a=tuple(1<<j for j in range(m-1))+((1<<(m-1))-1,)+(1,)*(r+1)
            assert len(a)==n
            for trial in range(15):
                lower=tuple(rng.randrange(-30,31)*(1<<(d+2))+(1<<j) for j in range(d))
                b=list(lower)
                for j in range(d,n):
                    b.append((sum(abs(v) for v in b)+rng.randrange(1,10))*(-1 if rng.randrange(2) else 1))
                item=check(a,tuple(b),False)
                assert item is not None and sum(item['eligible_F'])==0 and sum(item['orphans'])==0
                assert item['q']==(1<<(d-1))+r
                assert item['minimum_C'] >= (1<<(n-1))-(1<<(d-1))-r
                broad.append(item)
    for n in range(3,10):
        for trial in range(20):
            b=list(rng.sample(range(-20,21),3))
            for j in range(3,n):
                b.append((sum(abs(v) for v in b)+rng.randrange(1,10))*(-1 if rng.randrange(2) else 1))
            item=check((1,)*n,tuple(b),False)
            assert item is not None and sum(item['eligible_F'])==0 and sum(item['orphans'])==0
            assert item['minimum_C'] >= (1<<(n-1))-n-1
            broad.append(item)
    records=[r for r in records if r]
    out={'status':'PASS','vectors':len(records),'vertex_entries':sum(1<<r['n'] for r in records),
         'orphan_triples':sum(sum(r['orphans']) for r in records),'violations':0,
         'all_Q4_signed_chambers':len(chambers),'nonlex_family':family,
         'broad_family_cases':len(broad),'broad_family_vertex_entries':sum(1<<r['n'] for r in broad),
         'deterministic_sha256':hashlib.sha256(json.dumps(records+family+broad,sort_keys=True).encode()).hexdigest(),
         'seconds':round(time.monotonic()-start,3),
         'scope':'Finite audits of the written transport theorem; no general RLC constant-density proof is claimed.'}
    Path(__file__).with_name('prefix_transport_defect_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({key:value for key,value in out.items() if key!='nonlex_family'},indent=2))
if __name__=='__main__':main()
