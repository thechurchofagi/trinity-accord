#!/usr/bin/env python3
"""Integer audit of the analytic periodic constant-cut-budget theorem.

No numerical optimization or floating-point feasibility is used. The
constant-size graph proof, explicit rank and shared-capacity packing
establish all-dimensional scope; generated scans audit them through Q18.
"""
from pathlib import Path
from collections import defaultdict
from itertools import product
import hashlib,json,time
from verify_gray_reflection_graph import order_and_scores
from verify_paired_sibling_ranks import linear_graph,rank,fast_runs
from paired_sibling_ancestor_optimizer import optimize
from paired_antipodal_half_graph import split,integer_cut

I=(0,1,8,9,2,3,4,5,10,11,12,13,6,7)
V=(0,1,14,15,8,9,2,3,4,5,10,11,12,13,6,7)
F=(14,15)

def key(a,b):return tuple(sorted((a,b)))

def raw_graph(p,n):
    """Independent raw product enumeration, retaining both signs per edge."""
    q=1<<(n-1);offset=[q-(1<<(n-h-1)) for h in range(n-1)]
    labels=[];signs=[]
    for x,y in zip(p,p[1:]):
        h=(x^y).bit_length()-1
        labels.append(q-1 if h==n-1 else offset[h]+(x>>(h+2)))
        gx=x^(x>>1);gy=y^(y>>1)
        signs.append(1 if gy>gx else -1)
    D=0;counts=defaultdict(lambda:[0,0]);turns=[]
    for i,(a,b) in enumerate(zip(labels,labels[1:])):
        s=signs[i]*signs[i+1]
        if a==b:
            assert s==-1;D+=1
        else:counts[key(a,b)][int(s<0)]+=1
        turns.append({'triple':p[i:i+3],'labels':[a,b],'product':s})
    edges=tuple((a,b,c[0]-c[1]) for (a,b),c in sorted(counts.items()) if c[0]!=c[1])
    return {'D':D,'K':sum(min(c) for c in counts.values()),'W':sum(abs(v) for a,b,v in edges),
            'edges':edges,'raw_counts':[(a,b,*c) for (a,b),c in sorted(counts.items())],'turns':turns}

def core_weights(k):return tuple(16*(1<<j) for j in reversed(range(k-4)))+(1,6,8,4)

def predicted_core(k,T):
    q=1<<(k-1);a=q-2;b=q-1;u=[q-8+j for j in range(4)];A=2*T-1;B=2*T
    return tuple(sorted([(u[0],a,-A),(u[0],b,B),(u[1],a,A),(u[1],b,A),
                         (u[2],a,A),(u[2],b,-A),(u[3],a,-A),(u[3],b,-B)]))

def energy(edges,negative):return sum(v*(-1 if ((a in negative)!=(b in negative)) else 1) for a,b,v in edges)

def active_brute(edges,top):
    active=sorted({u for a,b,v in edges for u in (a,b)}-{top})
    return max(energy(edges,{active[j] for j,b in enumerate(bits) if b}) for bits in product((0,1),repeat=len(active)))

def loads_certificate(edges,cycles,paths=()):
    J={key(a,b):v for a,b,v in edges};loads=defaultdict(int)
    for z,amount in cycles:
        assert len(set(z))==len(z);sg=1
        for a,b in zip(z,z[1:]+z[:1]):
            sg*=1 if J[key(a,b)]>0 else -1;loads[key(a,b)]+=amount
        assert sg==-1
    for z,amount in paths:
        assert len(set(z))==len(z)
        for a,b in zip(z,z[1:]):loads[key(a,b)]+=amount
    assert all(load<=abs(J[e]) for e,load in loads.items())
    return [(a,b,v) for (a,b),v in sorted(loads.items())]

def core_audit(k):
    T=1<<(k-4);N=1<<k;q=N//2;w=core_weights(k)
    p,scores=order_and_scores(w);core=tuple(x>>(k-4) for x in p)
    assert core==I+V*(T-1)+F
    g=linear_graph(p,k);assert g['edges']==predicted_core(k,T)
    assert (g['D'],g['K'],g['W'])==(0,2,16*T-6)
    s=split(g,k);cut=integer_cut(s['edges'],s['root'],s['top'])
    A=2*T-1;u=[q-8+j for j in range(4)];a=q-2;b=q-1
    assert cut['value']==2*A
    cycles=[([a,u[0],b,u[1]],A),([a,u[3],b,u[2]],A)]
    loads=loads_certificate(g['edges'],cycles)
    negative={u[3]};E=energy(g['edges'],negative)
    assert E==8*T-2==active_brute(g['edges'],b)
    phi=(g['W']-E)//2;assert phi==2*A==sum(amount for z,amount in cycles)
    out={'n':k,'T':T,'weights':w,'D':0,'K':2,'W':g['W'],'half_cut':cut,
         'graph_edges':g['edges'],'cycles':cycles,'cycle_loads':loads,
         'attaining_negative_indices':sorted(negative),'E_max':E,'phi':phi,'R_min':4*T+1,
         'projected_word_sha256':hashlib.sha256(bytes(core)).hexdigest()}
    if k<=12:
        z=optimize(g,k);assert z['E_max']==E
        mask=1<<u[3];assert fast_runs([rank(x,k,mask) for x in range(N)],p)==out['R_min']
        out['independent_ancestor_optimizer']=z
    return out

