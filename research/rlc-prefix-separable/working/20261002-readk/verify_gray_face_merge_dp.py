#!/usr/bin/env python3
"""Exact reflected face-merge DP; finite Gray Q5 optimum and hierarchy exclusion.

Standard library only. Q4 chamber completeness depends on Maclagan, section 4,
chi_H4(x)=(x-1)(x-11)(x-13)(x-15), and the region formula stated there.
No dimension-independent lower bound is claimed.
"""
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json
import time

HIERARCHY_WITNESS = (
    7,6,5,15,14,23,22,21,39,38,37,47,46,3,4,13,
    31,30,19,20,55,54,53,35,36,45,29,2,63,62,51,52,
    11,12,1,0,61,34,18,27,28,10,9,8,43,44,33,32,
    50,59,60,17,16,26,25,24,42,41,40,49,48,58,57,56)

def gray(x):
    return x ^ (x >> 1)

def order(weights):
    scores=[0]
    for w in weights:
        scores += [s+w for s in scores]
    if len(set(scores)) != len(scores):
        return None
    return tuple(sorted(range(len(scores)),key=scores.__getitem__))

def statistics(values):
    e=[1 if b>a else -1 for a,b in zip(values,values[1:])]
    linear=1+sum(a!=b for a,b in zip(e,e[1:]))
    close=1 if values[0]>values[-1] else -1
    cyclic=(linear-1)+int(e[-1]!=close)+int(close!=e[0])
    return linear,cyclic

def signed_chambers(d):
    if d==1:
        reps=[(1,)]
    elif d==2:
        reps=[(1,2)]
    elif d==3:
        reps=[(1,2,4),(2,3,4)]
    elif d==4:
        base={}
        for w in combinations(range(1,13),4):
            p=order(w)
            if p is not None:base.setdefault(p,w)
        assert len(base)==14
        reps=sorted(base.values())
    else:
        raise ValueError('No chamber completeness claim beyond Q4')
    result={}
    for seed in reps:
        for v in permutations(seed):
            for z in range(1<<d):
                w=tuple(-a if (z>>j)&1 else a for j,a in enumerate(v))
                p=order(w)
                assert p is not None
                result.setdefault(p,w)
    assert len(result)=={1:2,2:8,3:96,4:5376}[d]
    return reps,result

def merge_order(parent,word):
    L=len(parent)
    idx=[0,0];result=[]
    for b in map(int,word):
        result.append(parent[idx[b]]+b*L)
        idx[b]+=1
    assert idx==[L,L]
    return tuple(result)

def merge_words(L):
    def visit(i,j,prefix):
        if i+j==L:
            yield prefix+''.join(str(1-int(b)) for b in reversed(prefix))
            return
        yield from visit(i+1,j,prefix+'0')
        if j<i:
            yield from visit(i,j+1,prefix+'1')
    yield from visit(0,0,'')

def validate_parent(parent):
    L=len(parent)
    assert L>=2 and L&(L-1)==0
    assert set(parent)==set(range(L))
    assert all(parent[-1-i]==(parent[i]^(L-1)) for i in range(L))

def dp(parent,linear=False,path=False):
    """Minimum over all centrally symmetric ordered Dyck merges, NOT all weights.

    State (i,j,u,v): used lower/upper counts and last two layer bits.
    Paired homogeneous triples cost twice the parent turn; alternating triples
    cost 2; other mixed triples cost 1. Each end adds 1 plus its switch flag.
    For linear cost, the first switch flag is removed exactly.
    """
    validate_parent(parent)
    L=len(parent);A=tuple(map(gray,parent));B=tuple(L+a for a in reversed(A))
    cur={(2,0,0,0):0,(1,1,0,1):0 if linear else 1}
    previous={}
    for length in range(2,L):
        nxt={}
        for state,cost in sorted(cur.items()):
            i,j,u,v=state
            for b in (0,1):
                ni,nj=i+int(b==0),j+int(b==1)
                if ni<nj:continue
                if u==v==b:
                    arr=A if b==0 else B;k=i if b==0 else j
                    delta=2*int((arr[k-1]-arr[k-2])*(arr[k]-arr[k-1])<0)
                else:
                    delta=2 if u==b else 1
                key=(ni,nj,v,b);value=cost+delta
                if key not in nxt or value<nxt[key]:
                    nxt[key]=value
                    if path:previous[key]=state
        cur=nxt
    value,state=min((cost+2+int(u!=v),state)
        for state,cost in cur.items() for i,j,u,v in [state])
    if not path:return value
    rev=[];key=state
    while key[0]+key[1]>2:
        rev.append(str(key[3]));key=previous[key]
    prefix=str(key[2])+str(key[3])+''.join(reversed(rev))
    assert len(prefix)==L
    word=prefix+''.join(str(1-int(b)) for b in reversed(prefix))
    child=merge_order(parent,word)
    assert statistics(tuple(map(gray,child)))[0 if linear else 1]==value
    return value,word,child

