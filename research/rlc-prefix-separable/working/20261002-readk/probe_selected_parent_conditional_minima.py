#!/usr/bin/env python3
"""Exact complete Q4 parent / certified Q5 conditional-mean pressure.

The complete Q5 chamber source is inherited, not established by sampling.
All labels of the new lowest level are averaged. Signed reflections are
handled by the exact paired-rank reflection identity, with root normalization.
"""
import gzip,hashlib,json,time
from itertools import permutations
from pathlib import Path
import numpy as np
from verify_paired_sibling_ranks import rank,reflection_mask
from verify_gray_reflection_graph import positive_chambers,order_and_scores,counts

def reflection_index(n):
    Q=(1<<(n-1))-1
    ans=[]
    for z in range(1<<n):
        row=[]
        for mask in range(1<<Q):
            m,t=reflection_mask(n,mask,z)
            row.append(m^((1<<Q)-1) if t else m)
        ans.append(row)
    return np.array(ans,dtype=np.int64)

def cyclic_vector(p,rr):
    a=rr[:,np.roll(p,-1)]>rr[:,p]
    return np.sum(a!=np.roll(a,-1,axis=1),axis=1)

def conditional_vector(p,rr):
    # Comparisons changing the lowest bit only are fresh; all others
    # compare fixed parent ranks. Distinct middle vertices forbid two
    # adjacent fresh comparisons (including the closing edge).
    fresh=(p^np.roll(p,-1))==1
    assert not np.any(fresh & np.roll(fresh,-1))
    fixedturns=(~fresh)&(~np.roll(fresh,-1))
    v=p>>1;a=rr[:,np.roll(v,-1)]>rr[:,v]
    return fresh.sum()+np.sum((a!=np.roll(a,-1,axis=1))&fixedturns,axis=1)

def main():
    start=time.monotonic();digest=hashlib.sha256()
    rr=np.array([[rank(x,4,m) for x in range(16)] for m in range(128)],dtype=np.int64)
    reflections=reflection_index(4)
    zpos=np.full(128,16,dtype=np.int64)
    for w in positive_chambers(4):
        p=np.array(order_and_scores(w)[0]);zpos=np.minimum(zpos,cyclic_vector(p,rr))
    z=np.min(zpos[reflections],axis=0)
    assert sorted(set(map(int,z)))==[4,6]
    assert np.sum(z==6)==56
    source=Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()
    inherited=json.loads(gzip.decompress(source))['n5_orders_and_certificates']
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in inherited if r['coherence_certificate']['coherent']]
    assert len(seeds)==516
    minima=np.full(128,32,dtype=np.int64);arg=[None]*128;cases=0
    for seed in seeds:
        for perm in permutations(range(5)):
            w=tuple(seed[j] for j in perm)
            result=order_and_scores(w);assert result is not None
            p=np.array(result[0],dtype=np.int64);mu=conditional_vector(p,rr)
            # Individual cyclic values are even; their conditional mean
            # can be odd when different fresh states straddle it.
            update=np.flatnonzero(mu<minima)
            for i in update:arg[int(i)]=w
            minima=np.minimum(minima,mu);cases+=1
            digest.update(bytes(map(int,mu)))
        if cases%12000==0:print(json.dumps({'positive_chambers_completed':cases}),flush=True)
    assert cases==61920
    rows=[]
    for m in range(128):
        iz=int(np.argmin(minima[reflections[:,m]]));target=int(reflections[iz,m]);mu=int(minima[target]);w=arg[target]
        signed=(w[0],)+tuple(w[j+1]*(-1 if iz>>j&1 else 1) for j in range(4))
        p=np.array(order_and_scores(signed)[0]);check=int(conditional_vector(p,rr)[m]);assert check==mu
        vals=[]
        for lower in range(256):
            full=(m<<8)|lower
            a=[rank(int(x),5,full) for x in p]
            vals.append(counts(a)[1])
        assert sum(vals)==256*mu
        rows.append({'parent_mask':m,'parent_all_signed_cyclic_minimum':int(z[m]),
            'all_signed_conditional_mean_minimum':mu,'exact_mean_doubling_loss':2*int(z[m])-mu,
            'attaining_actual_signed_weights':signed,'fresh_assignments':256,
            'child_cyclic_minimum_on_witness':min(vals),'child_cyclic_maximum_on_witness':max(vals)})
    out={'status':'COMPLETE_SELECTED_PARENT_CONDITIONAL_MINIMA',
        'scope':'Q4 all128 normalized paired parents; Q4 complete5376 signed chambers; Q5 inherited516 certified positive sorted chambers times120 coordinate permutations and32 sign reflections. Conditional averaging over ALL256 fresh bottom labels. Finite-dimensional only; no all-n controlled-loss claim.',
        'source_sha256':hashlib.sha256(source).hexdigest(),
        'positive_q5_cases':cases,'signed_q5_chambers':cases*32,
        'upper_reflection_classes_used':16,'lowest_reflection_invariance':'A lowest-input reflection only permutes/complements fresh labels, hence preserves their uniform mean.',
        'max_parent_conditional_minimum':max(r['all_signed_conditional_mean_minimum'] for r in rows),
        'optimal_parent_conditional_minima':sorted(set(r['all_signed_conditional_mean_minimum'] for r in rows if r['parent_all_signed_cyclic_minimum']==6)),
        'largest_doubling_loss':max(r['exact_mean_doubling_loss'] for r in rows),
        'all_parent_records':rows,'audit_stream_sha256':digest.hexdigest(),
        'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('selected_parent_conditional_minima_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='all_parent_records'}),flush=True)

if __name__=='__main__':main()
