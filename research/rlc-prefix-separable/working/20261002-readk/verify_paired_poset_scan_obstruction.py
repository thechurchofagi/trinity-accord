#!/usr/bin/env python3
"""Poset-coherent, nonadditive scans defeat direction-only paired bounds.

All paired ranks admit Boolean-poset extensions with <=6n-7 runs. Forward
Gray admits antipodal poset extensions with exactly4n-8 runs for n>=3.
The constructions are NOT additive: explicit translated-face nesting
requires simultaneously w2<w3 and w3<w2 once n>=5.
"""
from pathlib import Path
import hashlib,json,random,time
from verify_paired_sibling_ranks import rank,fast_runs,separator_check,linear_graph
from paired_antipodal_half_graph import split

def gray(x):return x^(x>>1)

def group(faces,values,peak):
    prefix=[];suffix=[]
    for y in faces:
        vertices=[(y<<2)|j for j in range(4)]
        signs=[values[vertices[j+1]]>values[vertices[j]] for j in range(3)]
        assert signs[0]==peak and signs[-1]!=peak
        change=next(j for j in (1,2) if signs[j]!=signs[0])
        prefix+=vertices[:change+1];suffix+=vertices[change+1:]
    prefix.sort(key=values.__getitem__,reverse=not peak)
    suffix.sort(key=values.__getitem__,reverse=peak)
    p=prefix+suffix;assert fast_runs(values,p)==2
    return p

def arbitrary_paired(n,theta):
    values=[rank(x,n,theta) for x in range(1<<n)];p=[];G=0
    for weight in range(n-1):
        faces=[y for y in range(1<<(n-2)) if y.bit_count()==weight]
        for peak in (True,False):
            selected=[y for y in faces if (values[y<<2]&1)==int(not peak)]
            if selected:p+=group(selected,values,peak);G+=1
    assert len(p)==1<<n and len(set(p))==1<<n
    R=fast_runs(values,p);assert R<=3*G-1<=6*n-7
    edges=poset_check(p,n)
    return {'n':n,'groups':G,'R':R,'bound':6*n-7,'all_cube_edges_checked':edges,
            'mask_sha256':hashlib.sha256(theta.to_bytes(((1<<(n-1))-1+7)//8,'little')).hexdigest(),
            'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}

def poset_check(p,n):
    N=1<<n;position=[0]*N
    for i,x in enumerate(p):position[x]=i
    count=0
    for x in range(N):
        for j in range(n):
            if not(x>>j&1):assert position[x]<position[x|(1<<j)];count+=1
    assert count==n*(N//2)
    return count

def antipodal_gray(n):
    assert n>=3;N=1<<n;values=[gray(x) for x in range(N)];p0=[];layers=n-2
    for weight in range(layers):
        faces=[y for y in range(1<<(n-3)) if y.bit_count()==weight]
        p0+=group(faces,values,True)
    assert len(p0)==N//2 and fast_runs(values,p0)==2*layers
    p=p0+[x^(N-1) for x in reversed(p0)]
    assert all(p[i]^p[-1-i]==N-1 for i in range(N))
    assert fast_runs(values,p)==4*n-8
    edgecount=poset_check(p,n);g=linear_graph(p,n);h=split(g,n)
    assert 1+g['D']+g['K']+(g['W']-sum(c for u,v,c in g['edges']))//2==4*n-8
    result={'n':n,'R':4*n-8,'antipodal':True,'all_cube_edges_checked':edgecount,
            'D':g['D'],'K':g['K'],'W':g['W'],'Gray_unsatisfied_graph_cost':(g['W']-sum(c for u,v,c in g['edges']))//2,
            'half_signed_edges':len(h['edges']),'order_sha256':hashlib.sha256(json.dumps(p).encode()).hexdigest()}
    if n>=5:
        pos={x:i for i,x in enumerate(p)}
        assert pos[4]<pos[8] and pos[11]<pos[7]
        result['strict_additive_contradiction']={'comparisons':[(4,8),(11,7)],
            'positions':[(pos[4],pos[8]),(pos[11],pos[7])],
            'required_inequalities':['w2<w3','w3<w2']}
    if n<=6:result['strict_prefix_separator_checks']=separator_check(values,n,0)
    return result

def main():
    start=time.monotonic();rng=random.Random(202610031348)
    grayrows=[antipodal_gray(n) for n in range(3,19)]
    randomrows=[]
    for n in range(2,13):
        for trial in range(8):randomrows.append(arbitrary_paired(n,rng.getrandbits((1<<(n-1))-1)))
    out={'status':'VERIFIED_ALL_DIMENSION_DIRECTION_ONLY_PAIRED_SCAN_OBSTRUCTIONS',
         'analytic_statement':'Every paired rank on Q_n,n>=2 admits a Boolean-poset linear extension with at most6n-7 runs. Forward Gray on every n>=3 admits an antipodal Boolean-poset extension with exactly4n-8 runs. For n>=5 the latter is explicitly nonadditive.',
         'scope':'Excludes positive-density paired certificates from coordinate directions alone; the antipodal Gray witness also passes ancestry and all local permutation budgets. These are NOT generic additive scans, not main M_n upper bounds.',
         'proof':'Within an upper-cardinality layer, different two-coordinate faces are incomparable. Every paired local four-vertex natural order is unimodal, peak if theta0=0 and valley if theta0=1. Merge all first monotone parts by rank in their common direction, then all remaining parts in reverse direction; each group has exactly2 runs and preserves every face order. There are at most2(n-1) groups. For Gray all groups are peaks; in the top-bit-zero half there are n-2 layers, each has one turn, and each layer boundary adds one. Complement-reversing this half preserves the poset and antipodal order and doubles its runs, because Gray complement changes only the top rank bit. The nested incomparable faces4,8 and11,7 contradict shared additive translation.',
         'antipodal_gray_actual_dimension_audits':grayrows,'random_paired_rank_audits':randomrows,
         'seed':202610031348,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path(__file__).with_name('paired_poset_scan_obstruction_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('proof','antipodal_gray_actual_dimension_audits','random_paired_rank_audits')}),flush=True)

if __name__=='__main__':main()
