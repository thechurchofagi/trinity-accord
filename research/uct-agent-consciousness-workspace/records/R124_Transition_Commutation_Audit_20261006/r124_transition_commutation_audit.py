#!/usr/bin/env python3
"""R124 reproducibility script for the transition-commutation audit.

Reads existing R122 out-of-fold prediction CSV.GZ files only.
It does not refit neural data or claim the decoded coordinate is a complete
biological state. The primary mapping is allowed to fail.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
B2 = HERE.parent / "R122_Biology_B1_B2_20261006" / "b2_results"
FILES = sorted(B2.glob("*_B2_predictions.csv.gz"))

def corr(x, y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    if len(x)<2 or np.std(x)==0 or np.std(y)==0:
        return float("nan")
    return float(np.corrcoef(x,y)[0,1])

def metric(df, col):
    y=df["dy"].to_numpy(float)
    p=df[col].to_numpy(float)
    persistence=np.mean(y*y)
    mse=np.mean((p-y)**2)
    nz=y!=0
    return {
        "n":int(len(df)),
        "persistence_mse":float(persistence),
        "transition_mse":float(mse),
        "skill_vs_persistence":float(1-mse/persistence),
        "corr":corr(p,y),
        "nonzero_increment_n":int(nz.sum()),
        "sign_accuracy":float(np.mean(np.sign(p[nz])==np.sign(y[nz]))),
    }

def main():
    assert len(FILES)==12, f"expected 12 R122 OOF files, found {len(FILES)}"
    use=["trial_id","rat","session_id","bin_index0","cumulative_click_difference",
         "prediction_FOF","prediction_ADS",
         "prediction_choice_time_nuisance",
         "prediction_choice_time_recent_evidence"]
    rows=pd.concat([pd.read_csv(p,usecols=use) for p in FILES],ignore_index=True)
    assert len(rows)==32656
    pairs=[]
    # Adjacent bins are formed inside each source trial only.
    for tid,g in rows.groupby("trial_id",sort=False):
        g=g.sort_values("bin_index0")
        a=g.iloc[:-1].reset_index(drop=True)
        b=g.iloc[1:].reset_index(drop=True)
        keep=(b.bin_index0.to_numpy()==a.bin_index0.to_numpy()+1)
        for i in np.flatnonzero(keep):
            pairs.append({
                "rat":a.rat.iloc[i],"session_id":a.session_id.iloc[i],
                "dy":b.cumulative_click_difference.iloc[i]-a.cumulative_click_difference.iloc[i],
                "dFOF":b.prediction_FOF.iloc[i]-a.prediction_FOF.iloc[i],
                "dADS":b.prediction_ADS.iloc[i]-a.prediction_ADS.iloc[i],
                "dnuis":b.prediction_choice_time_nuisance.iloc[i]-a.prediction_choice_time_nuisance.iloc[i],
                "drecent":b.prediction_choice_time_recent_evidence.iloc[i]-a.prediction_choice_time_recent_evidence.iloc[i],
            })
    d=pd.DataFrame(pairs)
    assert len(d)==29337
    rats=sorted(d.rat.unique())
    out={"n_rows":len(rows),"n_transitions":len(d),"rats":rats,"regions":{}}
    for key in ["FOF","ADS","nuis","recent"]:
        per={r:metric(d[d.rat==r],"d"+key) for r in rats}
        out["regions"][key]={
            "per_rat":per,
            "equal_rat_mean_skill":float(np.mean([per[r]["skill_vs_persistence"] for r in rats])),
            "equal_rat_mean_corr":float(np.mean([per[r]["corr"] for r in rats])),
            "equal_rat_mean_sign_accuracy":float(np.mean([per[r]["sign_accuracy"] for r in rats])),
            "pooled":metric(d,"d"+key),
        }

    # Frozen sensitivity scan: d_pred[i] vs d_true[i+lag], -6..+6 bins.
    scans={}
    # Re-form sequences to avoid crossing trial boundaries.
    for key in ["FOF","ADS","recent"]:
        scans[key]=[]
        for lag in range(-6,7):
            byrat=[]
            for rat in rats:
                xx=[]; yy=[]
                for tid,g in rows[rows.rat==rat].groupby("trial_id",sort=False):
                    g=g.sort_values("bin_index0").reset_index(drop=True)
                    val=g["prediction_"+({"FOF":"FOF","ADS":"ADS","recent":"choice_time_recent_evidence"}[key])].to_numpy(float)
                    y=g.cumulative_click_difference.to_numpy(float)
                    bins=g.bin_index0.to_numpy(int)
                    ok=(bins[1:]==bins[:-1]+1)
                    dp=np.diff(val)[ok]; dy=np.diff(y)[ok]
                    for i,p in enumerate(dp):
                        j=i+lag
                        if 0<=j<len(dy):
                            xx.append(p); yy.append(dy[j])
                byrat.append(corr(xx,yy))
            scans[key].append({"lag_bins":lag,"lag_ms":50*lag,
                               "equal_rat_corr":float(np.mean(byrat)),
                               "by_rat":dict(zip(rats,byrat))})
    out["lag_scan"]=scans
    (HERE/"R124_transition_reproduction.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
