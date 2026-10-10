"""Fixed full-data and artificial fivefold evaluation of four BCI models.

The plan is BCI_EXECUTION_PLAN.json. No held-out score selects starts or retries.
The model implementation is supplied separately by the root analysis.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import multiprocessing
import hashlib
import json
import sys
import time
import os

import numpy as np
import pandas as pd
from scipy.special import xlogy
from scipy import stats

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"root_analysis"))
import fit_response_models as model

OUT=HERE/"results"/"bci_response"
FIT_SEED=2026101019
CV_SEED=2026101017
FULL_STARTS=16
CV_STARTS=8

def native(value):
    if isinstance(value,dict):return {str(k):native(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [native(v) for v in value]
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    return value

def fit_record(fit,name,counts,trials,seed,additional):
    p=model.probabilities_and_derivatives(fit["theta"],name)[0]
    return native({**fit,"model":name,"fit_seed":seed,
        "parameters_interpreted":model.fit_summary(fit,name),
        "probabilities":p,"counts":counts,"trials":trials,
        "additional_start_parameters":additional,
        "numerical_quality_flag":not fit["success"] or fit["projected_gradient_max"]>1e-3})

def full_one(args):
    participant,counts,source=args
    records={}
    for j,name in enumerate(model.MODELS):
        base=name.split("_")[0]
        add=[model.source_initial(source[base],name)]
        if name.endswith("_shift"):
            add.append(np.r_[records[base]["theta"],0.,0.])
        seed=FIT_SEED+participant*100+j
        fitted=model.fit_one(counts,10,name,seed=seed,n_starts=FULL_STARTS,additional_starts=add)
        records[name]=fit_record(fitted,name,counts,10,seed,add)
        records[name]["participant"]=participant+1
        records[name]["phase"]="full"
        records[name]["generic_starts_requested"]=FULL_STARTS
        records[name]["matching_source_nll"]=float(model.nll_and_gradient(add[0],counts,10,name)[0])
        if name.endswith("_shift"):
            records[name]["nesting_violation"]=bool(fitted["nll"]>records[base]["nll"]+1e-6)
    return participant,records

def cv_one(args):
    participant,fold,train,test=args
    records={}
    for j,name in enumerate(model.MODELS):
        seed=FIT_SEED+10000+participant*100+fold*10+j
        fitted=model.fit_one(train,8,name,seed=seed,n_starts=CV_STARTS,additional_starts=None)
        record=fit_record(fitted,name,train,8,seed,[])
        record["participant"]=participant+1
        record["fold"]=fold+1
        record["phase"]="cv"
        record["generic_starts_requested"]=CV_STARTS
        record["heldout_counts"]=test.tolist()
        record["heldout_trials"]=2
        record["heldout_nll"]=float(model.nll_and_gradient(fitted["theta"],test,2,name)[0])
        record["full_data_or_source_initialization_used"]=False
        records[name]=record
    return participant,fold,records

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    code=Path(model.__file__).read_bytes()
    code_hash=hashlib.sha256(code).hexdigest()
    raw=pd.read_excel(HERE/"inputs"/"Experiment_3.xlsx",header=None)
    counts=raw.iloc[3:33,1:43].to_numpy(int).reshape(30,6,7)
    saved=pd.read_excel(HERE/"inputs"/"Experiment_3_Computational_modelling.xlsx",header=None)
    prior=saved.iloc[1:31,1:10].to_numpy(float)
    sigma=saved.iloc[35:65,1:8].to_numpy(float)
    assert np.isfinite(prior).all() and np.isfinite(sigma).all()
    rng=np.random.default_rng(CV_SEED)
    heldout=np.zeros((5,30,6,7),int)
    for i,t,s in np.ndindex(counts.shape):
        binary=np.r_[np.ones(counts[i,t,s],int),np.zeros(10-counts[i,t,s],int)]
        heldout[:,i,t,s]=rng.permutation(binary).reshape(5,2).sum(axis=1)
    assert np.array_equal(heldout.sum(axis=0),counts)
    np.savez(OUT/"cv_partition_counts.npz",full_counts=counts,test_counts=heldout,
             train_counts=counts[None,:,:,:]-heldout,seed=CV_SEED)
    full=[None]*30
    ctx=multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=4,mp_context=ctx) as pool:
        pending=[pool.submit(full_one,(i,counts[i],{"sigma":sigma[i],"prior":prior[i]})) for i in range(30)]
        for done,future in enumerate(as_completed(pending),1):
            i,records=future.result();full[i]=records
            if done%5==0:print("full_participants",done,"elapsed",round(time.monotonic()-start,2),flush=True)
    (OUT/"full_fits.json").write_text(json.dumps(full,indent=2)+"\n")
    cv=[[None]*5 for _ in range(30)]
    with ProcessPoolExecutor(max_workers=4,mp_context=ctx) as pool:
        pending=[pool.submit(cv_one,(i,f,counts[i]-heldout[f,i],heldout[f,i])) for i in range(30) for f in range(5)]
        for done,future in enumerate(as_completed(pending),1):
            i,f,records=future.result();cv[i][f]=records
            if done%15==0:print("cv_participant_folds",done,"elapsed",round(time.monotonic()-start,2),flush=True)
    (OUT/"cv_fits.json").write_text(json.dumps(cv,indent=2)+"\n")
    rows=[]
    for i in range(30):
        for name in model.MODELS:
            fit=full[i][name]
            scores=[cv[i][f][name]["heldout_nll"] for f in range(5)]
            rows.append({"participant":i+1,"model":name,"full_nll":fit["nll"],
                "heldout_nll_sum":sum(scores),"heldout_nll_per_binary_judgment":sum(scores)/420,
                "full_numerical_quality_flag":fit["numerical_quality_flag"],
                "cv_numerical_quality_flags":sum(cv[i][f][name]["numerical_quality_flag"] for f in range(5))})
    frame=pd.DataFrame(rows);frame.to_csv(OUT/"participant_scores.csv",index=False)
    sat=float(-np.sum(xlogy(counts,counts/10)+xlogy(10-counts,1-counts/10)))
    summaries={}
    ks=dict(zip(model.MODELS,[6,8,8,10]))
    for name in model.MODELS:
        part=frame[frame.model==name]
        nll=float(part.full_nll.sum());dev=2*(nll-sat);df=1260-30*ks[name]
        summaries[name]={"effective_parameters_per_participant":ks[name],"full_nll_sum":nll,
            "full_deviance":dev,"nominal_deviance_df":df,"nominal_deviance_chi2_p":float(stats.chi2.sf(dev,df)),
            "sum_AIC":2*nll+2*30*ks[name],"sum_BIC_using420_binary_judgments_per_person":2*nll+np.log(420)*30*ks[name],
            "heldout_nll_sum":float(part.heldout_nll_sum.sum()),
            "heldout_nll_per_binary_judgment":float(part.heldout_nll_sum.sum()/12600),
            "full_quality_flags":int(part.full_numerical_quality_flag.sum()),
            "cv_quality_flags":int(part.cv_numerical_quality_flags.sum()),
            "full_participants_with_any_parameter_bound":sum(bool(full[i][name]["bounds_hit"]) for i in range(30)),
            "cv_fits_with_any_parameter_bound":sum(bool(cv[i][f][name]["bounds_hit"]) for i in range(30) for f in range(5))}
    contrasts={}
    for a,b in [("sigma","prior"),("sigma_shift","prior_shift"),("sigma","sigma_shift"),("prior","prior_shift")]:
        da=frame[frame.model==a].sort_values("participant").heldout_nll_sum.to_numpy()
        db=frame[frame.model==b].sort_values("participant").heldout_nll_sum.to_numpy()
        difference=da-db
        se=float(difference.std(ddof=1)/np.sqrt(30))
        ci=stats.t.interval(.95,29,loc=float(difference.mean()),scale=se)
        contrasts[a+"_minus_"+b]={"definition":"positive means second named model has smaller held-out NLL",
            "total_nll_difference":float(difference.sum()),"mean_participant_nll_difference":float(difference.mean()),
            "sd_across_participants":float(difference.std(ddof=1)),"participant_t95_interval_mean":list(ci),
            "participants_positive":int((difference>0).sum()),"participants_negative":int((difference<0).sum()),
            "individual_differences":difference.tolist(),
            "uncertainty_scope":"Descriptive paired participant interval conditional on this artificial partition and fitting procedure; selected source sample, no independent replication."}
    report={"finished_at_utc":datetime.now(timezone.utc).isoformat(),"elapsed_seconds":time.monotonic()-start,
        "source_model_file":str(Path(model.__file__)),"source_model_sha256":code_hash,
        "source_model_bytes_unchanged":hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()==code_hash,
        "full_fit_records":120,"cv_fit_records":600,"folds":5,"full_starts_requested":FULL_STARTS,
        "cv_starts_requested":CV_STARTS,"canonical_start_additional":True,"cv_seed":CV_SEED,"fit_seed":FIT_SEED,
        "saturated_count_nll":sat,"models":summaries,"paired_cv_contrasts":contrasts,
        "full_shift_nesting_violations":sum(full[i][name].get("nesting_violation",False) for i in range(30) for name in model.MODELS),
        "cv_partition_warning":"Artificial binary partitions of aggregate counts under conditional exchangeability. Trial chronology, block dependence and independent replication are not reconstructed.",
        "deviance_warning":"Reference chi-square only. Small cell counts, boundaries, nonlinear parameters, fitting uncertainty and ignored dependence limit calibration.",
        "score_warning":"NLL omits binomial coefficients so that all folds sum binary predictive log scores; these common constants do not alter paired comparisons."}
    (OUT/"response_comparison_summary.json").write_text(json.dumps(native(report),indent=2)+"\n")
    print(json.dumps(native(report),indent=2))

if __name__=="__main__":main()
