"""Build truthful scoped ledgers and a disabled application from current inputs."""
from pathlib import Path
import json, hashlib, shutil, argparse
R = Path(__file__).resolve().parent
def dump(name, obj):
    p=R/name; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser()
parser.add_argument('--baseline',type=Path,required=True,help='Restored authoritative UCT-MAP-v1.1.2 effective graph')
base=parser.parse_args().baseline
g=json.loads(base.read_text())
desc=json.loads((R/'inputs/root/UCT_FORMAL_GRAPH_MODULES.json').read_text())
assert sha(base)==desc['effective_graph_sha256']
N={n['id']:n for n in g['nodes']}; assert len(N)==913
for rule in g['rules']:
    assert set(rule['all_of'])<=N.keys() and rule['conclusion'] in N
scoped={
 'A:TOKEN_CRITERIA':'Models are abstract; actual process admission is not asserted.',
 'A:P3':'No persisting local experience is deleted by macro-level discussion.',
 'A:P6':'Token identity, complete type and lineage are not identified.',
 'A:K':'Ports, time, boundary and operations must be fixed for any ontic transfer.',
 'A:C1':'Retained as a stipulated identity axiom, not empirically proved.',
 'A:C1_OI':'Finite endpoint equality is not complete-type equivalence.',
 'A:U1':'No memory, concurrency or correctness gate for basic experience.',
 'C:P2_COORD':'The residual-function proof applies existing fiber factorization.',
 'TA17:QUOTIENT':'Task-relative equivalence need not preserve other consumers.',
 'R173:RETENTIVE_BINDING_RELATION':'General retention example does not establish the grounded frame/history contract.',
 'IE:QUERY_SUFFICIENCY':'Minimum residual-code states specialize joint-query sufficiency.',
 'OL20261009:C1_APPLICATION':'Any nonisomorphism transfer still requires PHYSICAL_REDUCT, not code-level difference alone.',
 'UI20261009:FUTURE_QUOTIENT':'Endpoint relation is weaker than equality of every admitted future word.'}
assert set(scoped)<=N.keys()
dump('SCOPED_COMPATIBILITY.json',{'baseline':g['version'],'scope':'LOCAL_COMPATIBILITY_NOT_FULL_ORIGINAL_PROOF_REVIEW','items':[{'id':i,'rationale':v,'source_record':N[i]} for i,v in scoped.items()]})
rows=['kind\tid\tstructural_status\tsemantic_status\tproof_review_this_run']
for kind,key in [('node','nodes'),('rule','rules'),('context','context_links')]:
    ids=[]
    for idx,item in enumerate(g[key]):
        identity=item.get('id') or item.get('key')
        assert identity, (kind,idx)
        ids.append(identity)
        sem='SCOPED_COMPATIBILITY_ONLY' if identity in scoped else 'NOT_REVIEWED_THIS_RUN'
        rows.append(f'{kind}\t{identity}\tREAD_ID_AND_REFERENCES\t{sem}\tNOT_REPROVED')
    assert len(ids)==len(set(ids))
for identity in g['suspended_historical_rule_ids']:
    rows.append(f'suspended_rule\t{identity}\tREMAINS_DISABLED\tNOT_REVIEWED_THIS_RUN\tNOT_REPROVED')
(R/'PER_ID_AUDIT.tsv').write_text('\n'.join(rows)+'\n')
dump('AUDIT_RECEIPT.json',{'baseline':g['version'],'baseline_sha256':sha(base),'rows':len(rows)-1,
 'counts':{'nodes':913,'rules':424,'contexts':261,'suspended':10},'scoped_node_count':len(scoped),
 'historical_items_without_scoped_semantic_review':len(rows)-1-len(scoped),
 'full_historical_proofs_reproved_this_run':0,'full_semantic_audit':'AUDIT_INCOMPLETE',
 'complete_map_changed':False,'pending_premises_promoted':False})

claims=[
 ('TJR-C1','NEW_APPLICATION','Same boundary truth table does not identify use of a nominated record.',['TA18:JOINT_WITNESS','R173:RETENTIVE_BINDING_RELATION'],'SCU v1.0.1 and A3R; no new general source-use theorem','3'),
 ('TJR-C2','NEW_APPLICATION','Buffered serial writes preserve the stipulated block-endpoint update; in-place writes need extra identities.',['A:K','UI20261009:FUTURE_QUOTIENT'],'Classical update semantics; UCT I Appendix D','4'),
 ('TJR-C3','INHERITED','Exact serial retention iff its fibers refine residual-answer classes; minimum states equal distinct rows.',['C:P2_COORD','IE:QUERY_SUFFICIENCY'],'Aaronson 2005 Proposition 3.1; existing project factorization','5'),
 ('TJR-C4','INHERITED','A task-sufficient code may discard distinctions required by other consumers.',['TA17:QUOTIENT','IE:QUERY_SUFFICIENCY'],'TA17; RTTH; no new quotient theorem','5'),
 ('TJR-C5','NEW_APPLICATION','Actual present joint use does not entail that its retained values were a synchronous world snapshot.',['A:TOKEN_CRITERIA','A:K'],'Classical snapshot problem plus inherited UCT actuality/content distinction','6'),
 ('TJR-C6','CORRECTION','Task preservation alone does not establish complete experiential equivalence; grounded nonisomorphism requires the full constitutive contract.',['A:C1','A:C1_OI','A:U1','OL20261009:C1_APPLICATION'],'UCT I/III and existing OL rule; no AI phenomenality verdict','7'),
 ('TJR-C7','NEGATIVE_RESULT','This bounded comparison does not establish a new standalone theoretical contribution.',['TA17:QUOTIENT','IE:QUERY_SUFFICIENCY'],'Source-based novelty assessment, not a deductive scientific rule','9')]
