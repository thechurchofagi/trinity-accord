"""Exact finite checks for SB20261008; no experiential outcomes are simulated."""
from itertools import product
import json
from pathlib import Path


def episode(a, r, mode, report=True):
    s = a
    j = s if mode else r
    c, v = j, a
    u = int(c == v)
    trace = (j, c, v, u) + ((u,) if report else ())
    edges = [('A', 'S'), ('A', 'V'), ('J', 'C'), ('C', 'U'), ('V', 'U')]
    edges.append(('S' if mode else 'R', 'J'))
    if report:
        edges.append(('U', 'Q'))
    return {'trace': trace, 'edges': edges, 'G': mode, 'U': u}


def reaches(edges, start, end):
    seen, todo = {start}, [start]
    while todo:
        src = todo.pop()
        for a, b in edges:
            if a == src and b not in seen:
                seen.add(b)
                todo.append(b)
    return end in seen


checks = []
def record(name, condition, cases):
    assert condition, name
    checks.append({'name': name, 'passed': True, 'cases': cases})


all_cases = [(a, r, m, episode(a, r, m)) for a, r, m in product((0, 1), repeat=3)]
record('active current-command feedback path equals mode',
       all(reaches(e['edges'], 'A', 'J') == bool(m) for a, r, m, e in all_cases), 8)
record('current command still reaches comparator in replay',
       all(reaches(episode(a, r, 0)['edges'], 'A', 'U') for a, r in product((0, 1), repeat=2)), 4)
record('live feedback changes with current command at fixed replay',
       all(episode(0, r, 1)['trace'][0] != episode(1, r, 1)['trace'][0] for r in (0, 1)), 2)
record('replay feedback independent of current command at fixed replay',
       all(episode(0, r, 0)['trace'][0] == episode(1, r, 0)['trace'][0] for r in (0, 1)), 2)
record('matched traces with and without reports',
       all(episode(a, a, 1, q)['trace'] == episode(a, a, 0, q)['trace']
           for a, q in product((0, 1), (False, True))), 4)
record('mismatched replay fails selected trace match',
       all(episode(a, 1-a, 1)['trace'] != episode(a, 1-a, 0)['trace'] for a in (0, 1)), 2)
record('candidate predictions disagree in matched replay only',
       all(episode(a, a, 1)['G'] == episode(a, a, 1)['U'] == 1 and
           episode(a, a, 0)['G'] == 0 and episode(a, a, 0)['U'] == 1 for a in (0, 1)), 2)
down = {'J', 'C', 'V', 'U', 'Q'}
record('downstream edge restrictions identical',
       all([(x,y) for x,y in episode(a,a,1)['edges'] if x in down and y in down] ==
           [(x,y) for x,y in episode(a,a,0)['edges'] if x in down and y in down] for a in (0,1)), 2)
# Exhaust all binary evidence functions on the four reachable complete traces.
traces = sorted({e['trace'] for _, _, _, e in all_cases})
equality_tests = 0
for outputs in product((0, 1), repeat=len(traces)):
    evidence = dict(zip(traces, outputs))
    for a in (0,1):
        assert evidence[episode(a,a,1)['trace']] == evidence[episode(a,a,0)['trace']]
        equality_tests += 1
record('all binary functions of reachable trace give equal matched evidence', True, equality_tests)
record('upstream mode reveals condition while not deciding phenomenal bridge',
       episode(1,1,1)['G'] != episode(1,1,0)['G'], 1)
# Independent bodily relation witness: identical feature/target binding, opposite source side.
body = [{'source': s, 'target': 'right', 'feature': 1, 'binding': 'right'} for s in ('left','right')]
record('crossed limb source preserves stipulated feature and target binding',
       body[0]['source'] != body[1]['source'] and
       all(body[0][k] == body[1][k] for k in ('target','feature','binding')), 1)
out = {'schema':'uct-sb-exact-checks/1.0', 'model_checks':len(checks), 'checks':checks,
       'finite_rows':[{'A':a,'R':r,'M':m,**e} for a,r,m,e in all_cases],
       'reachable_traces':len(traces), 'evidence_function_evaluations':equality_tests,
       'scope':'Finite stipulated controller only. No human data, no F_A/F_O/F_T values measured or inferred.'}
Path(__file__).with_name('MODEL_RESULTS.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({'checks':len(checks),'finite_rows':len(all_cases),'evidence_evaluations':equality_tests}))
