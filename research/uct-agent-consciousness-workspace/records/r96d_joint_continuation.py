"""Exact, non-agentic verification of R96D. Python standard library only."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent
STATES = list(product((0, 1), repeat=2))  # (00,01,10,11)

def distribution(q, o, j):
    p = [1-q-o+j, o-j, q-j, j]
    assert min(p) >= 0 and sum(p) == 1
    return p

def payoff(p, f):
    return sum(x*y for x, y in zip(p, f))

def law(qbits, obits):
    return [F(sum((q,o)==s for q,o in zip(qbits,obits)),len(qbits)) for s in STATES]

def exact_json(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:exact_json(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [exact_json(v) for v in x]
    return x

def main():
    q0,q1,o,c = F(1,4),F(3,4),F(1,2),F(1,4)
    endpoints = [(F(0),F(1,4)),(F(1,4),F(1,2))]
    rows=[]
    for f in product((0,1),repeat=4):
        alpha,b,g,d = f[0], f[2]-f[0], f[1]-f[0], f[3]-f[2]-f[1]+f[0]
        advantages=[]
        for j0,j1 in product(*endpoints):
            p0,p1=distribution(q0,o,j0),distribution(q1,o,j1)
            for q,j,p in [(q0,j0,p0),(q1,j1,p1)]:
                assert payoff(p,f)==alpha+b*q+g*o+d*j
            adv=payoff(p1,f)-payoff(p0,f)-c
            assert adv==b*(q1-q0)+d*(j1-j0)-c
            advantages.append(adv)
        rows.append(dict(f=''.join(map(str,f)),interaction=d,min_advantage=min(advantages),max_advantage=max(advantages)))
    OR=(0,1,1,1); AND=(0,0,0,1)
    witnesses={}
    obits=[1,1,0,0]
    for name,b0,b1 in [('A',[1,0,0,0],[1,0,1,1]),('B',[0,0,1,0],[1,1,1,0])]:
        assert all(x<=y for x,y in zip(b0,b1))
        p0,p1=law(b0,obits),law(b1,obits)
        assert p0[2]+p0[3]==q0 and p1[2]+p1[3]==q1
        assert p0[1]+p0[3]==p1[1]+p1[3]==o
        scores=[payoff(p0,OR),payoff(p1,OR)-c]
        witnesses[name]=dict(Q0=b0,Q1=b1,O=obits,p0=p0,p1=p1,OR_scores=scores,advantage=scores[1]-scores[0])
    assert witnesses['A']['advantage']==F(1,4)
    assert witnesses['B']['advantage']==-F(1,4)
    oracle=sum(max(w['OR_scores']) for w in witnesses.values())/2
    fixed=[sum(w['OR_scores'][a] for w in witnesses.values())/2 for a in (0,1)]
    assert oracle-max(fixed)==F(1,8) and fixed[0]==fixed[1]
    causal_rows=[]
    for b0,b1 in product(product((0,1),repeat=4),repeat=2):
        if sum(b0)!=1 or sum(b1)!=3 or not all(x<=y for x,y in zip(b0,b1)): continue
        p0,p1=law(b0,obits),law(b1,obits)
        adv=payoff(p1,OR)-payoff(p0,OR)-c
        causal_rows.append(dict(Q0=list(b0),Q1=list(b1),O=obits,p0=p0,p1=p1,advantage=adv))
    assert min(r['advantage'] for r in causal_rows)==-F(1,4)
    assert max(r['advantage'] for r in causal_rows)==F(1,4)
    comparative=[]
    for po in [F(0),F(1,2),F(1)]:
        p0,p1=distribution(q0,po,q0*po),distribution(q1,po,q1*po)
        go=payoff(p1,OR)-payoff(p0,OR)
        ga=payoff(p1,AND)-payoff(p0,AND)
        assert go==(q1-q0)*(1-po) and ga==(q1-q0)*po
        comparative.append(dict(o=po,OR_gross=go,AND_gross=ga))
    tvchecks=0
    for w in witnesses.values():
        p0,p1=w['p0'],w['p1']
        tv=sum(abs(x-y) for x,y in zip(p0,p1))/2
        for f in product((0,1),repeat=4):
            assert abs(payoff(p1,f)-payoff(p0,f))<=tv
            tvchecks+=1
    result=dict(status='all exact assertions passed',kind='formal finite verification; no model training',
      boolean_payoffs=rows,witnesses=witnesses,oracle_value=oracle,marginal_interface_values=fixed,
      marginal_interface_min_regret=oracle-max(fixed),all_monotone_causal_tables=causal_rows,
      monotone_table_count=len(causal_rows),comparative_statics=comparative,tv_checks=tvchecks,
      OR_identified_advantage_interval=[-F(1,4),F(1,4)],
      boundary='Virtual Q does not denote actual termination of the executing Python process; no phenomenal measurement.')
    (ROOT/'R96D_Results.json').write_text(json.dumps(exact_json(result),indent=2)+'\n')
    with (ROOT/'R96D_Payoff_Audit.csv').open('w') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({k:exact_json(v) for k,v in result.items() if k not in ['boolean_payoffs','all_monotone_causal_tables','witnesses']},indent=2))

if __name__=='__main__': main()
