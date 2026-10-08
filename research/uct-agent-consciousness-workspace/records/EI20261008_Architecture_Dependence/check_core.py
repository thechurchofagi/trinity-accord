#!/usr/bin/env python3
"""Exact finite arithmetic/dependency checks, not experience measurements."""
from itertools import product
from collections import Counter
from fractions import Fraction as F
import json

def task(x,y,c): return x+y if c==0 else x*y

def run(x,y,c,a,l):
    h=0 if l in ('H','both') else c
    q=0 if l in ('Q','both') else c
    z=h if a=='shared' else q if a=='bypass' else h|q
    return h,q,z,task(x,y,z),h

arches=('shared','bypass','redundant')
clamps=('none','H','Q','both')
inputs=list(product(range(4),range(4),(0,1)))
rows=[]; table={}; reports={}
for a,l in product(arches,clamps):
    correct=rc=0
    for x,y,c in inputs:
        h,q,z,out,r=run(x,y,c,a,l)
        correct+=(out==task(x,y,c)); rc+=(r==c)
        rows.append([a,l,x,y,c,h,q,z,out,r])
        hbar=1 if l in ('H','both') else 1-c
        qbar=1 if l in ('Q','both') else 1-c
        hh,qq=1-hbar,1-qbar
        zz=hh if a=='shared' else qq if a=='bypass' else hh|qq
        assert (task(x,y,zz),hh)==(out,r)
    table[a+'/'+l]=str(F(correct,32)); reports[a+'/'+l]=str(F(rc,32))
for x,y,c in inputs:
    assert len({run(x,y,c,a,'none') for a in arches})==1
expected={'shared':('1','9/16','1','9/16'),
          'bypass':('1','1','9/16','9/16'),
          'redundant':('1','1','1','9/16')}
for a in arches:
    assert tuple(table[a+'/'+l] for l in clamps)==expected[a]
    assert tuple(reports[a+'/'+l] for l in clamps)==('1','1/2','1','1/2')
optimum=sum(max(Counter(task(x,y,c) for c in (0,1)).values())
            for x,y in product(range(4),repeat=2))
assert F(optimum,32)==F(9,16)
encoder_count=0
for n in range(1,7):
    for m in range(1,4):
        best=F(0)
        for e in product(range(m),repeat=n):
            p=F(len(set(e)),n); encoder_count+=1
            assert p<=min(F(1),F(m,n)); best=max(best,p)
        assert best==min(F(1),F(m,n))
assert len(rows)==384 and encoder_count==1224
# Enumerate minimal sufficient surviving routes in the fixed clamp model.
kept={'none':frozenset(('H','Q')),'H':frozenset(('Q',)),
      'Q':frozenset(('H',)),'both':frozenset()}
mins={}
for a in arches:
    good=[kept[l] for l in clamps if table[a+'/'+l]=='1']
    mins[a]=sorted([sorted(s) for s in good if not any(t<s for t in good)])
assert mins=={'shared':[['H']],'bypass':[['Q']],'redundant':[['H'],['Q']]}
result={'status':'CORE_PASS','scores':table,'report_scores':reports,
        'arithmetic_rows':len(rows),'encoder_cases':encoder_count,
        'minimal_sufficient_sets':mins,'optimal_both_erased':'9/16',
        'scope':'Exact finite models only; no phenomenal or whole-map validation'}
print(json.dumps(result,indent=2))
