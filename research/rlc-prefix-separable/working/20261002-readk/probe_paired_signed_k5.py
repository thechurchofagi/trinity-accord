#!/usr/bin/env python3
"""Candidate signed K5 minors; explicit gauges, trees, and bridges validate hits.

Absence in this bounded random search is not an exclusion theorem.
Both parallel signs are retained after contractions; they never cancel.
"""
from collections import defaultdict,Counter
from pathlib import Path
import json,random,time,hashlib
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_complement_half_graph import decompose

def key(a,b):return tuple(sorted((a,b)))
def flip(mask):return ((mask&1)<<1)|((mask&2)>>1)

def odd_clique(edges,k=5):
    vertices=sorted({a for a,b in edges}|{b for a,b in edges})
    choices=[(u,s) for u in vertices for s in (1,-1)]
    adjacency=[0]*len(choices)
    for i,(u,s) in enumerate(choices):
        for j,(v,t) in enumerate(choices):
            if u==v:continue
            mask=edges.get(key(u,v),0)
            if mask & (2 if s==t else 1):adjacency[i]|=1<<j
    def extend(chosen,possible):
        if len(chosen)==k:return chosen
        if possible.bit_count()<k-len(chosen):return None
        while possible:
            bit=possible&-possible;i=bit.bit_length()-1;possible^=bit
            hit=extend(chosen+[i],possible&adjacency[i])
            if hit is not None:return hit
            if possible.bit_count()<k-len(chosen):break
        return None
    # The global switching symmetry fixes the first selected gauge to +.
    for i in range(0,len(choices),2):
        hit=extend([i],adjacency[i]&~((1<<(i+2))-1))
        if hit is not None:return [choices[j] for j in hit]
    return None

def certificate(original,groups,trees,clique):
    J={key(a,b):(1 if c>0 else -1) for a,b,c in original}
    branches=[];used=set()
    for u,s in clique:
        gauges={v:s*g for v,g in groups[u].items()}
        assert not used.intersection(gauges);used.update(gauges)
        seen={min(gauges)}
        T=trees[u]
        assert len(T)==len(gauges)-1
        for a,b in T:assert J[key(a,b)]*gauges[a]*gauges[b]==1
        while True:
            old=len(seen)
            for a,b in T:
                if a in seen:seen.add(b)
                if b in seen:seen.add(a)
            if len(seen)==old:break
        assert seen==set(gauges)
        branches.append({'gauges':sorted(gauges.items()),'positive_tree':T})
    bridges=[]
    for i in range(len(branches)):
        for j in range(i+1,len(branches)):
            A=dict(branches[i]['gauges']);B=dict(branches[j]['gauges'])
            witnesses=[(a,b,J[key(a,b)]) for a in A for b in B
                       if key(a,b) in J and J[key(a,b)]*A[a]*B[b]==-1]
            assert witnesses
            bridges.append((i,j,witnesses[0]))
    assert len(bridges)==10
    return {'branches':branches,'negative_bridges':bridges}

def search(original,rng,trials=64):
    base={key(a,b):(1 if c>0 else 2) for a,b,c in original}
    vertices=sorted({a for a,b in base}|{b for a,b in base})
    for trial in range(trials):
        E=base.copy();groups={u:{u:1} for u in vertices};trees={u:[] for u in vertices}
        while len(groups)>=5:
            hit=odd_clique(E)
            if hit is not None:return certificate(original,groups,trees,hit),trial
            adjacency=defaultdict(list)
            for (a,b),mask in E.items():adjacency[a].append(b);adjacency[b].append(a)
            leaves=[u for u in groups if len(adjacency[u])<2]
            if leaves:
                for u in leaves:
                    del groups[u];del trees[u]
                    E={e:m for e,m in E.items() if u not in e}
                continue
            if len(groups)==5:break
            # Contract from a low-degree group, varying the neighbor and gauge.
            order=sorted(groups,key=lambda u:(len(adjacency[u]),rng.random()))
            u=rng.choice(order[:min(3,len(order))]);v=rng.choice(adjacency[u])
            signs=[s for s,m in ((1,1),(-1,2)) if E[key(u,v)]&m]
            s=rng.choice(signs)
            # Gauges in v are multiplied by s before joining u.
            bridge=None
            for a,sa in groups[u].items():
                for b,sb in groups[v].items():
                    raw=next((1 if c>0 else -1 for x,y,c in original if key(x,y)==key(a,b)),None)
                    if raw is not None and raw*sa*sb==s:bridge=(a,b);break
                if bridge is not None:break
            assert bridge is not None
            groups[u].update({a:s*t for a,t in groups[v].items()})
            trees[u]+=trees[v]+[bridge];del groups[v];del trees[v]
            new={}
            for (a,b),mask in E.items():
                if a==v or b==v:
                    if s<0:mask=flip(mask)
                    a=u if a==v else a;b=u if b==v else b
                if a!=b:new[key(a,b)]=new.get(key(a,b),0)|mask
            E=new
    return None,trials

def main():
    rng=random.Random(202610031330);start=time.monotonic();counts=Counter();rows=[]
    seeds=[(3998575,4578511,42715,7899299,2129239,2794740,3504965,7382886)]
    for n in range(6,13):
        for sample in range(80):
            if sample%4==0:
                B=1<<n;w=[B+(1<<j) for j in range(n)];rng.shuffle(w)
            else:w=[rng.randrange(1,100000000) for j in range(n)]
            seeds.append(tuple(w))
    for index,w in enumerate(seeds):
        n=len(w);o=order_and_scores(w)
        if o is None:counts['nongeneric']+=1;continue
        g=linear_graph(o[0],n);H,r,a,tau=decompose(g,n)
        hit,tries=search(H,rng,trials=32)
        counts['generic']+=1
        row={'n':n,'weights':w,'half_vertices':len({v for u,v,c in H}|{u for u,v,c in H}),
             'half_edges':len(H),'trials':tries,'found':hit is not None}
        if hit is not None:
            row.update({'half_signed_edges':H,'certificate':hit});rows.append(row)
            print(json.dumps({'index':index,**row}),flush=True);break
        rows.append(row)
        if index%20==0:print(json.dumps({'completed':index+1,'counts':dict(counts),'elapsed':time.monotonic()-start}),flush=True)
    out={'status':'BOUNDED_REAL_HALF_SIGNED_K5_SEARCH','seed':202610031330,'counts':dict(counts),
         'scope':'Each hit has an exact independently checked branch/gauge/tree/bridge certificate. No-hit rows do not certify signed minor exclusion.',
         'rows':rows,'seconds':time.monotonic()-start}
    raw=json.dumps(out,indent=2)+'\n';Path(__file__).with_name('paired_signed_k5_pressure.json').write_text(raw)
    print(json.dumps({'found':any(z['found'] for z in rows),'seconds':out['seconds'],'report_sha256':hashlib.sha256(raw.encode()).hexdigest()}),flush=True)

if __name__=='__main__':main()
