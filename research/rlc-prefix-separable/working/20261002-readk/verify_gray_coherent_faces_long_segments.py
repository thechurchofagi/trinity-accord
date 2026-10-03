#!/usr/bin/env python3
"""Exact face characterization and all-dimensional long-segment witness."""
from pathlib import Path
from itertools import product
import hashlib,json,time
from verify_gray_reflection_graph import gray,counts
from verify_face_local_obstruction import subset_scores

def vertices(base,free):
    out=[base]
    for j in free:out += [x|(1<<j) for x in out]
    return out

def direct_R_max(values):
    signs=[1 if b>a else -1 for a,b in zip(values,values[1:])]
    R=1+sum(a!=b for a,b in zip(signs,signs[1:]));cur=mx=2
    for a,b in zip(signs,signs[1:]):
        cur=cur+1 if a==b else 2;mx=max(mx,cur)
    return R,mx

def main():
    start=time.monotonic();digest=hashlib.sha256();face_rows=[];face_total=0;vertex_total=0
    for n in range(1,10):
        good=bad=0;maxdim=0
        for state in product((0,1,2),repeat=n):
            free=tuple(j for j,s in enumerate(state) if s==2)
            base=sum(1<<j for j,s in enumerate(state) if s==1)
            predicted=not any(j+1 in free for j in free)
            coefs={j:gray(base|(1<<j))-gray(base) for j in free}
            vv=vertices(base,free)
            affine=all(gray(x)==gray(base)+sum(a for j,a in coefs.items() if x>>j&1) for x in vv)
            assert affine==predicted
            if predicted:
                good+=1;maxdim=max(maxdim,len(free))
                assert all(coefs.values())
            else:
                bad+=1;j=next(j for j in free if j+1 in free)
                aa,bb=base,base|(1<<(j+1))
                # Two translated coordinate edges demand opposite signs for w_j.
                one=gray(aa|(1<<j))-gray(aa)
                two=gray(bb|(1<<j))-gray(bb)
                assert one*two<0
                assert two-one==-(1<<(j+1))
            face_total+=1;vertex_total+=len(vv)
            digest.update(json.dumps((n,state,predicted,coefs,affine)).encode())
        assert maxdim==(n+1)//2
        face_rows.append({'n':n,'all_faces':3**n,'coherent_affine_faces':good,
                          'noncoherent_faces':bad,'maximum_affine_face_dimension':maxdim})
    rows=[];scan_vertices=0
    for n in range(1,19):
        even=tuple(j for j in range(n) if j%2==0);odd=tuple(j for j in range(n) if j%2)
        coef={j:1 if j==0 else 3*(1<<(j-1)) for j in even}
        span=sum(coef.values());A=span+1
        w=tuple(coef[j] if j in coef else A*(1<<odd.index(j)) for j in range(n))
        score=subset_scores(w);p=tuple(sorted(range(1<<n),key=score.__getitem__))
        assert len(set(score))==1<<n
        L=1<<len(even);expected=tuple(sorted(vertices(0,even)))
        assert p[:L]==expected
        assert all(gray(x)==score[x] for x in expected)
        ranks=tuple(map(gray,p));assert all(a<b for a,b in zip(ranks[:L],ranks[1:L]))
        R,mx=direct_R_max(ranks);rr,cc,_=counts(ranks)
        assert R==rr==(1<<(n-1)) and mx>=L
        row={'n':n,'free_even_coordinates':even,'fixed_odd_coordinates':odd,
             'integer_score_weights':w,'block_width':A,'first_coherent_face_size':L,
             'actual_longest_run_vertices':mx,'actual_R_C':[rr,cc],
             'full_order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}
        rows.append(row);scan_vertices+=1<<n;digest.update(json.dumps(row,sort_keys=True).encode())
    out={'state':'VERIFIED_COHERENT_FACE_CHARACTERIZATION_AND_EXPONENTIAL_LONG_SEGMENT',
         'all_dimension_theorem':'A coordinate face has coherent forward-Gray order iff its free coordinates contain no adjacent positions. Its rank is affine exactly under the same condition. Maximum coherent-face dimension is ceil(n/2). The displayed integer scan has a contiguous increasing Gray segment of size 2^ceil(n/2) and total R=2^(n-1).',
         'face_audits':face_rows,'all_faces_audited':face_total,'face_vertices_audited':vertex_total,
         'integer_scan_witnesses':rows,'full_scan_vertices_audited':scan_vertices,
         'violations':0,'verification_digest':digest.hexdigest(),
         'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'The analytic theorem covers all dimensions; finite audits test formulas. This excludes a polynomial maximum-run route for Gray, not a positive total-run lower bound. It does not characterize all coherent slabs or longest possible scan segments.'}
    Path(__file__).with_name('gray_coherent_faces_long_segments_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','all_faces_audited','face_vertices_audited','full_scan_vertices_audited','violations','verification_digest','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
