#!/usr/bin/env python3
"""Post-hoc R123 robustness/negative-control audit of archived R122 metrics.
No refitting or new biology. Session-region scores are NOT independent rats.
The eventual-choice control is diagnostic, NOT an online implementable agent.
"""
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    here=Path(__file__).resolve().parent
    p=here/'B2_session_metrics.csv'; raw=p.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert blob=='5d398ea4fc530b5418ba84fd133ba6fd03cedba3'
    df=pd.read_csv(p)
    assert len(df)==12 and df.rat.nunique()==5 and df.B2_trials.sum()==3319 and df.rows.sum()==32656
    cols=['FOF_R2','ADS_R2','FOF_r','ADS_r','FOF_wc_r','ADS_wc_r','nuisance_R2','nuisance_recent_R2']
    rat=df.groupby('rat',sort=True)[cols].mean()
    summary={}
    for reg in ('FOF','ADS'):
        per_session=df[f'{reg}_R2']-df.nuisance_R2
        per_rat=rat[f'{reg}_R2']-rat.nuisance_R2
        loo=[]
        for excluded in rat.index:
            kept=rat.drop(excluded)
            loo.append({'excluded_rat':excluded, **{k:float(kept[k].mean()) for k in (f'{reg}_R2',f'{reg}_wc_r')}})
        summary[reg]={'equal_rat_R2':float(rat[f'{reg}_R2'].mean()),
            'negative_session_R2':int((df[f'{reg}_R2']<0).sum()),
            'session_wins_over_choice_time_control':int((per_session>0).sum()),
            'rat_wins_over_choice_time_control':int((per_rat>0).sum()),
            'equal_rat_R2_minus_choice_time_control':float(per_rat.mean()),
            'equal_rat_centered_r':float(rat[f'{reg}_wc_r'].mean()),
            'leave_one_rat_out':loo}
    out={'source_commit':'bf55557992b84f6df4dfc6a924f291dfde7b976b',
         'input_git_blob_sha1':blob,'input_sha256':hashlib.sha256(raw).hexdigest(),
         'n_sessions':12,'n_rats':5,'B2_trials':3319,'heldout_bins':32656,
         'aggregation':'session means within rat; equal rats; post-hoc sensitivity only',
         'rat_means':rat.reset_index().to_dict(orient='records'),
         'equal_rat_choice_time_control_R2':float(rat.nuisance_R2.mean()),
         'equal_rat_choice_time_recent_control_R2':float(rat.nuisance_recent_R2.mean()),
         'region_audit':summary,
         'interpretation_limits':['A standalone neural model losing to a control is not a test of conditional neural increment.',
           'Do not call the eventual-choice baseline an online memoryless accumulator.',
           'Do not subtract R2 values and call the difference conditional information.',
           'Centered correlations are descriptive, not conditional causal effects.',
           'Small N=5, exploratory analyses; no significance or equivalence claim.',
           'No T2 closure or experiential measurement.']}
    out['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (here/'retained_data_audit_results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
