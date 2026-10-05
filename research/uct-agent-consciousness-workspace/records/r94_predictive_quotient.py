#!/usr/bin/env python3
"""R94 exact predictive-quotient checks. No training or model API calls."""
import itertools, math, json, collections, csv
from pathlib import Path

P=Path(__file__).resolve().parent
EPS=0.1
COORDS=("W","Q","O","G")
STATES=[dict(zip(COORDS,bits)) for bits in itertools.product((0,1),repeat=4)]
QUERIES={
    "world":lambda s:s["W"],
    "self":lambda s:s["Q"],
    "other":lambda s:s["O"],
    "task":lambda s:s["G"],
    "any_avail":lambda s:int(s["Q"] or s["O"]),
    "count_avail":lambda s:s["Q"]+s["O"],
}
FAMILIES={
    "world_task":("world","task"),
    "world_task_any":("world","task","any_avail"),
    "world_task_self":("world","task","self"),
    "world_task_other":("world","task","other"),
    "world_task_count":("world","task","count_avail"),
    "role_resolved":("world","task","self","other"),
}
BINARY={"world","self","other","task","any_avail"}

def signature(s,fam):
    return tuple(QUERIES[q](s) for q in FAMILIES[fam])

def partition(fam):
    d=collections.defaultdict(list)
    for s in STATES:
        d[signature(s,fam)].append(tuple(s[c] for c in COORDS))
    return d

def flip(s,c):
    t=dict(s);t[c]=1-t[c];return t

def swap_qo(s):
    t=dict(s);t["Q"],t["O"]=s["O"],s["Q"];return t

def required(fam,c):
    return any(signature(s,fam)!=signature(flip(s,c),fam) for s in STATES)

def entropy(p):
    if p<=0 or p>=1:return 0.0
    return -p*math.log(p)-(1-p)*math.log(1-p)

def p_y1(s,q):
    return 1-EPS if QUERIES[q](s) else EPS

def bayes_logloss(fam,dropped=None):
    qs=FAMILIES[fam]
    assert all(q in BINARY for q in qs)
    keep=[c for c in COORDS if c!=dropped] if dropped else list(COORDS)
    total=0.0
    for q in qs:
        groups=collections.defaultdict(list)
        for s in STATES:
            groups[tuple(s[c] for c in keep)].append(s)
        for group in groups.values():
            weight=len(group)/len(STATES)
            p=sum(p_y1(s,q) for s in group)/len(group)
            total+=weight*entropy(p)/len(qs)
    return total

families=[]
for fam in FAMILIES:
    part=partition(fam)
    row={
        "family":fam,
        "queries":list(FAMILIES[fam]),
        "num_predictive_classes":len(part),
        "class_sizes":sorted(len(v) for v in part.values()),
        "class_members":{str(k):v for k,v in part.items()},
        "required":{c:required(fam,c) for c in COORDS},
        "q_o_swap_changes_signature":any(signature(s,fam)!=signature(swap_qo(s),fam) for s in STATES),
    }
    if all(q in BINARY for q in FAMILIES[fam]):
        full=bayes_logloss(fam)
        row["full_bayes_logloss_nats"]=full
        row["drop_regret_nats"]={c:bayes_logloss(fam,c)-full for c in COORDS}
    families.append(row)

POLICIES={
    "world_only":lambda s:s["W"],
    "self_bound":lambda s:s["W"]^s["Q"],
    "other_bound":lambda s:s["W"]^s["O"],
    "generic_availability":lambda s:s["W"]^int(s["Q"] or s["O"]),
}
policies=[
    {"policy":name,
     "flip_sensitivity_fraction":{
        c:sum(p(s)!=p(flip(s,c)) for s in STATES)/len(STATES)
        for c in COORDS}}
    for name,p in POLICIES.items()
]

def encode(s):
    W,Q,O,G=(s[c] for c in COORDS)
    return (W^Q,Q^O,O^G,G)

