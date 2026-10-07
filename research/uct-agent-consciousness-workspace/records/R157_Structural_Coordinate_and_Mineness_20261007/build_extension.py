"""Append the scoped R157 layer without rewriting inherited R156 entries."""
from pathlib import Path
import copy,hashlib,json

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent.parent
REL=str(HERE.relative_to(ROOT)); NOTE=REL+'/Structural_Coordinate_and_Mineness_v0_1.md'
GRAPH=ROOT/'UCT_FORMAL_GRAPH.json'; raw=GRAPH.read_bytes(); g=json.loads(raw)
assert g['revision']=='R156-v1.0'
old_nodes,old_rules,old_links=copy.deepcopy(g['nodes']),copy.deepcopy(g['rules']),copy.deepcopy(g['context_links'])
note_sha=hashlib.sha256((ROOT/NOTE).read_bytes()).hexdigest()

common='One admitted actual token P, interval I, complete many-sorted signature K, D_ontic,K(P), Phi_K(P), C1 isomorphism h; correctly sorted tuples and fixed/transported parameters. Formula selection is internal to K and physically grounded separately.'
nodes=[]
def add(suffix,kind,statement,domain,section,status,proof,limits,obligations):
 n=dict(id='R157:'+suffix,kind=kind,label=suffix.replace('_',' ').title(),statement=statement,domain=domain,scope=domain,source=NOTE+' '+section,source_lineage=NOTE+' '+section,status=status,proof=proof,counterexamples_and_limits=limits)
 n['formal_contract_R157']=dict(object_domain=domain,quantifiers='Fixed P,I,K and declared parameters per instance. Formula quantifiers range over the correctly sorted carriers of that instance. Semantic vocabulary outside K is never silently quantified as a K-relation.',bearer_time_signature='Same actual bearer token, interval, complete K, formula and parameter transport throughout one T1 instance.',source_anchor=dict(path=NOTE,sha256=note_sha,locator=section),premise_routes=[],purpose='Locate the exact conditional step from actual body-centered organization to an experiential substructure, while keeping mineness semantics and measurement explicit.',thought_experiments=NOTE+' §7',open_obligations=obligations,machine_formalized=False)
 nodes.append(n);return n['id']

