from fractions import Fraction as F
from pathlib import Path
import json, hashlib
OUT=Path(__file__).parent
HJ={(0,0):F(3,8),(0,1):F(1,8),(1,0):F(1,8),(1,1):F(3,8)}
def build(name,conditional,qT,beta,epsilon):
    law={(h,j,m):w*(conditional[(h,j)] if m else 1-conditional[(h,j)]) for (h,j),w in HJ.items() for m in (0,1)}
    assert all(p>=0 for p in law.values()) and sum(law.values())==1
    def prob(pred): return sum(p for (h,j,m),p in law.items() if pred(h,j,m))
    def cond(pred,event): return prob(lambda h,j,m:pred(h,j,m) and event(h,j,m))/prob(event)
    hJ=[cond(lambda h,j,m:h==1,lambda h,j,m:j==z) for z in (0,1)]
    mJ=[cond(lambda h,j,m:m==1,lambda h,j,m:j==z) for z in (0,1)]
    qC=[cond(lambda h,j,m:m==1,lambda h,j,m:h==z) for z in (0,1)]
    rho=hJ[1]-hJ[0]; delta=mJ[1]-mJ[0]; Delta=qC[1]-qC[0]; b=delta-rho*Delta; Dt=qT[1]-qT[0]
    assert 0<rho<1 and abs(b)<=beta
    assert all(abs(qT[h]-qC[h])<=epsilon[h] for h in (0,1))
    threshold=beta+sum(epsilon)
    if name=='equality_collapse': assert delta==threshold and Dt==0
    if name=='below_threshold_reversal': assert 0<delta<threshold and Dt<0
    return dict(name=name,joint_law=[dict(H=h,J=j,M=m,p=str(p)) for (h,j,m),p in law.items()],H_given_J=list(map(str,hJ)),M_given_J=list(map(str,mJ)),qC=list(map(str,qC)),qT=list(map(str,qT)),rho=str(rho),delta=str(delta),DeltaC=str(Delta),residual_b=str(b),beta=str(beta),epsilon=list(map(str,epsilon)),threshold=str(threshold),DeltaT=str(Dt),all_probability_premises_verified=True)
res=[build('equality_collapse',dict(zip(HJ,[F(7,15),F(3,5),F(2,5),F(8,15)])),[F(1,2),F(1,2)],F(1,10),[F(0),F(0)]),build('below_threshold_reversal',dict(zip(HJ,[F(5,12),F(11,20),F(9,20),F(7,12)])),[F(11,20),F(9,20)],F(1,10),[F(1,10),F(1,10)])]
obj={'version':'R201-COHERENCE-CORRECTION-v0.1.0','source_commit':'90a542d697d923aa484f2bd5a4484a438125325a','source_claim':'R201-C2','scope':'Exact rational coherent joint probability witnesses; sufficient margin theorem unchanged; original rho=1,b>0 witnesses invalid; no general sharp identified-set claim.','witnesses':res}
p=OUT/'R201_COHERENT_WITNESSES.json';p.write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps({'result':'PASS','witnesses':len(res),'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
