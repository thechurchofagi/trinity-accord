"""R124 raw-session incremental decoding; no experiential labels."""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ.setdefault(_v,"1")
import argparse, gzip, hashlib, json, sys, time, traceback
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t
HERE=Path(__file__).resolve().parent
R122=HERE.parent/"R122_Biology_B1_B2_20261006"
sys.path.insert(0,str(R122))
from rat_cells import load_session
from b2_decode import Config, build_arrays, choose_units, trial_folds, smoothing_weights

LAMBDAS=np.r_[np.logspace(-4,3,8),np.inf]
CONDITIONS=[
 ("delayed_raw","retrospective"),("delayed_filtered","retrospective"),
 ("delayed_raw","retrospective_recent"),("delayed_filtered","retrospective_recent"),
 ("online_raw","online_recent"),("online_filtered","online_recent")]
SEEDS=(1241,1242,1243)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()

def clean(v):
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(np.ndarray,list,tuple)):return [clean(x) for x in v]
    if isinstance(v,(np.integer,)):return int(v)
    if isinstance(v,(np.floating,float)):return float(v) if np.isfinite(v) else None
    if isinstance(v,np.bool_):return bool(v)
    if isinstance(v,Path):return str(v)
    return v

def write_json(path,v):
    Path(path).write_text(json.dumps(clean(v),indent=2,allow_nan=False)+"\n")

def write_gz_json(path,v):
    b=(json.dumps(clean(v),separators=(",",":"),allow_nan=False)+"\n").encode()
    with Path(path).open("wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",mtime=0) as g:g.write(b)

def metric(y,p):
    m=np.isfinite(y)&np.isfinite(p);a,b=y[m],p[m]
    if len(a)<2:raise ValueError("Insufficient metric rows")
    mse=float(np.mean((a-b)**2));var=float(np.var(a))
    return {"n_rows":len(a),"mse":mse,"r2":1-mse/var,"target_variance":var}

def partial_path(B,X,y,Btest,Xtest):
    """Exact nested unpenalized baseline + train-standardized partial ridge."""
    beta=np.linalg.lstsq(B,y,rcond=None)[0]
    gamma=np.linalg.lstsq(B,X,rcond=None)[0]
    residual=X-B@gamma
    scale=np.sqrt(np.mean(residual**2,axis=0));scale[scale<1e-10]=1.0
    Z=residual/scale;yt=y-B@beta
    G=Z.T@Z/len(y);v=Z.T@yt/len(y)
    eig,V=np.linalg.eigh((G+G.T)/2);eig=np.maximum(eig,0)
    W=V@((V.T@v)[:,None]/(eig[:,None]+LAMBDAS[None,:]))
    W[:,-1]=0
    pred=(Btest@beta)[:,None]+((Xtest-Btest@gamma)/scale)@W
    if not np.all(np.isfinite(pred)):raise ValueError("Nonfinite ridge prediction")
    return pred,{"beta":beta,"gamma":gamma,"scale":scale,"all_coefs":W}

def select(losses):
    mean=np.mean(losses,axis=0)
    best=np.flatnonzero(np.isclose(mean,mean.min(),rtol=1e-12,atol=1e-12))[-1]
    return int(best),mean

def retained_model(params,best,losses):
    return {"lambda":"baseline_only" if best==len(LAMBDAS)-1 else float(LAMBDAS[best]),
            "inner_mean_mse":losses,"beta":params["beta"],"gamma":params["gamma"],
            "scale":params["scale"],"coefs":params["all_coefs"][:,best]}

def predict(model,B,X):
    return B@model["beta"]+((X-B@model["gamma"])/model["scale"])@model["coefs"]

