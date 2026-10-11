#!/usr/bin/env python3
"""PR-v4.0.0. Exact finite evidence/backup frontiers; no AI or human data.

Three independent views are compared: covering by action columns, partitioning
history rows, and coloring all minimal incompatible history sets. The optimizer
is exact for the enumerated finite menu, not a scalable general synthesis tool.
"""
from __future__ import annotations
import argparse,itertools,json,math,platform,time
from functools import lru_cache
from pathlib import Path


def partitions(n:int):
    """Each set partition once, represented by bit-mask blocks."""
    if n==0: return [()]
    out=[]
    for old in partitions(n-1):
        b=1<<(n-1)
        out.append(old+(b,))
        for i in range(len(old)):out.append(old[:i]+(old[i]|b,)+old[i+1:])
    return out


def common(rows:tuple[int,...], cell:int, nplans:int)->int:
    out=(1<<nplans)-1
    for h,row in enumerate(rows):
        if cell>>h&1:out &= row
    return out


def minimum_cover(nworlds:int,covers:tuple[int,...]):
    if nworlds < 1: raise ValueError("The declared world set must be nonempty")
    target=(1<<nworlds)-1
    if any(c < 0 or c > target for c in covers): raise ValueError("Plan covers contain invalid world bits")
    if not covers or union(covers)!=target:return math.inf,()
    @lru_cache(None)
    def solve(todo):
        if not todo:return ()
        h=(todo&-todo).bit_length()-1
        candidates=[]
        for j,c in enumerate(covers):
            if c>>h&1:candidates.append((j,)+solve(todo&~c))
        return min(candidates,key=lambda p:(len(p),p))
    plan=solve(target)
    return len(plan),plan


def union(xs):
    out=0
    for x in xs:out|=x
    return out


def relation_checks():
    count=0;partition_checks=0;pairwise_blind=0;distribution={};first_counter=None
    for n,m in ((3,4),(4,3)):
        parts=partitions(n)
        for rows in itertools.product(range(1,1<<m),repeat=n):
            covers=tuple(sum(1<<h for h,r in enumerate(rows) if r>>p&1) for p in range(m))
            best,_=minimum_cover(n,covers)
            intersections={B:common(rows,B,m) for B in range(1,1<<n)}
            forbidden=tuple(B for B,v in intersections.items() if not v and
                all(intersections[B&~(1<<h)] for h in range(n) if B>>h&1 and B!=(1<<h)))
            best_partition=n+1;best_coloring=n+1
            for part in parts:
                direct=all(intersections[B] for B in part)
                colored=all(not any((E&B)==E for E in forbidden) for B in part)
                assert bool(direct)==colored
                if direct:best_partition=min(best_partition,len(part))
                if colored:best_coloring=min(best_coloring,len(part))
                partition_checks+=1
            assert best==best_partition==best_coloring
            pairs_pass=all(intersections[(1<<i)|(1<<j)] for i in range(n) for j in range(i+1,n))
            if pairs_pass and not intersections[(1<<n)-1]:
                pairwise_blind+=1
                if first_counter is None:first_counter={'n':n,'m':m,'rows':rows,'minimal_bad_cells':forbidden,'messages':best}
            count+=1;distribution[str(best)]=distribution.get(str(best),0)+1
    # An irreducible failure at the sensor, not at the communication link.
    rows=(0b01,0b10);coarse=0b11
    assert common(rows,coarse,2)==0
    # Relabeling/repeating plan or history records cannot add a capability.
    rows=(0b011,0b110,0b101)
    covers=tuple(sum(1<<h for h,row in enumerate(rows) if row>>p&1) for p in range(3))
    before=minimum_cover(3,covers)[0]
    after=minimum_cover(3,covers+covers*4)[0]
    assert before==after==2
    return {'tables':count,'partition_equivalence_checks':partition_checks,
            'message_count_distribution':distribution,'pairwise_checks_miss_global_failure_tables':pairwise_blind,
            'first_pairwise_counterexample':first_counter,'duplicate_action_columns_preserve_optimum':True,
            'unresolvable_sensor_cell_control':True}


