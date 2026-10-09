#!/usr/bin/env python3
"""R187 candidate-only MGTD checks. NOT a full semantic map audit."""
import json,csv,hashlib,sys
from collections import Counter,defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent
src=P/'sources'
parent=list(csv.DictReader((src/'PARENT_V111_ID_INVENTORY.csv').open()))
legacy=json.loads((src/'UCT_EFFECTIVE_GRAPH.json').read_text())
parentids=[r['item_id'] for r in parent]
assert len(parent)==1419,len(parent)
assert len(set(parentids))==1419
assert Counter(r['item_type'] for r in parent)=={'node':804,'rule':387,'context':228},Counter(r['item_type'] for r in parent)
oldnodes={n['id']:n for n in legacy['nodes']}
N=[]
def add(id,kind,statement,status='CONDITIONAL_OR_OPEN',domain='Finite controlled state systems with matched declared observation/action interfaces',proof='RESEARCH_NOTE.md'):
 N.append(dict(id=f'R187:{id}',kind=kind,statement=statement,scope=domain,status=status,proof_source=proof,source='R187-20261009 CMA-RESULT-v0.1.0',automatic_premise_truth=False))
add('PORT_CONTRACT','definition','Admissible commands U require actual source/edge/clock identities; equal action names do not establish physically equivalent interventions.',status='DEFINITION')
add('OCCURRENCE_DISTINCTION','definition','One grounded physical relation occurrence may have multiple actual token memberships; distinct synchronized occurrence IDs remain distinct despite equal values or reports.',status='DEFINITION',proof='R185-C1/C2 (pending, source only)')
add('BISIM_RELATION','domain_assumption','A related-state relation preserves all common-action transitions and admitted readouts; stochastic analogue has a relation-preserving kernel coupling.',status='MODEL_GUARD')
add('ALL_POLICY_THEOREM','conditional_theorem','With matched related initial states, PORT_CONTRACT and BISIM_RELATION, all adaptive policy transcript laws agree at every finite horizon; equal-prior discrimination Bayes risk=1/2.',proof='RESEARCH_NOTE.md §2 Proposition 1')
add('DIAGONAL_WITNESS','finite_countermodel','A shared single binary source and m>=2 distinct synchronized binary source loci driven only by a common toggle have identical every-length readout histories.',proof='RESEARCH_NOTE.md §2 + check_models.py')
add('DURATION_LIMIT','inference_limit','More trials cannot distinguish exactly bisimilar interface models; a finite-horizon hidden interaction need not be interface-level bisimulation. No global impossibility without fixed U.',status='SCOPED_NEGATIVE_RESULT')
add('PORT_FIDELITY','open_realization','Independently confirm a physical constituent write rather than an edge/readout rewrite, plus timing, omitted channels and traceable occurrence identity.',status='OPEN_ACTUAL_INSTANCE')
add('SELECTIVE_WITNESS','conditional_theorem','With genuinely constituent-specific write and no compensating synchronization before faithful readout, an off-diagonal output excludes the restricted one-bit shared source model.',proof='RESEARCH_NOTE.md §3')
add('SYNC_ERASURE','counterexample','Copied state may be overwritten by synchronizer before observation, hiding a valid internal selective write.',status='COUNTEREXAMPLE')
add('EDGE_MIMIC','counterexample','A single common-source event plus downstream readout-edge modifier can create same off-diagonal output as separate copy-write.',status='COUNTEREXAMPLE')
add('MULTIBIT_SINGLE','counterexample','A single physical occurrence with two writable internal degrees can exhibit 2-dimensional response rank; rank does not count actual occurrences.',status='COUNTEREXAMPLE')
add('RANK_LIMIT','inference_limit','Measured input-response rank counts controlled directions only under stipulated true physical port basis, not number of experience-bearing events or subjects.',status='SCOPED_NEGATIVE_RESULT')
add('METRIC_GUARD','domain_assumption','Known calibrated Euclidean two-output channels, fixed selective delta, best free common-mode t, and independent two-sided readout errors <=epsilon.',status='MODEL_GUARD')
add('NOISE_SEPARATION','conditional_theorem','Exact model gap is |delta|/sqrt(2); two-sided error balls disjoint if |delta|>2sqrt(2)epsilon.',proof='RESEARCH_NOTE.md §4')
add('PROB_LEAK_GUARD','domain_assumption','Reset independent Bernoulli mismatch in copied model with fixed p and exact zero mismatches for shared model; equal priors.',status='MODEL_GUARD')
add('TV_SHARP','conditional_theorem','After T independent reset trials TV=1-(1-p)^T and exact Bayes classification error=(1-p)^T/2; p=0 persists at 1/2.',proof='RESEARCH_NOTE.md §5')
add('APPROX_COUPLING','conditional_theorem','If per-step matched-history coupling failure<=eta under a common policy, T-step TV<=1-(1-eta)^T<=Teta and equal-prior error>=(1-min(1,Teta))/2.',proof='RESEARCH_NOTE.md §5 coupling extension')
add('LINEAGE_GUARD','open_realization','Selective intervention alters the physical process at test epoch; to infer earlier undisturbed occurrence identity requires independent same-bearer temporal lineage and noncircular intervention mapping.',status='OPEN_ACTUAL_INSTANCE')
add('SUBJECT_COUNT_LIMIT','inference_limit','Neither occurrence count nor incidence multiplicity nor intervention rank entails numeric phenomenal event identity, number of subjects, or experiential intensity.',status='SCOPED_NEGATIVE_RESULT')
add('UCT_APPLICATION','conditional_interpretation','When independent actual token admission, complete same-instance K and a comparison-invariant physical distinction hold, inherited C1-OI can conditionally distinguish complete types; not a named quality or existence gate.',status='OPEN_ACTUAL_AND_PHENOMENAL')
add('NOVELTY_BOUNDARY','research_status','Uses classical bisimulation, intervention hierarchy, Euclidean projection, Le Cam bounds; project-specific synthesis beyond R185/OL/CM, historical priority unverified.',status='PRIORITY_UNVERIFIED')
add('REAL_SYSTEM_TARGET','open_problem','Choose one actual retina/prosthetic/duplicated-compute instance with traceable physical event source and full intervention/observation boundary; measure whether branch and source writes are separable.',status='OPEN_NEXT')

