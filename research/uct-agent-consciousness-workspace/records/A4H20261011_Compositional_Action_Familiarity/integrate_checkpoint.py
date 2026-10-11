"""Conservative A4H navigation repair/integration; run from repository root."""
import json,hashlib,subprocess
from pathlib import Path
root=Path('research/uct-agent-consciousness-workspace')
rel='records/A4H20261011_Compositional_Action_Familiarity'
out=root/rel
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
state=json.loads((root/'CURRENT_STATE.json').read_bytes())
bad=(root/'UNIFIED_RESEARCH_INDEX.json').read_bytes()
restored=subprocess.check_output(['git','show','e792283f086a914da0b289c1554b7c1342742820:'+str(root/'UNIFIED_RESEARCH_INDEX.json')])
assert sha(restored)=='7cd3e8f4ad31e0d766c6777612b1c70f216ff0230a878ad79770afbb04939c55'
index=json.loads(restored)
prior_ids=[x['id'] for x in index['followup_applications']]
# Current state carries the later objects absent from the last parseable index.
by_id={x['id']:x for x in index['followup_applications']}
for x in state['followup_applications']:by_id[x['id']]=x
new=dict(id='A4H20261011',version='A4H-COMPOSITION-v0.1.0',
 status='DISABLED_SCOPED_POSITIVE_CANDIDATE_AND_FINITE_WITNESS',
 enabled_as_established_premises=False,
 source=rel+'/RESEARCH_NOTE.md',handoff=rel+'/HANDOFF_ZH.md',work_log=rel+'/WORK_LOG.md',
 claim_ledger=rel+'/CLAIM_LEDGER.json',map_extension=rel+'/MAP_EXTENSION.json',
 exact_results=rel+'/EXACT_RESULTS.json',parent_science='A3V20261010',
 parent_followup='A4G20261011',completed_map='UCT-MAP-v1.1.2',
 scientific_delta=dict(nodes=0,rules=0,contexts=0),
 independent_h_validation=False,actual_bodily_installation=False,standalone_manuscript='HOLD')
by_id[new['id']]=new
index['followup_applications']=list(by_id.values())
index['latest_followup_application']=new
state['followup_applications']=list(by_id.values())
state['latest_followup_application']=new
state.setdefault('next_priority_before_A4H',state['next_priority'])
state['next_priority']='Test a bounded, independently interpreted continuation-familiarity question that distinguishes familiar components from an unfamiliar conjunction without substituting effort or remembered practice. Compare B_summary/B_relation/B_fit at fixed grain. Reopen actuator provenance only with an actual apparatus and a specific blocked mainline inference.'
state['next_priority_after_A4H']=state['next_priority']
state['latest_activity_persistence_before_A4H']=state.get('latest_activity_persistence')
state['latest_activity_persistence']={'status':'A4H_SCIENCE_CHECKPOINT_VERIFIED_FINAL_DUAL_SAVE_PENDING','checkpoint':'435dacd0d1206e8a5d4b7f69ba114384f2ac2300','receipt':rel+'/PERSISTENCE_RECEIPT.json'}
state['latest_persistence_receipt']=rel+'/PERSISTENCE_RECEIPT.json'
repair=dict(id='A4H-G00',corrupt_sha256=sha(bad),corrupt_bytes=len(bad),
 last_inspected_valid_commit='e792283f086a914da0b289c1554b7c1342742820',
 valid_source_sha256=sha(restored),prior_ids=prior_ids,
 reconstructed_followups=list(by_id),source_for_later_entries='CURRENT_STATE.json at recovery head2e27c1e5cdcb64b2b713375fc1ea2303e7ec969c',
 completed_map_modified=False,exact_corruption_cause='OPEN; encoded truncated-output warning observed',
 history_preserved=True)
