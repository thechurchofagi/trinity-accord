"""Finite proposal/dispatch/retrospective-report construction; no phenomenal labels."""
from itertools import product
from pathlib import Path
import json

def run(origin, proposal, goal, route, pre_memory, post_memory=None):
    # t0: physically distinct producer route delivers proposal p to the same port.
    # t1: an executed compare/select stage uses current goal; output differs on mismatch.
    # 'auto' has exactly the same effective policy as 'regulated', with no extra monitor.
    selected = proposal if goal == 0 or proposal == goal else goal
    # t2: bypass overwrites proximal command; it does not erase the selector computation.
    command = proposal if route == 'bypass' else selected
    # t3: a memory-reading report may be clamped after action, or read its pre-action value.
    read_memory = pre_memory if post_memory is None else post_memory
    report = int(read_memory == command)
    return dict(origin=origin,proposal=proposal,goal=goal,route=route,
                selected=selected,command=command,pre_memory=pre_memory,
                post_memory=post_memory,report=report,
                active_output_path='proposal->override->command' if route=='bypass' else 'compare/select->command')

rows=[run(o,p,g,k,m,z) for o,p,g,k,m,z in product(
 ['external','internal'],[-1,1],[-1,0,1],['regulated','auto','bypass'],[-1,1],[None,-1,1])]
tests=[]
def check(name,condition,interpretation):
    assert condition,name
    tests.append(dict(id=name,pass_=True,interpretation=interpretation))
check('R180-M1',len(rows)==216,'all finite configurations executed')
check('R180-M2',all(x['command']==(x['proposal'] if x['goal']==0 else x['goal']) for x in rows if x['route']!='bypass'),'selected policy actually reaches output')
check('R180-M3',all(x['command']==x['proposal'] for x in rows if x['route']=='bypass'),'override controls output, even if internal selector agrees accidentally')
check('R180-M4',all(run('external',p,g,k,m)['command']==run('internal',p,g,k,m)['command'] for p,g,k,m in product([-1,1],[-1,1],['regulated','auto','bypass'],[-1,1])),'origin alone does not determine the selected output-use relation')
check('R180-M5',all(run(o,p,-1,k,m)['command']!=run(o,p,1,k,m)['command'] for o,p,k,m in product(['external','internal'],[-1,1],['regulated','auto'],[-1,1])),'under the declared intervention family, output responds to changed goal through both policy routes')
check('R180-M6',all(run(o,p,-1,'bypass',m)['command']==run(o,p,1,'bypass',m)['command'] for o,p,m in product(['external','internal'],[-1,1],[-1,1])),'goal sensitivity absent under the stipulated override')
check('R180-M7',all(run(o,p,g,k,m,-1)['command']==run(o,p,g,k,m,1)['command'] and run(o,p,g,k,m,-1)['report']!=run(o,p,g,k,m,1)['report'] for o,p,g,k,m in product(['external','internal'],[-1,1],[-1,1],['regulated','auto','bypass'],[-1,1])),'post-action memory changes report without changing the past command')
check('R180-M8',all(run(o,p,g,k,-1)['command']==run(o,p,g,k,1)['command'] and run(o,p,g,k,-1)['report']!=run(o,p,g,k,1)['report'] for o,p,g,k in product(['external','internal'],[-1,1],[-1,1],['regulated','auto','bypass'])),'even a pre-action stored representation can be report-only in this architecture')
check('R180-M9',all(run(o,p,g,'auto',m)['command']==run(o,p,g,'regulated',m)['command'] for o,p,g,m in product(['external','internal'],[-1,1],[-1,1],[-1,1])),'policy dependence does not establish reflective voluntariness')
check('R180-M10',all(run(o,p,p,'regulated',m)['command']==run(o,p,p,'bypass',m)['command'] for o,p,m in product(['external','internal'],[-1,1],[-1,1])),'matched-output episodes do not establish shared active path')
check('R180-M11',any(x['route']=='bypass' and x['report']==1 for x in rows),'positive retrospective report can accompany bypass')
check('R180-M12',any(x['route']=='regulated' and x['report']==0 for x in rows),'negative retrospective report can accompany operative policy use')

# General clamped-observation obstruction, represented by two freely differing policies.
# Models F1 and F2 have U=G versus U=-G only in free-generation mode. Under clamp=1,
# both set U=P. Their common report reads only M and U. Exhaustive clamped trials
# cannot choose the free-generation law, even when goal/memory are varied.
def clamp_model(sign,goal,proposal,memory,clamped):
    u=proposal if clamped else sign*goal
    return u,int(memory==u)
check('R180-M13',all(clamp_model(1,g,p,m,True)==clamp_model(-1,g,p,m,True) for g,p,m in product([-1,1],repeat=3)),'clamped response equality for all admitted goal/proposal/memory interventions')
check('R180-M14',all(clamp_model(1,g,p,m,False)[0]!=clamp_model(-1,g,p,m,False)[0] for g,p,m in product([-1,1],repeat=3)),'free generation differs despite all clamped records agreeing')
# Goal 0 denotes the accept-proposal policy, not a zero motor command.
check('R180-M15',all(run(o,-1,0,k,m)['command']!=run(o,1,0,k,m)['command'] for o,k,m in product(['external','internal'],['regulated','auto'],[-1,1])),'proposal content affects command under accept policy for either origin')
check('R180-M16',all(run(o,-1,g,k,m)['command']==run(o,1,g,k,m)['command'] for o,g,k,m in product(['external','internal'],[-1,1],['regulated','auto'],[-1,1])),'override policy makes command invariant to proposal content; selected route alone does not prove token influence')
out=dict(round='R180',status='TOY_CONSTRUCTION_NOT_LLM_OR_HUMAN_EXPERIMENT',checks=tests,rows=rows,
 witnesses={'external_uptake':run('external',1,-1,'regulated',1),
            'internal_bypass':run('internal',1,-1,'bypass',1),
            'externally_suggested_and_accepted':run('external',1,1,'regulated',1),
            'automatic_policy':run('internal',1,-1,'auto',1)},
 limits=['Report is an explicit Boolean toy readout, not a feeling.','Origin is recorded provenance; origin differences can remain in full organization.',
         'Regulated and automatic share this selected policy: the model does not decide voluntariness.',
         'The artificial pre_memory/report-only route is a countermodel, not an inferred LLM circuit.',
         'No clinical experiment, raw-data reanalysis or actual LLM inference was run.'])
Path(__file__).with_name('MODEL_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(configurations=len(rows),checks=len(tests),status=out['status'])))
