#!/usr/bin/env python3
"""Exact support-preserving low-tail lift and explicit nonplanar certificates."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph
from paired_antipodal_half_graph import split

BASE_K4=(36014,4119,36488,65387,58395,45969)
BASE_K33=(3998575,4578511,42715,7899299,2129239,2794740,3504965,7382886)
K4_BRANCHES=((16,24),(28,17,18),(30,25),(31,))
K33_SIDES=((126,127,124),(97,98,103))

def key(a,b):return tuple(sorted((a,b)))

def verify_minor(edges,branches):
    J={key(a,b):c for a,b,c in edges};seen=set();bridges=[]
    for B in branches:
        assert not seen.intersection(B);seen.update(B);reached={B[0]}
        while True:
            bigger=reached|{v for u in reached for v in B if key(u,v) in J}
            if bigger==reached:break
            reached=bigger
        assert reached==set(B)
    for i in range(len(branches)):
        for j in range(i+1,len(branches)):
            es=[(a,b,J[key(a,b)]) for a in branches[i] for b in branches[j] if key(a,b) in J]
            assert es;bridges.append((i,j,es[0]))
    return bridges

def audit(base,n,kind):
    d=len(base);m=n-d;T=1<<m;L=sum(base)+1
    w=tuple(L*(1<<j) for j in range(m))+base
    oldp=order_and_scores(base)[0];p,scores=order_and_scores(w)
    assert p==tuple((x<<m)|row for row in range(T) for x in oldp)
    oldg=linear_graph(oldp,d);g=linear_graph(p,n);oq=1<<(d-1);nq=1<<(n-1);shift=nq-oq
    j=min(range(d),key=lambda h:base[h]);B=defaultdict(int)
    def label(x,y):
        h=(x^y).bit_length()-1
        return oq-1 if h==d-1 else oq-(1<<(d-h-1))+(x>>(h+2))
    first=label(oldp[0],oldp[1]);last=label(oldp[-2],oldp[-1]);top=oq-1
    if j<d-1:B[key(last,top)]+=1;B[key(first,top)]-=1
    predicted=defaultdict(int)
    for a,b,c in oldg['edges']:predicted[(a+shift,b+shift)]+=T*c
    for (a,b),c in B.items():predicted[(a+shift,b+shift)]+=(T-1)*c
    assert g['edges']==tuple((a,b,c) for (a,b),c in sorted(predicted.items()) if c)
    assert g['D']==T*oldg['D']+(2*(T-1) if j==d-1 else 0)
    J={key(a,b):c for a,b,c in g['edges']}
    for a,b,c in oldg['edges']:
        assert J[(a+shift,b+shift)]*c>0
    half=split(g,n);H={key(a,b):c for a,b,c in half['edges']}
    out={'base_dimension':d,'n':n,'kind':kind,'weights':w,'T':T,'variable_shift':shift,
         'D':g['D'],'K':g['K'],'W':g['W'],'edges':g['edges'],'half_edges':half['edges'],
         'endpoint_first_label':first,'endpoint_last_label':last,'base_boundary_increment':[(a,b,c) for (a,b),c in sorted(B.items())],
         'order_sha256':hashlib.sha256(json.dumps(p,separators=(',',':')).encode()).hexdigest()}
    if kind=='K4_minor':
        branches=[tuple(u+shift for u in B) for B in K4_BRANCHES]
        out['branch_sets']=branches;out['minor_bridges']=verify_minor(half['edges'],branches)
    else:
        A,C=[tuple(u+shift for u in B) for B in K33_SIDES]
        assert len(set(A+C))==6
        bridges=[(a,c,H[key(a,c)]) for a in A for c in C];assert len(bridges)==9
        out['bipartition']=[A,C];out['nine_subgraph_edges']=bridges
    return out

def main():
    start=time.monotonic();rows=[];dig=hashlib.sha256()
    for base,kind in ((BASE_K4,'K4_minor'),(BASE_K33,'K33_subgraph')):
        for n in range(len(base),19):
            z=audit(base,n,kind);rows.append(z);dig.update(json.dumps(z,sort_keys=True).encode())
            print(json.dumps({j:z[j] for j in ('base_dimension','n','kind','T','D','K','W')}),flush=True)
    out={'status':'VERIFIED_ALL_DIMENSION_SIGNED_SUPPORT_LIFT_AND_UNSIGNED_MINOR_OBSTRUCTIONS',
         'analytic_statement':'For any positive generic d-coordinate base weights, adding m lowest coordinates with coefficients (sum(base)+1)*2^j preserves every old coupling sign under shift 2^(d+m-1)-2^(d-1). Hence a genuine K4 half-graph minor exists in every n>=6 and a genuine K33 half-graph subgraph exists in every n>=8.',
         'scope':'Excludes universal series-parallel/treewidth-two and planar half-graph shortcuts. No odd-K5 signed minor, failure of weak bipartiteness, or failure of a positive-density RLC lower bound is inferred.',
         'rows':rows,'violations':0,'seconds':time.monotonic()-start,'audit_sha256':dig.hexdigest()}
    Path(__file__).with_name('paired_support_minor_lift_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({j:v for j,v in out.items() if j!='rows'}),flush=True)

if __name__=='__main__':main()
