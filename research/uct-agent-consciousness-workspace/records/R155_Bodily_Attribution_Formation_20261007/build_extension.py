"""Append a scoped R155 extension; keep every inherited node/rule unchanged."""
from pathlib import Path
import copy, hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GRAPH = ROOT/'UCT_FORMAL_GRAPH.json'
PARENT = '5123c4c20d09fc7102225376ac30c943ed48090d'
REL = str(HERE.relative_to(ROOT))
NOTE = REL+'/Bodily_Action_Attribution_v0_1.md'
raw = GRAPH.read_bytes()
g = json.loads(raw)
assert g['revision'] == 'R154-v1.0', 'Run once against the pinned parent graph.'
old_nodes, old_rules, old_links = copy.deepcopy(g['nodes']), copy.deepcopy(g['rules']), copy.deepcopy(g['context_links'])
source_hash = hashlib.sha256((ROOT/NOTE).read_bytes()).hexdigest()
model = 'Fixed T>=2, actual-bearer/candidate/port assignment if realized, externally fixed unbiased schedule, n_O,n_A<=T; independent Bernoulli(1/2) H,K priors and conditionally independent trials; X likelihoods 3/4 vs 1/4; randomized U with K=1 noisy-copy Y (error 1/4), K=0 independent fair Y; Z=1[Y=U]; count registers, exact finite rational readouts, theta=2/3 and two installed consumer roles. Statistical hypotheses, actual attachment and experiential targets are distinct.'
nodes = []
def node(suffix, kind, statement, domain, section, proof, limits, status='MANUAL_CONDITIONAL_MATHEMATICAL_ARGUMENT'):
    n = dict(id='R155:'+suffix, kind=kind, label=suffix.replace('_',' ').capitalize(), statement=statement,
             domain=domain, scope=domain, source=NOTE+' '+section, source_lineage=NOTE+' '+section,
             status=status, proof=proof, counterexamples_and_limits=limits)
    n['formal_contract_R155'] = dict(object_domain=domain,
        quantifiers='Parameters fixed per instance; all legal histories within T unless the explicitly separate unbounded finite-state proposition applies. Existential witnesses are not universal biological claims.',
        bearer_time_signature='Same bearer/candidate/ports, temporal grain, trial schedule and typed state/use roles within each comparison; actual realization is separately required.',
        source_anchor=dict(path=NOTE,sha256=source_hash,locator=section),
        purpose='Positive formation model for bodily/action attribution, with explicit limits on interpreting it as felt mineness.',
        machine_formalized=False, open_obligations=['F153-09','F153-10','F153-11','F153-16','F153-17'],
        thought_experiments='Note §7: formation, abacus/calculator, human implementation, memory/rewiring.')
    nodes.append(n)
    return n['id']

