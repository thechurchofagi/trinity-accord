"""Exact finite checks of future editability; Python standard library only.

Mathematics uses integers for F_2^n with coordinate 0 the least significant bit.
The partition-refinement oracle does not use the period/essential-variable formulas.
This is a finite software experiment, not a neural-model experiment.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import platform
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def assign(x, i, b):
    return (x & ~(1 << i)) | (b << i)


def ops(n, family):
    if family == 'toggle':
        return [lambda x, i=i: x ^ (1 << i) for i in range(n)]
    return [lambda x, i=i, b=b: assign(x, i, b)
            for i in range(n) for b in (0, 1)]


def partition_minimum(table, operations):
    """Coarsest stable refinement of the output partition, independent oracle."""
    colors = tuple(table)
    while True:
        signatures = [(colors[x], tuple(colors[op(x)] for op in operations))
                      for x in range(len(table))]
        unique = {s: i for i, s in enumerate(sorted(set(signatures)))}
        new = tuple(unique[s] for s in signatures)
        if all((colors[x] == colors[y]) == (new[x] == new[y])
               for x in range(len(table)) for y in range(len(table))):
            return len(set(new))
        colors = new


def output_closed(table, operations):
    for op in operations:
        seen = {}
        for x, z in enumerate(table):
            value = table[op(x)]
            if z in seen and seen[z] != value:
                return False
            seen[z] = value
    return True


def classify(n, table):
    states = range(1 << n)
    periods = [h for h in states if all(table[x ^ h] == table[x] for x in states)]
    essential = [i for i in range(n) if any(table[x] != table[x ^ (1 << i)] for x in states)]
    affine = any(all(table[x] == (b ^ ((a & x).bit_count() % 2)) for x in states)
                 for a in states for b in (0, 1))
    toggles, assignments = ops(n, 'toggle'), ops(n, 'assign')
    t = partition_minimum(table, toggles)
    a = partition_minimum(table, assignments)
    assert t == (1 << n) // len(periods)
    assert a == 1 << len(essential)
    assert output_closed(table, toggles) == affine
    assert output_closed(table, assignments) == (len(essential) <= 1)
    return t, a, affine, len(essential) <= 1


def parity(x):
    return x.bit_count() % 2


class Worker:
    """Consumer with an explicit state and no source lookup.

    summary/helper consumers receive only the parity at construction. Helpers
    are passed a per-edit old bit by an OUTSIDE oracle, recorded by the caller.
    report_only has full input but deliberately does not install an edit.
    """
    def __init__(self, mode, payload):
        self.mode = mode
        self.state = payload

    def read(self):
        return parity(self.state) if self.mode in ('full', 'report_only') else self.state

    def step(self, op, old_bit=None):
        kind, i, b = op
        before = self.state
        if self.mode in ('full', 'report_only'):
            proposed = self.state ^ (1 << i) if kind == 'toggle' else assign(self.state, i, b)
            answer = parity(proposed)
            if self.mode == 'full':
                self.state = proposed
        elif kind == 'toggle':
            answer = self.state ^ 1
            self.state = answer
        else:
            # summary's guess old_bit=0 is optimal only under the balanced
            # uniform one-step prior used here; it is not a general algorithm.
            old = 0 if self.mode == 'summary' else old_bit
            assert old in (0, 1)
            answer = self.state ^ old ^ b
            self.state = answer
        return {'op': list(op), 'old_bit_from_outside': old_bit,
                'before': before, 'reported_answer': answer, 'after': self.state}


def worker_experiments(n=4):
    states = range(1 << n)
    operations = [('toggle', i, None) for i in range(n)] + [
        ('assign', i, b) for i in range(n) for b in (0, 1)]
    one = {}
    for mode in ('full', 'summary', 'helper', 'report_only', 'corrupt_helper'):
        counts = Counter()
        for x in states:
            for op in operations:
                kind, i, b = op
                target = x ^ (1 << i) if kind == 'toggle' else assign(x, i, b)
                actualmode = 'helper' if mode == 'corrupt_helper' else mode
                w = Worker(actualmode, x if mode in ('full', 'report_only') else parity(x))
                old = ((x >> i) & 1) if actualmode == 'helper' else None
                if mode == 'corrupt_helper':
                    old ^= 1
                r = w.step(op, old)
                counts[kind + '_total'] += 1
                counts[kind + '_correct'] += r['reported_answer'] == parity(target)
        one[mode] = dict(counts)
    assert one['summary']['assign_correct'] * 2 == one['summary']['assign_total']
    assert one['helper']['assign_correct'] == one['helper']['assign_total']
    assert one['corrupt_helper']['assign_correct'] == 0
    assert all(v['toggle_correct'] == v['toggle_total'] for v in one.values())

    edits = [o for o in operations if o[0] == 'assign']
    sequential = {}
    witness = None
    for mode in ('full', 'summary', 'helper', 'report_only'):
        counts = Counter()
        for x in states:
            for word in itertools.product(edits, repeat=2):
                w = Worker(mode, x if mode in ('full', 'report_only') else parity(x))
                true_state = x
                trace = []
                for step, op in enumerate(word):
                    _, i, b = op
                    old = (true_state >> i) & 1 if mode == 'helper' else None
                    true_state = assign(true_state, i, b)
                    r = w.step(op, old)
                    r['target'] = parity(true_state)
                    trace.append(r)
                    counts[f'step_{step + 1}_total'] += 1
                    counts[f'step_{step + 1}_correct'] += r['reported_answer'] == r['target']
                if mode == 'report_only' and trace[-1]['reported_answer'] != trace[-1]['target'] and witness is None:
                    witness = {'initial_state': x, 'coordinate_convention': 'bit i has weight 2**i', 'trace': trace}
        sequential[mode] = dict(counts)
    for mode in ('full', 'helper'):
        assert sequential[mode]['step_2_correct'] == sequential[mode]['step_2_total']
    assert sequential['report_only']['step_1_correct'] == sequential['report_only']['step_1_total']
    assert sequential['report_only']['step_2_correct'] < sequential['report_only']['step_2_total']

    # The paired-history impossibility witness is independent of our guesser.
    balance = {}
    for z, i, b in itertools.product((0, 1), range(n), (0, 1)):
        c = Counter(parity(assign(x, i, b)) for x in states if parity(x) == z)
        assert c[0] == c[1]
        balance[f'{z},{i},{b}'] = dict(c)
    return {'n': n, 'one_step': one, 'committed_two_step': sequential,
            'report_only_witness': witness, 'summary_conditioned_target_balance': balance}


def protocol_examples(n=4):
    # Future commands deliberately contain no old value. Original facts are
    # held by evaluator; only the condition's allowed payload goes to a model.
    result = []
    for x in range(1 << n):
        for i, b in itertools.product(range(n), (0, 1)):
            result.append({'example_id': f'n{n}_x{x}_i{i}_b{b}',
                'consumer_payload_summary_condition': {'parity': parity(x)},
                'future_command': {'operation': 'assign', 'coordinate': i, 'value': b,
                                   'semantics': 'commit to current scenario'},
                'evaluator_only': {'initial_bits_lsb_first': [(x >> j) & 1 for j in range(n)],
                                   'target_parity': parity(assign(x, i, b)),
                                   'helper_old_bit': (x >> i) & 1}})
    return result


def main():
    finite = []
    for n in (1, 2, 3):
        counts = Counter()
        joint = Counter()
        for packed in range(1 << (1 << n)):
            table = tuple((packed >> x) & 1 for x in range(1 << n))
            t, a, affine, unary = classify(n, table)
            counts['functions_checked'] += 1
            counts['output_closed_for_toggles'] += affine
            counts['output_closed_for_assignments'] += unary
            joint[f'{t},{a}'] += 1
        assert counts['output_closed_for_toggles'] == 1 << (n + 1)
        assert counts['output_closed_for_assignments'] == 2 + 2 * n
        finite.append({'n': n, **dict(counts), 'toggle_assign_minimum_state_counts': dict(sorted(joint.items()))})
    named = []
    for n in range(2, 7):
        for name, table in [('parity', tuple(parity(x) for x in range(1 << n))),
                            ('and', tuple(int(x == (1 << n) - 1) for x in range(1 << n)))]:
            t, a, _, _ = classify(n, table)
            named.append({'name': name, 'n': n, 'toggle_states': t, 'assignment_states': a})
    result = {'research_id': 'REV20261010', 'scope': 'EXACT_FINITE_SOFTWARE_ONLY',
              'function_checks': finite, 'named_functions': named,
              'workers': worker_experiments(), 'neural_models_tested': 0,
              'human_participants': 0, 'status': 'PASS'}
    out = ROOT/'MODEL_RESULTS.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    examples = ROOT/'PROTOCOL_EXAMPLES.jsonl'
    examples.write_text(''.join(json.dumps(x, separators=(',', ':'))+'\n' for x in protocol_examples()))
    receipt = {'command': 'python3 revision_reuse/check_revision.py', 'python': platform.python_version(),
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'result_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
               'examples_sha256': hashlib.sha256(examples.read_bytes()).hexdigest(),
               'boolean_functions_exhausted': sum(x['functions_checked'] for x in finite),
               'protocol_examples': 128, 'status': 'PASS',
               'not_established': ['Neural performance', 'Physical organization identity', 'Phenomenal classification', 'Global mathematical priority']}
    (ROOT/'RUN_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'receipt': receipt, 'workers': result['workers']}, indent=2))


if __name__ == '__main__':
    main()
