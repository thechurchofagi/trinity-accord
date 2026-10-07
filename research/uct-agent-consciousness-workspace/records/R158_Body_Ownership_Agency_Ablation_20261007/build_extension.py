"""R158 scoped extension; run once on the exact R157 parent graph."""
from pathlib import Path
import copy, hashlib, itertools, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REL=str(HERE.relative_to(ROOT)); NOTE=REL+'/Body_Ownership_Agency_Ablation_v0_1.md'
GRAPH=ROOT/'UCT_FORMAL_GRAPH.json'; raw=GRAPH.read_bytes(); g=json.loads(raw)
assert g['revision']=='R157-v1.0'
old=copy.deepcopy(g); anchor=hashlib.sha256((ROOT/NOTE).read_bytes()).hexdigest()
def write(name,data):
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
nodes=[]
def node(suffix,kind,statement,domain,quantifiers,section,status,proof,limits):
    n=dict(id='R158:'+suffix,kind=kind,label=suffix.replace('_',' ').title(),statement=statement,domain=domain,scope=domain,source=NOTE+' '+section,source_lineage=NOTE+' '+section,status=status,proof=proof,counterexamples_and_limits=limits)
    n['formal_contract_R158']=dict(object_domain=domain,quantifiers=quantifiers,bearer_time_signature='As specified per claim; actual token P, candidate c and interval I never conflated. Abstract K-witnesses are not asserted to be actual organisms.',source_anchor=dict(path=NOTE,sha256=anchor,locator=section),premise_routes=[],purpose='Separate bodily ownership and action agency within experience and correct selector closure without adding basal gates.',thought_experiments=NOTE+' §7',open_obligations=['F153-09','F153-10','F153-11','F153-12','F153-17'],machine_formalized=False)
    nodes.append(n);return n['id']
a=node('TARGET_SPLIT','DEFINITION','Distinguish actual bearer P/support s from represented candidate c; distinguish actual membership M, coupling C, body-frame binding B, installed use U, intervention-relative efficacy E, internal judgments J, selected felt targets F, beliefs Q and reports R. Undefined membership is not false membership.','Declared actual token/candidate domain with typed partial membership and protocol-relative reports.','Fixed P,c,I,K per instance; each coordinate has its declared type; no universal F equivalence is asserted.','§2','DECLARED_TARGET_CONTRACT','Typed definitions, with candidate/implementation distinction and intervention convention.','A model hand and a virtual referent require different membership typing; R is not F.')
b=node('NECESSITY_WITNESS_SETUP','ASSUMPTION_PACKAGE','Fix nonempty Omega, total Boolean F and n>=1 total Boolean g_i; define Theta=AND_i g_i. Require jointly an admissible w* in Omega and j in {1,...,n} with F(w*)=1 and g_j(w*)=0. F interpretation is independent of Theta.','Classical two-valued scoped domain; actual application additionally requires physical admissibility and independent target evidence.','For each fixed n,Omega,F,(g_i) satisfying all listed premises, select one declared witness w* and j.','§5 T1','DECLARED_CONJUNCTIVE_ASSUMPTIONS','A one-element abstract domain with F=1 and g_1=0 is jointly satisfiable; not an actual phenomenal witness.','Report-only evidence does not establish F_O; undefined predicates require domain repair, not zero fill.')
c=node('CONJUNCTION_REJECTION','CONDITIONAL_LIMIT','Under NECESSITY_WITNESS_SETUP, not forall w in Omega: F(w)->Theta(w); hence not forall w: F(w)<->Theta(w).','Exactly the fixed classical domain and all simultaneous setup premises.','Every setup satisfying all premises; existential counterexample w*; no assertion that any actual F_O witness has been established.','§5 T1','MANUAL_CLASSICAL_CONDITIONAL_ARGUMENT','g_j(w*)=0 makes Theta(w*)=0; F(w*)=1 falsifies necessity implication and thus biconditional.','Elementary prior mathematics. Requires an independently warranted target witness and admissibility, not arbitrary gate assignments.')
d=node('RELATIONAL_SELECTION_SETUP','ABSTRACT_WITNESS_PACKAGE','Let K have one sort, constant a and unary f. D has carrier {0,1}, a=0, f(0)=1, f(1)=0; theta(x) is x=a and S={0}.','One fully specified finite abstract K-structure.','This concrete abstract structure; h, when used, is any K-isomorphism transporting a and f.','§5 T2','SPECIFIED_FINITE_COUNTERMODEL','All carrier, constant and function assignments are explicit and jointly satisfiable.','Not a human or experiential observation; arbitrary relational selectors of higher arity are tuple relations.')
e=node('SELECTION_CLOSURE_LIMIT','COUNTEREXAMPLE_LIMIT','Definability alone does not guarantee substructure closure: in RELATIONAL_SELECTION_SETUP, f(0)=1 is outside S. R157 formula transport remains valid for the selected relation; closure/physical autonomy are additional obligations.','General not-guaranteed claim witnessed by one finite structure; closure means contains constants and closed under functions in a fixed signature.','There exists a definable selection not closed under a K-function; not every selection is claimed nonclosed.','§5 T2','MANUAL_FINITE_COUNTEREXAMPLE','0 belongs to S while its f-image does not; this refutes the general entailment. Isomorphism carries both selected set and function, preserving the failure.','Purely relational induced substructures may be available; an arbitrary tuple relation still is not itself a carrier. C1 is not refuted.')
f=node('TARGET_SPECIFIC_BRIDGE_PROFILE','OPEN_BRIDGE_SCHEMA','Retain the R157 conjunction only as an unproved joint functional body-use configuration. Compare ownership-oriented body-frame binding/use and agency-oriented source-attribution/use on separately declared target domains. Actual membership and efficacy are separate from judgments; optional coordinates have no proved universal necessity.','Declared actual intervention domain and independently fixed F_O/F_A interpretation, still to be supplied.','Candidate comparison only; no universal necessity, sufficiency, equivalence or basal-experience threshold.','§6','OPEN_REFINED_SCHEMA','Explanatory proposal informed by scoped primary evidence and counterexamples; not deduced as a phenomenal theorem.','Reports, drift and threat measures are fallible; B+U is not established sufficient for familiar mineness; broad route deletion is not supplied.')
rules=[]
for rid,prem,con,bindings in [
 ('r158_conjunction_rejection',[b],c,['same Omega,n,F,g_i and Theta throughout','w* admissible in Omega; j in declared index set','F independently interpreted; all predicates total Boolean']),
 ('r158_selection_closure',[d],e,['same declared K,D,a,f,theta,S','substructure closure uses all K functions and constants','counterexample abstract; no actual experience premise'])]:
    n=next(x for x in nodes if x['id']==con)
    r=dict(id=rid,all_of=prem,conclusion=con,statement=n['statement'],proof_sketch=n['proof'],source=n['source'],kind='SCOPED_CLASSICAL_ARGUMENT',review=n['status'])
    r['formal_contract_R158']=dict(premise_connective='AND',bindings_required=bindings,quantification=n['formal_contract_R158']['quantifiers'],proof_location=n['source'],source_sha256=anchor,machine_proof=False)
    rules.append(r)
