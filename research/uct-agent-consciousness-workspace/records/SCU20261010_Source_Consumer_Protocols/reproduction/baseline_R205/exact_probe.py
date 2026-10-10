#!/usr/bin/env python3
"""Finite structural-equation audit; no phenomenal variable or empirical claim."""
import itertools,json,hashlib
from pathlib import Path

def run(P,F,s,r,B,R):
    # Two physically distinct source registers; directed reads fixed before values.
    carrier=(B,R)
    return P[carrier[s]],F[carrier[r]]

def main():
    counts=dict(single_read_installations=0,matched_episodes=0,source_probe_episodes=0,
                identified_installations=0,recoded_episodes=0,cancellation_source_probes=0,
                cancellation_branch_probes=0)
    profiles=set()
    for n in range(2,6):
        for P in itertools.permutations(range(n)):
            F=P # calibrated predictor, while s/r need not correspond
            for s,r in itertools.product(range(2),repeat=2):
                counts['single_read_installations']+=1
                profiles.add((s==0,s==r))
                for a in range(n):
                    y,z=run(P,F,s,r,a,a)
                    assert y==z==P[a]
                    counts['matched_episodes']+=1
                    b=(a+1)%n
                    baseline=(y,z)
                    probeB=run(P,F,s,r,b,a)
                    probeR=run(P,F,s,r,a,b)
                    counts['source_probe_episodes']+=2
                    # Independently recover selection from output changes, not source names.
                    signature=tuple(int(v!=w) for pr in (probeB,probeR) for v,w in zip(pr,baseline))
                    lookup={(1,1,0,0):(0,0),(1,0,0,1):(0,1),
                            (0,1,1,0):(1,0),(0,0,1,1):(1,1)}
                    assert lookup[signature]==(s,r)
                counts['identified_installations']+=1
                if n<=4:
                    for h in itertools.permutations(range(n)):
                        inverse={v:k for k,v in enumerate(h)}
                        transported=tuple(P[inverse[x]] for x in range(n))
                        for B,R in itertools.product(range(n),repeat=2):
                            assert run(P,F,s,r,B,R)==run(transported,transported,s,r,h[B],h[R])
                            counts['recoded_episodes']+=1
    assert profiles=={(False,False),(False,True),(True,False),(True,True)}
    witnesses=[]
    for n in range(2,8):
        # Remote-driven actuator y=R. Two live B fan-out ports are locally consumed
        # in z=(R+e1-e2)%n, where e1=e2=B absent edge interventions.
        for B,R in itertools.product(range(n),repeat=2):
            direct=(R,R)
            cancellation=(R,(R+B-B)%n)
            assert direct==cancellation
            counts['cancellation_source_probes']+=1
            for delta in range(1,n):
                z1=(R+(B+delta)%n-B)%n
                z2=(R+B-(B+delta)%n)%n
                assert z1!=R and z2!=R
                counts['cancellation_branch_probes']+=2
        witnesses.append(dict(n=n,direct_z='R',cancellation_z='(R+e1-e2) mod n',
            unperturbed_edges='e1=e2=B',all_source_assignments_equal=True,
            branch_probe=dict(B=0,R=0,delta=1,direct_z=0,cancellation_z=1)))
    result=dict(schema='uct-r205-exact/1',result_version='ASC-RESULT-v0.1.0',
        status='FINITE_MODEL_CLAIMS_VERIFIED_NOT_EMPIRICAL',counts=counts,
        profiles=sorted([list(x) for x in profiles]),
        matched_square=[dict(actuator_source=s,predictor_source=r,local_driver=s==0,
            same_source=s==r,y=0,z=0) for s,r in itertools.product(range(2),repeat=2)],
        cancellation_witnesses=witnesses,violations=0,
        limitations=['single-read source identification requires injectivity and valid isolated probes',
            'cancellation defeats unrestricted identification of branch consumption',
            'no actual human installation, H, phenomenal polarity, subject count or consciousness detector'])
    dest=Path(__file__).with_name('EXACT_RESULTS.json')
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],counts=counts,violations=0)))
if __name__=='__main__':main()
