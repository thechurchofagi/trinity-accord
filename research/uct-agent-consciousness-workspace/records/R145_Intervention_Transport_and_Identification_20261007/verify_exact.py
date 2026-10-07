"""Finite exact verification for R145. No data, training, or experience measurement."""
from itertools import product
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
checks={};counts={}
def T(s,u,k):x,y=s;return y^k,x^u^k
def pi(s):return s[0]^s[1]

for n in (1,2,3):
 G=range(1<<n);S=list(product(G,repeat=2));allS=set(S)
 for k in G:
  for u in G:
   assert {T(s,u,k) for s in S}==allS
   for s in S:
    assert pi(T(s,u,k))==pi(s)^u
    for v in G:assert T(T(s,u,k),v,k)==(s[0]^u,s[1]^v)
  assert {T(T((0,0),u,k),v,k) for u in G for v in G}==allS
  fixed=[s for s in S if T(s,0,k)==s]
  assert len(fixed)==1<<n and {pi(s) for s in fixed}=={k}
  x,y=T((0,0),0,k);assert pi((0,y))==k
  assert any(T((0,0),u,k)==(0,0) for u in G)==(k==0)
 for s in S:
  for i in range(n):
   mask=1<<i
   assert pi((s[0]^mask,s[1]))==pi(s)^mask
   assert pi((s[0],s[1]^mask))==pi(s)^mask
 checks[f'n{n}_transition_bijection_composition_reachability_fixed_points_reset_sensitivity']=True
 counts[f'n{n}']={'models':1<<n,'states_per_model':len(S),'inputs':1<<n}

# All maps on the four-state carrier, including nonlinear maps.
S=list(product(range(2),repeat=2));index={s:i for i,s in enumerate(S)}
maps=[]
for outputs in product(S,repeat=4):
 if all(pi(outputs[index[s]])==pi(outputs[index[t]]) for s in S for t in S if pi(s)==pi(t)):
  maps.append(outputs)
assert len(maps)==64
# The full equal-output relation must be closed under each admitted same-label operation.
relation={(s,t) for s in S for t in S if pi(s)==pi(t)}
for s,t in relation:
 for u in (0,1):assert (T(s,u,0),T(t,u,1)) in relation
 for J in maps:assert (J[index[s]],J[index[t]]) in relation
# Independent BFS from common initial pointing, no horizon cutoff.
seen={((0,0),(0,0))};front=list(seen)
while front:
 s,t=front.pop();assert pi(s)==pi(t)
 successors=[(T(s,u,0),T(t,u,1)) for u in (0,1)]
 successors += [(J[index[s]],J[index[t]]) for J in maps]
 for pair in successors:
  if pair not in seen:seen.add(pair);front.append(pair)
assert seen==relation
checks['all_256_maps_classified_64_descending']=True
checks['unbounded_finite_product_equivalence']=True
counts['n1_product_states']=len(seen)

def mul(rows,x):return sum(((row&x).bit_count()%2)<<i for i,row in enumerate(rows))
def rank(rows,n):
 rows=list(rows);r=0
 for c in range(n):
  pivot=next((j for j in range(r,len(rows)) if rows[j]&(1<<c)),None)
  if pivot is None:continue
  rows[r],rows[pivot]=rows[pivot],rows[r]
  for j in range(len(rows)):
   if j!=r and rows[j]&(1<<c):rows[j]^=rows[r]
  r+=1
 return r

# Enumerate general affine maps with a 2n by 2n matrix and 2n-bit offset.
for n in (1,2):
 N=1<<n;V=range(1<<(2*n));f=lambda q:(q&(N-1))^(q>>n)
 total=0
 for rows in product(V,repeat=2*n):
  L=[(rows[i]^(rows[n+i])) for i in range(n)]
  L=[(r&(N-1))^(r>>n) for r in L]
  algebra=not any(L)
  # Offset cannot change constancy, so directly classify the zero-offset map once.
  byfiber={};direct=True
  for q in V:
   z=f(q);out=f(mul(rows,q))
   if z in byfiber and byfiber[z]!=out:direct=False
   byfiber[z]=out
  assert direct==algebra
  for offset in V:
   for k in range(N):assert f(mul(rows,k|(k<<n))^offset)==mul(L,k)^f(offset)
   total+=1
 checks[f'n{n}_every_affine_map_descent_and_probe_formula']=True
 counts[f'n{n}_affine_maps']=total

# All ordered pairs of 2x2 sensitivity matrices: rank and candidate-fiber size.
n=2;G=range(4);matrices=list(product(G,repeat=2));cases=0
for L1,L2 in product(matrices,repeat=2):
 fibers={}
 for k in G:fibers.setdefault((mul(L1,k),mul(L2,k)),[]).append(k)
 r=rank(list(L1)+list(L2),n)
 assert len(fibers)==1<<r and all(len(f)==1<<(n-r) for f in fibers.values())
 cases+=1
checks['all_n2_two_probe_rank_fibers']=True;counts['n2_two_probe_cases']=cases
result={'scope':'Exact finite checks supplement symbolic general proofs; no empirical or experiential validation.','checks':checks,'counts':counts,'all_passed':all(checks.values())}
(OUT/'EXACT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
