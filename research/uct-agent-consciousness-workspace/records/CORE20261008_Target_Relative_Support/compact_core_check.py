from itertools import product
import json

def mins(F):
    return {s for s in F if not any(t!=s and t&s==t for t in F)}
def meet(F,V):
    a=V
    for s in F:a&=s
    return a
checked=monotone=0
for word in range(1,65536):
    F={s for s in range(16) if word>>s&1}; M=mins(F)
    assert M and all(any(m&s==m for m in M) for s in F)
    k=meet(F,15)
    assert k==meet(M,15)
    assert (len(M)==1)==(k in F)
    checked+=1
    if all(t in F for s in F for t in range(16) if s&t==s):
        monotone+=1
        cuts={d for d in range(16) if (15^d) not in F}
        assert cuts=={d for d in range(16) if all(d&m for m in M)}

def step(s,q,u,w):
    if not(s&1):return None
    return ((q if s&2 else 0)|(q if s&4 else 0))^ (u if s&8 else 0) ^ (w if s&16 else 0)
words=list(product(tuple(product((0,1),repeat=2)),repeat=3))
F=set(); FV=set()
for s in range(64):
    ok=True
    for word in words:
        a,b=0,1
        for u,w in word:
            a,b=step(s,a,u,w),step(s,b,u,w)
            if a is None or b is None or a^b!=1:ok=False;break
        if not ok:break
    assert ok==bool((s&1) and (s&6))
    if ok:
        F.add(s)
        if all(step(s,q,0,w)!=step(s,q,1,w) for q,w in product((0,1),repeat=2)):FV.add(s)
assert mins(F)=={3,5} and meet(F,63)==1 and 1 not in F
assert mins(FV)=={11,13}
assert mins({d for d in range(64) if (63^d) not in F})=={1,6}

def gate(c,a,b,q):return (q if a==b else 0) if c else None
FG={s for s in range(8) if s&1 and gate(1,bool(s&2),bool(s&4),0)!=gate(1,bool(s&2),bool(s&4),1)}
assert FG=={1,7} and all((7^(1<<i)) not in FG for i in range(3))
assert gate(1,0,0,1)==1 and gate(1,0,0,gate(1,0,1,1))==0
print(json.dumps({'scope':'compact exact mathematical verifier, no phenomenal measurement','status':'PASS','nonempty_families':checked,'nonempty_monotone_families':monotone,'relay_minimal_masks':sorted(mins(F)),'retention_plus_input_masks':sorted(mins(FV)),'nonmonotone_success_masks':sorted(FG),'simultaneous_vs_sequential_final_q':[1,0]}))
