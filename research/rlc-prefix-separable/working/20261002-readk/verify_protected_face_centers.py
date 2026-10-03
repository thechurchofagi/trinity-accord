#!/usr/bin/env python3
"""A positive-density restricted-scan theorem allowing interior face overlaps.

The general all-dimensional lemma uses any certified fixed-core minimum L;
it does not require importing the separately saved complete Q5 theorem.
"""
from pathlib import Path
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import rank,fast_runs,linear_graph
from paired_sibling_ancestor_optimizer import optimize

CORE=(65,66,68,72,80);D=5;Q=32;STEP=284

def verify_centers(weights,theta,k,L):
    n=len(weights);p,scores=order_and_scores(weights);F=1<<(n-D)
    cp,cs=order_and_scores(weights[:D]);S=sum(abs(w) for w in weights[:D])
    norm=[s-cs[0] for s in cs];assert norm==[S-s for s in reversed(norm)]
    outerp,outer_scores=order_and_scores(weights[D:])
    gaps=[b-a for a,b in zip(outer_scores,outer_scores[1:])]
    assert not gaps or min(gaps)>S-norm[k]
    position=[0]*(1<<n)
    for i,x in enumerate(p):position[x]=i
    values=[rank(x,n,theta) for x in range(1<<n)]
    retained=0;minimum_face_runs=10**9
    for f in range(F):
        face=[(f<<D)|u for u in cp]
        center=face[k:Q-k];where=[position[x] for x in center]
        assert where==list(range(where[0],where[0]+len(center)))
        face_runs=fast_runs(values,face);minimum_face_runs=min(minimum_face_runs,face_runs)
        assert face_runs>=L
        center_turns=fast_runs(values,center)-1
        assert center_turns>=max(0,face_runs-1-2*k)>=max(0,L-1-2*k)
        retained+=center_turns
    R=fast_runs(values,p);bound=1+F*max(0,L-1-2*k)
    assert R>=1+retained>=bound
    return {'n':n,'weights':weights,'k':k,'L':L,'core_trim_threshold':S-norm[k],
            'minimum_outer_gap':min(gaps) if gaps else None,'F':F,'R':R,'bound':bound,
            'retained_center_turns':retained,'minimum_face_runs':minimum_face_runs,
            'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}

def good_two_faces(p,n):
    total=0
    for start in range(len(p)-3):
        v=p[start:start+4];origin=v[0]
        diff=0
        for x in v:diff|=origin^x
        if diff.bit_count()==2:
            lo=(diff&-diff).bit_length()-1
            if diff==3<<lo:total+=1
    return total

def main():
    start=time.monotonic();rng=random.Random(202610031359);cp,cs=order_and_scores(CORE)
    # Independent direct enumeration; the optimizer only supplies a cross-check.
    histogram={};minimum=10**9;attainer=None
    for theta in range(1<<15):
        values=[rank(x,5,theta) for x in range(32)];R=fast_runs(values,cp)
        histogram[R]=histogram.get(R,0)+1
        if R<minimum:minimum=R;attainer=theta
    assert minimum==12
    g=linear_graph(cp,5);opt=optimize(g,5)
    assert (32+g['D']-opt['E_max'])//2==minimum
    assert fast_runs([rank(x,5,opt['mask']) for x in range(32)],cp)==minimum
    rows=[];classopt=[]
    for n in range(5,14):
        w=CORE+tuple(STEP*(1<<j) for j in range(n-5))
        p,s=order_and_scores(w);assert good_two_faces(p,n)==0
        for trial in range(8):
            theta=rng.getrandbits((1<<(n-1))-1)
            row=verify_centers(w,theta,3,minimum);row['zero_contiguous_adjacent_two_faces']=True;rows.append(row)
        if n<=10:
            g=linear_graph(p,n);op=optimize(g,n);R=(2**n+g['D']-op['E_max'])//2
            assert R>=1+5*(1<<(n-5))
            assert fast_runs([rank(x,n,op['mask']) for x in range(1<<n)],p)==R
            classopt.append({'n':n,'exact_full_family_minimum':R,'bound':1+5*(1<<(n-5)),
                             'optimizer_states':op['conditional_states'],'table_sha256':op['table_sha256']})
    # Signed core/outer and permuted outer priorities preserve the gap class;
    # directly recompute face restrictions instead of trusting the reflection code.
    for n in range(6,12):
        for trial in range(8):
            tail=list(STEP*(1<<j) for j in range(n-5));rng.shuffle(tail)
            w=tuple(b*(1 if rng.getrandbits(1) else -1) for b in CORE+tuple(tail))
            theta=rng.getrandbits((1<<(n-1))-1);rows.append(verify_centers(w,theta,3,minimum))
    out={'status':'VERIFIED_PROTECTED_CENTER_POSITIVE_DENSITY_INTERIOR_OVERLAP_CLASS',
         'analytic_lemma':'Use the LOWEST d INPUT coordinates as a q=2^d core with fixed-weight paired minimum L, normalized subset scores s0=0<...<s(q-1)=S, and every outer gap>S-s_k. For EVERY paired mask R>=1+max(0,L-1-2k)*2^(n-d). Each face middleq-2k vertices is a protected contiguous global block. This holds all n and arbitrary signed outer/core weights after normalization.',
         'concrete_all_n_statement':'For every n>=5, core(65,66,68,72,80) has exact paired minimum12, S351,s3=68. All generic outer weights with consecutive subset-score gaps>283 have R>=1+5*2^(n-5). In particular outer tail(284,568,1136,...) genuinely overlaps interior vertices and has no contiguous adjacent-coordinate two-faces.',
         'scope':'A restricted-weight ALL-DIMENSION theorem, not the main all-weight RLC or M_n target. The general trimming lemma is elementary sign accounting. The finite core12 is exhaustively independently checked; no reliance on an unavailable priorQ5 archive.',
         'core_exhaustion':{'weights':CORE,'all_normalized_masks':32768,'minimum':minimum,'first_attaining_mask':attainer,
                            'histogram':histogram,'ancestor_crosscheck':opt},
         'actual_mask_audits':rows,'exact_class_family_optima':classopt,
         'seed':202610031359,'violations':0,'seconds':time.monotonic()-start,
         'known_implementation_failure':'In the preceding separate interior-loss verifier, initial score translation lookup mistakenly indexed the sorted-score tuple by vertex; corrected to dict(zip(order,scores)) before certification. No theorem or rank formula was changed.'}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('protected_face_centers_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('actual_mask_audits','exact_class_family_optima','core_exhaustion','known_implementation_failure')}),flush=True)

if __name__=='__main__':main()
