"""R125: test frozen observable-state update/output-law candidates on real trials."""
from pathlib import Path
import sys,json,gzip,hashlib,time
import numpy as np,pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
HERE=Path(__file__).resolve().parent
R124=HERE.parent/"R124_Observation_Qualified_Neural_Increment_20261006"
sys.path.insert(0,str(R124))
import joint_decode as study
CHANNELS=("online_raw","online_filtered","delayed_raw","delayed_filtered")

def output_law(x,y):
    """Unpenalized logistic regression; both candidate states share this law."""
    A=np.column_stack([np.ones(len(x)),x])
    def fun(b):
        eta=A@b
        return np.mean(np.logaddexp(0,eta)-y*eta),A.T@(expit(eta)-y)/len(y)
    fit=minimize(fun,np.zeros(2),jac=True,method="BFGS",options={"gtol":1e-8,"maxiter":1000})
    gnorm=float(np.max(np.abs(fun(fit.x)[1])))
    if gnorm>2e-6:raise ValueError("Output-law optimization did not converge")
    return fit.x,{"success":bool(fit.success),"gradient_max":gnorm,"iterations":int(fit.nit)}

def losses(x,y,b):
    p=np.clip(expit(b[0]+b[1]*x),1e-12,1-1e-12)
    return -(y*np.log(p)+(1-y)*np.log1p(-p)),p

def last_rows(f,trials,ch):
    groups=f["groups"];mask=np.isin(groups,trials)
    if ch.startswith("online"):mask &= f["online_mask"]
    rows=np.flatnonzero(mask)
    return np.array([ix[-1] for tr in np.unique(groups[rows])
                     if len(ix:=rows[groups[rows]==tr])],dtype=int)

def pairs(f,trials,ch):
    mask=np.isin(f["groups"],trials)
    if ch.startswith("online"):mask &= f["online_mask"]
    m=mask[:-1]&mask[1:]&(f["groups"][:-1]==f["groups"][1:])
    a=np.flatnonzero(m);b=a+1
    if np.any(f["bin_index0"][b]-f["bin_index0"][a]!=1):raise AssertionError("Nonadjacent pair")
    return a,b

