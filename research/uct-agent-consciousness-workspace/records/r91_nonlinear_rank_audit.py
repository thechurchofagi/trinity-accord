#!/usr/bin/env python3
"""Exact counterexamples and scope checks; no training or phenomenology."""
import csv
import hashlib
import json
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import r90_anchor_transport_stress_test as prior

ROOT = Path(__file__).resolve().parent
AXES = prior.STATE_AXES
INPUTS = ('core','wanting','viability','other','defense')

def encode(x):
    return sum((v+1)*3**i for i,v in enumerate(x))

def decode(z):
    return tuple((z//3**i)%3-1 for i in range(5))

def reset(z,i,v):
    old=(z//3**i)%3-1
    return z+(v-old)*3**i

class EncodedController:
    def run(self,spec,raw=False):
        z=encode((0,)*5)
        rows=[]
        for t in range(prior.STEPS):
            if t==0:
                for i,key in enumerate(INPUTS):
                    old=(z//3**i)%3-1
                    z=reset(z,i,max(-1,min(1,old+spec.get(key,0))))
            x=decode(z)
            y=0 if spec.get('report_disconnect',False) else spec.get('report_override',x[0])
            rows.append({'z':z,'Y':y} if raw else dict(zip(AXES,x))|{'Y':y,'L':x[0]})
        return rows

def main():
    tests={}
    transitions=[]
    for x in product((-1,0,1),repeat=5):
        z=encode(x)
        assert decode(z)==x
        for i in range(5):
            for v in (-1,0,1):
                new=reset(z,i,v)
                want=list(x);want[i]=v
                ok=decode(new)==tuple(want)
                transitions.append([z,i,v,new,ok])
    tests['all_243_states_decode']=True
    tests['all_3645_local_reset_conjugacies']=all(row[-1] for row in transitions)
    with (ROOT/'R91_Encoded_Reset_Checks.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['old_code','axis','value','new_code','commutes']);w.writerows(transitions)

    enc=EncodedController()
    trajectories={name:enc.run(spec) for name,spec in prior.SCENARIOS.items()}
    matches={name:rows==prior.FactorizedController().run(prior.SCENARIOS[name]) for name,rows in trajectories.items()}
    tests['all_ten_R90_scenarios_match_after_decoding']=all(matches.values())
    basis,decoded=prior.response_matrix(enc)
    rb=enc.run({},raw=True)
    raw=[]
    for name in basis:
        rows=enc.run(prior.SCENARIOS[name],raw=True)
        raw.append([rows[t][a]-rb[t][a] for t in range(3) for a in ('z','Y')])
    zonly=[r[::2] for r in raw]
    ranks={'encoded_register_only':prior.exact_rank(zonly),'encoded_register_plus_report':prior.exact_rank(raw),'decoded_signature':prior.exact_rank(decoded)}
    tests['nonlinear_readout_changes_finite_response_rank']=ranks=={'encoded_register_only':1,'encoded_register_plus_report':2,'decoded_signature':6}

    curve=[[z**j for j in range(1,7)] for z in range(1,7)]
    derivative=[[j*2**(j-1)] for j in range(1,7)]
    curve_ranks={'finite_secant':prior.exact_rank(curve),'derivative_at_two':prior.exact_rank(derivative)}
    tests['smooth_scalar_has_rank_six_secants_but_rank_one_tangent']=curve_ranks=={'finite_secant':6,'derivative_at_two':1}

    _,bundle=prior.response_matrix(prior.BundledController(False))
    replicas=[]
    for n in (1,2,10,100):
        expanded=[row*n for row in bundle]
        rank=prior.exact_rank(expanded)
        replicas.append({'copies':n,'shape':[len(expanded),len(expanded[0])],'calculated_rank':rank})
    tests['materialized_repeated_columns_keep_rank_two']=all(r['calculated_rank']==2 for r in replicas)

    path=[]
    for alpha in (Q(0),Q(1,1000),Q(1,10),Q(1)):
        matrix=[[1,0],[0,alpha]]
        path.append({'alpha':str(alpha),'rank':prior.exact_rank(matrix),'smallest_singular_value':str(alpha),'operator_distance_from_zero_path_endpoint':str(alpha)})
    tests['continuous_path_has_discontinuous_rank']= [r['rank'] for r in path]==[1,2,2,2]

    result={'scope':'exact constructed counterexamples, no training or subjective measurement','tests':tests,'status':'PASS' if all(tests.values()) else 'FAIL','state_count':243,'minimum_fixed_binary_bits_for_243_states':8,'reset_checks':len(transitions),'scenario_matches':matches,'trajectories':trajectories,'intervention_basis':basis,'raw_matrix':raw,'decoded_matrix':decoded,'ranks':ranks,'smooth_curve_matrix':curve,'derivative_matrix_at_two':derivative,'smooth_curve_ranks':curve_ranks,'materialized_replications':replicas,'continuous_path':path,'R90_code_sha256':hashlib.sha256((ROOT/'r90_anchor_transport_stress_test.py').read_bytes()).hexdigest()}
    (ROOT/'R91_Nonlinear_Rank_Results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'tests':tests,'ranks':ranks,'curve':curve_ranks,'resets':len(transitions),'replicas':replicas},indent=2))
    assert all(tests.values())

if __name__=='__main__':
    main()