def fault_relation(n:int,k:int,r:int):
    if not (1 <= k <= n and 0 <= r <= n): raise ValueError("Require 1 <= k <= n and 0 <= r <= n")
    worlds=tuple(itertools.combinations(range(n),k))
    plans=tuple(itertools.combinations(range(n),r))
    covers=tuple(sum(1<<h for h,F in enumerate(worlds) if set(F)<=set(A)) for A in plans)
    return worlds,plans,covers


def fault_checks():
    cases=[]
    # Single dependency uncertainty: exact pigeonhole frontier, independent cover DP.
    for n in range(2,10):
        for r in range(1,n+1):
            worlds,plans,covers=fault_relation(n,1,r)
            M,witness=minimum_cover(n,covers)
            assert M==math.ceil(n/r)
            cases.append({'n':n,'r':r,'M_star':M,'bits':math.ceil(math.log2(M)),
                          'codebook':[plans[j] for j in witness]})
    multi=[]
    for n in range(3,7):
        for r in range(2,n+1):
            worlds,plans,covers=fault_relation(n,2,r)
            M,w=minimum_cover(len(worlds),covers)
            assert union(covers[j] for j in w)==(1<<len(worlds))-1
            multi.append({'n':n,'k':2,'r':r,'M_star':M,'codebook':[plans[j] for j in w],
                          'simple_counting_lower_bound':math.ceil(math.comb(n,2)/math.comb(r,2))})
    w,p,c=fault_relation(6,2,3)
    M,witness=minimum_cover(len(w),c)
    assert M==6
    # Independent exhaustive exclusion of every <=5-block codebook.
    excluded=0
    for size in range(6):
        for sub in itertools.combinations(range(len(p)),size):
            assert union(c[j] for j in sub)!=(1<<len(w))-1
            excluded+=1
    # All pairs of 3 worlds work with two slots, the triple does not.
    rows=(0b011,0b101,0b110)
    assert all(common(rows,(1<<i)|(1<<j),3) for i in range(3) for j in range(i+1,3))
    assert common(rows,0b111,3)==0
    # A coarse sensor and its derived reports cannot reveal any finer cell.
    # The restricted-sensor frontier is maximum cell size in this single-fault family.
    for n in range(2,8):
        for part in partitions(n):
            needed=max(B.bit_count() for B in part)
            for r in range(1,n+1):
                feasible=all(B.bit_count()<=r for B in part)
                assert feasible==(r>=needed)
    return {'single_fault_cases':cases,'two_fault_covering_cases':multi,
            'C_6_3_2':{'value':6,'failing_codebooks_with_at_most_five_blocks':excluded,
                       'six_block_witness':[p[j] for j in witness]},
            'pairwise_counterexample':{'worlds':3,'backup_capacity':2,'all_pairs':True,'all_three':False}}


def delay_checks():
    # Prefix deadline: b reliable bits/round, l rounds before irrevocable commit.
    checks=0;rows=[]
    for n,r,b,l in itertools.product(range(2,10),range(1,10),range(0,4),range(0,4)):
        if r>n:continue
        M=1<<(b*l);feasible=M*r>=n
        direct=math.ceil(n/M)<=r
        assert feasible==direct
        checks+=1
        if n==8 and r==2 and b==1:rows.append({'n':n,'r':r,'bits_per_round':b,'available_rounds':l,'possible':feasible})
    return {'cases':checks,'n8_r2_one_bit_per_round':rows,
            'interpretation':'Fixed noiseless transcript alphabet and no precommit service gap; no claim about continuous-time energy.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='frontier_v4.json');a=ap.parse_args()
    t=time.monotonic()
    result={'version':'PR-v4.0.0','scope':'Exact finite constructed relations and dependency isolation; no model evaluation',
            'general_relation':relation_checks(),'dependency_frontier':fault_checks(),'deadline_channel':delay_checks(),
            'python':platform.python_version(),'elapsed_seconds':round(time.monotonic()-t,6),'assertions':'PASS'}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['version','general_relation','deadline_channel','elapsed_seconds','assertions']},indent=2))
    print('C(6,3,2)',result['dependency_frontier']['C_6_3_2'])

if __name__=='__main__':main()
