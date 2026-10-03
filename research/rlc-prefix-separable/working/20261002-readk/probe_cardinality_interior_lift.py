#!/usr/bin/env python3
"""Find a fixed cardinality-secondary core with nonzero interior coupling."""
from collections import defaultdict
import itertools
import json
from pathlib import Path
from verify_gray_reflection_graph import gray, graph
from verify_face_local_obstruction import subset_scores

def interior(secondary):
    n=len(secondary);scores=subset_scores(secondary)
    p=tuple(sorted(range(1<<n),key=lambda x:(x.bit_count(),scores[x])))
    j=defaultdict(int);D=0
    for a,b,c in zip(p,p[1:],p[2:]):
        if a.bit_count()!=b.bit_count() or b.bit_count()!=c.bit_count():continue
        h=(a^b).bit_length()-1;k=(b^c).bit_length()-1
        e=1 if gray(b)>gray(a) else -1;f=1 if gray(c)>gray(b) else -1
        if h==k:D+=1
        else:j[tuple(sorted((h,k)))]+=e*f
    return p,tuple((h,k,v) for (h,k),v in sorted(j.items()) if v),D

def main():
    records=[];found=None
    for n in range(3,9):
        checked=0
        for perm in itertools.permutations(range(n)):
            secondary=tuple(1<<j for j in perm);p,edges,D=interior(secondary);checked+=1
            if edges:
                found={'n':n,'secondary':secondary,'interior_edges':edges,'interior_D':D,'full_edges':graph(p,n)['edges']};break
        records.append({'n':n,'permutations_checked':checked,'found':bool(found)})
        if found:break
    out={'scope':'Permutation of binary secondary priorities, first witness only; not all coherent secondary chambers.','records':records,'first_witness':found}
    Path(__file__).with_name('cardinality_interior_lift_discovery.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps(out))

if __name__=='__main__':main()
