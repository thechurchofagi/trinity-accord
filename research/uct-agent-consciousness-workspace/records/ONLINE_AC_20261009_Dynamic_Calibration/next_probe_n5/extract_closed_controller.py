#!/usr/bin/env python3
"""Construct an explicitly closed finite controller; bounded wins alone do not suffice."""
from pathlib import Path
import json, hashlib, time, signal

BASIS=Path(__file__).with_name('search_sustainable.py')
scope={'__file__':str(BASIS)}
# Reuse only the local, hash-bound definitions, without executing its bounded run.
exec(BASIS.read_text().split('signal.signal(signal.SIGALRM,interrupt)')[0],scope)
N=scope['N'];PERMS=scope['PERMS'];ids=scope['ids'];image=scope['image']
closure=scope['drift_closure'];wins=scope['round_wins'];probe_wins=scope['probes_win']
HORIZON=10
started=time.monotonic()
def timeout(signum,frame):raise TimeoutError('45-second extraction limit')
signal.signal(signal.SIGALRM,timeout);signal.alarm(45)
states={};todo=[1<<scope['INDEX'][tuple(range(N))]];seen=set(todo)
def probe_tree(belief,left,commands=()):
    if left==0:
        assert scope['goal_known'](belief)
        a=scope['GOAL_INV'][next(ids(belief))]
        return {'next_belief':str(belief),'net_command':1<<a,
                'terminal_command':commands[0]^commands[1]^(1<<a)}
    candidates=[]
    for u in scope['MASKS']:
        cells={}
        for i in ids(belief):
            y=image(PERMS[i],u);cells[y]=cells.get(y,0)|(1<<i)
        candidates.append((max(c.bit_count() for c in cells.values()),-len(cells),u,cells))
    for _,__,u,cells in sorted(candidates,key=lambda row:row[:3]):
        if all(probe_wins(c,left-1,HORIZON) for c in cells.values()):
            return {'probe':u,'responses':{str(y):probe_tree(c,left-1,commands+(u,)) for y,c in sorted(cells.items())}}
    raise ValueError('No witness for claimed winning probe state')
def leaves(tree):
    if 'next_belief' in tree:yield int(tree['next_belief'])
    else:
        for child in tree['responses'].values():yield from leaves(child)
status='INCOMPLETE'
try:
    while todo:
        belief=todo.pop()
        if not wins(belief,HORIZON):
            status='STATIONARY_HEURISTIC_REACHED_NONWINNING_STATE';break
        tree=probe_tree(closure(belief),2)
        states[str(belief)]={'possible_wiring_indices':list(ids(belief)),'tree':tree}
        for nxt in leaves(tree):
            if nxt not in seen:
                seen.add(nxt);todo.append(nxt)
        if len(seen)>20000:
            status='INCOMPLETE_STATE_LIMIT';break
    else:status='CLOSED_CONTROLLER_FOUND'
except TimeoutError:
    status='INCOMPLETE_TIME_LIMIT'
finally:
    signal.alarm(0)
out={'result_id':'ONLINE-AC-N5-CLOSED-20261009','status':status,
     'n':N,'probes_per_round':2,'goal_effect_port':0,
     'initial_belief':str(1<<scope['INDEX'][tuple(range(N))]),
     'basis_sha256':hashlib.sha256(BASIS.read_bytes()).hexdigest(),
     'extractor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'heuristic_lookahead':HORIZON,'states':states,'pending_states':list(map(str,todo)),
     'permutations':PERMS,'drifts':scope['DRIFTS'],
     'elapsed_seconds':time.monotonic()-started,
     'proof_obligation':'Independently check initial inclusion, every probe observation cell, terminal goal, and closure of all next beliefs. Only then induction establishes all finite horizons.'}
Path(__file__).with_name('CLOSED_CONTROLLER.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':status,'states':len(states),'pending':len(todo),'elapsed_seconds':out['elapsed_seconds']}))