rules=[]
def rule(i,pre,head,guard):
 rules.append(dict(id=f'R187:r_{i}',kind='DEDUCTIVE_CONDITIONAL',all_of=[f'R187:{x}' for x in pre],conclusion=f'R187:{head}',statement=guard,guard=guard,binding='Same actual experiment interface, time interval and correctly typed source/readout port instances',status='PENDING_MAP',no_assumption_promotion=True,proof_source='RESEARCH_NOTE.md'))
rule('allpolicy',['PORT_CONTRACT','BISIM_RELATION'],'ALL_POLICY_THEOREM','Identical related initial conditions; same fully supported common action algebra and observations, with bisimulation closure for every allowed action.')
rule('diagonal',['PORT_CONTRACT'],'DIAGONAL_WITNESS','One binary source versus distinct copied binary sources initially equal; global toggles only, faithful readouts, m>=2.')
rule('duration',['ALL_POLICY_THEOREM','DIAGONAL_WITNESS'],'DURATION_LIMIT','Do not widen from common interface to arbitrary physical interventions or from output identity to token identity.')
rule('selective',['PORT_CONTRACT','PORT_FIDELITY','DIAGONAL_WITNESS'],'SELECTIVE_WITNESS','Physical copy-locus-specific writer independently verified, comparator limited to one single bit source and unchanged faithful readout, synchronizer isolated.')
rule('noise',['METRIC_GUARD','SELECTIVE_WITNESS'],'NOISE_SEPARATION','Bounded calibrated errors, same physical port + time, no branch modifier or hidden synchronizer action.')
rule('tv',['PROB_LEAK_GUARD'],'TV_SHARP','Independent reset trials and fixed p, zero discrepancy in source model; Bayes error uses equal priors.')
rule('coupling',['PORT_CONTRACT','BISIM_RELATION'],'APPROX_COUPLING','For approximate case, a declared matched-history coupling of failure probability<=eta must be supplied independently; exact bisim alone gives eta=0.')

context=[]
def ctx(k,source,target,reason):context.append(dict(id=f'R187:ctx_{k}',source=source,target=f'R187:{target}',relation='CONTEXT_NOT_DEDUCTION',reason=reason))
ctx('r185','R185:SAME_OCCURRENCE','OCCURRENCE_DISTINCTION','R185 pending occurrence identity definition; no premise promotion')
ctx('r185_copy','R185:COPIED_COUNTERMODEL','DIAGONAL_WITNESS','All-policy extension of copied/shared finite witness')
ctx('r186','R186-HOM-20261009','DURATION_LIMIT','Finite-depth hidden effects differ from interface-structural nonidentifiability')
ctx('cm','CM20261009:CAUSAL_MASK','SYNC_ERASURE','Corrective/synchronizer masking; CM is separately pending')
ctx('ol','OL20261009','NOISE_SEPARATION','Classical finite-observation projection used at physical port boundary')
ctx('c1','A:C1_OI','UCT_APPLICATION','Only conditional same-complete-signature type inference')
ctx('u1','A:U1','SUBJECT_COUNT_LIMIT','No experience gate or subject-number identity')
ctx('p3','A:P3','LINEAGE_GUARD','Local persistence must be grounded')
ctx('ta25','C:P2_COORD','RANK_LIMIT','Prior target-conditional factorization; coordinate views do not count events')

