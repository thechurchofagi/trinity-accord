from pathlib import Path
import json,shutil,hashlib,re,sys,datetime
P=Path(__file__).parent;S=P/'source';O=P/'output';V='integration/UCT-INTEGRATION-v1.0.0';R='records/NAV20261010_Map_Integration'
def put(p,s):
 f=O/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s)
def js(p,x):put(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
base=json.loads((P/'base.json').read_text())['commit'];s=json.loads((O/'CURRENT_STATE.json').read_text());cat=json.loads((O/'UNIFIED_RESEARCH_INDEX.json').read_text());valid=json.loads((O/V/'VALIDATION.json').read_text());g=json.loads((P/'restored/UCT_EFFECTIVE_GRAPH.json').read_text())
# Remove operational tail from policy presentation, keep exact archival original.
guide=(O/'RESEARCH_MASTER_GUIDE.md').read_text();guide=guide.split('# Current checkpoint addendum — R197')[0].rstrip()+'\n';put('RESEARCH_MASTER_GUIDE.md',guide)
report=f'''# UCT 地图整合交接 — UCT-INTEGRATION-v1.0.0

本轮已完成导航和停用候选视图整合。正式科学图仍为 UCT-MAP-v1.1.2；全历史独立语义／证明审查未完成，候选科学采用不由本轮代办。

固定仓库 `thechurchofagi/trinity-accord`；分支 `uct-agent-consciousness-workspace`；根目录 `research/uct-agent-consciousness-workspace`。源提交 `{base}`。用户授权：2026-10-10 要求把上一轮发现的地图分散问题整合完成。

## 实际完成

1. 以 CURRENT_STATE 与各登记表的并集核对 38 个检查点；统一当前状态、扩展索引、研究注册表、模块清单及日志索引。此前数量依次为 38、33、36、25、35，现在均为 38。
2. 用 7 个问题家族组织候选：行动校准、自我相关组织、体验端点桥接、来源与使用、装置与消费者、身体熟悉感、身体判断噪声。家族与主干定位都是非演绎导航。
3. 恢复并验证原封装 82 个文件；正式图 913 节点、424 条有效规则、261 条非演绎关联，10 条暂停规则；1,608 项审查账原哈希保留。
4. 将全部候选文档及原有默认合同纳入统一数据视图。含 360 条节点／声明记录、163 条规则记录、188 条背景关联记录、16 条应用回链；数量包含已登记修正新增记录，是文档记录数，不能当作独立原创成果数或正式图增长。
5. 对 R194、R201、R202 的 8 个修正目标执行原记录哈希守卫，合入原已登记修正；历史源文件不覆盖，修正来源与顺序完整记录。
6. 检查全部候选规则的 all_of／conclusion 及应用回链：没有未解析的演绎引用或多义节点目标。另有 6 条明确的文献／主题背景引用，按非节点来源保留，不伪造为演绎节点。
7. 重写简洁总图、唯一入口、主索引、交接和审计首页；原首页、指南和记忆按原字节归档。指南政策正文和前言中的最高原则保留，逐轮“当前／最新”通知进入历史。
8. 保留 CTD 三个阶段的不同声明，归入同一成果家族；不把它们算作三篇新论文。保持发表覆盖 UCT-PUB-v1.0.31，未产生新科学主张或公开论文。

## 使用入口

- `START_HERE.md`：统一开始点。
- `UCT_FORMAL_MAP.md`：主干、七个分支与当前收束点。
- `PENDING_RESEARCH.md`：38 项逐项来源、交接与记录数量。
- `UNIFIED_RESEARCH_INDEX.json`：同源目录、源哈希和状态。
- `{V}/UNIFIED_MAP.json.gz`：完整正式图及停用候选有效副本。
- `{V}/COMPLETED_RULE_ROUTES.md`：424 条原有合取推理路线；完整限制仍在统一图对象中。
- `{V}/REFERENCE_RESOLUTION.json`：逐引用解析。
- `{V}/RECONCILIATION.json`：各入口补齐明细及 8 项修正。
- `{V}/VALIDATION.json`：本轮实际检查结果。
- `{V}/HISTORY_INDEX.md`：历史原字节及哈希。

## 边界与下一步

本次做完的是地图组织、登记对齐和可追溯候选装配。候选保持停用，没有宣称 v1.1.3 科学版已经完成，也未把已有局部证明等同于全历史重证。保留 QC-20261008-10、IA-QC11、QC-20261008-12、QC-20261008-13、SCU-OPEN-R191-NORMALIZATION、SCU-AUDIT-DEPTH 及各候选全部其他 OPEN。

具体候选应以源文档、证明、修正和独立前提为依据完成科学采用。文献背景引用不算缺失的演绎前提；结构解析通过也不证明所有数学论证正确。本轮没有重新查新或独立重算科学实验，不新增原创性声明。

最新科学接续保持 A3V20261010。下一题是独立指定可错的身体熟悉感端点，固定实际身体路线粒度和消费关系，对比保留历史与当下协调；分开提示熟悉、动作流畅、归属报告和能动性。R173 的条件路线不以双政策 SPC 为普遍前提。

后续窗口新增候选时，应先更新唯一目录，再同步五个登记入口、分组和当前摘要；运行下方校验。不要向每个首页重复堆放同一轮日志。历史记录保留在本轮目录或各研究目录。

```bash
python integration/UCT-INTEGRATION-v1.0.0/validate_navigation.py --root .
python integration/UCT-INTEGRATION-v1.0.0/restore_unified_map.py --output UCT_UNIFIED_MAP_EXPANDED.json
```

保存状态见本轮 PERSISTENCE_RECEIPT.json；只有回读完成的提交才可称远端完成。
'''
put(R+'/HANDOFF_ZH.md',report)
put(R+'/WORK_LOG.md',f'''# NAV20261010 work log

Version: UCT-INTEGRATION-v1.0.0. Base: `{base}`. Task: integrate the fragmented map navigation and pending registry identified in the preceding status review.

Read the master guide, governing policy, version policy, AGENTS, MEMORY, HANDOFF, MASTER_INDEX, review supervision, current-state, registry/module/extension/session/publication indexes; restored the frozen capsule and inspected every pending map document plus the three effective correction overlays. Retrieved 22 root/capsule files and 124 registry-linked paths, then 277 current checkpoint references (overlapping paths reused). All downloads succeeded; this count is retrieval work, not scientific review depth.

Results: five registry sets reconciled; 38 pending identities in seven editorial families; 8 guarded existing record corrections; exact core and review-ledger byte hashes preserved. All pending inferential references resolve. Six named literature/topic contexts retained as external declarations.

Implementation failures retained: first build stopped on a Python string quoting error; next stopped because MPC used `source` rather than `path`/`module` for its extension. Fixed syntax and the schema adapter, reran successfully. No failed build was committed as a completed result. No theorem or empirical experiment was rerun. No new DOI/OTS/AR, publication, scheduler, CI or deployment action.

Publication coverage: UCT-PUB-v1.0.31 retained; no changed or newly disclosed scientific claim IDs. Existing publication status is separate from candidate adoption. No manuscript is warranted for a navigation-only change. Precise prior publication claims were not re-audited in this task.

See HANDOFF_ZH.md for results and remaining scientific obligations; VALIDATION.json for actual verification; PERSISTENCE_RECEIPT.json for real remote save/readback. The next scientific question remains A3V's independently oriented bodily-familiarity endpoint, not continued generic selector certification.
''')
js(R+'/PUBLICATION_COVERAGE_UPDATE.json',{'coverage_version':'UCT-PUB-v1.0.31','changed_scientific_claim_ids':[],'newly_covered_claim_ids':[],'reason_no_change':'Navigation-only integration; raw claim source bytes, exact published editions and publication coverage ledger unchanged. Existing guarded corrections already recorded in SCU are displayed, not new scientific corrections.','checked_sources':['PUBLICATION_COVERAGE.json','CURRENT_STATE.json','UCT_FORMAL_GRAPH_MODULES.json'],'main_branch_observed':'7b6634f67c38caa2726c64d7f70e32ff35dc8353','scope':'Existing local publication coverage reused; no new full public-deposit or priority audit.','manuscript_decision':'NOT_APPLICABLE_NAVIGATION_ONLY'})
js(R+'/PERSISTENCE_RECEIPT.json',{'id':'NAV20261010','version':cat['version'],'source_commit':base,'github_status':'PREPARED_NOT_YET_COMMITTED','library_status':'PENDING','completion_scope':'NAVIGATION_AND_DISABLED_CANDIDATE_ASSEMBLY','scientific_promotion':False})
put(R+'/RESEARCH_NOTE.md','# Unified navigation and disabled-candidate assembly\n\nThis is a research-management integration record, not a new scientific manuscript. See HANDOFF_ZH.md, WORK_LOG.md, the unified index, and integration/UCT-INTEGRATION-v1.0.0/VALIDATION.json. The existing completed scientific graph and proof ledger retain their original byte hashes. Candidate records remain disabled.\n')
route='# Completed conditional inference routes — UCT-MAP-v1.1.2\n\nAll premises within one row are AND; different rules for a conclusion remain alternative routes. These are inherited conditional schemas, not unconditional facts. This directory is an index only: read every exact scope, binding, source and proof field in UNIFIED_MAP.json.gz before reuse. Context links and pending candidates do not supply active premises.\n\n'
for r in g['rules']:
 route+='## '+r['id']+'\n\n'+'**ALL OF:** '+', '.join('`'+x+'`' for x in r['all_of'])+'\n\n**Conclusion:** `'+r['conclusion']+'`\n\n'+r.get('statement','')+'\n\n'
put(V+'/COMPLETED_RULE_ROUTES.md',route)
put(V+'/restore_unified_map.py',(P/'restore_unified_map.py').read_text());put(V+'/validate_navigation.py',(P/'validate_navigation.py').read_text())
put(V+'/BUILD_SOURCE.py',(P/'build.py').read_text());put(V+'/FINALIZE_SOURCE.py',Path(__file__).read_text())
o=(O/'UCT_FORMAL_MAP.md').read_text();o=o.replace('## 精确数据与历史','[正式图 424 条推导路线](integration/UCT-INTEGRATION-v1.0.0/COMPLETED_RULE_ROUTES.md)\n\n## 精确数据与历史');put('UCT_FORMAL_MAP.md',o)
shutil.copytree(O,P/'check',dirs_exist_ok=True)
sys.path.insert(0,str(P));from validate_navigation import check
result=check(P/'check');result.update({k:v for k,v in valid.items() if k not in result});js(V+'/VALIDATION.json',result)
# Manifest excludes only itself and future save receipts.
manifest=[]
for f in sorted(O.rglob('*')):
 if f.is_file() and f.name not in ['FILE_MANIFEST.json','PERSISTENCE_RECEIPT.json']:
  b=f.read_bytes();manifest.append({'path':str(f.relative_to(O)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
js(V+'/FILE_MANIFEST.json',{'files':manifest,'note':'Receipt commits may add operational save metadata; scientific baseline remains unchanged.'})
print(json.dumps({'validation':result,'changed_or_new_files':len(list(O.rglob('*.*'))),'total_bytes':sum(f.stat().st_size for f in O.rglob('*') if f.is_file())},ensure_ascii=False))