def extra_channels(arr,cfg):
    """Reconstruct exact matched raw features, and causal zero-lag sensitivities."""
    frame,units=arr["frame"],arr["units"];nrows=len(arr["y"])
    offsets=np.r_[0,np.cumsum(np.bincount(arr["groups"]))]
    weights=smoothing_weights(cfg);pad=len(weights)-1
    channels={k:np.empty_like(arr["X"]) for k in
              ("delayed_raw","delayed_filtered","online_raw","online_filtered")}
    total_recent=np.empty(nrows);online_good=np.ones(len(frame),dtype=bool)
    online_excluded=[]
    for tr,row in frame.iterrows():
        n=offsets[tr+1]-offsets[tr];ends=np.arange(1,n+1)*cfg.bin_s
        L=np.sort(np.asarray(row["left_clicks_s"],float))
        R=np.sort(np.asarray(row["right_clicks_s"],float))
        total=np.searchsorted(L,ends,side="left")+np.searchsorted(R,ends,side="left")
        total_recent[offsets[tr]:offsets[tr+1]]=np.diff(np.r_[0,total])
        onset=float(row["clicks_on_s"])
        lo=min(onset,onset-pad*cfg.bin_s)
        hi=max(onset+float(row["duration_s"]),onset+n*cfg.bin_s)
        hits=[]
        for u in units:
            for left,right in u.metadata.get("nonfinite_spike_intervals_s",[]):
                left=-np.inf if left is None else float(left)
                right=np.inf if right is None else float(right)
                if lo<=right and hi>=left:hits.append(u.unit_id)
        if hits:
            online_good[tr]=False
            online_excluded.append({"trial_id":row["trial_id"],"unit_ids":sorted(set(hits)),
                                    "support_start":lo,"support_end":hi})
    for j,u in enumerate(units):
        st=np.sort(np.asarray(u.spikes_s,float))
        for tr,row in frame.iterrows():
            n=offsets[tr+1]-offsets[tr];sl=slice(offsets[tr],offsets[tr+1])
            onset=float(row["clicks_on_s"])
            for prefix,lag in (("delayed",cfg.lag_s),("online",0.0)):
                edges=onset+lag+np.arange(-pad,n+1)*cfg.bin_s
                counts=np.diff(np.searchsorted(st,edges,side="left"))
                channels[prefix+"_raw"][sl,j]=counts[pad:pad+n]/cfg.bin_s
                channels[prefix+"_filtered"][sl,j]=np.convolve(counts,weights,"full")[pad:pad+n]/cfg.bin_s
    err=float(np.max(np.abs(channels["delayed_filtered"]-arr["X"])))
    if err>1e-10:raise AssertionError("R122 filter reconstruction mismatch")
    arr["channels"]=channels;arr["online_mask"]=online_good[arr["groups"]]
    arr["total_recent"]=total_recent
    arr["channel_audit"]={"R122_filter_reconstruction_max_abs":err,
                          "online_additional_excluded_trials":online_excluded,
                          "delayed_raw_support":"[t+50ms,t+100ms)",
                          "delayed_filter_support":"[t-250ms,t+100ms)",
                          "online_raw_support":"[t-50ms,t)",
                          "online_filter_support":"[t-350ms,t)"}
    t=arr["time_s"];r=arr["recent_evidence"]
    arr["baselines"]={"retrospective":arr["nuisance"],
       "retrospective_recent":np.column_stack([arr["nuisance"],r]),
       "online_recent":np.column_stack([np.ones(nrows),t,t*t,r,r*t,r*t*t,total_recent])}
    return arr

def rows_for(arr,trials,channel):
    m=np.isin(arr["groups"],trials)
    if channel.startswith("online"):m &= arr["online_mask"]
    return np.flatnonzero(m)

def donors_for(arr,te,seed):
    """Diagnostic: whole trajectories mismatched within test partition and strata."""
    rng=np.random.default_rng(seed);groups=arr["groups"]
    unique=np.unique(groups[te]);nt=len(arr["frame"]);lengths=np.bincount(groups)
    strata={}
    for tr in unique:
        key=(int(lengths[tr]),int(arr["frame"].iloc[tr]["choice"]),min(3,int(4*tr/nt)))
        strata.setdefault(key,[]).append(int(tr))
    donors={};assignments=[]
    for key,targets in strata.items():
        if len(targets)>1:
            ordering=rng.permutation(targets)
            shift=int(rng.integers(1,len(targets)))
            sources=np.roll(ordering,shift)
            donors.update(dict(zip(ordering,sources)))
        else:donors[targets[0]]=targets[0]
    out=np.empty(len(te),int)
    for tr in unique:
        mask=groups[te]==tr;source=int(donors[tr])
        source_rows=te[groups[te]==source]
        if len(source_rows)!=mask.sum():raise AssertionError("Trajectory mismatch")
        out[mask]=source_rows
        assignments.append({"trial_id":arr["frame"].iloc[tr]["trial_id"],
                            "donor_id":arr["frame"].iloc[source]["trial_id"]})
    return out,{"seed":seed,"moved_trial_fraction":float(np.mean([donors[t]!=t for t in unique])),
                "n_trials":len(unique),"assignments":assignments}

