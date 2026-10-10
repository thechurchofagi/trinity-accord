"""Preserve targeted alternative-metric diagnostics; no source-value repair."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares,minimize
from scipy.special import xlogy
from reconstruct_gaussian_widths import X,counts,published,residual_jac

HERE=Path(__file__).resolve().parent
rows=[]
for i,t,f in [(0,1,0),(23,0,2)]:
    y=counts[i,t,f]/10
    for target in [1.,float(y.max())]:
        def resid(z):
            offset,mu,logsd=z
            return offset+(target-offset)*np.exp(-.5*((X-mu)/np.exp(logsd))**2)-y
        r=least_squares(resid,[0.,0.,np.log(.4)],
            bounds=([-2,-1.25,np.log(.0025)],[min(y.max(),target),1.25,np.log(10)]),
            max_nfev=10000,ftol=1e-13,gtol=1e-13,xtol=1e-13)
        rows.append({"participant":i+1,"task":t,"condition":f,"model":"LS_fixed_peak_"+str(target),
            "sd_ms":float(np.exp(r.x[2])*400),"source_ms":float(published[i,t,f]),"sse":float(2*r.cost)})
    for label,weights in [
        ("Poisson_observed",np.maximum(y,.05)**-.5),
        ("binomial_observed_padded",(np.clip(y,.05,.95)*(1-np.clip(y,.05,.95)))**-.5)]:
        r=least_squares(lambda z:residual_jac(z,y,"free","free")[0]*weights,
            [.05,.95,0,np.log(.4)],
            bounds=([-10,0,-1.25,np.log(.0025)],[1,20,1.25,np.log(10)]),
            max_nfev=10000,ftol=1e-13,gtol=1e-13,xtol=1e-13)
        rows.append({"participant":i+1,"task":t,"condition":f,"model":label,
            "sd_ms":float(np.exp(r.x[3])*400),"source_ms":float(published[i,t,f]),
            "weighted_objective":float(2*r.cost)})
    def nll(z):
        floor,peak,mu,lsd=z
        p=floor+(peak-floor)*np.exp(-.5*((X-mu)/np.exp(lsd))**2)
        return float(-np.sum(xlogy(counts[i,t,f],p)+xlogy(10-counts[i,t,f],1-p)))
    candidates=[]
    for floor in [0.,.1,.2]:
        r=minimize(nll,[floor,.99,0.,np.log(.4)],method="SLSQP",
            bounds=[(1e-10,.999999),(1e-9,1-1e-10),(-1.25,1.25),(np.log(.0025),np.log(10))],
            constraints=[{"type":"ineq","fun":lambda z:z[1]-z[0]}],
            options={"ftol":1e-11,"maxiter":2000})
        candidates.append(r)
    r=min(candidates,key=lambda z:z.fun)
    rows.append({"participant":i+1,"task":t,"condition":f,"model":"binomial_floor_peak_free_center",
        "sd_ms":float(np.exp(r.x[3])*400),"source_ms":float(published[i,t,f]),
        "nll":float(r.fun),"converged":bool(r.success),"floor":float(r.x[0]),"peak":float(r.x[1])})
(HERE/"results"/"two_case_alternative_metrics.json").write_text(json.dumps(rows,indent=2)+"\n")
print(json.dumps(rows,indent=2))
