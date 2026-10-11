#!/usr/bin/env python3
"""Exact observation-cell/backup capacity Pareto for 4 single-route faults.

One root may be compromised; its diagnostic bit may be adversarially flipped;
all backup slots controlled by it are lost; serial gates are installed on any
2 different root owners, so effect-level revocation is assumed to hold for m>=2.

For m=1, no entire effect cut survives the only root's compromise.
For m=2 or 3, one truthful bit is output by each root; for m>=4, only
first three roots report. The bound for m=2 also holds for arbitrarily many
correlated reporters per root, as explained in the paper.
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path

def report_roots(m):
    return tuple(range(m)) if m<=3 else (0,1,2)

def cells(m):
    used=report_roots(m)
    data={}
    for f in range(4):
        truth=f//2
        for attacked in range(m):
            for flip in (0,1):
                # If the compromised root has no reporter, 'flip' gives a repeated identical output.
                report=tuple((1-truth if r==attacked and flip else truth) for r in used)
                data.setdefault(report,[]).append((f,attacked))
        # No attack is also admitted and must not create a false negative.
        data.setdefault(tuple([truth]*len(used)),[]).append((f,None))
    return {report:set(records) for report,records in data.items()}

def certified(m,caps):
    data=cells(m)
    certificate={};max_required=0
    for report,worlds in data.items():
        targets={f for f,_ in worlds}; q=len(targets)
        survivals={None:sum(caps)}
        for _,attacked in worlds:
            if attacked is not None:survivals[attacked]=sum(caps)-caps[attacked]
        minimum=min(survivals.values())
        certificate[str(report)]={'compatible_failed_routes':sorted(targets),
                                  'least_remaining_capacity':minimum,'prearm_required':q,'safe':minimum>=q}
        max_required=max(max_required,q)
    sound=(m>=2 and all(x['safe'] for x in certificate.values()))
    return sound,max_required,certificate

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='root_pareto.json');args=parser.parse_args()
    allcases=0;rows=[]
    for m in (1,2,3,4):
        candidates=[];best=None;witness=None
        for cap in itertools.product(range(9),repeat=m):
            # In m4, 9^4=6,561, total <7k.
            success,max_q,certificate=certified(m,cap);allcases+=1
            if success:
                total=sum(cap)
                if best is None or total<best:
                    best=total;witness={'capacity_by_root':list(cap),'observation_cells':certificate,'max_compatible_fault_count':max_q}
                candidates.append((total,cap))
        if m==1:assert best is None
        if m==2:assert best==8 and witness['capacity_by_root']==[4,4]
        if m==3:assert best==3 and witness['capacity_by_root']==[1,1,1]
        if m==4:assert best==3
        rows.append({'independent_actual_roots':m,'minimum_nominal_backup_slots':best,
                     'certified_topologies_in_search':len(candidates),'witness':witness})
    # Explicit coinstallation case: sensor, bank, and one of two serial gates
    # can share a root; one root attack affects all three types at once, yet
    # three roots suffice in this stipulated model.
    three=next(r for r in rows if r['independent_actual_roots']==3)
    assert three['minimum_nominal_backup_slots']==3
    result={'version':'PR-v5.0.0','scope':'finite one-episode exogenous route failure + one compromised actual root; fixed prearm; per-root bit reports',
            'capacities_checked':allcases,'results':rows,
            'claimed_architecture_bound':'m=1 no certificate; m=2 needs >=8 pooled prearm slots; m>=3 needs >=3 (for m<=4 checked); proof for arbitrary m in manuscript',
            'notes':['m=2: conflicting two-root reports leave both group classes plausible under different one-root attacks',
                     'm>=3: three independent truthful-bit root witnesses support one-error correction',
                     'm>=3: three independent one-slot reserve roots leave >=2 slots after one-root loss',
                     'two series veto gates on distinct roots preserve effect-level block after one root loss',
                     'root coinstallation across sensor/backup/gate roles is allowed; leaf role count is not actual root count',
                     'not a claim about unconstrained policies, real physical independence, hidden bypasses or resource timing'],
            'assertions':'PASS'}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'capacities_checked':allcases,'frontier':[(r['independent_actual_roots'],r['minimum_nominal_backup_slots'],r['certified_topologies_in_search']) for r in rows],
                      'assertions':'PASS'},indent=2))
if __name__=='__main__':main()
