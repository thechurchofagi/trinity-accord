#!/usr/bin/env python3
"""Integer certificate excluding an upper-run-only translated-face recursion."""
from pathlib import Path
import gzip,hashlib,json,time
from probe_large_translated_quartet_recurrence import fast

def main():
    start=time.monotonic();here=Path(__file__).parent
    source=json.loads(gzip.decompress((here/'large_translated_quartet_pressure.json.gz').read_bytes()))['counterexamples'][0]
    assert source['F']==32 and source['minimum_runs']==31 and source['upper_runs']==9
    values=source['actual_rank_values'];sg=[1 if y>x else -1 for x,y in zip(values,values[1:])]
    assert all(x//4!=y//4 for x,y in zip(values,values[1:]))
    assert sg[0]==sg[-1]==1 and sum(t<0 for t in sg)==15
    assert all(not(x<0 and y<0) for x,y in zip(sg,sg[1:]))
    upper=source['block_rank'];us=[1 if y>x else -1 for x,y in zip(upper,upper[1:])]
    assert us[0]==us[-1]==1 and sum(t<0 for t in us)==4
    assert all(not(x<0 and y<0) for x,y in zip(us,us[1:]))
    seed_scores=[s+c for s in source['offsets'] for c in (0,source['a'],source['b'],source['a']+source['b'])]
    assert len(set(seed_scores))==128
    rows=[]
    for k in (1,2,3,4,8,16,32,64):
        scale=k+1;offsets=[scale*s+t for s in source['offsets'] for t in range(k)]
        block=[k*b+t for b in source['block_rank'] for t in range(k)]
        z=fast(offsets,scale*source['a'],scale*source['b'],block)
        assert z is not None and z['minimum_runs']==31 and z['upper_runs']==9
        assert all(v==0 for v in z['local_masks'])
        rows.append({'clones_per_face':k,'F':32*k,'minimum_runs':31,'upper_runs':9,
                     'proposed_bound':min(32*k+1,33),'integer_score_generic':True})
    out={'status':'VERIFIED_UNBOUNDED_FACE_COUNT_COUNTEREXAMPLE_TO_UPPER_RUN_ONLY_RECURSION',
         'analytic_statement':'For every positive integer k, there are F=32k equal-gap translated quartets with R_upper=9 but exact minimum R=31. Thus R>=min(cF+C,4R_upper-3) fails for every fixed c>0 and finite C.',
         'scope':'Arbitrary face-block permutation and face offsets. Not claimed to be cube subset sums, an admissible paired upper rank, or a main M_n counterexample.',
         'seed':source,'seed_isolated_negative_comparisons':15,'seed_upper_isolated_negative_comparisons':4,
         'proof':'Scale seed scores by k+1 and replace each face by k offsets separated by1, refining block rank k*B+t. Every old event becomes an increasing clone track. Cross-event signs retain their sign; all negative signs were isolated with positive first/last signs. Hence exactly15 isolated negatives and31 runs persist; the upper order similarly retains4 isolated negatives and9 runs. Four integer costs per face attain the same exact minimum.',
         'finite_audits':rows,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    (here/'translated_quartet_failure_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('seed','finite_audits','proof')}),flush=True)

if __name__=='__main__':main()
