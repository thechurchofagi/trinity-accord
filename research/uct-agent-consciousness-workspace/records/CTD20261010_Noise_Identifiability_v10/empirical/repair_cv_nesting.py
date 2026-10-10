"""Uniform training-only numerical nesting repair; prior scores are archived."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import multiprocessing
import json
import time
import shutil
import hashlib
import numpy as np
from run_bci_response_comparison import model,fit_record,summarize_outputs,OUT,FIT_SEED,CV_STARTS

HERE=Path(__file__).resolve().parent
ARCHIVE=HERE/"results"/"pre_nested_cv_repair"

def refit_shifted(args):
    participant,fold,name,train,test,base_fit=args
    j=list(model.MODELS).index(name)
    seed=FIT_SEED+10000+participant*100+fold*10+j
    additional=[np.r_[base_fit["theta"],0.,0.]]
    fit=model.fit_one(train,8,name,seed=seed,n_starts=CV_STARTS,additional_starts=additional)
    record=fit_record(fit,name,train,8,seed,additional)
    record.update({"participant":participant+1,"fold":fold+1,"phase":"cv",
        "generic_starts_requested":CV_STARTS,"heldout_counts":test.tolist(),"heldout_trials":2,
        "heldout_nll":float(model.nll_and_gradient(fit["theta"],test,2,name)[0]),
        "full_data_or_source_initialization_used":False,
        "same_training_fold_unshifted_start_added":True,
        "nested_training_reference_nll":base_fit["nll"],
        "nested_training_nll_difference":fit["nll"]-base_fit["nll"]})
    return participant,fold,name,record

def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    full=json.loads((ARCHIVE/"full_fits.json").read_text())
    cv=json.loads((ARCHIVE/"cv_fits.json").read_text())
    old_cv=json.loads((ARCHIVE/"cv_fits.json").read_text())
    partition=np.load(ARCHIVE/"cv_partition_counts.npz")
    y=partition["full_counts"];train=partition["train_counts"];test=partition["test_counts"]
    ctx=multiprocessing.get_context("spawn")
    tasks=[(i,f,base+"_shift",train[f,i],test[f,i],cv[i][f][base]) for i in range(30) for f in range(5) for base in ["sigma","prior"]]
    with ProcessPoolExecutor(max_workers=4,mp_context=ctx) as pool:
        pending=[pool.submit(refit_shifted,arg) for arg in tasks]
        for done,future in enumerate(as_completed(pending),1):
            i,f,name,record=future.result();cv[i][f][name]=record
            if done%30==0:print("uniform_shifted_cv_refits",done,"elapsed",round(time.monotonic()-start,2),flush=True)
    violations=[]
    changes=[]
    for i in range(30):
        for f in range(5):
            for base in ["sigma","prior"]:
                name=base+"_shift"
                gap=cv[i][f][name]["nll"]-cv[i][f][base]["nll"]
                if gap>1e-6:violations.append({"participant":i+1,"fold":f+1,"model":name,"gap":gap})
                delta=cv[i][f][name]["nll"]-old_cv[i][f][name]["nll"]
                if abs(delta)>1e-6:
                    changes.append({"participant":i+1,"fold":f+1,"model":name,
                        "training_nll_change":delta,
                        "heldout_nll_change":cv[i][f][name]["heldout_nll"]-old_cv[i][f][name]["heldout_nll"]})
                assert cv[i][f][base]==old_cv[i][f][base]
    repair={"refits":300,"changed_training_objectives_beyond_1e-6":changes,"remaining_nesting_violations":violations,
            "unshifted_cv_fits_unchanged":True,"full_fits_unchanged":True,
            "heldout_scores_not_used_to_select_or_trigger_individual_refits":True,
            "elapsed_seconds":time.monotonic()-start}
    (OUT/"cv_nesting_repair_summary.json").write_text(json.dumps(repair,indent=2)+"\n")
    assert not violations,violations
    shutil.copyfile(ARCHIVE/"full_fits.json",OUT/"full_fits.json")
    shutil.copyfile(ARCHIVE/"cv_partition_counts.npz",OUT/"cv_partition_counts.npz")
    (OUT/"cv_fits.json").write_text(json.dumps(cv,indent=2)+"\n")
    code_hash=hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()
    summarize_outputs(full,cv,y,code_hash,time.monotonic()-start,extra_metadata={
        "run_status":"Final after uniform training-only nesting repair",
        "pre_repair_results":"results/pre_nested_cv_repair",
        "repair_decision":"BCI_CV_NESTING_REPAIR_DECISION.json",
        "retained_full_fit_records":120,"retained_unshifted_cv_records":300,
        "uniformly_refitted_shifted_cv_records":300})

if __name__=="__main__":main()
