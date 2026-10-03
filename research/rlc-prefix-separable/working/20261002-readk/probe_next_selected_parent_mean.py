#!/usr/bin/env python3
"""Counterexample pressure on all fifty optimal natural-parent Q5 children.

Exact one-parameter new-bottom slices of specified integer Q5 cores are
audited. This is NOT complete Q6 chamber enumeration. Every rejecting
witness is a generic integer scan; a survivor is not a theorem.
"""
import gzip,hashlib,json,time
from itertools import permutations
from pathlib import Path
import numpy as np
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import order_and_scores,counts
from probe_selected_parent_conditional_minima import conditional_vector

def main():
    start=time.monotonic();child=json.loads(Path('fixed_natural_parent_children_certificate.json').read_text())
    parents=child['best_child_masks'];assert len(parents)==50
    rr=np.array([[rank(x,5,m) for x in range(32)] for m in parents],dtype=np.uint8)
    inherited=json.loads(gzip.decompress(Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()))['n5_orders_and_certificates']
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in inherited if r['coherence_certificate']['coherent']]
    minima=np.full(50,64,dtype=np.int64);arg=[None]*50;cases=cores=0;stream=hashlib.sha256()
    for seed in seeds:
        for perm in permutations(range(5)):
            core=tuple(seed[j] for j in perm);p,scores=order_and_scores(core)
            breaks=sorted({abs(a-b) for a in scores for b in scores if a!=b}|{0,max(scores)+1})
            for lo,hi in zip(breaks,breaks[1:]):
                w=(lo+hi,)+tuple(2*a for a in core)
                result=order_and_scores(w);assert result is not None
                mu=conditional_vector(np.array(result[0]),rr)
                for i in np.flatnonzero(mu<minima):arg[int(i)]=w
                minima=np.minimum(minima,mu);cases+=1;stream.update(bytes(map(int,mu)))
            cores+=1
            if np.all(minima<24):break
            if cores>=2500:break
        if np.all(minima<24) or cores>=2500:break
    witnesses=[]
    for m,mu,w in zip(parents,minima,arg):
        p=order_and_scores(w)[0];full=m<<16
        # Independent direct rank-word endpoint average. Fresh level0
        # has additive independent two-state turn costs, already proved.
        C0=counts([rank(x,6,full) for x in p])[1]
        C1=counts([rank(x,6,full|65535) for x in p])[1]
        assert C0+C1==2*int(mu)
        diffs=[]
        for i in range(16):
            Ci=counts([rank(x,6,full|(1<<i)) for x in p])[1]
            diffs.append(Ci-C0)
        assert C1==C0+sum(diffs)
        for choice in [65535^(1<<i) for i in range(16)]+[0xaaaa,0x5555,0x1234,0x9876]:
            C=counts([rank(x,6,full|choice) for x in p])[1]
            assert C==C0+sum(diffs[i] for i in range(16) if choice>>i&1)
        witnesses.append({'parent_mask':m,'certified_parent_all_signed_cyclic_minimum':12,
            'sampled_conditional_minimum':int(mu),'exact_loss_below24':24-int(mu),
            'actual_integer_weights':w,'fresh_comparison_count':sum((a^b)==1 for a,b in zip(p,p[1:]+p[:1])),
            'cyclic_value_allfresh0':C0,'cyclic_value_allfresh1':C1,'independent_singleton_differences':diffs,
            'status':'REJECTS_LOSSLESS_MEAN_EXTENSION' if mu<24 else 'NO_REJECTION_FOUND_IN_THIS_SLICE_PRESSURE'})
    out={'status':'SELECTED_PARENT_NEXT_MEAN_PRESSURE',
        'scope':'Specified positive generic Q6 integer slices only. No complete-Q6 lower bound. Independent fixed parent minima12 come from complete Q5 certificate. Means are exact, not sampled over labels.',
        'core_slices':cores,'actual_q6_orders':cases,'parent_count':50,
        'rejected_parents':sum(r['sampled_conditional_minimum']<24 for r in witnesses),
        'surviving_parent_masks':[r['parent_mask'] for r in witnesses if r['sampled_conditional_minimum']>=24],
        'witnesses':witnesses,'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('next_selected_parent_mean_pressure.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='witnesses'}),flush=True)

if __name__=='__main__':main()