s=add('DEFINABLE_SELECTOR_SETUP','DEFINITION_AND_ASSUMPTION_PACKAGE','Fix a parameter-free K-formula theta(x_bar), or declared parameters p_bar transported by h. S_theta(D,p_bar) is the set of tuples satisfying theta. The claimed relations are internal to the complete K-structure and independently physically grounded; analyst-only labels are excluded.',common, '§2','DECLARED_SELECTOR_CONTRACT','Definition plus physical-grounding obligation; no claim that theta denotes mineness.','Arbitrary complete-type projections, frozen external labels and omitted relations do not satisfy this internal-selector contract. Definability alone does not establish semantic correctness.',['F153-09','F153-10','F153-11','F153-17'])
t=add('COORDINATE_TRANSPORT','CONDITIONAL_RESULT','For every K-formula theta and correctly sorted tuple a_bar, D |= theta(a_bar,p_bar) iff Phi |= theta(h(a_bar),h(p_bar)); hence h[S_theta(D,p_bar)]=S_theta(Phi,h(p_bar)).',common,'§3 T1','MANUAL_CONDITIONAL_MODEL_THEORETIC_ARGUMENT','Induction on formulas: K-isomorphism preserves/refects atomic formulas and equality; Boolean cases follow; existential witnesses map by h and return by surjectivity; universal follows; tuplewise equivalence yields set equality.','Standard isomorphism preservation. Tokenwise and K-relative; no empirical identification of h, complete-signature validation or mineness semantics.',['F153-09','F153-10','F153-11','F153-16','F153-17'])
v=add('SEMANTIC_VOCABULARY_SETUP','DEFINITION_AND_ASSUMPTION_PACKAGE','Let L be a semantic vocabulary outside K containing the expression felt bodily mineness. Metalinguistic assignments nu interpret L without changing D,Phi,h,theta or any K-fact.',common+' L and nu are metalinguistic, not new relations in K.','§4','DECLARED_METASEMANTIC_COMPARISON','Definition of two-level structural/semantic comparison.','If the mineness predicate is explicitly added to complete K with independently fixed interpretation, this setup changes; its physical/semantic grounding must then be supplied rather than assumed.',['F153-11','F153-17'])
r=add('SEMANTIC_RESIDUAL','CONDITIONAL_LIMIT','A:C1 plus a K-definable transported coordinate does not uniquely determine which external L-name denotes that experiential substructure. In particular, the name felt bodily mineness requires an additional fixed bridge B_min.',common+' Same K-structure and experiential structure; only L-assignments differ.','§4 T2','MANUAL_METATHEORETIC_NONENTAILMENT_ARGUMENT','Keep D,Phi,h,theta and the transported support fixed. One nu names it felt bodily mineness; another names it only body-related experiential role and leaves the former undefined or separately assigned. Both preserve every K-fact, so uniqueness is not entailed.','This does not assign different experiences to identical complete organization. It varies metalinguistic interpretation only; it does not show all names are equally empirically adequate.',['F153-11','F153-17'])
rd=add('REPORT_DOMAIN_SETUP','DEFINITION_AND_ASSUMPTION_PACKAGE','Let Omega=Omega_rep union Omega_norep include admitted actual tokens with and without a typed report channel. An operational report measure M_rep has domain Omega_rep because its protocol requires that channel.', 'Mixed declared actual domain Omega; report protocol and channel typing fixed. Omega_norep is nonempty for the coverage witness.','§5','DECLARED_MEASUREMENT_DOMAIN','Definition of a partial operational measure.','A structural predicate ReportPresent can be total and false outside Omega_rep; that is not the same object as executing the partial measurement protocol.',['F153-11','F153-12'])
rl=add('REPORT_COVERAGE_LIMIT','CONDITIONAL_LIMIT','M_rep alone cannot evaluate a target quantified over all Omega. Every total extension requires separately assigned values on Omega_norep; assigning no report to no mineness is an extra rule, not a consequence of the partial measure, A:C1 or A:U1.', 'Exactly R157:REPORT_DOMAIN_SETUP; mathematical conclusion concerns the partial map. C1/U1 are interpretation context, not premises needed for the set-theoretic domain fact.','§5 T3','MANUAL_DOMAIN_ARGUMENT','M_rep is undefined outside Omega_rep. A total function on Omega must add values there; at least two Boolean extensions agree on Omega_rep and differ on a nonreporter. The partial map does not choose between them.','Does not assert or deny bodily mineness for nonreporters. A report-based bridge may be valid on Omega_rep; universal extension remains additional.',['F153-11','F153-12','F153-17'])
b=add('MINENESS_BRIDGE_SCHEMA','OPEN_BRIDGE_SCHEMA','A candidate B_min must jointly specify: grounded theta_body; T1 transport; independently fixed target semantics; common bearer/body/time/signature/operation domain; separate fallible measurement; and explicit failure criteria. Missing report is not target absence. The candidate theta_body conjunction uses attachment, body-directed sensory routing, body-directed action-consequence routing and installed attribution use; interoception, affect and persistence are named optional extensions.', 'Candidate selected bodily-mineness interpretation on a declared actual domain. This is not a basal-experience gate or a proved necessary/sufficient condition.','§6','OPEN_METHOD_PACKAGE_NOT_DERIVED','Obligation/schema only. B:BAC supplies admissibility requirements; T1 supplies structural transport but not the semantic or empirical premises.','No proof that theta_body is complete, necessary, sufficient or realized biologically. A fiber counterexample with independently warranted F_O would refute sufficiency on that domain.',['F153-09','F153-10','F153-11','F153-12','F153-17'])

rules=[]
def rule(id,premises,conclusion,kind='DEDUCTIVE_APPLICATION'):
 n=next(n for n in nodes if n['id']==conclusion)
 z=dict(id=id,all_of=premises,conclusion=conclusion,statement=n['statement'],proof_sketch=n['proof'],source=n['source'],kind=kind,review=n['status'])
 z['formal_contract_R157']=dict(premise_connective='AND',alternative_routes='Other rule IDs would be OR; no alternate route is asserted here.',bindings_required=['same P,I,K and sorted carriers','same theta and parameter transport','structural and semantic vocabularies not conflated'],quantification=n['formal_contract_R157']['quantifiers'],proof_location=n['source'],source_sha256=note_sha,review_status=n['status'],machine_proof=False)
 rules.append(z)
rule('r157_coordinate_transport',['A:C1',s],t)
rule('r157_semantic_residual',[t,v],r,'META_THEORETIC_LIMIT')
rule('r157_report_coverage',[rd],rl,'DOMAIN_LIMIT')
for n in nodes:n['formal_contract_R157']['premise_routes']=[dict(rule=x['id'],all_of=x['all_of']) for x in rules if x['conclusion']==n['id']]
links=[
 dict(**{'from':'R126:P1','to':s},relation='contrast: arbitrary transported type projection versus internally definable physically grounded selector'),
 dict(**{'from':'B:BAC','to':b},relation='methodological admissibility requirements for the still-open semantic/measurement bridge'),
 dict(**{'from':'R155:MINENESS_OBLIGATION','to':b},relation='R157 refines the open obligation into structural, semantic and measurement layers'),
 dict(**{'from':'R156:SNAPSHOT_USE_LIMIT','to':s},relation='installed use is one possible K-relation, not itself a mineness conclusion'),
 dict(**{'from':t,'to':b},relation='conditional structural transport discharges only the middle layer'),
 dict(**{'from':r,'to':b},relation='semantic residual remains to be supplied and tested'),
 dict(**{'from':'A:U1','to':rl},relation='context: undefined/no report cannot be made an experience-existence or mineness conclusion from U1')]

