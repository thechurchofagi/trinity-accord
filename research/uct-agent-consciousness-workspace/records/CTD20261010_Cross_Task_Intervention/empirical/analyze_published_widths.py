"""Retrospective secondary analysis of published participant-level TBW parameters.

Raw source workbook stays unchanged. Same-row source TBWs are analyzed as
published; measurement-error uncertainty is unavailable and not imputed from
the separate aggregate-count table, whose Gaussian-refit mapping is unresolved.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from scipy import stats

BASE=Path(__file__).resolve().parent
PLAN=BASE/'analysis_plan.json'
assert PLAN.exists()
out=BASE/'results'
out.mkdir(exist_ok=True)
raw=pd.read_excel(BASE/'Experiment_3.xlsx',header=None)
ids=raw.iloc[3:,0].to_numpy(dtype=int)
counts=raw.iloc[3:,1:43].to_numpy(dtype=float).reshape(30,2,3,7)
widths=raw.iloc[3:,63:69].to_numpy(dtype=float).reshape(30,2,3)
assert list(ids)==list(range(1,31))
assert np.isfinite(counts).all() and ((counts>=0)&(counts<=10)).all()
assert (counts==counts.astype(int)).all()
assert np.isfinite(widths).all() and (widths>0).all()
tasks=['ownership','simultaneity']; freqs=['8Hz','sham','13Hz']
long=[]
for i,p in enumerate(ids):
    for t,task in enumerate(tasks):
        for f,freq in enumerate(freqs):
            long.append({'participant':int(p),'task':task,'stimulation':freq,'TBW_ms':widths[i,t,f],
                         'source_col_zero_based':63+3*t+f,
                         'source_header':raw.iloc[2,63+3*t+f]})
pd.DataFrame(long).to_csv(out/'published_tbw_tidy.csv',index=False)
countlong=[]
for i,p in enumerate(ids):
    for t,task in enumerate(tasks):
        for f,freq in enumerate(freqs):
            for s,async_ms in enumerate([-400,-200,-100,0,100,200,400]):
                countlong.append({'participant':int(p),'task':task,'stimulation':freq,'asynchrony_ms':async_ms,
                                  'yes':int(counts[i,t,f,s]),'n_trials':10})
pd.DataFrame(countlong).to_csv(out/'aggregate_counts_tidy.csv',index=False)

rng=np.random.default_rng(20261010)
def desc(x):
    x=np.asarray(x,dtype=float);n=len(x);se=stats.sem(x);m=x.mean()
    t,p=stats.ttest_1samp(x,0)
    ci=stats.t.interval(.95,n-1,loc=m,scale=se)
    bs=rng.choice(x,(20000,n),replace=True).mean(axis=1)
    w=stats.wilcoxon(x)
    return dict(n=n,mean=float(m),sd=float(x.std(ddof=1)),se=float(se),median=float(np.median(x)),
                t=float(t),df=n-1,p_two_sided=float(p),ci95=list(map(float,ci)),
                bootstrap_mean_ci95=list(map(float,np.quantile(bs,[.025,.975]))),
                wilcoxon_stat=float(w.statistic),wilcoxon_p=float(w.pvalue),
                positive=int((x>0).sum()),negative=int((x<0).sum()))

logw=np.log(widths)
taskgap=logw[:,0,:]-logw[:,1,:]
delta8v13=taskgap[:,0]-taskgap[:,2]
delta8vsham=taskgap[:,0]-taskgap[:,1]
delta13vsham=taskgap[:,2]-taskgap[:,1]
primary=desc(delta8v13)
primary['geometric_ratio_of_gains']=float(np.exp(primary['mean']))
primary['ratio_of_gains_ci95']=list(map(float,np.exp(primary['ci95'])))
primary['tost_sensitivity']={}
for margin in (1.10,1.20,1.30):
    bound=np.log(margin);m=delta8v13.mean();se=stats.sem(delta8v13)
    pleft=stats.t.sf((m+bound)/se,29)
    pright=stats.t.cdf((m-bound)/se,29)
    primary['tost_sensitivity'][str(margin)]={'log_margin':float(bound),'p_tost':float(max(pleft,pright)),
                                           'ci90':list(map(float,stats.t.interval(.90,29,loc=m,scale=se)))}
secondary={'8Hz_vs_sham':desc(delta8vsham),'13Hz_vs_sham':desc(delta13vsham)}
ps=[secondary[k]['p_two_sided'] for k in secondary];order=np.argsort(ps)
adj=np.minimum(1,np.maximum.accumulate([2*ps[order[0]],ps[order[1]]]))
for j,idx in enumerate(order):secondary[list(secondary)[idx]]['p_holm_two_followups']=float(adj[j])

# Added theory-derived diagnostic, explicitly exploratory and not inferential
# evidence that an individual's true width requires a given perturbation.
epsilon=np.ptp(taskgap,axis=1)/4
orders=np.argsort(widths,axis=2)
sameorder=np.all(orders[:,0,:]==orders[:,1,:],axis=1)
individual=[]
for i,p in enumerate(ids):
    individual.append({'participant':int(p),'log_gain_ownership_8v13':float(logw[i,0,0]-logw[i,0,2]),
                       'log_gain_simultaneity_8v13':float(logw[i,1,0]-logw[i,1,2]),
                       'difference_log_gains_8v13':float(delta8v13[i]),
                       'epsilon_min_max_cell_log_perturbation':float(epsilon[i]),
                       'multiplicative_tolerance_percent':float(100*np.expm1(epsilon[i])),
                       'same_stimulation_rank_across_tasks':bool(sameorder[i])})
pd.DataFrame(individual).to_csv(out/'published_tbw_individual_diagnostics.csv',index=False)
summary={
  'analysis_time_utc':datetime.now(timezone.utc).isoformat(),
  'primary_population_mean_necessary_implication':primary,
  'secondary_population_contrasts':secondary,
  'descriptive_source_means_ms':{tasks[t]:{freqs[f]:float(widths[:,t,f].mean()) for f in range(3)} for t in range(2)},
  'theory_diagnostic_exploratory':{
    'formula':'epsilon_i = (max_f(log Wown-log Wsim)-min_f(log Wown-log Wsim))/4',
    'not_a_measurement_error_confidence_interval':True,
    'epsilon_median':float(np.median(epsilon)),
    'tolerance_percent_quantiles':{str(q):float(np.quantile(100*np.expm1(epsilon),q)) for q in [0,.25,.5,.75,1]},
    'same_rank_count':int(sameorder.sum()),'n':30,
    'within_10pct_multiplicative_tolerance_count':int((np.expm1(epsilon)<=.1).sum())},
  'inherited_effect_correlations':{
    'sham_minus_8Hz':stats.pearsonr(widths[:,0,1]-widths[:,0,0],widths[:,1,1]-widths[:,1,0])._asdict(),
    '13Hz_minus_sham':stats.pearsonr(widths[:,0,2]-widths[:,0,1],widths[:,1,2]-widths[:,1,1])._asdict()},
  'source_mapping_warning':'The final three source headers repeat OwnLow/OwnSham/OwnHigh. Values reproduce the published simultaneity means; mapping is preserved in tidy data. Gaussian refits of counts do not uniformly reproduce source widths, so counts are not used to infer errors on these source TBWs.',
  'limits':['Population contrast tests do not establish or refute individual equality by themselves.',
            'No trial-order or block-level records are available. Source fitted-width uncertainty is absent.',
            'The multiplicative width model is a new stronger operational bridge, not a necessary implication of the original BCI common-uncertainty model.']
}
summary['inherited_effect_correlations']={k:{'r':float(v['statistic']),'p':float(v['pvalue'])} for k,v in summary['inherited_effect_correlations'].items()}
(out/'published_widths_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
