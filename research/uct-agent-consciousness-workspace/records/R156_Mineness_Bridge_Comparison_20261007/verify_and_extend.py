from pathlib import Path
import json, hashlib, copy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REL=str(HERE.relative_to(ROOT))
note=REL+'/Selected_Mineness_Bridges_v0_1.md'
sha=hashlib.sha256((ROOT/note).read_bytes()).hexdigest()
rows=[]
for c in [0,1]:
    current=c*1+(1-c)*1
    table=[c*m+(1-c)*1 for m in [0,1]]
    rows.append(dict(c=c,current_M=1,current_D=1,current_V=current,intervention_table=table,R=int(table[0]!=table[1])))
assert rows[0]['current_V']==rows[1]['current_V']==1
assert rows[0]['R']==0 and rows[1]['R']==1
assert all(int(r['intervention_table'][0]!=r['intervention_table'][1])==r['R'] for r in rows)
# If the operation changes D along with M, the null-use witness disappears.
assert [0*m+1*m for m in [0,1]]==[0,1]
validation=dict(status='PASS',checks=['equal_snapshot','different_fixed_D_use','table_recovers_defined_R','changing_D_invalidates_original_operation_contract'],rows=rows,empirical_validation=False,phenomenal_values_assigned=False,proof_assistant_certified=False)
(HERE/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
f=ROOT/'UCT_FORMAL_GRAPH.json'; raw=f.read_bytes();g=json.loads(raw)
assert g['revision']=='R155-v1.0','Run once on R155 parent only.'
old=copy.deepcopy(g['nodes']),copy.deepcopy(g['rules']),copy.deepcopy(g['context_links'])
domain='Two deterministic typed devices c in {0,1}; current M=D=1; V=c*M+(1-c)*D; identical independent prediction/readout ports; legal do(M=0),do(M=1) keep D=1,c and other ports fixed; snapshot descriptor excludes wiring c. Abstract comparison; physical realization is extra.'
base=dict(domain=domain,scope=domain,source=note+' §3',source_lineage=note+' §3',counterexamples_and_limits='R is a declared functional consumer sensitivity, not selected mineness F_O. Including wiring in the descriptor or changing D under intervention changes the claim. No actual realization, full-type difference or phenomenal contrast is inferred.')
setup=dict(base,id='R156:INSTALLATION_WITNESS',kind='DEFINITION_AND_ASSUMPTION_PACKAGE',label='Matched snapshot with two installation choices',statement=domain,status='DECLARED_FINITE_MODEL',proof='Explicit alternative device/operation definitions; c=0 and c=1 are compared worlds, not simultaneous values.')
claim=dict(base,id='R156:SNAPSHOT_USE_LIMIT',kind='CONDITIONAL_RESULT',label='Snapshot does not recover installed attribution use',statement='The devices have the same declared snapshot including M,D,V and attribution/prediction readouts, but R(c)=1[V(do(M=0))!=V(do(M=1))] equals c. No fixed snapshot decoder recovers R for both; the two-entry response table does recover R on this domain.',status='MANUAL_CONDITIONAL_ARGUMENT_WITH_EXACT_WITNESS',proof='At M=D=1 both outputs are 1. With fixed D=1 the c=0 table is (1,1), c=1 table (0,1), so R differs. Equal decoder inputs cannot give these different R values. Comparing table entries recovers R.')
rule=dict(id='r156_snapshot_use_limit',all_of=[setup['id']],conclusion=claim['id'],statement=claim['statement'],proof_sketch=claim['proof'],source=claim['source'],kind='DEDUCTIVE_APPLICATION',review=claim['status'])
for n in [setup,claim]:
 n['formal_contract_R156']=dict(object_domain=domain,quantifiers='Both c=0,1 devices in W and both separately admissible interventions; one equal-input/different-target counterexample is sufficient to refute a universal decoder on W.',bearer_time_signature='Fixed typed ports and one pre-intervention instant; actual bearer realization remains extra.',source_anchor=dict(path=note,sha256=sha,locator='§3'),premise_routes=[] if n is setup else [dict(rule=rule['id'],all_of=rule['all_of'])],purpose='Compare candidate descriptors for selected bodily mineness without substituting an operational contrast for a phenomenal contrast.',thought_experiments=note+' §6',open_obligations=['R155-G1','R155-G2','R155-G5'],machine_formalized=False)
rule['formal_contract_R156']=dict(premise_connective='AND',alternative_routes='Separate rule IDs would be OR; one route here.',bindings_required=['fixed D under both operations','same snapshot domain excluding c','same functional R target; never substitute F_O'],proof_location=note+' §3',source_sha256=sha,machine_proof=False)
links=[dict(**{'from':'R155:BRIDGE_CRITERION','to':claim['id']},relation='equal-descriptor contrast for functional R only; not an independently given phenomenal target'),dict(**{'from':claim['id'],'to':'R155:MINENESS_OBLIGATION'},relation='open selected-mineness interpretation remains; no deductive discharge'),dict(**{'from':'R147:MEMORY_LIMIT','to':setup['id']},relation='causal installation versus record-only isolation comparison')]
g['nodes'] += [setup,claim];g['rules'].append(rule);g['context_links']+=links
assert g['nodes'][:-2]==old[0] and g['rules'][:-1]==old[1] and g['context_links'][:-3]==old[2]
ids={n['id'] for n in g['nodes']}
assert len(ids)==len(g['nodes']) and len({r['id'] for r in g['rules']})==len(g['rules'])
assert all(r['conclusion'] in ids and all(p in ids for p in r['all_of']) for r in g['rules'])
# New conclusion and root are fresh; their only dependency is the new root.
# No inherited rule references them, so adding this route cannot create a cycle.
assert not any(p.startswith('R156:') for r in old[1] for p in r['all_of'])
g['revision']='R156-v1.0';g['base_commit']='9c8b36836facba39a7eb761b163fd6e253979182'
g['research_R156']=dict(parent_graph_sha256=hashlib.sha256(raw).hexdigest(),note=note,new_nodes=2,new_rules=1,scope='Functional installation comparison; three candidate phenomenal bridges remain open.',end_of_round_audit=note+' §7',hourly_protocol='HOURLY_RESEARCH_PROTOCOL.md',no_inherited_open_family_closed=True)
f.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
(HERE/'MAP_EXTENSION.json').write_text(json.dumps(dict(nodes=[setup,claim],rules=[rule],context_links=links),ensure_ascii=False,indent=2)+'\n')
(HERE/'MAP_AUDIT.json').write_text(json.dumps(dict(status='SCOPED_AUDIT_PASS',nodes=len(g['nodes']),rules=len(g['rules']),inherited_nodes_rules_context_unchanged=True,new_edges_acyclic=True,no_deduction_to_F_O=True,joint_premise_review=note+' §7',purpose='Direct candidate-description comparison; next work must address mineness interpretation rather than repeat insufficiency lemmas.',global_semantic_certification=False),indent=2)+'\n')
(HERE/'GAP_LEDGER.json').write_text(json.dumps(dict(inherited='records/R155_Bodily_Attribution_Formation_20261007/GAP_LEDGER.json',closed=[],entries=[dict(id='R156-G1',status='OPEN',issue='No independently established F_O contrast for matched snapshot/different use pair.',affected=['R155:MINENESS_OBLIGATION'],forbidden_inference='R differs therefore F_O differs',next='Independently specify selected mineness target and fixed interpretation before assigning values.'),dict(id='R156-G2',status='DECLARED_BOUNDARY',issue='Diagnostic M intervention can break q/M consistency; it is a latch disposition test, not a calibrated posterior history.',affected=[setup['id'],claim['id']],next='Retain off-manifold/physical-operation premise explicitly.'),dict(id='R156-G3',status='OPEN',issue='The finite use table omits complete constitutive organization.',affected=['A:C1_OI','R155:BRIDGE_CRITERION'],next='Do not infer complete experiential equality from finite table equality.')]),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(model_checks=4,nodes=len(g['nodes']),rules=len(g['rules']),inherited_preserved=True)))
