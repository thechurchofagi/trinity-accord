"""Reconstruct a lost OOF prediction artifact from frozen maps; do not refit."""
from pathlib import Path
import json,gzip
import numpy as np,pandas as pd
import joint_decode as study
H=Path(__file__).resolve().parent
stem="X087_2021_07_25_g0_t0.imec0.ap_res.Cells"
sfile=H/(stem+"_summary.json");s=json.loads(sfile.read_text())
a=s["artifacts"][0];path=H/a["file"]
rejected={"file":path.name,"expected_sha256":a["sha256"],"expected_bytes":a["bytes"],
          "observed_bytes":path.stat().st_size,"observed_sha256":study.sha(path)}
f=np.load(H/s["feature_artifact"]["file"],allow_pickle=False)
with gzip.open(H/(stem+"_models.json.gz"),"rt") as g:models=json.load(g)
t=f["time_s"];r=f["recent"];choice=f["choice"];duration=f["duration"];n=len(t)
B={"retrospective":np.column_stack([np.ones(n),choice,t,t*t,choice*t,choice*t*t,duration]),
   "retrospective_recent":np.column_stack([np.ones(n),choice,t,t*t,choice*t,choice*t*t,duration,r]),
   "online_recent":np.column_stack([np.ones(n),t,t*t,r,r*t,r*t*t,f["total_recent"]])}
columns={};groups=f["groups"];fold=np.full(n,-1,int)
for ch,ctx in study.CONDITIONS:
    key=f"{ch}__{ctx}";columns[key+"__baseline"]=np.full(n,np.nan)
    for reg in ("FOF","ADS"):
        columns[key+"__"+reg+"__joint"]=np.full(n,np.nan)
        columns[ch+"__"+reg+"__neural"]=np.full(n,np.nan)
unit_ids=list(f["unit_ids"])
for outer in models:
    common=np.isin(groups,outer["test_trials"]);fold[common]=outer["outer"]
    ix={reg:[unit_ids.index(v) for v in ids] for reg,ids in outer["selected_unit_ids"].items()}
    for key,m in outer["models"].items():
        parts=key.split("__");ch=parts[0]
        mask=common.copy()
        if ch.startswith("online"):mask &= f["online_mask"]
        if parts[-1]=="neural":reg=parts[1];base=np.ones((n,1))
        else:
            ctx,reg=parts[1:3];base=B[ctx]
            columns[f"{ch}__{ctx}__baseline"][mask]=base[mask]@np.asarray(m["beta"])
        model={k:np.asarray(m[k]) for k in ("beta","gamma","scale","coefs")}
        X=f[ch][:,ix[reg]]
        columns[key][mask]=study.predict(model,base[mask],X[mask])
errors=[]
for row in s["metrics"]:
    ch,ctx,reg=row["channel"],row["context"],row["region"]
    mask=f["online_mask"] if ch.startswith("online") else np.ones(n,bool)
    for field,key in (("baseline_r2",f"{ch}__{ctx}__baseline"),
                      ("neural_r2",f"{ch}__{reg}__neural"),
                      ("joint_r2",f"{ch}__{ctx}__{reg}__joint")):
        actual=study.metric(f["y"][mask],columns[key][mask])["r2"]
        errors.append(abs(actual-row[field]))
if max(errors)>2e-10:raise AssertionError("Reconstructed metrics disagree")
pred=pd.DataFrame({"rat":s["rat"],"session":s["session"],
 "trial_id":f["trial_ids"][groups],"source_row1":f["source_row1"][groups],
 "outer_fold":fold,"bin_index0":f["bin_index0"],"target_time_s":t,
 "y":f["y"],"online_valid":f["online_mask"],**columns})
pred.to_csv(path,index=False,compression={"method":"gzip","mtime":0})
a["sha256"]=study.sha(path);a["bytes"]=path.stat().st_size
study.write_json(sfile,s)
study.write_json(H/"prediction_repair.json",{"rejected":rejected,
 "repair":"reconstructed solely from already-saved features, selected neurons and frozen coefficients",
 "refitted_models":False,"max_saved_R2_discrepancy":max(errors),"repaired_artifact":a})
manifest=json.loads((study.R122/"R122_Input_Manifest.json").read_text())
summaries=[]
for exp in manifest["sessions"]:
    v=json.loads((H/(Path(exp["file"]).stem+"_summary.json")).read_text())
    if v["source_sha256"]!=exp["sha256"]:raise AssertionError("Source provenance changed")
    for a in [v["feature_artifact"]]+v["artifacts"]:
        if study.sha(H/a["file"])!=a["sha256"]:raise AssertionError("Artifact changed: "+a["file"])
    summaries.append(v)
result=study.aggregate(summaries,H)
assert (result["n_sessions"],result["n_rats"],result["n_trials"],result["n_bins"])==(12,5,3319,32656)
repair=json.loads((H/"single_session_repair.json").read_text())
repair.update(repair_status="VERIFIED_AND_ANALYZED",all_twelve_artifact_digests_checked=True,
              final_cohort=[12,5,3319,32656],repaired_sha256=manifest["sessions"][7]["sha256"])
study.write_json(H/"single_session_repair.json",repair)
print(json.dumps({"status":"PASS","prediction_max_R2_discrepancy":max(errors),
 "sessions":12,"trials":3319,"bins":32656,"all_twelve_saved_artifacts_verified":True}))

