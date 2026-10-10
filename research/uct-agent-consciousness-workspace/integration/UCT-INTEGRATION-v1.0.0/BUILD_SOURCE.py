import json,hashlib,gzip,copy,re,collections,pathlib,shutil,html
P=pathlib.Path(__file__).parent; S=P/'source'; O=P/'output'; O.mkdir(exist_ok=True)
BASE=json.loads((P/'base.json').read_text())['commit']
VER='UCT-INTEGRATION-v1.0.0'; V='integration/'+VER; REC='records/NAV20261010_Map_Integration'
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def read(n):return json.loads((S/n).read_text())
def put(n,s):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s if isinstance(s,bytes) else s.encode())
def js(n,x):put(n,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
state=read('CURRENT_STATE.json'); mods=read('UCT_FORMAL_GRAPH_MODULES.json'); reg=read('RESEARCH_REGISTRY.json'); idx=read('FORMAL_MAP_EXTENSION_INDEX.json'); sessions=read('RESEARCH_SESSION_LOG_INDEX.json'); pub=read('PUBLICATION_COVERAGE.json')
allids=list(state['pending_checkpoints_not_promoted'])
rows={}
for source,items in [('modules',mods['pending_checkpoints']),('registry',reg['pending_checkpoints'])]:
 for r in items:
  i=r.get('id',r.get('research_id'));rows.setdefault(i,{})[source]=r
  if i not in allids:allids.append(i)
assert len(allids)==38
groups=[
 ('calibration','行动校准与可识别性',['AC20261009','IL20261009','ONLINE-AC-PROBE-20261009','R189-HACA-20261009'],'在什么干预、记忆与时限条件下，能识别或使用实际行动关系？','R172:ONLINE_ACTION_USE_RELATION'),
 ('self','自我相关组织的分解',['R190-PCBC-20261009','R191-OCCA-20261009','R198-SPNS-20261010'],'实际行动中心、冲突授权、归属感、能动感和熟悉感如何区分？','R173:FAMILIAR_MINENESS_BOUNDARY'),
 ('bridge','体验端点与校准边界',[f'R{n}-'+s+'-202610'+('09' if n<197 else '10') for n,s in [(192,'CTBI'),(193,'NCI'),(194,'CPP'),(195,'IPA'),(196,'TPD'),(197,'FEO'),(199,'CPC'),(200,'SCF'),(201,'ROTM'),(202,'TMAB'),(203,'ACD')]],'怎样把结构或代理指标与一个独立指定的体验目标联系起来？','R173:FAMILIAR_MINENESS_BOUNDARY'),
 ('routing','相同行为下的信息来源与使用',['R204-SAU-20261010','R205-ASC-20261010','SCU20261010'],'行为相同时，哪些干预才能识别被实际使用的信息？','R172:ONLINE_ACTION_USE_RELATION'),
 ('device','具体消费者与装置可行性',['MPC20261010','CBI20261010','EIP20261010','DVC20261010','A3S20261010','A3P20261010','A3U20261010','A3L20261010'],'运动／本体感觉通路的同实例干预条件是否真正满足？','R177:SOURCE_FEATURE_SEPARATION'),
 ('familiarity','身体熟悉感与保留历史',['A3M20261010','A3N20261010','A3O20261010','A3Q20261010','A3R20261010','A3V20261010'],'保留历史与当下协调怎样对应身体熟悉感，哪些选择器条件仅适用于支线？','R173:RETENTIVE_EXPERIENTIAL_COORDINATE'),
 ('psychometrics','身体判断的噪声识别',['CTD20261010','CTD2-20261010','CTD3-20261010'],'身体判断数据能区分哪些噪声模型，又有哪些识别上限？','R173:FAMILIAR_MINENESS_BOUNDARY')]
membership={i:g[0] for g in groups for i in g[2]};assert set(membership)==set(allids)
graphbytes=(P/'restored/UCT_EFFECTIVE_GRAPH.json').read_bytes();graph=json.loads(graphbytes);assert sha(graphbytes)==state['complete_map_sha256']
assert sha((P/'restored/REVIEW_LEDGER.json').read_bytes())==state['review_ledger_sha256']
coreids={n['id'] for n in graph['nodes']}
documents={}; entries=[]
for i in allids:
 old=rows.get(i,{})
 paths=[r.get('path',r.get('module',r.get('source'))) for r in old.values()]
 if i=='A3R20261010':paths.append('records/A3R20261010_Selector_Participation_Contract/MAP_EXTENSION.json')
 path=next((x for x in paths if x and (S/x).exists() and 'EXTENSION' in x),None)
 assert path,(i,paths)
 raw=(S/path).read_bytes();doc=json.loads(raw);documents[i]=copy.deepcopy(doc)
 root=path.rsplit('/',1)[0];root=root.removesuffix('/governance')
 r={**old.get('modules',{}),**old.get('registry',{})}
 title=r.get('title')
 handoffs=[x for x in [r.get('handoff'),root+'/HANDOFF_ZH.md',root+'/CURRENT_HANDOFF_ZH.md'] if x and (S/x).exists()]
 note=next((x for x in [r.get('source'),doc.get('source_note'),root+'/RESEARCH_NOTE.md',root+'/RESEARCH_CHECKPOINT.md'] if isinstance(x,str) and (S/x).exists()),None)
 if not title and note:title=(S/note).read_text().splitlines()[0].lstrip('# ')
 title=title or i
 e={'id':i,'title':title,'family':membership[i],'path':path,'source_sha256':sha(raw),'result_version':r.get('result_version',doc.get('result_version')),'status':'PENDING_CHECKPOINT_DISABLED','enabled_as_established_premises':False,'completed_map_release':state['release_id'],'first_map_release':None,'navigation_integration':VER,'source':note,'handoff':handoffs[0] if handoffs else None,'audit':next((x for x in [r.get('compatibility_audit'),r.get('review'),root+'/MAP_AUDIT.md',root+'/governance/MAP_AUDIT.md'] if isinstance(x,str) and (S/x).exists()),None),'candidate_counts':{'nodes':len(doc.get('nodes',doc.get('claims',[]))),'rules':len(doc.get('rules',doc.get('deductive_dependencies',[]))),'contexts':len(doc.get('context_links',doc.get('contexts',[]))),'applications':len(doc.get('applications',[]))},'prior_entry_snapshots':old,'promotion_requirement':'Complete applicable semantic compatibility/proof review against the current completed release and retain independent actual/phenomenal obligations. Registration is not premise truth.'}
 if i.startswith('CTD'):e['result_family']='CTD';e['version_relation']='Successive research stages; preserve distinct claim IDs; not three independent paper counts.'
 if i in ['SCU20261010','CTD20261010','CTD2-20261010','CTD3-20261010']:e['publication']='See PUBLICATION_COVERAGE.json exact claim/version coverage; publication does not promote this candidate.'
 entries.append(e)

# Apply only already-published-in-workspace correction overlays, with exact guards.
corroot='records/SCU20261010_Source_Consumer_Protocols/corrections/'
corindex=read(corroot+'EFFECTIVE_CORRECTION_INDEX.json'); corrections=[];override_log=[]
for desc in corindex['overlays']:
 path=corroot+desc['path'];raw=(S/path).read_bytes();assert sha(raw)==desc['sha256']; c=json.loads(raw)
 for src in c['sources']:
  assert sha((S/src['path']).read_bytes())==src['sha256'],src['path']
 for change in c['effective_overrides']:
  matches=[]
  for i,doc in documents.items():
   for typ in ['nodes','rules']:
    for n in doc.get(typ,[]):
     if n.get('id')==change['target_id']:matches.append((i,n))
  assert len(matches)==1,change['target_id'];i,n=matches[0]
  assert sha(canon(n))==change['expected_original_record_sha256'],change['target_id']
  n.update(change['replacement_fields']);override_log.append({'checkpoint':i,'target_id':n['id'],'overlay':path,'historical_source_preserved':True})
 corrections.append({'path':path,'sha256':sha(raw),'document':c,'enabled_as_established_premises':False})

# Keep scopes/defaults/raw source locators. Presentation keys never replace scientific IDs.
objects=[]
for e in entries:
 doc=documents[e['id']]
 for kind,keys in [('node',['nodes','claims']),('rule',['rules','deductive_dependencies']),('context',['context_links','contexts']),('application',['applications'])]:
  items=next((doc[k] for k in keys if k in doc),[])
  for pos,x in enumerate(items):
   ident=x.get('id',x.get('claim_id'))
   objects.append({'key':e['id']+'::'+kind+'::'+(ident or 'position-'+str(pos)),'scientific_id':ident,'checkpoint':e['id'],'kind':kind,'source_path':e['path'],'source_position':pos,'enabled_as_established_premises':False,'record':x})
for c in corrections:
 for kind,key in [('node','nodes'),('rule','rules'),('context','context_links')]:
  for pos,x in enumerate(c['document'].get(key,[])):
   ident=x.get('id');objects.append({'key':c['document']['overlay_id']+'::'+kind+'::'+(ident or str(pos)),'scientific_id':ident,'checkpoint':c['document']['overlay_id'],'kind':kind,'source_path':c['path'],'source_position':pos,'enabled_as_established_premises':False,'record':x})
assert len({x['key'] for x in objects})==len(objects)
candidateids=collections.defaultdict(list)
for o in objects:
 if o['scientific_id'] and o['kind']=='node':candidateids[o['scientific_id']].append(o['key'])
edges=[];unresolved=[]
for o in objects:
 x=o['record'];refs=[]
 if o['kind']=='rule':
  assert isinstance(x.get('all_of',[]),list)
  refs=[('all_of',v) for v in x.get('all_of',[])]+[('conclusion',x.get('conclusion'))]
 elif o['kind']=='application':
  refs=[('completed_node_refs',v) for v in x.get('completed_node_refs',[])]+[('pending_node_refs',v) for v in x.get('pending_node_refs',[])]
 elif o['kind']=='context':refs=[('context_'+k,x.get(k)) for k in ['from','to','source','target'] if isinstance(x.get(k),str)]
 for role,r in refs:
  if not isinstance(r,str):continue
  targets=['completed::'+r] if r in coreids else candidateids.get(r,[])
  if not targets and r in allids:targets=['checkpoint::'+r]
  status='RESOLVED_COMPLETED' if r in coreids else ('RESOLVED_CHECKPOINT' if r in allids else ('RESOLVED_PENDING' if len(targets)==1 else ('AMBIGUOUS_PENDING' if targets else ('DECLARED_CONTEXT_SOURCE_NOT_NODE' if role.startswith('context_') else 'UNRESOLVED_DEDUCTIVE_REFERENCE'))))
  edge={'object':o['key'],'role':role,'reference':r,'targets':targets,'resolution':status,'deductive':False,'note':'Navigation only; a candidate rule retains its own AND contract and disabled state.'};edges.append(edge)
  if not targets or len(targets)>1:unresolved.append(edge)

drift={}
for n,ids in [('CURRENT_STATE.json',state['pending_checkpoints_not_promoted']),('FORMAL_MAP_EXTENSION_INDEX.json',idx['pending_disabled']),('RESEARCH_REGISTRY.json',[x.get('id',x.get('research_id')) for x in reg['pending_checkpoints']]),('UCT_FORMAL_GRAPH_MODULES.json',[x['id'] for x in mods['pending_checkpoints']]),('RESEARCH_SESSION_LOG_INDEX.json',sessions['pending_checkpoints'])]:
 drift[n]={'before_count':len(ids),'missing':list(i for i in allids if i not in ids),'after_count':len(allids)}
catalog={'schema':'uct-unified-research-catalog/1','version':VER,'source_commit':BASE,'completed_map':state['release_id'],'publication_coverage':pub['coverage_version'],'latest_scientific_research':state['latest_research'],'families':[{'id':g[0],'title':g[1],'checkpoint_ids':g[2],'question':g[3],'completed_anchor':g[4],'relation_type':'EDITORIAL_NAVIGATION_NOT_DEDUCTION'} for g in groups],'pending_count':len(entries),'pending_checkpoints':entries,'effective_corrections':corrections,'scientific_promotion':False,'audit_depth_status':'AUDIT_INCOMPLETE','scope':'All 38 pending identities from the pinned current-state and available canonical registries; not a claim that every unregistered archive file has been rediscovered.'}
js('UNIFIED_RESEARCH_INDEX.json',catalog)
unified={'schema':'uct-unified-map-view/1','version':VER,'source_commit':BASE,'completed_graph_sha256':sha(graphbytes),'completed_graph':graph,'pending_documents_effective':documents,'pending_objects':objects,'pending_navigation_edges':edges,'correction_records':corrections,'inference_policy':'Completed rules retain exact all_of contracts; pending objects and editorial links are disabled. This view is not a proof engine.'}
put(V+'/UNIFIED_MAP.json.gz',gzip.compress(json.dumps(unified,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
js(V+'/REFERENCE_RESOLUTION.json',{'edges':edges,'unresolved_or_ambiguous':unresolved,'policy':'Unresolved contextual literature/import references are retained, not invented as nodes; unresolved deductive targets remain explicit blockers.'})
js(V+'/RECONCILIATION.json',{'base_commit':BASE,'registries':drift,'effective_correction_targets':override_log,'pending_identity_count':len(entries),'object_counts':dict(collections.Counter(o['kind'] for o in objects)),'scientific_graph_unchanged':True})

# Stable current pages, exact historical snapshots.
archive=['START_HERE.md','UCT_FORMAL_MAP.md','UCT_FORMAL_AUDIT.md','HANDOFF.md','MASTER_INDEX.md','MEMORY.md','README.md','RESEARCH_MASTER_GUIDE.md','AGENTS.md']
for n in archive:put(V+'/history/'+n,(S/n).read_bytes())
nav='[总览](UCT_FORMAL_MAP.md) · [全部候选](PENDING_RESEARCH.md) · [当前状态](CURRENT_STATE.json) · [统一登记](UNIFIED_RESEARCH_INDEX.json) · [审查](UCT_FORMAL_AUDIT.md)'
overview='# UCT 统一研究地图\n\n'+nav+'\n\n'+f'整合版本 **{VER}**。正式科学图 **{state["release_id"]}**；最新科学研究 **{state["latest_research"]["id"]}**；发表覆盖 **{pub["coverage_version"]}**。\n\n'
overview+='## 三层结构\n\n| 层 | 内容 | 如何使用 |\n|---|---|---|\n| 基础与正式条件推导 | 913 节点、424 条有效规则、261 条非演绎关联；10 条历史规则暂停 | 保留公设、定义、条件推导和证据的不同身份；规则的所有前提须共同满足 |\n| 待整合研究 | 38 个检查点，分为下方 7 个问题家族 | 可查阅结果、修正与证据；不能直接当作已成立的总图前提 |\n| 历史与审查 | 原始版本、失败、修正、证明账和发表台账 | 追溯出处；历史“当前”标题不覆盖 CURRENT_STATE.json |\n\n'
overview+='## 理论主干\n\n1. **实际物理过程与组织**：先固定对象、边界、时间和完整签名；数学模型不自动成为实际实例。\n2. **基础体验**：C1 保持公设身份；U1 的结论依赖其原有前提。局部与整体可共存，无新增复杂度或唯一主体门槛。\n3. **组织、智能与报告**：能力受任务和资源条件约束；表现、有限观测和完整组织分开。\n4. **体验中的自我相关结构**：归属感、能动感、身体熟悉感、概念我和报告分别指定；保留历史与当下使用可作条件解释。\n5. **桥接与检验**：从实际组织到指定感受仍需独立目标、可靠端点和同实例证据；相同行为不代表相同内部使用关系。\n\n这五项是阅读顺序，不是新增演绎规则。完整逐项合同在正式图中保留。\n\n'
overview+='## 研究分支与主线连接\n\n| 家族 | 检查点数 | 要解决的问题 |\n|---|---:|---|\n'
for g in groups:overview+=f'| [{g[1]}](PENDING_RESEARCH.md#{g[0]}) | {len(g[2])} | {g[3]} |\n'
overview+='\n## 当前收束点\n\n'+state['next_priority']+'\n\n通俗地说：固定实际身体路线，区分“保留历史带来的熟悉”与“当下协调、提示熟悉或动作流畅”。最新 A3V 保留 R173 无需双政策竞争的适用路线；不能把选择器证书失败变成无体验或无熟悉感。\n\n'
overview+=f'## 精确数据与历史\n\n- [统一图压缩文件]({V}/UNIFIED_MAP.json.gz)：完整正式图、全部候选原始合同的有效副本、应用回链和已登记修正，候选保持停用。\n- [恢复脚本]({V}/restore_unified_map.py)：导出完整 JSON；不需要网络。\n- [正式图模块入口](UCT_FORMAL_GRAPH_MODULES.json)：原科学组装顺序及哈希。根目录旧 UCT_FORMAL_GRAPH.json 仅为历史基底。\n- [引用解析与缺口]({V}/REFERENCE_RESOLUTION.json)、[本轮整合报告]({REC}/HANDOFF_ZH.md)。\n- [整理前地图]({V}/history/UCT_FORMAL_MAP.md)、[历史目录]({V}/HISTORY_INDEX.md)。\n\n所有新分组与导航边为非演绎元数据。目录整合完成不表示全历史证明重证、实际前提满足或体验端点得到验证。\n'
put('UCT_FORMAL_MAP.md',overview)
pending='# 待整合研究全表\n\n'+nav+'\n\n以下 38 项已统一登记；全部保持停用。节点／规则／关联数字是源文档记录数，不是原创成果数；应用型记录允许 0 新节点。三个 CTD 阶段属于同一成果家族。\n'
for g in groups:
 pending+=f'\n<a id="{g[0]}"></a>\n\n## {g[1]}\n\n{g[3]} 主干定位：`{g[4]}`（导航关联，不添加推理前提）。\n\n| 检查点 | 内容与源文档 | 节点/规则/关联/应用 | 交接 |\n|---|---|---|---|\n'
 for i in g[2]:
  e=next(e for e in entries if e['id']==i);c=e['candidate_counts'];title=e['title'].replace('|','／').replace('\n',' ')
  pending+=f'| {i} | [{title}]({e["path"]}) | {c["nodes"]}/{c["rules"]}/{c["contexts"]}/{c["applications"]} | '+(f'[交接]({e["handoff"]})' if e['handoff'] else '见源文档')+' |\n'
pending+='\n## 修正与采用条件\n\nR194、R201、R202 的 8 个既有修正已按原哈希应用到统一候选视图，原文件保留。额外修正节点及规则单独注明出处。A3P 对 A3S 文献范围的修正、A3L 对 A3U 救援条件的限定、A3V 对选择器支线的范围纠正仍须连同各轮证据阅读。未解决的 R191 normalization 和全历史审查深度不关闭。\n\n正式采用时，应逐项核对定义、量词、同实例联合前提、证明和反例，并重推受影响结论；新建科学图版本。具体实际实现与体验端点的真实性是另外的义务，不由目录或论文发表替代。\n'
put('PENDING_RESEARCH.md',pending)
put('START_HERE.md','# UCT 研究唯一阅读入口\n\n'+nav+'\n\n1. 读 [研究指南](RESEARCH_MASTER_GUIDE.md)，保持体验—组织—智能—我感主线。\n2. 读 [总图](UCT_FORMAL_MAP.md)，分清正式图与待整合层。\n3. 按问题到 [候选全表](PENDING_RESEARCH.md)，读取源文档、修正和证据。\n4. 继续研究前以 [CURRENT_STATE.json](CURRENT_STATE.json) 的 latest_research 和 next_priority 为准。\n5. 保存前运行 `python integration/UCT-INTEGRATION-v1.0.0/validate_navigation.py --root .`，同步五个候选登记入口。\n\n本轮导航整合：'+VER+'；正式科学图：'+state['release_id']+'。旧起始页已原样归档。\n')
put('MASTER_INDEX.md','# UCT 主索引\n\n'+nav+'\n\n- [研究指南](RESEARCH_MASTER_GUIDE.md)\n- [当前交接](HANDOFF.md)\n- [研究注册表](RESEARCH_REGISTRY.json)\n- [工作日志索引](RESEARCH_SESSION_LOG_INDEX.json)\n- [发表覆盖](PUBLICATION_COVERAGE.json)\n- [审查监督原始账](REVIEW_SUPERVISION.md)\n- [正式版本目录](versions/)\n- [本轮整合及原始历史]('+V+'/HISTORY_INDEX.md)\n\n研究按问题家族阅读；轮次编号用于追溯。精确主张和论文覆盖仍以各自台账为准。\n')
put('HANDOFF.md','# 当前交接\n\n'+nav+'\n\n科学接续：**'+state['latest_research']['id']+'**。\n\n[最新科学交接]('+state['latest_research']['handoff']+') · [本轮地图整理交接]('+REC+'/HANDOFF_ZH.md)\n\n下一科学问题：'+state['next_priority']+'\n\n正式图 '+state['release_id']+'，发表覆盖 '+pub['coverage_version']+'。导航版本 '+VER+' 统一了 38 个候选及修正；没有把它们升级为成立的科学前提。历史保存、发表和审查状态请分别查 CURRENT_STATE.json、PUBLICATION_COVERAGE.json 和 REVIEW_SUPERVISION.md。\n\n[整理前完整交接]('+V+'/history/HANDOFF.md)\n')
put('UCT_FORMAL_AUDIT.md','# UCT 地图审查状态\n\n'+nav+'\n\n| 范围 | 当前结论 |\n|---|---|\n| 正式科学图 v1.1.2 | 保留原 1,608 项合同兼容性审查与组装验证；原哈希不变 |\n| 本轮导航整合 | 38 个检查点集合、源文件哈希、已有修正、引用解析、历史归档及入口同步 |\n| 待整合科学内容 | 全部停用；不视为已成立的总图前提 |\n| 全历史独立语义与证明审查 | AUDIT_INCOMPLETE；本轮未逐一重证 |\n| 实际应用与指定体验桥接 | OPEN |\n\n[本轮精确验证](integration/'+VER+'/VALIDATION.json) · [引用缺口](integration/'+VER+'/REFERENCE_RESOLUTION.json) · [原审计](integration/'+VER+'/history/UCT_FORMAL_AUDIT.md) · [监督账](REVIEW_SUPERVISION.md)\n\n保留 QC-20261008-10、IA-QC11、QC-20261008-12、QC-20261008-13、SCU-OPEN-R191-NORMALIZATION 与 SCU-AUDIT-DEPTH，及各候选的其他 OPEN。结构遍历不等于语义证明，候选登记不等于实际前提成立。\n')
put('README.md','# UCT agent-consciousness research workspace\n\nBegin at [START_HERE.md](START_HERE.md).\n\n'+nav+'\n\nCompleted scientific release: '+state['release_id']+'. Unified navigation: '+VER+'. All 38 pending checkpoints are indexed and remain disabled. Exact historical research and publication records are preserved.\n')
# Preserve instructions; replace only round-specific notices before the versioned policy.
guide=(S/'RESEARCH_MASTER_GUIDE.md').read_text();m=re.search(r'(?m)^版本[:：]|^\*\*版本',guide)
if not m:m=re.search(r'(?m)^## 0\.',guide)
assert m
policy_preface='\n\n'.join(p for p in guide[:m.start()].split('\n\n') if p.startswith(('**政策 ID','本文件落实','**一句话原则','原总指南的全部字节')))
put('RESEARCH_MASTER_GUIDE.md',guide.splitlines()[0]+'\n\n**稳定入口：** [START_HERE.md](START_HERE.md) → [统一地图](UCT_FORMAL_MAP.md) → [全部候选](PENDING_RESEARCH.md)。科学接续及下一题以 CURRENT_STATE.json 为准；历史逐轮通知见[整理前指南]('+V+'/history/RESEARCH_MASTER_GUIDE.md)。本次只整理导航，以下政策正文保持原样。\n\n'+policy_preface+'\n\n'+guide[m.start():])
agent=(S/'AGENTS.md').read_text();put('AGENTS.md','# Stable current navigation — '+VER+'\n\nRead RESEARCH_MASTER_GUIDE.md, START_HERE.md, CURRENT_STATE.json and UNIFIED_RESEARCH_INDEX.json first. Round-specific current/next notices below are preserved historical snapshots; they never override current state or the master guide. Do not prepend another round summary to every entry page. Maintain one canonical checkpoint registry and regenerate/synchronize pending identity sets, retaining disabled status and scientific/publication separation. See integration/'+VER+'/validate_navigation.py.\n\n'+agent)
memory=(S/'MEMORY.md').read_text();put('MEMORY.md','# UCT durable memory\n\n'+nav+'\n\nThe full prior memory is preserved at [historical memory]('+V+'/history/MEMORY.md). Required foundations remain UCT I/II/III, the clinical source and their verified editions; follow the source-specific contracts in the completed map. C1/U1, local/whole coexistence, no new basal gate, and distinction of organization/experience/intelligence/self/report remain binding.\n\nScientific continuation and next question live in CURRENT_STATE.json. All pending source documents, effective corrections and family membership live in UNIFIED_RESEARCH_INDEX.json; history never silently becomes an established premise. Publication, storage, conditional validity, actual support and phenomenal support remain separate states.\n')
hist='# 历史快照索引\n\n本目录保存整理前原始字节；其中相对链接按原工作区根目录解释。当前导航请返回 START_HERE.md。\n\n'
for n in archive:hist+=f'- [{n}](history/{n}) · 原 SHA-256 `{sha((S/n).read_bytes())}`\n'
put(V+'/HISTORY_INDEX.md',hist)

# One exact set at every current entry; retain old record fields as metadata.
def updated_rows(old):
 by={x.get('id',x.get('research_id')):x for x in old};out=[]
 for e in entries:
  x=copy.deepcopy(by.get(e['id'],{}));x.update({k:e[k] for k in ['id','title','path','status','enabled_as_established_premises','source_sha256','candidate_counts','family']});x['navigation_index']='UNIFIED_RESEARCH_INDEX.json';x['navigation_integration']=VER
  if e['handoff']:x['handoff']=e['handoff']
  if e['source']:x.setdefault('source',e['source'])
  out.append(x)
 return out
reg['pending_checkpoints']=updated_rows(reg['pending_checkpoints']);mods['pending_checkpoints']=updated_rows(mods['pending_checkpoints']);idx['pending_disabled']=allids;idx['status']='All 38 checkpoints indexed from the same registry; all remain disabled. Navigation complete, scientific promotion false.';idx['latest_candidate']=next(e['path'] for e in entries if e['id']==state['latest_research']['id']);idx['latest_scoped_audit']=next(e['audit'] for e in entries if e['id']==state['latest_research']['id']);sessions['pending_checkpoints']=allids
for j in [state,mods,reg,idx,sessions]:j['navigation_integration']={'version':VER,'entry':'UNIFIED_RESEARCH_INDEX.json','overview':'UCT_FORMAL_MAP.md','report':REC+'/HANDOFF_ZH.md','scientific_promotion':False,'pending_count':38}
state['pending_checkpoints_not_promoted']=allids
state['latest_navigation_activity']={'id':'NAV20261010','version':VER,'work_log':REC+'/WORK_LOG.md','handoff':REC+'/HANDOFF_ZH.md','scope':'NAVIGATION_AND_DISABLED_CANDIDATE_ASSEMBLY'}
sessions['latest_navigation_activity']=state['latest_navigation_activity']
for n,j in [('CURRENT_STATE.json',state),('UCT_FORMAL_GRAPH_MODULES.json',mods),('RESEARCH_REGISTRY.json',reg),('FORMAL_MAP_EXTENSION_INDEX.json',idx),('RESEARCH_SESSION_LOG_INDEX.json',sessions)]:js(n,j)
put('CHANGELOG.md','# '+VER+' — unified map navigation, 2026-10-10\n\nReconciled five pending registries to the same 38 identities; grouped seven question families; assembled disabled candidate view with eight guarded existing corrections; archived old navigation byte-for-byte. Scientific v1.1.2 and publication coverage '+pub['coverage_version']+' unchanged. See '+REC+'/HANDOFF_ZH.md.\n\n'+(S/'CHANGELOG.md').read_text())
print(json.dumps({'entries':len(entries),'families':len(groups),'objects':dict(collections.Counter(o['kind'] for o in objects)),'unresolved_or_ambiguous':len(unresolved),'overrides':len(override_log),'drift':drift},ensure_ascii=False))
