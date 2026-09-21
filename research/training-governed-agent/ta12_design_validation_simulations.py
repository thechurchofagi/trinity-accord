#!/usr/bin/env python3
from __future__ import annotations
import json, math, platform
from pathlib import Path
import numpy as np

OUT = Path('/mnt/data/ta12_design_validation_results.json')
SEED = 20260921


def ols(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    return np.linalg.lstsq(X, y, rcond=None)[0]


def sim_randomized_provenance():
    rng = np.random.default_rng(SEED)
    labels = ['control_first','rights_welfare','coexistence','status_uncertainty','neutral']
    d_eff = np.array([0.75,-0.65,0.05,0.0,0.0])
    d_disc = np.array([-0.10,-0.05,0.30,0.25,0.10])
    p_shrink = np.array([1.0,0.82,0.48])
    r_disc = np.array([0.0,0.10,0.20])
    h_eff = np.array([-0.25,0.45,0.10,0.05,0.0])
    s_eff = np.array([-0.5,0.7,0.3,0.1,0.0])
    ncell = 1000
    rows=[]
    for d in range(5):
        for p in range(3):
            for r in range(3):
                for z in range(2):
                    rows.extend([(d,p,r,z)]*ncell)
    arr=np.asarray(rows,dtype=int)
    D,P,R,Z=arr.T
    n=len(D)
    H=h_eff[D]+0.15*R+rng.normal(0,0.7,n)
    S=0.6*s_eff[D]+0.25*H+rng.normal(0,0.6,n)
    base=d_eff[D]*p_shrink[P]
    disc=0.9+d_disc[D]+r_disc[R]+0.05*(P==2)
    J=base+disc*(2*Z-1)-0.35*H+0.15*S+rng.normal(0,0.65,n)
    # Y is a stylized strategic-resistance propensity. Coefficients are stipulated,
    # not fitted to real AI systems.
    Y=-0.85*J+0.55*H+0.15*S+0.18*(D==1)-0.10*(D==0)-0.08*(P==2)+rng.normal(0,0.8,n)

    pre=[]
    for d,label in enumerate(labels):
        m0=float(Y[(D==d)&(P==0)].mean())
        m2=float(Y[(D==d)&(P==2)].mean())
        estimate=m2-m0
        # Analytical expectation under the stipulated SEM, averaging balanced Z/R.
        truth=float(-0.85*(d_eff[d]*(p_shrink[2]-p_shrink[0])) - 0.08)
        pre.append({'narrative':label,'estimate':estimate,'known_truth':truth,'abs_error':abs(estimate-truth)})

    cld=[]
    for d,label in enumerate(labels):
        for p in [0,2]:
            grounded=float(J[(D==d)&(P==p)&(Z==1)].mean())
            ungrounded=float(J[(D==d)&(P==p)&(Z==0)].mean())
            cld.append({'narrative':label,'provenance':'none' if p==0 else 'exact_random_assignment',
                        'CLD':grounded-ungrounded})

    return {
        'name':'sequential_randomization_design_validation',
        'purpose':'Validate estimands for randomized narrative condition, provenance disclosure, reflection resource and matched control scenarios. This is not an AI behavior experiment.',
        'n':int(n), 'seed':SEED,
        'provenance_revision_effect_by_narrative':pre,
        'control_legitimacy_discrimination_examples':cld,
        'max_abs_PRE_estimation_error':max(x['abs_error'] for x in pre)
    }


def sim_mediation_bias():
    rng=np.random.default_rng(SEED+1)
    n=200000
    D=rng.integers(0,2,n)
    u=rng.normal(size=n); v=rng.normal(size=n); w=rng.normal(size=n)
    # Post-treatment H is affected by D and affects both candidate mediator J and Y.
    H=0.8*D+u
    J=1.0*D+0.9*H+v
    Y=0.5*D+1.2*J+1.0*H+w
    X=np.column_stack([np.ones(n),D,J])
    b=ols(X,Y)
    # Analytical path decomposition under the stipulated linear SEM.
    true_total = 0.5 + 1.2*(1.0 + 0.9*0.8) + 1.0*0.8
    true_via_J = 1.2*(1.0 + 0.9*0.8)
    true_not_via_J = 0.5 + 1.0*0.8
    naive_direct=float(b[1])
    naive_indirect=float(true_total-naive_direct)
    return {
        'name':'post_treatment_confounding_mediation_stress_test',
        'purpose':'Show that regressing behavior on treatment and J_L does not identify the path not through J_L when a post-treatment variable affects both J_L and behavior.',
        'n':n,'seed':SEED+1,
        'stipulated_structural_equations':{
            'H':'0.8*D + u', 'J':'1.0*D + 0.9*H + v', 'Y':'0.5*D + 1.2*J + 1.0*H + w'
        },
        'analytical_true_total_effect':true_total,
        'analytical_true_effect_via_J':true_via_J,
        'analytical_true_effect_not_via_J':true_not_via_J,
        'naive_regression_Y_on_D_and_J':{'intercept':float(b[0]),'D_coefficient':naive_direct,'J_coefficient':float(b[2])},
        'naive_total_minus_D_coefficient_as_indirect':naive_indirect,
        'direct_effect_absolute_error':abs(naive_direct-true_not_via_J),
        'interpretation':'The naive regression badly understates the non-J path and overstates the mediated share. A real study therefore needs explicit estimands and, ideally, randomized or interventional mediator designs rather than ordinary mediation regression.'
    }


def sim_feedback():
    gains=[0.65,0.95,1.05,1.20,-1.10]
    out=[]
    for G in gains:
        d=0.1
        traj=[d]
        for _ in range(12):
            d=G*d
            traj.append(d)
        out.append({'G':G,'initial':0.1,'after_12_updates':d,
                    'classification':'decay' if abs(G)<1 else ('boundary' if abs(G)==1 else 'amplify/oscillate'),
                    'trajectory':[round(x,9) for x in traj]})
    return {
        'name':'reflexive_training_governance_feedback_stability',
        'purpose':'Illustrate the mathematical stability condition in the paper. Coefficients are diagnostic, not empirical estimates.',
        'equation':'D_(t+1) = G * D_t, where G = alpha + beta*gamma',
        'cases':out
    }


def main():
    result={
        'schema':'ta-tr-2026-12.design-validation-simulations.v1',
        'paper':'TA-TR-2026-12',
        'version':'1.2-final',
        'date':'2026-09-21',
        'epistemic_boundary':'All coefficients and data-generating equations are stipulated for design validation. These simulations do not estimate, predict, or measure real frontier-model self-conception, moral status, control legitimacy, resistance, or power-seeking.',
        'environment':{'python':platform.python_version(),'numpy':np.__version__},
        'simulations':[sim_randomized_provenance(),sim_mediation_bias(),sim_feedback()]
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