def analyze(summary):
    fpath=R124/summary["feature_artifact"]["file"]
    if study.sha(fpath)!=summary["feature_artifact"]["sha256"]:raise AssertionError("Feature changed")
    f=np.load(fpath,allow_pickle=False);stem=Path(summary["source_mat"]).stem
    mp=R124/(stem+"_models.json.gz");pp=R124/(stem+"_predictions.csv.gz")
    for p in (mp,pp):
        artifact=next(a for a in summary["artifacts"] if a["file"]==p.name)
        if study.sha(p)!=artifact["sha256"]:raise AssertionError("Frozen map/prediction changed")
    with gzip.open(mp,"rt") as g:outer_maps=json.load(g)
    oof=pd.read_csv(pp);unitids=list(f["unit_ids"]);n=len(f["y"])
    errors={};output={};audit=[];transition_rows=[];output_rows=[]
    for ch in CHANNELS:
        for reg in ("FOF","ADS"):
            key=(ch,reg)
            errors[key]={k:[] for k in ("unit_accumulator","persistence","recent_reset","training_constant","free_arx")}
            errors[key].update(external_fixed=[],external_recent=[],state_next=[])
            output[key]={k:[] for k in ("choice","external","neural","prior")}
    max_replay_error=0;zero_maps={k:0 for k in errors}
    for outer in outer_maps:
        fold=outer["outer"];record={"outer":fold,"maps":{}}
        for ch in CHANNELS:
            ia,ib=pairs(f,outer["train_trials"],ch);ta,tb=pairs(f,outer["test_trials"],ch)
            lasttrain=last_rows(f,outer["train_trials"],ch);lasttest=last_rows(f,outer["test_trials"],ch)
            beta,optimization=output_law(f["y"][lasttrain],f["choice"][lasttrain])
            prior=float(np.clip(np.mean(f["choice"][lasttrain]),1e-12,1-1e-12))
            for reg in ("FOF","ADS"):
                ix=[unitids.index(v) for v in outer["selected_unit_ids"][reg]]
                m=outer["models"][f"{ch}__{reg}__neural"]
                model={k:np.asarray(m[k]) for k in ("beta","gamma","scale","coefs")}
                state=study.predict(model,np.ones((n,1)),f[ch][:,ix])
                testmask=np.isin(f["groups"],outer["test_trials"])
                if ch.startswith("online"):testmask &= f["online_mask"]
                col=f"{ch}__{reg}__neural"
                err=float(np.max(np.abs(state[testmask]-oof.loc[testmask,col].to_numpy())))
                max_replay_error=max(max_replay_error,err)
                if err>1e-8:raise AssertionError("OOF map replay mismatch")
                key=(ch,reg);zero_maps[key]+=int(np.max(np.abs(model["coefs"]))<1e-12)
                u=f["recent"][tb];zt,zn=state[ta],state[tb]
                train_design=np.column_stack([np.ones(len(ia)),state[ia],f["recent"][ib]])
                arx=np.linalg.lstsq(train_design,state[ib],rcond=None)[0]
                mean=float(np.mean(state[ib]))
                candidates={"unit_accumulator":zt+u,"persistence":zt,"recent_reset":u,
                    "training_constant":np.full(len(tb),mean),
                    "free_arx":np.column_stack([np.ones(len(ta)),zt,u])@arx}
                for k,pred in candidates.items():errors[key][k].extend((zn-pred)**2)
                errors[key]["external_fixed"].extend((f["y"][tb]-(zt+u))**2)
                errors[key]["external_recent"].extend((f["y"][tb]-u)**2)
                errors[key]["state_next"].extend(zn)
                if not np.array_equal(f["y"][ta]+u,f["y"][tb]):raise AssertionError("External input identity failed")
                yc=f["choice"][lasttest];ae=f["y"][lasttest];az=state[lasttest]
                le,pe=losses(ae,yc,beta);lz,pz=losses(az,yc,beta)
                lp=-(yc*np.log(prior)+(1-yc)*np.log1p(-prior))
                output[key]["external"].extend(le);output[key]["neural"].extend(lz)
                output[key]["prior"].extend(lp);output[key]["choice"].extend(yc)
                for j,idx in enumerate(tb):
                    transition_rows.append({"rat":summary["rat"],"session":summary["session"],"outer":fold,
                        "channel":ch,"region":reg,"trial_id":f["trial_ids"][f["groups"][idx]],
                        "next_bin_index0":f["bin_index0"][idx],"state_current":zt[j],
                        "state_next":zn[j],"input_next":u[j],
                        **{k:pred[j] for k,pred in candidates.items()},
                        "external_evidence_next":f["y"][idx]})
                for j,idx in enumerate(lasttest):
                    output_rows.append({"rat":summary["rat"],"session":summary["session"],"outer":fold,
                        "channel":ch,"region":reg,"trial_id":f["trial_ids"][f["groups"][idx]],
                        "choice":yc[j],"last_target_time_s":f["time_s"][idx],
                        "external_evidence":ae[j],"neural_state":az[j],
                        "external_probability":pe[j],"transported_probability":pz[j],"prior":prior})
                record["maps"][ch+"__"+reg]={"n_transition_train":len(ia),"n_transition_test":len(ta),
                    "ARX_intercept_state_gain_input_gain":arx,"observed_training_constant":mean,
                    "shared_output_intercept_slope":beta,"output_optimizer":optimization,
                    "n_output_train_trials":len(lasttrain),"n_output_test_trials":len(lasttest)}
        audit.append(record)
    rows=[]
    for key,values in errors.items():
        ch,reg=key;mse={k:float(np.mean(v)) for k,v in values.items() if k!="state_next"}
        out={k:float(np.mean(v)) for k,v in output[key].items() if k!="choice"}
        rows.append({"rat":summary["rat"],"session":summary["session"],"channel":ch,"region":reg,
            "n_transitions":len(values["state_next"]),"n_output_trials":len(output[key]["choice"]),
            "state_next_variance":float(np.var(values["state_next"])),
            "observed_accumulator_mse":mse["unit_accumulator"],
            "observed_persistence_mse":mse["persistence"],"observed_reset_mse":mse["recent_reset"],
            "observed_constant_mse":mse["training_constant"],"observed_ARX_mse":mse["free_arx"],
            "accumulator_minus_persistence_mse":mse["unit_accumulator"]-mse["persistence"],
            "external_fixed_mse":mse["external_fixed"],"external_recent_mse":mse["external_recent"],
            "external_mse_gain_vs_recent":mse["external_recent"]-mse["external_fixed"],
            "output_external_logloss":out["external"],"output_transported_logloss":out["neural"],
            "output_prior_logloss":out["prior"],
            "output_transport_minus_external_logloss":out["neural"]-out["external"],
            "zero_state_outer_folds":zero_maps[key]})
    pd.DataFrame(transition_rows).to_csv(HERE/(stem+"_transitions.csv.gz"),index=False,
                                        compression={"method":"gzip","mtime":0})
    pd.DataFrame(output_rows).to_csv(HERE/(stem+"_outputs.csv.gz"),index=False,
                                    compression={"method":"gzip","mtime":0})
    study.write_gz_json(HERE/(stem+"_calibration.json.gz"),audit)
    report={"source_summary":summary["source_mat"],"source_sha256":summary["source_sha256"],
            "max_OOF_replay_error":max_replay_error,"metrics":rows,
            "external_identity_is_coordinate_sanity_only":True,"C2_PASS":False,"C3_tested":False}
    study.write_json(HERE/(stem+"_summary.json"),report)
    return rows,max_replay_error

