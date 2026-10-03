#!/usr/bin/env python3
"""Exact fragmented two-face loss certificates at genuine additive scans."""
from pathlib import Path
from collections import defaultdict
from itertools import combinations
import hashlib,json,random,time
from verify_paired_all_lex_quarter import labels_signs
from verify_paired_sibling_ranks import linear_graph,rank
from verify_gray_reflection_graph import order_and_scores,counts
from paired_sibling_ancestor_optimizer import optimize

def certify(p,n,j,k,g=None):
    N=1<<n;mask=(1<<j)|(1<<k);pos={x:i for i,x in enumerate(p)}
    bases=tuple(x for x in range(N) if x&mask==0);good={}
    labels,signs=labels_signs(p,n);g=linear_graph(p,n) if g is None else g
    for b in bases:
        ids=sorted(pos[x] for x in (b,b|(1<<j),b|(1<<k),b|mask))
        if ids[-1]-ids[0]==3:
            t=ids[0];x=p[t]
            assert tuple(p[t:t+4])==(x,x^(1<<j),x^(1<<k),x^mask)
            good[b]=t
    F=len(bases)-len(good);forced=[];pairs=[];loads=defaultdict(int)
    def contribution(i):
        a,b=labels[i],labels[i+1];assert a!=b
        return tuple(sorted((a,b))),signs[i]*signs[i+1]
    def pair(a,b):
        aa,sa=contribution(a);bb,sb=contribution(b);assert aa==bb and sa==-sb
        pairs.append((a,b));loads[aa]+=1
    if j>k:
        for t in good.values():
            for i in (t,t+1):
                assert labels[i]==labels[i+1] and signs[i]==-signs[i+1];forced.append(i)
        lower=2*len(good);case='fastest_above_second'
    elif k==j+1:
        for t in good.values():pair(t,t+1)
        lower=len(good);case='adjacent_controller'
    else:
        for b,t in good.items():
            other=b^(1<<(j+1))
            if b<other and other in good:pair(t,good[other]);pair(t+1,good[other]+1)
        lower=len(pairs);case='nonadjacent_paired_good_faces'
    used=forced+[i for pp in pairs for i in pp];assert len(set(used))==len(used)
    raw=defaultdict(lambda:[0,0])
    for i in range(N-2):
        if labels[i]!=labels[i+1]:
            key,s=contribution(i);raw[key][int(s<0)]+=1
    assert all(load<=min(raw[key]) for key,load in loads.items())
    assert lower==len(forced)+len(pairs)<=g['D']+g['K']
    assert lower>=N//4-2*F
    return {'j':j,'k':k,'case':case,'parallel_faces':N//4,'fragmented_faces':F,
            'good_face_starts':sorted(good.items()),'forced_turn_indices':forced,
            'raw_opposite_product_pairs':pairs,'certified_D_plus_K':lower,
            'uniform_R_lower':1+max(0,N//4-2*F)}

def main():
    start=time.monotonic();rng=random.Random(202610031012);rows=[];digest=hashlib.sha256();pairs_checked=0
    def check(w,tag,forced_pair=None):
        nonlocal pairs_checked
        n=len(w);res=order_and_scores(w)
        if res is None:return False
        p=res[0];g=linear_graph(p,n);opt=optimize(g,n)
        actual_R=counts(tuple(rank(x,n,opt['mask']) for x in p))[0]
        summaries=[];best=None;selected=None
        for a,b in combinations(range(n),2):
            j,k=(a,b) if abs(w[a])<abs(w[b]) else (b,a)
            c=certify(p,n,j,k,g);pairs_checked+=1
            assert actual_R>=1+c['certified_D_plus_K']>=c['uniform_R_lower']
            summaries.append([j,k,c['fragmented_faces'],c['certified_D_plus_K']])
            if best is None or c['certified_D_plus_K']>best['certified_D_plus_K']:best=c
            if forced_pair==(j,k):selected=c
            if tag=='cardinality_no_good_two_faces':assert c['fragmented_faces']==1<<(n-2)
        if forced_pair is not None:assert selected is not None and selected['fragmented_faces']==0
        row={'n':n,'tag':tag,'weights':w,'D_K':[g['D'],g['K']],
             'exact_R_min':actual_R,'attaining_mask':opt['mask'],'optimizer_table_sha256':opt['table_sha256'],
             'all_pair_F_and_budget':summaries,'best_certificate':best,'selected_face_block_certificate':selected}
        rows.append(row);digest.update(json.dumps(row,sort_keys=True).encode());return True
    for n in range(3,11):
        for trial in range(8):
            while True:
                w=tuple(rng.choice((-1,1))*x for x in rng.sample(range(1,100000),n))
                if check(w,'arbitrary_signed_integer_pressure_not_coverage'):break
    for n in range(5,13):
        for trial in range(6):
            j,k=rng.sample(range(n),2);rest=tuple(a for a in range(n) if a not in (j,k))
            while True:
                slow=tuple(rng.sample(range(1,10000),n-2));w=[0]*n;w[j]=1;w[k]=2
                for a,v in zip(rest,slow):w[a]=8*v
                if check(tuple(w),'arbitrary_slow_order_separated_faces',(j,k)):break
    for n in range(3,13):check(tuple((1<<n)+(1<<j) for j in range(n)),'cardinality_no_good_two_faces')
    out={'state':'VERIFIED_ALL_DIMENSION_FRAGMENTED_TWO_FACE_REPAIR',
         'seed':202610031012,'all_dimension_theorem':'For any generic additive scan, choose j,k with |w_j|<|w_k| and let F be fragmented parallel two-faces. Every paired rank has R>=1+max(0,2^(n-2)-2F). If F=0 then R>=2^(n-2)+1 regardless of slow-coordinate order.',
         'all_dimension_gap_certificate':'For all n>=3, every two-coordinate face is fragmented in a cardinality-first scan: its three cardinality levels contain an entire middle layer of size at least n>2. Thus F=2^(n-2) for every pair.',
         'genuine_scan_count':len(rows),'coordinate_pairs_audited':pairs_checked,'records':rows,
         'violations':0,'verification_digest':digest.hexdigest(),'elapsed_seconds':round(time.monotonic()-start,3),
         'limitations':'Exact conditional all-dimensional theorem with explicit loss, not a dimension-uniform positive bound on arbitrary scans. Pressure is not chamber coverage. Main M_n target remains OPEN.'}
    Path(__file__).with_name('paired_fragmented_faces_certificate.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k] for k in ('state','genuine_scan_count','coordinate_pairs_audited','violations','verification_digest','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
