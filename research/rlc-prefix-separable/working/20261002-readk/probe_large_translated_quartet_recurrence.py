#!/usr/bin/env python3
"""Large-F exact pressure exploiting independent face orientation costs.

This relaxation permits arbitrary face-block ranks and offsets. Each
comparison internal to a face depends only on its own two local bits;
two consecutive internal comparisons must belong to the SAME face.
Thus four integer assignments per face suffice for a full exact minimum.
"""
from pathlib import Path
import hashlib,json,random,time
from probe_translated_quartet_recurrence import solve as exhaustive

def fast(offsets,a,b,block):
    F=len(offsets)
    rows=sorted((s+c,f,x) for f,s in enumerate(offsets) for x,c in enumerate((0,a,b,a+b)))
    if len({s for s,f,x in rows})!=4*F:return None
    descriptors=[]
    for (_,f,x),(_,g,y) in zip(rows,rows[1:]):
        if f!=g:descriptors.append((None,0,1 if block[g]>block[f] else -1))
        else:descriptors.append((f,(x^y).bit_length()-1,1 if (y^(y>>1))>(x^(x>>1)) else -1))
    costs=[[0]*4 for f in range(F)];constant=1
    def sign(d,mask):return d[2] if d[0] is None else d[2]*(-1 if mask>>d[1]&1 else 1)
    for d,e in zip(descriptors,descriptors[1:]):
        free={z[0] for z in (d,e) if z[0] is not None}
        assert len(free)<=1
        if not free:constant+=int(d[2]!=e[2])
        else:
            f=next(iter(free))
            for mask in range(4):costs[f][mask]+=int(sign(d,mask)!=sign(e,mask))
    local=[min(range(4),key=cost.__getitem__) for cost in costs]
    R=constant+sum(min(cost) for cost in costs)
    values=[4*block[f]+((x^(x>>1))^local[f]) for s,f,x in rows]
    signs=[1 if y>x else -1 for x,y in zip(values,values[1:])]
    assert R==1+sum(x!=y for x,y in zip(signs,signs[1:]))
    order=sorted(range(F),key=offsets.__getitem__);upper=[block[f] for f in order]
    ss=[1 if y>x else -1 for x,y in zip(upper,upper[1:])]
    U=1+sum(x!=y for x,y in zip(ss,ss[1:]));target=min(F+1,4*U-3)
    return {'F':F,'offsets':offsets,'a':a,'b':b,'block_rank':block,'local_masks':local,
            'minimum_runs':R,'upper_runs':U,'proposed_bound':target,
            'constant_cross_turn_cost':constant,'minimum_local_costs':[min(cost) for cost in costs],
            'actual_rank_values':values,'recurrence_failure':R<target}

def main():
    start=time.monotonic();rng=random.Random(202610031305);rows=[];fails=[];ties=0;checks=0
    for i in range(16000):
        F=(4,8,16,32,64,128)[i%6]
        if i%4==0:offsets=sorted(rng.sample(range(0,100000),F))
        elif i%4==1:offsets=list(range(F))
        else:
            # Clustered/unequal gaps, distinct integer offsets.
            offsets=[0]
            for f in range(1,F):offsets.append(offsets[-1]+rng.randrange(1,10 if f%4 else 1000))
        scale=offsets[-1]+1
        a=rng.randrange(1,4*scale+1);b=rng.randrange(a+1,8*scale+2)
        block=list(range(F))
        if i%5==0:rng.shuffle(block)
        elif i%5==1:
            left=sorted(rng.sample(range(F-1),rng.randrange(F)))
            block=left+[F-1]+sorted(set(range(F-1))-set(left),reverse=True)
        elif i%5==2:
            width=max(1,F//8);chunks=[block[j:j+width] for j in range(0,F,width)];rng.shuffle(chunks);block=[x for chunk in chunks for x in chunk]
        elif i%5==3:
            for j in range(0,F,4):block[j:j+4]=reversed(block[j:j+4])
        z=fast(offsets,a,b,block)
        if z is None:ties+=1;continue
        if F<=8 and checks<128:
            old=exhaustive(offsets,a,b,block);assert old['minimum_runs']==z['minimum_runs'];checks+=1
        rows.append({k:v for k,v in z.items() if k not in ('actual_rank_values','minimum_local_costs','local_masks')})
        if z['recurrence_failure']:fails.append(z);break
        if i%2000==0:print(json.dumps({'proposals':i+1,'generic':len(rows),'failures':len(fails),'elapsed':time.monotonic()-start}),flush=True)
    out={'status':'EXACT_LARGE_TRANSLATED_QUARTET_PRESSURE','seed':202610031305,
         'scope':'Arbitrary offsets and face-block permutation; finite parameter pressure, not generic cube chamber completeness or all-dimensional theorem.',
         'exact_face_optimization':'Four integer orientation costs per face; checked independently against exhaustive orientation states.',
         'generic_cases':len(rows),'nongeneric_rejected':ties,'independent_exhaustive_checks':checks,
         'counterexamples':fails,'rows':rows,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    import gzip
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('large_translated_quartet_pressure.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','counterexamples')}|{'failures':len(fails),'first_failure':fails[0] if fails else None}),flush=True)

if __name__=='__main__':main()
