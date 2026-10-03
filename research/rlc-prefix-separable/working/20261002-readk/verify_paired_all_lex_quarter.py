#!/usr/bin/env python3
"""Exact disjoint forced/cancellation certificates for every signed lex order."""
from pathlib import Path
from itertools import permutations
from collections import Counter,defaultdict
import hashlib,json,random,time
from verify_gray_reflection_graph import gray,counts,order_and_scores
from verify_paired_sibling_ranks import rank,linear_graph,cyclic_extremal
from paired_sibling_ancestor_optimizer import optimize

def lex_order(order,z=0):
    n=len(order)
    return tuple(z^sum(((i>>r)&1)<<j for r,j in enumerate(order)) for i in range(1<<n))

def labels_signs(p,n):
    offsets=[];off=0
    for h in range(n-1):offsets.append(off);off+=1<<(n-h-2)
    labels=[];signs=[]
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1
        labels.append(off if h==n-1 else offsets[h]+(x>>(h+2)))
        signs.append(1 if gray(y)>gray(x) else -1)
    return labels,signs

def certificate(order,z=0):
    n=len(order);N=1<<n;p=lex_order(order,z);j,k=order[:2]
    labels,signs=labels_signs(p,n);g=linear_graph(p,n)
    forced=[];pairs=[];loads=defaultdict(int)
    def contribution(i):
        a,b=labels[i],labels[i+1]
        assert a!=b
        return tuple(sorted((a,b))),signs[i]*signs[i+1]
    def pair(a,b):
        aa,sa=contribution(a);bb,sb=contribution(b)
        assert aa==bb and sa==-sb
        pairs.append((a,b));loads[aa]+=1
    if j>k:
        case='fastest_above_second'
        for q in range(N//4):
            for i in (4*q,4*q+1):
                assert labels[i]==labels[i+1] and signs[i]==-signs[i+1]
                forced.append(i)
        assert len(forced)==N//2 and g['D']>=N//2
    elif k==j+1:
        case='adjacent_controller'
        for q in range(N//4):pair(4*q,4*q+1)
    else:
        case='nonadjacent_paired_blocks';lookup={p[4*q]:q for q in range(N//4)}
        assert j+1 not in (j,k)
        for q in range(N//4):
            other=lookup[p[4*q]^(1<<(j+1))]
            if q<other:
                pair(4*q,4*other);pair(4*q+1,4*other+1)
    used=forced+[i for pp in pairs for i in pp]
    assert len(set(used))==len(used)
    products=defaultdict(lambda:[0,0])
    for i in range(N-2):
        if labels[i]!=labels[i+1]:
            key,s=contribution(i);products[key][int(s<0)]+=1
    assert all(load<=min(products[key]) for key,load in loads.items())
    assert sum(min(a,b) for a,b in products.values())==g['K']
    if j<k:assert len(pairs)==N//4 and g['K']>=N//4
    assert g['D']+g['K']>=N//4
    return {'coordinate_order':order,'reflection':z,'case':case,'D':g['D'],'K':g['K'],
            'forced_indices':forced,'opposite_raw_pairs':pairs,
            'pair_loads':[(a,b,c) for (a,b),c in sorted(loads.items())],
            'certificate_sha256':hashlib.sha256(json.dumps((forced,pairs,sorted(loads.items()))).encode()).hexdigest()}

def main():
    start=time.monotonic();digest=hashlib.sha256();rows=[];representatives=[];positive_count=0;signed_count=0
    for n in range(2,8):
        cases=Counter();minimum=None;data=[];kept=set()
        for order in permutations(range(n)):
            c=certificate(order);positive_count+=1;cases[c['case']]+=1
            data.append([order,c['D'],c['K'],c['certificate_sha256']])
            digest.update(json.dumps((n,order,c['D'],c['K'],c['certificate_sha256'])).encode())
            if minimum is None or c['D']+c['K']<minimum['D']+minimum['K']:minimum=c
            if c['case'] not in kept:representatives.append({'n':n,**c});kept.add(c['case'])
            if n<=5:
                for z in range(1,1<<n):
                    cc=certificate(order,z);signed_count+=1
                    assert (cc['D'],cc['K'])==(c['D'],c['K'])
                    digest.update(json.dumps((n,order,z,cc['certificate_sha256'])).encode())
        rows.append({'n':n,'all_positive_lex_coordinate_orders':len(data),'case_histogram':dict(cases),
                     'minimum_D_plus_K':minimum['D']+minimum['K'],'minimum_certificate':minimum,
                     'order_D_K_digest_rows':data})
        print(json.dumps({'n':n,'coordinate_orders':len(data),'minimum_D_K':minimum['D']+minimum['K'],
                          'case_histogram':dict(cases),'elapsed':round(time.monotonic()-start,3)}),flush=True)
    rng=random.Random(202610031006);pressure=[];sharp=[]
    for n in range(6,13):
        for trial in range(8):
            order=list(range(n));rng.shuffle(order);order=tuple(order);z=rng.randrange(1<<n)
            c=certificate(order,z);signed_count+=1
            weights=tuple((-(1<<order.index(j)) if z>>j&1 else 1<<order.index(j)) for j in range(n))
            p=order_and_scores(weights)[0];assert p==lex_order(order,z)
            mask=rng.getrandbits((1<<(n-1))-1)
            observed=counts(tuple(rank(x,n,mask) for x in p))[0]
            assert observed>=(1<<n)//4+1
            pressure.append({'n':n,'weights':weights,'mask':mask,'actual_R':observed,'certificate':c})
            digest.update(json.dumps(pressure[-1],sort_keys=True).encode())
    for n in range(3,13):
        weights=tuple(8*(1<<j) for j in range(n-3))+(1,2,4)
        p=order_and_scores(weights)[0];g=linear_graph(p,n);r=optimize(g,n)
        observed=counts(tuple(rank(x,n,r['mask']) for x in p))[0]
        assert observed==(1<<n)//4+1
        sharp.append({'n':n,'weights':weights,'rank_mask':r['mask'],'R':observed,'optimizer':r})
    out={'state':'VERIFIED_ALL_DIMENSION_ALL_SIGNED_LEX_QUARTER_THEOREM',
         'all_dimension_theorem':'For every n>=2, every paired-sibling rank and every signed lexicographic coordinate significance order, D+K>=2^(n-2), hence R>=2^(n-2)+1. The bound is sharp over the family for all n>=3.',
         'positive_orders_exhausted':positive_count,'additional_signed_orders_audited':signed_count,
         'dimension_rows':rows,'representative_exact_cancellation_certificates':representatives,
         'fresh_signed_integer_scan_audits':pressure,'sharp_genuine_attainers':sharp,
         'violations':0,'verification_digest':digest.hexdigest(),'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Analytic theorem covers all dimensions and all signed lex orders. Finite checks pressure-test the disjoint certificate. General non-lex additive subset-sum interleavings remain OPEN; this is not a bound for RLC over all weights or M_n.'}
    Path(__file__).with_name('paired_all_lex_quarter_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','positive_orders_exhausted','additional_signed_orders_audited','violations','verification_digest','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