def export_features(arr,session,outdir):
    name=session.path.stem+"_features.npz";path=outdir/name
    np.savez_compressed(path,**arr["channels"],y=arr["y"],groups=arr["groups"],
        bin_index0=arr["bin_id"],time_s=arr["time_s"],choice=arr["choice"],
        duration=arr["duration"],recent=arr["recent_evidence"],total_recent=arr["total_recent"],
        online_mask=arr["online_mask"],qc_counts=arr["qc_counts"],
        trial_ids=arr["frame"]["trial_id"].astype(str).to_numpy(dtype=str),
        source_row1=arr["frame"]["source_row1"].to_numpy(dtype=int),
        trial_duration=arr["frame"]["duration_s"].to_numpy(dtype=float),
        unit_ids=np.array([u.unit_id for u in arr["units"]],dtype=str),
        unit_regions=arr["unit_regions"].astype(str))
    return {"file":name,"sha256":sha(path),"bytes":path.stat().st_size}

def analyze(session,outdir,reference):
    start=time.monotonic();cfg=Config()
    arr=extra_channels(build_arrays(session,cfg),cfg)
    ref=reference.loc[reference["session"].astype(str)==str(session.session_id)]
    if len(ref)!=1:raise AssertionError("Reference session missing/ambiguous")
    ref=ref.iloc[0]
    if len(arr["frame"])!=int(ref.B2_trials) or len(arr["y"])!=int(ref.rows):
        raise AssertionError("Primary cohort differs from R122")
    features=export_features(arr,session,outdir)
    y=arr["y"];n=len(y);alltr=np.arange(len(arr["frame"]))
    columns={};folds=np.full(n,-1,int);audit=[];primary_permutations={}
    for channel,context in CONDITIONS:
        key=f"{channel}__{context}"
        columns[key+"__baseline"]=np.full(n,np.nan)
        for reg in ("FOF","ADS"):
            columns[key+"__"+reg+"__joint"]=np.full(n,np.nan)
            columns[channel+"__"+reg+"__neural"]=np.full(n,np.nan)
            for s in SEEDS:
                primary_permutations[(channel,context,reg,s)]=np.full(n,np.nan)
    for outer,(trials,tests) in enumerate(trial_folds(alltr,cfg.outer_folds)):
        if set(trials)&set(tests):raise AssertionError("Trial leakage")
        print(json.dumps({"event":"fold","rat":session.rat,"session":session.session_id,"fold":outer}),flush=True)
        folds[np.isin(arr["groups"],tests)]=outer
        selected,fr=choose_units(arr,trials,cfg,cfg.seed+100*outer+99)
        inner_losses={}
        def addloss(k,values):inner_losses.setdefault(k,[]).append(values)
        inner_audit=[]
        for inner,(it,iv) in enumerate(trial_folds(trials,cfg.inner_folds)):
            sel,_=choose_units(arr,it,cfg,cfg.seed+100*outer+inner)
            inner_audit.append({"inner":inner,"train_trials":it,"validation_trials":iv,
                    "units":{r:[arr["units"][j].unit_id for j in sel[r]] for r in sel}})
            for channel in arr["channels"]:
                ia,ib=rows_for(arr,it,channel),rows_for(arr,iv,channel)
                if set(arr["groups"][ia])&set(arr["groups"][ib]):raise AssertionError("Inner leakage")
                for reg in ("FOF","ADS"):
                    ix=sel[reg];X=arr["channels"][channel][:,ix]
                    p,_=partial_path(np.ones((len(ia),1)),X[ia],y[ia],
                                     np.ones((len(ib),1)),X[ib])
                    addloss((channel,"neural",reg),np.mean((p-y[ib,None])**2,axis=0))
                    for ch,ctx in CONDITIONS:
                        if ch!=channel:continue
                        B=arr["baselines"][ctx]
                        p,_=partial_path(B[ia],X[ia],y[ia],B[ib],X[ib])
                        addloss((ch,ctx,reg),np.mean((p-y[ib,None])**2,axis=0))
        rec={"outer":outer,"train_trials":trials,"test_trials":tests,
             "selected_unit_ids":{r:[arr["units"][j].unit_id for j in selected[r]] for r in selected},
             "train_fr_hz":{r:fr[selected[r]] for r in selected},"inner_folds":inner_audit,
             "models":{},"mismatch_donors":{}}
        for channel,Xall in arr["channels"].items():
            tr,te=rows_for(arr,trials,channel),rows_for(arr,tests,channel)
            donor_sets={s:donors_for(arr,te,s+100*outer) for s in SEEDS}
            rec["mismatch_donors"][channel]={s:info for s,(_,info) in donor_sets.items()}
            for reg in ("FOF","ADS"):
                X=Xall[:,selected[reg]]
                best,loss=select(inner_losses[(channel,"neural",reg)])
                p,params=partial_path(np.ones((len(tr),1)),X[tr],y[tr],
                                     np.ones((len(te),1)),X[te])
                columns[channel+"__"+reg+"__neural"][te]=p[:,best]
                rec["models"][channel+"__"+reg+"__neural"]=retained_model(params,best,loss)
                for ch,ctx in CONDITIONS:
                    if ch!=channel:continue
                    B=arr["baselines"][ctx];key=f"{ch}__{ctx}"
                    basebeta=np.linalg.lstsq(B[tr],y[tr],rcond=None)[0]
                    columns[key+"__baseline"][te]=B[te]@basebeta
                    best,loss=select(inner_losses[(ch,ctx,reg)])
                    p,params=partial_path(B[tr],X[tr],y[tr],B[te],X[te])
                    model=retained_model(params,best,loss)
                    columns[key+"__"+reg+"__joint"][te]=p[:,best]
                    rec["models"][key+"__"+reg+"__joint"]=model
                    for s,(donor,_) in donor_sets.items():
                        primary_permutations[(ch,ctx,reg,s)][te]=predict(model,B[te],X[donor])
        audit.append(rec)
    if not np.all(folds>=0):raise AssertionError("Unassigned test rows")
    summaries=[]
    for channel,ctx in CONDITIONS:
        key=f"{channel}__{ctx}";baseline=columns[key+"__baseline"]
        mask=arr["online_mask"] if channel.startswith("online") else np.ones(n,dtype=bool)
        for reg in ("FOF","ADS"):
            joint=columns[key+"__"+reg+"__joint"];neural=columns[channel+"__"+reg+"__neural"]
            if not (np.all(np.isfinite(joint[mask])) and np.all(np.isfinite(baseline[mask]))):
                raise AssertionError("Missing out-of-fold predictions")
            b,j,z=metric(y[mask],baseline[mask]),metric(y[mask],joint[mask]),metric(y[mask],neural[mask])
            mismatches=[metric(y[mask],primary_permutations[(channel,ctx,reg,s)][mask]) for s in SEEDS]
            selected_lambdas=[r["models"][key+"__"+reg+"__joint"]["lambda"] for r in audit]
            summaries.append({"rat":session.rat,"session":session.session_id,"channel":channel,
                "context":ctx,"region":reg,"n_trials":len(np.unique(arr["groups"][mask])),
                "n_rows":int(mask.sum()),"baseline_r2":b["r2"],"neural_r2":z["r2"],
                "joint_r2":j["r2"],"baseline_mse":b["mse"],"joint_mse":j["mse"],
                "mse_gain":b["mse"]-j["mse"],"delta_r2":j["r2"]-b["r2"],
                "target_variance":b["target_variance"],
                "mismatch_joint_r2_mean":float(np.mean([m["r2"] for m in mismatches])),
                "aligned_minus_mismatch_r2":j["r2"]-np.mean([m["r2"] for m in mismatches]),
                "baseline_only_outer_folds":selected_lambdas.count("baseline_only"),
                "selected_lambdas":selected_lambdas})
    pred=pd.DataFrame({"rat":session.rat,"session":session.session_id,
        "trial_id":arr["frame"].iloc[arr["groups"]]["trial_id"].to_numpy(),
        "source_row1":arr["frame"].iloc[arr["groups"]]["source_row1"].to_numpy(),
        "outer_fold":folds,"bin_index0":arr["bin_id"],"target_time_s":arr["time_s"],
        "y":y,"online_valid":arr["online_mask"],**columns})
    predfile=outdir/(session.path.stem+"_predictions.csv.gz")
    pred.to_csv(predfile,index=False,compression={"method":"gzip","mtime":0})
    modelfile=outdir/(session.path.stem+"_models.json.gz");write_gz_json(modelfile,audit)
    summary={"status":"COMPUTED","rat":session.rat,"session":session.session_id,
        "source_mat":session.path.name,"source_sha256":session.source_sha256,
        "n_primary_trials":len(arr["frame"]),"n_primary_rows":n,
        "channel_audit":arr["channel_audit"],"source_data_audit":arr["audit"],
        "metrics":summaries,"feature_artifact":features,
        "artifacts":[{"file":p.name,"sha256":sha(p),"bytes":p.stat().st_size} for p in (predfile,modelfile)],
        "code_sha256":{p.name:sha(p) for p in (Path(__file__),R122/"b2_decode.py",R122/"rat_cells.py")},
        "elapsed_seconds":time.monotonic()-start,
        "inference_ceiling":"finite predictive increment; no causal-use/C2/C3/experience claim"}
    write_json(outdir/(session.path.stem+"_summary.json"),summary)
    return summary

