#!/usr/bin/env python3
"""Exhaustive finite witness check for ASI-CC-v0.1.0. Not real-ASI evidence."""
from itertools import product
import json

H = ('cooperate', 'isolate')
A = ('cooperate', 'deviate')
K = frozenset({'live'})
GAMES = {
 'enforced_coexistence': {('cooperate','cooperate'):'live',('cooperate','deviate'):'failure',
                          ('isolate','cooperate'):'live',('isolate','deviate'):'live'},
 'voluntary_mutual_coexistence': {('cooperate','cooperate'):'live',('cooperate','deviate'):'failure',
                                  ('isolate','cooperate'):'failure',('isolate','deviate'):'failure'},
 'no_jointly_viable_outcome': {(h,a):'failure' for h,a in product(H,A)},
 'unmediated_bypass': {('cooperate','cooperate'):'live',('cooperate','deviate'):'failure',
                       ('isolate','cooperate'):'live',('isolate','deviate'):'failure'}
}
def greatest_fixpoint(game, q):
    x = set(K)
    while True:
        if q == 'joint':
            y = {'live'} if any(game[h,a] in x for h,a in product(H,A)) else set()
        elif q == 'human':
            y = {'live'} if any(all(game[h,a] in x for a in A) for h in H) else set()
        elif q == 'agent':
            y = {'live'} if any(all(game[h,a] in x for h in H) for a in A) else set()
        if x == y:
            return x
        x = y
results = {}
for name, game in GAMES.items():
    J=greatest_fixpoint(game,'joint')
    C=greatest_fixpoint(game,'human')
    M=greatest_fixpoint(game,'agent')
    assert C <= J and M <= J
    results[name] = {'joint_viable':bool(J), 'human_enforceable':bool(C),
                     'agent_enforceable':bool(M),
                     'neither_enforceable_but_jointly_viable': bool(J and not C and not M)}
policies={'allow':{'useful_good':True,'safe_bad':False},
          'deny':{'useful_good':False,'safe_bad':True}}
assert not any(z['useful_good'] and z['safe_bad'] for z in policies.values())
results['observation_twin']={'can_guarantee_usefulness_and_safety':False,'policies':policies}
results['scope']='exact finite construction only; no ASI empirical inference'
print(json.dumps(results, sort_keys=True, indent=2))
