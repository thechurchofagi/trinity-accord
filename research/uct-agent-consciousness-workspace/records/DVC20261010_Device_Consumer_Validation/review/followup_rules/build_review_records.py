"""Serialize an already performed human core-field audit; not a semantic test."""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/scratch/465328c0080c')
OUT = ROOT / 'workbench/doi20261010/map_followup_rules'
BASE = ROOT / 'workbench/audit/baseline/UCT_EFFECTIVE_GRAPH.json'
PREVIOUS = ROOT / 'workbench/doi20261010/dvc_review/BASELINE_PER_ID_READ_SCOPE.json'
CANDIDATE_ROOT = ROOT / 'uct_repo/research/uct-agent-consciousness-workspace/records/DVC20261010_Device_Consumer_Validation'
CBI = ROOT / 'uct_repo/research/uct-agent-consciousness-workspace/records/CBI20261010_Consumer_Branch_Isolation/RESEARCH_NOTE.md'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def record_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',', ':')).encode()).hexdigest()

def write(name, value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def at(value, path):
    for part in path.strip('/').split('/'):
        value = value[int(part)] if isinstance(value,list) else value[part]
    return value

def leaves(value, path):
    if isinstance(value,dict) and value:
        return [p for key,v in value.items() for p in leaves(v,path+'/'+str(key))]
    if isinstance(value,list) and value:
        return [p for i,v in enumerate(value) for p in leaves(v,path+'/'+str(i))]
    return [path]

def omitted(value, paths, path=''):
    if path in paths:
        return []
    if not any(p.startswith(path+'/') for p in paths):
        return [path]
    if isinstance(value,dict):
        return [p for key,v in value.items() for p in omitted(v,paths,path+'/'+str(key))]
    if isinstance(value,list):
        return [p for i,v in enumerate(value) for p in omitted(v,paths,path+'/'+str(i))]
    raise ValueError('Reading path not realized in source object: '+path)

graph=json.loads(BASE.read_text())
rules={r['id']:r for r in graph['rules']}
old=json.loads(PREVIOUS.read_text())
old_rules={x['item_id']:x for x in old['items'] if x['item_type']=='rule' and x['reading_status']=='SCOPED_FIELDS_READ_COMPATIBILITY_REVIEWED'}
index=json.loads((OUT/'CARD_INDEX.json').read_text())['rules']
supplement=json.loads((OUT/'PRIOR137_CORE_MATERIALIZATION.json').read_text())['items']
notes={int(r['ordinal']):r['local_dvc_assessment'] for r in csv.DictReader((OUT/'SEMANTIC_NOTES.tsv').open(),delimiter='\t')}
assert set(notes)==set(range(287))
assert len(old_rules)==137 and len(index)==287
assert {x['id'] for x in index}.isdisjoint(old_rules)
assert {x['id'] for x in index}|set(old_rules)==set(rules)
assert sha(BASE)==old['graph_sha256']
status_fields='effective_status status premise_truth_discharged_by_review map_status declaration_role conditional_declaration_available mathematical_registry_availability registry_status'.split()
conclusion_supp={x['rule_id']:x for x in json.loads((OUT/'CONCLUSION_TEXT_SUPPLEMENT.json').read_text())}

def supplemental_assessment(rid):
    if rid.startswith('a'):
        return ('The additional core contract preserves its exact root-premise route and common bearer, interval, signature, law and interpretation. Actual-token admission, complete equivalence, history, continuity, self witnesses and bridge directions apply only where expressly listed; DVC does not manufacture any such premise from a device label, model success or missing report. C1/U1 gain no new intake threshold.')
    if rid.startswith('b'):
        return ('The additional core contract retains the particular framework bridge or graph/model premise, with AND within a route and alternative rules kept separate. DVC device M_D/P_E signals and exploratory endpoints do not certify the corresponding neural, language, workspace or theoretical-translation premises.')
    if rid.startswith('c'):
        return ('The additional core contract retains the exact fixed-J, set-map, selection, decision, memory, transcript or finite-loss root package shown for this rule. The reanalysis does not turn a selected response statistic into a complete capability ordering, evolutionary law, physiological input model or experiential magnitude.')
    if rid.startswith('d129'):
        return ('The path, payoff, dependence, grid or additive-class assumptions listed here remain jointly fixed. DVC makes no inference from separately matched margins to their joint law and does not promote a device gate setting into actual whole-process equivalence.')
    if rid.startswith('r147'):
        return ('The routing model, memory isolation and actual bridge remain distinct premises. This is inherited source-routing coverage; DVC contributes its explicit arrival/capture/read contract and does not claim a new general theorem that equal outputs can conceal routing differences.')
    if rid.startswith('r149_ta18'):
        return ('The named TA18 witness, pair-separation, bridge, null-equivalence or germ contract remains the entire scoped import. DVC gives neither a new proof of that historical result nor actual phenomenal premise discharge.')
    if rid.startswith('r169'):
        return ('The newly read quantifier stays on the declared graph/component/hidden-context domain, with simultaneous budgets and the same pre-compensation consumer/effect definition. Invalid calibration cannot be promoted to a mediator null, and DVC does not close the graph beyond that certificate.')
    if rid.startswith('r171'):
        return ('The newly read target, admissible-world, direct-versus-reachable and certificate clauses stay explicit. Proper finite observations do not prove universal closure. Effective actual applications additionally require their typed, jointly discharged external obligations; all remain OPEN for DVC hardware.')
    if rid.startswith('r172'):
        return ('Both local certificates, every compatibility clause and the same actual application must be supplied together. Corrected application, role bridge, actual path, C1 instance and K grounding are not inferred from node registration or finite code execution; no complete-organization promotion follows.')
    if rid.startswith('r173'):
        return ('The history comparison uses alternative histories, actual sorted H0/eta roles and one common P/I0/K transport with all effective R172 premises. An external archive, test list or copied DVC header does not supply the actual retained coordinate.')
    if rid.startswith('r174'):
        return ('The exact S/C/H domain, faithful source perturbation and clamp, admitted finite rival class and separate actual C1 grounding remain explicit. Finite probes do not eliminate an unexcluded hidden gate; neither report nor F_order is turned into a basal gate or unique-owner rule.')
    if rid.startswith('r175') or rid.startswith('r176'):
        return ('The effective boundary/replacement and same-domain binding are retained. DVC does not revive a superseded target claim, conjoin alternative histories, or add a named experiential conclusion from present-slice or order evidence.')
    special={
      'R187:r_allpolicy':'Bisimulation closure is required for every allowed action, with related initial states and the same fully supported algebra; the finite DVC run is not such an unrestricted certificate.',
      'R187:r_diagonal':'The source-versus-copies witness has m>=2, initial equality, faithful readouts and global toggles only. Copy-locus writers are a different declared intervention class.',
      'R187:r_duration':'Common-interface agreement cannot be widened to arbitrary physical interventions or token identity by increasing run duration.',
      'R187:r_selective':'A verified physical copy-locus writer, a one-bit source comparator, faithful readout and isolated synchronizer are all required; DVC actual hardware admission does not yet establish them.',
      'R187:r_noise':'The exact two-output metric/error family is mathematical; physical ports, timing and exclusion of branch rewriting or hidden synchronization remain independent obligations.',
      'R187:r_tv':'Independent resets, fixed p, zero source-model discrepancy and equal Bayes priors are explicit conditions, not facts established by the public psychometric fits.',
      'R187:r_coupling':'An approximate matched-history coupling with failure probability <= eta must be independently supplied; high observed correlation alone is insufficient.',
      'R188:r_gap':'The K=2,L=1 and uniform external (T,J) comparison shares target/scoring/deadline while changing internal context incidence; DVC does not conjoin those different mechanisms.',
      'R188:r_repair':'Binary feedback arriving before a reply and a three-symbol feedforward code are separate strengthened interfaces; neither is free access in the (2,1) baseline.',
      'R188:r_complete':'The complete-graph specialization retains integer n>=2, uniform edge/endpoint law and C=min(n,K^L) with its stated integer division. No neural channel or phenomenal dimension bound follows.'
    }
    if rid in special:
        return special[rid]
    if rid.startswith('R188'):
        return ('The declared coding/profile/interaction contract and disabled-premise status are retained. DVC does not widen the operation alphabet, grant earlier feedback for free, or turn a selected source-consumer score into complete UCT or human-target identification.')
    raise ValueError(rid)

items=[]
for ordinal,entry in enumerate(index):
    rid=entry['id'];r=rules[rid]
    paths=list(entry['field_paths_materialized'])
    paths += ['/'+k for k in status_fields if k in r]
    if 'new_scientific_execution' in r.get('formal_contract',{}):
        paths.append('/formal_contract/new_scientific_execution')
    paths=list(dict.fromkeys(paths))
    item={'id':rid,'item_type':'rule','review_pass':'PREVIOUSLY_UNREAD_287_CORE_FIELDS',
      'source_record_sha256':record_sha(r),'reading_status':'DECLARED_CORE_FIELDS_READ_AND_DVC_COMPATIBILITY_REVIEWED',
      'whole_value_paths_read':paths,'exact_leaf_paths_read':[p for path in paths for p in leaves(at(r,path),path)],
      'unread_subtree_paths':omitted(r,set(paths)),
      'read_core_values':{p:at(r,p) for p in paths},
      'local_dvc_assessment':notes[ordinal],
      'result':'NO_DVC_INDUCED_CORE_RULE_REWRITE_REQUIRED_WITH_DISABLED_SCOPED_DVC_STATUS',
      'historical_proof_revalidated':False,'actual_premises_discharged':False,'named_phenomenal_premises_discharged':False,
      'scientific_promotion':False,'reviewer_controlled_status_changed':False}
    if rid in conclusion_supp:
        item['additional_conclusion_record_excerpt_read']=conclusion_supp[rid]
        item['additional_conclusion_scope']='Only the listed target-node fields; no full-node or proof completion credit.'
    items.append(item)

for entry in supplement:
    rid=entry['id'];r=rules[rid];prev=old_rules[rid]
    new_paths=entry['additional_paths_materialized']
    paths=list(dict.fromkeys(entry['previous_paths_read']+new_paths))
    items.append({'id':rid,'item_type':'rule','review_pass':'PRIOR137_OMITTED_CORE_BINDINGS_SUPPLEMENT',
      'source_record_sha256':record_sha(r),'reading_status':'PREVIOUS_STATEMENT_SCOPE_PLUS_NEW_CORE_CONTRACT_READING',
      'previous_frozen_audit_paths':entry['previous_paths_read'],'newly_read_whole_value_paths':new_paths,
      'whole_value_paths_read_cumulative':paths,'exact_leaf_paths_read_cumulative':[p for path in paths for p in leaves(at(r,path),path)],
      'unread_subtree_paths':omitted(r,set(paths)),
      'newly_read_core_values':{p:at(r,p) for p in new_paths},
      'previous_local_assessment':prev['semantic_assessment'],
      'additional_core_assessment':supplemental_assessment(rid),
      'result':'NO_DVC_INDUCED_CORE_RULE_REWRITE_REQUIRED_WITH_DISABLED_SCOPED_DVC_STATUS',
      'historical_proof_revalidated':False,'actual_premises_discharged':False,'named_phenomenal_premises_discharged':False,
      'scientific_promotion':False,'reviewer_controlled_status_changed':False})

deep={'ids_with_historical_deeper_fields':1034,'historical_deeper_fields':1828,'historical_proof_ids':1347,
      'review_items_open':['QC10','IA-QC11','QC12','QC13'],
      'closed_by_this_core_reading':False,
      'explanation':'Specific additional core pointers are now read. The inherited gap ledger is preserved; no deep-proof rereview or blanket historical closure is claimed.'}
write('PER_RULE_CORE_REVIEW.json',{
 'schema':'uct-dvc-bounded-core-rule-followup/1','created_utc':datetime.now(timezone.utc).isoformat(),
 'baseline_version':graph['version'],'baseline_graph_sha256':sha(BASE),'previous_frozen_scope_sha256':sha(PREVIOUS),
 'counts':{'active_rules':424,'previously_unread_rules_now_core_read':287,'prior_rules_with_core_contract_supplement':137,
           'conclusion_node_excerpts_only':45,'new_numerical_tests':0,'full_map_semantic_completion':False},
 'scope':'Serialized rule conditions, relation fields, quantifiers and same-instance obligations specified per ID; not all referenced premise/proof closures.',
 'historical_depth_gaps_kept_open':deep,'items':items})
write('UNREAD_CORE_REVIEW_FIELDS.json',{
 'schema':'uct-rule-followup-explicit-unread-subtrees/1','graph_sha256':sha(BASE),
 'meaning':'Each listed pointer denotes a whole source subtree not read in the cumulative frozen-plus-followup rule scope. An omitted proof locator is not a read proof; a read rule premise ID is not automatic review of the referenced proof or actual premise truth.',
 'items':[{'id':r['id'],'unread_subtree_paths':r['unread_subtree_paths']} for r in items],
 'historical_depth_gaps_kept_open':deep})

evidence=json.loads((CANDIDATE_ROOT/'EVIDENCE_CANDIDATE_ADDITION.json').read_text())
evidence_notes={
 'DVC20261010:PUBLIC_DATA_DOMAIN':'The archive, exclusions and exact analysis specifications are frozen. The 18 participants, 9704 in-range command records, 108 cells and 216 fits are different denominators. These describe a public-data reanalysis rather than new collected observations; actual consumer application remains false.',
 'DVC20261010:EXPLORATORY_ENDPOINT_REANALYSIS':'The stated 0.68299755 passive Start-minus-End sigma matches the frozen independent reanalysis. PSE means the model-dependent 0.5 crossing; physical response-code orientation remains unverified. Independent sigma and source-labelled JND remain separate. Paired-t/Holm results are explicitly exploratory and not distribution-free coverage, an installed intake contrast or H evidence.',
 'DVC20261010:ACTUAL_ADMISSION_GAP':'This is a bounded statement about the inspected sources, not impossibility of an experiment. Parsed time-bearing rows do not identify physical onset. Every token, consumer, clock, capture/read and consequence clause must hold in one installation/episode, and device M_D/P_E are not identified human neural inputs.',
 'DVC20261010:ctx_empirical_endpoint_tensor':'An explicitly nondeductive connection to the separately typed, disabled MPC endpoint tensor; it neither equates precision with response location nor identifies agency/ownership.',
 'DVC20261010:ctx_empirical_actual_contract':'An explicitly nondeductive statement of the unfilled same-instance actual-consumer contract; it creates no rule applying empirical fits to hardware validity.',
 'DVC20261010:ctx_empirical_semantic_bridge':'An explicitly nondeductive nonidentification context: a fitted comparison response is not familiar mineness, conceptual self, RetBind or a validated target bridge.'
}
review=[]
for kind in ['nodes','context_links']:
    for obj in evidence[kind]:
        review.append({'id':obj['id'],'item_type':kind,'source_record_sha256':record_sha(obj),
           'read_scope':'ENTIRE_SERIALIZED_RECORD','exact_leaf_paths_read':leaves(obj,''),
           'assessment':evidence_notes[obj['id']],
           'decision':'RETAIN_AS_DISABLED_EVIDENCE_OR_NONDEDUCTIVE_CONTEXT','blocking_issue':None})

old_map=json.loads((ROOT/'workbench/doi20261010/device_model/MAP_EXTENSION.json').read_text())
new_map=json.loads((CANDIDATE_ROOT/'MAP_EXTENSION.json').read_text())
diffs=[]
for kind in ['nodes','rules','context_links']:
    old_items={x['id']:x for x in old_map[kind]};new_items={x['id']:x for x in new_map[kind]}
    assert old_items.keys()<=new_items.keys()
    for rid,obj in old_items.items():
        changed={k:{'old':obj.get(k),'new':new_items[rid].get(k)} for k in set(obj)|set(new_items[rid]) if obj.get(k)!=new_items[rid].get(k)}
        if changed:
            diffs.append({'id':rid,'changed_fields':changed})
            assert kind=='rules' and set(changed)=={'proof_location'}

write('EVIDENCE_ADDITION_REVIEW.json',{
 'schema':'uct-dvc-independent-evidence-addition-review/1',
 'source_file_sha256':sha(CANDIDATE_ROOT/'EVIDENCE_CANDIDATE_ADDITION.json'),
 'assembled_map_sha256_at_review':sha(CANDIDATE_ROOT/'MAP_EXTENSION.json'),
 'counts':{'new_empirical_nodes':3,'new_nondeductive_contexts':3,'new_rules':0,'assembled_nodes':24,'assembled_rules':6,'assembled_contexts':15},
 'items':review,'scientific_blocking_issues':[],
 'nonblocking_clarification':'If edited later, Pr(InputValue=1 | command=x)=0.5 would make the covariate explicit in the PSE sentence; the current fitted-location wording is already scoped and scientifically acceptable.',
 'original_39_items':{'scope':'Alias/preservation verification against the independently reviewed frozen component; no duplicate new scientific credit.','unchanged_nodes':21,'unchanged_contexts':12,'rules_changed_only_in_proof_location':diffs},
 'concurrent_CBI':{'remote_commit_supplied_by_parent':'bd66a621949948d49788243e7fa8313f1256dfbb','note_sha256':sha(CBI),'actual_read_scope':'RESEARCH_NOTE.md in full, all eight sections; no new rereview of the external primary studies or CBI proofs.',
   'net_increment_deduction':'CBI already supplies consumer-relative P=0, the transduction/delivery/read branch-cut boundary, matched-world-output versus complete-organization distinction and source-constrained human feasibility. None is newly credited to DVC. DVC retains event admission, buffers/capture/commit/read, interval/deadline contracts and its explicitly exploratory reanalysis.'},
 'actual_consumer_application_established':False,'phenomenal_bridge_established':False,'publication_of_new_DVC_paper_recommended':False})

read_files=[]
for name in ['COMPACT_CONTRACT_CATALOG.txt','STATUS_FIELD_SUPPLEMENT.txt','CONCLUSION_TEXT_SUPPLEMENT.json',
             'PRIOR137_NEW_VALUE_CATALOG.txt','PRIOR137_REFERENCE_CATALOG.txt','PRIOR137_CORE_TEMPLATE_CATALOG.txt','PRIOR137_CORE_COMPACT.txt']:
    path=OUT/name;read_files.append({'file':name,'sha256':sha(path),'read_scope':'ENTIRE_CONTENT'})
for path in sorted((OUT/'compact_cards').glob('*.txt')):
    read_files.append({'file':str(path.relative_to(OUT)),'sha256':sha(path),'read_scope':'ALL_RULE_LINES; final large batches were read in bounded contiguous chunks'})
write('SOURCE_AND_READING_SCOPE.json',{
 'schema':'uct-dvc-core-followup-reading-provenance/1',
 'baseline':{'path':str(BASE),'sha256':sha(BASE),'version':graph['version']},
 'read_displays':read_files,
 'external_record_reads':[{'path':str(CANDIDATE_ROOT/'EVIDENCE_CANDIDATE_ADDITION.json'),'sha256':sha(CANDIDATE_ROOT/'EVIDENCE_CANDIDATE_ADDITION.json'),'scope':'Entire JSON'},
   {'path':str(CBI),'sha256':sha(CBI),'scope':'Entire note; no underlying source rereview'},
   {'path':str(CANDIDATE_ROOT/'MAP_EXTENSION.json'),'sha256':sha(CANDIDATE_ROOT/'MAP_EXTENSION.json'),'scope':'Full machine comparison of original 39 IDs plus manual reading of every changed proof-location field and all six new records; no new full-map semantic proof'}],
 'non_read_materializations':['cards/*.txt','prior137_core_cards/*.txt','PRIOR137_GROUPED_FIELDS.txt'],
 'non_read_materialization_note':'These intermediate verbose displays were generated for the compact workflow but are not claimed as separately read. Equivalent selected values were actually read through the listed compact displays and exact-value catalogues.',
 'prior_frozen_review_unchanged':{'manifest_sha256':sha(ROOT/'workbench/doi20261010/dvc_review/ARTIFACT_MANIFEST.json'),'main_report_sha256':sha(ROOT/'workbench/doi20261010/dvc_review/INDEPENDENT_REVIEW.md')},
 'new_numerical_execution':False,
 'parent_final_model_execution':'Parent reports a final exact-byte model reproduction in canonical DVC/FINAL_MODEL_REPRODUCTION.json. This subagent did not rerun it in this bounded follow-up and does not claim that receipt as its own execution.'})

counts={'rules':len(items),'new287_whole_value_fields':sum(len(i.get('whole_value_paths_read',[])) for i in items),
 'prior137_additional_whole_value_fields':sum(len(i.get('newly_read_whole_value_paths',[])) for i in items),
 'cumulative_rule_leaf_paths_read':sum(len(i.get('exact_leaf_paths_read',i.get('exact_leaf_paths_read_cumulative',[]))) for i in items),
 'unread_subtree_pointers':sum(len(i['unread_subtree_paths']) for i in items)}
write('REVIEW_SUMMARY.json',{'schema':'uct-dvc-followup-summary/1','decision':'RETAIN_DISABLED_DVC_AND_EXPLORATORY_EVIDENCE; NO_NEW_LOCAL_SCIENTIFIC_BLOCKER','counts':counts,
 'rule_ids_without_any_core_visit_this_round':[],'core_fields_do_not_equal_full_record_or_full_proof_review':True,
 'whole_map_semantic_completion':False,'historical_depth_gaps_kept_open':deep,
 'completed_map_version_unchanged':'UCT-MAP-v1.1.2','new_candidate_rules_enabled':0,
 'whole_1608_id_aggregation':'Not certified by this subagent: parent must combine exact per-ID node, context, suspended-rule and rule scopes from their separate audits.'})
print(json.dumps(counts,indent=2))
