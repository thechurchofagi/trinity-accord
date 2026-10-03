#!/usr/bin/env python3
"""No-LP independent certificate audit and lower-controller elimination.

Checks every retained integer witness/Farkas vector and recomputes paired
minima without the ancestor optimizer. Does NOT prove unknown all-n claims.
"""
from pathlib import Path
from itertools import permutations
from collections import Counter
import gzip,hashlib,json,time
from verify_paired_sibling_ranks import rank,fast_runs

def term_check(p,n):
    N=1<<n;assert len(p)==N and set(p)==set(range(N)) and p[0]==0
    pos={x:i for i,x in enumerate(p)}
    # A different direct test: enumerate EVERY permitted common addition,
    # instead of using the generator's cancellation-of-intersection test.
    for i,a in enumerate(p):
        for b in p[i+1:]:
            free=(N-1)^(a|b);c=free
            while True:
                assert pos[a|c]<pos[b|c]
                if c==0:break
                c=(c-1)&free
    assert p==tuple(x^(N-1) for x in reversed(p))

def neighbors(p,n):
    N=1<<n;pos={x:i for i,x in enumerate(p)}
    for a,b in zip(p,p[1:]):
        if not a or a&b or (a.bit_count()==b.bit_count()==1):continue
        free=(N-1)^(a|b);ss=[c for c in range(N) if c&free==c]
        if all(pos[a|c]+1==pos[b|c] for c in ss):
            q=list(p)
            for c in ss:q[pos[a|c]],q[pos[b|c]]=q[pos[b|c]],q[pos[a|c]]
            yield tuple(q),(a,b)

def permute(p,perm):
    result=[]
    for x in p:
        value=0
        while x:
            low=x&-x;value|=1<<perm[low.bit_length()-1];x^=low
        result.append(value)
    return tuple(result)

def independent_minimum(p,n):
    F=1<<(n-2);best=10**9;bestmask=None
    for uppermask in range(1<<((F//2)-1)):
        B=[rank(f,n-2,uppermask) for f in range(F)];signs=[]
        for x,y in zip(p,p[1:]):
            f,g=x>>2,y>>2
            if f!=g:signs.append((None,0,1 if B[g]>B[f] else -1))
            else:
                a,b=x&3,y&3;h=(a^b).bit_length()-1
                signs.append((f,h,1 if (b^(b>>1))>(a^(a>>1)) else -1))
        C=1;c=[[0]*4 for _ in range(F)]
        for left,right in zip(signs,signs[1:]):
            free={z[0] for z in (left,right) if z[0] is not None}
            assert len(free)<=1
            if not free:C+=left[2]!=right[2]
            else:
                f=next(iter(free))
                for m in range(4):
                    a=left[2]*(-1 if left[0] is not None and m>>left[1]&1 else 1)
                    b=right[2]*(-1 if right[0] is not None and m>>right[1]&1 else 1)
                    c[f][m]+=a!=b
        total=C;mask=uppermask<<(F+F//2)
        for z in range(F//2):
            candidates=[]
            for controller in (0,1):
                chosen=[];val=0
                for f in (2*z,2*z+1):
                    phase=(f&1)^controller
                    m=min((2*phase,2*phase+1),key=c[f].__getitem__)
                    chosen.append(m);val+=c[f][m]
                candidates.append((val,controller,chosen))
            val,controller,chosen=min(candidates);total+=val;mask|=controller<<(F+z)
            for f,m in zip((2*z,2*z+1),chosen):mask|=(m&1)<<f
        if total<best:best=total;bestmask=mask
    assert fast_runs([rank(x,n,bestmask) for x in range(1<<n)],p)==best
    return best,bestmask

def main():
    start=time.monotonic();pfile=Path(__file__).with_name('paired_boolean_term_orders_certificate.json.gz')
    raw=gzip.decompress(pfile.read_bytes());data=json.loads(raw);orders={tuple(r['order']) for r in data['n5_orders_and_certificates']}
    assert len(orders)==546;coherent=noncoherent=0;cases=0;dig=hashlib.sha256();min5=10**9
    for row in data['n5_orders_and_certificates']:
        p=tuple(row['order']);term_check(p,5)
        assert all(q in orders for q,pair in neighbors(p,5))
        cert=row['coherence_certificate']
        A=[[((b>>j)&1)-((a>>j)&1) for j in range(5)] for a,b in zip(p,p[1:])]
        if cert['coherent']:
            w=cert['integer_weights'];assert all(sum(a*b for a,b in zip(r,w))>0 for r in A);coherent+=1
        else:
            y=dict(cert['integer_farkas']);assert y and all(x>0 for x in y.values())
            assert all(sum(v*A[i][j] for i,v in y.items())==0 for j in range(5));noncoherent+=1
            hist=Counter()
            for perm in permutations(range(5)):
                pp=permute(p,perm);R,mask=independent_minimum(pp,5);hist[R]+=1;cases+=1;min5=min(min5,R)
                dig.update(json.dumps((p,perm,R,mask)).encode())
            assert dict(hist)=={int(k):v for k,v in row['paired_test']['priority_histogram'].items()}
    assert (coherent,noncoherent,cases,min5)==(516,30,3600,12)
    six=[]
    for row in data['n6_examples']:
        p=tuple(row['order']);term_check(p,6);A=[[((b>>j)&1)-((a>>j)&1) for j in range(6)] for a,b in zip(p,p[1:])]
        y=dict(row['coherence_certificate']['integer_farkas']);assert y and all(v>0 for v in y.values())
        assert all(sum(v*A[i][j] for i,v in y.items())==0 for j in range(6))
        hist=Counter()
        for perm in permutations(range(6)):
            pp=permute(p,perm);R,mask=independent_minimum(pp,6);hist[R]+=1
            dig.update(json.dumps((p,perm,R,mask)).encode())
        assert dict(hist)=={int(k):v for k,v in row['paired_test']['priority_histogram'].items()}
        six.append(min(hist))
    out={'status':'VERIFIED_INTEGER_BOOLEAN_TERM_ORDER_CERTIFICATES_AND_INDEPENDENT_PAIRED_MINIMA',
         'scope':'Exact listed546-order flip-component closure, ALL integer coherence/noncoherence certificates, ALL3600noncoherentQ5 priorities plus1440specifiedQ6priorities. This verifier invokes no LP or ancestor optimizer. Not an all-dimensional lower bound.',
         'n5_orders':546,'coherent':coherent,'noncoherent':noncoherent,'new_Q5_priority_cases':cases,
         'noncoherent_Q5_minimum':min5,'two_Q6_minima':six,'certificate_raw_sha256':hashlib.sha256(raw).hexdigest(),
         'violations':0,'seconds':time.monotonic()-start,'audit_sha256':dig.hexdigest()}
    Path(__file__).with_name('paired_boolean_term_orders_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