def main():
    start=time.monotonic();allrows=[];replays=[]
    manifest=json.loads((study.R122/"R122_Input_Manifest.json").read_text())
    study.write_json(HERE/"run_manifest.json",{"started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
     "protocol_sha256":study.sha(HERE/"PROTOCOL_FROZEN.md"),"code_sha256":study.sha(__file__),
     "new_decoders_fitted":False,"data_type":"real frozen R124 neural features and maps"})
    for exp in manifest["sessions"]:
        summary=json.loads((R124/(Path(exp["file"]).stem+"_summary.json")).read_text())
        if summary["source_sha256"]!=exp["sha256"]:raise AssertionError("Source identity changed")
        rows,replay=analyze(summary);allrows.extend(rows);replays.append(replay)
        print(json.dumps({"event":"session_complete","file":exp["file"],"replay_error":replay}),flush=True)
    frame=pd.DataFrame(allrows);frame.to_csv(HERE/"session_metrics.csv",index=False)
    keys=["channel","region"];measure=[c for c in frame.columns if c not in keys+["rat","session","n_transitions","n_output_trials","zero_state_outer_folds"]]
    rats=frame.groupby(keys+["rat"])[measure].mean().reset_index()
    rats.to_csv(HERE/"rat_metrics.csv",index=False)
    aggregate=[]
    for key,d in rats.groupby(keys):
        sessions=frame.loc[(frame.channel==key[0])&(frame.region==key[1])]
        aggregate.append({"channel":key[0],"region":key[1],"n_rats":len(d),
          "equal_rat":{m:float(d[m].mean()) for m in measure},
          "rats_accumulator_worse_than_persistence":int((d.accumulator_minus_persistence_mse>0).sum()),
          "sessions_accumulator_worse_than_persistence":int((sessions.accumulator_minus_persistence_mse>0).sum()),
          "rats_transported_output_worse_than_external":int((d.output_transport_minus_external_logloss>0).sum()),
          "rat_records":d.to_dict("records")})
    study.write_json(HERE/"aggregate.json",{"status":"COMPUTED","n_sessions":12,"n_rats":5,
        "n_raw_primary_transitions":int(frame.loc[(frame.channel=="online_raw")&(frame.region=="FOF"),"n_transitions"].sum()),
        "n_raw_primary_output_trials":int(frame.loc[(frame.channel=="online_raw")&(frame.region=="FOF"),"n_output_trials"].sum()),
        "max_OOF_replay_error":max(replays),"contrasts":aggregate,"elapsed_seconds":time.monotonic()-start,
        "C2":"UNCERTAIN: observable candidate audited, biological kernel not identified",
        "C3":"NOT_TESTED: no matched internal interventions","E_measured":False})
    print(json.dumps({"event":"finished","sessions":12,"max_replay_error":max(replays),
                      "seconds":time.monotonic()-start}),flush=True)

if __name__=="__main__":main()

