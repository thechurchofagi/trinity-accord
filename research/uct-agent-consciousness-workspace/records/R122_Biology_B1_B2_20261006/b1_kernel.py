"""R122 independent rat psychophysical temporal kernel, not an author replication.

Execute only after reading R122_B1_Frozen_Protocol.md. Inputs are the 12 genuine
Gupta et al. 2026 MATLAB sessions; no synthetic trials or experiential labels.
"""
from __future__ import annotations

import argparse
import json
import platform
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.stats import t as student_t
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.preprocessing import StandardScaler

from rat_cells import load_session, save_trial_table, file_sha256, jsonable

N_BINS = 10
N_FOLDS = 5
C_FIXED = 1.0
MODELS = ("full10", "lastbin", "total", "nuisance")
NUISANCE = ("duration_s", "previous_rewarded_choice", "previous_error_choice", "previous_history_missing")


def evidence_matrix(df: pd.DataFrame, n_bins: int = N_BINS) -> np.ndarray:
    matrix = []
    for row in df.itertuples():
        edges = np.linspace(0, row.duration_s, n_bins+1)
        left = np.histogram(row.left_clicks_s, edges)[0]
        right = np.histogram(row.right_clicks_s, edges)[0]
        if left.sum() != row.n_left or right.sum() != row.n_right:
            raise ValueError(f"Click conservation failed: {row.trial_id}")
        matrix.append(right-left)
    return np.asarray(matrix, dtype=float)


def design(evidence: np.ndarray, df: pd.DataFrame, model: str) -> tuple[np.ndarray, list[str]]:
    nuisance = df.loc[:, NUISANCE].to_numpy(dtype=float)
    if model == "full10":
        x, names = evidence, [f"e{i+1}" for i in range(N_BINS)]
    elif model == "lastbin":
        x, names = evidence[:, -1:], ["e10"]
    elif model == "total":
        x, names = evidence.sum(axis=1, keepdims=True), ["total_evidence"]
    elif model == "nuisance":
        x, names = np.empty((len(df), 0)), []
    else:
        raise ValueError(model)
    return np.column_stack([x, nuisance]), names + list(NUISANCE)


def fit_logistic(x: np.ndarray, y: np.ndarray):
    if not np.all(np.isfinite(x)) or not np.all(np.isin(y, [0, 1])):
        raise ValueError("Nonfinite predictor or nonbinary observed choice")
    if len(np.unique(y)) < 2:
        raise ValueError("Training choices contain only one class")
    scaler = StandardScaler().fit(x)
    # l1_ratio=0 is the sklearn>=1.8 nondeprecated L2 interface.
    mdl = LogisticRegression(C=C_FIXED, l1_ratio=0.0, solver="lbfgs", tol=1e-8, max_iter=2000)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        mdl.fit(scaler.transform(x), y)
    problems = [str(w.message) for w in caught if issubclass(w.category, ConvergenceWarning)]
    if problems:
        raise RuntimeError("; ".join(problems))
    return scaler, mdl


def model_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    good = np.isfinite(p)
    if not good.any():
        return {"n_oof": 0, "log_loss": None, "brier": None, "accuracy": None}
    return {"n_oof": int(good.sum()), "log_loss": float(log_loss(y[good], p[good], labels=[0,1])), "brier": float(brier_score_loss(y[good], p[good])), "accuracy": float(accuracy_score(y[good], p[good] >= 0.5))}


def individual_loss(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-15, 1-1e-15)
    return -(y*np.log(p)+(1-y)*np.log1p(-p))


def mean_interval(values: list | np.ndarray) -> dict:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return {"n": 0, "mean": None, "sd": None, "descriptive_t95": None}
    m = float(x.mean())
    sd = float(x.std(ddof=1)) if len(x)>1 else None
    width = float(student_t.ppf(0.975, len(x)-1)*sd/np.sqrt(len(x))) if len(x)>1 else None
    return {"n": len(x), "mean": m, "sd": sd, "descriptive_t95": [m-width,m+width] if width is not None else None}


