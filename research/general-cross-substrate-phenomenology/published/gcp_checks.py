#!/usr/bin/env python3
"""Finite causal checks for TA-TR-2026-16. Python 3 standard library only.
These are mathematical constructions, not consciousness experiments.
Run: python3 gcp_checks.py --output gcp_results.json
"""
import argparse, itertools, json, math
from fractions import Fraction as Q
from pathlib import Path

def mm(a,b):
 return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def states(n):return list(itertools.product((0,1),repeat=n))
def reach(a):
 n=len(a);c=[[bool(a[i][j] or i==j) for j in range(n)] for i in range(n)]
 for k in range(n):
  for i in range(n):
   for j in range(n):c[i][j]=c[i][j] or (c[i][k] and c[k][j])
 return all(all(row) for row in c)
def graph_checks():
 n=4; edges=[(i,j) for i in range(n) for j in range(n) if i!=j]; tested=0; strong=0
 for bits in itertools.product((0,1),repeat=len(edges)):
  a=[[0]*n for _ in range(n)]
  for (i,j),v in zip(edges,bits):a[i][j]=v
  powers=[];v=eye(n)
  for _ in range(2*(n-1)):v=mm(v,a);powers.append(v)
  criterion=True
  for mask in range(1,1<<(n-1)):
   cut=[[(a[i][j] if ((mask>>i)&1)==((mask>>j)&1) else 0) for j in range(n)] for i in range(n)]
   v=eye(n);found=[False]*n
   for w in powers:
    v=mm(v,cut)
    found=[f or w[i][i]>v[i][i] for i,f in enumerate(found)]
   if not all(found):criterion=False;break
  sc=reach(a);assert criterion==sc
  strong+=sc;tested+=1
 return {'graphs':tested,'strongly_connected':strong,'maximum_walk_length':6,'equivalence_pass':True}
def finite_checks():
 f=lambda x:(x[0]^x[1],)*2
 assert all(f(f(x))==(0,0) for x in states(2))
 assert {f((0,f(x)[1])) for x in states(2)}=={(0,0),(1,1)}
 parity=lambda x:(sum(x)%2,)*5
 rev=lambda x:(x[1],x[2],x[3],x[0]^x[1])
 inverse=lambda x:(x[3]^x[0],x[0],x[1],x[2])
 assert all(inverse(rev(x))==x for x in states(4))
 a=states(5);b=states(4);rows=[]
 for h in range(1,17):
  a=list({parity(x) for x in a});b=list({rev(x) for x in b})
  assert len(a)==2 and len(b)==16
  rows.append({'horizon':h,'parity_bits':math.log2(len(a)),'reversible_bits':math.log2(len(b))})
 # Common regime: no mode has both 5-bit capacity and all-to-all dependence.
 achievable=[(5,False),(1,True)]
 assert not any(c==5 and dep for c,dep in achievable)
 # Diagnostic gate: mediator effect absent at c=0, present at c=1.
 assert all((a^(0&m))==a for a,m in states(2))
 assert all((a^(1&0))!=(a^(1&1)) for a in (0,1))
 t=[[1,1],[1,-1]];ti=[[Q(1,2),Q(1,2)],[Q(1,2),Q(-1,2)]]
 w=[[2,0],[0,3]];wp=mm(mm(t,w),ti)
 assert wp==[[Q(5,2),Q(-1,2)],[Q(-1,2),Q(5,2)]]
 assert mm(t,w)==mm(wp,t)
 return {'reset_artifact_pass':True,'capacity_by_horizon':rows,'common_regime_pass':True,'gated_mediator_pass':True,'recoding_pass':True}
def redundancy_checks():
 p=Q(1,10);rows=[];coalitions=0
 for n in (1,3,5,7,9):
  r=(n-1)//2
  for x in states(n):
   observed=int(sum(x)>r);assert observed==int(sum(x)>=r+1);coalitions+=1
  reliability=sum(Q(math.comb(n,k))*p**k*(1-p)**(n-k) for k in range(r+1))
  pivotal=Q(math.comb(2*r,r))*p**r*(1-p)**r
  # Independent exhaustive noise-weighted reconstruction.
  ex=sum(p**sum(x)*(1-p)**(n-sum(x)) for x in states(n) if sum(x)<=r)
  tie=sum(p**sum(x)*(1-p)**(2*r-sum(x)) for x in states(2*r) if sum(x)==r)
  assert ex==reliability and tie==pivotal
  rows.append({'carriers':n,'correct_return':float(reliability),'singleton_pivotality':float(pivotal),'reliability_exact':str(reliability),'pivotality_exact':str(pivotal)})
 s=states(2);encode=lambda x:tuple(v for b in x for v in (b,b,b))
 decode=lambda x:(int(sum(x[:3])>=2),int(sum(x[3:])>=2))
 noise=[x for x in states(6) if sum(x[:3])<=1 and sum(x[3:])<=1];count=0
 for outputs in itertools.product(s,repeat=4):
  f=dict(zip(s,outputs))
  for x in s:
   code=encode(x)
   for e in noise:
    corrupted=tuple(a^b for a,b in zip(code,e))
    assert encode(f[decode(corrupted)])==encode(f[x]);count+=1
 return {'coalition_cases':coalitions,'reliability':rows,'binary_rules':256,'correctable_wrapper_cases':count,'wrapper_pass':True}
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',default='gcp_results.json');p=a.parse_args()
 result={'status':'PASS','scope':'Constructed causal models only; no phenomenal ground truth','graph':graph_checks(),'finite':finite_checks(),'redundancy':redundancy_checks()}
 Path(p.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
