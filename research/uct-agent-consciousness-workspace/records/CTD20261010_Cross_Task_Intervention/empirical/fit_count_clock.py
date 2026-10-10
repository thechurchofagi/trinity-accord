"""Independent aggregate-count sensitivity analysis for a strict Gaussian clock.

This does not reproduce the publication's fitted TBW estimator, and no errors
are transported from these counts to the published-width table.
"""
from pathlib import Path
from datetime import datetime, timezone
import os,json,argparse,time
import numpy as np
from scipy.special import expit,logit,log_expit,xlogy
from scipy.optimize import minimize
from scipy import stats
from concurrent.futures import ProcessPoolExecutor,as_completed
import multiprocessing

BASE=Path(__file__).resolve().parent
X=np.array([-400,-200,-100,0,100,200,400],dtype=float)/400
N=10

def decode(theta,shared):
    amp=expit(theta[:6]).reshape(2,3)
    mu=theta[6:12].reshape(2,3)
    if shared:
        base=theta[12:14]
        gain=np.array([theta[14],0,theta[15]])
        logw=base[:,None]+gain[None,:]
    else:logw=theta[12:18].reshape(2,3)
    width=np.exp(logw)
    z=(X-mu[...,None])/width[...,None]
    logprob=log_expit(theta[:6]).reshape(2,3,1)-.5*z*z
    prob=np.exp(logprob)
    return prob,amp,mu,width,z

def lossgrad(theta,counts,shared):
    p,a,mu,w,z=decode(theta,shared)
    # Compute the Gaussian probability in log space. A probability floor would
    # make the objective flat in extreme tails while retaining nonzero gradients.
    logp=log_expit(theta[:6]).reshape(2,3,1)-.5*z*z
    val=-np.sum(counts*logp+(N-counts)*np.log1p(-p))
    g=(N*p-counts)/(1-p)
    ga=np.sum(g,axis=-1)*(1-a)
    gm=np.sum(g*(X-mu[...,None])/w[...,None]**2,axis=-1)
    gw=np.sum(g*z*z,axis=-1)
    if shared:
        grad=np.concatenate([ga.ravel(),gm.ravel(),gw.sum(axis=1),[gw[:,0].sum(),gw[:,2].sum()]])
    else:grad=np.concatenate([ga.ravel(),gm.ravel(),gw.ravel()])
    return val,grad

def bounds(shared):
    b=[(-6,14)]*6+[(-.75,.75)]*6
    return b+([(-3,2.3)]*2+[(-3,3)]*2 if shared else [(-6,6)]*6)

def alt_to_null(th):
    lw=th[12:].reshape(2,3)
    g=lw.mean(axis=0)-lw[:,1].mean()
    b=(lw-g).mean(axis=1)
    return np.r_[th[:12],np.clip(b,-3,2.3),np.clip(g[[0,2]],-3,3)]

def null_to_alt(th):
    lw=th[12:14,None]+np.array([th[14],0,th[15]])[None,:]
    return np.r_[th[:12],lw.ravel()]

def optimize(th,counts,shared,maxiter=800):
    return minimize(lossgrad,th,args=(counts,shared),jac=True,method='L-BFGS-B',bounds=bounds(shared),
                    options={'maxiter':maxiter,'ftol':1e-11,'gtol':1e-6,'maxls':50})

