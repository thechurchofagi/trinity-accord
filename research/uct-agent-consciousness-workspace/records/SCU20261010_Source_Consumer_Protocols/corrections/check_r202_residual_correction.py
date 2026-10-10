from fractions import Fraction as F
from pathlib import Path
import json,hashlib
OUT=Path(__file__).parent
# The feasible dependent twin is inherited from R203-C2, not a new discovery.
cells={0:[F(19,50),F(1,50),F(21,50),F(9,50)],1:[F(9,50),F(21,50),F(1,50),F(19,50)]}
law={(h,m,j):F(1,2)*cells[h][2*m+j] for h in (0,1) for m in (0,1) for j in (0,1)}
assert all(p>=0 for p in law.values()) and sum(law.values())==1
def prob(pred):return sum(p for (h,m,j),p in law.items() if pred(h,m,j))
def cond(pred,event):return prob(lambda h,m,j:pred(h,m,j) and event(h,m,j))/prob(event)
pi=prob(lambda h,m,j:h==1);m=prob(lambda h,m,j:m==1);j=prob(lambda h,m,j:j==1);r=prob(lambda h,m,j:m==1 and j==1)
a=cond(lambda h,m,j:j==1,lambda h,m,j:h==1);c=cond(lambda h,m,j:j==1,lambda h,m,j:h==0)
q=[cond(lambda h,m,j:m==1,lambda h,m,j:h==z) for z in (0,1)]
cov=[cond(lambda h,m,j:m==1 and j==1,lambda h,m,j:h==z)-q[z]*(a if z else c) for z in (0,1)]
R=(1-pi)*cov[0]+pi*cov[1];hat=[(a*m-r)/(a-j),(r-c*m)/(j-c)];fixed=[hat[0]+R/(a-j),hat[1]-R/(j-c)]
assert q==[F(3,5),F(2,5)] and hat==[F(2,5),F(3,5)] and fixed==q and R==F(3,50)
obj={'version':'R202-RESIDUAL-CORRECTION-v0.1.0','source_claim':'R202-C2','counterexample_lineage':'R203-C2 dependent twin; inherited correction witness','joint_law':[dict(H=h,M=m,J=j,p=str(p)) for (h,m,j),p in law.items()],'quantities':{k:str(v) for k,v in dict(pi=pi,m=m,j=j,r=r,a=a,c=c,R=R).items()},'true_q0_q1':list(map(str,q)),'invalid_exact_formula_q0_q1':list(map(str,hat)),'corrected_q0_q1':list(map(str,fixed)),'residual_correction':{'pi':'(j-c)/(a-c)','q1':'(r-c*m-R)/(j-c)','q0':'(a*m-r+R)/(a-j)','R':'(1-pi)*Cov(M,J|H=0)+pi*Cov(M,J|H=1)'},'conditions':'Exact original inversion requires R=0; J independent of M given H is sufficient. Merely bounded nonzero R produces a set, not exact point ID. Same common R must be retained across both coordinates.','bounded_outer_intervals':{'q1':'[qhat1-kappa/(j-c), qhat1+kappa/(j-c)] intersect [0,1]','q0':'[qhat0-kappa/(a-j), qhat0+kappa/(a-j)] intersect [0,1]','warning':'Conservative marginal outer intervals; combine only using one common residual R and coherent binary-law feasibility; no sharp identified-set claim.'}}
p=OUT/'R202_RESIDUAL_CORRECTION.json';p.write_text(json.dumps(obj,indent=2)+'\n')
print(json.dumps({'result':'PASS','witnesses':1,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
