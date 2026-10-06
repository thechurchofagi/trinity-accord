#!/usr/bin/env python3
"""R99 bounded-domain path-certificate audit. NumPy only."""
import itertools,json,csv,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
BETA=2.;STEPS=5000;LR=.03;SEEDS=list(range(200,208))
BASE=np.array([[1,0,1],[0,1,1],[1,1,1],[-1,0,-1],[0,-1,-1],[-1,-1,-1]],float)
INT=np.array([[.5,0,0],[0,.5,0],[0,0,.5],[-.5,0,0],[0,-.5,0],[0,0,-.5]],float)
XTR=np.vstack([BASE,INT])
FAM={"task_only":np.array([0.,0.,1.]),"direct_Q":np.array([1.,0.,0.]),"mixed_Q_task":np.array([1.,0.,1.]),"successor_only":np.array([0.,1.,0.])}
GV=np.arange(-1.25,1.2500001,.125);GRID=np.array(list(itertools.product(GV,repeat=3)),float);RAD=np.sqrt(3)*.125/2
def sig(z):return 1/(1+np.exp(-np.clip(z,-50,50)))
def adam(p,grad,X,y):
 m=[np.zeros_like(x) if isinstance(x,np.ndarray) else 0. for x in p];v=[np.zeros_like(x) if isinstance(x,np.ndarray) else 0. for x in p]
 for t in range(1,STEPS+1):
  g=grad(p,X,y)
  for i in range(len(p)):
   m[i]=.9*m[i]+.1*g[i];v[i]=.999*v[i]+.001*g[i]*g[i]
   p[i]-=LR*(m[i]/(1-.9**t))/(np.sqrt(v[i]/(1-.999**t))+1e-8)
 return p
def init_g(seed):
 r=np.random.default_rng(seed);return [r.normal(scale=.3,size=(3,3)),np.zeros(3),r.normal(scale=.3,size=3),0.]
def fg(p,X):W,a,v,b=p;return np.tanh(X@W.T+a)@v+b
def gg(p,X,y):
 W,a,v,b=p;h=np.tanh(X@W.T+a);z=h@v+b;dz=(sig(z)-y)/len(X);pre=(dz[:,None]*v)*(1-h*h)
 return [pre.T@X,pre.sum(0),h.T@dz,dz.sum()]
def init_a(seed):
 r=np.random.default_rng(seed);return [r.normal(scale=.3,size=(3,2)),np.zeros((3,2)),r.normal(scale=.3,size=(3,2)),0.]
def fa(p,X):w,a,v,b=p;h=np.tanh(X[:,:,None]*w[None,:,:]+a[None,:,:]);return np.sum(h*v[None,:,:],axis=(1,2))+b
def ga(p,X,y):
 w,a,v,b=p;h=np.tanh(X[:,:,None]*w[None,:,:]+a[None,:,:]);z=np.sum(h*v[None,:,:],axis=(1,2))+b;dz=(sig(z)-y)/len(X);pre=dz[:,None,None]*v[None,:,:]*(1-h*h)
 return [np.sum(pre*X[:,:,None],0),np.sum(pre,0),np.sum(dz[:,None,None]*h,0),dz.sum()]
def ctxvar(f,p):
 out=[]
 for j in range(3):
  oi=[k for k in range(3) if k!=j];es=[]
  for uv in itertools.product(GV,repeat=2):
   xp=np.zeros(3);xm=np.zeros(3);xp[j]=.5;xm[j]=-.5;xp[oi]=uv;xm[oi]=uv
   es.append(float(f(p,xp[None,:])[0]-f(p,xm[None,:])[0]))
  out.append(max(es)-min(es))
 return out
rows=[]
for name,th in FAM.items():
 truth=BETA*(GRID@th);tp=sig(truth);Z=np.c_[XTR,np.ones(len(XTR))];sol=np.linalg.lstsq(Z,BETA*(XTR@th),rcond=None)[0];w,b=sol[:3],sol[3]
 rows.append([name,"path_linear","",np.max(abs(GRID@w+b-truth)),np.max(abs(sig(GRID@w+b)-tp)),0.,abs(b)+1.25*np.sum(abs(w-BETA*th))])
 for seed in SEEDS:
  for model,p,f,g in [("generic_mlp",init_g(seed),fg,gg),("path_additive_mlp",init_a(seed),fa,ga)]:
   p=adam(p,g,XTR,sig(BETA*(XTR@th)));z=f(p,GRID);cv=max(ctxvar(f,p))
   if model=="generic_mlp":L=np.linalg.norm(p[2])*np.linalg.norm(p[0],2)+BETA*np.linalg.norm(th)
   else:L=np.linalg.norm(np.sum(abs(p[2]*p[0]),axis=1))+BETA*np.linalg.norm(th)
   le=float(np.max(abs(z-truth)));rows.append([name,model,seed,le,float(np.max(abs(sig(z)-tp))),cv,le+L*RAD])
with (P/"R99_Regenerated_Summary.csv").open("w",newline="") as f:
 w=csv.writer(f);w.writerow(["family","model","seed","grid_max_logit_error","grid_max_prob_error","max_context_effect_variation","continuous_logit_upper"]);w.writerows(rows)
print("R99 regenerated",len(rows),"model-runs")
