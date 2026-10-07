"""Exact finite checks for the thought experiment; no physical experiments."""
from itertools import permutations,product
from pathlib import Path
import json,math

def inv(p):
    return tuple(p.index(j) for j in range(len(p)))
def relative(s,t):
    ti=inv(t)
    return tuple(ti[s[i]] for i in range(len(s)))
def response(x,u,s,t):
    ti=inv(t)
    xp=tuple(x[j]^u[ti[j]] for j in range(len(x)))
    return tuple(xp[s[i]] for i in range(len(x)))

out={"scope":"Exact finite model checks; the general proof is in SELF_REFERENCE_REWIRING.md. No phenomenology, physical realization or historical priority certified."}
rows=[]
for n in range(2,5):
    ps=list(permutations(range(n)));vectors=list(product(range(2),repeat=n));zero=(0,)*n
    laws={};case_count=0
    for s,t in product(ps,repeat=2):
        L=relative(s,t)
        law=tuple(response(zero,u,s,t) for u in vectors)
        laws.setdefault(law,[]).append((s,t,L))
        for x,u in product(vectors,repeat=2):
            m=tuple(x[s[i]] for i in range(n));y=response(x,u,s,t)
            assert y==tuple(m[i]^u[L[i]] for i in range(n))
            case_count+=1
        for i in range(n):
            perfect=all(response(zero,u,s,t)[i]==u[i] for u in vectors)
            assert perfect==(s[i]==t[i])
    assert len(laws)==math.factorial(n)
    assert all(len(cls)==math.factorial(n) and len({x[2] for x in cls})==1 for cls in laws.values())
    # Relative laws' equivalence classes are exactly common body postcomposition orbits.
    for cls in laws.values():
        s,t,_=cls[0];ti=inv(t)
        for ss,tt,_ in cls:
            g=tuple(tt[ti[j]] for j in range(n))
            assert tuple(g[j] for j in s)==ss and tuple(g[j] for j in t)==tt
    rows.append({"n":n,"connection_pairs":len(ps)**2,"response_classes":len(laws),"class_size":math.factorial(n),"state_command_pair_checks":case_count})
out['enumeration']=rows

I=(0,1);S=(1,0);table=[]
for s,t in [(I,I),(S,I),(I,S),(S,S)]:
    perfect=all(response((0,0),u,s,t)==u for u in product(range(2),repeat=2))
    sync=all(response((0,0),(a,a),s,t)==(a,a) for a in range(2))
    own=[s[i]==t[i]==i for i in range(2)]
    table.append({'sensor':s,'action':t,'relative':relative(s,t),'perfect_all_actions':perfect,'perfect_synchronized_actions':sync,'own_relative_to_fixed_assembly':own})
assert [x['perfect_all_actions'] for x in table]==[True,False,False,True]
assert all(x['perfect_synchronized_actions'] for x in table)
out['swap_table']=table

# Full renaming preserves the predicates, unlike physical double rewiring at fixed beta.
rename_checks=0
ps=list(permutations(range(3)))
for beta,s,t,g,h in product(ps,repeat=5):
    hi=inv(h)
    rename=lambda p:tuple(g[p[hi[k]]] for k in range(3))
    bb,ss,tt=map(rename,[beta,s,t])
    for i in range(3):
        assert (s[i]==t[i]==beta[i])==(ss[h[i]]==tt[h[i]]==bb[h[i]])
        assert (s[i]==t[i])==(ss[h[i]]==tt[h[i]])
        rename_checks+=1
out['predicate_rename_checks']=rename_checks
out['all_checks_passed']=True
Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
