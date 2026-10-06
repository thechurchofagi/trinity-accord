"""Repair one rejected local MAT copy and finish the fixed twelve-session cohort."""
from pathlib import Path
import hashlib,json,shutil,time,zipfile
import joint_decode as study
from rat_cells import load_session
HERE=Path(__file__).resolve().parent
DATA=Path("/workspace/scratch/57a6ec9cccb0/data")
NAME="X062_2020_03_20_g0_t0.imec0.ap_res.Cells.mat"
manifest=json.loads((study.R122/"R122_Input_Manifest.json").read_text())
expected={s["file"]:s for s in manifest["sessions"]}
source=DATA/"Cells"/NAME
if (HERE/"aggregate.json").exists():
    shutil.copyfile(HERE/"aggregate.json",HERE/"First_Pass_11_Sessions_Aggregate.json")
failure=HERE/(Path(NAME).stem+"_failure.json")
if failure.exists():
    failure.rename(HERE/(Path(NAME).stem+"_first_pass_failure.json"))
rejected={"file":NAME,"observed_bytes":source.stat().st_size,"observed_sha256":study.sha(source),
    "expected_bytes":expected[NAME]["bytes"],"expected_sha256":expected[NAME]["sha256"],
    "outcome":"REJECTED_BEFORE_MODEL_FIT",
    "cause":"local copy is truncated; cause of post-recovery truncation not established",
    "not_a_biological_exclusion":True}
study.write_json(HERE/"single_session_repair.json",{"rejected":rejected,"repair_status":"STARTED"})
if study.sha(DATA/"Cells.zip")!=manifest["archive_sha256"]:raise AssertionError("Archive changed")
reject_dir=DATA/"rejected";reject_dir.mkdir(exist_ok=True)
source.rename(reject_dir/(NAME+".truncated"))
tmp=source.with_suffix(".repair")
with zipfile.ZipFile(DATA/"Cells.zip") as z:
    member=next(v for v in z.infolist() if v.filename=="Cells_upload/"+NAME)
    with z.open(member) as src,tmp.open("wb") as out:
        count=0
        while b:=src.read(8*1024*1024):
            written=out.write(b)
            if written!=len(b):raise IOError("Short write")
            count+=written
if count!=expected[NAME]["bytes"] or study.sha(tmp)!=expected[NAME]["sha256"]:
    raise AssertionError("Re-extracted session digest mismatch")
tmp.rename(source)
print(json.dumps({"event":"repaired_and_verified","file":NAME,"bytes":count}),flush=True)
session=load_session(source,load_neural=True)
if session.source_sha256!=expected[NAME]["sha256"]:raise AssertionError("Input changed during loading")
reference=study.pd.read_csv(HERE/"reference_B2_session_metrics.csv")
summary=study.analyze(session,HERE,reference)
summaries=[]
for name,exp in expected.items():
    p=HERE/(Path(name).stem+"_summary.json")
    v=json.loads(p.read_text())
    if v["status"]!="COMPUTED" or v["source_sha256"]!=exp["sha256"]:
        raise AssertionError("Unexpected session provenance")
    for artifact in [v["feature_artifact"]]+v["artifacts"]:
        if study.sha(HERE/artifact["file"])!=artifact["sha256"]:
            raise AssertionError("Saved artifact changed")
    summaries.append(v)
result=study.aggregate(summaries,HERE)
if (result["n_sessions"],result["n_rats"],result["n_trials"],result["n_bins"])!=(12,5,3319,32656):
    raise AssertionError("Final cohort differs from fixed R122 cohort")
study.write_json(HERE/"single_session_repair.json",{"rejected":rejected,"repair_status":"VERIFIED_AND_ANALYZED",
    "repaired_bytes":source.stat().st_size,"repaired_sha256":study.sha(source),
    "all_twelve_artifact_digests_checked":True,"final_cohort":[12,5,3319,32656]})
print(json.dumps({"event":"twelve_session_completion","trials":3319,"bins":32656,"all_saved_artifacts_verified":True}),flush=True)

