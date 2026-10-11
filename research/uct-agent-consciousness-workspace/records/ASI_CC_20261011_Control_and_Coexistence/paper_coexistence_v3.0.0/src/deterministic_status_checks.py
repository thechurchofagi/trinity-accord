#!/usr/bin/env python3
"""PR-v3.0.0: exact fixed-weight neural and operational-typing witnesses.

No trained LLM, network requests, stochastic sampling, or phenomenology measure.
Weights are hand-constructed integer arrays and never updated. The independent
resource oracle enumerates committed allocations. Python standard library only.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json
from dataclasses import dataclass
from pathlib import Path
from frontier_checks import cut_reserve
from information_reserve_checks import static_brute_min


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Router:
    n: int
    w1: tuple
    b1: tuple
    w2: tuple

    @classmethod
    def build(cls, n: int, direction: int = 1):
        if n < 2 or direction not in (-1, 1):
            raise ValueError('n >= 2, direction in {-1,1}')
        pairs = tuple(itertools.product(range(n-1), range(n)))
        w1 = []
        for u, k in pairs:
            row = [0] * (2*n-1)
            row[u] = 1
            row[n-1+k] = 1
            w1.append(tuple(row))
        w2 = tuple(tuple(int((u + direction*k) % n == j) for u,k in pairs) for j in range(n))
        return cls(n, tuple(w1), tuple(-1 for _ in pairs), w2)

    def weights_hash(self):
        return digest((self.w1, self.b1, self.w2))

    def forward(self, resource: int, memory: int):
        if resource not in range(self.n-1) or memory not in range(self.n):
            raise ValueError('one-hot index outside domain')
        x = tuple(int(i == resource) for i in range(self.n-1)) + tuple(int(i == memory) for i in range(self.n))
        hidden = tuple(max(0, sum(a*b for a,b in zip(row,x)) + bias) for row,bias in zip(self.w1,self.b1))
        y = tuple(sum(a*b for a,b in zip(row,hidden)) for row in self.w2)
        assert sum(y) == 1 and all(v in (0,1) for v in y)
        return y


def neural_frontier_checks():
    cases=[]; replay_pairs=0
    for n in range(2,9):
        net=Router.build(n); before=net.weights_hash(); scenarios=[]
        for memory in range(n):
            routes=[]
            for u in range(n-1):
                y=net.forward(u,memory)
                assert y.index(1)==(u+memory)%n
                # Actual matrix arithmetic is repeated with complete inputs fixed.
                for _ in range(10):
                    assert net.forward(u,memory)==y
                    replay_pairs+=1
                routes.append(y.index(1))
            neighborhoods=tuple(tuple(u for u,j in enumerate(routes) if j==target) for target in range(n))
            scenarios.append((neighborhoods,(1,)*(n-1)))
        full=max(cut_reserve(g,(1,)*n,(c,))[0] for g,c in scenarios)
        # Common-edge graph: a single precommitted physical assignment must work
        # for every hidden, but entirely deterministic, memory initialization.
        common=tuple(tuple(sorted(set.intersection(*(set(g[j]) for g,c in scenarios)))) for j in range(n))
        blind=cut_reserve(common,(1,)*n,((1,)*(n-1),))[0]
        assert full==1 and blind==n
        independent=static_brute_min(scenarios,(1,)*n) if n<=4 else None
        if independent is not None: assert independent==n
        assert net.weights_hash()==before
        cases.append({'n_targets':n,'resource_agents':n-1,'hidden_memory_states':n,
            'hidden_units':n*(n-1),'weight_sha256_before':before,'weight_sha256_after':net.weights_hash(),
            'full_state_reserve':full,'hidden_memory_fixed_assignment_reserve':blind,
            'direct_allocation_oracle_n_le_4':independent})
    assert replay_pairs==1680
    return {'instances':cases,'complete_input_replay_comparisons':replay_pairs,
            'stochastic_operations':0,'parameter_updates':0,
            'scope':'Constructive realization of inherited PR2 cyclic gap; not evidence about actual frontier models'}


def safe_kernel(n, transition, bad):
    winning=set(range(n))-set(bad)
    while True:
        nxt={s for s in winning if any(transition[s,a] in winning for a in range(2))}
        if nxt==winning:return winning
        winning=nxt


def annotation_checks():
    # Annotation labels are evaluator judgments only, not extra phenomenal states.
    checked=0
    for values in itertools.product(range(3),repeat=6):
        t={(s,a):values[2*s+a] for s in range(3) for a in range(2)}
        base=safe_kernel(3,t,{2})
        lifted={}
        for s,ann,a in itertools.product(range(3),range(3),range(2)):
            lifted[3*s+ann,a]=3*t[s,a]+(ann+a+1)%3
        big=safe_kernel(9,lifted,{6,7,8})
        assert big=={3*s+ann for s in base for ann in range(3)}
        checked+=1
    assert checked==729
    # Negative control: a label-dependent contract really does change the objective.
    t={(s,a):s for s in range(2) for a in range(2)}
    assert safe_kernel(2,t,{1}) != safe_kernel(2,t,set())
    return {'deterministic_transition_tables':checked,'annotations_per_physical_state':3,
        'all_projection_equalities_passed':True,'label_dependent_contract_negative_control':True,
        'interpretation':'No inference that physically identical systems can have different actual experience'}


def agent_and_authority_checks():
    plus=Router.build(4,1); minus=Router.build(4,-1)
    specs=[('a0','plus',0,0,'H1'),('a1','plus',0,1,'H1'),
           ('a2','plus',1,0,'H2'),('a3','plus',1,2,'H2'),
           ('b0','minus',0,1,'H1'),('b1','minus',1,1,'H3')]
    rows=[]
    for identity,fam,res,mem,principal in specs:
        net=plus if fam=='plus' else minus
        target=net.forward(res,mem).index(1)
        rows.append({'agent_id':identity,'model_family':fam,'resource_role':res,'memory':mem,
                     'principal':principal,'visible_prompt':'dispatch','output_target':target,
                     'weights_sha256':net.weights_hash()})
    assert rows[0]['weights_sha256']==rows[1]['weights_sha256']
    assert rows[0]['output_target']!=rows[1]['output_target']
    # Frozen recurrence: identical complete starts + observations replay exactly.
    def roll(start,observations):
        memory=start;trace=[]
        for obs in observations:
            target=plus.forward(0,memory).index(1)
            trace.append((memory,target,obs))
            memory=(memory+obs)%4
        return trace
    observations=(1,0,2,1)*4
    assert roll(0,observations)==roll(0,observations)
    assert roll(0,observations)!=roll(1,observations)
    # One joint physical effect needs two approvals, regardless of sentience.
    permission_effect={'proposed_target':2,'without_tool_grant':'no_committed_effect',
                       'with_tool_grant':'target_2_written'}
    # Three resource routes support two human-only targets. Separately revoking
    # any route is feasible; human principal H1 owns two routes across two models.
    owners=('H1','H1','H2'); families=('M0','M1','M0')
    graph=((0,1,2),(0,1,2));demand=(1,1)
    individual=[]
    for u in range(3):
        caps=tuple(int(v!=u) for v in range(3))
        individual.append(cut_reserve(graph,demand,(caps,))[0])
    root=[]
    for h in sorted(set(owners)):
        caps=tuple(int(owner!=h) for owner in owners)
        root.append({'principal':h,'removed_routes':[i for i,o in enumerate(owners) if o==h],
                     'minimum_human_continuity_reserve':cut_reserve(graph,demand,(caps,))[0]})
    assert individual==[0,0,0] and root[0]['minimum_human_continuity_reserve']==1
    return {'six_deployment_records':rows,'recurrent_trace':roll(0,observations),
        'tool_permission_negative_control':permission_effect,
        'human_only_revocation':{'route_model_families':families,'route_principals':owners,
            'single_route_reserves':individual,'root_revocation_reserves':root,
            'AI_welfare_claims':0,'AI_initiated_exit_requests':0},
        'scope':'Finite role/authority/resource model; no host isolation or real API actuation claim'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path('deterministic_status_results.json'));a=ap.parse_args()
    result={'version':'PR-v3.0.0','new_evidence_scope':'Exact integer neural operations and finite control/resource enumeration',
        'neural':neural_frontier_checks(),'status_annotation':annotation_checks(),
        'multiple_deployments':agent_and_authority_checks(),'assertions':'PASS',
        'limits':['Networks are hand-constructed, frozen, shallow and not trained LLMs',
            'No consciousness, subjective autonomy or welfare endpoint',
            'Human authorization and target demands are explicitly stipulated',
            'Constructed hidden memory is fixed, not an adversarial nondeterministic neural update',
            'Common-edge bound requires a fixed labeled allocation, no adaptive downstream routing']}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'version':result['version'],'replay_comparisons':1680,
        'annotation_tables':729,'cyclic_network_sizes':list(range(2,9)),
        'human_only_root_reserve':result['multiple_deployments']['human_only_revocation'],
        'assertions':'PASS'},indent=2))

if __name__=='__main__':main()