m=node('MODEL','DEFINITION_AND_ASSUMPTION_PACKAGE',model,'Finite stochastic acquisition device M, not a definition of basal experience.','§§2–3','Explicit definitions and simultaneous assumptions; no deduction of their physical truth.','Coupled priors/noise, biased selection, drifting laws, alternative efficacy mappings and unbounded acquisition require a changed contract.','DECLARED_MODEL_NOT_PHYSIOLOGICAL_VALIDATION')
p1=node('FORMATION','CONDITIONAL_RESULT','For every legal M history, q_O=3^(2r-n_O)/(1+3^(2r-n_O)) and q_A=3^s/(3^s+2^n_A) equal their model posteriors; finite counter updates realize them. For a fixed finite history, posterior dependence on positive prior/likelihood parameters is continuous; threshold consumption may be discontinuous.',model,'§4 P1','Multiply likelihood ratios 3 or 1/3 and 3/2 or 1/2; independent priors/noises cancel other-channel evidence. Normalize positive odds. Finite state counts and positive-denominator ratios give the realization/continuity claims.','Correct relative to M, not guaranteed latent truth. Missing channel data retain prior 1/2. No experiential onset claim.')
p2=node('SEPARATION','CONDITIONAL_RESULT','At n_O=n_A=2, X in {11,00} and Z in {11,00} give q_O in {9/10,1/10}, q_A in {9/13,1/5}; theta=2/3 realizes all four consumer pairs, each with positive conditional probability for every H,K.',model,'§4 P2','Substitute counts in P1 and compare with fixed theta; positive likelihoods and independence give support.','Functional source/efficacy attribution only. Not a universal phenomenal dissociation or actual attachment change.')
p3=node('ERROR','CONDITIONAL_RESULT','Every finite legal history leaves positive posterior mass on every latent pair H,K. The high/high specified history has conditional probability 1/64 when H=K=0 and joint prior-weighted probability 1/256.',model,'§4 P3','Products of positive likelihoods and priors remain positive; normalize. The false-high witness is (1/4)^2(1/2)^2, multiplied by prior 1/4 for the joint event.','No inference from posterior confidence to actual membership or felt mineness; even a correctly inferred shared external source need not belong to the containing assembly.')
p4=node('MEMORY_BOUNDARY','CONDITIONAL_RESULT','Copying installed state (2,2,2,2) over (2,0,2,2), with ports/attachment fixed, changes q_O and its consumer while q_A remains 9/13. Separately, no deterministic finite-state updater with state-only fixed readout and no external unbounded clock/memory can reproduce exact q_O for all unbounded all-success histories.',model+' The unbounded clause deliberately drops the finite horizon and tests a separate finite-state exactness demand.','§4 P4','Substitute copied counters. For the separate impossibility, outputs 3^n/(1+3^n) are infinitely many distinct numbers; a finite-state fixed readout has finitely many outputs.','Installed memory differs from R147 report-isolated records. Copying breaks automatic posterior/provenance validity and proves no numerical identity or experience transfer.')
target=node('SELECTED_TARGET','DEFINITION_AND_ASSUMPTION_PACKAGE','Fix nonempty actual configuration domain Omega, common bearer/window/signature/target convention, finite descriptor J:Omega->Jspace and independently specified selected experiential target F:Omega->Fspace. Do not define F from J or from a report to make the desired bridge true.','Actual configurations with a fixed target convention; no claim that a physically adequate J or identifiable mineness F has already been supplied.','§5','Typed target contract, not evidence that its phenomenological instantiation is known.','A mathematical target can be stipulated, but its mineness interpretation remains open.','DECLARED_TARGET_CONTRACT')
fiber=node('BRIDGE_CRITERION','CONDITIONAL_RESULT','A fixed decoder psi on the realized descriptor image with F=psi∘J exists iff F is constant on every J-fiber. This criterion supplies no selected mineness semantics, injectivity, monotonicity or empirical measurement bridge.','The shared Omega,J,F contract of R155:SELECTED_TARGET; decoder required only on realized J values.','§5','Necessity follows by equal decoder input. For sufficiency assign each realized J the unique F value of its nonempty fiber. Application of existing C:P2_COORD.','No premises in the acquisition device establish the required phenomenal F or its fiber constancy.')
bridge=node('MINENESS_OBLIGATION','OPEN_OBLIGATION','To interpret the acquisition device as a model of selected felt mineness, independently ground actual realization, selected experiential target, fixed output-blind interpretation, descriptor sufficiency/fiber constancy on a specified domain and an empirical measurement bridge when observations are used. These conditions remain open.','Restricted bodily/action-related mineness; neither all selfhood nor basal consciousness.','§§5,8','Obligation ledger only; no proof edge from functional acquisition to felt mineness.','C1 complete experiential identity does not by itself select this coordinate; naming a register ownership is insufficient.','OPEN_NOT_DERIVED')

rules=[]
def rule(id, premises, conclusion):
    n=next(n for n in nodes if n['id']==conclusion)
    r=dict(id=id,all_of=premises,conclusion=conclusion,statement=n['statement'],proof_sketch=n['proof'],source=n['source'],kind='DEDUCTIVE_APPLICATION',review=n['status'])
    r['formal_contract_R155']=dict(relation_type=r['kind'],premise_connective='AND',alternative_routes='Separate rule IDs denote OR alternatives; no unstated physiological or experiential premise is discharged.',
        bindings_required=['same model parameters and legal histories','same target/bearer/ports/time grain where shared','fixed consumer and evidence protocol','no observational/interventional substitution'],
        quantification=n['formal_contract_R155']['quantifiers'],proof_location=n['source'],source_sha256=source_hash,
        review_status=n['status'],machine_proof=False)
    rules.append(r)
rule('r155_formation',[m],p1)
rule('r155_separation',[m,p1],p2)
rule('r155_error',[m,p1],p3)
rule('r155_memory_boundary',[m,p1],p4)
rule('r155_selected_bridge',[target,'C:P2_COORD'],fiber)
for n in nodes:
    n['formal_contract_R155']['premise_routes']=[dict(rule=r['id'],all_of=r['all_of']) for r in rules if r['conclusion']==n['id']]
links=[
    dict(**{'from':'A:C1','to':bridge},relation='experiential axiom does not independently identify the selected mineness coordinate'),
    dict(**{'from':'A:U1','to':m},relation='consumer threshold is not a basal experience gate'),
    dict(**{'from':'R146:SELF_CONTRACT','to':m},relation='target/grounding/use distinctions; source estimate is not automatically an own-target estimator'),
    dict(**{'from':'R147:ROUTING_LIMIT','to':p3},relation='grounded routing counterexample motivates separation of prediction and attachment; context not a Bayes proof premise'),
    dict(**{'from':'R147:MEMORY_LIMIT','to':p4},relation='different isolation assumptions: active consumer memory versus report-only record'),
    dict(**{'from':fiber,'to':bridge},relation='criterion states the unfulfilled selected-target sufficiency obligation')]