def run_session(session, output: Path) -> dict:
    df = session.trials.loc[session.trials.eligible].copy().reset_index(drop=True)
    if len(df) < 25:
        raise ValueError(f"Only {len(df)} eligible trials; five-block fitting not justified")
    y = df.choice.to_numpy(dtype=int)
    evidence = evidence_matrix(df)
    if not np.array_equal(evidence.sum(axis=1), df.delta_clicks.to_numpy()):
        raise ValueError("Trial evidence-total identity failed")
    fold_vector = np.full(len(df), -1, dtype=int)
    partitions = list(np.array_split(np.arange(len(df)), N_FOLDS))
    failures = []
    probabilities = {}
    coefs = {}
    folds = []
    for fold, test in enumerate(partitions):
        fold_vector[test] = fold
        train_mask = np.ones(len(df), dtype=bool)
        train_mask[test] = False
        for idx in (int(test[0])-1, int(test[-1])+1):
            if 0 <= idx < len(df):
                train_mask[idx] = False
        folds.append((np.flatnonzero(train_mask), test))
    for model in MODELS:
        x, names = design(evidence, df, model)
        probs = np.full(len(df), np.nan)
        for fold, (train, test) in enumerate(folds):
            try:
                scaler, mdl = fit_logistic(x[train], y[train])
                probs[test] = mdl.predict_proba(scaler.transform(x[test]))[:,1]
            except Exception as exc:
                failures.append({"model":model,"fold":fold,"error_type":type(exc).__name__,"error":str(exc),"n_train":len(train),"n_test":len(test)})
        probabilities[model] = probs
        scaler, mdl = fit_logistic(x, y)
        standard_coef = mdl.coef_[0]
        raw_coef = standard_coef/scaler.scale_
        coefs[model] = {"names":names,"standardized_coefficients":standard_coef.tolist(),"raw_coefficients":raw_coef.tolist(),"raw_intercept":float(mdl.intercept_[0]-np.dot(raw_coef,scaler.mean_)),"feature_means":scaler.mean_.tolist(),"feature_scales":scaler.scale_.tolist(),"design_rank_with_intercept":int(np.linalg.matrix_rank(np.column_stack([np.ones(len(x)), x]))),"design_columns_with_intercept":x.shape[1]+1,"l2_regularized":True,"n_fit_iterations":int(mdl.n_iter_[0])}
    identity = ["trial_id","source_row1","rat","session_id","choice","is_hit","duration_s","delta_clicks","tie"]
    pred = df[identity].copy()
    pred["fold"] = fold_vector
    for i in range(N_BINS):
        pred[f"e{i+1}"] = evidence[:,i]
    for model, p in probabilities.items():
        pred[f"p_right_{model}"] = p
        pred[f"loss_{model}"] = individual_loss(y, p)
    pred["loss_gain_full10_over_lastbin"] = pred.loss_lastbin-pred.loss_full10
    pred["loss_gain_total_over_lastbin"] = pred.loss_lastbin-pred.loss_total
    pred["loss_gain_full10_over_total"] = pred.loss_total-pred.loss_full10
    pred.to_csv(output / f"{session.session_id}_oof_predictions.csv", index=False)
    kernel = pd.DataFrame({"rat":session.rat,"session_id":session.session_id,"bin":np.arange(1,11),"fraction_midpoint":(np.arange(10)+0.5)/10,"raw_coefficient":coefs['full10']['raw_coefficients'][:10],"standardized_coefficient":coefs['full10']['standardized_coefficients'][:10]})
    kernel.to_csv(output / f"{session.session_id}_kernel.csv", index=False)
    nonties = ~df.tie
    return {"rat":session.rat,"session_id":session.session_id,"source_file":session.path.name,"source_sha256":session.source_sha256,"n_raw_trials":len(session.trials),"n_eligible_trials":len(df),"n_ties_kept":int(df.tie.sum()),"nontie_majority_agreement":float(np.mean((df.loc[nonties,"delta_clicks"]>0)==df.loc[nonties,"choice"])) if nonties.any() else None,"source_hit_rate":float(df.is_hit.mean()),"duration_quantiles_s":np.quantile(df.duration_s,[0,.25,.5,.75,1]).tolist(),"models":{m:model_metrics(y, probabilities[m]) for m in MODELS},"paired_loss_gain":{k:float(pred[k].mean()) for k in ("loss_gain_full10_over_lastbin","loss_gain_total_over_lastbin","loss_gain_full10_over_total")},"fit_coefficients":coefs,"folds":[{"fold":i,"n_train":len(train),"n_test":len(test),"test_first_source_row1":int(df.iloc[test[0]].source_row1),"test_last_source_row1":int(df.iloc[test[-1]].source_row1)} for i,(train,test) in enumerate(folds)],"failures":failures}


