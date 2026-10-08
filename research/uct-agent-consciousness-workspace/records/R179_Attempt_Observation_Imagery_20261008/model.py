"""R179 finite route model. No phenomenal or human-classification variables."""
from itertools import product
from pathlib import Path
import json

def episode(q, dispatch, rehearse, register, blocked, imposed):
    # Each enabled consumer executes at t=1. Registers start empty.
    # D is a displayed movement feature, not guaranteed veridical body feedback.
    command = q if dispatch else None
    scratch = q if rehearse else None
    sensory = q if register else None
    endogenous_motion = bool(dispatch and not blocked)
    movement = q if endogenous_motion or imposed else 0
    return dict(q=q, dispatch=dispatch, rehearse=rehearse, register=register,
                blocked=blocked, imposed=imposed, command=command,
                scratch=scratch, sensory=sensory, prospective=q,
                movement=movement,
                routes=[x for x, on in [('plan->motor_port',dispatch),
                                        ('plan->scratch',rehearse),
                                        ('display->sensor',register)] if on])

rows=[episode(q,*bits) for q in [-1,1] for bits in product([False,True],repeat=5)]
checks=[]
def check(name,predicate,scope):
    assert predicate, name
    checks.append(dict(id=name,result=True,scope=scope))

check('R179-M01',len(rows)==64,'complete enumeration of the declared six-coordinate finite domain')
check('R179-M02',all(r['command']==(r['q'] if r['dispatch'] else None) for r in rows),'proximal dispatch equation')
check('R179-M03',all(r['scratch']==(r['q'] if r['rehearse'] else None) for r in rows),'scratch consumer equation')
check('R179-M04',all(r['sensory']==(r['q'] if r['register'] else None) for r in rows),'display consumer equation')
check('R179-M05',all(r['movement']==0 for r in rows if r['blocked'] and not r['imposed']),'blocking downstream prevents specified plant displacement')
check('R179-M06',all(r['command'] is not None for r in rows if r['dispatch'] and r['blocked']),'blocked output does not erase issued proximal token')
check('R179-M07',any(r['movement']!=0 and r['command'] is None for r in rows),'imposed displacement defeats movement-implies-command')
check('R179-M08',all(len({r['prospective'] for r in rows if r['q']==q})==1 for q in [-1,1]),'prospective feature alone does not classify routes')
check('R179-M09',any(r['dispatch'] and r['rehearse'] and r['register'] for r in rows),'three routes can co-occur; one-hot partition fails')
check('R179-M10',all(len({tuple(r['routes']) for r in rows if r['q']==q})==8 for q in [-1,1]),'each fixed movement feature admits eight declared route profiles')
check('R179-M11',any(r['scratch'] is not None and r['movement']==0 for r in rows),'actual rehearsal state does not require represented displacement')

witnesses={
 'issued_and_moving':episode(1,True,False,True,False,False),
 'issued_but_blocked':episode(1,True,False,True,True,False),
 'scratch_only':episode(1,False,True,False,False,False),
 'display_only':episode(1,False,False,True,False,False),
 'mixed_consumers':episode(1,True,True,True,False,False),
 'imposed_motion':episode(1,False,False,True,False,True),
}
out=dict(round='R179',status='FINITE_MODEL_ONLY',checks=checks,witnesses=witnesses,rows=rows,
 limits=['Routing is stipulated, not measured in a human.',
         'Independent displayed feature is not veridical bodily feedback.',
         'No feeling, intention, consciousness or self-reference predicate is computed.',
         'Eight route profiles are actual finite program assignments, not eight semantic or phenomenal modes.'])
Path(__file__).with_name('MODEL_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),rows=len(rows),status=out['status'])))