g['nodes']+=nodes;g['rules']+=rules;g['context_links']+=links
g['revision']='R155-v1.0';g['base_commit']=PARENT
g['research_R155']=dict(parent_commit=PARENT,parent_graph_sha256=hashlib.sha256(raw).hexdigest(),record=NOTE,new_nodes=len(nodes),new_rules=len(rules),
    status='FINITE_FUNCTIONAL_FORMATION_MODEL_WITH_OPEN_MINENESS_BRIDGE',
    current_contract='R155 for new nodes/rules only; inherited R154/R153 effective contracts unchanged',
    claims='Classical Bayesian construction and finite-state arguments; no broad novelty, physiological or phenomenal validation.',
    gap_ledger=REL+'/GAP_LEDGER.json',validation=REL+'/VALIDATION.json')
assert g['nodes'][:len(old_nodes)]==old_nodes and g['rules'][:len(old_rules)]==old_rules and g['context_links'][:len(old_links)]==old_links
ids=[n['id'] for n in g['nodes']];rids=[r['id'] for r in g['rules']]
assert len(ids)==len(set(ids)) and len(rids)==len(set(rids))
assert all(r['conclusion'] in ids and all(p in ids for p in r['all_of']) for r in g['rules'])
# Validate the directed dependency graph, including inherited routes, for cycles.
deps={i:set() for i in ids}
for r in g['rules']:deps[r['conclusion']].update(r['all_of'])
visited=set();active=set()
def visit(i):
    assert i not in active, ('cycle',i)
    if i in visited:return
    active.add(i)
    for p in deps[i]:visit(p)
    active.remove(i);visited.add(i)
for i in ids:visit(i)
GRAPH.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
(HERE/'MAP_EXTENSION.json').write_text(json.dumps(dict(nodes=nodes,rules=rules,context_links=links),ensure_ascii=False,indent=2)+'\n')
gaps=[
    dict(id='R155-G1',status='OPEN',family='F153-11',issue='Independent selected felt-mineness target and fixed interpretation not supplied.',consequence='No P1–P4 to felt-mineness theorem.',next='Compare candidate selected-target bridges on a fixed domain; reject any that define their target from their predictor.'),
    dict(id='R155-G2',status='OPEN',family='F153-09/F153-10',issue='Actual realization and constitutive descriptor adequacy are not established.',consequence='Functional toy is not a complete physical organization or unique bearer criterion.',next='Specify physically witnessed typed roles and retained/omitted structure for each proposed realization.'),
    dict(id='R155-G3',status='DECLARED_LIMIT',family='M',issue='Factorized prior/noise, fixed likelihoods and unbiased schedule are restrictive.',consequence='Dependent H=K witness breaks separate posterior update.',next='Use joint updating only for a specified relevant coupled case; do not silently reuse P1.'),
    dict(id='R155-G4',status='DECLARED_LIMIT',family='M',issue='Passive/no-action observation is missing evidence, not a failed command.',consequence='Neutral agency estimate implies no phenomenal absence.',next='Separate passive agency target and its evidence protocol if required.'),
    dict(id='R155-G5',status='OPEN',family='F153-12',issue='No human-data fit or independent mineness measurement bridge.',consequence='Four functional outcomes are not a new empirical dissociation.',next='Use cited work as antecedent and constraint; test specified bridge without outcome-driven refitting.'),
    dict(id='R155-G6',status='RESOLVED_SCOPE_ONLY',family='finite memory',issue='Unbounded exact update conflicts with finite state-only storage.',consequence='Finite-T claim retained; no unbounded exact finite-state claim.',next='Declare approximation/forgetting/storage change before extending horizon.'),
    dict(id='R155-G7',status='OPEN',family='F153-16/F153-17',issue='No proof-assistant certification or derivation of experiential interpretation from uninterpreted mathematics.',consequence='Manual conditional arguments only; C1 remains an axiom.',next='Keep semantic and mathematical obligations separate.')]
(HERE/'GAP_LEDGER.json').write_text(json.dumps(dict(inherited_ledger='records/R154_All_Rule_Proof_Review_20261007/GAP_LEDGER.json',inherited_families_closed=[],entries=gaps),ensure_ascii=False,indent=2)+'\n')
audit=dict(status='STRUCTURAL_EXTENSION_CHECKS_PASS',nodes=len(ids),rules=len(rids),new_nodes=len(nodes),new_rules=len(rules),inherited_nodes_rules_and_links_unchanged=True,all_rule_endpoints_present=True,unique_ids=True,dependency_acyclic=True,manual_joint_audit=NOTE+' §8',source_sha256=source_hash,global_semantic_consistency_certified=False,proof_assistant_certified=False)
(HERE/'STRUCTURAL_VALIDATION.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit))
