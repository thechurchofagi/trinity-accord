#!/usr/bin/env python3
"""Bounded exact signed-contraction search on REAL scan half supports.

An explicit signed odd-K5 witness is a theorem. No witness in a bounded
search is NOT an exclusion theorem. This intentionally avoids interpreting
unsigned K4/K33 certificates as signed odd-K5 certificates.
"""
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations,product
import gzip,hashlib,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_antipodal_half_graph import split,balance_or_cycle
from probe_paired_weak_bipartite_support import min_fill_width

def key(a,b):return tuple(sorted((a,b)))
def switch_flags(v):return ((v&1)<<1)|((v&2)>>1)

def verify_witness(edges,branches,gauges,trees,bridges):
    J={key(a,b):c for a,b,c in edges};seen=set()
    assert len(branches)==5
    for B,tree in zip(branches,trees):
        assert not seen.intersection(B);seen.update(B);reached={B[0]}
        for u,v in tree:assert u in B and v in B and gauges[u]*(1 if J[key(u,v)]>0 else -1)*gauges[v]==1
        while True:
            bigger=reached|{v for u in reached for v in B if key(u,v) in {key(a,b) for a,b in tree}}
            if bigger==reached:break
            reached=bigger
        assert reached==set(B)
    assert len(bridges)==10 and len({(i,j) for i,j,u,v in bridges})==10
    for i,j,u,v in bridges:
        assert i<j and u in branches[i] and v in branches[j]
        assert gauges[u]*(1 if J[key(u,v)]>0 else -1)*gauges[v]==-1
    return True

def search(edges,limit=20000):
    original={key(a,b):(1 if c>0 else -1) for a,b,c in edges}
    flags={e:(1 if c>0 else 2) for e,c in original.items()}
    vertices=sorted({u for e in flags for u in e});initial_branches={u:{u:1} for u in vertices};initial_trees={u:[] for u in vertices}
    memo=set();states=0;limited=False
    def connected_components(es,bs):
        adj=defaultdict(set)
        for a,b in es:adj[a].add(b);adj[b].add(a)
        remaining=set(bs);components=[]
        while remaining:
            z={min(remaining)}
            while True:
                bigger=z|{v for u in z for v in adj[u]}
                if bigger==z:break
                z=bigger
            remaining-=z;components.append(z)
        return components
    def merge(es,bs,ts,a,b,sg):
        # Contract a chosen edge after switching the whole b branch.
        ga=bs[a];gb=bs[b]
        candidate=next((key(u,v) for u in ga for v in gb if key(u,v) in original and ga[u]*original[key(u,v)]*gb[v]==sg),None)
        assert candidate is not None
        nb={u:dict(B) for u,B in bs.items() if u!=b};nb[a].update({u:sg*t for u,t in gb.items()})
        nt={u:list(T) for u,T in ts.items() if u!=b};nt[a]+=ts[b]+[candidate]
        ne={}
        for (u,v),fl in es.items():
            if key(u,v)==key(a,b):continue
            if u==b or v==b:
                u=a if u==b else u;v=a if v==b else v
                if sg<0:fl=switch_flags(fl)
            if u!=v:ne[key(u,v)]=ne.get(key(u,v),0)|fl
        return ne,nb,nt
    def recurse(es,bs,ts):
        nonlocal states,limited
        if len(bs)<5 or len(es)<10:return None
        state=(tuple(sorted(bs)),tuple((a,b,c) for (a,b),c in sorted(es.items())))
        if state in memo:return None
        if states>=limit:limited=True;return None
        memo.add(state);states+=1
        adj=defaultdict(set)
        for a,b in es:adj[a].add(b);adj[b].add(a)
        # Unused vertices cannot be isolated/pendant branch vertices of K5.
        low=next((u for u in bs if len(adj[u])<2),None)
        if low is not None:
            return recurse({e:c for e,c in es.items() if low not in e},{u:B for u,B in bs.items() if u!=low},{u:T for u,T in ts.items() if u!=low})
        comps=connected_components(es,bs)
        if len(comps)>1:
            for C in comps:
                if len(C)>=5:
                    z=recurse({e:c for e,c in es.items() if e[0] in C and e[1] in C},{u:B for u,B in bs.items() if u in C},{u:T for u,T in ts.items() if u in C})
                    if z:return z
            return None
        if len(bs)==5:
            if len(es)<10:return None
            vs=sorted(bs)
            for bits in product((1,-1),repeat=4):
                s=[1,*bits]
                if all(es.get(key(vs[i],vs[j]),0)&(1 if -s[i]*s[j]>0 else 2) for i,j in combinations(range(5),2)):
                    branches=[sorted(bs[u]) for u in vs];gauges={v:t*s[i] for i,u in enumerate(vs) for v,t in bs[u].items()};bridges=[]
                    for i,j in combinations(range(5),2):
                        a,b=next((a,b) for a in branches[i] for b in branches[j] if key(a,b) in original and gauges[a]*original[key(a,b)]*gauges[b]==-1)
                        bridges.append((i,j,a,b))
                    trees=[ts[u] for u in vs];verify_witness(edges,branches,gauges,trees,bridges)
                    return {'branch_sets':branches,'gauges':sorted(gauges.items()),'positive_branch_trees':trees,'ten_negative_bridges':bridges}
            return None
        # A degree-two vertex is only an internal path vertex in a K5 minor.
        low=next((u for u in bs if len(adj[u])==2),None)
        choices=[key(low,min(adj[low]))] if low is not None else sorted(es,key=lambda e:(-len(adj[e[0]]&adj[e[1]]),-(len(adj[e[0]])+len(adj[e[1]])),e))
        for a,b in choices:
            for sg,flag in ((1,1),(-1,2)):
                if not es[(a,b)]&flag:continue
                z=recurse(*merge(es,bs,ts,a,b,sg))
                if z:return z
                if limited:return None
        return None
    witness=recurse(flags,initial_branches,initial_trees)
    return {'status':'explicit_signed_odd_K5' if witness else ('bounded_no_witness' if limited else 'searched_no_witness'),
            'states':states,'state_limit':limit,'witness':witness,
            'caution':'Only an explicit verified witness is used as a theorem. No all-dimensional exclusion is inferred from absent witnesses.'}

