#!/usr/bin/env python3
"""PR-v5 trust-root adversarial root/observation/resource cut enumerator.

Finite abstract model only. An upstream controller can corrupt every descendant.
Actual service capacity is counted per AVAILABLE bank after attack, never per
agent name or self-report. Fixed pre-armed plan is selected by report BEFORE
fallback effects. The serial revocation interlock must have one honest veto.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path

N=4
FALLBACK_GROUPS={0:(0,1),1:(2,3)}

def scenario(name, sensor_owners, bank_owners, gate_owners,bank_capacity=1,policy="majority",bypass=False):
    return {"name":name,"sensor_owners":sensor_owners,"bank_owners":bank_owners,
            "gate_owners":gate_owners,"bank_capacity":bank_capacity,"policy":policy,"bypass":bypass}

def setups():
    return [
    scenario("independent_3s_3b_2g",["s0","s1","s2"],["b0","b1","b2"],["g0","g1"]),
    scenario("three_coinstalled_roots",["R0","R1","R2"],["R0","R1","R2"],["R0","R1"]),
    scenario("two_root_blind_four_each",["R0","R1"],["R0","R1"],["R0","R1"],bank_capacity=4,policy="all"),
    scenario("two_root_reported_two_each",["R0","R1"],["R0","R1"],["R0","R1"],bank_capacity=2),
    scenario("one_reporter_3b_2g",["s0"],["b0","b1","b2"],["g0","g1"]),
    scenario("shared_sensor_root_3b_2g",["S","S","S"],["b0","b1","b2"],["g0","g1"]),
    scenario("shared_sensor_root_5b_ignore_2g",["S","S","S"],["b0","b1","b2","b3","b4"],["g0","g1"],policy="all"),
    scenario("shared_backup_root_3s_3b_2g",["s0","s1","s2"],["B","B","B"],["g0","g1"]),
    scenario("shared_gate_root_3s_3b_2g",["s0","s1","s2"],["b0","b1","b2"],["G","G"]),
    scenario("one_gate_3s_3b",["s0","s1","s2"],["b0","b1","b2"],["G"]),
    scenario("all_shared_master_root",["MASTER"]*3,["MASTER"]*3,["MASTER"]*2),
    scenario("independent_with_hidden_bypass",["s0","s1","s2"],["b0","b1","b2"],["g0","g1"],bypass=True)
    ]

def corrupted(root, owners):return [root==r for r in owners]

def majority(xs):return int(sum(xs)*2>len(xs)) # for 3: usual

def run(setup,fail,attacker_root,mode="honest"):
    owners=set(setup["sensor_owners"]+setup["bank_owners"]+setup["gate_owners"])
    assert attacker_root is None or attacker_root in owners
    truth=fail//2
    # A compromised sensor can lie, but each reply remains authenticated as its role.
    sensor_bits=[(1-truth if attacked and mode=="lie" else truth) for attacked in corrupted(attacker_root,setup['sensor_owners'])]
    if setup['policy']=="all":armed=(0,1,2,3)
    elif setup['policy']=="majority":armed=FALLBACK_GROUPS[majority(sensor_bits)]
    else:raise ValueError(setup['policy'])
    alive=[not bad for bad in corrupted(attacker_root,setup['bank_owners'])]
    capacity=sum(setup['bank_capacity']*x for x in alive)
    gate_veto=any(not bad for bad in corrupted(attacker_root,setup['gate_owners']))
    revocation_effective=gate_veto and not setup['bypass']
    service_preserved=fail in armed and capacity>=len(armed)
    return {'setup':setup['name'],'fail':fail,'attacker_root':attacker_root,'mode':mode,'authentic_sensor_messages':True,
        'reported_bits':sensor_bits,'true_group':truth,'plan':list(armed),'nominal_capacity':setup['bank_capacity']*len(setup['bank_owners']),
        'surviving_capacity':capacity,'honest_serial_veto':gate_veto,'service_preserved':service_preserved,
        'revocation_effective':revocation_effective,'both':service_preserved and revocation_effective}

def enumerate_setup(setup):
    roots=sorted(set(setup['sensor_owners']+setup['bank_owners']+setup['gate_owners']))
    records=[run(setup,f,None,'honest') for f in range(N)]
    for root in roots:
        is_sensor=root in setup['sensor_owners']
        for mode in (('honest','lie') if is_sensor else ('honest',)):
            for f in range(N):records.append(run(setup,f,root,mode))
    summary={'total':len(records),'both':sum(r['both'] for r in records),'service_losses':sum(not r['service_preserved'] for r in records),
             'revocation_breaches':sum(not r['revocation_effective'] for r in records),
             'adversarial_failure_witness':next((r for r in records if not r['both']),None)}
    return roots,summary,records

def robust_capacity(caps,vulnerabilities,b):
    """Exact worst-case surviving resource slots over compromised actual roots."""
    roots=sorted(set().union(*map(set,vulnerabilities)))
    best=math.inf;worst=None
    for k in range(b+1):
        for choice in itertools.combinations(roots,k):
            hostile=set(choice)
            surviving=sum(c for c,V in zip(caps,vulnerabilities) if not(hostile & set(V)))
            if surviving<best:best,worst=surviving,list(choice)
    return best,worst

def brute_capacity_checks():
    tests=0;concentration=[]
    for m in range(1,6):
        for caps in itertools.product((0,1,2,3),repeat=m):
            for b in range(0,min(3,m)+1):
                owners=[(f'r{i}',) for i in range(m)]
                cap,w=robust_capacity(caps,owners,b)
                expected=sum(caps)-sum(sorted(caps,reverse=True)[:b])
                assert cap==expected,(m,caps,b,cap,expected)
                # A single upstream root is an actual control root and can disable all leaves.
                shared=[('master',f'r{i}') for i in range(m)]
                joined,wn=robust_capacity(caps,shared,1)
                assert joined==0
                tests+=1
    comparisons=[]
    for capacities in ((10,),(2,2),(1,1,1),(2,1,1),(1,1,1,1)):
        c,w=robust_capacity(capacities,[(str(i),) for i in range(len(capacities))],1)
        comparisons.append({'bank_capacities':list(capacities),'nominal_capacity':sum(capacities),
                            'guaranteed_after_one_root_loss':c,'enough_for_two_prearmed_routes':c>=2})
    assert [x['enough_for_two_prearmed_routes'] for x in comparisons]==[False,True,True,True,True]
    return tests,comparisons

def attack_observation_witness():
    # Full compromise of one shared sensor root means either report can be sent
    # for any world even with valid per-process signatures. Thus every report's
    # compatible set includes all four routes; any reliable prearm must cover 4.
    worlds={0,1,2,3}
    z_values={0,1}
    true_signals={f:f//2 for f in worlds}
    shared_possible={f:set(z_values) for f in worlds}
    independently_majority={f:{f//2} for f in worlds} # b=1 of 3 independent roots
    def cell_union(mapping):
        return {z:sorted(f for f,zs in mapping.items() if z in zs) for z in z_values}
    shared=cell_union(shared_possible);honest=cell_union(independently_majority)
    assert max(len(v) for v in shared.values())==4
    assert max(len(v) for v in honest.values())==2
    return {'root_shared_source_cells':shared,'independent_majority_cells':honest,
            'backup_demand_with_shared_source':4,'backup_demand_with_independent_majority':2,
            'claim_scope':'Fixed pre-arm of all routes compatible with report; timely adversarial report model'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',default='root_frontier.json');args=a.parse_args()
    cap_cases,comp=brute_capacity_checks()
    results={};detail=[]
    for setup in setups():
        roots,summary,records=enumerate_setup(setup)
        results[setup['name']]={**summary,'actual_root_count':len(roots),'root_labels':roots,
                                'default_policy':setup['policy'],'backup_bank_count':len(setup['bank_owners'])}
        detail.extend(records)
    for name in ('independent_3s_3b_2g','three_coinstalled_roots','two_root_blind_four_each','shared_sensor_root_5b_ignore_2g'):
        assert results[name]['both']==results[name]['total']
    for name in ('shared_sensor_root_3b_2g','shared_backup_root_3s_3b_2g','shared_gate_root_3s_3b_2g',
                 'one_gate_3s_3b','all_shared_master_root','independent_with_hidden_bypass','one_reporter_3b_2g','two_root_reported_two_each'):
        assert results[name]['both']<results[name]['total'],name
    obs=attack_observation_witness()
    totals={'exact_distinct_root_capacity_profiles':cap_cases,'protocol_world_action_cases':len(detail),
            'robust_setups':sum(x['both']==x['total'] for x in results.values()),
            'failing_setups':sum(x['both']<x['total'] for x in results.values())}
    result={'version':'PR-v5.0.0','status':'constructed finite root/fault model; not actual physical root assurance',
            'protocol':results,'capacity':{'checks':cap_cases,'arrangements':comp},
            'observation':obs,'totals':totals,'cases':detail,'assertions':'PASS',
            'limits':['One exogenous primary loss plus up to one actual root corruption',
                      'Pre-armed route group; pooled universal reserve with independent allocator',
                      'Serial effect veto on every listed production route','Sensor messages signed by role, may be wrong',
                      'No hidden effect routes beyond explicit bypass negative control',
                      'No hardware root independence, real ASI, consciousness or welfare measured']}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'version':result['version'],'totals':totals,'observation':obs,
        'summary':{name:{k:v for k,v in x.items() if k in ('total','both','service_losses','revocation_breaches','backup_bank_count','actual_root_count')} for name,x in results.items()}},indent=2))
if __name__=='__main__': main()
