"""Audit source TBWs against explicitly declared Gaussian curve variants.

Uses source row/column identities without relabeling, never consults p values,
and does not overwrite v0.1 files. Ordinary least squares, not binomial fitting.
"""
from pathlib import Path
from itertools import product
import json
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"inputs"
OUT=HERE/"results"
OUT.mkdir(exist_ok=True)
X=np.array([-400,-200,-100,0,100,200,400.])/400
raw=pd.read_excel(SOURCE/"Experiment_3.xlsx",header=None)
counts=raw.iloc[3:33,1:43].to_numpy(float).reshape(30,2,3,7)
published=raw.iloc[3:33,63:69].to_numpy(float).reshape(30,2,3)

def unpack(theta,baseline,center):
    j=0
    if baseline=="zero": b=0.
    else: b=theta[j];j+=1
    amp=theta[j];j+=1
    if center=="zero": mu=0.
    else: mu=theta[j];j+=1
    sd=np.exp(theta[j])
    return b,amp,mu,sd

def residual_jac(theta,y,baseline,center):
    b,amp,mu,sd=unpack(theta,baseline,center)
    z=(X-mu)/sd; h=np.exp(-.5*z*z)
    prediction=b+amp*h
    columns=[]
    if baseline!="zero":columns.append(np.ones_like(X))
    columns.append(h)
    if center!="zero":columns.append(amp*h*z/sd)
    columns.append(amp*h*z*z)
    return prediction-y,np.column_stack(columns)

def fit(y,baseline,center):
    low=[];high=[]
    if baseline!="zero":
        low.append(0. if baseline=="nonnegative" else -10.);high.append(1.)
    low.append(0.);high.append(20.)
    if center!="zero":low.append(-1.25);high.append(1.25)
    low.append(np.log(.0025));high.append(np.log(10.))
    candidates=[]
    starts=[]
    for sd in [.2,.4,.8]:
        b=0 if baseline=="zero" else max(0.,float(y.min())-.05)
        amp=max(.05,float(y.max())-b)
        mu=float(np.sum(X*(y-y.min()+.01))/np.sum(y-y.min()+.01))
        theta=[]
        if baseline!="zero":theta.append(b)
        theta.append(amp)
        if center!="zero":theta.append(mu)
        theta.append(np.log(sd))
        starts.append(theta)
    for theta in starts:
        r=least_squares(lambda th:residual_jac(th,y,baseline,center)[0],theta,
                        jac=lambda th:residual_jac(th,y,baseline,center)[1],bounds=(low,high),
                        xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=10000)
        candidates.append(r)
    result=min(candidates,key=lambda r:r.cost)
    b,a,mu,sd=unpack(result.x,baseline,center)
    residual,_=residual_jac(result.x,y,baseline,center)
    return dict(offset=b,amplitude=a,center_ms=mu*400,sd_ms=sd*400,
                sse=float(np.sum(residual**2)),converged=bool(result.success),
                optimality=float(result.optimality),nfev=int(result.nfev))

def main():
    rows=[]
    for baseline,center in product(["zero","free","nonnegative"],["free","zero"]):
        model=baseline+"_baseline_"+center+"_center"
        for i,t,f in product(range(30),range(2),range(3)):
            info=fit(counts[i,t,f]/10,baseline,center)
            rows.append(dict(model=model,participant=i+1,task=["ownership","simultaneity"][t],
                             condition=["8Hz","sham","13Hz"][f],published_sd_ms=published[i,t,f],
                             abs_error_ms=abs(info["sd_ms"]-published[i,t,f]),**info))
        sub=pd.DataFrame([r for r in rows if r["model"]==model])
        print(model,"max_error_ms",sub.abs_error_ms.max(),"median",sub.abs_error_ms.median(),
              "within_0.01ms",int((sub.abs_error_ms<.01).sum()),flush=True)
    frame=pd.DataFrame(rows)
    frame.to_csv(OUT/"all_gaussian_candidate_fits.csv",index=False)
    summary={}
    for name,d in frame.groupby("model"):
        e=d.abs_error_ms.to_numpy()
        summary[name]={"n_widths":len(d),"max_abs_error_ms":float(e.max()),"median_abs_error_ms":float(np.median(e)),
                       "RMSE_ms":float(np.sqrt(np.mean(e**2))),"pearson":float(np.corrcoef(d.sd_ms,d.published_sd_ms)[0,1]),
                       "within_ms":{str(x):int((e<x).sum()) for x in [1e-4,1e-3,1e-2,1.,5.]},
                       "all_converged":bool(d.converged.all())}
    (OUT/"gaussian_reconstruction_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
