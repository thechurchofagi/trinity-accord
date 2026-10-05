#!/usr/bin/env python3
"""R95 tiny paired acquisition experiment. NumPy only; no model API or external actions."""
from pathlib import Path
import itertools,json,csv
import numpy as np

P=Path(__file__).resolve().parent
SEEDS=list(range(100,108))
STEPS=3000
LR=.02
H=4
X=np.array(list(itertools.product([-1.,1.],repeat=4)),dtype=float)
YA=np.stack([X[:,0],X[:,3],X[:,2],X[:,0]],axis=1)
YB=np.stack([X[:,0],X[:,3],X[:,2],X[:,1]],axis=1)

def sigm(x): return 1/(1+np.exp(-np.clip(x,-50,50)))

def init(seed):
    r=np.random.default_rng(seed)
    A=r.normal(scale=.3,size=(H,H))
    E=r.normal(scale=.3,size=(H,4)); E[:,1]=0.
    B=r.normal(scale=.3,size=(4,H)); b=np.zeros(4)
    return [A,E,B,b]

def forward(p):
    A,E,B,b=p
    h=np.zeros((len(X),H)); hs=[h]
    for t in range(4):
        h=np.tanh(h@A.T+X[:,t,None]*E[:,t][None,:]); hs.append(h)
    return h@B.T+b,hs

def loss_grad(p,Y):
    A,E,B,b=p
    h=np.zeros((len(X),H)); hs=[h]
    for t in range(4):
        h=np.tanh(h@A.T+X[:,t,None]*E[:,t][None,:]); hs.append(h)
    z=h@B.T+b; yt=(Y+1)/2
    loss=np.mean(np.maximum(z,0)-z*yt+np.log1p(np.exp(-np.abs(z))))
    dz=(sigm(z)-yt)/(len(X)*4)
    dB=dz.T@h; db=dz.sum(0); dh=dz@B
    dA=np.zeros_like(A); dE=np.zeros_like(E)
    for t in range(3,-1,-1):
        cur=hs[t+1]; q=dh*(1-cur*cur)
        dE[:,t]=(q*X[:,t,None]).sum(0)
        dA+=q.T@hs[t]
        dh=q@A
    return float(loss),[dA,dE,dB,db]

def train(seed,Y):
    p=[a.copy() for a in init(seed)]
    m=[np.zeros_like(a) for a in p]; v=[np.zeros_like(a) for a in p]
    for step in range(1,STEPS+1):
        loss,g=loss_grad(p,Y)
        for i in range(4):
            m[i]=.9*m[i]+.1*g[i]; v[i]=.999*v[i]+.001*g[i]*g[i]
            mh=m[i]/(1-.9**step); vh=v[i]/(1-.999**step)
            p[i]-=LR*mh/(np.sqrt(vh)+1e-8)
    return p

def best_single(h,y):
    best=0.
    for j in range(H):
        vals=h[:,j]; s=np.sort(vals)
        ths=[s[0]-1e-9]+[(a+b)/2 for a,b in zip(s[:-1],s[1:])]+[s[-1]+1e-9]
        for th in ths:
            for pol in (1,-1):
                pred=np.where(pol*(vals-th)>=0,1.,-1.)
                best=max(best,float(np.mean(pred==y)))
    return best

def linear_probe(h,y):
    Z=np.c_[h,np.ones(len(h))]
    w=np.linalg.lstsq(Z,y,rcond=None)[0]
    return float(np.mean(np.where(Z@w>=0,1.,-1.)==y))

def analyze(p,Y):
    z,hs=forward(p); h=hs[-1]; pred=np.where(z>=0,1.,-1.); probs=sigm(z)
    index={tuple(row):i for i,row in enumerate(X)}
    sign=np.zeros(4); tv=np.zeros(4); ds=[]
    for i,row in enumerate(X):
        rr=row.copy(); rr[1]*=-1; j=index[tuple(rr)]
        sign+=(pred[i]!=pred[j]); tv+=np.abs(probs[i]-probs[j])
        if i<j: ds.append(float(np.linalg.norm(h[i]-h[j])))
    sign/=len(X); tv/=len(X)
    q=[a.copy() for a in p]; q[1][:,1]=0.
    z0,_=forward(q); pred0=np.where(z0>=0,1.,-1.)
    l0,_=loss_grad(q,Y)
    return {
      "loss":loss_grad(p,Y)[0],
      "accuracy":float(np.mean(pred==Y)),
      "q_input_norm":float(np.linalg.norm(p[1][:,1])),
      "q_hidden_pair_min":min(ds),"q_hidden_pair_mean":float(np.mean(ds)),"q_hidden_pair_max":max(ds),
      "q_linear_probe_accuracy":linear_probe(h,X[:,1]),
      "q_best_single_unit_threshold_accuracy":best_single(h,X[:,1]),
      "q_output_sign_flip_fraction":sign.tolist(),
      "q_output_probability_tv_mean":tv.tolist(),
      "zero_q_path_accuracy":float(np.mean(pred0==Y)),
      "zero_q_path_per_output_accuracy":np.mean(pred0==Y,axis=0).tolist(),
      "zero_q_path_loss":l0
    }

out={"round":"R95","numpy":np.__version__,"seeds":SEEDS,"runs":{},"initial_q_gradient_norm":{}}
for name,Y in [("A",YA),("B",YB)]:
    out["runs"][name]=[]; out["initial_q_gradient_norm"][name]=[]
    for seed in SEEDS:
        p0=init(seed); _,g=loss_grad(p0,Y)
        out["initial_q_gradient_norm"][name].append(float(np.linalg.norm(g[1][:,1])))
        p=train(seed,Y); r=analyze(p,Y); r["seed"]=seed
        out["runs"][name].append(r)
(P/"R95_Results.regenerated.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print("R95 regenerated")
for name in ("A","B"):
    print(name,[(r["seed"],r["accuracy"],r["loss"],r["q_linear_probe_accuracy"],r["q_output_sign_flip_fraction"]) for r in out["runs"][name]])
