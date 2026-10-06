#!/usr/bin/env python3
import json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[1]
WORK=REPO/"research/uct-agent-consciousness-workspace"
FROZEN=WORK/"drafts/From_Shutdown_Resistance_to_Self_Continuation_Control_v0.3_20261006.md"
SOURCE=ROOT/"source-main.md"
def blob(path):
    return subprocess.check_output(["git","rev-parse","HEAD:"+path.relative_to(REPO).as_posix()],cwd=REPO,text=True).strip()
def fail(msg): raise RuntimeError(msg)
source=SOURCE.read_text(encoding="utf-8"); frozen=FROZEN.read_text(encoding="utf-8")
if "TA-TR-2026-24" not in source or "**Version 1.0" not in source or "__DOI_RESERVED_AT_RELEASE__" not in source: fail("release identity mismatch")
if source.split("## Abstract",1)[1] != frozen.split("## Abstract",1)[1]: fail("substantive body changed")
if blob(FROZEN)!="ea6d6c4d5b7ad63df6e343c9357e5d3f5959f3a6": fail("reviewed source blob changed")
fm=json.loads((ROOT/"FORMAL-MAP.json").read_text())
prohibited={(x["from"],x["to"]) for x in fm["prohibited_inferences"]}
if not {("E1","self_awareness"),("A1","direct_Q_value"),("E4","negative_valence"),("S1","fear")}.issubset(prohibited): fail("prohibited inference coverage missing")
low=source.lower()
for phrase in ("does not treat continuation control as a measure of consciousness, negative valence, or fear","evaluator-declared bearer-role predictive relation","nothing above establishes consciousness"):
    if phrase not in low: fail("required nonclaim missing: "+phrase)
r96=json.loads((WORK/"records/R96_Results.json").read_text())
if (r96["num_profiles"],r96["bundled_exact"]["signatures"],r96["bundled_exact"]["max_class"],r96["full_exact"]["signatures"])!=(243,43,17,243): fail("R96 identity mismatch")
r96d=json.loads((WORK/"records/R96D_Results.json").read_text())
if r96d["oracle_value"]!="3/4" or r96d["marginal_interface_values"]!=["5/8","5/8"]: fail("R96D identity mismatch")
r98=json.loads((WORK/"records/R98_Results.json").read_text())
if r98["paired_counts"]!={"lower_test_max_prob_error":25,"lower_test_mean_abs_prob_error":31,"total_runs":32}: fail("R98 identity mismatch")
r99=json.loads((WORK/"records/R99_Results.json").read_text())
if r99["domain"]["grid_points"]!=9261 or r99["domain"]["cube"]!=[-1.25,1.25]: fail("R99 identity mismatch")
r101=json.loads((WORK/"records/R101_ROGUE_Public_Aggregate_Extract.json").read_text())
if r101["source_commit"]!="faf8f378c1b8bc8e17cab8477052c0856a3f3312" or r101["core_interpretation"]["first_missing_layer_for_current_bearer_claim"]!="L0": fail("R101 identity mismatch")
rep=json.loads((ROOT/"REPRODUCIBILITY-SOURCES.json").read_text())
for item in rep["files"]:
    p=REPO/item["path"]
    if not p.is_file() or blob(p)!=item["git_blob_sha"]: fail("repro source mismatch "+item["path"])
print(json.dumps({"state":"FORMAL_RELEASE_AUDIT_PASS","report":"TA-TR-2026-24","version":"1.0","repro_sources":len(rep["files"])},indent=2))
