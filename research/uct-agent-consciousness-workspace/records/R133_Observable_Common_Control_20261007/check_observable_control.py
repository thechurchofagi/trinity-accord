"""Small exact witnesses, not a proof assistant or experimental evidence.

Compare support recursion with direct hidden-state policy-tree evaluation.
Independently compare covering with all observation partitions/decision rules.
"""
from fractions import Fraction as F
from itertools import product, combinations
from functools import lru_cache
from pathlib import Path
import json

checks = []
def check(name, ok):
    checks.append({'check': name, 'pass': bool(ok)})
    if not ok:
        raise AssertionError(name)

ACTIONS = ('a0', 'a1', 'p')
OBS = ('0', '1', '?')
STATES = tuple((m, s) for m in (0, 1) for s in ('start', 'goal', 'dead'))
GOAL = frozenset(x for x in STATES if x[1] == 'goal')

def kernel(mode, x, a):
    m, s = x
    if s != 'start':
        return ((x, '?', F(1)),)
    if a != 'p':
        return (((m, 'goal' if a == 'a'+str(m) else 'dead'), '?', F(1)),)
    if mode == 'preserving':
        return ((x, str(m), F(1)),)
    if mode == 'uninformative':
        return ((x, '?', F(1)),)
    if mode == 'destructive':
        return (((m, 'dead'), str(m), F(1)),)
    if mode == 'noisy':
        return ((x, str(m), F(4,5)), (x, str(1-m), F(1,5)))
    raise ValueError(mode)

@lru_cache(None)
def trees(h):
    # All deterministic observable policy trees, including early stop.
    if not h:
        return (('stop', ()),)
    return (('stop', ()),) + tuple(
        (a, branches) for a in ACTIONS for branches in product(trees(h-1), repeat=len(OBS))
    )

@lru_cache(None)
def direct_value(mode, x, tree):
    # Evolve one fixed hidden mechanism. This code does not use supports.
    a, branches = tree
    if a == 'stop':
        return F(x in GOAL)
    return sum(p*direct_value(mode, xp, branches[OBS.index(o)])
               for xp, o, p in kernel(mode, x, a))

@lru_cache(None)
def wins(mode, support, h):
    if support <= GOAL:
        return True
    if h == 0:
        return False
    for a in ACTIONS:
        successors = {o: frozenset(xp for x in support for xp, ob, p in kernel(mode, x, a)
                                  if ob == o and p > 0) for o in OBS}
        if all(wins(mode, b, h-1) for b in successors.values() if b):
            return True
    return False

subsets = [frozenset(c) for k in range(1, len(STATES)+1) for c in combinations(STATES, k)]
comparison_count = 0
for mode in ('preserving', 'uninformative', 'destructive', 'noisy'):
    for b in subsets:
        for h in range(3):
            brute = any(all(direct_value(mode, x, t) == 1 for x in b) for t in trees(h))
            assert brute == wins(mode, b, h), (mode, b, h)
            comparison_count += 1
check('support recursion agrees with exhaustive direct policy trees in 756 cases', comparison_count == 756)
initial = frozenset({(0, 'start'), (1, 'start')})
check('preserving diagnosis wins in two steps but not one', wins('preserving', initial, 2) and not wins('preserving', initial, 1))
check('uninformative and destructive probes cannot guarantee two-step success', not wins('uninformative', initial, 2) and not wins('destructive', initial, 2))
check('known individual mechanisms each win in one step', all(wins('uninformative', frozenset({x}), 1) for x in initial))
check('noisy diagnostic has exact best deterministic worst-case value four fifths, not one',
      max(min(direct_value('noisy', x, t) for x in initial) for t in trees(2)) == F(4,5)
      and not wins('noisy', initial, 2))
for mode in ('uninformative', 'destructive'):
    vectors = [(direct_value(mode, (0, 'start'), t), direct_value(mode, (1, 'start'), t)) for t in trees(2)]
    check(mode+' all deterministic policies have sum of two successes at most one', all(sum(v) <= 1 for v in vectors))