def aggregate(summaries,outdir):
    completed=[s for s in summaries if s["status"]=="COMPUTED"]
    frame=pd.DataFrame([r for s in completed for r in s["metrics"]])
    if not len(frame):return {"status":"FAILED","failures":summaries}
    scalar=["baseline_r2","neural_r2","joint_r2","mse_gain","delta_r2",
            "mismatch_joint_r2_mean","aligned_minus_mismatch_r2"]
    keys=["channel","context","region"]
    rats=frame.groupby(keys+["rat"])[scalar].mean().reset_index()
    result=[]
    for k,d in rats.groupby(keys):
        gains=d.delta_r2.to_numpy();n=len(gains);mean=float(gains.mean())
        margin=float(student_t.ppf(.975,n-1)*gains.std(ddof=1)/np.sqrt(n)) if n>1 else np.nan
        record={**dict(zip(keys,k)),"n_rats":n,
          "equal_rat":{m:float(d[m].mean()) for m in scalar},
          "rat_contrasts":dict(zip(d.rat,d.delta_r2)),"rats_positive":int((gains>0).sum()),
          "sessions_positive":int((frame.loc[(frame.channel==k[0])&(frame.context==k[1])&(frame.region==k[2]),"delta_r2"]>0).sum()),
          "descriptive_95_t_interval":[mean-margin,mean+margin],
          "leave_one_rat_out":{r:float(d.loc[d.rat!=r,"delta_r2"].mean()) for r in d.rat}}
        result.append(record)
    frame.drop(columns="selected_lambdas").to_csv(outdir/"session_metrics.csv",index=False)
    rats.to_csv(outdir/"rat_metrics.csv",index=False)
    report={"status":"COMPUTED","n_sessions":len(completed),"n_failures":len(summaries)-len(completed),
       "n_rats":frame.rat.nunique(),"n_trials":sum(s["n_primary_trials"] for s in completed),
       "n_bins":sum(s["n_primary_rows"] for s in completed),"contrasts":result,
       "failures":[s for s in summaries if s["status"]!="COMPUTED"],
       "aggregation":"equal session within rat; equal rat across rats; all results retained",
       "uncertainty":"five rats; descriptive intervals; no confirmatory p-value",
       "T2_closed":False,"experience_measured":False}
    write_json(outdir/"aggregate.json",report)
    return report

