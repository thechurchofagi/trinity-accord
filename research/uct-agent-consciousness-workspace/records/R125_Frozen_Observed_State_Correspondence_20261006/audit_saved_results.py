"""Independent lightweight audit of saved real-data predictions; no refitting."""
from pathlib import Path
import json, hashlib, gzip
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
J=HERE.parent/"R124_Observation_Qualified_Neural_Increment_20261006"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def close(a,b):
    if not np.isclose(a,b,rtol=2e-11,atol=2e-11):
        raise AssertionError((a,b))
    return abs(a-b)

def logloss(y,p):
    p=np.clip(p,1e-12,1-1e-12)
    return np.mean(-(y*np.log(p)+(1-y)*np.log1p(-p)))

def main():
    joint_errors=[];state_errors=[];ntrans=ntrial=0
    for p in sorted(J.glob("*_summary.json")):
        s=json.loads(p.read_text());stem=Path(s["source_mat"]).stem
        for a in [s["feature_artifact"]]+s["artifacts"]:
            if sha(J/a["file"])!=a["sha256"]:raise AssertionError(a["file"])
        f=np.load(J/s["feature_artifact"]["file"],allow_pickle=False)
        pred=pd.read_csv(J/(stem+"_predictions.csv.gz"))
        assert len(pred)==len(f["y"])
        with gzip.open(J/(stem+"_models.json.gz"),"rt") as g:models=json.load(g)
        for m in models:
            assert not(set(m["train_trials"])&set(m["test_trials"]))
            assert set(m["train_trials"])|set(m["test_trials"])==set(f["groups"])
        for m in s["metrics"]:
            ch=m["channel"];ct=m["context"];rg=m["region"]
            mask=pred.online_valid.astype(bool) if ch.startswith("online") else np.ones(len(pred),dtype=bool)
            d=pred.loc[mask];v=np.var(d.y)
            for name,col in [("baseline",f"{ch}__{ct}__baseline"),
                             ("joint",f"{ch}__{ct}__{rg}__joint")]:
                mse=np.mean((d.y-d[col])**2)
                joint_errors.append(close(m[name+"_mse"],mse))
                joint_errors.append(close(m[name+"_r2"],1-mse/v))
        assert np.allclose(f["online_raw"]*.05,np.rint(f["online_raw"]*.05))
        ss=json.loads((HERE/(stem+"_summary.json")).read_text())
        tr=pd.read_csv(HERE/(stem+"_transitions.csv.gz"))
        out=pd.read_csv(HERE/(stem+"_outputs.csv.gz"))
        for m in ss["metrics"]:
            a=tr.loc[(tr.channel==m["channel"])&(tr.region==m["region"])]
            o=out.loc[(out.channel==m["channel"])&(out.region==m["region"])]
            assert len(a)==m["n_transitions"] and len(o)==m["n_output_trials"]
            assert not a.duplicated(["outer","trial_id","next_bin_index0"]).any()
            assert not o.duplicated(["outer","trial_id"]).any()
            close(np.max(np.abs(a.unit_accumulator-(a.state_current+a.input_next))),0)
            for k,col in [("accumulator","unit_accumulator"),("persistence","persistence"),
                          ("reset","recent_reset"),("constant","training_constant"),("ARX","free_arx")]:
                state_errors.append(close(m[f"observed_{k}_mse"],np.mean((a.state_next-a[col])**2)))
            for k,col in [("external","external_probability"),("transported","transported_probability"),("prior","prior")]:
                state_errors.append(close(m[f"output_{k}_logloss"],logloss(o.choice,o[col])))
            if m["channel"]=="online_raw" and m["region"]=="FOF":
                ntrans+=len(a);ntrial+=len(o)
    assert (ntrans,ntrial)==(29337,3319)
    r={"status":"PASS","no_refit":True,"all_saved_R124_feature_model_prediction_hashes_pass":True,
       "saved_joint_metric_recalculation_max_error":max(joint_errors),
       "saved_transition_output_metric_recalculation_max_error":max(state_errors),
       "whole_trial_partitions_disjoint":True,"no_duplicate_test_pairs_or_output_trials":True,
       "raw_rates_integer_spike_counts_per_50ms":True,
       "primary_transitions":ntrans,"primary_output_trials":ntrial}
    (HERE/"saved_result_audit.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r))

if __name__=="__main__":main()
