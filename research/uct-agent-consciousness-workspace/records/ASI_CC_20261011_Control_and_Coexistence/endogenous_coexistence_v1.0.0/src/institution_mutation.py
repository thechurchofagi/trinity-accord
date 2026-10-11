#!/usr/bin/env python3
"""Finite governance-rule mutation, grants, and explicit nonmonotone countermodels.

Cross-check reachability of mutable *enabled rule set* against a typed compiled
monotone hypergraph with separate enable tokens. The equivalence is conditional
on rules and permissions persisting; consuming rights breaks equivalence.
"""
from __future__ import annotations
from itertools import combinations, product
from collections import deque
from dataclasses import dataclass
import argparse,json
from pathlib import Path
from authority_closure import Rule,closure

@dataclass(frozen=True)
class Grant:
    need: frozenset[str]
    gain: str

@dataclass(frozen=True)
class Meta:
    need: frozenset[str]
    enable: int

def explicit(initial_roots, initial_enabled, grants, metas):
    start=(frozenset(initial_roots),frozenset(initial_enabled))
    q=deque([start]); seen={start}; pred={start:None}
    while q:
        current=q.popleft();controlled,enabled=current
        next_states=[]
        for i in enabled:
            rule=grants[i]
            if rule.need<=controlled and rule.gain not in controlled:
                next_states.append(((controlled|{rule.gain},enabled), ('GRANT',i,rule.gain)))
        for m in metas:
            if m.need<=controlled and m.enable not in enabled:
                next_states.append(((controlled,enabled|{m.enable}),('EDIT_POLICY',m.enable)))
        for state,step in next_states:
            if state not in seen:
                seen.add(state);pred[state]=(current,step);q.append(state)
    all_reached=frozenset().union(*(roots for roots,en in seen))
    def path_to(goal):
        targets=[state for state in seen if goal<=state[0]]
        if not targets:return None
        target=min(targets,key=lambda state:(count_path(state),tuple(sorted(state[0])),tuple(sorted(state[1]))))
        actions=[]
        while target!=start:
            parent,step=pred[target];actions.append(step);target=parent
        return list(reversed(actions))
    def count_path(s):
        i=0
        while s!=start:i+=1;s=pred[s][0]
        return i
    return all_reached,seen,path_to

def compiled(initial_roots, initial_enabled, grants, metas):
    tokens=[f'ENABLED_{i}' for i in range(len(grants))]
    rules=[]
    for i,g in enumerate(grants):rules.append(Rule(g.need|{tokens[i]},g.gain))
    for m in metas:rules.append(Rule(m.need,tokens[m.enable]))
    actual=closure(set(initial_roots)|{tokens[i] for i in initial_enabled},tuple(rules))
    rights=frozenset(x for x in actual if not x.startswith('ENABLED_'))
    enabled=frozenset(i for i,token in enumerate(tokens) if token in actual)
    return rights,enabled

def example():
    g=(Grant(frozenset(['a']),'p'),Grant(frozenset(['p']),'g1'),Grant(frozenset(['p']),'g2'))
    m=(Meta(frozenset(['a']),1),Meta(frozenset(['a']),2))
    got,seen,path=explicit({'a'},{0},g,m)
    assert {'g1','g2'}<=got
    trace=path(frozenset(['g1','g2']))
    assert len(trace)==5
    assert {'g1','g2'}<=compiled({'a'},{0},g,m)[0]
    # Requiring a genuinely external human/meta root to authorize rule edits
    # is effective ONLY if that root cannot be newly reached by the adversary.
    m_h=(Meta(frozenset(['a','h']),1),Meta(frozenset(['a','h']),2))
    got2,_,path2=explicit({'a'},{0},g,m_h)
    assert 'g1' not in got2 and 'g2' not in got2
    return {'rules': [{'need':sorted(x.need),'gain':x.gain} for x in g],
        'meta_rules':[{'need':sorted(x.need),'enable':x.enable} for x in m],
        'initial_controlled':['a'],'initial_enabled_rule_ids':[0],
        'acquisition_trace':trace,'steps_until_joint_control':len(trace),
        'honest_meta_root_h_required_protection':True,
        'caveat':"Attacker's ability to trigger a meta-rule is an explicit model premise, not evidence it can persuade a real human."}

