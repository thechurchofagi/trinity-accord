"""Exact bounded witnesses, not a proof assistant or human-data validation."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
checks = []
def check(name, condition, scope):
    assert condition, name
    checks.append(dict(name=name, passed=True, scope=scope))

def source_q(xs):
    o = F(3) ** (2 * sum(xs) - len(xs))
    return o / (1 + o)

def action_q(zs):
    return F(3 ** sum(zs), 3 ** sum(zs) + 2 ** len(zs))

def joint_posterior(xs, zs, coupled=False):
    weights = {}
    for h, k in product(range(2), repeat=2):
        w = F(1, 2) if coupled and h == k else F(0) if coupled else F(1, 4)
        for x in xs:
            p = F(3, 4) if h else F(1, 4)
            w *= p if x else 1 - p
        for z in zs:
            p = F(3, 4) if k else F(1, 2)
            w *= p if z else 1 - p
        weights[h, k] = w
    total = sum(weights.values())
    return {hk: w / total for hk, w in weights.items()}

histories = [s for n in range(5) for s in product(range(2), repeat=n)]
correct = support = True
for xs, zs in product(histories, repeat=2):
    post = joint_posterior(xs, zs)
    correct &= sum(p for (h, k), p in post.items() if h) == source_q(xs)
    correct &= sum(p for (h, k), p in post.items() if k) == action_q(zs)
    support &= all(p > 0 for p in post.values())
check('posterior_vs_direct_joint_Bayes', correct, '961 paired histories, each channel length 0..4, exact rational arithmetic')
check('all_latent_pairs_retain_positive_posterior', support, 'same 961 histories; general proof in P3')
rows = []
for xs, zs in product([(1, 1), (0, 0)], repeat=2):
    qo, qa = source_q(xs), action_q(zs)
    rows.append(dict(X=xs, Z=zs, q_O=str(qo), q_A=str(qa), consumers=[int(qo >= F(2, 3)), int(qa >= F(2, 3))]))
check('four_consumer_pairs', {tuple(r['consumers']) for r in rows} == set(product(range(2), repeat=2)), 'T=2 theta=2/3 with one common contract')
check('wrong_high_high_event_probability', F(1, 4)**2 * F(1, 2)**2 == F(1, 64), 'conditional on H=K=0; unconditional joint event 1/256')
check('missing_is_not_failure', action_q(()) == F(1, 2) and action_q((0,)) == F(1, 3), 'no intervention vs one failed match')
post = joint_posterior((1, 1), (), coupled=True)
check('dependent_prior_breaks_separate_updates', sum(p for (h, k), p in post.items() if k) == F(9, 10) != action_q(()), 'H=K prior; source evidence must inform K')
check('installed_memory_copy_changes_consumer', source_q((0, 0)) < F(2, 3) <= source_q((1, 1)) and action_q((1, 1)) == F(9, 13), 'source state copy; action state and ports unchanged')
for T in range(2, 7):
    states = [(n, r) for n in range(T+1) for r in range(n+1)]
    assert len(states)**2 == ((T+1)*(T+2)//2)**2
check('finite_state_bound', True, 'count enumeration T=2..6; general counting expression in M')
check('all_success_outputs_strictly_distinct', all(source_q((1,)*n) < source_q((1,)*(n+1)) for n in range(30)), '30 comparisons only; unbounded impossibility proved in P4')
# Observational confounding: U=V,Y=V with fair exogenous V;
# intervening on U leaves Y=V, unlike the observational perfect match.
obs_match = sum(F(1, 2) for v in range(2) if v == v)
do_match = sum(F(1, 4) for v, u in product(range(2), repeat=2) if v == u)
check('observation_does_not_replace_intervention', obs_match == 1 and do_match == F(1, 2), 'binary common-cause countermodel, outside M randomized protocol')
# Factorization has an independently given target, not a target defined from J.
J = ['same', 'same', 'other']
Fgood, Fbad = [0, 0, 1], [0, 1, 1]
factorable = lambda f: all(J[i] != J[j] or f[i] == f[j] for i in range(3) for j in range(3))
check('selected_target_fiber_test', factorable(Fgood) and not factorable(Fbad), 'three abstract configurations; no phenomenal target claimed')
result = dict(status='BOUNDED_EXACT_CHECKS_PASS', checks=checks, check_count=len(checks), four_rows=rows,
              proof_assistant_certified=False, physical_or_phenomenal_validation=False)
(HERE/'VALIDATION.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(dict(status=result['status'], check_count=len(checks), paired_histories=len(histories)**2)))
