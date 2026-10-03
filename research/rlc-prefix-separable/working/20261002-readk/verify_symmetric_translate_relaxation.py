#!/usr/bin/env python3
"""Exact central two-chain relaxation; explicit nonadditive integer witness.

No floating-point solver is used by the verifier. The supplied symmetric
integer scores came from exploratory LP, but all claims use integer checks.
The original all-additive lower-bound problem remains open.
"""
import hashlib,json,time
from itertools import product
from pathlib import Path
from verify_paired_sibling_ranks import rank
from verify_gray_reflection_graph import counts,positive_chambers,order_and_scores

def central_dp(rr):
    """Minimize exact fresh-bit conditional cyclic mean over central shuffles.

    State: first/second chain counts, last chain, forward and reflected edge
    signs. 2 means a fresh comparison. The reflected comparison is reversed.
    A fresh edge contributes one expected cyclic turn and has no adjacent
    fresh edge. Mirror pairs therefore contribute two to the mean.
    """
    M=len(rr);close=int(rr[0]>rr[-1])
    D={(1,0,0,close,close):(0,(0,))};layers=[]
    for k in range(1,M):
        E={}
        for (i,j,last,s,t),(c,path) in D.items():
            a=i-1 if last==0 else j-1
            for side in [0,1]:
                b=i if side==0 else j
                if b>=M or (side==1 and j>=i):continue
                if a==b:ss=tt=2
                else:
                    ss=int(rr[b]>rr[a]);tt=int(rr[M-1-a]>rr[M-1-b])
                add=int(s!=2 and ss!=2 and s!=ss)+int(t!=2 and tt!=2 and t!=tt)+2*int(ss==2)
                key=(i+int(side==0),j+int(side==1),side,ss,tt)
                val=(c+add,path+(side,))
                if key not in E or val<E[key]:E[key]=val
        D=E;layers.append([k+1,len(D),min(v[0] for v in D.values())])
    ans=[]
    for (i,j,last,s,t),(c,path) in D.items():
        a=i-1 if last==0 else j-1;middle=int(rr[M-1-a]>rr[a])
        ans.append((c+int(s!=2 and s!=middle)+int(t!=2 and t!=middle),
            path+tuple(1-x for x in path[::-1])))
    return min(ans),layers

def project_word(path,base):
    ij=[0,0];p=[]
    for side in path:
        assert side==0 or ij[1]<ij[0]
        p.append(2*base[ij[side]]+side);ij[side]+=1
    assert ij==[len(base),len(base)]
    return p

def exact_mean(p,rr):
    # Independent direct conditional mean formula, no DP states involved.
    v=[x>>1 for x in p];fresh=[v[i]==v[(i+1)%len(p)] for i in range(len(p))]
    assert not any(fresh[i] and fresh[(i+1)%len(p)] for i in range(len(p)))
    signs=[int(rr[v[(i+1)%len(p)]]>rr[v[i]]) for i in range(len(p))]
    return sum(fresh)+sum(not fresh[i] and not fresh[(i+1)%len(p)] and
        signs[i]!=signs[(i+1)%len(p)] for i in range(len(p)))

def enumerate_halves(M):
    for half in product([0,1],repeat=M):
        if half[0]!=0:continue
        i=j=0;valid=True
        for side in half:
            if side==1 and j>=i:valid=False;break
            if side==0:i+=1
            else:j+=1
        if valid:yield half+tuple(1-s for s in half[::-1])

def main():
    st=time.monotonic();stream=hashlib.sha256();cases=paths=0
    for n in [1,2,3]:
        M=1<<n;shuffles=list(enumerate_halves(M))
        for w in positive_chambers(n):
            for reflection in range(M):
                base=[x^reflection for x in order_and_scores(w)[0]]
                assert all(base[M-1-i]==(base[i]^(M-1)) for i in range(M))
                for mask in range(1<<((M>>1)-1)):
                    rr=[rank(x,n,mask) for x in range(M)]
                    seq=[rr[x] for x in base];(minimum,path),_=central_dp(seq)
                    brute=min(exact_mean(project_word(s,base),rr) for s in shuffles)
                    assert brute==minimum==exact_mean(project_word(path,base),rr)
                    cases+=1;paths+=len(shuffles)
                    stream.update(json.dumps((n,w,reflection,mask,minimum)).encode())
    n=5;M=32;mask=2;rr=[rank(x,n,mask) for x in range(M)]
    (minimum,path),layers=central_dp(rr)
    assert minimum==18
    first=[-123,-121,-95,-93,-87,-67,-65,-59,-45,-43,-41,-39,-37,-15,-3,-1]
    scores=first+[-x for x in first[::-1]];shift=32
    assert all(scores[i]<scores[i+1] for i in range(31))
    assert all(scores[i]+scores[31-i]==0 for i in range(32))
    p=sorted(range(64),key=lambda x:scores[x>>1]+shift*(x&1))
    values=[scores[x>>1]+shift*(x&1) for x in p]
    assert len(set(values))==64 and p==project_word(path,list(range(32)))
    assert all(p[63-i]==(p[i]^63) for i in range(64))
    pos={x:i for i,x in enumerate(p)}
    assert all(pos[x]<pos[y] for x in range(64) for y in range(64) if x!=y and x&y==x)
    assert all((a^b)!=1 for a,b in zip(p,p[1:]+p[:1]))
    assert exact_mean(p,rr)==18
    # With no fresh comparison, ALL65536 bottom-label assignments have C18.
    for low in range(65536):
        C=counts([rank(x,6,(mask<<16)|low) for x in p])[1]
        assert C==18
    # Exact common-addition rejection; the two differences cancel to zero.
    a,b,z=4,1,34
    assert a&z==b&z==0 and pos[a]<pos[b] and pos[b|z]<pos[a|z]
    def difference(x,y):return [((y>>h)&1)-((x>>h)&1) for h in range(6)]
    d1=difference(a,b);d2=difference(b|z,a|z)
    assert all(x+y==0 for x,y in zip(d1,d2))
    parent_numeric_C=counts(rr)[1]
    out={'status':'EXACT_CENTRAL_EQUAL_TRANSLATION_RELAXATION_OBSTRUCTION',
        'scope':'Finite relaxed conditional mean18, versus proposed24 doubling for a certified Q5 parent with all-signed minimum12. This scan is NOT additive on Q6; no counterexample to the actual target.',
        'dp_bruteforce_contexts':cases,'independent_bruteforce_paths':paths,
        'selected_parent_mask':2,'parent_numeric_cyclic_value':parent_numeric_C,
        'relaxed_central_dp_minimum':minimum,'dp_layers':layers,
        'symmetric_integer_upper_scores':scores,'positive_translation':shift,
        'vertex_order':p,'integer_full_scores_in_order':values,
        'fresh_comparison_count':0,'all_fresh_assignments_checked':65536,
        'cyclic_value_every_fresh_assignment':18,
        'common_addition_infeasibility':{'a':a,'b':b,'disjoint_z':z,
            'a_before_b_positions':[pos[a],pos[b]],
            'b_plus_z_before_a_plus_z_positions':[pos[b|z],pos[a|z]],
            'strict_required_difference_vectors':[d1,d2],'sum_vector':[0]*6},
        'audit_stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('symmetric_translate_relaxation_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
