"""Exact finite proof witness; no sampling, training, or empirical inference."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

S = list(product((0, 1), repeat=3))
def transition(s):
    z = s[2]
    return {(u, u ^ z, z): F(1, 2) for u in (0, 1)}
def push(s, projection):
    out = {}
    for t, probability in transition(s).items():
        k = projection(t)
        out[k] = out.get(k, F(0)) + probability
    return {k: v for k, v in out.items() if v}
def closed(states, projection):
    laws = {}
    for s in states:
        key, law = projection(s), push(s, projection)
        if key in laws and laws[key] != law:
            return False
        laws[key] = law
    return True

px, py, pair = lambda s: s[0], lambda s: s[1], lambda s: s[:2]
assert all(sum(transition(s).values()) == 1 for s in S)
assert closed(S, px) and closed(S, py)
assert not closed(S, pair)
assert push((0,0,0), pair) != push((0,0,1), pair)
invariant = [s for s in S if s[2] == (s[0] ^ s[1])]
assert all(t in invariant for s in S for t in transition(s))
assert closed(invariant, pair)
split_blocks = 0
for x, y in product((0, 1), repeat=2):
    assert push((x,y,0), pair) != push((x,y,1), pair)
    split_blocks += 1
assert closed(S, lambda s: s)
# Minimal refinement is forced because all original two-element blocks split.
assert split_blocks == 4
result = {
    'states': len(S), 'nonzero_transition_entries': sum(len(transition(s)) for s in S),
    'arithmetic': 'fractions.Fraction', 'random_samples': 0,
    'marginal_x_closed': True, 'marginal_y_closed': True,
    'joint_closed_on_all_eight_states': False,
    'joint_closed_on_four_state_invariant_subset': True,
    'joint_partition_blocks': 4, 'blocks_forced_to_split': split_blocks,
    'minimum_stable_refinement_blocks': 8,
    'witness_rows': {
        str(s): {str(k): str(v) for k,v in push(s,pair).items()}
        for s in [(0,0,0),(0,0,1)]
    },
    'scope': 'finite exact countermodel; not proof-assistant validation or empirical evidence'
}
out = Path(__file__).with_name('JOINT_CLOSURE_CHECK.json')
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
