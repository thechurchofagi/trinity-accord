#!/usr/bin/env python3
"""Bounded exact safety search for the next unsolved ONLINE-AC case.

Nature chooses one transposition/identity before each round, fixed in the round.
Two physically enacted probes return full effect vectors; the final command
compensates their effects. All-success histories have no extra information in
the forced terminal response. Belief sets contain every still possible wiring.
This searches exact zero-error deadline guarantees, not an average probability.
"""
from itertools import permutations, combinations
from functools import lru_cache
from pathlib import Path
import json, time, signal, hashlib

N=5
PERMS=tuple(permutations(range(N)))
INDEX={p:i for i,p in enumerate(PERMS)}
MASKS=range(1<<(N-1))  # complement probes induce identical partitions
GOAL_INV=tuple(p.index(0) for p in PERMS)
def image(p,u):return sum(1<<p[i] for i in range(N) if u>>i&1)
IMAGES=tuple(tuple(image(p,u) for u in MASKS) for p in PERMS)
DRIFTS=[tuple(range(N))]
for a,b in combinations(range(N),2):
    p=list(range(N));p[a],p[b]=p[b],p[a];DRIFTS.append(tuple(p))
MOVES=tuple(tuple(INDEX[tuple(d[x] for x in p)] for d in DRIFTS) for p in PERMS)
START=time.monotonic()
COUNTS={'round_states':0,'probe_states':0,'query_candidates':0}
RESULTS=[]

def ids(bits):
    while bits:
        low=bits&-bits;yield low.bit_length()-1;bits-=low

@lru_cache(None)
def drift_closure(belief):
    out=0
    for i in ids(belief):
        for j in MOVES[i]:out|=1<<j
    return out

@lru_cache(None)
def partitions(belief,u):
    cells={}
    for i in ids(belief):
        y=IMAGES[i][u];cells[y]=cells.get(y,0)|(1<<i)
    return tuple(sorted(cells.values(),key=int.bit_count,reverse=True))

@lru_cache(None)
def goal_known(belief):
    return len({GOAL_INV[i] for i in ids(belief)})==1

@lru_cache(None)
def round_wins(belief,rounds):
    COUNTS['round_states']+=1
    return probes_win(drift_closure(belief),2,rounds)

@lru_cache(None)
def probes_win(belief,left,rounds):
    COUNTS['probe_states']+=1
    if left==0:
        return goal_known(belief) and (rounds==1 or round_wins(belief,rounds-1))
    # These are the entire legal binary-vector query partitions, ordered only
    # for efficiency; equivalent/complement partitions are tested once.
    choices=set(partitions(belief,u) for u in MASKS)
    for cells in sorted(choices,key=lambda c:(max(x.bit_count() for x in c),-len(c))):
        COUNTS['query_candidates']+=1
        if all(probes_win(cell,left-1,rounds) for cell in cells):return True
    return False

def interrupt(signum,frame):raise TimeoutError('bounded 45-second search deadline')
signal.signal(signal.SIGALRM,interrupt)
signal.alarm(45)
status='COMPLETED_DEFINED_HORIZONS'
try:
    for h in range(1,7):
        before=time.monotonic()
        answer=round_wins(1<<INDEX[tuple(range(N))],h)
        row={'horizon':h,'zero_error_strategy_exists':answer,
             'seconds':time.monotonic()-before,'cumulative_counts':dict(COUNTS)}
        RESULTS.append(row);print(json.dumps(row),flush=True)
        if not answer:
            status='FINITE_OBSTRUCTION_FOUND_NOT_INDEPENDENTLY_VERIFIED';break
except TimeoutError as exc:
    status='INCOMPLETE_TIME_BOUND';print(str(exc),flush=True)
finally:
    signal.alarm(0)
    out={'result_id':'ONLINE-AC-N5-BOUNDED-20261009','status':status,
         'n':N,'probes_per_round':2,'initial_wiring':'identity',
         'goal_effect_port':0,'wiring_count':len(PERMS),'drift_choices':len(DRIFTS),
         'terminal_feedback':'full; forced on successful prefixes',
         'objective':'every round net increment is e_0',
         'horizons_completed':RESULTS,'counts':COUNTS,
         'elapsed_seconds':time.monotonic()-START,
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'limit':'Exact finite belief recursion if completed; no infinite-horizon result or general n theorem is inferred from positive bounded horizons.'}
    Path(__file__).with_name('SEARCH_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':status,'counts':COUNTS}),flush=True)