check('half-half immediate commitment attains minimax one half', all((F(m == 0)+F(m == 1))/2 == F(1,2) for m in (0,1)))

def partitions(xs):
    if not xs:
        yield ()
        return
    first, *rest = xs
    for p in partitions(rest):
        yield (frozenset({first}),)+p
        for j in range(len(p)):
            yield p[:j]+(p[j] | {first},)+p[j+1:]

parts = list(partitions([0, 1, 2]))
check('enumerated all five partitions of three candidates', len(parts) == 5)
family_count = cell_count = 0
for rows in product(range(1, 8), repeat=3):
    good = [{a for a in range(3) if rows[m] & (1 << a)} for m in range(3)]
    cover = min(k for k in range(1, 4) if any(all(any(a in good[m] for a in chosen) for m in range(3))
                                            for chosen in combinations(range(3), k)))
    possible_message_counts = []
    for p in parts:
        cell_ok = all(set.intersection(*(good[m] for m in cell)) for cell in p)
        direct_ok = any(all(decision[j] in good[m] for j, cell in enumerate(p) for m in cell)
                        for decision in product(range(3), repeat=len(p)))
        assert bool(cell_ok) == direct_ok
        if direct_ok:
            possible_message_counts.append(len(p))
        cell_count += 1
    assert min(possible_message_counts) == cover
    family_count += 1
check('cell criterion matches direct decisions for 1715 observation partitions', cell_count == 1715)
check('minimum message count equals action cover for all 343 nonempty-row 3x3 families', family_count == 343)
g = [{0,1}, {1,2}, {0,2}]
check('pairwise successful-action intersection does not imply full intersection', all(g[i]&g[j] for i,j in combinations(range(3),2)) and not set.intersection(*g))
good_parts = [p for p in parts if all(set.intersection(*({0,1,2}-{m} for m in cell)) for cell in p)]
two_cells = [p for p in good_parts if len(p) == 2]
check('three incomparable minimal two-cell successful partitions, no one-cell solution', len(two_cells) == 3 and all(len(p) >= 2 for p in good_parts))
for n in (2, 3, 10, 100):
    uniform = [F(1,n)]*n
    check(f'avoidance n={n}: uniform minimax witness and two-message decoder',
          min(1-p for p in uniform) == F(n-1,n)
          and all((1 if m==0 else 0) != m for m in range(n)))

actual = {(1,0), (0,1)}
envelope = set(product({0,1}, repeat=2))
check('persistent mechanisms always succeed but rectangular envelope fabricates failure',
      all(1 in t for t in actual) and (0,0) in envelope and (0,0) not in actual)
after_zero = {m for m,t in enumerate(((1,0),(0,1))) if t[0] == 0}
check('correct output update retains only the persistent compatible mechanism', after_zero == {1})
check('finite fair-trial failure remains positive at every checked horizon', all(F(1,2)**h > 0 for h in range(1,9)))

# Partial enabledness: each hidden mechanism has its own sole successful action.
menus = {0:{'a0'}, 1:{'a1'}}
check('separate enabled successful actions do not provide a common executable action',
      all(menus.values()) and not set.intersection(*menus.values()))
# Same support does not carry quantitative success weights.
check('identical outcome support can have distinct success probabilities',
      {o for o,p in [('success',F(9,10)),('failure',F(1,10))] if p>0}
      == {o for o,p in [('success',F(1,10)),('failure',F(9,10))] if p>0}
      and F(9,10) != F(1,10))

result = {'round':'R133', 'checks':checks, 'all_pass':True,
          'policy_comparisons':comparison_count, 'observation_partitions_checked':cell_count,
          'success_families_checked':family_count, 'horizon_two_policy_trees_per_probe_model':len(trees(2)),
          'arithmetic':'Python standard-library Fraction; exact integer/set operations',
          'scope':'Small finite mathematical checks; general statements rely on the written conditional proofs. Not proof-assistant certification or empirical evidence.'}
(Path(__file__).parent/'EXACT_CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','scope')}, indent=2))
print('Named checks passed:', len(checks))