objects=[]
for i,kind,statement,anchors,prior,section in claims:
    assert set(anchors)<=N.keys()
    objects.append({'id':i,'classification':kind,'statement':statement,'existing_anchors':anchors,
      'prior_coverage':prior,'evidence':f'RESEARCH_NOTE.md section {section}',
      'enabled_as_established_premises':False,'physical_instance_status':'OPEN',
      'phenomenal_bridge_status':'OPEN','global_priority':'NOT_CLAIMED'})
dump('CLAIM_LEDGER.json',{'research_id':'TJR20261010','version':'TJR-v0.1.0','claims':objects,
 'manuscript_decision':'HOLD','reason':'Inherited mathematics, internal overlap and a useful scoped comparison; no sufficient independent new theory.',
 'coverage_version':'UCT-PUB-v1.0.33','coverage_change':'NO_CHANGE_AFTER_RELEVANT_CLAIM_REVIEW'})
dump('MAP_EXTENSION.json',{'schema':'uct-disabled-scoped-application/1','research_id':'TJR20261010',
 'version':'TJR-v0.1.0','base_map':'UCT-MAP-v1.1.2','status':'PENDING_MAP_SCOPED_APPLICATION',
 'enabled_as_established_premises':False,'nodes':[],'rules':[],'context_links':[],
 'application_records':[{'id':'TJR-APP1','claim_ids':[x['id'] for x in objects],
   'existing_anchors':sorted({a for x in objects for a in x['existing_anchors']}),
   'source':'RESEARCH_NOTE.md','claim_ledger':'CLAIM_LEDGER.json','audit':'AUDIT_REPORT.md',
   'same_instance_required':True,'automatic_inference':False}],
 'merge_semantics':'Navigation only; do not load as an active scientific module.',
 'canonical_entry':'UNIFIED_RESEARCH_INDEX.json#scoped_foundational_reviews',
 'global_semantic_status':'AUDIT_INCOMPLETE','new_actual_or_named_phenomenal_claims':0})
dump('PUBLICATION_COVERAGE_UPDATE.json',{'research_id':'TJR20261010','coverage_version_before':'UCT-PUB-v1.0.33',
 'coverage_version_after':'UCT-PUB-v1.0.33','status':'RELEVANT_CLAIMS_REVIEWED_NO_CHANGE',
 'published_sources_compared':['UCT I v1.2','UCT II v1.1 sections 2,4,12','UCT III v1.0','TA25 v1.0','SCU v1.0.1','RTTH v1.0.0'],
 'map_source_only_overlap':['TA17:QUOTIENT','IE:QUERY_SUFFICIENCY','UI20261009:FUTURE_QUOTIENT','R173:RETENTIVE_BINDING_RELATION'],
 'pending_overlap':['A3R'], 'claim_ids':[x['id'] for x in objects],
 'new_publications':0,'new_published_versions':0,'published_source_bytes_modified':False,
 'uncertainty':'Not an exhaustive census or global priority proof. Map-only overlaps are not presented as fresh full-source proof reviews.',
 'standalone_manuscript':'HOLD','claim_ledger':'CLAIM_LEDGER.json'})

sources=[
 {'id':'Bennett2026','url':'https://arxiv.org/html/2601.11620v2','version':'v2','scope':'Sections 4–8, definitions 10–19, Theorems 3–4, Remark 3; separate supplement not fully recovered','use':'Occurrence/co-instantiation distinction and conditional capacity argument; persistence is acknowledged.'},
 {'id':'KanaiMa2026','url':'https://arxiv.org/html/2606.15348v1','version':'v1','scope':'Abstract; sections 4–6 including definitions and recurrent toy model; sections 7 and 9 limitations','use':'Mechanism-enriched realization precedes this study; conditional invariance and grain remain separate.'},
 {'id':'Chalmers1996','url':'https://consc.net/papers/rock.html','scope':'Implementation argument, especially sections 5–6','use':'Structured state components and local/global dependencies; not merely arbitrary trajectory labeling.'},
 {'id':'Aaronson2005','url':'https://theoryofcomputing.org/articles/v001a001/v001a001.pdf','scope':'Section 3, Proposition 3.1; quantum portions not used','use':'Classical deterministic one-way distinct-row bound; no new mathematical priority.'},
 {'id':'AfekEtAl1990_1993','url':'https://groups.csail.mit.edu/tds/papers/Shavit/TM-429.pdf','scope':'Author technical report introduction and snapshot definition; full algorithms not re-proved','use':'Classical atomic snapshot problem; our finite example is a diagnostic application.'},
 {'id':'CommunicationLecture','url':'https://www.cs.toronto.edu/~toni/Courses/CommComplexity/Lectures/lecture1.pdf','scope':'Parity/equality examples and deterministic model','use':'Additional background only; primary research attribution uses Aaronson.'}]