def paired_formula(parent,word,linear=False):
    L=len(parent);A=tuple(map(gray,parent));B=tuple(L+a for a in reversed(A))
    half=tuple(map(int,word[:L]));i=j=0;cost=0
    values=[]
    for b in half:
        values.append((A if b==0 else B)[i if b==0 else j])
        i+=int(b==0);j+=int(b==1)
    for k in range(L-2):
        u,v,b=half[k:k+3]
        if u==v==b:
            cost+=2*int((values[k+1]-values[k])*(values[k+2]-values[k+1])<0)
        else:cost+=2 if u==b else 1
    return cost+2+int(half[-2]!=half[-1])+(0 if linear else int(half[0]!=half[1]))

def verify_hierarchy(p):
    d=(len(p)).bit_length()-1
    q=p;levels=[]
    while d:
        L=1<<(d-1);lo=tuple(x for x in q if x<L);hi=tuple(x-L for x in q if x>=L)
        assert lo==hi
        assert all(q[-1-i]==(q[i]^((1<<d)-1)) for i in range(1<<d))
        levels.append({'dimension':d,'R_C':statistics(tuple(map(gray,q)))})
        q=lo;d-=1
    return levels

def main():
    start=time.monotonic();digest=hashlib.sha256();brute_cases=0
    # Independent exhaustive traversal of all half Dyck words: no DP pruning.
    for d in (1,2,3):
        _,parents=signed_chambers(d);words=list(merge_words(1<<d))
        assert len(words)=={1:2,2:6,3:70}[d]
        for p in sorted(parents):
            minimum=[1<<(d+1),1<<(d+1)]
            for word in words:
                child=merge_order(p,word);actual=statistics(tuple(map(gray,child)))
                assert paired_formula(p,word,True)==actual[0]
                assert paired_formula(p,word,False)==actual[1]
                minimum=[min(a,b) for a,b in zip(minimum,actual)]
                brute_cases+=1
                digest.update(json.dumps((d,p,word,actual)).encode())
            assert dp(p,True)==minimum[0] and dp(p,False)==minimum[1]
    reps,parents=signed_chambers(4);rows=[];hist_R=Counter();hist_C=Counter()
    for p,w in sorted(parents.items()):
        R=dp(p,True);C=dp(p,False)
        assert R>=10 and C>=10
        hist_R[R]+=1;hist_C[C]+=1
        rows.append({'weights':w,'order':p,'min_relaxed_R':R,'min_relaxed_C':C})
        digest.update(json.dumps((p,R,C)).encode())
    assert min(hist_R)==min(hist_C)==10
    witness_weights=(1,14,4,12,20);p=order(witness_weights)
    assert statistics(tuple(map(gray,p)))==(10,10)
    # Test actual translation coverage and endpoint formula on fixed Q4 parent
    # representatives: every positive t interval, NOT the entire Q4 cones.
    actual_translations=0
    for w in parents.values():
        scores=sorted(sum(w[j]*((x>>j)&1) for j in range(4)) for x in range(16))
        cuts=sorted({b-a for a in scores for b in scores if a<b})
        bounds=[0]+cuts;probes=[a+b for a,b in zip(bounds,bounds[1:])]+[2*(cuts[-1]+1)]
        for t in probes:
            weights=tuple(2*a for a in w)+(t,);child=order(weights)
            assert child is not None
            word=''.join(str(x>>4) for x in child)
            assert word==''.join(str(1-int(b)) for b in reversed(word))
            height=0
            for b in word:
                height+=1 if b=='0' else -1
                assert height>=0
            actual=statistics(tuple(map(gray,child)))
            parent=tuple(x for x in child if x<16)
            assert paired_formula(parent,word,True)==actual[0]
            assert paired_formula(parent,word,False)==actual[1]
            assert actual[0]>=dp(parent,True)
            actual_translations+=1
    levels=verify_hierarchy(HIERARCHY_WITNESS)
    assert statistics(tuple(map(gray,HIERARCHY_WITNESS)))==(12,12)
    pos={x:i for i,x in enumerate(HIERARCHY_WITNESS)}
    assert pos[0]<pos[10] and pos[62]<pos[52]
    assert (52&10)==0
    for j in range(6):
        signs={pos[x|(1<<j)]>pos[x] for x in range(64) if not ((x>>j)&1)}
        assert len(signs)==1
    lift_cases=[]
    for n in range(6,15):
        m=n-6;full=tuple((z<<m)|y for y in range(1<<m) for z in HIERARCHY_WITNESS)
        assert statistics(tuple(map(gray,full)))==(12*(1<<m),12*(1<<m))
        verify_hierarchy(full)
        lift_cases.append({'n':n,'R_C':statistics(tuple(map(gray,full)))})
    table=Path(__file__).with_name('gray_q5_parent_dp_certificate.json')
    order_digest=hashlib.sha256()
    for row in rows:order_digest.update(bytes(row['order']))
    table.write_text(json.dumps({'scope':'all signed Q4 parents; relaxed Dyck merge minima',
        'q4_representatives':reps,'parent_count':len(rows),
        'sorted_parent_order_sha256':order_digest.hexdigest(),
        'encoding':'One character per lexicographically sorted parent order; 0123456789ABCDEFG encode integer costs 0 through 16.',
        'linear_minima':''.join('0123456789ABCDEFG'[r['min_relaxed_R']] for r in rows),
        'cyclic_minima':''.join('0123456789ABCDEFG'[r['min_relaxed_C']] for r in rows)},
        separators=(',',':'))+'\n')
    receipt={'state':'EXACT_Q5_GRAY_OPTIMUM_AND_HIERARCHY_EXCLUSION_PASS',
        'all_dimensional_result':'Exact paired cost and shortest-path recurrence for relaxed centrally symmetric same-order face merging; not an additive-chamber reduction.',
        'brute_force_merge_cases':brute_cases,'q4_signed_parents':len(parents),
        'q5_relaxed_linear_histogram':dict(sorted(hist_R.items())),
        'q5_relaxed_cyclic_histogram':dict(sorted(hist_C.items())),
        'G5':10,'F5':10,'additive_witness':{'weights':witness_weights,'order':p,'R_C':[10,10]},
        'actual_fixed_parent_translation_intervals_checked':actual_translations,
        'hierarchy_counterexample':{'order':HIERARCHY_WITNESS,'R_C':[12,12],
            'levels':levels,'uniform_coordinate_edge_signs':[-1,-1,-1,1,1,1],
            'nonadditivity_certificate':'0 precedes 10 but 62 precedes 52: the same difference 10=(bit 1)+(bit 3) has opposite signs.',
            'positions_0_10_52_62':[pos[x] for x in (0,10,52,62)]},
        'hierarchy_row_lifts':lift_cases,
        'coverage_source':{'preprint':'https://arxiv.org/pdf/math/9809134','section':4,
            'chi_H4':'(x-1)(x-11)(x-13)(x-15)','regions':5376,'count_is_prior_art':True},
        'certificate_sha256':hashlib.sha256(table.read_bytes()).hexdigest(),
        'verification_digest':digest.hexdigest(),'violations':0,
        'elapsed_seconds':round(time.monotonic()-start,3),
        'limitations':'No exact value for M5 or G6, no positive density proof, no n^-2 improvement; new priority unconfirmed.'}
    Path(__file__).with_name('gray_face_merge_dp_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
