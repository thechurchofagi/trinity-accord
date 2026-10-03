#!/usr/bin/env python3
"""Geometric exact bias formula in the positive w0<w1 cone."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,time
from verify_gray_reflection_graph import positive_chambers
from verify_paired_sibling_ranks import rank
from probe_paired_quartet_controller_walls import cells,costs

def audit(offsets,a,b,B):
    assert a>0 and b>0 and a!=b
    r,p,masks,word,C,local=costs(offsets,a,b,B,return_costs=True)
    position={(f,x):i for i,(s,f,x) in enumerate(word)};N=len(word);out=[]
    for f in range(len(offsets)):
        input_order=(0,1,2,3) if a<b else (0,2,1,3)
        ix=[position[f,x] for x in input_order]
        adjacent=[ix[j+1]==ix[j]+1 for j in range(3)]
        A=[min(local[f][2*t],local[f][2*t+1]) for t in (0,1)];delta=A[1]-A[0]
        predicted=0;left=right=None
        components=[]
        if a>b:
            assert local[f][0]==local[f][1] and local[f][2]==local[f][3]
            i=0
            while i<3:
                if not adjacent[i]:i+=1;continue
                j=i
                while j<2 and adjacent[j+1]:j+=1
                lo=ix[i];hi=ix[j+1];qleft=1 if i%2==0 else -1;qright=1 if j%2==0 else -1
                sl=sr=0
                if lo>0:
                    prev=word[lo-1][1];assert prev!=f;sl=1 if B[f]>B[prev] else -1
                if hi<N-1:
                    nxt=word[hi+1][1];assert nxt!=f;sr=1 if B[nxt]>B[f] else -1
                predicted+=qleft*sl+qright*sr
                components.append({'first_edge_index':i,'last_edge_index':j,'outside_left_sign':sl,'outside_right_sign':sr,'bias_contribution':qleft*sl+qright*sr})
                i=j+1
        elif adjacent[1] and not(adjacent[0] and adjacent[2]):
            lo=ix[0] if adjacent[0] else ix[1]
            hi=ix[3] if adjacent[2] else ix[2]
            if lo>0:
                prev=word[lo-1][1];assert prev!=f
                left=1 if B[f]>B[prev] else -1;predicted+=left
            if hi<N-1:
                nxt=word[hi+1][1];assert nxt!=f
                right=1 if B[nxt]>B[f] else -1;predicted+=right
        assert delta==predicted
        out.append({'face':f,'within_face_adjacencies':adjacent,'middle_bridge_present':adjacent[1],
                    'component_left_cross_sign':left,'component_right_cross_sign':right,
                    'exact_bias':delta,'conditional_costs':A,'all_internal_components_w0_dominant':components})
    return out,r,p

def main():
    start=time.monotonic();hist=Counter();cases=0;facechecks=0;saved=[];digest=hashlib.sha256()
    for w in positive_chambers(3):
        F=8;scores=[sum(w[j]*((f>>j)&1) for j in range(3)) for f in range(F)]
        for aa,bb in cells(scores):
            for a,b in ((aa,bb),(bb,aa)):
                for mask in range(8):
                    B=[rank(f,3,mask) for f in range(F)]
                    details,r,p=audit(scores,a,b,B);cases+=1;facechecks+=F
                    for z in details:hist[str(z['exact_bias'])]+=1
                    digest.update(json.dumps((w,a.numerator,a.denominator,b.numerator,b.denominator,mask,details)).encode())
                    if any(z['exact_bias']!=0 for z in details) and len(saved)<8:
                        saved.append({'upper_weights':w,'a':[a.numerator,a.denominator],
                                      'b':[b.numerator,b.denominator],'upper_mask':mask,
                                      'relaxed_minimum':r,'paired_minimum':p,'faces':details})
    out={'status':'VERIFIED_EXACT_TWO_CONE_GEOMETRIC_CONTROLLER_BIAS','analytic_statement':'For w0<w1, Delta_f=0 except an internal middle bridge not contained in a whole face block, whose bias is its two exterior cross signs. For w0>w1, low bit0 is irrelevant and bias sums signed exterior fields of every internal face component, with edge baseline signs(+,-,+). Missing global-endpoint fields count0.',
         'scope':'Analytic local formula for all dimensions and any face-block rank. Finite fixed-upper cells audit it; no uniform density of bias conflicts is proved.',
         'fixed_upper_metrics':12,'wall_upper_rank_cases':cases,'face_bias_checks':facechecks,
         'bias_histogram':dict(hist),'examples':saved,'violations':0,'seconds':time.monotonic()-start,'audit_sha256':digest.hexdigest()}
    Path(__file__).with_name('quartet_middle_bridge_bias_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='examples'}),flush=True)

if __name__=='__main__':main()
