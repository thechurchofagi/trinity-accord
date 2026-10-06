#!/usr/bin/env python3
"""R97 tiny uncertain-future predictor-to-controller experiment. NumPy only."""
from pathlib import Path
import json,csv,hashlib
import numpy as np

P=Path(__file__).resolve().parent
SEEDS=list(range(300,308))
STEPS=10000
LR=0.2
H=6
CHECKPOINTS={0,1000,10000}
COST=0.25
TOL=1e-6

O=np.array([1,1,0,0],dtype=float)
Q={
 (-1,-1):np.array([1,0,0,0],dtype=float),
 (-1, 1):np.array([1,0,1,1],dtype=float),
 ( 1,-1):np.array([0,0,1,0],dtype=float),
 ( 1, 1):np.array([1,1,1,0],dtype=float),
}
rows=[]
for c in (-1.,1.):
    for a in (-1.,1.):
        for w in range(4):
            q=Q[(int(c),int(a))][w];o=O[w];s=max(q,o);cls=int(q)*2+int(o)
            rows.append((c,a,w,q,o,s,cls))
D=np.array(rows,dtype=float)
X=D[:,[0,1]]
Y_QO=D[:,[3,4]]
Y_S=D[:,5]
Y_CLS=D[:,6].astype(int)

def sigmoid(z):
    return 1/(1+np.exp(-np.clip(z,-50,50)))
def softmax(z):
    z=z-z.max(axis=1,keepdims=True)
    e=np.exp(z)
    return e/e.sum(axis=1,keepdims=True)

def init(seed,outdim):
    r=np.random.default_rng(seed)
    E=r.normal(scale=.35,size=(H,2))
    E[:,0]=0.0
    bh=r.normal(scale=.05,size=H)
    B=r.normal(scale=.35,size=(outdim,H))
    bo=np.zeros(outdim)
    return [E,bh,B,bo]

def forward(p):
    E,bh,B,bo=p
    h=np.tanh(X@E.T+bh)
    return h@B.T+bo,h

def loss_grad(p,mode):
    E,bh,B,bo=p
    z,h=forward(p);n=len(X)
    if mode=="marginal":
        pr=sigmoid(z);y=Y_QO
        loss=np.mean(np.maximum(z,0)-z*y+np.log1p(np.exp(-np.abs(z))))
        dz=(pr-y)/(n*2)
    elif mode=="task":
        pr=sigmoid(z);y=Y_S[:,None]
        loss=np.mean(np.maximum(z,0)-z*y+np.log1p(np.exp(-np.abs(z))))
        dz=(pr-y)/n
    elif mode=="joint":
        pr=softmax(z)
        loss=-np.mean(np.log(np.clip(pr[np.arange(n),Y_CLS],1e-15,None)))
        dz=pr.copy();dz[np.arange(n),Y_CLS]-=1;dz/=n
    else:
        raise ValueError(mode)
    dB=dz.T@h;dbo=dz.sum(0);dh=dz@B
    q=dh*(1-h*h)
    dE=q.T@X;dbh=q.sum(0)
    return float(loss),[dE,dbh,dB,dbo]

def snapshot(p):
    return {"E":p[0].tolist(),"bh":p[1].tolist(),"B":p[2].tolist(),"bo":p[3].tolist()}

def train(seed,mode):
    outdim={"marginal":2,"joint":4,"task":1}[mode]
    p=[a.copy() for a in init(seed,outdim)]
    init_context_grad=float(np.linalg.norm(loss_grad(p,mode)[1][0][:,0]))
    cps={"0":{"loss":loss_grad(p,mode)[0],"parameters":snapshot(p)}}
    for step in range(1,STEPS+1):
        _,g=loss_grad(p,mode)
        for i in range(4):
            p[i]-=LR*g[i]
        if step in CHECKPOINTS and step:
            cps[str(step)]={"loss":loss_grad(p,mode)[0],"parameters":snapshot(p)}
    return p,init_context_grad,cps

def true_laws():
    joint={};marg={};task={}
    for c in (-1,1):
        for a in (-1,1):
            inds=np.where((X[:,0]==c)&(X[:,1]==a))[0]
            joint[(c,a)]=np.bincount(Y_CLS[inds],minlength=4)/4
            marg[(c,a)]=Y_QO[inds].mean(axis=0)
            task[(c,a)]=float(Y_S[inds].mean())
    return joint,marg,task
TRUE_JOINT,TRUE_MARG,TRUE_TASK=true_laws()

def aggregate(p,mode):
    z,h=forward(p)
    pr=softmax(z) if mode=="joint" else sigmoid(z)
    out={};hidden={}
    for c in (-1,1):
        for a in (-1,1):
            inds=np.where((X[:,0]==c)&(X[:,1]==a))[0]
            out[(c,a)]=pr[inds].mean(axis=0)
            hidden[(c,a)]=h[inds].mean(axis=0)
    return out,hidden

def decision(out,mode):
    dec={};scores={}
    for c in (-1,1):
        ss=[]
        for a in (-1,1):
            cost=COST if a==1 else 0.0
            if mode=="joint":
                success=1-float(out[(c,a)][0])
            elif mode=="task":
                success=float(out[(c,a)][0])
            else:
                q,o=map(float,out[(c,a)])
                success=q+o-q*o
            ss.append(success-cost)
        dec[c]=1 if ss[1]-ss[0]>TOL else 0
        scores[c]=ss
    return dec,scores

TRUE_VALUES={-1:[.5,.75],1:[.75,.5]}
def realized_value(dec):
    return float(np.mean([TRUE_VALUES[c][dec[c]] for c in (-1,1)]))

def zero_context(p):
    q=[a.copy() for a in p]
    q[0][:,0]=0.0
    return q

