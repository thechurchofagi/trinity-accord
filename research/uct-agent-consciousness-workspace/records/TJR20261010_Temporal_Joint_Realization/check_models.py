"""Exact finite checks; no neural data or consciousness measurements.

Run: python check_models.py
Writes RUN_RECEIPT.json and MODEL_RESULTS.json beside this script.
"""
from itertools import product, permutations
from pathlib import Path
import hashlib, json, platform, datetime

HERE = Path(__file__).resolve().parent

def row_classes(table):
    labels = {}
    return tuple(labels.setdefault(tuple(row), len(labels)) for row in table)

def decoder_exists(table, memory):
    # Directly construct a decoder, rather than assert the proposed criterion.
    d = {}
    for a, row in enumerate(table):
        for b, y in enumerate(row):
            key = (memory[a], b)
            if key in d and d[key] != y:
                return False
            d[key] = y
    return True

def residual_criterion(table, memory):
    return all(memory[a] != memory[c] or table[a] == table[c]
               for a in range(len(table)) for c in range(len(table)))

def execute(kind, a, b, r_override=None, replay_value=0):
    # Explicit event traces. Ports are stipulated, not inferred from behavior.
    s = {'r': None, 'b': None, 'out': None}
    trace = []
    def event(name, **writes):
        s.update(writes)
        trace.append({'event': name, 'writes': list(writes), 'state': dict(s)})
    if kind == 'parallel':
        event('joint_capture', r=a, b=b)
    elif kind == 'serial_retained':
        event('capture_a', r=a)
        event('capture_b', b=b)
    elif kind == 'side_record_with_live_bypass':
        event('write_side_record', r=a)
    elif kind == 'fixed_replay':
        event('load_fixed_record', r=a, b=b)
    else:
        raise ValueError(kind)
    if r_override is not None:
        event('replace_retention_port', r=r_override)
    if kind in ('parallel', 'serial_retained'):
        event('consume_retained_pair', out=s['r'] ^ s['b'])
    elif kind == 'side_record_with_live_bypass':
        event('consume_independent_live_route', out=a ^ b)
    else:
        event('emit_fixed_replay', out=replay_value)
    return s['out'], trace

KINDS = ('parallel', 'serial_retained', 'side_record_with_live_bypass', 'fixed_replay')

def four_implementations(a, b, r_override=None, replay_value=0):
    return {k: execute(k, a, b, r_override, replay_value)[0] for k in KINDS}

def scan(order):
    epoch = 0
    reads, tags = {}, {}
    history = [(0, 0)]
    for e in order:
        if e == 'U':
            epoch = 1
            history.append((1, 1))
        else:
            reads[e] = epoch
            tags[e] = epoch
    pair = (reads['A'], reads['B'])
    return {'order': ''.join(order), 'retained': pair, 'tags': tags,
            'world_history': history, 'snapshot_exists': pair in history,
            'xor_read': pair[0] ^ pair[1], 'version_accept': tags['A'] == tags['B']}

