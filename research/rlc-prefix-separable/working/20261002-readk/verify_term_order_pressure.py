#!/usr/bin/env python3
"""Finite follow-up on Maclagan Example 2.5; no asymptotic claim."""
from itertools import permutations
from collections import Counter
from pathlib import Path
import json
from verify_gray_face_merge_dp import gray,statistics

def main():
    p=(0,1,2,4,8,3,16,5,6,9,17,10,18,12,7,11,20,24,19,13,21,14,22,25,26,15,28,23,27,29,30,31)
    pos={x:i for i,x in enumerate(p)};checks=0
    for x in range(32):
        for y in range(x+1,32):
            common=31^(x|y);z=common
            while z:
                assert (pos[x]<pos[y])==(pos[x|z]<pos[y|z])
                checks+=1;z=(z-1)&common
    best=32;hist=Counter()
    for perm in permutations(range(5)):
        q=tuple(sum(((x>>j)&1)<<perm[j] for j in range(5)) for x in p)
        for z in range(32):
            o=tuple(x^z for x in q);R,C=statistics(tuple(map(gray,o)));hist[C]+=1
            if R<best:best=R;witness=o
    assert best==min(hist)==18 and checks==945 and sum(hist.values())==3840
    r={'source':'Maclagan, arXiv math/9809134v2, Example 2.5',
       'all_translation_pair_checks':checks,'coordinate_assignments_and_reflections':3840,
       'minimum_R_C':[18,18],'cyclic_histogram':dict(sorted(hist.items())),
       'minimizing_order':witness,
       'interpretation':'This single published noncoherent order does not defeat 1/4 or 5/16 density. No all-dimensional conclusion.'}
    Path(__file__).with_name('noncoherent_term_order_pressure.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))

if __name__=='__main__':main()
