#!/usr/bin/env python3
"""New v1.1 numerical reimplementation of archived v1.0 model equations.

Not original generation code. All parameters and conventions are declared below.
Archived rows supply sweep inputs only, not model outputs. Outputs are calculated
from fixed equations and compared afterward. This is numerical reproducibility,
not held-out empirical validation or proof of A1/A5.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent / 'baselines' / 'B_v1.0_audit'
OUT = HERE / 'regenerated'
OUT.mkdir(exist_ok=True)
BIASES = (-5.2, -5.1, -5.0, -4.9, -4.8)
TOL = 1e-9

def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))

def access(z: float) -> float:
    return sum(sigmoid(b + 7.0 * z) for b in BIASES) / len(BIASES)

def model1(g: float, drive: float = .3, cut: bool = False) -> dict:
    q = sigmoid(10.0 * (g - .5))
    local = lambda a, b: sigmoid(-2.0 + 1.2*a + 1.2*b + 3.0*q*a*b)
    delta = local(1, 1)-local(1, 0)-local(0, 1)+local(0, 0)
    # Remove the gated x1 -> x2 return edge only; local DIT readout remains unchanged.
    q_workspace = 0.0 if cut else q
    x1 = x2 = 0.0
    for iteration in range(20000):
        y1 = sigmoid(5.0 * (-.5 + drive + 2.0*x2))
        y2 = sigmoid(5.0 * (-.5 + 3.0*q_workspace*x1))
        change = max(abs(y1-x1), abs(y2-x2))
        x1, x2 = y1, y2
        if change < 1e-13:
            break
    else:
        raise RuntimeError(f'Fixed-point iteration failed at g={g}, drive={drive}, cut={cut}')
    G = access((x1+x2)/2.0)
    return dict(g=g, gate_q=q, DIT_interaction_delta=delta,
                RPT_spectral_gain_rho=math.sqrt(6.0*q_workspace),
                workspace_x1=x1, workspace_x2=x2,
                GNWT_global_access_G=G, GNWT_high_access=int(G >= .8))

def model2(lam: float, cut_memory: bool = False, cut_workspace: bool = False) -> dict:
    m, h, w = 1.0, 0.0, 0.0
    ms, hs, ws = [m], [h], [w]
    for _ in range(39):
        new_m = lam*m
        new_h = .6*h + .4*sigmoid(12.0*((0.0 if cut_memory else m)-.35))
        new_w = .7*w + .3*sigmoid(10.0*((0.0 if cut_workspace else h)+1.2*w-.8))
        m, h, w = new_m, new_h, new_w
        ms.append(m); hs.append(h); ws.append(w)
    G = max(access(z) for z in ws)
    return {'lambda': lam, 'MToC_retention_t5': ms[5], 'MToC_retention_auc': sum(ms),
            'HOT_peak_h': max(hs), 'HOT_duration_h_gt_0.5': sum(h > .5 for h in hs),
            'HOT_auc': sum(hs), 'GNWT_peak_w': max(ws), 'GNWT_peak_G': G,
            'GNWT_high_access': int(G >= .8)}

def load(name: str) -> list[dict]:
    with (ARCHIVE/name).open(newline='') as f: return list(csv.DictReader(f))

def save(name: str, rows: list[dict]) -> None:
    with (OUT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

checks = []
def compare(name: str, calculated: list[dict]) -> None:
    archived = load(name)
    if len(archived) != len(calculated): raise AssertionError('row count '+name)
    max_error = 0.0; mismatches = []; comparisons = 0
    for index, (old, new) in enumerate(zip(archived, calculated)):
        for key, oldval in old.items():
            if key not in new: raise AssertionError('missing column '+key)
            v = new[key]
            if oldval in ('True','False'):
                if bool(v) != (oldval == 'True'): mismatches.append([index,key,oldval,v])
            elif oldval == '':
                if v is not None and not (isinstance(v,float) and math.isnan(v)):
                    mismatches.append([index,key,oldval,v])
            else:
                try: number = float(oldval)
                except ValueError:
                    if str(v) != oldval: mismatches.append([index,key,oldval,v])
                else:
                    err=abs(float(v)-number); max_error=max(max_error,err)
                    if err > TOL: mismatches.append([index,key,oldval,v])
            comparisons += 1
    save(name,calculated)
    checks.append({'file':name,'rows':len(archived),'cells':comparisons,'max_abs_error':max_error,
                   'mismatches':mismatches[:12], 'state':'FAIL' if mismatches else 'PASS',
                   'archived_sha256':hashlib.sha256((ARCHIVE/name).read_bytes()).hexdigest()})

base1='UCT_v0.57_SharedLaw_DIT_RPT_GNWT_'
base2='UCT_v0.59_MToC_HOT_GNWT_'
main1=[model1(float(r['g'])) for r in load(base1+'MainSweep.csv')]
control1=[model1(float(r['g']),cut=True) for r in load(base1+'NoReturn_Control.csv')]
compare(base1+'MainSweep.csv',main1)
compare(base1+'NoReturn_Control.csv',control1)
main2=[model2(float(r['lambda'])) for r in load(base2+'MainSweep.csv')]
cutm=[model2(float(r['lambda']),cut_memory=True) for r in load(base2+'Cut_Memory_to_HOT.csv')]
cuth=[model2(float(r['lambda']),cut_workspace=True) for r in load(base2+'Cut_HOT_to_Workspace.csv')]
compare(base2+'MainSweep.csv',main2)
compare(base2+'Cut_Memory_to_HOT.csv',cutm)
compare(base2+'Cut_HOT_to_Workspace.csv',cuth)
summary=[]
for label, rows in [('full model',main2),('cut memory→HOT',cutm),('cut HOT→workspace',cuth)]:
    summary.append(dict(Condition=label,max_MToC_retention_t5=max(r['MToC_retention_t5'] for r in rows),
                        max_HOT_peak_h=max(r['HOT_peak_h'] for r in rows),
                        max_GNWT_peak_G=max(r['GNWT_peak_G'] for r in rows),
                        GNWT_high_access_any=any(r['GNWT_high_access'] for r in rows)))
compare(base2+'ControlSummary.csv',summary)

drive_rows=[]
for old in load(base1+'HeldOutSweep.csv'):
    s=float(old['content_drive_s']);rows=[model1(i*.0025,drive=s) for i in range(401)]
    hits=[r['g'] for r in rows if r['GNWT_high_access']]
    drive_rows.append({'content_drive_s':s,'RPT_rho1_gate_analytic':.5+math.log(.2)/10.,
                       'GNWT_G0.8_ignition_gate':hits[0] if hits else None,
                       'max_global_access_G':max(r['GNWT_global_access_G'] for r in rows),
                       'ignition_observed':bool(hits)})
compare(base1+'HeldOutSweep.csv',drive_rows)

result={'state':'PASS' if all(c['state']=='PASS' for c in checks) else 'FAIL',
        'implementation':'New v1.1 reimplementation; not original generation or v1.0 audit code.',
        'parameters':{'consumer_biases':BIASES,'consumer_gain':7,'model1_start':[0,0],
                      'model1_update':'synchronous, each sweep point restarted from zero',
                      'model1_stop_max_change':1e-13,'model1_max_iterations':20000,
                      'model2_transitions':39,'model2_initial':[1,0,0]},
        'thresholds':{'model1_first_tested_high_access':next(r['g'] for r in main1 if r['GNWT_high_access']),
                      'model2_first_tested_HOT':next(r['lambda'] for r in main2 if r['HOT_peak_h']>=.5),
                      'model2_first_tested_high_access':next(r['lambda'] for r in main2 if r['GNWT_high_access']),
                      'model1_control_max_access':max(r['GNWT_global_access_G'] for r in control1)},
        'checks':checks,'tolerance':TOL,
        'empirical_validation':False,'historical_no_tuning_certified':False}
(HERE/'shared_model_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if result['state']!='PASS':raise SystemExit(1)
