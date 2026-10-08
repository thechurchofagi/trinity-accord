"""Finite practical-centering construction. No variable denotes consciousness or a feeling."""
from itertools import product
from pathlib import Path
import json

def run(origin, target, directive, closure, blocked, imposed_motion, attribution):
    # A fixed desired feature +1 is either used by the selected target policy or not.
    command = 1 if directive and target == "overt" else 0
    rehearsal = 1 if directive and target == "imagery" else 0
    movement = 1 if imposed_motion else (command if not blocked else 0)
    target_feedback = movement if target == "overt" else rehearsal
    mismatch = int(bool(directive) and target_feedback != 1)
    mismatch_used = int(bool(closure) and bool(mismatch))
    practical_center = int(bool(directive) and bool(closure))
    return dict(origin=origin, target=target, directive=directive, closure=closure,
                blocked=blocked, imposed_motion=imposed_motion,
                attribution=attribution, command=command, rehearsal=rehearsal,
                movement=movement, target_feedback=target_feedback,
                mismatch=mismatch, mismatch_used=mismatch_used,
                practical_center=practical_center, report=int(bool(attribution)))

rows = [run(*x) for x in product(
    ["external", "internal"], ["overt", "imagery"],
    [0, 1], [0, 1], [0, 1], [0, 1], [0, 1])]

checks = []
def check(name, condition, interpretation):
    assert condition, name
    checks.append(dict(id=name, passed=True, interpretation=interpretation))

check("R181-M1", len(rows) == 128, "all declared configurations executed")
check("R181-M2", all(
    run("external", t, d, c, b, x, a)["practical_center"] ==
    run("internal", t, d, c, b, x, a)["practical_center"]
    for t, d, c, b, x, a in product(["overt","imagery"],[0,1],[0,1],[0,1],[0,1],[0,1])),
    "proposal provenance does not determine the selected practical relation")
check("R181-M3", run("external","overt",1,1,0,0,0)["practical_center"] == 1,
      "an externally prompted action can instantiate the declared practical relation")
check("R181-M4", run("internal","overt",0,0,0,1,1)["practical_center"] == 0,
      "internal provenance plus imposed output and positive attribution need not instantiate it")
check("R181-M5", run("internal","overt",1,1,1,0,0)["movement"] == 0 and
      run("internal","overt",1,1,1,0,0)["mismatch_used"] == 1,
      "blocked attempt retains directive closure and consumes failure without movement")
check("R181-M6", run("internal","overt",0,0,0,1,1)["movement"] == 1,
      "movement can occur without target-bound directive closure")
check("R181-M7", run("internal","imagery",1,1,0,0,0)["practical_center"] == 1 and
      run("internal","imagery",1,1,0,0,0)["movement"] == 0,
      "practical centering can concern the activity of imagery rather than overt motion")
check("R181-M8", any(x["practical_center"] == 1 and x["report"] == 0 for x in rows) and
      any(x["practical_center"] == 0 and x["report"] == 1 for x in rows),
      "current practical relation and later attribution dissociate")
check("R181-M9", any(x["practical_center"] == 1 and x["movement"] == 0 for x in rows) and
      any(x["practical_center"] == 0 and x["movement"] == 1 for x in rows),
      "movement and practical centering dissociate")
check("R181-M10", run("internal","overt",1,1,0,0,1)["movement"] ==
      run("internal","overt",0,0,0,1,1)["movement"] == 1 and
      run("internal","overt",1,1,0,0,1)["report"] ==
      run("internal","overt",0,0,0,1,1)["report"] == 1 and
      run("internal","overt",1,1,0,0,1)["practical_center"] !=
      run("internal","overt",0,0,0,1,1)["practical_center"],
      "even joint origin/movement/report observations do not identify the relation")
check("R181-M11", all(x["practical_center"] == int(bool(x["directive"]) and bool(x["closure"])) for x in rows),
      "declared relation is exactly the simultaneous conjunction, not either premise")
check("R181-M12", all(x["report"] == x["attribution"] for x in rows),
      "later report is a separate stipulated current process")

result = dict(round="R181", status="FINITE_ROLE_CONSTRUCTION_NOT_PHENOMENOLOGY",
              configurations=len(rows), checks=checks, rows=rows,
              limits=[
                  "directive and closure are stipulated actual role variables in this model",
                  "practical_center is not consciousness, voluntariness, mineness or a feeling",
                  "automatic and reflective execution are not distinguished here",
                  "counterexamples reject single-factor identifications only in the declared domain",
                  "no human, animal or LLM experiment was run"])
Path(__file__).with_name("MODEL_RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(configurations=len(rows), checks=len(checks), status=result["status"])))
