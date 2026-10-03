#!/usr/bin/env python3
"""Exact Q5 orbit reduction of locally distinct child queries.

Cube coordinate permutations and reflections preserve the sweep class.
This is a geometry reduction, not a run-complexity theorem.
"""
import hashlib,json,time
from pathlib import Path
from collections import deque
from adaptive_query_research import query_trees,reflect_geometry,validate

def main():
 st=time.monotonic();n=5;N=1<<n
 universe={tuple(q[u] for u in range(1,N)) for q in query_trees(tuple(range(n)))}
 assert len(universe)==34560
 remaining=set(universe);rows=[]
 while remaining:
  root=min(remaining);orbit={root};todo=deque([root])
  while todo:
   cur=todo.popleft();q=dict(enumerate(cur,1));nexts=[]
   for j in range(n-1):nexts.append(tuple(j+1 if a==j else j if a==j+1 else a for a in cur))
   for j in range(n):
    r=reflect_geometry(q,n,1<<j);nexts.append(tuple(r[u] for u in range(1,N)))
   for v in nexts:
    assert v in universe
    if v not in orbit:orbit.add(v);todo.append(v)
  remaining-=orbit;validate(dict(enumerate(root,1)),n)
  rows.append({'representative_queries':list(root),'orbit_size':len(orbit),
    'orbit_sha256':hashlib.sha256(json.dumps(sorted(orbit)).encode()).hexdigest()})
  print('orbit',len(rows),len(orbit),'remaining',len(remaining),flush=True)
 out={'status':'EXACT_Q5_LOCAL_QUERY_GEOMETRY_ORBITS','n':n,'all_tree_count':len(universe),'orbits':rows,
      'scope':'Complete finite geometry orbit reduction only; no all-weight lower bound in Q5 or all-n theorem.',
      'seconds':time.monotonic()-st}
 out['receipt_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
 Path('locally_adaptive_query_orbits_q5.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='orbits'}),flush=True)
if __name__=='__main__':main()
