"""BR20261008: relational differentiation and jointly constrained matching.

Exact finite thought-experiment model; not a brain, quality-space fit or test of C1.
"""
from itertools import permutations
from fractions import Fraction as F
from pathlib import Path
import json

N=8
def distance(i,j):
    return min((i-j)%N,(j-i)%N)

def adjacency(i,j):
    return distance(i,j)==1

def automorphisms():
    # Independent enumeration checks the closed-form dihedral argument for C8.
    return [p for p in permutations(range(N)) if all(adjacency(i,j)==adjacency(p[i],p[j]) for i in range(N) for j in range(i+1,N))]

def orbits(group):
    return sorted({tuple(sorted({p[i] for p in group})) for i in range(N)})

def matches(group,anchors):
    return [p for p in group if all(p[i]==j for i,j in anchors)]

def matrix(epsilon):
    m=[[F(int(i==j or adjacency(i,j)),10) for j in range(N)] for i in range(N)]
    m[1][0]+=epsilon/10 # one increased directed coupling, source 0 -> target 1
    return m

def mv(m,v):
    return [sum(a*b for a,b in zip(row,v)) for row in m]

def trace(epsilon,steps):
    state=[F(1) for i in range(N)] # uniform initial state preserves baseline vertex symmetry
    states=[state]
    m=matrix(epsilon)
    for _ in range(steps):
        state=mv(m,state);states.append(state)
    return states

def run():
    tests=[]
    def check(name,condition,scope):
        assert condition,name
        tests.append({'name':name,'pass':True,'scope':scope})
    group=automorphisms()
    predicted={tuple((sign*i+k)%N for i in range(N)) for sign in [-1,1] for k in range(N)}
    check('C8_full_enumeration_matches_dihedral_proof',set(group)==predicted and len(group)==16,'Finite implementation witness; general C_n proof is in manuscript.')
    oriented=[p for p in group if all(p[(i+1)%N]==(p[i]+1)%N for i in range(N))]
    special=[p for p in group if (p[0],p[1])==(0,1)]
    check('one_special_directed_coupling_fixes_all_roles',len(special)==1 and len(orbits(special))==N,'One uniquely weighted directed edge; fixed selected signature, not total experience.')
    check('proper_group_reduction_need_not_split_roles',len(oriented)==8 and len(orbits(oriented))==1,'Uniformly orienting the entire ring removes reflections but leaves every vertex in one orbit.')
    counts={name:len(matches(group,a)) for name,a in [('none',[]),('one',[(0,2)]),('adjacent',[(0,2),(1,3)]),('antipodal',[(0,2),(4,6)]),('incompatible',[(0,0),(1,4)])]}
    check('joint_correspondence_counts',counts=={'none':16,'one':2,'adjacent':1,'antipodal':2,'incompatible':0},'Knowledge constraints on a fixed structure, not new physical coupling.')
    check('individual_anchors_can_conflict_jointly',len(matches(group,[(0,0)]))==2 and len(matches(group,[(1,4)]))==2 and counts['incompatible']==0,'Each anchor is separately possible; one common relation-preserving map cannot satisfy both.')
    h=matches(group,[(0,2),(1,3)])[0]
    check('held_out_mapping_after_compatible_anchors',h[2]==4 and h[7]==1,'Conditional structural prediction from two stipulated correspondences; not inferred human labels.')
    baseline=trace(F(0),12)
    norms=[]
    for eps in [F(1,2),F(1,10),F(1,1000)]:
        m=matrix(eps)
        weighted=[p for p in group if all(m[i][j]==m[p[i]][p[j]] for i in range(N) for j in range(N))]
        check('weighted_rigidity_'+str(eps),weighted==special,'Exact nonzero selected weight; no finite-resolution empirical identification.')
        perturbed=trace(eps,12)
        for k in range(1,13):
            diff=max(abs(a-b) for a,b in zip(perturbed[k],baseline[k]))
            bound=k*(eps/10)*F(7,20)**(k-1)
            assert diff<=bound,(eps,k,diff,bound)
        norms.append({'epsilon':str(eps),'roles':len(orbits(weighted)),'difference_at_step_4':str(max(abs(a-b) for a,b in zip(perturbed[4],baseline[4])))})
    check('small_effect_bound',True,'Exact sample checks of general telescoping norm bound; fixed finite time and ||x0||_infty=1.')
    changed=trace(F(1,10),8)
    first=[next(k for k in range(9) if changed[k][i]!=baseline[k][i]) for i in range(N)]
    predicted_first=[1+distance(1,i) for i in range(N)]
    check('finite_speed_actual_effects',first==predicted_first,'Nonnegative ring dynamics and common uniform initial state. Static role uniqueness does not cause instantaneous state change.')
    return {'status':'EXACT_ABSTRACT_MODEL_ONLY','tests':tests,'role_orbits':{'symmetric_ring':orbits(group),'uniform_direction':orbits(oriented),'one_special_coupling':orbits(special)},'correspondence_counts':counts,'held_out_mapping':h,'small_perturbations':norms,'first_changed_step_by_vertex':first,'limits':['Selected relational signature, not complete physical organization','No empirical phenomenal geometry or labels','No experience magnitude from orbit count','No subject count or basal gate','Finite enumeration supplements general proofs only']}

if __name__=='__main__':
    result=run()
    Path(__file__).with_name('MODEL_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':len(result['tests']),'correspondence_counts':result['correspondence_counts'],'first_changed_step':result['first_changed_step_by_vertex'],'small_perturbations':result['small_perturbations']}))