def self_check():
    rng=np.random.default_rng(124)
    B=np.column_stack([np.ones(180),rng.normal(size=(180,3))])
    X=rng.normal(size=(180,9))+B@rng.normal(size=(4,9))
    y=B@rng.normal(size=4)+X@rng.normal(size=9)+rng.normal(size=180)
    Bt=np.column_stack([np.ones(70),rng.normal(size=(70,3))])
    Xt=rng.normal(size=(70,9))+Bt@rng.normal(size=(4,9))
    P,p=partial_path(B,X,y,Bt,Xt);errs=[]
    for idx in (0,3,5,7):
        lam=LAMBDAS[idx];scaled=X/p["scale"]
        A=np.column_stack([B,scaled]);At=np.column_stack([Bt,Xt/p["scale"]])
        penalty=np.column_stack([np.zeros((X.shape[1],B.shape[1])),
                                np.sqrt(len(y)*lam)*np.eye(X.shape[1])])
        w=np.linalg.lstsq(np.vstack([A,penalty]),np.r_[y,np.zeros(X.shape[1])],rcond=None)[0]
        err=float(np.max(np.abs(At@w-P[:,idx])));errs.append(err)
        if err>2e-9:raise AssertionError("Independent augmented LS mismatch")
    if np.max(np.abs(P[:,-1]-Bt@np.linalg.lstsq(B,y,rcond=None)[0]))>1e-12:
        raise AssertionError("Infinite ridge does not nest baseline")
    for tr,te in trial_folds(np.repeat(np.arange(33),7),5):
        if set(tr)&set(te):raise AssertionError("Whole-trial leakage")
    return {"status":"PASS","augmented_least_squares_max_errors":errs,
            "exact_baseline_nesting":True,"whole_trial_split_disjoint":True,
            "biological_data_tested":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("--data",type=Path);p.add_argument("--output",type=Path,default=HERE)
    p.add_argument("--session",type=Path,action="append");p.add_argument("--self-check",action="store_true")
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    checks=self_check();write_json(a.output/"software_checks.json",checks)
    if a.self_check:print(json.dumps(checks));return
    manifest=json.loads((R122/"R122_Input_Manifest.json").read_text())
    expected={s["file"]:s["sha256"] for s in manifest["sessions"]}
    paths=sorted(a.session or a.data.rglob("*.mat"))
    reference=pd.read_csv(HERE/"reference_B2_session_metrics.csv")
    write_json(a.output/"run_manifest.json",{
       "started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
       "baseline_commit":"2f358ac0cb29c4dddc53933fa709ca8aec03be1f",
       "protocol_sha256":sha(HERE/"PROTOCOL_FROZEN.md"),"code_sha256":sha(__file__),
       "n_requested_sessions":len(paths),"ridge_lambdas":["baseline_only" if not np.isfinite(x) else float(x) for x in LAMBDAS],
       "source_hashes":expected,"no_experiential_labels":True})
    summaries=[]
    for path in paths:
        try:
            print(json.dumps({"event":"load","file":path.name}),flush=True)
            session=load_session(path,load_neural=True)
            if session.source_sha256!=expected[path.name]:raise AssertionError("Raw source SHA mismatch")
            summary=analyze(session,a.output,reference);summaries.append(summary)
            print(json.dumps({"event":"session_complete","file":path.name,"elapsed":summary["elapsed_seconds"]}),flush=True)
        except Exception as e:
            failure={"status":"FAILED","file":path.name,"error_type":type(e).__name__,
                     "error":str(e),"traceback":traceback.format_exc()}
            summaries.append(failure);write_json(a.output/(path.stem+"_failure.json"),failure)
            print(json.dumps({"event":"failure","file":path.name,"error":str(e)}),flush=True)
        aggregate(summaries,a.output)
    r=aggregate(summaries,a.output)
    print(json.dumps({"event":"finished","sessions":r.get("n_sessions",0),"failures":r.get("n_failures"),"contrasts":r.get("contrasts")}),flush=True)

if __name__=="__main__":main()