for n in nodes:
    n['formal_contract_R158']['premise_routes']=[dict(rule=r['id'],all_of=r['all_of']) for r in rules if r['conclusion']==n['id']]
amendments=[]
for ident,repair in [
 ('R157:COORDINATE_TRANSPORT','The transported selector is a definable relation / tuple support. Do not infer carrier closure, autonomous process or substructure without additional conditions.'),
 ('R157:SEMANTIC_RESIDUAL','Replace the historical word substructure by selected experiential relation / tuple support in the semantic-naming argument. No varying experience of a fixed complete organization is asserted.'),
 ('R157:MINENESS_BRIDGE_SCHEMA','The four-way conjunction is only an unproved joint functional body-use schema; distinguish ownership and agency targets, narrow membership and broad coupling, performed action and available/efficacious routes. Use R158 target profile for current priority.')]:
    n=next(x for x in g['nodes'] if x['id']==ident)
    n['formal_contract_R158']=dict(amends='formal_contract_R157 terminology/scope only; historical statement and contract retained',effective_reading=repair,source_anchor=dict(path=NOTE,sha256=anchor,locator='§§2,5,6,8'),open_obligations=['F153-09','F153-10','F153-11','F153-12','F153-17'],machine_formalized=False)
    amendments.append(dict(id=ident,repair=repair,old_history_preserved=True))
r=next(x for x in g['rules'] if x['id']=='r157_report_coverage')
r['formal_contract_R158']=dict(amends='generic binding checklist only',bindings_required=['same Omega,Omega_rep,Omega_norep and partial M_rep','Omega_norep nonempty for two-extension witness','same codomain with at least two distinct values when two extensions are asserted'],effective_reading='Domain result needs no K-formula or C1 premise. No report-to-F inference.',source=NOTE+' §8',machine_proof=False)
amendments.append(dict(id=r['id'],repair=r['formal_contract_R158'],old_history_preserved=True))
links=[dict(**{'from':x,'to':y},relation=z) for x,y,z in [
 ('R157:MINENESS_BRIDGE_SCHEMA',f,'scope refinement, not inference'),
 ('R157:COORDINATE_TRANSPORT',e,'terminology correction; coordinate theorem retained'),
 (a,f,'target typing for candidate comparison; not proof'),
 ('R156:SNAPSHOT_USE_LIMIT',f,'functional installed-use limit remains; no phenomenal witness'),
 ('R157:REPORT_COVERAGE_LIMIT',c,'independent target witness cannot be supplied by report partiality')]]
