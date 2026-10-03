#!/usr/bin/env python3
"""Integer audit of middle-vertex incidence budgets for paired variables."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores,positive_chambers
from verify_paired_sibling_ranks import linear_graph

def audit(p,n,detail=False):
    q=1<<(n-1);offset=[q-(1<<(n-h-1)) for h in range(n-1)]
    labels=[];levels=[];sg=[];meta={q-1:(n-1,0)}
    for h in range(n-1):
        for prefix in range(1<<(n-h-2)):meta[offset[h]+prefix]=(h,prefix)
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1;u=q-1 if h==n-1 else offset[h]+(x>>(h+2))
        labels.append(u);levels.append(h);sg.append(1 if (y^(y>>1))>(x^(x>>1)) else -1)
    raw=defaultdict(lambda:[0,0]);same=defaultdict(int);middles=defaultdict(set);L=defaultdict(int);ends=defaultdict(int)
    for u in labels:L[u]+=1
    if labels:ends[labels[0]]+=1;ends[labels[-1]]+=1
    for i,(u,v) in enumerate(zip(labels,labels[1:])):
        middle=p[i+1]
        for z in {u,v}:
            h,prefix=meta[z]
            if h<n-1:assert middle>>(h+2)==prefix
            assert middle not in middles[z];middles[z].add(middle)
        if u==v:same[u]+=1;assert sg[i]!=sg[i+1]
        else:raw[tuple(sorted((u,v)))][int(sg[i]!=sg[i+1])]+=1
    norm=defaultdict(int);cancel=defaultdict(int);incident=defaultdict(int);ancnorm=defaultdict(int)
    for (u,v),(plus,minus) in raw.items():
        for z in (u,v):
            norm[z]+=abs(plus-minus);cancel[z]+=min(plus,minus);incident[z]+=plus+minus
        if meta[u][0]<meta[v][0]:ancnorm[u]+=abs(plus-minus)
        else:ancnorm[v]+=abs(plus-minus)
    rows=[]
    for u,(h,prefix) in sorted(meta.items()):
        size=1<<n if h==n-1 else 1<<(h+2)
        assert incident[u]+same[u]==len(middles[u])<=size
        assert norm[u]+2*cancel[u]+same[u]<=size
        assert incident[u]+2*same[u]+ends[u]==2*L[u]
        assert ancnorm[u]<=size
        if detail or norm[u]+2*cancel[u]+same[u]==size:
            rows.append({'variable':u,'level':h,'prefix':prefix,'prefix_subcube_size':size,
                         'net_incident_norm':norm[u],'incident_cancellation':cancel[u],
                         'same_label_turns':same[u],'raw_mixed_incidence':incident[u],
                         'comparison_occurrences':L[u],'endpoint_comparisons':ends[u],
                         'middle_vertex_count':len(middles[u]),'ancestor_net_norm':ancnorm[u]})
    g=linear_graph(p,n)
    assert sum(same.values())==g['D'] and sum(cancel.values())==2*g['K']
    assert sum(norm.values())==2*g['W']
    return {'n':n,'D':g['D'],'K':g['K'],'W':g['W'],'variables':q,'budgets':rows,
            'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}

def main():
    start=time.monotonic();rng=random.Random(202610031246);rows=[];actual=0;arbitrary=0;ties=0
    for n in range(2,5):
        for w in positive_chambers(n):
            z=audit(order_and_scores(w)[0],n);rows.append({'kind':'all_positive_small_chambers','weights':w,**z});actual+=1
    for n in range(5,13):
        for j in range(16):
            w=tuple((1<<n)+(1<<h) for h in range(n)) if j==0 else tuple(rng.randrange(1,10000000) for h in range(n))
            os=order_and_scores(w)
            if os is None:ties+=1;continue
            z=audit(os[0],n);rows.append({'kind':'new_genuine_generic_pressure','weights':w,**z});actual+=1
    for n in range(2,11):
        for j in range(8):
            p=list(range(1<<n));rng.shuffle(p);z=audit(p,n);rows.append({'kind':'arbitrary_vertex_permutation','permutation_seed_index':j,**z});arbitrary+=1
    # Explicit local impossibility in the former diagnostic nonideal family.
    # Variable462 in Q10 has h=3,p=14, prefix size32. Its two ancestor
    # tree edges 462-499 and462-510 would each have capacity33.
    diagnostic={'n':10,'variable':462,'level':3,'prefix':14,'size':32,
                'two_higher_ancestor_edges':[(462,499,33),(462,510,33)],
                'incident_norm_lower_bound':66,'conclusion':'Impossible for ANY cube vertex permutation, hence impossible for additive scans.'}
    assert diagnostic['incident_norm_lower_bound']>diagnostic['size']
    out={'status':'VERIFIED_LOCAL_MIDDLE_VERTEX_INCIDENCE_BUDGETS','analytic_statement':'For every vertex permutation and paired variable u=theta_(h,p), net incident norm +2 incident cancellation + same-label turns <=2^(h+2). Also raw mixed incidence +2 same turns + endpoint comparisons =2 comparison occurrences. Top uses total cube size.',
         'scope':'Necessary realizability constraints, not sufficient for a generic additive scan and not a constant-density theorem. Elementary event counting is an inherited technique.',
         'seed':202610031246,'actual_scans':actual,'arbitrary_permutations':arbitrary,'nongeneric_rejected':ties,
         'explicit_impossible_diagnostic':diagnostic,'rows':rows,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('paired_local_vertex_budget_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','explicit_impossible_diagnostic')}),flush=True)

if __name__=='__main__':main()
