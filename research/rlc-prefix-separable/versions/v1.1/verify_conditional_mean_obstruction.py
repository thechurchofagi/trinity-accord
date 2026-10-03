"""Exact actual-additive obstruction to uniform doubling of a parent's minimum.

Complete Q4 chamber coverage is inherited from the certified dependency.
The Q5 obstruction itself is a direct integer certificate, with no solver.
"""
from pathlib import Path
import sys, json, hashlib
sys.path.insert(0, str(Path(__file__).resolve().parent / 'dependencies'))
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import positive_chambers, order_and_scores, counts

def main():
    parent = 50
    best = 16
    chamber_count = 0
    witness = None
    for w in positive_chambers(4):
        order = order_and_scores(w)[0]
        for z in range(16):
            C = counts([rank(x ^ z, 4, parent) for x in order])[1]
            chamber_count += 1
            if C < best:
                best, witness = C, {'positive_weights': w, 'reflection': z}
    assert best == 6 and chamber_count == 5376
    w = (16, 1, 10, 8, 12)
    p, scores = order_and_scores(w)
    assert len(set(scores)) == 32
    assert all((a >> 1) != (b >> 1) for a, b in zip(p, p[1:] + p[:1]))
    child_counts = [counts([rank(x, 5, (parent << 8) | low) for x in p])[:2]
                    for low in range(256)]
    assert set(child_counts) == {(10, 10)}
    out = {'status': 'VERIFIED_ACTUAL_ADDITIVE_CONDITIONAL_MEAN_OBSTRUCTION',
           'parent_dimension': 4, 'parent_mask': parent,
           'parent_exact_min_cyclic_turns': best,
           'signed_parent_chambers_checked': chamber_count,
           'parent_min_witness': witness,
           'child_weights': w, 'child_order': p, 'child_sorted_scores': scores,
           'fresh_bottom_comparisons': 0, 'all_fresh_assignments_checked': 256,
           'every_child_linear_runs': 10, 'every_child_cyclic_turns': 10,
           'conditional_cyclic_mean': 10, 'twice_parent_minimum': 12,
           'refuted': 'For EVERY paired parent and EVERY actual additive child sweep, E_fresh C >= 2 min_v C(parent along pi_v).',
           'scope': 'Refutes the exact any-parent doubling lemma only. Neither the original existence theorem nor a recurrence allowing losses is refuted.',
           'coverage': 'Q4 completeness inherited; Q5 is one actual generic integer-weight witness, exhaustively checked over its 256 fresh assignments.'}
    out['audit_sha256'] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()
    Path('conditional_mean_obstruction_verification.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out))

if __name__ == '__main__':
    main()