def main():
    start=time.monotonic();saved=json.loads(gzip.decompress(Path(__file__).with_name('paired_weak_bipartite_support_pressure.json.gz').read_bytes()))
    weights=sorted({tuple(z['weights']) for z in saved['rows']},key=lambda w:(len(w),w));rows=[];hist=Counter();dig=hashlib.sha256()
    for index,w in enumerate(weights):
        n=len(w);p=order_and_scores(w)[0];g=linear_graph(p,n);h=split(g,n);width,trace=min_fill_width(h['edges'])
        if width<=3:z={'status':'unsigned_K5_excluded_by_width_upper_certificate','fill_trace':trace}
        elif balance_or_cycle(h['edges'])['balanced']:z={'status':'balanced_signed_support'}
        else:z=search(h['edges'])
        out={'n':n,'weights':w,'half_edges':h['edges'],'degree_fill_upper_width':width,**z}
        rows.append(out);hist[z['status']]+=1;dig.update(json.dumps(out,sort_keys=True).encode())
        if index%16==0 or width>3:
            print(json.dumps({'completed_scans':index+1,'current_n':n,'current_status':z['status'],'states':z.get('states'),
                              'status_counts':dict(hist),'elapsed':time.monotonic()-start}),flush=True)
        if z['status']=='explicit_signed_odd_K5':break
    out={'status':'BOUNDED_SIGNED_MINOR_PRESSURE','reused_source_digest':saved['audit_sha256'],
         'counts':dict(hist),'rows':rows,'seconds':time.monotonic()-start,'audit_sha256':dig.hexdigest()}
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('paired_odd_k5_minor_pressure.json').write_bytes(raw)
    Path(__file__).with_name('paired_odd_k5_minor_pressure.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({j:v for j,v in out.items() if j!='rows'}),flush=True)

if __name__=='__main__':main()
