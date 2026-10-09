#!/usr/bin/env python3
"""Exact compact CM verifier. Requires SymPy; no phenomenal measurement."""
import itertools
from fractions import Fraction as F
import sympy as s

cases=identified=hidden=endpoints=0
I=s.eye(2)
monitors=[]
for h in itertools.product((-1,0,1),repeat=2):
    H=s.Matrix(1,2,h);Hp=H.pinv();P=I-Hp*H
    assert P*P==P and H*P==s.zeros(1,2)
    monitors.append((H,Hp,P))
for mv in itertools.product((0,1),repeat=4):
    M=s.Matrix(2,2,mv)
    for H,Hp,P in monitors:
        for kv in itertools.product((-1,0,1),repeat=2):
            K=s.Matrix(1,2,kv);A=K*M
            ok=A*P==s.zeros(1,2)
            assert ok==(H.col_join(A).rank()==H.rank())
            cases+=1
            if ok:
                assert A*Hp*H==A
                identified+=1
            else:
                v=P*A.T
                assert H*v==s.zeros(1,1) and A*v!=s.zeros(1,1)
                assert (-M*v)+M*v==s.zeros(2,1)
                hidden+=1
            z=H*s.Matrix([1,-1]);u0=Hp*z
            left=4-(u0.T*u0)[0];sigma2=(A*P*A.T)[0]
            assert left>=0 and sigma2>=0
            if sigma2:
                for sign in (-1,1):
                    v=sign*s.sqrt(left/sigma2)*P*A.T;u=u0+v
                    assert s.simplify((u.T*u)[0]-4)==0
                    assert s.simplify(H*u-z)==s.zeros(1,1)
                    assert s.simplify((A*v)[0]**2-left*sigma2)==0
                    endpoints+=1
assert (cases,identified,hidden,endpoints)==(1296,566,730,1460)
M=s.Matrix([[1,1]])
for h,expected in [([1,1],0),([1,-1],1)]:
    H=s.Matrix(1,2,h);P=I-H.pinv()*H
    assert s.Rational(1,2)*(M*P*M.T)[0]==expected
for alpha in (F(1),F(1,2),F(1,4)):
    u=F(0);d=F(1)
    for t in range(11):
        e=d+u
        assert e==d*(1-alpha)**t and e-u==d
        u-=alpha*e
moments=0
for g,b,a in itertools.product(map(F,range(-2,3)),map(F,range(-2,3)),(F(1,2),F(1),F(2))):
    assert sum(x*(g*x+b) for x in (-a,a))/2==g*a*a
    assert sum((g*x+b)**2 for x in (-a,a))/2==g*g*a*a+b*b
    moments+=1
assert moments==75
assert all(2*x+(-2*x)==0 for x in (-1,1))
print('CM CORE PASS',dict(cases=cases,identified=identified,hidden=hidden,endpoints=endpoints,moments=moments))
print('Conditional finite mathematics only; no C1, experience, or subject-count validation.')
