"""Exact checks of a stipulated two-register organization, not phenomenal data."""
from fractions import Fraction as F
import json
from pathlib import Path

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mv(A,x): return tuple(sum((a*b for a,b in zip(row,x)),F(0)) for row in A)
def mm(A,B): return tuple(tuple(sum((A[i][k]*B[k][j] for k in range(2)),F(0)) for j in range(2)) for i in range(2))
def mode(x): return (x[0]+x[1],x[0]-x[1])
def physical(z): return ((z[0]+z[1])/2,(z[0]-z[1])/2)
def reset_x(x,c): return (c,x[1])
def transported_reset(z,c): return (c+(z[0]-z[1])/2,c-(z[0]-z[1])/2)

A=((F(1,2),F(1,4)),(F(1,4),F(1,2)))
D=((F(3,4),F(0)),(F(0),F(1,4)))
S=((F(1),F(1)),(F(1),F(-1)))
checks={}
checks['dynamics_conjugacy']=mm(S,A)==mm(D,S)
rows=[]
for x in [(F(0),F(0)),(F(1),F(0)),(F(0),F(1)),(F(2),F(-1))]:
 for c in [F(0),F(1)]:
  lhs=mode(reset_x(x,c)); rhs=transported_reset(mode(x),c)
  rows.append({'state':x,'reset':c,'transported_result':rhs,'equal':lhs==rhs})
checks['reset_transport']=all(r['equal'] for r in rows)
checks['mixed_reset_not_local']=transported_reset((F(3),F(1)),F(0))!=(F(0),F(1))
base=(F(0),F(0)); dx=(F(1),F(0)); dy=(F(0),F(1))
effects={'coupled_x_to_y':mv(A,dx)[1],'coupled_y_to_x':mv(A,dy)[0],
         'separate_x_to_y':mv(D,dx)[1],'separate_y_to_x':mv(D,dy)[0]}
checks['physical_cross_effects']=effects=={'coupled_x_to_y':F(1,4),'coupled_y_to_x':F(1,4),'separate_x_to_y':F(0),'separate_y_to_x':F(0)}
checks['same_eigenvalue_invariants']=sum((A[i][i] for i in range(2)),F(0))==sum((D[i][i] for i in range(2)),F(0)) and A[0][0]*A[1][1]-A[0][1]*A[1][0]==D[0][0]*D[1][1]
checks['matched_zero_trajectory']=mv(A,base)==mv(D,base)==base
out={'status':'formal checks only; no trained model or subjective data','checks':checks,
 'matrices':{'coupled':A,'independent_physical_registers':D,'coordinate_map':S},
 'reset_cases':rows,'physical_cross_effects':effects,
 'failed_inferences':['Diagonal update alone proves physical independence.',
 'Equal state dimension and spectrum identify constituent organization.',
 'Cross-part coupling proves a unified subject or a scalar increase in experience.'],
 'interpretation':'First two failed inferences have explicit counterexamples; the third is not entailed by this construction or C1.'}
Path('R77_Organization_Ports_Results.json').write_text(json.dumps(out,default=str,ensure_ascii=False,indent=2)+'\n')
assert all(checks.values()), checks
print(json.dumps({'checks':checks,'cross_effects':effects},default=str))
