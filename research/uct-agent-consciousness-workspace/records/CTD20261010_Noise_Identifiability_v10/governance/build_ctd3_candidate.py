"""Register a disabled finite-sample application and a precisely scoped audit.
This does not activate a UCT premise or claim historical semantic reproof.
"""
from pathlib import Path
import gzip,hashlib,io,json,subprocess,tarfile
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
# In an extracted scratch record, use the adjacent preserved repository.
# Inside the repository record tree, use its nearest real Git worktree.
def repository_path():
 for q in (PACKAGE.parent/'uct_repo',PACKAGE,*PACKAGE.parents):
  if q.is_dir() and subprocess.run(['git','rev-parse','--is-inside-work-tree'],cwd=q,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
   return q
 raise RuntimeError('The preserved UCT research Git repository is required.')
REPO=repository_path()
PREFIX='research/uct-agent-consciousness-workspace/'

def sha(x): return hashlib.sha256(x).hexdigest()
def canon(x): return sha(json.dumps(x,sort_keys=True,ensure_ascii=False).encode())
def write(name,d): (HERE/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def node(i,label,kind,statement,premises,domain,quantifier,limits,evidence):
 return dict(id=f'CTD3-N{i:03d}',label=label,kind=kind,statement=statement,all_premises=premises,
  domain=domain,quantifier=quantifier,counterexamples_and_limits=limits,
  novelty_status=['INHERITED_STATISTICAL_PRINCIPLE','NEW_APPLICATION','PRIORITY_UNVERIFIED'],
  source_lineage=['Clopper and Pearson 1934, DOI 10.1093/biomet/26.4.404','CTD2-N010 through CTD2-N016','Classical confidence-set projection and union bound'],
  evidence_paths=evidence,proof_locations=[{'path':'finite_sample/PROOF.md','section':'Finite-sample projection and calibration uncertainty'},{'path':'manuscript/noise-identifiability-bodily-judgments-v1.0.0.md','section':'6.4 and Appendix B.5'}],
  status='PENDING_MAP_CONDITIONAL_OR_RECORDED_CALCULATION',enabled=False,enabled_as_established_premise=False,
  actual_application_premises_discharged=False,experience_inference='NONE')

def main():
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
 def get(p): return subprocess.check_output(['git','show',head+':'+PREFIX+p],cwd=REPO)
 raw=get('versions/UCT-MAP-v1.1.2/UCT_MAP_v1.1.2_Capsule.tar.xz')
 with tarfile.open(fileobj=io.BytesIO(raw)) as t: graph_bytes=t.extractfile('UCT_EFFECTIVE_GRAPH.json').read()
 graph=json.loads(graph_bytes)
 assert sha(graph_bytes)=='0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612'
 prior=json.loads((HERE/'MAP_EXTENSION.json').read_text())
 assert (len(prior['nodes']),len(prior['rules']),len(prior['context_links']))==(20,7,13)
 known={x['id'] for k in ('nodes','rules','context_links') for x in graph[k]}|set(graph['suspended_historical_rule_ids'])
 prior_ids={x['id'] for k in ('nodes','rules','context_links') for x in prior[k]}
 old=json.loads(gzip.decompress((HERE/'BASELINE_PER_ID_STRUCTURE.json.gz').read_bytes()))
 old_records={x['id']:x for x in old['items']}
 records=[]; missing=[]
 for key,kind in [('nodes','node'),('rules','active_rule'),('context_links','context')]:
  for x in graph[key]:
   h=canon(x); assert old_records[x['id']]['record_sha256']==h
   refs=[]
   if key=='rules': refs=x.get('all_of',[])+[x['conclusion']]
   elif key=='context_links':
    source=x.get('from',x.get('source')); target=x.get('to',x.get('target'))
    external=x.get('external_source',False) or x.get('from_type',x.get('source_type')) in {'source_reference','module_reference','module','external_reference'}
    refs=[target]+([] if external else [source])
   unresolved=[r for r in refs if r not in known]
   if unresolved: missing.append(dict(id=x['id'],refs=unresolved))
   records.append(dict(id=x['id'],kind=kind,record_sha256=h,all_fields_hashed_and_compared=True,unchanged=True,
    references_resolve=not unresolved,status_preserved=True,active_dependency_change=False,
    full_historical_source_semantic_reproof=False,compatibility_scope='New statistical objects stay in a separate disabled observation-model domain; no baseline definition or active premise is replaced.'))
 for x in graph['suspended_historical_rule_ids']:
  records.append(dict(id=x,kind='suspended_rule_id',suspended_status_preserved=True,active_dependency_change=False,full_historical_source_semantic_reproof=False))
 assert len(records)==1608
 assert not missing
 n1=node(1,'Fixed-calibration paired binomial experiment','MODEL_CONTRACT',
  'For n independent identically distributed paired responses from one same internal Gaussian sensory draw, count joint-yes outcomes K~Binomial(n,p11). Marginal variances, finite halfwidths, lapses, centered criteria and criterion-correlation bound are fixed known parameters; the complete CTD2 joint observation contract applies.',
  ['One same internal sensory draw per pair, not merely the same external stimulus.','Gaussian sensory variable independent of the jointly Gaussian criteria.','Independent lapse indicators and fair guesses across reports and variables.','Calibrated common center; positive marginal variances; finite nonnegative halfwidths; legal lapse and kappa bounds.','Independent identically distributed trials and fixed n; no optional stopping claim.'],
  'One explicitly calibrated paired-response law.','All n>=0 integer counts under this fixed law.',
  ['Blockwise human counts do not instantiate the paired experiment.','Unknown calibration and correlated lapses are not covered by treating fitted values as known.'],['finite_sample/confidence_sets.py','finite_sample/PROOF.md'])
 n2=node(2,'Exact binomial confidence-set projection','CONDITIONAL_MATHEMATICAL_RESULT',
  'The preimage of an equal-tailed (1-alpha) Clopper-Pearson probability interval through the complete attainable observation model contains the entire sharp population variance set with probability at least 1-alpha. Equal-v nonempty endpoints are v*max(0,(rL-kappa)/(1-kappa)) and v*(rU+kappa)/(1+kappa) for kappa<1, and [0,v*(1+rU)/2] for kappa=1.',
  ['All CTD3-N001 premises for the same experiment.','0<alpha<1 and the classical binomial tail coverage guarantee.','Project the whole probability interval intersected with the attainable law, including both covariance signs and all allowed criterion covariances.','Use the sharp feasibility result CTD2-N013; it remains a conditional premise, not empirical installation.'],
  'Variance confidence sets in the centered Gaussian paired-interval observation family.','For every admitted fixed calibration and parameter value; coverage is over repeated binomial samples.',
  ['Empty intersection returns empty set; degenerate constant readout returns full domain only when its probability lies in the binomial interval.','Real-arithmetic coverage theorem; double-precision evaluation is not certified interval arithmetic.','Nonempty sets do not establish the mechanism assumptions, physical consumer, anatomical locus or experience.'],['finite_sample/confidence_sets.py','finite_sample/PROOF.md'])
 n3=node(3,'Honest nuisance-calibration region','CALIBRATION_COVERAGE_CONTRACT',
  'A random calibration region K_gamma covers the true nuisance vector with probability at least 1-gamma, and the binomial probability interval separately retains its own guarantee for the same law.',
  ['A valid simultaneous region for the complete nuisance vector; marginal individual error bars do not automatically provide it.','0<=gamma<1 and alpha+gamma<1.','Calibration and main observation contracts refer to the same parameters and response mechanism.'],
  'One specified calibration procedure and paired observation model.','Repeated sampling under the joint experiment; independence of the two coverage events is not required.',
  ['No actual human calibration procedure is validated here.','A grid sampled from a continuous nuisance region is not its complete representation.'],['finite_sample/PROOF.md','finite_sample/confidence_sets.py'])
 n4=node(4,'Calibration-union confidence set','CONDITIONAL_MATHEMATICAL_RESULT',
  'Union of the complete variance projections over an honest calibration region has true-variance coverage at least 1-alpha-gamma by event intersection and the union bound. A genuinely finite region can be enumerated exactly; if only kappa is uncertain over an interval, nesting makes its upper endpoint sufficient for the continuous union.',
  ['CTD3-N001 and CTD3-N003 contracts bind the same experiment and true nuisance vector.','Take the complete set union, or a certified outer superset; never replace a continuous region by unqualified point sampling.','The binomial interval and nuisance region each have their stated coverage.'],
  'Joint sampling uncertainty in a specified paired law and honest calibration region.','Every admitted true nuisance vector covered by the stated calibration contract.',
  ['No efficiency or shortest-interval optimality is asserted.','General continuous multi-parameter numerical projection is not implemented or certified.'],['finite_sample/PROOF.md','finite_sample/confidence_sets.py'])
 n5=node(5,'Prespecified finite probability-law operating characteristics','SYNTHETIC_NUMERICAL_EVIDENCE',
  'All 240 valid cases among 480 prespecified synthetic scenarios have true-variance coverage at least 0.95023456 and complete-set coverage at least 0.95015146 at nominal 95%. Wide sets remain at n=4096; wrong criterion bounds, sensory resampling and shared lapses expose contract failures despite valid binomial probability coverage.',
  ['Fixed ANALYSIS_PLAN.json before these calculations.','Enumerate every possible count and sum its binomial probability; no Monte Carlo or new human observations.','All three response profiles, four n values and five generating variances retained.','Resampled per-task variance is not relabeled as actual shared variance.','Empty-set probability is reported separately from width-zero convention.'],
  'The 480 fixed dimensionless model scenarios and archived code/tables.','Only these finite cases; not a proof of the general theorem or recommended human sample size.',
  ['Known-calibration grid does not validate estimated-nuisance coverage.','Numerical coverage is evidence about the implementation, not empirical realization.'],['finite_sample/ANALYSIS_PLAN.json','finite_sample/operating_characteristics.csv','finite_sample/operating_characteristics_summary.json','finite_sample/EXECUTION_PROVENANCE.json'])
 n5['novelty_status']=['NEW_APPLICATION','SYNTHETIC_CHECK_NOT_EMPIRICAL_DISCOVERY']
 nodes=[n1,n2,n3,n4,n5]
 rules=[]
 for i,prem,conclusion in [(1,['CTD3-N001','CTD2-N013'],'CTD3-N002'),(2,['CTD3-N001','CTD3-N003','CTD2-N013'],'CTD3-N004')]:
  rules.append(dict(id=f'CTD3-R{i:03d}',kind='CONDITIONAL_MATHEMATICAL_RULE',all_of=prem,conclusion=conclusion,
   same_instance_required=True,binding='All complete contracts refer to the same population law, calibration vector, confidence procedure and variance target.',
   premise_semantics='AND inside this route; separately named routes remain alternatives, never pooled evidence.',
   proof_locations=[{'path':'finite_sample/PROOF.md','section':'Coverage and calibration union'}],
   actual_premises_discharged=False,enabled=False,enabled_as_established_premise=False))
 links=[('CTD2-N014','CTD3-N002','WEAK_IDENTIFICATION_PRECISION_MOTIVATION'),('CTD2-N016','CTD3-N005','ASSUMPTION_VIOLATION_COMPARISON'),('CTD3-N002','CTD3-N005','NUMERICAL_CHECK_NOT_PROOF'),('CTD3-N004','CTD2-N018','CALIBRATION_OBLIGATIONS'),('CTD3-N002','R188:INFERENCE_CONTRACT','MODEL_REJECTION_SCOPE'),('CTD3-N002','R169:HELDOUT_CALIBRATION_FALSIFIER','NONDEDUCTIVE_FAILURE_ANALOGY')]
 contexts=[dict(id=f'CTD3-C{i:03d}',**{'from':a,'to':b},type=t,deductive=False,enabled=False,enabled_as_established_premise=False) for i,(a,b,t) in enumerate(links,1)]
 newids={x['id'] for x in nodes+rules+contexts}
 assert len(newids)==13 and not newids&(known|prior_ids)
 for r in rules: assert set(r['all_of']+[r['conclusion']]) <= known|prior_ids|newids
 for c in contexts: assert {c['from'],c['to']} <= known|prior_ids|newids
 a3n_path='records/A3N20261010_Route_Fluency_Crossing/MAP_EXTENSION.json'
 evidence={}
 for x in nodes:
  for path in x['evidence_paths']+[z['path'] for z in x['proof_locations']]:
   p=PACKAGE/path
   if p.is_file(): evidence[path]={'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
   else: raise RuntimeError('Missing scientific evidence: '+path)
 candidate=dict(schema='uct-pending-extension/1',id='CTD3-20261010',result_version='CTD-RESULT-v1.0.0',candidate_version='CTD3-MAP-CANDIDATE-v0.1.0',base_release='UCT-MAP-v1.1.2',
  status='PENDING_MAP',enabled=False,enabled_as_established_premise=False,global_semantic_audit_status='AUDIT_INCOMPLETE',
  release_effect='No completed-map or active-premise change; DOI publication is orthogonal to scientific premise admission.',
  base_commit=head,baseline_graph_sha256=sha(graph_bytes),baseline_counts=dict(nodes=913,rules=424,contexts=261,suspended=10,total=1608),
  preserved_ctd2_candidate_sha256=sha((HERE/'MAP_EXTENSION.json').read_bytes()),preserved_a3n_candidate_sha256=sha(get(a3n_path)),
  inherited_open_obligations=prior['inherited_open_obligations']+prior['new_open_obligations'],inherited_open_debt=prior['inherited_open_debt'],
  new_open_obligations=['CTD3-OPEN-ACTUAL-CALIBRATION','CTD3-OPEN-CERTIFIED-CONTINUOUS-PROJECTION'],nodes=nodes,rules=rules,context_links=contexts)
 write('CTD3_MAP_EXTENSION.json',candidate)
 (HERE/'CTD3_BASELINE_PER_ID_REVIEW.json.gz').write_bytes(gzip.compress(json.dumps(dict(items=records,graph_sha256=sha(graph_bytes),scope='All baseline items hash/field/status/reference checked; no full historical source semantic reproof.'),ensure_ascii=False).encode(),mtime=0))
 write('CTD3_MAP_REVIEW_RECEIPT.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),base_commit=head,baseline_visited=1608,baseline_changed=0,unresolved_structural_references=missing,
  candidate_counts=dict(nodes=5,rules=2,contexts=6,total=13),all_candidates_disabled=True,full_historical_semantic_reproof=False,historical_audit_status='AUDIT_INCOMPLETE',
  directly_compared_baseline_ids=[x['id'] for x in json.loads((HERE/'CTD3_AFFECTED_BASELINE_NODES.json').read_text())],
  affected_dependency_rederivation='Binomial coverage implies full preimage coverage; conjunction of honest probability and calibration events gives union-bound coverage. No inference from empirical grid, report law or calibration to actual organization or C1 is added.',
  evidence=evidence,protected_open_debt=prior['inherited_open_debt']))
 print(json.dumps({'candidate':'CTD3-20261010','items':13,'disabled':True,'baseline_visited':1608,'historical_semantic_audit':'AUDIT_INCOMPLETE'}))
if __name__=='__main__': main()
