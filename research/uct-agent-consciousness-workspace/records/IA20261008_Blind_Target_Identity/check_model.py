"""Exact finite checks; no human data, model training, or experience measurement."""
from itertools import permutations
from math import factorial
from pathlib import Path
import json

def between(order):
    rank={x:i for i,x in enumerate(order)}
    return {(a,b,c) for a,b,c in permutations(order,3)
            if rank[a]<rank[b]<rank[c] or rank[c]<rank[b]<rank[a]}

def carries(physical, experiential, mapping):
    return {tuple(mapping[x] for x in t) for t in between(physical)} == between(experiential)

def endpoint_orders(n):
    return [(0,)+m+(n-1,) for m in permutations(range(1,n-1))]

checks={}
rows=[]
for n in range(4,9):
    x=tuple(range(n)); orders=endpoint_orders(n)
    adaptive=sum(carries(x,e,dict(zip(x,e))) for e in orders)
    frozen=sum(carries(x,e,{i:i for i in x}) for e in orders)
    checks[f"n{n}_adaptive_all"]=adaptive==factorial(n-2)
    checks[f"n{n}_frozen_one"]=frozen==1
    # The fixed query e1<e2 varies in the evidence-only class.
    signs=[e.index(1)<e.index(2) for e in orders]
    checks[f"n{n}_background_both_signs"]=sum(signs)*2==len(signs)
    rows.append(dict(n=n,possible_orders=len(orders),adaptive_fits=adaptive,
                     frozen_fits=frozen,target_true=sum(signs),target_false=len(signs)-sum(signs)))
x=(0,1,2,3); rev_middle=(0,2,1,3); ident={i:i for i in x}
checks["negative_control_fixed_identity_rejects"]=not carries(x,rev_middle,ident)
adaptive=dict(zip(x,rev_middle))
checks["negative_control_adaptive_rescue"]=carries(x,rev_middle,adaptive)
checks["rescue_changes_target_identity"]=adaptive[1]!=ident[1] and adaptive[2]!=ident[2]
# Data-only logical closure: endpoints and one betweenness clause already fix q.
D=[e for e in endpoint_orders(4) if (0,1,2) in between(e)]
checks["betweenness_clause_leaks_q"]=len(D)==1 and D[0].index(1)<D[0].index(2)
checks["without_clause_both_outcomes"]=len(endpoint_orders(4))==2
# Preserve R175 mathematical theorem; distinguish it from empirical qualification.
for n in range(3,7):
    x=tuple(range(n))
    maps=[p for p in permutations(x) if carries(x,x,dict(zip(x,p)))]
    checks[f"R175_n{n}_two_maps"]=len(maps)==2
# Fixed chronology, changed represented-order state: inherited mechanism witness.
exec_order=("record_red","record_blue","compare","output")
machine=[dict(r=r,q=2-1-r,execution_order=exec_order) for r in (0,2)]
checks["execution_same_content_opposite"]=(machine[0]["execution_order"]==machine[1]["execution_order"]
                                          and machine[0]["q"]>0>machine[1]["q"])

def ancestry(edges, sources, target):
    ans=set()
    for s in sources:
        todo=[s]; seen={s}
        while todo:
            cur=todo.pop()
            for a,b in edges:
                if a==cur and b not in seen: seen.add(b);todo.append(b)
        if target in seen: ans.add(s)
    return ans

edges={("B","rb"),("rb","ub"),("C","rc"),("rc","uc")}
base={"B":10,"rb":11,"ub":12,"C":20,"rc":21,"uc":22}
slow={"B":10,"rb":25,"ub":30,"C":20,"rc":21,"uc":22}
sources={"B","C"}
checks["trace_legal_retimings"]=all(t[a]<t[b] for t in (base,slow) for a,b in edges)
checks["trace_use_order_reverses"]=(base["ub"]<base["uc"] and slow["ub"]>slow["uc"])
checks["trace_singletons_fixed"]=(ancestry(edges,sources,"ub")=={"B"} and ancestry(edges,sources,"uc")=={"C"})
mixed=edges|{("rc","ub")}
checks["trace_mixed_source_fails_singleton"]=(ancestry(mixed,sources,"ub")==sources and all(slow[a]<slow[b] for a,b in mixed))
redundant=edges|{("B","ub")}
checks["trace_same_source_redundancy"]=ancestry(redundant,sources,"ub")=={"B"}
subdiv=(edges-{("rb","ub")})|{("rb","new"),("new","ub")}
rename={v:"renamed_"+v for v in base}
checks["trace_subdivide_and_rename"]=(all(ancestry(subdiv,sources,u)==ancestry(edges,sources,u) for u in ("ub","uc"))
 and ancestry({(rename[a],rename[b]) for a,b in edges},{rename[s] for s in sources},rename["ub"])=={rename["B"]})

result={"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,
        "passed":sum(checks.values()),"total":len(checks),"permutation_cases":rows,
        "negative_example":{"observed_order":rev_middle,"frozen_mapping":ident,
                            "adaptive_mapping":adaptive},
        "execution_witness":machine,
        "scope":"Exact abstract finite checks plus general proofs in note; not empirical validation."}
Path(__file__).with_name("MODEL_RESULTS.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
assert all(checks.values())
