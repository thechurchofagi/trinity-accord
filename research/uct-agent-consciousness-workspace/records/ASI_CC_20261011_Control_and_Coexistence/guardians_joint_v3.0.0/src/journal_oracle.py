#!/usr/bin/env python3
"""Independent explicit-state oracle for joint signatures; no theorem-module import.
Every reachable per-root journal state is explored one signing action at a time.
The observation is the set of proposal signature counts, not a closed-form set
intersection. Single and overlapping minimal conflict patterns are tested.
"""
import argparse,itertools,json
from collections import deque
from pathlib import Path


def reachable_counts(n,p,edges,witnesses,B):
    initial=(0,)*n;seen={initial};todo=deque([initial]);counts=set();transitions=0
    while todo:
        state=todo.popleft()
        counts.add(tuple(sum(bool(s&(1<<x)) for s in state) for x in range(p)))
        for r in range(n):
          for x in range(p):
            if state[r]>>x&1:continue
            after=state[r]|(1<<x)
            if not B>>r&1 and any((witnesses[e]>>r&1) and after&e==e for e in edges):continue
            nxt=state[:r]+(after,)+state[r+1:];transitions+=1
            if nxt not in seen:seen.add(nxt);todo.append(nxt)
    return counts,len(seen),transitions


def check(n,p,edges,H,B):
    counts,states,edges_visited=reachable_counts(n,p,edges,H,B)
    tested=0
    for qs in itertools.product(range(1,n+1),repeat=p):
        possible=False
        for c in counts:
            certified=sum(1<<x for x in range(p) if c[x]>=qs[x])
            if any(certified&e==e for e in edges):possible=True;break
        predicted=any((H[e]&~B).bit_count()<=sum(n-qs[x] for x in range(p) if e>>x&1) for e in edges)
        assert possible==predicted,(n,p,edges,H,B,qs,possible,predicted)
        tested+=1
    return states,edges_visited,tested


def main(out):
    specs=0;states=0;steps=0;thresholds=0
    for n in range(1,5):
      for p in range(2,5):
        if n*p>10:continue
        e=(1<<p)-1
        for H in range(1,1<<n):
          for B in range(1<<n):
            a,b,c=check(n,p,(e,),{e:H},B)
            specs+=1;states+=a;steps+=b;thresholds+=c
    overlapping=0
    for H1,H2 in itertools.product(range(1,8),repeat=2):
      for B in range(8):
        a,b,c=check(3,3,(3,6),{3:H1,6:H2},B)
        specs+=1;overlapping+=1;states+=a;steps+=b;thresholds+=c
    r={'version':'EAC-v3.0.0','method':'BFS all per-root journal signing transitions, then test all proposal-specific threshold vectors; no theorem code imported',
        'specifications':specs,'overlapping_conflict_specs':overlapping,'reachable_states_across_models':states,'signing_transitions_explored':steps,'heterogeneous_threshold_vectors':thresholds,'assertions':'PASS',
        'limits':['supplied minimal forbidden subsets and sound witness capability','no arbitrary conflict discovery or real network adversary','finite declared mobile exposure abstracted into B']}
    Path(out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='journal_oracle.json');main(p.parse_args().out)