for n in ['UCT_I','UCT_II','UCT_III','TA25','SCU','RTTH','A3R']:
    p=R/'inputs'/f'{n}.md'
    sources.append({'id':n,'local_snapshot':f'inputs/{n}.md','sha256':sha(p),
       'role':'Author/repository source snapshot; published and pending versions distinguished in the note.'})
dump('SOURCE_LEDGER.json',{'retrieval_date':'2026-10-10','sources':sources,
 'limitations':['Supplement retrieval incomplete; no exhaustive literature census.',
 'One initial RTTH fetch failed with 404 due to omitted published/ directory; recovered from exact receipt-bound path and commit.',
 'Search result dates are not used as paper publication dates.'],
 'external_full_text_redistribution':False})

record='records/TJR20261010_Temporal_Joint_Realization/'
entry={'id':'TJR20261010','version':'TJR-v0.1.0','title':'Temporal retention and joint realization',
 'status':'DISABLED_SCOPED_FOUNDATIONAL_APPLICATION','enabled_as_established_premises':False,
 'source':record+'RESEARCH_NOTE.md','handoff':record+'HANDOFF_ZH.md','work_log':record+'WORK_LOG.md',
 'claim_ledger':record+'CLAIM_LEDGER.json','map_extension':record+'MAP_EXTENSION.json',
 'audit':record+'AUDIT_REPORT.md','source_sha256':sha(R/'MAP_EXTENSION.json'),
 'completed_map':'UCT-MAP-v1.1.2','coverage_version':'UCT-PUB-v1.0.33',
 'scientific_delta':{'nodes':0,'rules':0,'contexts':0},'application_records':1,
 'manuscript_status':'HOLD','actual_and_named_phenomenal_status':'OPEN'}
rootout=R/'root_updates'; rootout.mkdir(exist_ok=True)
names=['CURRENT_STATE.json','UNIFIED_RESEARCH_INDEX.json','RESEARCH_REGISTRY.json',
       'RESEARCH_SESSION_LOG_INDEX.json','UCT_FORMAL_GRAPH_MODULES.json','FORMAL_MAP_EXTENSION_INDEX.json']
for name in names:
    p=R/'inputs/root'/name; o=json.loads(p.read_text())
    field='scoped_foundational_reviews'
    items=o.setdefault(field,[]);items[:]=[v for v in items if v.get('id')!='TJR20261010'];items.append(entry)
    if name=='CURRENT_STATE.json': o['latest_foundational_review']=entry
    if name=='RESEARCH_SESSION_LOG_INDEX.json':o['latest_foundational_work_log']=entry['work_log']
    (rootout/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
    # These scientifically important pointer/collection fields must not change.
    old=json.loads(p.read_text())
    for k in ['latest_research','latest_followup_application','next_priority','pending_checkpoints','pending_checkpoints_not_promoted','pending_disabled','merge_order']:
        if k in old: assert o[k]==old[k],(name,k)
for name in ['HANDOFF.md','MASTER_INDEX.md','UCT_FORMAL_MAP.md']:
    old=(R/'inputs/root'/name).read_text()
    addition='\n\n基础问题专线 TJR20261010：[交接]('+record+'HANDOFF_ZH.md) · [正文]('+record+'RESEARCH_NOTE.md) · [日志]('+record+'WORK_LOG.md)。串行保留、联合读取与压缩的停用应用；原科学接续和身体熟悉感路线保留。原理多属继承，独立成稿HOLD，全图深审仍未完成。\n'
    (rootout/name).write_text(old.rstrip()+addition)
audit_old=(R/'inputs/root/UCT_FORMAL_AUDIT.md').read_text()
(rootout/'UCT_FORMAL_AUDIT.md').write_text(audit_old.rstrip()+'\n\nTJR基础问题复核：[审查]('+record+'AUDIT_REPORT.md)，1608项仅结构遍历、13节点有限兼容性核对；全历史深审AUDIT_INCOMPLETE，0新增正式节点/规则/关系。\n')
print(json.dumps({'audit_rows':len(rows)-1,'claims':len(objects),'new_formal_nodes':0,
 'root_updates':sorted(p.name for p in rootout.iterdir()),'pending_count_unchanged':38}))
