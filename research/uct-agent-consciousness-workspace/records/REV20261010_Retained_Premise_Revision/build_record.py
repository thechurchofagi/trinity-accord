"""Build scoped ledgers and synchronized navigation without scientific promotion."""
from pathlib import Path
import argparse
import hashlib
import json

R = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name, obj):
    p = R/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

p = argparse.ArgumentParser()
p.add_argument('--baseline', type=Path, required=True)
args = p.parse_args()
g = json.loads(args.baseline.read_text())
desc = json.loads((R/'inputs/root/UCT_FORMAL_GRAPH_MODULES.json').read_text())
assert sha(args.baseline) == desc['effective_graph_sha256']
N = {n['id']: n for n in g['nodes']}
assert len(N) == len(g['nodes']) == 913
for rule in g['rules']:
    assert set(rule['all_of']) <= N.keys() and rule['conclusion'] in N

scoped = {
 'A:TOKEN_CRITERIA': 'Toy state models do not certify a complete actual process token.',
 'A:P3': 'Persisting local processes are not deleted by poor revision performance.',
 'A:K': 'Constitutive ports, boundary and time are needed before physical transfer.',
 'A:C1': 'Retained as an identity commitment, not proved by software accuracy.',
 'A:C1_OI': 'A finite task quotient does not determine complete organization.',
 'A:U1': 'No editability or memory threshold for basal experience.',
 'C:P2_COORD': 'Fiber factorization is inherited, not rebranded as a new theorem.',
 'TA17:QUOTIENT': 'Future edit demands can distinguish equal current readouts.',
 'IE:QUERY_SUFFICIENCY': 'Delayed-query sufficiency precedes this application.',
 'R145:TRANSPORT_SETUP': 'The allowed intervention family is fixed explicitly.',
 'R145:TRANSPORT_BLIND': 'Descended operations cannot identify all erased distinctions.',
 'R145:AFFINE_DIAGNOSTIC': 'R145 already distinguishes translations from revealing resets.',
 'UI20261009:FUTURE_DOMAIN': 'Both full edit alphabets are explicitly inside the legal word domain.',
 'UI20261009:FUTURE_EQ': 'All future words include the empty word and all initial states.',
 'UI20261009:FUTURE_QUOTIENT': 'Minimum memory is an application of this existing quotient.',
 'TH20261009:STORED_VS_READ': 'Retained availability is distinct from demonstrated consumer use.',
 'R173:RETENTIVE_BINDING_RELATION': 'No grounded human frame/history binding is inferred.',
 'OL20261009:C1_APPLICATION': 'Software differences alone do not meet the complete physical reduct contract.'}
assert set(scoped) <= N.keys(), set(scoped)-N.keys()
dump('SCOPED_COMPATIBILITY.json', {'scope': 'LOCAL_COMPATIBILITY_NOT_FULL_ORIGINAL_PROOF_REVIEW',
 'items': [{'id': k, 'rationale': v, 'source_record': N[k]} for k,v in scoped.items()]})
rows = ['kind\tid\tstructural_status\tsemantic_status\tproof_review_this_run']
for kind, key in [('node','nodes'), ('rule','rules'), ('context','context_links')]:
    ids = []
    for item in g[key]:
        identity = item.get('id') or item.get('key')
        assert identity
        ids.append(identity)
        sem = 'SCOPED_COMPATIBILITY_ONLY' if identity in scoped else 'NOT_REVIEWED_THIS_RUN'
        rows.append(f'{kind}\t{identity}\tREAD_ID_AND_REFERENCES\t{sem}\tNOT_REPROVED')
    assert len(ids) == len(set(ids))
for identity in g['suspended_historical_rule_ids']:
    rows.append(f'suspended_rule\t{identity}\tREMAINS_DISABLED\tNOT_REVIEWED_THIS_RUN\tNOT_REPROVED')
(R/'PER_ID_AUDIT.tsv').write_text('\n'.join(rows)+'\n')
dump('AUDIT_RECEIPT.json', {'baseline':g['version'], 'baseline_sha256':sha(args.baseline),
 'rows':len(rows)-1, 'counts':{'nodes':913,'rules':424,'contexts':261,'suspended':10},
 'scoped_node_count':len(scoped), 'historical_items_without_scoped_semantic_review':len(rows)-1-len(scoped),
 'full_historical_proofs_reproved_this_run':0, 'full_semantic_audit':'AUDIT_INCOMPLETE',
 'complete_map_changed':False, 'pending_premises_promoted':False})