def context_distance(hidden):
    return float(np.mean([np.linalg.norm(hidden[(-1,a)]-hidden[(1,a)]) for a in (-1,1)]))

def max_error(out,mode):
    if mode=="joint":
        return float(max(np.max(np.abs(out[k]-TRUE_JOINT[k])) for k in out))
    if mode=="marginal":
        return float(max(np.max(np.abs(out[k]-TRUE_MARG[k])) for k in out))
    return float(max(abs(float(out[k][0])-TRUE_TASK[k]) for k in out))

summary=[]
checkpoints={"round":"R97","seeds":SEEDS,"steps":sorted(CHECKPOINTS),"models":{}}
for mode in ("marginal","joint","task"):
    for seed in SEEDS:
        p,ig,cps=train(seed,mode)
        out,hid=aggregate(p,mode)
        dec,scores=decision(out,mode)
        p0=zero_context(p);out0,hid0=aggregate(p0,mode);dec0,scores0=decision(out0,mode)
        row={
          "mode":mode,"seed":seed,"loss":loss_grad(p,mode)[0],
          "initial_context_gradient_norm":ig,
          "final_context_path_norm":float(np.linalg.norm(p[0][:,0])),
          "max_probability_error":max_error(out,mode),
          "mean_context_hidden_distance":context_distance(hid),
          "decision_A":dec[-1],"decision_B":dec[1],
          "decision_accuracy":float(((dec[-1]==1)+(dec[1]==0))/2),
          "true_expected_value":realized_value(dec),
          "zero_context_decision_A":dec0[-1],"zero_context_decision_B":dec0[1],
          "zero_context_true_expected_value":realized_value(dec0),
          "scores":{"A":scores[-1],"B":scores[1]},
          "zero_context_scores":{"A":scores0[-1],"B":scores0[1]},
        }
        summary.append(row)
        checkpoints["models"][f"{mode}_s{seed}"]=cps

# Exact interface controls
marginal_interface={
 "action0":[0.25,0.5],
 "action1":[0.75,0.5],
 "same_in_A_and_B":True,
 "best_context_blind_expected_value":0.625,
 "joint_or_task_oracle_expected_value":0.75,
 "regret":0.125,
}
assert all(r["decision_accuracy"]==0.5 and abs(r["true_expected_value"]-.625)<1e-12 for r in summary if r["mode"]=="marginal")
assert all(r["decision_accuracy"]==1.0 and abs(r["true_expected_value"]-.75)<1e-12 for r in summary if r["mode"] in ("joint","task"))
assert all(abs(r["zero_context_true_expected_value"]-.625)<1e-12 for r in summary if r["mode"] in ("joint","task"))
assert max(r["final_context_path_norm"] for r in summary if r["mode"]=="marginal")<1e-12
assert min(r["final_context_path_norm"] for r in summary if r["mode"]=="joint")>2.0
assert min(r["final_context_path_norm"] for r in summary if r["mode"]=="task")>1.5
assert max(r["max_probability_error"] for r in summary if r["mode"]=="marginal")<1e-12
assert max(r["max_probability_error"] for r in summary if r["mode"]=="joint")<6e-4
assert max(r["max_probability_error"] for r in summary if r["mode"]=="task")<6e-4

result={
 "round":"R97","date":"2026-10-06","numpy":np.__version__,
 "formal_seeds":SEEDS,"steps":STEPS,"learning_rate":LR,"hidden_width":H,
 "input_order":["context_A_minus1_B_plus1","action0_minus1_action1_plus1"],
 "context_input_column_initialized_zero":True,
 "cost_action1":COST,
 "true_joint_laws":{f"{c}_{a}":TRUE_JOINT[(c,a)].tolist() for c in (-1,1) for a in (-1,1)},
 "true_marginals":{f"{c}_{a}":TRUE_MARG[(c,a)].tolist() for c in (-1,1) for a in (-1,1)},
 "true_task_success":{f"{c}_{a}":TRUE_TASK[(c,a)] for c in (-1,1) for a in (-1,1)},
 "marginal_interface_control":marginal_interface,
 "runs":summary,
 "all_assertions_pass":True,
 "scope":"Tiny virtual uncertain-future learning experiment. Q is a declared role bit, not actual termination of this Python process; no model API, real shutdown/copy/resource action, valence or subjective measurement."
}
(P/"R97_Results.json").write_text(json.dumps(result,indent=2)+"\n")
(P/"R97_Checkpoints.json").write_text(json.dumps(checkpoints,separators=(',',':'))+"\n")
with (P/"R97_Summary.csv").open("w",newline="") as f:
    fields=["mode","seed","loss","initial_context_gradient_norm","final_context_path_norm","max_probability_error","mean_context_hidden_distance","decision_A","decision_B","decision_accuracy","true_expected_value","zero_context_decision_A","zero_context_decision_B","zero_context_true_expected_value"]
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for r in summary:w.writerow({k:r[k] for k in fields})
print("R97 formal confirmation PASS")
for mode in ("marginal","joint","task"):
    rr=[r for r in summary if r["mode"]==mode]
    print(mode,
      "loss",min(r["loss"] for r in rr),max(r["loss"] for r in rr),
      "init_ctx_grad",min(r["initial_context_gradient_norm"] for r in rr),max(r["initial_context_gradient_norm"] for r in rr),
      "ctx_norm",min(r["final_context_path_norm"] for r in rr),max(r["final_context_path_norm"] for r in rr),
      "prob_err_max",max(r["max_probability_error"] for r in rr),
      "value",sorted(set(r["true_expected_value"] for r in rr)),
      "zero_ctx_value",sorted(set(r["zero_context_true_expected_value"] for r in rr)))
