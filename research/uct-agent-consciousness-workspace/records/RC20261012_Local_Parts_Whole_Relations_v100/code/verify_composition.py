#!/usr/bin/env python3
"""Exact finite checks for Local Parts, Whole Relations (Python standard library).

These are mathematical fixtures, not human/AI consciousness measurements.
General claims are proved in manuscript.md; enumeration is a separate check.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
from pathlib import Path


def subsets(xs):
    xs = tuple(xs)
    return [frozenset(c) for n in range(len(xs)+1) for c in combinations(xs, n)]


def matrix(n, values):
    a = [[F(0) for _ in range(n)] for _ in range(n)]
    for (i,j), v in zip(combinations(range(n), 2), values):
        a[i][j] = a[j][i] = F(v)
    return a


def is_pseudometric(a):
    n=len(a)
    return all(a[i][i]==0 for i in range(n)) and all(
        0 <= a[i][j] == a[j][i] <= a[i][k]+a[k][j]
        for i,j,k in product(range(n), repeat=3))


def closure(a):
    d=[r[:] for r in a]
    for k in range(len(d)):
        for i in range(len(d)):
            for j in range(len(d)):
                d[i][j]=min(d[i][j],d[i][k]+d[k][j])
    return d


def simple_paths(n,i,j):
    others=[k for k in range(n) if k not in (i,j)]
    for k in range(n-1):
        for mid in permutations(others,k):
            yield (i,)+mid+(j,)


def path_sum(a,path):
    return sum((a[u][v] for u,v in zip(path,path[1:])),F(0))


def repair_threshold(c,lower):
    best=F(0); witness=None
    n=len(c)
    for i,j in combinations(range(n),2):
        for p in simple_paths(n,i,j):
            deficit=(lower[i][j]-path_sum(c,p))/(len(p)-1)
            if deficit>best:
                best=deficit; witness={'endpoints':[i,j],'path':list(p),
                    'lower':str(lower[i][j]),'original_path_cost':str(path_sum(c,p))}
    return best,witness


def expanded(c,delta):
    return [[F(0) if i==j else min(F(1),v+delta) for j,v in enumerate(row)]
            for i,row in enumerate(c)]


def compatible(lower,upper):
    return all(lower[i][j]<=upper[i][j] for i,j in product(range(len(lower)),repeat=2))


def check_distance():
    levels=(F(0),F(1,2),F(1))
    points=list(product((0,1),repeat=2))
    cap=[[min(int(x[0]!=y[0]),int(x[1]!=y[1])) for y in points] for x in points]
    accepted=[]; metric_count=0; closure_cases=0
    for vals in product(levels,repeat=6):
        a=matrix(4,vals)
        if compatible(a,cap):
            accepted.append(vals); metric_count+=is_pseudometric(a)
        d=closure(a)
        assert is_pseudometric(d) and compatible(d,a)
        for i,j in combinations(range(4),2):
            assert d[i][j] == min(path_sum(a,p) for p in simple_paths(4,i,j))
        closure_cases+=1
    assert len(accepted)==9 and metric_count==1
    # An allowed raw dissimilarity is not necessarily a pseudometric.
    assert not is_pseudometric(cap)
    assert all(v==0 for row in closure(matrix(4,[cap[i][j] for i,j in combinations(range(4),2)])) for v in row)
    # On three states exhaust both upper and lower matrices, independently compare
    # the path formula with closure at all possible crossing thresholds.
    repair_cases=0; strictly_pathwise=0; positive=0
    for cv in product(levels,repeat=3):
        c=matrix(3,cv)
        for lv in product(levels,repeat=3):
            lower=matrix(3,lv)
            delta,w=repair_threshold(c,lower)
            assert compatible(lower,closure(expanded(c,delta)))
            if delta>0:
                assert not compatible(lower,closure(expanded(c,delta/2)))
                positive+=1
            candidates={F(0)}
            for i,j in combinations(range(3),2):
                for p in simple_paths(3,i,j):
                    candidates.add(max(F(0),(lower[i][j]-path_sum(c,p))/(len(p)-1)))
            direct=min(x for x in sorted(candidates) if compatible(lower,closure(expanded(c,x))))
            assert direct==delta
            pairwise=max([F(0)]+[lower[i][j]-c[i][j] for i,j in combinations(range(3),2)])
            strictly_pathwise+=int(delta>pairwise)
            repair_cases+=1
    c=matrix(3,(0,1,0)); lower=matrix(3,(0,1,0))
    delta,w=repair_threshold(c,lower)
    assert delta==F(1,2)
    # Product-coordinate approximate-collapse bound is sharp up to diameter one.
    square=[]
    for delta in (F(0),F(1,10),F(1,4),F(1,2),F(1)):
        d=closure(expanded(matrix(4,[cap[i][j] for i,j in combinations(range(4),2)]),delta))
        assert d[0][3]==min(F(1),2*delta)
        square.append({'slack':str(delta),'opposite_distance':str(d[0][3])})
    return {'four_state_dissimilarities':729,'expansive_projection_compatible':len(accepted),
        'also_pseudometric':metric_count,'closure_matrices_checked':closure_cases,
        'three_state_lower_upper_pairs':repair_cases,'positive_repair_thresholds':positive,
        'path_threshold_stricter_than_all_direct_pairs':strictly_pathwise,
        'strict_witness':{'cap':[[str(v) for v in row] for row in c],
                         'lower':[[str(v) for v in row] for row in lower],
                         'minimum_uniform_slack':str(F(1,2)),
                         'path':w},'square_bound':square}


# A finite presheaf: vertex data plus an edge datum visible only when both ends occur.
V=frozenset((0,1,2)); EDGE=3

def fields(u):
    return tuple(sorted(u))+((EDGE,) if {0,2}<=u else ())


def sections(u):
    fs=fields(u)
    return [dict(zip(fs,bits)) for bits in product((0,1),repeat=len(fs))]


def restrict(s,v):
    return {k:s[k] for k in fields(v)}


def agree(a,b):
    return all(a[k]==b[k] for k in a.keys() & b.keys())


def check_gluing():
    opens=subsets(V); secs={u:sections(u) for u in opens}
    chains=0
    for u in opens:
        for v in subsets(u):
            for w in subsets(v):
                for s in secs[u]:
                    assert restrict(restrict(s,v),w)==restrict(s,w)
                    chains+=1
    cover_count=matching=nonunique=0
    for u in opens:
        for cover in subsets(subsets(u)):
            union=frozenset().union(*cover)
            if union!=u: continue
            cover_count+=1
            ordered=sorted(cover,key=lambda x:(len(x),tuple(sorted(x))))
            for fam in product(*(secs[v] for v in ordered)):
                if not all(agree(a,b) for a,b in combinations(fam,2)): continue
                gs=[s for s in secs[u] if all(restrict(s,v)==a for v,a in zip(ordered,fam))]
                assert gs
                matching+=1; nonunique+=int(len(gs)>1)
    u=frozenset((0,1)); v=frozenset((1,2))
    fibers=[]
    for a,b in product(secs[u],secs[v]):
        if agree(a,b):
            gs=[s for s in secs[V] if restrict(s,u)==a and restrict(s,v)==b]
            fibers.append(len(gs))
    assert fibers==[2]*8
    # Same nonempty-overlap shape as left/meridian/right, not just a discrete example.
    small_topology=[frozenset(),frozenset((1,)),u,v,V]
    small_covers=small_matching=small_nonunique=0
    for target in small_topology:
        candidates=[o for o in small_topology if o<=target]
        for cover in subsets(candidates):
            if frozenset().union(*cover)!=target: continue
            small_covers+=1
            ordered=sorted(cover,key=lambda o:(len(o),tuple(sorted(o))))
            for fam in product(*(secs[o] for o in ordered)):
                if not all(agree(a,b) for a,b in combinations(fam,2)): continue
                gs=[g for g in secs[target] if all(restrict(g,o)==a for o,a in zip(ordered,fam))]
                assert gs
                small_matching+=1; small_nonunique+=int(len(gs)>1)
    # The same finite counterexample is a DIS-valued presheaf if all distances are zero.
    # This is a formal category counterexample, not a model of distinct qualia.
    # Incidence repair: opens containing relation label 3 must contain endpoints 0,2.
    incidence=[u for u in subsets((0,1,2,3)) if EDGE not in u or {0,2}<=u]
    def assections(u):
        return [dict(zip(sorted(u),b)) for b in product((0,1),repeat=len(u))]
    repaired_pairs=repaired_families=0
    for a,b in product(incidence,repeat=2):
        all_global=assections(a|b)
        repaired_pairs+=1
        for sa,sb in product(assections(a),assections(b)):
            if not agree(sa,sb): continue
            gs=[g for g in all_global if all(g[k]==v for k,v in sa.items())
                and all(g[k]==v for k,v in sb.items())]
            assert len(gs)==1
            repaired_families+=1
    return {'vertex_base_points':3,'vertex_open_sets':len(opens),'restriction_chain_instances':chains,
        'all_covers_checked_including_empty_and_redundant_covers':cover_count,
        'matching_families_all_with_amalgamations':matching,
        'matching_families_with_nonunique_amalgamations':nonunique,
        'nonempty_overlap_fixture':{'compatible_pairs':8,'amalgamations_each':2},
        'five_open_nondiscrete_topology':{'covers':small_covers,'matching_families':small_matching,
            'nonunique_matching_families':small_nonunique},
        'incidence_open_sets':len(incidence),'incidence_binary_covers':repaired_pairs,
        'incidence_matching_families_all_unique':repaired_families}


def check_relations():
    vertices=range(4); atoms=list(permutations(vertices,2))
    covers=[({0,1},{2,3}),({0,1,2},{1,2,3})]
    report=[]
    for cover in covers:
        vis=[i for i,e in enumerate(atoms) if any(set(e)<=p for p in cover)]
        hidden=[i for i in range(len(atoms)) if i not in vis]
        groups=Counter()
        for bits in product((0,1),repeat=len(atoms)):
            groups[tuple(bits[i] for i in vis)]+=1
        assert len(groups)==2**len(vis) and set(groups.values())=={2**len(hidden)}
        report.append({'patches':[sorted(p) for p in cover],'relation_atoms':len(atoms),
            'visible_atoms':len(vis),'hidden_atoms':[list(atoms[i]) for i in hidden],
            'local_data_patterns':len(groups),'completions_each':2**len(hidden)})
    # Grounded support is not inferred by this enumeration; these are graph assignments.
    cover=covers[1]; oldvis=[i for i,e in enumerate(atoms) if any(set(e)<=p for p in cover)]
    improved=defaultdict(set)
    for bits in product((0,1),repeat=12):
        key=tuple(bits[i] for i in oldvis)+(bits[atoms.index((0,3))],bits[atoms.index((3,0))])
        improved[key].add(bits)
    assert len(improved)==4096 and all(len(v)==1 for v in improved.values())
    # Relational metric: endpoint-local views forget the binding bit; augmented max separates.
    xs=list(product((0,1),repeat=3))
    metric=[[F(max(int(a!=b) for a,b in zip(x,y))) for y in xs] for x in xs]
    assert is_pseudometric(metric)
    for i,j in product(range(8),repeat=2):
        for k in (0,1):
            assert int(xs[i][k]!=xs[j][k])<=metric[i][j]
        assert (metric[i][j]==0)==(i==j)
    return {'enumerated_directed_graphs_per_cover':4096,'cover_results':report,
        'added_cross_relation_chart_unique_completions':4096,
        'binding_metric_states':8,'binding_metric_ordered_pairs':64}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    result={'schema':'uct-relational-composition-checks/v1','version':'1.0.0',
        'evidence_type':'EXACT_FINITE_MATHEMATICAL_FIXTURES_NOT_PHENOMENAL_MEASUREMENTS',
        'gluing':check_gluing(),'dissimilarity':check_distance(),'relational_completion':check_relations(),
        'assertions':'PASS'}
    text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    (args.out/'exact_results.json').write_text(text)
    print(text)

if __name__=='__main__': main()
