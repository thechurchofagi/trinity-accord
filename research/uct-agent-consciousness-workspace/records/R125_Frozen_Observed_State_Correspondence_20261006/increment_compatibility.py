"""Secondary harmonization with the concurrently committed R124 increment audit."""
from pathlib import Path
import json,gzip
import numpy as np,pandas as pd
import state_correspondence as current
H=Path(__file__).resolve().parent
rows=[]
for path in sorted(H.glob("*_transitions.csv.gz")):
    f=pd.read_csv(path)
    for (ch,reg),g in f.groupby(["channel","region"]):
        u=g.input_next.to_numpy();dz=g.state_next.to_numpy()-g.state_current.to_numpy()
        denom=float(np.mean(u*u));defect=float(np.mean((dz-u)**2))
        rows.append({"rat":g.rat.iloc[0],"session":str(g.session.iloc[0]),"channel":ch,"region":reg,
             "n_pairs":len(g),"input_increment_mse_vs_zero":denom,
             "commutation_defect_mse":defect,"increment_skill_vs_zero":1-defect/denom,
             "increment_correlation":float(np.corrcoef(u,dz)[0,1]) if np.std(dz)>0 else None})
frame=pd.DataFrame(rows);frame.to_csv(H/"increment_compatibility_session_metrics.csv",index=False)
rats=frame.groupby(["channel","region","rat"])[["increment_skill_vs_zero","increment_correlation"]].mean().reset_index()
rats.to_csv(H/"increment_compatibility_rat_metrics.csv",index=False)
out=[]
for (ch,reg),g in rats.groupby(["channel","region"]):
    d=frame.loc[(frame.channel==ch)&(frame.region==reg)]
    out.append({"channel":ch,"region":reg,"equal_rat_skill":float(g.increment_skill_vs_zero.mean()),
      "equal_rat_correlation":float(g.increment_correlation.mean()),"rats_positive_skill":int((g.increment_skill_vs_zero>0).sum()),
      "sessions_positive_skill":int((d.increment_skill_vs_zero>0).sum()),"rat_records":g.to_dict("records")})
current.study.write_json(H/"increment_compatibility.json",{"status":"COMPUTED","scope":"secondary metric harmonization after concurrent R124 was read; no new decoder or map",
 "concurrent_commit":"f2f34ca5f5a9738659780729c8a7e8aefe01dbf3",
 "denominator":"E[(actual signed input increment)^2], matching R124; distinct from observed-state persistence error",
 "n_sessions":12,"n_rats":5,"primary_pairs":int(frame.loc[(frame.channel=='online_raw')&(frame.region=='FOF'),'n_pairs'].sum()),
 "results":out,"C2_scope":"candidate point-map increment criterion only; latent biological kernel remains unidentified"})
print(json.dumps({"status":"COMPUTED","results":[{k:v for k,v in x.items() if k!='rat_records'} for x in out]}))

