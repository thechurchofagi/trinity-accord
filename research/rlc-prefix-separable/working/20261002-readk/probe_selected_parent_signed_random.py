#!/usr/bin/env python3
"""Additional exact signed Q6 pressure; samples are not general proofs."""
import hashlib,json,random,time
from itertools import permutations
from pathlib import Path
import numpy as np
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,counts
from probe_selected_parent_conditional_minima import conditional_vector

SEED=202610031647
def main():
    start=time.monotonic();rng=random.Random(SEED);stream=hashlib.sha256()
    parents=json.loads(Path('fixed_natural_parent_children_certificate.json').read_text())['best_child_masks']
    rr=np.array([[rank(x,5,m) for x in range(32)] for m in parents],dtype=np.uint8)
    minima=np.full(50,64);arg=[None]*50;cases=ties=0
    weights=[]
    for perm in permutations(range(6)):
        v=tuple(1<<i for i in perm)
        for z in range(64):weights.append(tuple(a*(-1 if z>>i&1 else 1) for i,a in enumerate(v)))
    for i in range(100000):
        mode=i%4
        if mode==0:v=tuple(rng.randint(1,400) for _ in range(6))
        elif mode==1:
            B=rng.randint(50,2000);v=tuple(B+rng.randint(-40,40) for _ in range(6))
        elif mode==2:v=tuple(rng.randint(1,1<<rng.randint(2,12)) for _ in range(6))
        else:
            powers=rng.sample(range(6),6);v=tuple((1<<h)*rng.randint(50,100)+rng.randint(-15,15) for h in powers)
        z=rng.randrange(64);weights.append(tuple(a*(-1 if z>>j&1 else 1) for j,a in enumerate(v)))
    for w in weights:
        result=order_and_scores(w)
        if result is None:ties+=1;continue
        mu=conditional_vector(np.array(result[0]),rr)
        for i in np.flatnonzero(mu<minima):arg[int(i)]=w
        minima=np.minimum(minima,mu);cases+=1;stream.update(bytes(map(int,mu)))
        if np.all(minima<24):break
    rows=[]
    for m,mu,w in zip(parents,minima,arg):
        p=order_and_scores(w)[0]
        C0=counts([rank(x,6,m<<16) for x in p])[1]
        C1=counts([rank(x,6,(m<<16)|65535) for x in p])[1]
        assert C0+C1==2*int(mu)
        L=sum((a^b)==1 for a,b in zip(p,p[1:]+p[:1]))
        rows.append({'parent_mask':m,'certified_cyclic_minimum':12,'pressure_conditional_minimum':int(mu),
            'loss_below24':24-int(mu),'actual_signed_weights':w,'fresh_comparisons':L,
            'allfresh0_cyclic':C0,'allfresh1_cyclic':C1,'status':'REJECTED' if mu<24 else 'UNRESOLVED'})
    out={'status':'SIGNED_Q6_SELECTED_PARENT_PRESSURE','scope':'All46080 signed permuted-binary sweeps followed by100000 generated weights; ties rejected. NOT completeQ6. Exact mean witnesses, independent known Q5 parent minima.',
        'seed':SEED,'cases':cases,'ties':ties,'rejected_count':sum(r['loss_below24']>0 for r in rows),
        'surviving_masks':[r['parent_mask'] for r in rows if r['loss_below24']<=0],
        'rows':rows,'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('selected_parent_signed_random_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