def high_audit(n):
    k=n-1;T=1<<(n-5);N=1<<n;q=N//2;v=core_weights(k);w=v+(sum(v)+1,)
    oldp=order_and_scores(v)[0];p,scores=order_and_scores(w)
    assert p==oldp+tuple(x+(1<<k) for x in oldp)
    oldg=predicted_core(k,T);oldq=1<<(k-1)
    def embed(u,right):
        if u==oldq-1:return q-2
        if u==oldq-2:return q-4+right
        assert oldq-8<=u<=oldq-5
        return q-16+4*right+(u-(oldq-8))
    predicted=[]
    for right in (0,1):
        for a,b,c in oldg:
            predicted.append((*key(embed(a,right),embed(b,right)),c*(-1 if right and b==oldq-1 else 1)))
    predicted+= [(q-13,q-1,-1),(q-12,q-1,1)]
    g=linear_graph(p,n);assert g['edges']==tuple(sorted(predicted))
    assert (g['D'],g['K'],g['W'])==(0,4,32*T-10)
    s=split(g,n);cut=integer_cut(s['edges'],s['root'],s['top']);assert cut['value']==1
    A=2*T-1;u=[q-16+j for j in range(4)];a=q-4;b=q-2;r=q-1
    cycles=[([a,u[0],b,u[1]],A),([a,u[3],b,u[2]],A)]
    paths=[([b,u[3],r],1)];loads=loads_certificate(s['edges'],cycles,paths)
    joint=sum(amount for z,amount in paths)+2*sum(amount for z,amount in cycles)
    assert joint==8*T-3
    negative={q-13,q-12,q-11,q-10,q-3};E=energy(g['edges'],negative)
    assert E==16*T-4==active_brute(g['edges'],r)
    phi=(g['W']-E)//2;assert phi==joint
    out={'n':n,'T':T,'weights':w,'D':0,'K':4,'W':g['W'],'half_cut':cut,
         'cut_only_budget':5,'graph_edges':g['edges'],'half_edges':s['edges'],
         'half_negative_cycles':cycles,'half_terminal_paths':paths,'combined_half_edge_loads':loads,
         'joint_P_plus_2C':joint,'attaining_negative_indices':sorted(negative),'E_max':E,'phi':phi,'R_min':8*T+2,
         'order_sha256':hashlib.sha256(json.dumps(p,separators=(',',':')).encode()).hexdigest()}
    if n<=12:
        z=optimize(g,n);assert z['E_max']==E
        mask=sum(1<<j for j in negative)
        assert fast_runs([rank(x,n,mask) for x in range(N)],p)==out['R_min']
        out['independent_ancestor_optimizer']=z;out['attaining_mask']=mask
    return out

def main():
    start=time.monotonic();base=raw_graph(I+F,4);increment=raw_graph(V+V[:2],4)
    assert (base['D'],base['K'],base['W'])==(0,2,10)
    assert (increment['D'],increment['K'],increment['W'])==(0,0,16)
    assert increment['edges']==tuple((a,b,2*(1 if v>0 else -1)) for a,b,v in base['edges'])
    core_rows=[];high_rows=[];dig=hashlib.sha256()
    for k in range(4,19):
        z=core_audit(k);core_rows.append(z);dig.update(json.dumps(z,sort_keys=True).encode())
        print(json.dumps({j:z[j] for j in ('n','T','D','K','W','phi','R_min')}),flush=True)
    for n in range(5,19):
        z=high_audit(n);high_rows.append(z);dig.update(json.dumps(z,sort_keys=True).encode())
        print(json.dumps({j:z[j] for j in ('n','T','D','K','W','cut_only_budget','phi','R_min')}),flush=True)
    out={'status':'VERIFIED_ALL_DIMENSION_CONSTANT_CUT_BUDGET_AND_EXACT_CYCLE_REPAIR',
         'core_theorem':'For k>=4, v_k=(16*2^(k-5),...,16,1,6,8,4) has D=0,K=2, phi=2^(k-2)-2, R_min=2^(k-2)+1.',
         'high_theorem':'For n>=5, append H=1+sum(v_(n-1)). Then D=0,K=4,lambda=1, phi=2^(n-2)-3, R_min=2^(n-2)+2.',
         'scope':'No positive-density D+K-only or D+K+lambda-only inequality can hold uniformly over genuine generic scans. The main M_n and universal paired quarter problems remain open.',
         'base_raw_certificate':base,'one_period_raw_increment_certificate':increment,
         'core_rows':core_rows,'high_rows':high_rows,'violations':0,'seconds':time.monotonic()-start,'audit_sha256':dig.hexdigest()}
    Path(__file__).with_name('paired_constant_cut_budget_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({j:v for j,v in out.items() if j not in ('base_raw_certificate','one_period_raw_increment_certificate','core_rows','high_rows')}),flush=True)

if __name__=='__main__':main()