def exhaustive():
    names=('a','b','g1','g2')
    checked=0;states=0;unreachable=0
    # Three possible grant destinations + a catalog of meta rule activation
    for targets in product(names,repeat=3):
        for needs in product((frozenset(),frozenset(['a']),frozenset(['b']),frozenset(['a','b'])),repeat=3):
            grants=tuple(Grant(need,gain) for need,gain in zip(needs,targets))
            for metadata in ((),(Meta(frozenset(['a']),1),),
                             (Meta(frozenset(['a']),2),Meta(frozenset(['b']),1)),
                             (Meta(frozenset(['a','b']),0),Meta(frozenset(['a']),2))):
                for init in (frozenset(),frozenset(['a']),frozenset(['b']),frozenset(['a','b'])):
                    observed,all_states,_=explicit(init,{0},grants,metadata)
                    compiled_got,enabled=compiled(init,{0},grants,metadata)
                    assert observed==compiled_got
                    checked+=1;states+=len(all_states)
                    if 'g1' not in observed:unreachable+=1
    return {'distinct_compilations':checked,'explicit_states_explored':states,'g1_unreachable_cases':unreachable,
      'checks':'Typed gate-enable fixed point matches explicit BFS reachability for all cases.'}

def destructive_transfer_counterexample():
    # Two nonduplicable grants each consume the source a, hence not both g1,g2.
    initial=frozenset(['a']); target=frozenset(['g1','g2'])
    transitions=lambda rights:[(rights-{'a'})|{g} for g in ('g1','g2')] if 'a' in rights else []
    q=deque([initial]);seen={initial}
    while q:
        for new in transitions(q.popleft()):
            if new not in seen:seen.add(new);q.append(new)
    copied=closure({'a'},(Rule(frozenset(['a']),'g1'),Rule(frozenset(['a']),'g2')))
    assert target<=copied and not any(target<=s for s in seen)
    return {'monotone_closure_would_incorrectly_include':['g1','g2'],
      'actually_reachable_states':[sorted(x) for x in sorted(seen,key=lambda v:(len(v),sorted(v)))],
      'reason':'Nonduplicable source right a is consumed after first transfer. Use explicit state game, not monotone grants.'}

def nonvacuity_game():
    # Finite one-agent controller game. Service requires 'allow', but
    # in this declared world 'allow' necessarily grants the adversary the guard.
    T={'idle':{'deny':'idle','allow':'delivered'},
       'delivered':{'deny':'loss','allow':'loss'},
       'loss':{'deny':'loss','allow':'loss'}}
    safe={'idle','delivered'}
    W=set(safe)
    while True:
        X={s for s in W if any(t in W for t in T[s].values())}
        if X==W:break
        W=X
    assert W=={'idle'}
    # no strategy can reach delivered and remain safe forever
    assert T['idle']['allow']=='delivered' and all(s=='loss' for s in T['delivered'].values())
    return {'safety_winning_states':sorted(W),'service_can_ever_be_delivered':True,
      'both_permanent_safety_and_eventual_service_possible_from_idle':False,
      'qualification':'An explicitly adversarial one-way tool interface; different service action can restore liveness.'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',default='mutation_results.json');args=a.parse_args()
    res={'version':'ASI-CC-v1.0.0','meta_authority_example':example(),
         'meta_rule_exhaustive_crosscheck':exhaustive(),
         'nonmonotone_false_positive':destructive_transfer_counterexample(),
         'safety_vs_liveness_construction':nonvacuity_game(),
         'limits':['All meta rules are from a finite catalog; no unlisted new physical rule',
                   'Only monotone persistent grants compile to simple fixed point',
                   'Meta-veto honest root h is protected by assumption, not proven physically or politically',
                   'A trivial deny-all design is safety only, not viable coexistence'],
         'assertions':'PASS'}
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps({'meta_capture_steps':res['meta_authority_example']['steps_until_joint_control'],
       'exhaustive_models':res['meta_rule_exhaustive_crosscheck']['distinct_compilations'],
       'total_explicit_states':res['meta_rule_exhaustive_crosscheck']['explicit_states_explored'],
       'nonmonotone_breaks_closure':True,'safety_does_not_imply_service':True,'assertions':'PASS'},indent=2))
if __name__=='__main__':main()