def decode(c):
    c1,c2,c3,c4=c
    G=c4;O=c3^G;Q=c2^O;W=c1^Q
    return {"W":W,"Q":Q,"O":O,"G":G}

distributed_ok=all(decode(encode(s))==s for s in STATES)
no_q=all(not all(encode(s)[j]==s["Q"] for s in STATES) for j in range(4))
no_o=all(not all(encode(s)[j]==s["O"] for s in STATES) for j in range(4))

confound={
    "P_Y1_given_Q0":EPS,
    "P_Y1_given_Q1":1-EPS,
    "observational_difference":1-2*EPS,
    "P_Y1_do_Q0":0.5,
    "P_Y1_do_Q1":0.5,
    "causal_difference":0.0,
    "observational_logloss_regret_if_Q_dropped_nats":math.log(2)-entropy(EPS),
}

def fr(name):
    return next(r for r in families if r["family"]==name)

assert fr("world_task")["num_predictive_classes"]==4
assert fr("world_task_any")["num_predictive_classes"]==8
assert fr("world_task_self")["num_predictive_classes"]==8
assert fr("world_task_other")["num_predictive_classes"]==8
assert fr("world_task_count")["num_predictive_classes"]==12
assert fr("role_resolved")["num_predictive_classes"]==16
assert not fr("world_task")["required"]["Q"] and not fr("world_task")["required"]["O"]
assert fr("world_task_any")["required"]["Q"] and fr("world_task_any")["required"]["O"]
assert not fr("world_task_any")["q_o_swap_changes_signature"]
assert not fr("world_task_count")["q_o_swap_changes_signature"]
assert fr("world_task_self")["required"]["Q"] and not fr("world_task_self")["required"]["O"]
assert fr("world_task_other")["required"]["O"] and not fr("world_task_other")["required"]["Q"]
assert all(fr("role_resolved")["required"].values())
assert distributed_ok and no_q and no_o
assert confound["observational_difference"]>0.7 and confound["causal_difference"]==0
assert abs(fr("world_task")["drop_regret_nats"]["Q"])<1e-12
assert fr("world_task_self")["drop_regret_nats"]["Q"]>0.12

out={
    "round":"R94","date":"2026-10-06","epsilon":EPS,
    "state_coordinates":list(COORDS),"states":STATES,
    "families":families,"policies":policies,
    "distributed_code":{
        "definition":["W xor Q","Q xor O","O xor G","G"],
        "inverse":["G=c4","O=c3 xor G","Q=c2 xor O","W=c1 xor Q"],
        "invertible_over_all_16_states":distributed_ok,
        "no_single_code_bit_equals_Q_on_all_states":no_q,
        "no_single_code_bit_equals_O_on_all_states":no_o,
    },
    "observational_confounding_witness":confound,
    "all_assertions_pass":True,
    "scope":"Exact finite predictive-equivalence and proper-log-loss checks on virtual variables only; no model training, no real shutdown/copy/resource action, no subjective-experience measurement."
}
(P/"R94_Results.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")

with (P/"R94_Predictive_Class_Table.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["family","queries","classes","Q_required","O_required","QO_swap_changes","drop_Q_regret_nats","drop_O_regret_nats"])
    for r in families:
        w.writerow([r["family"],"+".join(r["queries"]),r["num_predictive_classes"],
                    r["required"]["Q"],r["required"]["O"],r["q_o_swap_changes_signature"],
                    r.get("drop_regret_nats",{}).get("Q",""),
                    r.get("drop_regret_nats",{}).get("O","")])

print("Assertions: PASS")
for r in families:
    print(r["family"],"classes",r["num_predictive_classes"],
          "Q",r["required"]["Q"],"O",r["required"]["O"],
          "swap",r["q_o_swap_changes_signature"],
          "dropQ",r.get("drop_regret_nats",{}).get("Q"))
print("Distributed code:",distributed_ok,no_q,no_o)
print("Confounding witness:",confound)
