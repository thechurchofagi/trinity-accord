"""Integrity/numerical audit of the fixed BCI run; no model-selection retries."""
from pathlib import Path
import json
import sys
import hashlib
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"root_analysis"))
import fit_response_models as model

OUT=HERE/"results"/"bci_response"
full=json.loads((OUT/"full_fits.json").read_text())
cv=json.loads((OUT/"cv_fits.json").read_text())
partition=np.load(OUT/"cv_partition_counts.npz")
y=partition["full_counts"];test=partition["test_counts"];train=partition["train_counts"]
assert test.shape==(5,30,6,7) and train.shape==test.shape
assert np.array_equal(test.sum(axis=0),y)
assert np.array_equal(train+test,y[None,:,:,:]+np.zeros_like(test))
assert (test>=0).all() and (test<=2).all() and (train>=0).all() and (train<=8).all()
all_rows=[]
maximum_score_discrepancy=0.
for i in range(30):
    for name in model.MODELS:
        f=full[i][name]
        nll=model.nll_and_gradient(f["theta"],y[i],10,name)[0]
        maximum_score_discrepancy=max(maximum_score_discrepancy,abs(nll-f["nll"]))
        all_rows.append(f)
        for fold in range(5):
            f=cv[i][fold][name]
            assert f["additional_start_parameters"]==[]
            assert f["full_data_or_source_initialization_used"] is False
            assert np.array_equal(f["counts"],train[fold,i])
            assert np.array_equal(f["heldout_counts"],test[fold,i])
            nll=model.nll_and_gradient(f["theta"],train[fold,i],8,name)[0]
            heldout=model.nll_and_gradient(f["theta"],test[fold,i],2,name)[0]
            maximum_score_discrepancy=max(maximum_score_discrepancy,abs(nll-f["nll"]),abs(heldout-f["heldout_nll"]))
            all_rows.append(f)
boundaries={}
for phase in ["full","cv"]:
    boundaries[phase]={}
    for name in model.MODELS:
        selected=[f for f in all_rows if f["phase"]==phase and f["model"]==name]
        nu,ns,_,_,shift=model.structure(name)
        counters={"prior_logit":0,"log_sigma":0,"lapse":0,"task_center":0}
        centers=[]
        for f in selected:
            hits=set(f["bounds_hit"])
            counters["prior_logit"]+=bool(hits.intersection(range(nu)))
            counters["log_sigma"]+=bool(hits.intersection(range(nu,nu+ns)))
            counters["lapse"]+=(nu+ns in hits)
            counters["task_center"]+=bool(hits.intersection(range(nu+ns+1,len(f["theta"]))))
            if shift:centers.append(f["parameters_interpreted"]["task_centers_ms"])
        entry={"fit_count":len(selected),"fits_with_each_boundary_type":counters,
            "max_projected_gradient":max(f["projected_gradient_max"] for f in selected),
            "all_best_status_success":all(f["success"] for f in selected),
            "all_selected_probabilities_strictly_interior":all(np.all((np.asarray(f["probabilities"])>0)&(np.asarray(f["probabilities"])<1)) for f in selected),
            "min_number_successful_starts":min(f["successful_starts"] for f in selected)}
        if centers:
            centers=np.asarray(centers)
            entry["task_center_ranges_ms"]=[centers.min(axis=0).tolist(),centers.max(axis=0).tolist()]
            entry["task_center_medians_ms"]=np.median(centers,axis=0).tolist()
        boundaries[phase][name]=entry
assert maximum_score_discrepancy<1e-8
report={
    "partition_checks_passed":True,
    "all_600_cv_records_have_generic_only_initialization":True,
    "all_training_and_heldout_counts_match_saved_partition":True,
    "maximum_recomputed_score_discrepancy":maximum_score_discrepancy,
    "total_fit_records":len(all_rows),
    "best_status_success_count":sum(f["success"] for f in all_rows),
    "max_projected_gradient":max(f["projected_gradient_max"] for f in all_rows),
    "number_quality_flags":sum(f["numerical_quality_flag"] for f in all_rows),
    "boundaries_and_centers":boundaries,
    "full_original_models_max_nll_minus_source_start":max(full[i][name]["nll"]-full[i][name]["matching_source_nll"] for i in range(30) for name in ["sigma","prior"]),
    "source_fitter_sha256":hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest(),
    "interpretation":"Convergence and exact score accounting are numerical evidence, not a proof of global optima or of conditional binomial independence."
}
(OUT/"execution_integrity_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
