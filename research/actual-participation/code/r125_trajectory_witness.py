#!/usr/bin/env python3
from itertools import product
def step(x,g):
    a,b,c,d,u,v=x
    return ((a+b+g*u)%3,(a+2*b)%3,(c+d+g*v)%3,(c+2*d)%3,(u+v+a)%3,(u+2*v+c)%3)
def traj(x,g,T):
    out=[x]
    for _ in range(T): x=step(x,g); out.append(x)
    return tuple(out)
states=list(product(range(3),repeat=6))
counts={T:sum(traj(x,0,T)==traj(x,1,T) for x in states) for T in range(6)}
print(counts)
assert counts=={0:729,1:81,2:9,3:1,4:1,5:1}
print("PASS")
