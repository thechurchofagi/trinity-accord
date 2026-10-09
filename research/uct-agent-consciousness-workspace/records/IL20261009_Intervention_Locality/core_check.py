#!/usr/bin/env python3
"""Compact IL check. Standard library; mathematical models, not an experience assay."""
from fractions import Fraction as F
from itertools import product, permutations
import json


def mm(A,B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def mv(A,x):
    return tuple(sum(a*b for a,b in zip(row,x)) for row in A)


def det(A):
    return A[0][0]*A[1][1]-A[0][1]*A[1][0]


def reset_count(n):
    xs=list(product((0,1),repeat=n)); ix={x:i for i,x in enumerate(xs)}
    resets={tuple(ix[x[:i]+(a,)+x[i+1:]] for x in xs) for i in range(n) for a in (0,1)}
    good=0
    for h in permutations(range(len(xs))):
        inv=[0]*len(h)
        for i,j in enumerate(h): inv[j]=i
        good+=all(tuple(h[r[inv[y]]] for y in range(len(h))) in resets for r in resets)
    return good


A=[[F(1,2),F(0)],[F(0),F(1,4)]]
B=[[F(1)],[F(1)]]; C=[[F(1),F(1)]]
S=[[F(1),F(1)],[F(1),F(-1)]]
Si=[[F(1,2),F(1,2)],[F(1,2),F(-1,2)]]
D=mm(mm(S,A),Si); E=mm(S,B); H=mm(C,Si)
assert D==[[F(3,8),F(1,8)],[F(1,8),F(3,8)]]
assert E==[[2],[0]] and H==[[1,0]]
ctrA=[[B[i][0],mm(A,B)[i][0]] for i in range(2)]
ctrD=[[E[i][0],mm(D,E)[i][0]] for i in range(2)]
obsA=C+mm(C,A); obsD=H+mm(H,D)
assert [det(a) for a in (ctrA,ctrD,obsA,obsD)]==[F(-1,4),F(1,2),F(-1,4),F(1,8)]
x=(F(0),F(0)); z=x
for u in (-4,3):
    x=tuple(v+u for v in mv(A,x))
    z=tuple(v+b[0]*u for v,b in zip(mv(D,z),E))
    assert z==mv(S,x) and mv(C,x)==mv(H,z)
assert x==(1,2) and z==(3,-1)
traces=[]
for s,K,R in [((0,2),A,C),((0,-1),D,H),((3,0),D,H),((2,-2),D,H)]:
    pair=[]
    for _ in range(2):
        pair.append(mv(R,s)[0]); s=mv(K,s)
    traces.append(pair)
assert traces==[[2,F(1,2)],[0,F(-1,8)],[3,F(9,8)],[2,F(1,2)]]
a=F(21,11)
assert max(abs(a-2),abs((3*a-1)/8-F(1,2)))==F(1,11)
for d in range(1,20):
    for j in range(-100,101):
        a=F(j,d)
        assert max(abs(a-2),abs((3*a-1)/8-F(1,2)))>=F(1,11)
counts={str(n):reset_count(n) for n in (2,3)}
assert counts=={'2':8,'3':48}
print(json.dumps({'status':'PASS','reset_symmetries':counts,
  'post_write_readouts':[[str(v) for v in pair] for pair in traces],
  'minimax_one_part_error':'1/11','joint_write_error':'0',
  'scope':'Smaller finite verifier; general conclusions use the written proofs, not enumeration.'},indent=2))
