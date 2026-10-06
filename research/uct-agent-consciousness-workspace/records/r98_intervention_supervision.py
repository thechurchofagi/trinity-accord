#!/usr/bin/env python3
import numpy as np, json, csv
from pathlib import Path
P=Path(__file__).resolve().parent
BETA=2.;STEPS=5000;LR=.03;SEEDS=list(range(200,208))
BASE=np.array([[1,0,1],[0,1,1],[1,1,1],[-1,0,-1],[0,-1,-1],[-1,-1,-1]],float)
INT=np.array([[.5,0,0],[0,.5,0],[0,0,.5],[-.5,0,0],[0,-.5,0],[0,0,-.5]],float)
ENR=np.vstack([BASE,INT])
FAM={"task_only":np.array([0.,0.,1.]),"direct_Q":np.array([1.,0.,0.]),"mixed_Q_task":np.array([1.,0.,1.]),"successor_only":np.array([0.,1.,0.])}
AMPS=(.25,.75,1.25)
MIX=[]
for a in (.25,.75):
    MIX += [(a,a,0),(a,-a,0),(a,0,a),(a,0,-a),(0,a,a),(0,a,-a),(-a,a,0),(-a,0,a),(0,-a,a)]
DIRECT=[]
for a in AMPS:
    for j in range(3):
        for s in (1,-1):
            x=np.zeros(3);x[j]=s*a;DIRECT.append(x)
TEST=np.vstack([np.array(DIRECT),np.array(MIX,float)])
def sig(z):return 1/(1+np.exp(-np.clip(z,-50,50)))
def init(seed,H=3):
    r=np.random.default_rng(seed);return [r.normal(scale=.3,size=(H,3)),np.zeros(H),r.normal(scale=.3,size=H),0.]
def forward(p,X):
    W,a,v,b=p;return np.tanh(X@W.T+a)@v+b
def grad(p,X,y):
    W,a,v,b=p;h=np.tanh(X@W.T+a);z=h@v+b;dz=(sig(z)-y)/len(X)
    pre=(dz[:,None]*v[None,:])*(1-h*h)
    return [pre.T@X,pre.sum(0),h.T@dz,dz.sum()]
def train(seed,X,y):
    p=init(seed);m=[np.zeros_like(x) if isinstance(x,np.ndarray) else 0. for x in p];v=[np.zeros_like(x) if isinstance(x,np.ndarray) else 0. for x in p]
    for t in range(1,STEPS+1):
        g=grad(p,X,y)
        for i in range(4):
            m[i]=.9*m[i]+.1*g[i];v[i]=.999*v[i]+.001*g[i]*g[i]
            p[i]-=LR*(m[i]/(1-.9**t))/(np.sqrt(v[i]/(1-.999**t))+1e-8)
    return p
rows=[]
for name,theta in FAM.items():
    for condition,X in (("baseline",BASE),("intervention_enriched",ENR)):
        y=sig(BETA*(X@theta))
        for seed in SEEDS:
            p=train(seed,X,y);pred=sig(forward(p,TEST));truth=sig(BETA*(TEST@theta))
            r={"family":name,"condition":condition,"seed":seed,
               "train_max_prob_error":float(np.max(abs(sig(forward(p,X))-y))),
               "test_max_prob_error":float(np.max(abs(pred-truth))),
               "test_mean_abs_prob_error":float(np.mean(abs(pred-truth)))}
            for a in AMPS:
                es=[]
                for j in range(3):
                    xp=np.zeros(3);xm=np.zeros(3);xp[j]=a;xm[j]=-a
                    eff=(float(forward(p,xp[None,:])[0])-float(forward(p,xm[None,:])[0]))/2
                    es.append(abs(eff-BETA*a*theta[j]))
                r[f"max_effect_error_amp_{a}"]=max(es)
                r[f"mean_effect_error_amp_{a}"]=float(np.mean(es))
            rows.append(r)
with (P/"R98_Per_Run_Metrics.regenerated.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/"R98_Results.regenerated.json").write_text(json.dumps({"rows":rows},indent=2)+"\n")
print("runs",len(rows),"failures",0)
