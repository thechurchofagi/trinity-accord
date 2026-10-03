#!/usr/bin/env python3
"""Exact complement-symmetric half-graph reduction and balanced-half cuts.

Uses standard signed-graph switching, dynamic programming and max flow.
Only their application to the stated paired rank scan graph is asserted.
"""
from functools import lru_cache
from collections import defaultdict,deque
import hashlib,json
from paired_sibling_ancestor_optimizer import layout

def split(graph,n):
    assert n>=2
    top,nodes,info=layout(n);root=nodes[(0,0)]
    def mirror(u):
        if u==top:return top
        d,p=info[u];return nodes[(d,p^((1<<d)-1))]
    J={(a,b):v for a,b,v in graph['edges']}
    def key(a,b):return tuple(sorted((a,b)))
    assert J.get(key(root,top),0)==0
    for (a,b),v in J.items():
        ma,mb=mirror(a),mirror(b)
        assert J.get(key(ma,mb),0)==v*(-1 if top in (a,b) else 1)
    assert graph['D']%2==0
    side={top,root}|{u for u,(d,p) in info.items() if d>=1 and p<(1<<(d-1))}
    edges=[(a,b,v) for a,b,v in graph['edges'] if a in side and b in side]
    H=sum(abs(v) for a,b,v in edges)
    assert 2*H==graph['W']
    assert all((a in side and b in side) or (mirror(a) in side and mirror(b) in side) for a,b,v in graph['edges'])
    return {'top':top,'root':root,'side':side,'edges':edges,'H':H,'mirror':mirror,'nodes':nodes,'info':info}

