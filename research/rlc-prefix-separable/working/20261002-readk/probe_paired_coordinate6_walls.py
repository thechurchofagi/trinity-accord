#!/usr/bin/env python3
"""All true generic intervals of one Q9 coefficient in (0,128).

LP enumeration limits are retained explicitly; no claim about skipped
optima or other coordinate slices follows from this bounded audit.
"""
from pathlib import Path
from collections import Counter
import base64,gzip,hashlib,json,time
from probe_paired_joint_fractional_packing import solve
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph

def main():
    base=(216,246,244,442,248,642,6,601,128);j=6
    others=[w for i,w in enumerate(base) if i!=j]
    scores=sorted(sum(w*((x>>i)&1) for i,w in enumerate(others)) for x in range(256))
    assert len(set(scores))==256
    walls=sorted({0,128}|{b-a for a in scores for b in scores if 0<b-a<128})
    seen={};rows=[];counts=Counter();start=time.monotonic();gaps=[]
    for left,right in zip(walls,walls[1:]):
        w=tuple(left+right if i==j else 2*v for i,v in enumerate(base))
        p=order_and_scores(w);assert p is not None
        g=linear_graph(p[0],9);signature=(g['D'],g['K'],g['edges'])
        if signature in seen:
            rows.append({'interval':[left,right],'scaled_weights':w,'duplicate_graph_of_interval':seen[signature]})
            counts['duplicate']+=1;continue
        seen[signature]=[left,right];z=solve(w,retain=False);z['interval']=[left,right]
        rows.append(z);counts[z['status']]+=1
        if z.get('phi_minus_packing',[0])[0]>0:gaps.append({'gap':z['phi_minus_packing'],'interval':[left,right]})
        if len(rows)%20==0:
            print(json.dumps({'completed_intervals':len(rows),'counts':dict(counts),'elapsed':time.monotonic()-start}),flush=True)
    out={'status':'COMPLETE_ONE_COORDINATE_GENERIC_INTERVAL_AUDIT_IN_0_128',
         'base_weights':base,'varied_coordinate':j,'range':[0,128],'walls':walls,
         'scope':'Exhaustive generic intervals for one real coefficient in the stated range, with all other eight fixed. LP enumeration-limit cases certify no packing optimum. Other slices, endpoints, all Q9 chambers and higher dimensions are not covered.',
         'intervals':len(walls)-1,'unique_graphs':len(seen),'counts':dict(counts),
         'actual_packing_gaps':gaps,'rows':rows,'seconds':time.monotonic()-start}
    raw=(json.dumps(out,indent=2)+'\n').encode();root=Path(__file__).parent
    (root/'paired_signed_k5_coordinate6_wall_audit.json').write_bytes(raw)
    compressed=gzip.compress(raw,mtime=0)
    (root/'paired_signed_k5_coordinate6_wall_audit.json.gz.base64').write_text(base64.b64encode(compressed).decode()+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','walls')}),flush=True)
    print('sha256',hashlib.sha256(raw).hexdigest(),flush=True)

if __name__=='__main__':main()