def fit_one(counts,seednull=None,multi=True):
    # Starts do not use published width estimates.
    ymax=np.clip(counts.max(axis=-1)/N,.1,.995)
    weight=counts+0.01
    mu=np.clip((weight*X).sum(axis=-1)/weight.sum(axis=-1),-.5,.5)
    sd=np.clip(np.sqrt((weight*(X-mu[...,None])**2).sum(axis=-1)/weight.sum(axis=-1)),.12,1.5)
    initial=np.r_[logit(ymax).ravel(),mu.ravel(),np.log(sd).ravel()]
    candidates=[optimize(initial,counts,False)]
    if seednull is not None:candidates.append(optimize(null_to_alt(seednull),counts,False))
    if multi:
        for width in (.25,.6):
            trial=initial.copy();trial[6:12]=0;trial[12:]=np.log(width)
            candidates.append(optimize(trial,counts,False))
    alt=min(candidates,key=lambda r:r.fun)
    ns=[optimize(alt_to_null(alt.x),counts,True)]
    if seednull is not None:ns.append(optimize(seednull,counts,True))
    if multi:
        initialnull=alt_to_null(initial);initialnull[14:]=0
        ns.append(optimize(initialnull,counts,True))
    null=min(ns,key=lambda r:r.fun)
    # Nesting check: make the alternative no worse than the null.
    if alt.fun>null.fun+1e-7:
        alt=optimize(null_to_alt(null.x),counts,False)
    retried=0
    if not null.success:
        retried+=1
        candidate=optimize(null.x,counts,True,maxiter=8000)
        if candidate.fun<=null.fun+1e-8:null=candidate
    if not alt.success:
        retried+=1
        candidate=optimize(alt.x,counts,False,maxiter=8000)
        if candidate.fun<=alt.fun+1e-8:alt=candidate
    return {'null_nll':float(null.fun),'alt_nll':float(alt.fun),'null_theta':null.x,'alt_theta':alt.x,
            'null_converged':bool(null.success),'alt_converged':bool(alt.success),
            'null_message':str(null.message),'alt_message':str(alt.message),
            'null_iterations':int(null.nit),'alt_iterations':int(alt.nit),'numerical_retries':retried}

