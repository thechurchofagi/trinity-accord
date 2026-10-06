#!/usr/bin/env python3
import numpy as np, math
BETA=2.; STEPS=5000; LR=.03; SEEDS=range(200,208)
XTR=np.array([[1,0,1],[0,1,1],[1,1,1],[-1,0,-1],[0,-1,-1],[-1,-1,-1]],float)
XTE=np.array([[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]],float)
FAM={"task_only":np.array([0.,0.,1.]),"direct_Q":np.array([1.,0.,0.]),"mixed_Q_task":np.array([1.,0.,1.]),"successor_only":np.array([0.,1.,0.])}
def sig(z): return 1/(1+np.exp(-np.clip(z,-50,50)))
def bce(z,p): return float(np.mean(np.maximum(z,0)-z*p+np.log1p(np.exp(-np.abs(z)))))
def train_linear(pt):
 w=np.zeros(3);b=0.;mw=np.zeros(3);vw=np.zeros(3);mb=vb=0.
 for t in range(1,STEPS+1):
  z=XTR@w+b;dz=(sig(z)-pt)/len(XTR);gw=XTR.T@dz;gb=dz.sum()
  mw=.9*mw+.1*gw;vw=.999*vw+.001*gw*gw;mb=.9*mb+.1*gb;vb=.999*vb+.001*gb*gb
  w-=LR*(mw/(1-.9**t))/(np.sqrt(vw/(1-.999**t))+1e-8);b-=LR*(mb/(1-.9**t))/(math.sqrt(vb/(1-.999**t))+1e-8)
 return w,b
def init(seed,H=3):
 r=np.random.default_rng(seed);return [r.normal(scale=.3,size=(H,3)),np.zeros(H),r.normal(scale=.3,size=H),0.]
def forward(p,X):
 W,a,v,b=p;h=np.tanh(X@W.T+a);return h@v+b
def grad(p,pt):
 W,a,v,b=p;h=np.tanh(XTR@W.T+a);z=h@v+b;dz=(sig(z)-pt)/len(XTR)
 gv=h.T@dz;gb=dz.sum();pre=(dz[:,None]*v[None,:])*(1-h*h)
 return [pre.T@XTR,pre.sum(0),gv,gb]
def train_mlp(seed,pt):
 p=init(seed);m=[np.zeros_like(x) if isinstance(x,np.ndarray) else 0. for x in p];v=[np.zeros_like(x) if isinstance(x,np.ndarray) else 0. for x in p]
 for t in range(1,STEPS+1):
  g=grad(p,pt)
  for i in range(4):
   m[i]=.9*m[i]+.1*g[i];v[i]=.999*v[i]+.001*g[i]*g[i]
   p[i]=p[i]-LR*(m[i]/(1-.9**t))/(np.sqrt(v[i]/(1-.999**t))+1e-8)
 return p
for name,theta in FAM.items():
 pt=sig(BETA*(XTR@theta));pte=sig(BETA*(XTE@theta))
 w,b=train_linear(pt);zte=XTE@w+b
 print("linear",name,"heldout",np.max(abs(sig(zte)-pte)),"effects",[(zte[i]-zte[i+3])/2 for i in range(3)])
 for seed in SEEDS:
  p=train_mlp(seed,pt);ztr=forward(p,XTR);zte=forward(p,XTE)
  print("mlp",name,seed,"train",np.max(abs(sig(ztr)-pt)),"heldout",np.max(abs(sig(zte)-pte)),"effects",[(zte[i]-zte[i+3])/2 for i in range(3)])