def timing_sensitivity(sessions: list) -> dict:
    subset = [(s, s.trials.loc[s.trials.eligible & (s.trials.duration_s >= .8)].copy()) for s in sessions]
    total = sum(len(df) for _,df in subset)
    rats = {s.rat for s,df in subset if len(df)}
    result = {"eligible_long_duration_trials":total,"rats_with_long_trials":sorted(rats),"definition":"Four absolute 200ms bins on [0,.8]s plus post-.8 evidence nuisance, only duration>=.8s","session_fits":[],"failures":[]}
    if total < 50 or len(rats)<3:
        result["status"] = "NOT_RUN_PREDECLARED_MINIMUM_SAMPLE_NOT_MET"
        return result
    for s, df in subset:
        if len(df)<20 or df.choice.nunique()<2:
            result["failures"].append({"session_id":s.session_id,"rat":s.rat,"n":len(df),"reason":"fewer_than_20_trials_or_one_choice_class"})
            continue
        features = []
        for row in df.itertuples():
            edges = [0,.2,.4,.6,.8]
            # The histogram includes .8 in the last bin; tail uses strictly >.8.
            left = np.histogram(row.left_clicks_s,edges)[0]
            right = np.histogram(row.right_clicks_s,edges)[0]
            tail = np.sum(row.right_clicks_s>.8)-np.sum(row.left_clicks_s>.8)
            features.append(np.r_[right-left,tail])
        x = np.column_stack([features,df.loc[:,NUISANCE].to_numpy(dtype=float)])
        try:
            scaler, mdl = fit_logistic(x,df.choice.to_numpy(dtype=int))
            result["session_fits"].append({"session_id":s.session_id,"rat":s.rat,"n":len(df),"raw_coefs_first4":(mdl.coef_[0][:4]/scaler.scale_[:4]).tolist(),"tail_raw_coef":float(mdl.coef_[0][4]/scaler.scale_[4])})
        except Exception as exc:
            result["failures"].append({"session_id":s.session_id,"rat":s.rat,"n":len(df),"reason":str(exc)})
    result["status"] = "EXECUTED_DESCRIPTIVE_SENSITIVITY"
    if result["session_fits"]:
        mean_by_rat = {rat:np.mean([r['raw_coefs_first4'] for r in result['session_fits'] if r['rat']==rat],axis=0) for rat in sorted({r['rat'] for r in result['session_fits']})}
        result["equal_rat_raw_kernel"] = [mean_interval([v[k] for v in mean_by_rat.values()]) for k in range(4)]
    return result


def aggregate(results: list[dict]) -> dict:
    per_rat = []
    for rat in sorted({r["rat"] for r in results}):
        rows = [r for r in results if r["rat"]==rat]
        per_rat.append({"rat":rat,"n_sessions":len(rows),"n_trials":sum(r['n_eligible_trials'] for r in rows),"models":{m:{metric:float(np.mean([r['models'][m][metric] for r in rows])) for metric in ('log_loss','brier','accuracy')} for m in MODELS},"paired_loss_gain":{k:float(np.mean([r['paired_loss_gain'][k] for r in rows])) for k in rows[0]['paired_loss_gain']},"raw_kernel":np.mean([r['fit_coefficients']['full10']['raw_coefficients'][:10] for r in rows],axis=0).tolist(),"standardized_kernel":np.mean([r['fit_coefficients']['full10']['standardized_coefficients'][:10] for r in rows],axis=0).tolist()})
    return {"weighting":"Equal recording sessions within rat; equal rats for final aggregate","independent_unit":"rat; five clusters limit uncertainty calibration","per_rat":per_rat,"models":{m:{metric:mean_interval([r['models'][m][metric] for r in per_rat]) for metric in ('log_loss','brier','accuracy')} for m in MODELS},"paired_loss_gain":{k:mean_interval([r['paired_loss_gain'][k] for r in per_rat]) for k in per_rat[0]['paired_loss_gain']},"raw_kernel":[mean_interval([r['raw_kernel'][k] for r in per_rat]) for k in range(10)],"standardized_kernel":[mean_interval([r['standardized_kernel'][k] for r in per_rat]) for k in range(10)]}


