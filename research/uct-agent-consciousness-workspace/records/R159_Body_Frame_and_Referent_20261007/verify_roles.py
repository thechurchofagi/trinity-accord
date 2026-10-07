"""Exact bounded witnesses for R159. No neural/subjective data are simulated."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
def output(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
rows=0;parameter_cases=0
for to,ta,lam,mu in product([F(1,4),F(1,2),F(3,4)],[F(1,4),F(1,2),F(3,4)],[F(1,8),F(1,4),F(1,2)],[F(1,8),F(1,4),F(1,2)]):
    parameter_cases+=1
    val={(b,a):(F(b)-to+lam*b*a,F(a)-ta+mu*a*b) for b,a in product((0,1),repeat=2)}
    assert val[1,0][0]>0 and val[1,0][1]<0
    assert val[0,1][0]<0 and val[0,1][1]>0
    assert val[1,1][0]-val[1,0][0]==lam>0
    assert val[1,1][1]-val[0,1][1]==mu>0
    for (b,a),(o,q) in val.items():
        uncoupled=(F(b)-to,F(a)-ta)
        assert (o>0,q>0)==tuple(x>0 for x in uncoupled)
        rows+=1
assert parameter_cases==81 and rows==324
to=ta=F(1,2);lam=mu=F(1,4)
witness=[dict(binding=b,performed_source=a,o=str(F(b)-to+lam*b*a),q=str(F(a)-ta+mu*a*b)) for b,a in product((0,1),repeat=2)]
internal={'k0','k1'};external={'c0','c1'};psi={'k0':'c0','k1':'c1'};membership={'c0':True,'c1':False};selected={'k1'}
renamings=[]
for kp,cp in product([('k0','k1'),('k1','k0')],[('c0','c1'),('c1','c0')]):
    h=dict(zip(sorted(internal),kp));e=dict(zip(sorted(external),cp))
    mapped_psi={h[k]:e[c] for k,c in psi.items()};mapped_membership={e[c]:v for c,v in membership.items()}
    mapped_selected={h[k] for k in selected}
    assert mapped_selected=={h['k1']}
    assert not mapped_membership[mapped_psi[h['k1']]]
    assert 'c1' not in h # h is undefined for an external referent.
    renamings.append(dict(internal=h,environment=e,selected=sorted(mapped_selected),mapped_reference=mapped_psi,membership_false_for_selected=True))
checks=[]
g=json.loads((ROOT/'UCT_FORMAL_GRAPH.json').read_text())
for source in g['source_versions']:
    actual=hashlib.sha256((ROOT/source['snapshot_workspace_path']).read_bytes()).hexdigest()
    assert actual==source['sha256'];checks.append(dict(paper=source['paper'],sha256=actual,status='PASS'))
output('VALIDATION.json',dict(status='BOUNDED_EXACT_WITNESSES_PASS',parameter_cases=parameter_cases,corner_rows=rows,qualitative_categories_preserved_without_coupling=True,coupled_example=witness,internal_external_renamings=renamings,source_hashes=checks,scope='Abstract witness checks only; no raw-data analysis, fit, physiological installation or F observation.',general_argument='English note §5 contains the independent inequalities for all declared parameters; finite checks alone do not prove universality.',proof_assistant=False))
print(json.dumps(dict(status='PASS',parameter_cases=parameter_cases,corner_rows=rows,renamings=len(renamings),source_hashes=len(checks))))
