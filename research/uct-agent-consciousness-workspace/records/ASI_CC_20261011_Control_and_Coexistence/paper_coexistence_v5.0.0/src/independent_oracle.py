#!/usr/bin/env python3
"""Independent explicit plan enumeration; does not import root_pareto certificate.

For each reported vector, directly try all 16 pre-arm subsets against all
attacker/world combinations generating this vector. A serial 2-root effect
veto is separately assumed for m >= 2 (for m==1, failure is unavoidable).
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def feasible_via_direct_plan_enum(m,caps):
    sensor_roots=tuple(range(m)) if m<=3 else (0,1,2)
    world_by_report={}
    for failed_primary in range(4):
        true_bit=failed_primary//2
        for attacked_root in (None,)+tuple(range(m)):
            for attacked_output in (0,1):
                if attacked_root is None and attacked_output!=0:continue
                out=[]
                for root in sensor_roots:
                    if root==attacked_root and attacked_output:out.append(1-true_bit)
                    else:out.append(true_bit)
                world_by_report.setdefault(tuple(out),set()).add((failed_primary,attacked_root))
    if m<2:return False,None
    response={}
    for report,realities in world_by_report.items():
        allowed=[]
        for mask in range(16):
            chosen=frozenset(i for i in range(4) if mask>>i&1)
            if all((failed in chosen and (sum(caps)-(caps[attacked] if attacked is not None else 0))>=len(chosen))
                   for failed,attacked in realities):
                allowed.append(mask)
        if not allowed:return False,{'report':report,'possible_worlds':sorted((x,-1 if y is None else y) for x,y in realities),'no_safe_plan':True}
        response[str(report)]=allowed[0]
    return True,response

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='oracle_results.json');a=parser.parse_args()
    trials=0;best={};fail_count={}
    for m in (1,2,3,4):
        optimum=None;count=0;best_cap=None
        for cap in itertools.product(range(9),repeat=m):
            ok,response=feasible_via_direct_plan_enum(m,cap)
            trials+=1
            if ok:
                count+=1
                if optimum is None or sum(cap)<optimum:
                    optimum=sum(cap);best_cap=cap
        best[m]={'min_nominal_capacity':optimum,'witness':best_cap,'working_vectors':count}
    assert [best[i]['min_nominal_capacity'] for i in (1,2,3,4)]==[None,8,3,3]
    result={'version':'PR-v5.0.0','method':'brute enumerate all 16 pre-arm subsets per possible sensor-vector cell, without importing certificate implementation',
            'capacity_vectors_checked':trials,'results':best,'assertions':'PASS',
            'limitations':['One-bit truth per actual root and at most one corruption','Prearmed route sets; no state-dependent downstream router','All prescribed gates assumed serial and independent whenever m>=2']}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