def make_plot(summary: dict, output: Path) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    agg=summary['aggregate']
    fig, axs=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
    colors=['#22577a','#a44a3f','#588157','#8b5e83','#bd8b28']
    t=(np.arange(10)+.5)/10
    for row,c in zip(agg['per_rat'],colors):
        axs[0].plot(t,row['raw_kernel'],color=c,alpha=.7,lw=1,label=row['rat'])
    vals=agg['raw_kernel']; m=np.array([x['mean'] for x in vals]); lo=np.array([x['descriptive_t95'][0] for x in vals]); hi=np.array([x['descriptive_t95'][1] for x in vals])
    axs[0].plot(t,m,color='#182f3d',lw=2.5,label='Equal-rat mean')
    axs[0].fill_between(t,lo,hi,color='#182f3d',alpha=.12)
    axs[0].axhline(0,color='gray',lw=.8)
    axs[0].set(xlabel='Fraction of actual stimulus duration',ylabel='Regularized log-odds coefficient per R−L click',title='Observed temporal evidence weighting')
    axs[0].legend(fontsize=8,ncol=2,frameon=False)
    for j,model in enumerate(MODELS):
        v=agg['models'][model]['log_loss']; ci=v['descriptive_t95']
        axs[1].errorbar(j,v['mean'],yerr=[[v['mean']-ci[0]],[ci[1]-v['mean']]],fmt='o',capsize=4,color='#22577a',ms=7)
        for i,r in enumerate(agg['per_rat']):
            axs[1].scatter(j+(i-2)*.045,r['models'][model]['log_loss'],s=18,color=colors[i],alpha=.8)
    axs[1].set(xticks=range(4),xticklabels=['10 bins','Last bin','Total','Nuisance'],ylabel='Held-out choice log loss (lower is better)',title='Five blocked trial folds per recording')
    for ax in axs:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15)
    fig.suptitle('Rat evidence history predicts choice | R122 B1',fontsize=14,fontweight='bold')
    fig.supxlabel('12 sessions / 5 rats. Bands: descriptive across-rat t intervals. Observational analysis; no experience measurement.',fontsize=8)
    fig.savefig(output/'B1_temporal_kernel.png',dpi=180)
    fig.savefig(output/'B1_temporal_kernel.pdf')
    plt.close(fig)


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    protocol=Path(__file__).with_name('R122_B1_Frozen_Protocol.md')
    if not protocol.exists():
        raise FileNotFoundError('Frozen protocol missing')
    summary={'round':'R122','analysis':'B1 independent psychophysical temporal kernel','started_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':file_sha256(protocol),'code_sha256':file_sha256(Path(__file__)),'loader_sha256':file_sha256(Path(__file__).with_name('rat_cells.py')),'parameters':{'bins':N_BINS,'folds':N_FOLDS,'C_fixed':C_FIXED,'solver':'lbfgs','max_iter':2000,'tolerance':1e-8,'nuisance':NUISANCE,'seed':None,'randomization':'none; deterministic contiguous source-trial blocks'},'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__},'sessions':[],'session_failures':[],'scope_limits':['No author behavioral-kernel replication claimed','No out-of-rat generalization tested','No neural intervention or T2 closure established','AI experience E remains latent','No new AI run in this analysis']}
    (args.out/'run_manifest_start.json').write_text(json.dumps(jsonable(summary),indent=2,allow_nan=False)+'\n')
    sessions=[]
    for path in sorted(args.data.glob('*.mat')):
        try:
            session=load_session(path)
            sessions.append(session)
            sub=args.out/session.session_id
            sub.mkdir(exist_ok=True)
            save_trial_table(session.trials,sub/'all_source_trials.csv')
            (sub/'schema_audit.json').write_text(json.dumps(jsonable(session.audit),indent=2,allow_nan=False)+'\n')
            result=run_session(session,args.out)
            summary['sessions'].append(result)
            print(json.dumps({'session':session.session_id,'rat':session.rat,'raw':len(session.trials),'eligible':result['n_eligible_trials'],'losses':{k:v['log_loss'] for k,v in result['models'].items()},'failures':len(result['failures'])}),flush=True)
        except Exception as exc:
            failure={'file':path.name,'type':type(exc).__name__,'error':str(exc)}
            summary['session_failures'].append(failure)
            print(json.dumps({'FAILURE':failure}),flush=True)
    if summary['sessions']:
        summary['aggregate']=aggregate(summary['sessions'])
        summary['timing_sensitivity']=timing_sensitivity(sessions)
    summary['completed_utc']=datetime.now(timezone.utc).isoformat()
    summary['n_files_loaded']=len(sessions)
    summary['n_sessions_completed']=len(summary['sessions'])
    summary['status']='COMPLETE_12_SESSIONS' if len(summary['sessions'])==12 and not summary['session_failures'] and not any(r['failures'] for r in summary['sessions']) else 'PARTIAL_OR_FAILED_SEE_FAILURE_LEDGER'
    (args.out/'B1_results.json').write_text(json.dumps(jsonable(summary),indent=2,allow_nan=False)+'\n')
    if 'aggregate' in summary:
        make_plot(summary,args.out)
        print(json.dumps({'status':summary['status'],'equal_rat_models':summary['aggregate']['models'],'paired_loss_gain':summary['aggregate']['paired_loss_gain']},indent=2),flush=True)


if __name__=='__main__':
    main()
