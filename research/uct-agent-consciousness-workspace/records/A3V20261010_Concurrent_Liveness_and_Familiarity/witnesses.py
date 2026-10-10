#!/usr/bin/env python3
"""Small stipulated countermodels; no physical token or phenomenal validation."""
import json
from pathlib import Path
rows=[]
for a in (0,1):
    for b in (0,1):
        # Joint has two live policy occurrences; integrated has one combined state.
        joint_resolver=a+b
        integrated_state=a+b
        rows.append(dict(a=a,b=b,joint_output=joint_resolver,integrated_output=integrated_state))
assert all(r['joint_output']==r['integrated_output'] for r in rows)
# A single plan at each trial, versus simultaneous coordinates; only mean compared.
mixture_trials=[(1,0),(0,1)]
mean=[sum(x[k] for x in mixture_trials)/2 for k in (0,1)]
assert mean==[0.5,0.5]
# Simple ordered path; RetBind fields are stipulated, not empirically validated.
events=['earlier_frame','continued_trace','current_frame_consumer','route_execution']
retained_singleton={'events':events,'ordered':True,'same_bearer_lineage_stipulated':True,
 'trace_tolerance_stipulated':True,'current_use_stipulated':True,'live_policy_count':1,
 'dual_conflict':False,'actual_installation_verified':False,'C1_transport_verified':False,
 'H_identified':False}
out={'schema':'uct-a3v-finite-witness/1','rows':rows,'trial_mixture_mean':mean,
 'joint_live_policy_count':2,'integrated_distinct_policy_input_count':1,
 'output_and_displayed_input_perturbations_equal':True,'retained_singleton':retained_singleton,
 'scope':'STIPULATED_ARCHITECTURES_AND_LISTED_READOUTS_ONLY; NOT A TOKEN DECOMPOSITION THEOREM'}
Path(__file__).with_name('EXACT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('Finite witnesses checked; actual application and H remain open.')
