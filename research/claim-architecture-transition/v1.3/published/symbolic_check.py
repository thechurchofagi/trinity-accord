#!/usr/bin/env python3
"""Optional internal symbolic checks; requires SymPy, not used by audit.py."""
import json
import sympy as S
eta,u,v,p,s,ew,eo,M=S.symbols('eta u v p s ew eo M')
D=eta*ew*u+(1-eta)*eo*v
pd=-p*(u-v)/D
ud=ew*u/p*pd
B=(1-s)*M+p
N=eta*(u+p)-s*M
actual=((u+p+eta*(ud+pd))*B-N*pd)/B**2
P0=(eta*ew*u*(p+v)+(1-eta)*eo*v*(p+u))*(M+p)+eta*(1-eta)*p*(u-v)**2
Ps=M*(p+v)*(p+(1-s)*u)+(eta*(ew-1)*u*(p+v)+(1-eta)*(eo-1)*v*(p+u))*B
checks={
 'inverse_derivative':S.factor((actual.subs(s,0)-P0/(D*(M+p)**2)).subs(M,eta*u+(1-eta)*v)),
 'finite_labor_derivative':S.factor((actual-Ps/(D*B**2)).subs(M,eta*u+(1-eta)*v))}
a,b=S.symbols('a b',positive=True)
Da=a*(1-eta)+b*eta
pCD=M/(eta*(1-a)/a+(1-eta)*(1-b)/b)
rawCD=(eta*((1-a)/a*pCD+pCD)-s*M)/((1-s)*M+pCD)
checks['cobb_douglas_recovery']=S.factor(rawCD-(eta*b-s*(Da-a*b))/(Da-s*(Da-a*b)))
checks['zero_labor_bound_identity']=S.factor(N/B-eta*(u+p)/(M+p)+s*M*(1-eta*(u+p)/(M+p))/B)
for name,expr in checks.items():
 assert expr==0,(name,expr)
print(json.dumps({'status':'PASS','identities':len(checks),'sympy_version':S.__version__,
 'results':{k:str(v) for k,v in checks.items()},'independent_peer_review':False},indent=2))