g['nodes']+=nodes;g['rules']+=rules;g['context_links']+=links
for before,after in zip(old['nodes'],g['nodes']):
    without={k:v for k,v in after.items() if k!='formal_contract_R158'}
    assert without==before
for before,after in zip(old['rules'],g['rules']):
    assert {k:v for k,v in after.items() if k!='formal_contract_R158'}==before
assert g['context_links'][:len(old['context_links'])]==old['context_links']
ids=[x['id'] for x in g['nodes']];rids=[x['id'] for x in g['rules']]
assert len(ids)==len(set(ids)) and len(rids)==len(set(rids))
deps={x:set() for x in ids}
for r in g['rules']:
    assert r['all_of'] and r['conclusion'] in ids and all(p in ids for p in r['all_of'])
    deps[r['conclusion']].update(r['all_of'])
done=set();stack=set()
def visit(x):
    assert x not in stack
    if x in done:return
    stack.add(x)
    for y in deps[x]:visit(y)
    stack.remove(x);done.add(x)
for x in ids:visit(x)
g['revision']='R158-v1.0';g['base_commit']='d6ee6c53d28d4e6d03822b731307621ab1edad70'
g['research_R158']=dict(parent_branch_head=g['base_commit'],parent_graph_sha256=hashlib.sha256(raw).hexdigest(),note=NOTE,new_nodes=6,new_rules=2,current_contract='formal_contract_R158 for new entries and four explicitly scoped amendments only; all historical fields retained',status='OWNERSHIP_AGENCY_TARGET_SPLIT_AND_SELECTOR_CLOSURE_REPAIRED_BRIDGE_OPEN',proof_assistant_certified=False,empirical_validation=False)
GRAPH.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
write('MAP_EXTENSION.json',dict(nodes=nodes,rules=rules,context_links=links))
write('AMENDMENTS.json',dict(entries=amendments,source=NOTE,history_policy='No inherited field removed or rewritten; effective repairs recorded explicitly.'))

# Finite classical checks support the scoped manual arguments, not actual target truth.
cases=0;witnesses=0
for n in range(1,8):
    for bits in itertools.product((0,1),repeat=n):
        for target in (0,1):
            theta=all(bits);cases+=1
            if target and 0 in bits:
                assert not ((not target) or theta)
                assert target!=theta;witnesses+=1
assert cases==508 and witnesses==247
permutation_results=[]
for image in ((0,1),(1,0)):
    h=dict(enumerate(image));carrier=set(image);a=h[0]
    mapped_f={h[0]:h[1],h[1]:h[0]};selected={x for x in carrier if x==a}
    assert selected=={h[x] for x in (0,)}
    assert mapped_f[a] not in selected
    permutation_results.append(dict(image=list(image),constant=a,selected=sorted(selected),f_of_constant=mapped_f[a],closed=False))
source_checks=[]
for s in g['source_versions']:
    p=ROOT/s['snapshot_workspace_path'];actual=hashlib.sha256(p.read_bytes()).hexdigest()
    assert actual==s['sha256']
    source_checks.append(dict(paper=s['paper'],path=s['snapshot_workspace_path'],sha256=actual,status='PASS'))
