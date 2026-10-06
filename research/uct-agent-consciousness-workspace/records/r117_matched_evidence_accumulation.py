#!/usr/bin/env python3
"""R117 matched sequential-evidence artificial experiment.

Transparent support-relation experiment; not a consciousness model.
"""
import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, r2_score

SEED=117
N=60000
T=10
rng=np.random.default_rng(SEED)

side=rng.choice([-1,1],size=N)
strength=rng.choice([0.15,0.30,0.45,0.60],size=N)
base=3.0

lam_r=base*(1+strength*side)[:,None]
lam_l=base*(1-strength*side)[:,None]
R=rng.poisson(lam_r,size=(N,T))
L=rng.poisson(lam_l,size=(N,T))
E=R-L
tot=E.sum(axis=1)

mask=tot!=0
E=E[mask]
tot=tot[mask]
target=(tot>0).astype(int)
cum=np.cumsum(E,axis=1)
n=len(target)

def fit_kernel(choice):
    X=(E-E.mean(0))/E.std(0)
    mdl=LogisticRegression(C=1e6,solver="lbfgs",max_iter=1000)
    mdl.fit(X,choice)
    return mdl.coef_[0]

choice=(cum[:,-1]+rng.normal(0,3.0,size=n)>0).astype(int)
choice_last=(E[:,-1]+rng.normal(0,3.0,size=n)>0).astype(int)
choice_reset=(E[:,T//2:].sum(1)+rng.normal(0,3.0,size=n)>0).astype(int)

kernel=fit_kernel(choice)
kernel_last=fit_kernel(choice_last)
kernel_reset=fit_kernel(choice_reset)

z_measured=cum+rng.normal(0,1.0,size=cum.shape)
r2=[r2_score(cum[:,t],z_measured[:,t]) for t in range(T)]

def sigmoid(v,temp=3.0):
    return 1/(1+np.exp(-np.clip(v/temp,-40,40)))

base_p=sigmoid(cum[:,-1])
pulse_full=[
    float(np.mean(sigmoid(cum[:,-1]+1)-base_p))
    for _ in range(T)
]

reset_sum=E[:,T//2:].sum(1)
base_pr=sigmoid(reset_sum)
pulse_reset=[]
for j in range(T):
    pulse_reset.append(float(np.mean(
        sigmoid(reset_sum+(1 if j>=T//2 else 0))-base_pr
    )))

result={
    "round":"R117",
    "seed":SEED,
    "generated_trials":N,
    "trials_after_tie_filter":n,
    "bins":T,
    "accumulator_choice_accuracy_vs_evidence_majority":float(accuracy_score(target,choice)),
    "last_sample_choice_accuracy_vs_evidence_majority":float(accuracy_score(target,choice_last)),
    "midpoint_reset_choice_accuracy_vs_evidence_majority":float(accuracy_score(target,choice_reset)),
    "kernel_accumulator":kernel.tolist(),
    "kernel_last_sample":kernel_last.tolist(),
    "kernel_midpoint_reset":kernel_reset.tolist(),
    "state_cumulative_evidence_r2_by_time":r2,
    "causal_plus1_pulse_choice_probability_effect_accumulator":pulse_full,
    "causal_plus1_pulse_effect_midpoint_reset":pulse_reset,
    "scope":"Artificial matched sequential-evidence support experiment; not a consciousness measurement."
}
print(json.dumps(result,indent=2))
