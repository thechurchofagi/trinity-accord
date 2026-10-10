"""Exploratory exact-fit distances and explicitly hypothetical error budgets."""
from pathlib import Path
from itertools import permutations
from datetime import datetime,timezone
import json
import numpy as np
import pandas as pd
from scipy.stats import norm

BASE=Path(__file__).resolve().parent
OUT=BASE/'results'
amendment={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
 'status':'post-plan theory-directed exploratory extension, not prospectively registered',
 'monotone_distance':'Minimum across six frequency orders of half the largest positive inversion in either task log-width sequence',
 'budgets':'Hypothetical centered Gaussian log-error SD grid; neither the SD nor centered errors are established by these public source data',
 'no_individual_mechanism_certification':True}
(OUT/'exploratory_calibration_plan.json').write_text(json.dumps(amendment,indent=2))
raw=pd.read_excel(BASE/'Experiment_3.xlsx',header=None)
lw=np.log(raw.iloc[3:,63:69].to_numpy(dtype=float).reshape(30,2,3))
freqs=['8Hz','sham','13Hz']
rows=[]
for i,l in enumerate(lw):
    gap=l[0]-l[1];epsclock=np.ptp(gap)/4
    candidates=[]
    for perm in permutations(range(3)):
        z=l[:,perm]
        inv=max(0,max(float(z[t,a]-z[t,b]) for t in range(2) for a in range(3) for b in range(a+1,3)))
        candidates.append((inv/2,perm))
    epsmono,perm=min(candidates)
    assert epsmono<=epsclock+1e-12
    rows.append({'participant':i+1,'epsilon_clock_log':float(epsclock),'epsilon_monotone_log':float(epsmono),
                 'clock_upward_tolerance_percent':float(100*np.expm1(epsclock)),
                 'monotone_upward_tolerance_percent':float(100*np.expm1(epsmono)),
                 'monotone_optimal_weak_order':','.join(freqs[x] for x in perm),
                 'note':'Distances for released point estimates, not confidence bounds on true values'})
df=pd.DataFrame(rows);df.to_csv(OUT/'individual_clock_and_monotone_distances.csv',index=False)
budget=[]
for scope,m in [('one_participant_six_cells',6),('all_30_participants_180_cells',180)]:
    for method in ['independent_exact_gaussian_max','bonferroni_gaussian_marginals']:
        q=norm.ppf((1+.95**(1/m))/2) if method.startswith('independent') else norm.ppf(1-.05/(2*m))
        for sigma in [.0025,.005,.0075,.01,.015,.02,.025,.03,.04,.05,.075,.1]:
            eps=q*sigma
            budget.append({'hypothetical_log_error_sd':sigma,'coverage':.95,'scope':scope,
                 'method':method,'error_multiplier_quantile':float(q),'epsilon_log_bound':float(eps),
                 'error_upper_percent':float(100*np.expm1(eps)),'error_lower_percent':float(100*(1-np.exp(-eps))),
                 'clock_point_estimate_distance_exceeds_budget_n':int((df.epsilon_clock_log>eps).sum()),
                 'monotone_point_estimate_distance_exceeds_budget_n':int((df.epsilon_monotone_log>eps).sum()),
                 'measured_calibration_available':False,
                 'interpretation':'Conditional sensitivity only; no valid empirical rejection without independent error calibration'})
pd.DataFrame(budget).to_csv(OUT/'hypothetical_lognormal_calibration_budgets.csv',index=False)
res={'epsilon_monotone_positive_count':int((df.epsilon_monotone_log>0).sum()),
 'epsilon_monotone_log_max':float(df.epsilon_monotone_log.max()),
 'monotone_upward_tolerance_percent_max':float(df.monotone_upward_tolerance_percent.max()),
 'clock_upward_tolerance_percent_median':float(df.clock_upward_tolerance_percent.median()),
 'monotone_nonzero_rows':df.loc[df.epsilon_monotone_log>0].to_dict('records'),
 'error_budgets_not_calibrated_from_data':True}
(OUT/'calibration_budget_summary.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
