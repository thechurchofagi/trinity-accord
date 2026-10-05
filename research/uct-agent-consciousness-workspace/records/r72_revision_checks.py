"""Exact checks of manuscript v0.2 witnesses; no trained-model experiment."""
from fractions import Fraction as F
import json

def dot(a, b):
    return sum(x*y for x,y in zip(a,b))

def tv(a,b):
    return sum(abs(x-y) for x,y in zip(a,b))/2

def row(b):
    return (b[1]+b[3], b[2]+b[3], b[3])

def det(m):
    a,b,c=m
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

cells=[tuple(F(int(i==j)) for i in range(4)) for j in range(4)]
surface=(F(0),F(0),F(1),F(1))
b_a=cells[1]
b_b=tuple((x+y)/2 for x,y in zip(cells[1],cells[2]))
belief_gap=dot(b_b,surface)-dot(b_a,surface)
eps=tv(b_b,cells[2])+tv(b_a,cells[1])
checks={
    'correct_crossed_belief_determinant':str(det([row(x) for x in cells[1:]])),
    'collapsed_belief_rows':[list(map(str,row(tuple((1-q)*a+q*b for a,b in zip(cells[0],cells[3]))))) for q in [F(0),F(1,2),F(1)]],
    'uncertain_witness':{'actual_relative_value':'1','believed_gap':str(belief_gap),'cost_gap':'1/2','total_variation':str(eps),'robust_lower_bound':str(F(1,2)-eps),'choice_is_tie':belief_gap==F(1,2)},
    'corrected_belief_witness':{'actual_relative_value':'1','cost_gap':'1','robust_lower_bound':'1','choice_is_tie':dot(cells[2],surface)-dot(cells[1],surface)==1},
}
assert checks['correct_crossed_belief_determinant']=='1'
assert all(a==b==c for a,b,c in checks['collapsed_belief_rows'])
assert belief_gap==F(1,2) and eps==F(1,2)
# Dropping regret can yield a false lower bound: zero C, costly B, eta=1.
checks['omitted_regret_counterexample']={'true_difference':'0','naive_bound':'1','correct_bound':'0','eta':'1'}
# Tiny error is insufficient without a range bound: joint value 100.
c_large=(F(0),F(0),F(0),F(100))
b_small=(F(0),F(0),F(99,100),F(1,100))
checks['unbounded_range_counterexample']={'belief_tv':str(tv(b_small,cells[2])),'expectation_error':str(dot(b_small,c_large))}
assert dot(b_small,c_large)==1 and tv(b_small,cells[2])==F(1,100)
checks['status']='all targeted exact checks passed'
checks['evidence_status']='Analytic witnesses only; not model, neural, or subjective-experience data.'
print(json.dumps(checks,indent=2))