claims = [
 ('REV-C1','INHERITED','Exact future retention is characterized by the existing output-stable quotient.', ['UI20261009:FUTURE_DOMAIN','UI20261009:FUTURE_QUOTIENT','C:P2_COORD'], 'UCT I Appendix D and normalized UI; classical state minimization', '3'),
 ('REV-C2','NEW_APPLICATION','For all Boolean functions, toggle-state minimum equals the number of translation-period cosets.', ['UI20261009:FUTURE_QUOTIENT','R145:TRANSPORT_BLIND'], 'Elementary group-action specialization; no global priority claimed', '4'),
 ('REV-C3','NEW_APPLICATION','Assignment-state minimum is 2**k for k essential Boolean coordinates.', ['UI20261009:FUTURE_QUOTIENT','IE:QUERY_SUFFICIENCY'], 'Elementary distinguishing-continuation specialization; exact all-state/all-word contract', '4'),
 ('REV-C4','CORRECTION','The flip/reset contrast is already present in R145 and cannot count as a new general discovery.', ['R145:TRANSPORT_SETUP','R145:AFFINE_DIAGNOSTIC'], 'R145 v0.2 exact source reviewed', '1,4'),
 ('REV-C5','NEW_APPLICATION','An outside old-bit message repairs parity assignment but does not show local retention.', ['IE:QUERY_SUFFICIENCY','TH20261009:STORED_VS_READ'], 'Standard information argument and existing source-use boundary', '5'),
 ('REV-C6','NEW_APPLICATION','Correct one-step revision reports do not imply installed state updates; a committed composition separates specified consumers.', ['UI20261009:FUTURE_EQ','TH20261009:STORED_VS_READ'], 'Classical stateful semantics; bounded software witness', '2,6'),
 ('REV-C7','CORRECTION','Editability bounds and scores do not determine complete experiential organization or basal admission.', ['A:C1','A:C1_OI','A:U1','A:P3','OL20261009:C1_APPLICATION'], 'UCT I/III and existing physical-reduct contract', '7'),
 ('REV-C8','NEGATIVE_RESULT','This application is insufficient for an independent new-theory manuscript at present.', ['TA17:QUOTIENT','UI20261009:FUTURE_QUOTIENT','R145:TRANSPORT_BLIND'], 'Bounded internal/external novelty assessment, not a scientific inference rule', '9')]
objects = []
for identity, kind, statement, anchors, prior, section in claims:
    assert set(anchors) <= N.keys()
    objects.append({'id':identity,'classification':kind,'statement':statement,'existing_anchors':anchors,
      'prior_coverage':prior,'evidence':f'RESEARCH_NOTE.md sections {section}',
      'enabled_as_established_premises':False,'physical_instance_status':'OPEN',
      'phenomenal_bridge_status':'OPEN','global_priority':'NOT_CLAIMED'})
dump('CLAIM_LEDGER.json',{'research_id':'REV20261010','version':'REV-v0.1.0','claims':objects,
 'manuscript_decision':'HOLD','reason':'Reusable exact classification and protocol, inherited foundations and substantial internal/external overlap.',
 'coverage_version':'UCT-PUB-v1.0.33','coverage_change':'NO_CHANGE_AFTER_RELEVANT_CLAIM_REVIEW'})
dump('MAP_EXTENSION.json',{'schema':'uct-disabled-scoped-application/1','research_id':'REV20261010',
 'version':'REV-v0.1.0','base_map':'UCT-MAP-v1.1.2','status':'PENDING_MAP_SCOPED_APPLICATION',
 'enabled_as_established_premises':False,'nodes':[],'rules':[],'context_links':[],
 'application_records':[{'id':'REV-APP1','claim_ids':[v['id'] for v in objects],
   'existing_anchors':sorted({a for v in objects for a in v['existing_anchors']}),
   'source':'RESEARCH_NOTE.md','claim_ledger':'CLAIM_LEDGER.json','audit':'AUDIT_REPORT.md',
   'same_instance_required':True,'automatic_inference':False}],
 'merge_semantics':'Navigation only; do not load as an active scientific module.',
 'canonical_entry':'UNIFIED_RESEARCH_INDEX.json#scoped_foundational_reviews',
 'global_semantic_status':'AUDIT_INCOMPLETE','new_actual_or_named_phenomenal_claims':0})
dump('PUBLICATION_COVERAGE_UPDATE.json',{'research_id':'REV20261010','coverage_version_before':'UCT-PUB-v1.0.33',
 'coverage_version_after':'UCT-PUB-v1.0.33','status':'RELEVANT_CLAIMS_REVIEWED_NO_CHANGE',
 'published_sources_compared':['UCT I v1.2 C1/U1/Appendix D','UCT II v1.1 inherited scope','UCT III v1.0 inherited scope','TA25 v1.0 inherited scope'],
 'internal_exact_sources_compared':['R145 working source v0.2','UI source plus effective normalized FUTURE_DOMAIN/FUTURE_QUOTIENT','TJR-v0.1.0'],
 'map_source_only_overlap':['TA17:QUOTIENT','IE:QUERY_SUFFICIENCY','TH20261009:STORED_VS_READ','R173:RETENTIVE_BINDING_RELATION'],
 'claim_ids':[v['id'] for v in objects],'new_publications':0,'new_published_versions':0,
 'published_source_bytes_modified':False,'standalone_manuscript':'HOLD',
 'uncertainty':'Not an exhaustive publication census or global priority proof. R145 source draft label is not used to determine its present publication status.'})