write(root/'UNIFIED_RESEARCH_INDEX.json',index)
repair['repaired_index_sha256']=sha((root/'UNIFIED_RESEARCH_INDEX.json').read_bytes())
write(out/'INDEX_REPAIR.json',repair)
review='\n\n## A4H20261011 researcher response — compositional bodily action familiarity\n\n[Response]('+rel+'/REVIEW_RESPONSE.md) · [note]('+rel+'/RESEARCH_NOTE.md) · [gaps]('+rel+'/GAP_LEDGER.md). Fixed-grain equal component/pair exposure does not fix currently consumed higher-order continuation relations. This supplies a positive B_relation candidate, not H identity or calibration. QC10 remains ACKNOWLEDGED/OPEN; IA-QC11 and QC12/13 remain OPEN. R191 normalization remains OPEN; deep audit AUDIT_INCOMPLETE. A4H-G00 repairs corrupt navigation from a verified source plus later stable IDs; G06 preserves the temporary-workspace loss. No self-closed review and no C1/U1 change.\n'
f=root/'REVIEW_SUPERVISION.md'
if '## A4H20261011 researcher response' not in f.read_text():f.write_text(f.read_text()+review)
state['review_ledger_sha256']=sha(f.read_bytes())
state['publication_coverage']['latest_followup_application']=rel+'/PUBLICATION_COVERAGE_UPDATE.json'
write(root/'CURRENT_STATE.json',state)
for name,text in {
 'UCT_FORMAL_MAP.md':'\n\n### A4H：固定粒度的熟悉成分与组合\n[研究]('+rel+'/RESEARCH_NOTE.md)把已练成分/相邻对与当前使用的高阶接续关系分开，比较三项体验解释候选。有限例子不赋予H真值；0/0/0正式图增量，来源证书支线暂止。\n',
 'UCT_FORMAL_AUDIT.md':'\n\nA4H：[审查]('+rel+'/FORMAL_AUDIT.md)。固定粒度组合/使用反例不等于H校准；所有all_of按AND，R173未触发。统一索引截断修复有独立记录；全历史深审仍AUDIT_INCOMPLETE。\n',
 'HANDOFF.md':'\n\n## A4H20261011 接续\n[中文交接]('+rel+'/HANDOFF_ZH.md)。固定粒度比较熟悉成分与当前接续关系，返回体验内候选解释。最新优先级见CURRENT_STATE；损坏索引修复与本地维护丢失见GAP_LEDGER，双份状态见固定主交接与收据。\n',
 'MEMORY.md':'\n\n## A4H20261011\n熟悉成分/相邻对的计数不能代替当前使用的高阶接续关系。三候选均未校准H；不再无界扩展来源证书。索引修复及本地恢复记录见'+rel+'。\n',
 'MASTER_INDEX.md':'\n\n- [A4H：固定粒度的动作熟悉性组合问题]('+rel+'/RESEARCH_NOTE.md)；[交接]('+rel+'/HANDOFF_ZH.md)；[索引修复]('+rel+'/INDEX_REPAIR.json)。停用候选，非正式图晋级。\n'
}.items():
 f=root/name
 if 'A4H20261011' not in f.read_text():f.write_text(f.read_text()+text)
write(out/'PUBLICATION_COVERAGE_UPDATE.json',dict(round='A4H20261011',inherited_version='UCT-PUB-v1.0.33',new_publication=False,new_standalone_paper=False,decision='HOLD; candidate comparison and standard finite witness',primary_prior_art='Sakai et al.2003 DOI10.1007/s00221-003-1548-8',scope='No complete fresh publication census; preserve concurrent ASI_CC manuscript without UCT promotion.'))
sources=['RESEARCH_MASTER_GUIDE.md','AGENTS.md','REVIEW_SUPERVISION.md','UCT_FORMAL_GRAPH.json','integration/UCT-INTEGRATION-v1.0.0/UNIFIED_MAP.json.gz','records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md','records/R173_Familiar_Mineness_and_Retentive_History_20261008/Familiar_Mineness_Retentive_History_v0_1.md','records/R199_CONSTITUTIVE_RETENTION_AND_FAMILIARITY_2026-10-10/RESEARCH_NOTE.md','records/A3O20261010_Route_Grain_Selection_Crossing/RESEARCH_NOTE.md','records/A3X20261010_Action_Familiarity_Content_Admissibility/RESEARCH_NOTE.md','records/A4A20261011_Formation_Intervention/RESEARCH_NOTE.md']
write(out/'SOURCE_HASHES.json',{n:sha((root/n).read_bytes()) for n in sources})
print(json.dumps({'followup_ids':list(by_id),'index_sha256':repair['repaired_index_sha256'],'pending_count':index['pending_count']}))

