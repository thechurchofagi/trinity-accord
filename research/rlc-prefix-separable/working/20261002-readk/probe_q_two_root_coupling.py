#!/usr/bin/env python3
"""Stress |J_root,a|<=1 at raw q=2; distinguish actual and relaxed scans."""
from pathlib import Path
from itertools import permutations
import gzip,hashlib,json,random,time
from verify_tiny_raw_support_structure import labels
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs

def graph_q2(p,n):
    labs=labels(p,n);S=set(labs)-{(n-1,0)}
    if len(S)!=2:return None
    G=linear_graph(p,n);a=max([abs(v) for _,_,v in G['edges']]or[0])
    return G,a,sorted(S)

def term_violation(p,n):
    pos={x:i for i,x in enumerate(p)}
    for a in range(1<<n):
        for b in range(a+1,1<<n):
            avail=((1<<n)-1)&~(a|b)
            for j in range(n):
                if avail>>j&1 and ((pos[a]<pos[b])!=(pos[a|(1<<j)]<pos[b|(1<<j)])):
                    return {'pair':[a,b],'common_added_bit':j,
                        'preference_before':pos[a]<pos[b],
                        'preference_after':pos[a|(1<<j)]<pos[b|(1<<j)]}
    return None

def main():
    st=time.monotonic();rng=random.Random(202610031930)
    relaxed=[];attempts=0
    for n in (4,5,6):
        N=1<<n;half=N//2
        for _ in range(10000):
            first=[x^(N-1) if rng.randrange(2) else x for x in range(half)]
            rng.shuffle(first);p=tuple(first+[x^(N-1) for x in first[::-1]])
            attempts+=1;r=graph_q2(p,n)
            if r and r[1]>1:
                G,c,S=r
                minima=[(fast_runs([rank(x,n,t) for x in range(N)],p),t)
                    for t in range(1<<((1<<(n-1))-1))] if n<=5 else []
                relaxed.append({'n':n,'p':p,'G':G,'abs_root_coupling':c,'support':S,
                    'common_addition_violation':term_violation(p,n),
                    'minimum_run_mask':min(minima) if minima else None})
                break
    source=json.loads(gzip.decompress(Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()))
    actual=[];checked=0;support2=0;mx=0
    for row in source['n5_orders_and_certificates']:
        cert=row['coherence_certificate']
        if not cert['coherent']:continue
        core=cert['integer_weights']
        for pi in permutations(range(5)):
            w=tuple(core[j] for j in pi);p=order_and_scores(w)[0];checked+=1
            r=graph_q2(p,5)
            if r:
                G,c,S=r;support2+=1;mx=max(mx,c)
                if c>1:actual.append({'weights':w,'p':p,'G':G,'abs_root_coupling':c,'support':S})
    out={'status':'Q_TWO_ROOT_COUPLING_PRESSURE_ONLY_NOT_GENERAL_PROOF',
        'hypothesis':'Every genuine generic additive scan with raw non-top q=2 has |J_root,a|<=1.',
        'relaxed_attempts':attempts,'relaxed_counterexamples':relaxed,
        'coherent_q5_positive_coordinate_orders_checked':checked,'q_two_actual_cases':support2,
        'actual_max_abs_coupling':mx,'actual_counterexamples':actual,
        'scope':'The Q5 source supplies integer certificates for516 coherent sorted-magnitude orders; its completeness is inherited, not reproved here. Positive orders only; signed support unchanged but coefficient mapping must be separately audited before claiming signed coverage. Random centrally symmetric permutations are explicitly not assumed additive. No general theorem follows from this pressure test.',
        'seed':202610031930,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('q_two_root_coupling_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('relaxed_counterexamples','actual_counterexamples')}),flush=True)
    print(json.dumps({'relaxed_counterexamples':relaxed,'actual_counterexamples':actual}),flush=True)

if __name__=='__main__':main()