ext=dict(schema='uct-pending-map-module/1.1',research_id='R187-20261009',result_version='CMA-RESULT-v0.1.0',base_completed_release='UCT-MAP-v1.1.1',candidate_map_id='UCT-MAP-v1.1.2-R187-candidate.1',status='PENDING_MAP',audit_status='AUDIT_INCOMPLETE',enabled_as_established_premises=False,
             common_application='Finite deterministic/stochastic event-source models, matched control language/ports/clock; actual physical event identity and UCT basal-experience axiom remain independent assumptions.',
             nodes=N,rules=rules,context_links=context,reference_sources=['RESEARCH_NOTE.md','PRIOR_ART.md','check_models.py','TEST_RESULTS.json'],note='R185/CM/R186/OL are compared as source precedents; pending R185/CM/R186 are not used in deductive all_of.')
(P/'MAP_EXTENSION.json').write_text(json.dumps(ext,ensure_ascii=False,indent=2)+'\n')

parentidsset=set(parentids)
newids=[x['id'] for x in N]+[x['id'] for x in rules]+[x['id'] for x in context]
assert len(newids)==len(set(newids)) and not (set(newids)&parentidsset)
assert all(set(r['all_of'])<=set(n['id'] for n in N) for r in rules)
assert all(r['conclusion'] in {n['id'] for n in N} for r in rules)
assert all(r['guard'] and len(r['all_of']) and r['binding'] for r in rules)
assert all(x['relation']=='CONTEXT_NOT_DEDUCTION' for x in context)
assert not any(r['conclusion'] in parentidsset for r in rules)

graph=defaultdict(list)
for r in rules:
 for p in r['all_of']:graph[p].append(r['conclusion'])
seen=set();stack=set()
def dfs(v):
 if v in stack:raise ValueError('Cycle '+v)
 if v in seen:return
 stack.add(v)
 for w in graph[v]:dfs(w)
 stack.remove(v);seen.add(v)
for v in set(n['id'] for n in N):dfs(v)

# Individual inherited record coverage reflects exactly what this turn reviewed;
# generic archival statuses from previous version are not re-issued as new judgments.
anchors=['A:C1','A:C1_OI','A:U1','A:P3','A:P6','A:TOKEN_CRITERIA','A:ACTUAL_TOKEN','C:P2_COORD','R177:COMPENSATED_FEATURE_PRESERVATION','R177:SOURCE_FEATURE_SEPARATION','R184:RTR','R184:OVERLAP_NEXT']
anchor_found={p for p in anchors if p in oldnodes}
coverage=[]
for r in parent:
 x=r['item_id'];source=oldnodes.get(x)
 if x in anchor_found:
  tag='SCOPED_INHERITED_CLAUSE_READ_FROM_VERIFIED_V100_SNAPSHOT'
 else:tag='ID_INVENTORY_CHECK_ONLY_NOT_THIS_CYCLE_SEMANTIC_REVIEW'
 coverage.append({'item_id':x,'item_type':r['item_type'],'source_release':r['source_release'],
 'previous_release_review':r['review'],'source_record_sha256':r['source_record_sha256'],
 'this_cycle_review_status':tag,'full_v111_source_text_available_here':False,
 'comments':('Compared historical source meaning only, full current source hash compatibility not independently confirmed.' if x in anchor_found else 'Do not promote prior release review into fresh R187 semantic review.')})
(P/'REVIEW_COVERAGE.json').write_text(json.dumps(coverage,indent=2)+'\n')

results=json.loads((P/'TEST_RESULTS.json').read_text())
assert results['outcome']=='PASS'

report={"research_id":"R187-20261009","version":"CMA-RESULT-v0.1.0","current_completed_map":"UCT-MAP-v1.1.1",
"old_parent_item_id_inventory":len(parent),"parent_types":dict(Counter(r['item_type'] for r in parent)),
"original_v100_node_statement_sample_count":len(anchor_found),"missing_old_sample_ids":sorted(set(anchors)-anchor_found),
"new_nodes":len(N),"new_candidate_rules":len(rules),"new_context_not_inference":len(context),
"total_candidate_items_not_authoritative":len(parent)+len(N)+len(rules)+len(context),
"fresh_whole_item_semantic_review_completed":False,"audit_state":"AUDIT_INCOMPLETE",
"current_full_v111_effective_graph_loaded":False,"R185_pending_became_premise":False,
"R186_625_review_debt_closed":False,"existing_v111_map_modified":False,
"structural_checks":{"unique_new_ids":True,"no_collision_with_parent_id_inventory":True,"deductive_premise_bindings_complete":True,"rule_guards_nonempty":True,"acyclic_candidate_only":True,"no_old_rule_conclusion_replaced":True,"contexts_not_inference":True,"all_old_suspensions_retained_by_not_updating_map":True},
"uncertainty":"Incomplete latest binary capsule access and absence of a full new semantic census; even passing finite tests would not discharge application or phenomenal bridges.",
"test_file_sha256":hashlib.sha256((P/'TEST_RESULTS.json').read_bytes()).hexdigest()}
(P/'AUDIT_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
