#!/usr/bin/env python3
"""R115 exact anchored-content-geometry witnesses."""
import math, json

labels=("x0","x1","x2")
A={"x0":(0,0),"x1":(1,0),"x2":(1,1)}
B={"x0":(0,0),"x1":(1,1),"x2":(1,0)}
C={"x0":(0,0),"x1":(2,0),"x2":(2,2)}

def hamming(a,b):
    return sum(int(x!=y) for x,y in zip(a,b))

def euclid(a,b):
    return math.dist(a,b)

def matrix(codes,metric):
    return [
        [metric(codes[i],codes[j]) for j in labels]
        for i in labels
    ]

def upper_values(M):
    return sorted(
        M[i][j]
        for i in range(len(M))
        for j in range(i+1,len(M))
    )

def causal_signature(code):
    return tuple(int(v>0) for v in code)

sigA={k:causal_signature(v) for k,v in A.items()}
sigC={k:causal_signature(v) for k,v in C.items()}

hA=matrix(A,hamming)
hB=matrix(B,hamming)
eA=matrix(A,euclid)
eC=matrix(C,euclid)
cA=matrix(sigA,hamming)
cC=matrix(sigC,hamming)

result={
    "round":"R115",
    "grounded_label_swap":{
        "A_hamming":hA,
        "B_hamming":hB,
        "same_unlabeled_distance_multiset":upper_values(hA)==upper_values(hB),
        "unlabeled_distance_multiset":upper_values(hA),
        "same_grounded_distance_matrix":hA==hB,
    },
    "coordinate_scale":{
        "A_euclidean":eA,
        "C_euclidean":eC,
        "same_raw_euclidean_matrix":eA==eC,
        "A_causal_signatures":sigA,
        "C_causal_signatures":sigC,
        "same_causal_signature_geometry":cA==cC,
        "causal_hamming":cA,
    },
    "interpretation":"Unanchored geometry can preserve abstract distances while swapping grounded meanings; raw coordinate scale can change while selected causal discrimination structure is preserved. Not a consciousness measurement."
}

assert result["grounded_label_swap"]["same_unlabeled_distance_multiset"]
assert not result["grounded_label_swap"]["same_grounded_distance_matrix"]
assert not result["coordinate_scale"]["same_raw_euclidean_matrix"]
assert result["coordinate_scale"]["same_causal_signature_geometry"]

print(json.dumps(result,indent=2))
