#!/usr/bin/env python3
"""Independent integer sign-word audit of selected Q5 child mask2.

No NumPy and no inherited rank-comparison routine for the chamber check.
Build comparison signs from forward Gray and label incidences, toggle
whole sign-word bit sets, and count runs with integer XOR/popcount.
"""
import gzip,hashlib,json,time
from itertools import permutations
from pathlib import Path
from verify_paired_sibling_ranks import rank,reflection_mask
from verify_gray_reflection_graph import order_and_scores,counts

def main():
    start=time.monotonic();stream=hashlib.sha256();target=2;bits=(1<<32)-1
    orbit={}
    for z in range(32):
        m,t=reflection_mask(5,target,z);m=m^((1<<15)-1) if t else m
        orbit.setdefault(m,z)
    source=Path('paired_boolean_term_orders_certificate.json.gz').read_bytes()
    rows=json.loads(gzip.decompress(source))['n5_orders_and_certificates']
    seeds=[tuple(r['coherence_certificate']['integer_weights']) for r in rows if r['coherence_certificate']['coherent']]
    minC=32;minR=32;argC=argR=None;cases=0;words=0
    for seed in seeds:
        for perm in permutations(range(5)):
            w=tuple(seed[j] for j in perm);p=order_and_scores(w)[0]
            labelwords=[0]*16;baseline=0
            for i,(x,y) in enumerate(zip(p,p[1:]+p[:1])):
                h=(x^y).bit_length()-1
                label=15 if h==4 else 16-(1<<(4-h))+(x>>(h+2))
                labelwords[label]|=1<<i
                baseline|=int((y^(y>>1))>(x^(x>>1)))<<i
            for m,z in orbit.items():
                a=baseline;active=m
                while active:
                    lo=active&-active;a^=labelwords[lo.bit_length()-1];active-=lo
                C=(a^((a>>1)|((a&1)<<31))).bit_count()
                R=1+((a^(a>>1))&((1<<30)-1)).bit_count()
                if C<minC:minC=C;argC={'weights':w,'input_reflection':z}
                if R<minR:minR=R;argR={'weights':w,'input_reflection':z}
                stream.update(bytes((C,R)));words+=1
            cases+=1
    assert cases==61920 and minC==12
    for arg,expected,which in [(argC,minC,1),(argR,minR,0)]:
        signed=tuple(v*(-1 if arg['input_reflection']>>i&1 else 1) for i,v in enumerate(arg['weights']))
        p=order_and_scores(signed)[0];r=[rank(x,5,target) for x in p]
        assert counts(r)[which]==expected
        arg['actual_signed_weights']=signed;arg['full_vertex_order']=p;arg['rank_word']=r
    out={'status':'VERIFIED_SELECTED_Q5_CHILD_BY_INDEPENDENT_BITWORDS',
        'n':5,'parent_mask':0,'child_mask':target,'all_signed_cyclic_minimum':minC,'all_signed_linear_minimum':minR,
        'scope':'Complete finite inherited Q5 chamber set with exact reflection orbit; all-dimensional positive-density theorem remains OPEN.',
        'source_sha256':hashlib.sha256(source).hexdigest(),'positive_chambers':cases,
        'distinct_reflected_ranks':len(orbit),'bitwords_checked':words,
        'cyclic_attainer':argC,'linear_attainer':argR,
        'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('selected_child_bitwords_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
