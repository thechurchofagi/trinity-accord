#!/usr/bin/env python3
"""Extract two readable proof templates from the frozen controller certificate.

This is a witness formatter, not the independent verifier or a new search.
The certificate is identified by SHA-256; impossible observation branches are
absent. Composition is right-to-left; a tuple p lists command-to-effect images.
"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
source = HERE / 'CLOSED_CONTROLLER.json'
certificate = json.loads(source.read_text())
permutations = certificate['permutations']

def set_label(bits):
    members = [str(i) for i in range(5) if bits & (1 << i)]
    return '{' + ','.join(members) + '}' if members else 'empty'

def cycle_label(p):
    seen, cycles = set(), []
    for start in range(5):
        if start in seen:
            continue
        cycle, current = [], start
        while current not in seen:
            seen.add(current)
            cycle.append(current)
            current = p[current]
        if len(cycle) > 1:
            cycles.append('(' + ' '.join(map(str, cycle)) + ')')
    return ''.join(cycles) or 'I'

templates, lines = [], [
    '# Two canonical five-port calibration templates', '',
    'Goal: effect port 0. A set denotes a binary vector. Each row gives all',
    'remaining current wirings after its two observations. The terminal command',
    'is the symmetric difference of the two probes and the listed net port.',
    'An empty second probe uses no additional information. Cycle notation acts',
    'on command labels as their current effect images; products compose right to left.', '',
]
for name, belief_key in [('known_identity', '1'), ('identity_or_swap_34', '3')]:
    state = certificate['states'][belief_key]
    first = state['tree']
    rows = []
    for y1, second in first['responses'].items():
        for y2, leaf in second['responses'].items():
            bits = int(leaf['next_belief'])
            posterior = [p for i, p in enumerate(permutations) if bits & (1 << i)]
            rows.append({
                'first_effect': int(y1), 'second_probe': second['probe'],
                'second_effect': int(y2), 'posterior_wirings': posterior,
                'net_command': leaf['net_command'],
                'terminal_command': leaf['terminal_command'],
            })
    template = {
        'name': name,
        'old_belief': [permutations[i] for i in state['possible_wiring_indices']],
        'first_probe': first['probe'], 'rows': rows,
    }
    templates.append(template)
    lines.extend([
        f'## {name}', '', f'First probe: {set_label(first["probe"])}.', '',
        '| First effect | Second probe | Second effect | Exact posterior | Net command port |',
        '|---|---|---|---|---|',
    ])
    for row in rows:
        posterior = ', '.join(cycle_label(p) for p in row['posterior_wirings'])
        lines.append('| ' + ' | '.join([
            set_label(row['first_effect']), set_label(row['second_probe']),
            set_label(row['second_effect']), posterior,
            set_label(row['net_command']),
        ]) + ' |')
    lines.append('')
out = {
    'result_version': 'ONLINE-AC-RESULT-v0.2.0',
    'n': 5, 'goal_effect_port': 0,
    'source_certificate_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'formatter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'status': 'EXTRACTED_WITNESS_REQUIRES_INDEPENDENT_VALIDATION',
    'templates': templates,
    'transport': {
        'old_representative': 'rho is a selected member of the known belief, not an oracle for the actual wiring',
        'effect_bijection': 'f(0)=g; for a two-wiring belief {rho,(rs)rho}, f(3)=r, f(4)=s',
        'command_bijection': 'c = inverse(rho) composed with f',
        'canonical_observation': 'inverse(f) applied to the actual effect vector',
        'canonical_current_wiring': 'inverse(f) composed with actual_current_wiring composed with c',
        'invariant_family': 'singleton beliefs and pairs differing by one transposition of two non-goal effect ports',
        'family_size_for_fixed_goal': 480,
    },
}
(HERE / 'CANONICAL_TEMPLATES.json').write_text(json.dumps(out, indent=2) + '\n')
(HERE / 'CANONICAL_TABLES.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'templates': len(templates), 'observation_leaves': sum(len(t['rows']) for t in templates),
                  'old_drift_worlds': 33, 'status': out['status']}))