g['nodes']+=nodes;g['rules']+=rules;g['context_links']+=links
assert g['nodes'][:len(old_nodes)]==old_nodes and g['rules'][:len(old_rules)]==old_rules and g['context_links'][:len(old_links)]==old_links
ids=[n['id'] for n in g['nodes']];rids=[x['id'] for x in g['rules']]
assert len(ids)==len(set(ids)) and len(rids)==len(set(rids))
assert all(x['conclusion'] in ids and all(p in ids for p in x['all_of']) for x in g['rules'])
deps={i:set() for i in ids}
for x in g['rules']:deps[x['conclusion']].update(x['all_of'])
seen=set();active=set()
def visit(i):
 assert i not in active,('cycle',i)
 if i in seen:return
 active.add(i)
 for p in deps[i]:visit(p)
 active.remove(i);seen.add(i)
for i in ids:visit(i)
g['revision']='R157-v1.0';g['base_commit']='7af49dad7491910d3c6aa205fc4f89ba4b1c5134'
g['research_R157']=dict(parent_research_commit='d80d08a4c0c09559e2122da38e24956b17bb711b',parent_branch_head='7af49dad7491910d3c6aa205fc4f89ba4b1c5134',parent_graph_sha256=hashlib.sha256(raw).hexdigest(),note=NOTE,new_nodes=len(nodes),new_rules=len(rules),status='STRUCTURAL_COORDINATE_TRANSPORT_PROVED_SEMANTIC_MINENESS_BRIDGE_OPEN',current_contract='formal_contract_R157 for new entries only; inherited layers unchanged',validation=REL+'/VALIDATION.json',gap_ledger=REL+'/GAP_LEDGER.json',proof_assistant_certified=False,empirical_validation=False)
GRAPH.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
(HERE/'MAP_EXTENSION.json').write_text(json.dumps(dict(nodes=nodes,rules=rules,context_links=links),ensure_ascii=False,indent=2)+'\n')
(HERE/'MAP_AUDIT.json').write_text(json.dumps(dict(status='SCOPED_DIRECTION_AND_STRUCTURE_AUDIT_PASS',nodes=len(ids),rules=len(rids),new_nodes=len(nodes),new_rules=len(rules),inherited_nodes_rules_context_unchanged=True,all_rule_endpoints_present=True,unique_ids=True,dependency_acyclic=True,joint_premise_audit=NOTE+' §8',no_deduction_from_report_to_C1_or_U1=True,no_deduction_from_transport_to_mineness=True,global_semantic_consistency_certified=False,proof_assistant_certified=False),indent=2)+'\n')
gaps=dict(inherited='records/R156_Mineness_Bridge_Comparison_20261007/GAP_LEDGER.json',closed_inherited_families=[],entries=[
 dict(id='R157-G1',status='OPEN_REFINED',family='F153-11',issue='B_min semantic interpretation of the transported theta_body substructure is not supplied.',affected=[r,b],forbidden='T1 therefore felt bodily mineness',next='Specify and criticize a fixed semantic bridge; seek independent fiber contrasts.'),
 dict(id='R157-G2',status='OPEN',family='F153-09/F153-10',issue='Completeness and physical realization of candidate theta_body relations are not established.',affected=[s,t,b],next='For a concrete substrate, state the complete K relations and admissible perturbations; do not promote a finite view.'),
 dict(id='R157-G3',status='OPEN',family='F153-12',issue='No cross-domain measurement identifies F_O independently of report.',affected=[rl,b],next='Keep report as partial evidence and compare convergent fallible measures only after B_min is fixed.'),
 dict(id='R157-G4',status='DECLARED_BOUNDARY',family='semantic vocabulary',issue='Adding the word mineness to K would not ground its interpretation by syntax alone.',affected=[v,r],next='Any expanded signature must declare physical and semantic interpretation, not rename theta.'),
 dict(id='R157-G5',status='RESOLVED_SCOPE_ONLY',family='report coverage',issue='Report protocol was at risk of being used outside its domain.',affected=[rl],resolution='Represented as a partial map; total extension and no-report/no-mineness rule are separate assumptions.'),
 dict(id='R157-G6',status='OPEN',family='F153-16/F153-17',issue='Manual classical proof and C1 axiom remain uncertified/unvalidated.',affected=[t,r],next='Preserve conditional status; proof assistant would certify syntax only, not C1 truth or mineness semantics.')])
(HERE/'GAP_LEDGER.json').write_text(json.dumps(gaps,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status='PASS',nodes=len(ids),rules=len(rids),new_nodes=len(nodes),new_rules=len(rules),inherited_preserved=True)))
