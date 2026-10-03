#!/usr/bin/env python3
"""All Q5 children of the Q4 natural paired parent: exact signed minimax.

Uses all certified positive Q5 order chambers and exact reflection closure.
No claim about dimensions above five or every unrestricted prefix order.
"""
import gzip,hashlib,json,time
from itertools import permutations
from pathlib import Path
import numpy as np
from verify_paired_sibling_ranks import rank,reflection_mask
from verify_gray_reflection_graph import order_and_scores,counts
from probe_selected_parent_conditional_minima import cyclic_vector

def main():
    start=time.monotonic();digest=hashlib.sha256();allmask=(1<<15)-1
    targets=list(range(256));maps=[]
    for z in range(32):
        row=[]
        for mask in targets:
            m,t=reflection_mask(5,mask,z);row.append(m^allmask if t else m)
        maps.append(row)
    orbit=sorted({m for row in maps for m in row});assert len(orbit)==2048
    index={m:i for i,m in enumerate(orbit)};mapping=np.array([[index[m] for m in row] for row in maps])
    rr=np.array([[rank(x,5,m) for x in range(32)] for m in orbit],dtype=np.uint8)
    source=Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()
    inherited=json.loads(gzip.decompress(source))['n5_orders_and_certificates']
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in inherited if r['coherence_certificate']['coherent']]
    assert len(seeds)==516
    minima=np.full(len(orbit),32,dtype=np.int64);arg=[None]*len(orbit);cases=0
    for seed in seeds:
        for perm in permutations(range(5)):
            w=tuple(seed[j] for j in perm);result=order_and_scores(w);assert result is not None
            p=np.array(result[0]);cs=cyclic_vector(p,rr)
            for i in np.flatnonzero(cs<minima):arg[int(i)]=w
            minima=np.minimum(minima,cs);cases+=1;digest.update(bytes(map(int,cs)))
        if cases%12000==0:print(json.dumps({'positive_chambers_completed':cases}),flush=True)
    rows=[]
    for mask in targets:
        z=int(np.argmin(minima[mapping[:,mask]]));j=int(mapping[z,mask]);w=arg[j]
        signed=tuple(v*(-1 if z>>i&1 else 1) for i,v in enumerate(w));p=order_and_scores(signed)[0]
        R,C,a=counts([rank(x,5,mask) for x in p]);assert C==int(minima[j])
        rows.append({'child_mask':mask,'all_signed_cyclic_minimum':C,'attaining_actual_signed_weights':signed,'witness_linear_runs':R})
    out={'status':'COMPLETE_FIXED_NATURAL_PARENT_CHILD_MINIMAX',
        'scope':'Every one of256 normalized Q5 children of Q4 parent0, all1981440 signed additive chambers; inherited516 positive sorted chambers with exact integer coherence certificates times120 coordinate permutations times32 reflections. Finite only.',
        'source_sha256':hashlib.sha256(source).hexdigest(),'positive_chambers':cases,'full_reflection_closure_size':len(orbit),
        'best_child_cyclic_minimum':max(r['all_signed_cyclic_minimum'] for r in rows),
        'best_child_masks':[r['child_mask'] for r in rows if r['all_signed_cyclic_minimum']==max(s['all_signed_cyclic_minimum'] for s in rows)],
        'child_records':rows,'audit_stream_sha256':digest.hexdigest(),'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('fixed_natural_parent_children_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='child_records'}),flush=True)

if __name__=='__main__':main()