def bootstrap_one(args):
    index,seed,theta=args
    rng=np.random.default_rng(seed)
    total=0.;conv=0;retries=0;failed=[]
    for subject_index,t in enumerate(theta):
        p=decode(t,True)[0]
        y=rng.binomial(N,p)
        fit=fit_one(y,t,multi=False)
        total+=2*(fit['null_nll']-fit['alt_nll'])
        conv+=fit['null_converged'] and fit['alt_converged']
        retries+=fit['numerical_retries']
        if not (fit['null_converged'] and fit['alt_converged']):
            failed.append({'participant':subject_index+1,'null_message':fit['null_message'],'alt_message':fit['alt_message']})
    return index,total,int(conv),int(retries),failed

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bootstrap',type=int,default=199);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();out=BASE/'results';out.mkdir(exist_ok=True)
    d=np.load(BASE/'alignment_diagnostic.npz');counts=d['counts'].astype(int)
    modelplan={
      'timestamp_utc':datetime.now(timezone.utc).isoformat(),
      'secondary_model':'p_itf(s)=A_itf * exp[-0.5 ((s-mu_itf)/w_itf)^2]',
      'binomial_n':10,'treats_counts_as_independent_conditional_on_model':True,
      'null_width':'log w_itf = baseline_it + frequency_gain_if, gain_isham=0',
      'alternative_width':'six unconstrained log widths per participant',
      'amplitude_and_centers':'free for each participant/task/frequency in both models',
      'null_parameters_per_person':16,'alternative_parameters_per_person':18,
      'aggregate_LRT':'2 sum_i(NLL_null_i-NLL_alternative_i)',
      'bootstrap_replicates':args.bootstrap,'seed':202610101,
      'estimator_warning':'New explicit binomial Gaussian response model, not the source Gaussian least-squares estimator; no uncertainty transferred to source TBW analysis.',
      'bounds_scaled_by_400ms':{'amplitude_logit':[-6,14],'mu':[-.75,.75],'alternative_logw':[-6,6],'null_baseline_logw':[-3,2.3],'null_gains':[-3,3]}}
    (out/'count_model_plan.json').write_text(json.dumps(modelplan,indent=2))
    start=time.time();fits=[]
    for i,y in enumerate(counts):
        fits.append(fit_one(y,multi=True))
        if (i+1)%10==0:print('original fits',i+1,'elapsed_seconds',round(time.time()-start,1),flush=True)
    nulltheta=np.array([f['null_theta'] for f in fits]);alttheta=np.array([f['alt_theta'] for f in fits])
    lrt=2*sum(f['null_nll']-f['alt_nll'] for f in fits)
    pnull=np.array([decode(t,True)[0] for t in nulltheta]);palt=np.array([decode(t,False)[0] for t in alttheta])
    satp=counts/N
    sat_nll=float(-np.sum(xlogy(counts,satp)+xlogy(N-counts,1-satp)))
    nll0=sum(f['null_nll'] for f in fits);nll1=sum(f['alt_nll'] for f in fits)
    res={
      'n_participants':30,'yes_count_cells':1260,'nominal_trials':12600,
      'test_statistic':lrt,'chi_square_reference_df':60,'chi_square_reference_p':float(stats.chi2.sf(lrt,60)),
      'null_nll':nll0,'alternative_nll':nll1,'saturated_nll':sat_nll,
      'null_deviance':2*(nll0-sat_nll),'alternative_deviance':2*(nll1-sat_nll),
      'alternative_deviance_reference_df':720,'alternative_deviance_reference_p':float(stats.chi2.sf(2*(nll1-sat_nll),720)),
      'all_original_converged':all(f['null_converged'] and f['alt_converged'] for f in fits),
      'original_fit_status':[{k:v for k,v in f.items() if not k.endswith('theta')} for f in fits],
      'new_model_mean_widths_ms':(np.exp(alttheta[:,12:].reshape(30,2,3))*400).mean(axis=0).tolist(),
      'limitations':modelplan['estimator_warning']+' Binomial independence and Gaussian shape are assumptions. This tests a strict operational width constraint, not a general common cause or the original BCI model.'}
    np.savez(out/'count_model_fits.npz',nulltheta=nulltheta,alttheta=alttheta,pnull=pnull,palt=palt,counts=counts)
    (out/'count_model_summary.json').write_text(json.dumps(res,indent=2));print('ORIGINAL',json.dumps({k:v for k,v in res.items() if k!='original_fit_status'}),flush=True)
    if args.bootstrap:
        seedseq=np.random.SeedSequence(202610101).spawn(args.bootstrap)
        jobs=[(j,int(s.generate_state(1)[0]),nulltheta) for j,s in enumerate(seedseq)]
        boot=np.full(args.bootstrap,np.nan);convs=np.zeros(args.bootstrap,dtype=int);retries=np.zeros(args.bootstrap,dtype=int);failed=[]
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as ex:
            futures=[ex.submit(bootstrap_one,j) for j in jobs]
            for c,f in enumerate(as_completed(futures),1):
                j,t,conv,retry,failure=f.result();boot[j]=t;convs[j]=conv;retries[j]=retry
                if failure:failed.append({'replicate':j,'details':failure})
                if c%10==0:
                    print('bootstrap',c,'/',args.bootstrap,'elapsed_seconds',round(time.time()-start,1),flush=True)
                    np.savez(out/'count_model_bootstrap_progress.npz',lrt=boot,converged=convs)
        exceed=int((boot>=lrt).sum());p=(1+exceed)/(1+args.bootstrap)
        ci=stats.binomtest(exceed,args.bootstrap).proportion_ci(confidence_level=.95,method='exact')
        res['parametric_bootstrap']={'B':args.bootstrap,'exceedances':exceed,'p_plus_one':p,
          'binomial_tail_MC_ci95':[float(ci.low),float(ci.high)],'all_fits_converged':bool((convs==30).all()),
          'converged_subject_fit_pairs':int(convs.sum()),'total_subject_fit_pairs':30*args.bootstrap,
          'numerical_retry_count':int(retries.sum()),'unresolved_failures':failed,
          'null_LRT_quantiles':np.quantile(boot,[0,.025,.5,.95,.975,1]).tolist()}
        np.savez(out/'count_model_bootstrap.npz',lrt=boot,converged=convs)
        (out/'count_model_summary.json').write_text(json.dumps(res,indent=2));print('FINAL_BOOTSTRAP',json.dumps(res['parametric_bootstrap']),flush=True)

if __name__=='__main__':main()