def half_optima(graph,n):
    s=split(graph,n);nodes=s['nodes'];top=s['top'];root=s['root']
    J={tuple(sorted((a,b))):v for a,b,v in s['edges']}
    def coupling(a,b):return J.get(tuple(sorted((a,b))),0)
    decisions={}
    @lru_cache(None)
    def solve(d,p,state):
        u=nodes[(d,p)];field=coupling(u,top)
        for ad in range(d):field+=coupling(u,nodes[(ad,p>>(d-ad))])*(1-2*((state>>ad)&1))
        vals=[]
        for bit in (0,1):
            val=(1-2*bit)*field
            if d<n-2:
                val+=solve(d+1,2*p,state|(bit<<d))+solve(d+1,2*p+1,state|(bit<<d))
            vals.append(val)
        bit=int(vals[1]>vals[0]);decisions[(d,p,state)]=bit
        return vals[bit]
    F=[0,0] if n==2 else [solve(1,0,b) for b in (0,1)]
    masks=[]
    def recover(d,p,state):
        bit=decisions[(d,p,state)];mask=bit<<nodes[(d,p)]
        if d<n-2:
            state|=bit<<d
            mask|=recover(d+1,2*p,state)|recover(d+1,2*p+1,state)
        return mask
    for b in (0,1):
        mask=(b<<root)|(0 if n==2 else recover(1,0,b))
        assert sum(v*(-1 if ((mask>>a)^(mask>>c))&1 else 1) for a,c,v in s['edges'])==F[b]
        masks.append(mask)
    full=[]
    for r in (0,1):
        mask=masks[r]
        for u in s['side']-{root,top}:
            bit=((masks[1-r]>>u)&1)^1
            mask|=bit<<s['mirror'](u)
        assert ((mask>>root)&1)==r and (mask>>top)&1==0
        assert sum(v*(-1 if ((mask>>a)^(mask>>b))&1 else 1) for a,b,v in graph['edges'])==sum(F)
        full.append(mask)
    phi=[(s['H']-f)//2 for f in F]
    assert all(s['H']-f>=0 and (s['H']-f)%2==0 for f in F)
    return {'F_plus':F[0],'F_minus':F[1],'H':s['H'],'half_frustrations':phi,
            'E_max':sum(F),'full_attaining_masks_by_root':full,
            'half_attaining_masks_by_root':masks,'conditional_states':solve.cache_info().currsize}

def balance_or_cycle(edges):
    adj=defaultdict(list)
    for a,b,v in edges:
        sg=1 if v>0 else -1
        adj[a].append((b,sg));adj[b].append((a,sg))
    signs={};parent={}
    for u in sorted(adj):
        if u in signs:continue
        signs[u]=1;parent[u]=None;q=deque([u])
        while q:
            a=q.popleft()
            for b,sg in adj[a]:
                if b not in signs:signs[b]=signs[a]*sg;parent[b]=a;q.append(b)
                elif signs[b]!=signs[a]*sg:
                    pa=[];z=a
                    while z is not None:pa.append(z);z=parent[z]
                    pb=[];z=b
                    while z not in pa:pb.append(z);z=parent[z]
                    cycle=pa[:pa.index(z)+1]+list(reversed(pb))
                    assert len(cycle)>=3 and len(cycle)==len(set(cycle))
                    J={tuple(sorted((x,y))):v for x,y,v in edges};product=1
                    for x,y in zip(cycle,cycle[1:]+cycle[:1]):product*=1 if J[tuple(sorted((x,y)))]>0 else -1
                    assert product==-1
                    return {'balanced':False,'negative_cycle':cycle}
    return {'balanced':True,'gauge':signs}

def integer_cut(edges,source,sink):
    cap=defaultdict(int);vertices={source,sink}
    for a,b,v in edges:
        cap[(a,b)]+=abs(v);cap[(b,a)]+=abs(v);vertices|={a,b}
    adj=defaultdict(set)
    for a,b in cap:adj[a].add(b)
    residual=dict(cap);flow=0
    while True:
        parent={source:None};q=deque([source])
        while q and sink not in parent:
            a=q.popleft()
            for b in sorted(adj[a]):
                if b not in parent and residual.get((a,b),0)>0:parent[b]=a;q.append(b)
        if sink not in parent:break
        b=sink;delta=None
        while parent[b] is not None:
            a=parent[b];delta=residual[(a,b)] if delta is None else min(delta,residual[(a,b)]);b=a
        b=sink
        while parent[b] is not None:
            a=parent[b];residual[(a,b)]-=delta;residual[(b,a)]=residual.get((b,a),0)+delta;b=a
        flow+=delta
    shore=set(parent);cut=sum(abs(v) for a,b,v in edges if (a in shore)!=(b in shore))
    assert cut==flow
    directed={e:cap[e]-residual.get(e,0) for e in cap}
    divergences=defaultdict(int)
    for (a,b),v in directed.items():divergences[a]+=v
    for a in vertices:
        assert divergences[a]==(flow if a==source else -flow if a==sink else 0)
    assert all(-cap[(b,a)]<=v<=cap[(a,b)] and v==-directed[(b,a)] for (a,b),v in directed.items())
    return {'value':flow,'source_shore':sorted(shore),'signed_flows':[(a,b,v) for (a,b),v in sorted(directed.items()) if a<b and v]}

def certificate(graph,n):
    s=split(graph,n);out=half_optima(graph,n);b=balance_or_cycle(s['edges'])
    out['half_balance']=b
    cut=integer_cut(s['edges'],s['root'],s['top']);out['half_cut']=cut
    assert sum(out['half_frustrations'])>=cut['value']
    if b['balanced']:
        assert sum(out['half_frustrations'])==cut['value']
        assert sorted(out['half_frustrations'])==[0,cut['value']]
    positive={}
    for a,b,v in cut['signed_flows']:
        if v>0:positive[(a,b)]=v
        else:positive[(b,a)]=-v
    paths=[];total=0
    while total<cut['value']:
        par={s['root']:None};q=deque([s['root']])
        while q and s['top'] not in par:
            a=q.popleft()
            for x,y in sorted(positive):
                if x==a and positive[(x,y)]>0 and y not in par:par[y]=x;q.append(y)
        assert s['top'] in par
        path=[];u=s['top']
        while u is not None:path.append(u);u=par[u]
        path=list(reversed(path));delta=min(positive[(a,b)] for a,b in zip(path,path[1:]))
        for a,b in zip(path,path[1:]):positive[(a,b)]-=delta
        total+=delta;paths.append((path,delta))
    J={tuple(sorted((a,b))):v for a,b,v in graph['edges']};loads=defaultdict(int);cycles=[]
    for path,delta in paths:
        cyc=path+[s['mirror'](u) for u in reversed(path[1:-1])]
        assert len(cyc)==len(set(cyc)) and len(cyc)>=4
        sign=1
        for a,b in zip(cyc,cyc[1:]+cyc[:1]):
            key=tuple(sorted((a,b)));sign*=1 if J[key]>0 else -1;loads[key]+=delta
        assert sign==-1
        cycles.append({'vertices':cyc,'multiplicity':delta})
    assert total==cut['value'] and all(load<=abs(J[key]) for key,load in loads.items())
    out['negative_cycle_packing']=cycles
    out['cycle_packing_loads']=[(a,b,v) for (a,b),v in sorted(loads.items())]
    out['cut_certified_R_lower']=1+graph['D']+graph['K']+cut['value']
    out['half_edges']=s['edges']
    out['R_min']=1+graph['D']+graph['K']+sum(out['half_frustrations'])
    return out
