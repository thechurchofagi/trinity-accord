#!/usr/bin/env python3
"""Complete small geometric tests, not an asymptotic theorem.

Q4 sweep completeness reuses the audited positive chamber enumeration.
All final quantities and prefix separators are checked with integers.
"""
import hashlib,json,time
from pathlib import Path
from itertools import permutations
from adaptive_query_research import *
from verify_gray_reflection_graph import positive_chambers

def main():
    st=time.monotonic();digest=hashlib.sha256();out=[];prefixchecks=0
    for n in (3,4):
        trees=list(query_trees(tuple(range(n))));assert len(trees)=={3:6,4:96}[n]
        scans=[]
        for w in positive_chambers(n):
            p=additive_order(w)
            for z in range(1<<n):scans.append((tuple(-a if z>>h&1 else a for h,a in enumerate(w)),tuple(x^z for x in p)))
        assert len(scans)=={3:96,4:5376}[n]
        budgets=[]
        for q in trees:
            validate(q,n);minimum=1<<n;attainer=None
            for w,p in scans:
                g=graph(q,n,p);value=g['D']+g['K']+g['q']
                if value<minimum:minimum=value;attainer={'weights':w,'D':g['D'],'K':g['K'],'q':g['q']}
            budgets.append({'queries':sorted(q.items()),'minimum_D_plus_K_plus_q':minimum,'attainer':attainer})
            digest.update(json.dumps(budgets[-1],sort_keys=True).encode())
        q=trees[0];universalmin=1<<n;universalC=1<<n;best=None;states=0
        for w,p in scans:
            R,C,bits,g=exact_orientation_minimum(q,n,p);states+=1<<g['q'];universalC=min(universalC,g['min_C'])
            if R<universalmin:universalmin=R;best={'weights':w,'bits':sorted(bits.items()),'R':R,'C':C}
        assert universalmin=={3:3,4:4}[n]
        # All geometry isometries of one representative, including coordinate relabeling.
        orbit=set()
        for perm in permutations(range(n)):
            relabel={u:perm[j] for u,j in q.items()}
            for z in range(1<<n):orbit.add(tuple(sorted(reflect_geometry(relabel,n,z).items())))
        assert orbit=={tuple(sorted(t.items())) for t in trees}
        # A complete orbit maps every signed sweep and orientation to the representative.
        # Hence the exhaustive representative lower bound holds for every listed geometry.
        rr=rank_table(q,n,dict(best['bits']));inv=sorted(range(1<<n),key=rr.__getitem__)
        for k in range(1,1<<n):
            z=inv[k];c=separator(q,n,dict(best['bits']),z)
            for x in range(1<<n):
                S=sum(c[j]*(((x>>j)&1)-((z>>j)&1)) for j in range(n))
                assert (S<=-1)==(rr[x]<k);assert (S>=0)==(rr[x]>=k);prefixchecks+=1
        row={'n':n,'tree_count':len(trees),'signed_scan_count':len(scans),'orientation_words':states,
             'representative_queries':sorted(q.items()),'all_geometry_isometry_orbit_size':len(orbit),
             'minimum_R_over_ALL_geometries_orientations_actual_scans':universalmin,
             'minimum_C_over_ALL_geometries_orientations_actual_scans':universalC,
             'attainer_for_representative':best,'budgets':budgets}
        out.append(row);print(json.dumps({k:v for k,v in row.items() if k!='budgets'}),flush=True)
    receipt={'status':'EXACT_SMALL_LOCALLY_ADAPTIVE_QUERY_AUDIT','scope':'ALL locally distinct child-query geometries in Q3 and Q4, ALL orientations and genuine signed additive sweeps. NOT an all-n constant-density bound.',
             'rows':out,'prefix_vertex_checks':prefixchecks,'stream_sha256':digest.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    receipt['receipt_sha256']=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()
    Path('locally_adaptive_query_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