write('VALIDATION.json',dict(status='PASS_BOUNDED_CHECKS',boolean_rows=cases,conditional_witness_rows=witnesses,renaming_checks=permutation_results,source_checks=source_checks,interpretation='Boolean rows are abstract assignments, not physiological interventions or phenomenal observations.',proof_assistant=False,raw_data_reanalysis=False))
write('MAP_AUDIT.json',dict(status='PASS_SCOPED_AUDIT',nodes=len(ids),rules=len(rids),new_nodes=6,new_rules=2,unique_ids=True,endpoints_and_all_of_present=True,acyclic=True,inherited_fields_preserved_except_additive_amendments=True,inherited_context_links_preserved=True,semantic_review=NOTE+' §8',joint_premise_review=NOTE+' §5',global_semantic_proof=False,empirical_F_witness=False,basal_gate_added=False,checks_after_selection_result_before_save=['PASS','PASS','PASS'],effective_amendments=[x['id'] for x in amendments]))
gaps=[
 ('R158-G1','REPAIRED_TERMINOLOGY','R157 note §§1–4 and entrypoint prefixes','R157:COORDINATE_TRANSPORT / SEMANTIC_RESIDUAL; any downstream substructure or autonomy reading','{0} selected by x=a in toggle-function structure is not closed.','Use selected relation/tuple support; transport proof retained.','Any substructure claim must establish constants/function closure; autonomy needs physical premises.'),
 ('R158-G2','REPAIRED_SCOPE_BRIDGE_OPEN','R157 theta_body four-conjunction','R157:MINENESS_BRIDGE_SCHEMA and selected ownership/agency interpretation','S1 passive/active condition dissociation; report domain only.','Distinguish F_O/F_A and performed action/available route; conjunction only joint functional case.','Universal necessity/sufficiency of any phenomenal selector remains open.'),
 ('R158-G3','OPEN','ActualAttachment ambiguity','Ownership bridge; actual bearer/candidate relation','Model hand outside anatomy remains causally coupled.','Separate anatomical M from specified coupling C.','No general zero-coupling selected-mineness witness or complete grounding supplied.'),
 ('R158-G4','OPEN','Seven-ablation admissibility and target witness','R158:CONJUNCTION_REJECTION application to F_O/F_A','Abstract zero-bit setting is not a physical intervention; report is not F.','Require all_of domain, totality, admissibility, independent interpretation and witness together.','Actual target witness and independent measurement bridge not supplied.'),
 ('R158-G5','OPEN','U / interoception / affect / persistence necessity','R158:TARGET_SPECIFIC_BRIDGE_PROFILE','Toy deletes declared port/consumer but retains other routes; no phenomenal outcome assigned.','Separate architecture omission from total absence and selected target.','Specify actual intervention domain and convergent evidence; no forced node closure.'),
 ('R158-G6','REPAIRED_BINDINGS','r157_report_coverage formal_contract_R157','Partial report extension limit','Generic theta/K checklist did not describe the actual partial-map proof.','R158 effective checklist states Omega/report subdomains/codomain; no new premise edge.','Cross-domain phenomenal measurement remains open.'),
 ('R158-G7','OPEN','Complete K and C1 experiential interpretation','All actual application and transported selected-target claims','Finite toy/report views omit physical organization; C1 remains stipulated.','Preserve signature/source/actuality levels; no semantic promotion.','Complete physical grounding, C1 empirical justification, B_min and formal proof certification remain separate.')]
write('GAP_LEDGER.json',dict(inherited='records/R157_Structural_Coordinate_and_Mineness_20261007/GAP_LEDGER.json',closed_inherited_families=[],entries=[dict(id=i,status=s,location=l,affected=a,counterexample=c,repaired=r,unresolved=u) for i,s,l,a,c,r,u in gaps]))
write('SOURCE_LEDGER.json',dict(date='2026-10-07',prior_art_not_original=True,pinned_A_sha256=g['source_versions'][0]['sha256'],pinned_read_scope='UCT I v1.2 §§8.11–8.14; 14.7–14.10 targeted windows; R157 note §§1–8',all_ten_hash_checks='VALIDATION.json',full_ten_papers_reread=False,raw_data_reanalysis=False,sources=[
 dict(id='S1',doi='10.3389/fnhum.2012.00040',url='https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2012.00040/full',read_scope='Abstract, moving-hand apparatus/methods, experiment 3 conditions/results',evidence='Ownership/agency report dissociation; passive condition retained apparatus and latent motor capability.'),
 dict(id='S2',doi='10.1371/journal.pone.0156591',url='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0156591',read_scope='Abstract, imitation BCI methods, questionnaire and threat response results/discussion',evidence='Declared EEG command link absent; cue and visual pathways retained. Reports are not direct F observation.'),
 dict(id='S3',doi='10.1371/journal.pone.0021659',url='https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0021659',read_scope='Abstract, methods, drift/ownership result and discussion windows',evidence='Proprioceptive drift and ownership ratings dissociated in specified protocols.'),
 dict(id='S4',doi='10.1371/journal.pone.0206367',url='https://pmc.ncbi.nlm.nih.gov/articles/PMC6198980/',read_scope='Abstract and feeling/belief discussion, not numerical sample reanalysis',evidence='Instruction-dependent feeling/belief reports motivate distinct operational definitions.')]))
print(json.dumps(dict(status='PASS',nodes=len(ids),rules=len(rids),boolean_rows=cases,conditional_witness_rows=witnesses,source_hashes=len(source_checks))))