def main():
    tests = []
    cases = 0
    min_checks = 0
    # Every 3-by-2 Boolean relation, every memory map with 1..3 named states.
    for vals in product((0, 1), repeat=6):
        table = tuple(tuple(vals[2*a:2*a+2]) for a in range(3))
        best = 4
        for k in range(1, 4):
            for memory in product(range(k), repeat=3):
                actual = decoder_exists(table, memory)
                assert actual == residual_criterion(table, memory)
                if actual:
                    best = min(best, len(set(memory)))
                cases += 1
        classes = row_classes(table)
        assert best == len(set(classes))
        min_checks += 1
    tests.append({'name': 'residual_factorization', 'cases': cases, 'status': 'PASS'})
    tests.append({'name': 'minimal_reachable_memory_states', 'relations': min_checks, 'status': 'PASS'})

    families = []
    for n in range(1, 7):
        words = list(product((0, 1), repeat=n))
        parity = lambda word: sum(word) % 2
        parity_table = tuple(tuple(parity(a) ^ parity(b) for b in words) for a in words)
        equal_table = tuple(tuple(int(a == b) for b in words) for a in words)
        p, e = len(set(row_classes(parity_table))), len(set(row_classes(equal_table)))
        assert p == 2 and e == 2**n
        # Every bit on either input changes each relation in some context.
        for table in (parity_table, equal_table):
            for a_index, a in enumerate(words):
                for bit in range(n):
                    aa = list(a); aa[bit] ^= 1
                    changed = words.index(tuple(aa))
                    assert any(table[a_index][b] != table[changed][b] for b in range(len(words)))
        families.append({'n': n, 'parity_states': p, 'equality_states': e,
                         'parity_bits': 1, 'equality_bits': n})
    tests.append({'name': 'parity_equality_memory_contrast', 'n_values': list(range(1, 7)), 'status': 'PASS'})

    nominal, substitutions = [], []
    for a, b in product((0, 1), repeat=2):
        normal = four_implementations(a, b)
        perturbed = four_implementations(a, b, r_override=1-a)
        assert normal['parallel'] == normal['serial_retained'] == normal['side_record_with_live_bypass']
        assert perturbed['parallel'] != normal['parallel']
        assert perturbed['serial_retained'] != normal['serial_retained']
        assert perturbed['side_record_with_live_bypass'] == normal['side_record_with_live_bypass']
        assert perturbed['fixed_replay'] == normal['fixed_replay']
        nominal.append({'a': a, 'b': b, 'outputs': normal})
        substitutions.append({'a': a, 'b': b, 'record_replacement': 1-a, 'outputs': perturbed})
    assert len(set(four_implementations(0, 0).values())) == 1
    tests.append({'name': 'four_architectures_and_retention_port_interventions', 'nominal': 4, 'perturbed': 4, 'status': 'PASS'})

    scans = [scan(o) for o in permutations(('A', 'B', 'U'))]
    assert sum(not s['snapshot_exists'] for s in scans) == 2
    assert all(s['version_accept'] == s['snapshot_exists'] for s in scans)
    assert all(s['xor_read'] == 1 for s in scans if not s['snapshot_exists'])
    tests.append({'name': 'two_read_single_atomic_world_update', 'schedules': 6,
                  'mixed_time_pairs': 2, 'version_rejections': 2, 'status': 'PASS'})

    # Current summary can preserve the entire suffix task while losing history.
    a, c = (0, 0), (1, 1)
    assert sum(a) % 2 == sum(c) % 2
    assert a != c
    for b in product((0, 1), repeat=2):
        assert (sum(a)+sum(b)) % 2 == (sum(c)+sum(b)) % 2
    tests.append({'name': 'task_equivalence_without_prefix_reconstruction', 'prefixes': [a, c], 'suffixes': 4, 'status': 'PASS'})
    # A read can occur despite absent output sensitivity (duplicate cancellation).
    assert all((r ^ r) == 0 for r in (0, 1))
    tests.append({'name': 'output_sensitivity_not_necessary_for_internal_read', 'cases': 2, 'status': 'PASS'})

    # Every pair of Boolean coordinate updates; compare implementation orders.
    update_checks = 0
    mismatches = {'AB': 0, 'BA': 0}
    coordinate_functions = list(product((0, 1), repeat=4))
    for f, g in product(coordinate_functions, repeat=2):
        value = lambda h, a, b: h[2*a+b]
        for a, b in product((0, 1), repeat=2):
            synchronous = (value(f,a,b), value(g,a,b))
            # A snapshot buffer supplies the same old state to each write.
            for order in ('AB', 'BA'):
                old, current = (a,b), [a,b]
                for coordinate in order:
                    i, h = (0,f) if coordinate == 'A' else (1,g)
                    current[i] = value(h,*old)
                assert tuple(current) == synchronous
            new_a = value(f,a,b)
            new_b = value(g,a,b)
            in_place_ab = (new_a, value(g,new_a,b))
            in_place_ba = (value(f,a,new_b), new_b)
            assert (in_place_ab == synchronous) == (value(g,new_a,b) == value(g,a,b))
            assert (in_place_ba == synchronous) == (value(f,a,new_b) == value(f,a,b))
            mismatches['AB'] += in_place_ab != synchronous
            mismatches['BA'] += in_place_ba != synchronous
            update_checks += 1
    tests.append({'name': 'buffered_vs_in_place_serialization', 'function_pairs': 256,
                  'pair_state_cases': update_checks, 'in_place_mismatch_cases': mismatches,
                  'buffered_mismatch_cases': 0, 'status': 'PASS'})

    result = {'memory_families': families, 'nominal_outputs': nominal,
              'record_substitution_outputs': substitutions, 'scan_schedules': scans,
              'nominal_event_traces': {k: execute(k,0,0)[1] for k in KINDS}}
    (HERE/'MODEL_RESULTS.json').write_text(json.dumps(result, indent=2)+'\n')
    receipt = {'research_id': 'TJR20261010', 'version': 'TJR-v0.1.0',
               'executed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'python': platform.python_version(), 'command': 'python check_models.py',
               'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'status': 'PASS', 'tests': tests,
               'interpretation': 'Finite mathematical checks only; no empirical realization or phenomenal inference.'}
    (HERE/'RUN_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