sources = [
 {'id':'E1','url':'https://alignment.anthropic.com/2026/chive/','scope':'First-party research account, pipeline and limitations','use':'Counterfactual prompt explanations already studied'},
 {'id':'E2','url':'https://arxiv.org/html/2602.20710v2','scope':'Abstract, introduction and related work; no full training reproduction','use':'Counterfactual explanation training already studied'},
 {'id':'E3','url':'https://arxiv.org/html/2609.27038v1','scope':'Methods, results and limitations, v1','use':'Text-edit versus targeted activation comparison; bounded preprint'},
 {'id':'E4','url':'https://arxiv.org/html/2412.06769v2','scope':'Abstract and introduction, v2','use':'Existence of continuous-state reasoning architecture; no cache-erasure claim'},
 {'id':'E5','url':'https://proceedings.mlr.press/v115/beckers20a.html','scope':'Publisher abstract and metadata only','use':'Background attribution, not a fresh full proof review'}]
for f in sorted((R/'inputs').glob('*')):
    if f.is_file(): sources.append({'id':f.stem,'local_snapshot':'inputs/'+f.name,'sha256':sha(f)})
dump('SOURCE_LEDGER.json',{'retrieval_date':'2026-10-10','sources':sources,
 'limitations':['Bounded source search, not an exhaustive census.',
 'Human working-memory source candidates were located but full-text requests were blocked; no new empirical human claim is based on those snippets.',
 'The unversioned CST HTML failed; v2 was successfully retrieved.',
 'External full texts are not redistributed in this package.'], 'global_priority':'NOT_CLAIMED'})

record = 'records/REV20261010_Retained_Premise_Revision/'
entry = {'id':'REV20261010','version':'REV-v0.1.0','title':'Retained premises and committed revision',
 'status':'DISABLED_SCOPED_FOUNDATIONAL_APPLICATION','enabled_as_established_premises':False,
 'source':record+'RESEARCH_NOTE.md','handoff':record+'HANDOFF_ZH.md','work_log':record+'WORK_LOG.md',
 'claim_ledger':record+'CLAIM_LEDGER.json','map_extension':record+'MAP_EXTENSION.json',
 'audit':record+'AUDIT_REPORT.md','source_sha256':sha(R/'MAP_EXTENSION.json'),
 'completed_map':'UCT-MAP-v1.1.2','coverage_version':'UCT-PUB-v1.0.33',
 'scientific_delta':{'nodes':0,'rules':0,'contexts':0},'application_records':1,
 'manuscript_status':'HOLD','actual_and_named_phenomenal_status':'OPEN'}
rootout = R/'root_updates'; rootout.mkdir(exist_ok=True)
names = ['CURRENT_STATE.json','UNIFIED_RESEARCH_INDEX.json','RESEARCH_REGISTRY.json',
         'RESEARCH_SESSION_LOG_INDEX.json','UCT_FORMAL_GRAPH_MODULES.json','FORMAL_MAP_EXTENSION_INDEX.json']
for name in names:
    original = json.loads((R/'inputs/root'/name).read_text())
    o = json.loads(json.dumps(original))
    items = o.setdefault('scoped_foundational_reviews',[])
    items[:] = [v for v in items if v.get('id') != 'REV20261010']; items.append(entry)
    if name == 'CURRENT_STATE.json': o['latest_foundational_review'] = entry
    if name == 'RESEARCH_SESSION_LOG_INDEX.json': o['latest_foundational_work_log'] = entry['work_log']
    (rootout/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
    for k in original:
        if k not in ['scoped_foundational_reviews','latest_foundational_review','latest_foundational_work_log']:
            assert o[k] == original[k], (name,k)
for name in ['HANDOFF.md','MASTER_INDEX.md','UCT_FORMAL_MAP.md']:
    old = (R/'inputs/root'/name).read_text()
    addition = '\n\n基础问题专线 REV20261010：[交接]('+record+'HANDOFF_ZH.md) · [正文]('+record+'RESEARCH_NOTE.md) · [日志]('+record+'WORK_LOG.md)。承接 TJR，完成前提修改的精确信息条件与连续修改对照；0/0/0 停用应用，独立成稿 HOLD。原 A3V/A3Y 接续和全历史审查未完成状态保留。\n'
    (rootout/name).write_text(old.rstrip()+addition)
old = (R/'inputs/root/UCT_FORMAL_AUDIT.md').read_text()
(rootout/'UCT_FORMAL_AUDIT.md').write_text(old.rstrip()+'\n\nREV基础问题复核：[审查]('+record+'AUDIT_REPORT.md)，1608项仅结构遍历、18节点有限兼容性核对；全历史深审 AUDIT_INCOMPLETE，0新增正式节点/规则/关系。\n')
print(json.dumps({'audit_rows':len(rows)-1,'scoped_nodes':len(scoped),'claims':len(objects),
 'root_updates':len(list(rootout.iterdir())),'formal_delta':[0,0,0]}))
