"""Diagnose the two material TBW discrepancies without repairing source data."""
from pathlib import Path
from itertools import product,permutations
import json
import numpy as np
import pandas as pd
from scipy.optimize import least_squares, minimize_scalar
from reconstruct_gaussian_widths import residual_jac,unpack,counts,published,X

HERE=Path(__file__).resolve().parent
OUT=HERE/"results"
fits=pd.read_csv(OUT/"all_gaussian_candidate_fits.csv")
free=fits[fits.model=="free_baseline_free_center"].copy()
grid_bad=[]
for row in free.itertuples():
    z=(X*400-row.center_ms)/row.sd_ms
    p=row.offset+row.amplitude*np.exp(-.5*z*z)
    grid_bad.append(dict(participant=row.participant,task=row.task,condition=row.condition,
        observed_grid_min=float(p.min()),observed_grid_max=float(p.max()),
        grid_cells_below_zero=int((p<0).sum()),grid_cells_above_one=int((p>1).sum()),
        whole_line_infimum=row.offset,whole_line_maximum=row.offset+row.amplitude,
        whole_line_probability_compatible=bool(row.offset>=0 and row.offset+row.amplitude<=1)))
qc=pd.DataFrame(grid_bad)
qc.to_csv(OUT/"gaussian_probability_domain_diagnostics.csv",index=False)

# Check all global column permutations; do not apply any permutation to data.
w=free.sd_ms.to_numpy().reshape(30,6)
pub=published.reshape(30,6)
permutation_sse=[(float(np.sum((w-pub[:,p])**2)),list(p)) for p in permutations(range(6))]
permutation_sse.sort()

# Width conventions do not resolve the mismatch. An area amplitude is an
# equivalent nuisance parameterization and denominator changes only rescale y.
conventions={"sigma":1.,"MATLAB_gauss1_c":np.sqrt(2),"FWHM":2*np.sqrt(2*np.log(2)),
             "HWHM":np.sqrt(2*np.log(2)),"two_sigma":2.,"half_sigma":.5}
convention_rows=[]
for model,d in fits.groupby("model",sort=False):
    for name,factor in conventions.items():
        err=np.abs(d.sd_ms.to_numpy()*factor-d.published_sd_ms.to_numpy())
        convention_rows.append(dict(model=model,convention=name,factor=factor,
            RMSE_ms=float(np.sqrt(np.mean(err**2))),median_absolute_ms=float(np.median(err)),
            within_0_01_ms=int((err<.01).sum())))
pd.DataFrame(convention_rows).to_csv(OUT/"gaussian_width_convention_checks.csv",index=False)

cases=[]
for i,t,f in [(0,1,0),(23,0,2)]:
    y=counts[i,t,f]/10
    starts=[]
    for baseline,mu,sd in product([-.2,0.,.2],[ -.5,-.25,0.,.25,.5],[.15,.3,.5,1.]):
        initial=[baseline,max(.1,float(y.max())-baseline),mu,np.log(sd)]
        r=least_squares(lambda z:residual_jac(z,y,"free","free")[0],initial,
            jac=lambda z:residual_jac(z,y,"free","free")[1],
            bounds=([-10,0,-1.25,np.log(.0025)],[1,20,1.25,np.log(10)]),
            ftol=1e-13,gtol=1e-13,xtol=1e-13,max_nfev=10000)
        pars=unpack(r.x,"free","free")
        starts.append(dict(offset=pars[0],amplitude=pars[1],center_ms=pars[2]*400,
                           sd_ms=pars[3]*400,sse=float(2*r.cost),converged=bool(r.success)))
    # At fixed source sigma, solve offset and height exactly by linear LS;
    # optimize center over each local bracket from a fixed broad grid.
    source_sd=published[i,t,f]
    def at_mu(mu):
        g=np.exp(-.5*((X*400-mu)/source_sd)**2)
        design=np.c_[np.ones(7),g]
        coef=np.linalg.lstsq(design,y,rcond=None)[0]
        return float(np.sum((design@coef-y)**2))
    mg=np.linspace(-500,500,2001)
    sse_grid=np.array([at_mu(m) for m in mg])
    cand=[]
    for n in range(1,len(mg)-1):
        if sse_grid[n]<=sse_grid[n-1] and sse_grid[n]<=sse_grid[n+1]:
            r=minimize_scalar(at_mu,bounds=(mg[n-1],mg[n+1]),method="bounded",
                              options={"xatol":1e-11})
            cand.append((float(r.fun),float(r.x)))
    fixed_sse,fixed_mu=min(cand)
    g=np.exp(-.5*((X*400-fixed_mu)/source_sd)**2)
    coef=np.linalg.lstsq(np.c_[np.ones(7),g],y,rcond=None)[0]
    pred=coef[0]+coef[1]*g
    derivative=float(-2*np.sum((y-pred)*coef[1]*g*((X*400-fixed_mu)/source_sd)**2/source_sd))
    selected=fits[(fits.participant==i+1)&(fits.task==["ownership","simultaneity"][t])&
                  (fits.condition==["8Hz","sham","13Hz"][f])]
    cases.append(dict(participant=i+1,task=["ownership","simultaneity"][t],condition=["8Hz","sham","13Hz"][f],
        counts=counts[i,t,f].astype(int).tolist(),published_sd_ms=float(source_sd),
        baseline_center_conventions=selected[["model","sd_ms","abs_error_ms","sse"]].to_dict("records"),
        multistart_n=len(starts),multistart_best=min(starts,key=lambda x:x["sse"]),
        multistart_sigma_range_ms=[min(x["sd_ms"] for x in starts),max(x["sd_ms"] for x in starts)],
        multistart_sse_range=[min(x["sse"] for x in starts),max(x["sse"] for x in starts)],
        all_multistarts_converged=all(x["converged"] for x in starts),
        source_sd_profile_best_sse=fixed_sse,source_sd_profile_center_ms=fixed_mu,
        source_sd_profile_offset=float(coef[0]),source_sd_profile_amplitude=float(coef[1]),
        source_sd_profile_derivative_per_ms=derivative,
        source_sd_profile_sse_excess=fixed_sse-min(x["sse"] for x in starts),
        interpretation="Diagnostic under explicit unweighted four-parameter Gaussian LS only. No substitution or source-data repair is made."))

summary={
    "negative_offsets":int((free.offset<0).sum()),
    "observed_grid_curves_with_probability_violations":int(((qc.grid_cells_below_zero+qc.grid_cells_above_one)>0).sum()),
    "observed_grid_cells_below_zero":int(qc.grid_cells_below_zero.sum()),
    "observed_grid_cells_above_one":int(qc.grid_cells_above_one.sum()),
    "whole_real_line_curves_with_probability_violations":int((~qc.whole_line_probability_compatible).sum()),
    "best_global_published_column_permutation":permutation_sse[0],
    "second_best_global_published_column_permutation":permutation_sse[1],
    "column_order":["Own8","OwnSham","Own13","Sim8","SimSham","Sim13"],
    "column_permutation_applied":False,
    "material_discrepancies":cases,
    "denominator_invariance":"Scaling every ordinate by the same constant scales the free offset and height, but not least-squares optimal center or sigma. All source cells have n=10.",
    "area_height_invariance":"A free Gaussian area is A_height*sigma*sqrt(2*pi); for positive sigma it is a one-to-one nuisance reparameterization and leaves fitted sigma unchanged.",
}
(OUT/"reconstruction_residual_audit.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
