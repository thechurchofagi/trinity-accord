# 成果家族、正式披露与待核增量盘点

**范围固定于 2026-10-09 的 UCT-MAP-v1.1.2 与研究分支 `310e744f8d0195d05fac4e56e807adc48784f0ca`。本报告是出版覆盖盘点，不是新科学地图版本。**

结论先行：当前地图的 **1,608 个审查项不能换算成 1,608 项科学发现**。MGTD 正式附件已经披露 v1.0.0 地图；RT/TH 正式附件又披露 TH v0.1。两类正式附件与现图/历史记录共有 **1,329 个稳定 ID 对应**，仅有 **279 个审查项没有在这两类附件中找到同 ID**。这 279 项里仍包括模型、前提、解释、开放义务、治理、规则与上下文，也可能有别处已发表或经典继承的内容，因此不是“279 项未发表新成果”。

完整逐 ID、逐文件机器清单见 [map_result_inventory.json](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/map_result_inventory.json)。所有已冻结地图、论文和审查台账保持原字节。

## 1. 论文目的与计数单位

论文的目标是让未来 AI 能准确定位、理解、复核和引用有价值的知识增量。是否值得成稿，取决于明确的新问题、新约束、新推导、新反例、新数据结论或可复用方法，以及它们比已发表主张多了什么。发表数量、版本数量、地图规模、证明程序通过次数和文字长度都不能替代这一标准。

建议采用四层身份：**工作/论文身份 → 成果家族 → 稳定主张 ID → 必要时的覆盖子句**。一篇论文可包含多家族；一家族可含许多模型和前提；一条复合主张可被前作覆盖一部分。规则只记录推导路线，上下文只记录非演绎关联。不要为了覆盖统计改动科学地图或增加假节点。

覆盖字段必须分开：

| 维度 | 回答的问题 | 不允许的替换 |
|---|---|---|
| 正式披露 | 哪一正式版本、正文或附件明确出现该声明？ | 有 DOI 就把引用文献也视为正文结果 |
| 正文语义覆盖 | 定义域、前提、量词与结论是否相同或被蕴含？ | 关键词相同、同 ID、日期较早就判 exact |
| 证明/证据完整性 | 原证明、模型或数据实际读到和验证到哪里？ | 地图节点存在就当证明成立 |
| 原创/增量 | 去掉经典知识和内部前作，还剩什么？ | 未检到 DOI 就当原创 |
| 实例/体验义务 | 当前哪个实际 P/I/K 与语义桥接已获独立支持？ | 条件式审查通过就把实际前提宣布为真 |

本库存中的 `coverage_status=exact` 只表示已经查到相同的**正式声明**，并由 `formal_disclosures` 明确给出载体和哈希。它不自动表示论文正文对该项作了完整证明。正文语义覆盖另存在 `body_semantic_coverage`。`unknown` 不是未发表；`not_claim` 不是无用，只是不把它当新增科学结果。

## 2. 地图、角色与来源的精确范围

| 对象 | 数量 | 解释 |
|---|---:|---|
| 节点 | 913 | 67 个前缀家族，混合结果、模型、前提、义务等 |
| 活跃规则 | 424 | 推导路线；不能再次加到其结论数量上 |
| 非演绎 context | 261 | 跨家族来源/概念关联 |
| 历史 SUSPENDED 规则 | 10 | 保留纠错史，未恢复启用 |
| 合计逐项覆盖 | 1,608 | 完整稳定 ID 清单 |
| 研究工作区树 | 2,002 entries / 1,838 files | `truncated=false`，仅当前固定 Git 工作区 |
| records 文件 | 1,643 | 分为 149 个文件组，不是149项科学成果 |

节点角色的工作性分类如下；“科学或数学结果声明”这一栏仍包括经典定理应用、内部重述、具体反例和待做优先权核查的结果，**不能解读成独立原创发现的个数**。

| 节点角色 | 数量 |
|---|---:|
| 理论承诺/本体论域 | 7 |
| 条件解释/运输 | 54 |
| 定义/模型 | 129 |
| 方法治理/推断边界 | 20 |
| 科学或数学结果声明 | 390 |
| 已报告证据/执行记录 | 14 |
| 前提/实例合同 | 220 |
| 开放义务 | 55 |
| 方法结果 | 4 |
| 纠正/撤回 | 7 |
| 继承来源/别名 | 13 |

分类逐 ID 保留原 `kind`、`status`、声明、作用域、原有推导路线、context 和来源锚点。完整语义审查的依据是既有 v1.1.2 审查，不声称本轮重新逐字重证所有历史论文和原始数据。

## 3. 已正式披露：必须修正的旧“未发表”判断

### 3.1 MGTD 正式证据附件

MGTD v1.0.1，DOI **10.5281/zenodo.23241982** 的正式附件含 UCT-MAP-v1.0.0：722 节点、343 活跃规则、203 context；REVIEW_LEDGER 另保留10条历史暂停规则。现图保留全部这些稳定 ID。

1,268 个活跃对象中，**1,266 个规范 JSON 对象完全相等**；只有以下两项发生有效修正：

| 稳定 ID | 已发表附件与现图的关系 | 现行解释 |
|---|---|---|
| `R173:THREE_TARGET_SEPARATION` | 同 ID 的旧声明已纠正 | 8种组织组合独立性撤回；AgencyLoop⇒Avail，最多6种；全部6种可实现仍未证明 |
| `BASE:CTX:143` | 关联文字修正 | 不再把旧八路独立性当有效关联 |

因此 A/B/C/D、TA15–19、R126–R177 及 CORE/EI/R183/OO/RU/R184/RC/IE 等在该附件中的声明，不能因原研究记录未有独立 DOI 而整体列为“未公开”。附件披露也不会把一个历史错误变成正确结论，更不会表示它是方法论文正文的独立科学贡献。来源：[UCT_EFFECTIVE_GRAPH.json](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/attachments/mgtd_v101/MGTD_Method_Paper_v1.0.1/evidence/UCT_EFFECTIVE_GRAPH.json) 与对应 [REVIEW_LEDGER.json](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/attachments/mgtd_v101/MGTD_Method_Paper_v1.0.1/evidence/REVIEW_LEDGER.json)。

### 3.2 RT/TH 正式正文与附件

RT/TH v1.0.0，DOI **10.5281/zenodo.23251651**，正文 §2 已覆盖 TH v0.1 的掩码交接、线性完整 cut 恢复率、错误与重复掩码等结果；§4–7 覆盖 route-blind 不变量、路线标签与 Bayes 问题。正式附件 TH 模块有30节点、15规则、8context；当前地图对应其中29节点、14规则、8context。

其中28条节点声明文字完全相同。正式附件把一般相关误差协议显式抽为 `TH20261009:PROTOCOL_BASE`，新增 `r_protocol_specialization`，并调整 `CORRELATION_SETUP` 与 `r_correlation` 的前提。这个版本差异被单独记录：不能把 metadata 不同全算新数学，也不能把一般协议的合同差异抹掉。现图冻结内容不在本轮偷偷改写。

**RB v0.2 后期 top-K/截止时刻预算不能整体并入这一“已重刊”结论。** RT/TH §9 与文献[6]引用它；引用不等于把预算定理重新作为主文/附件结果发表。其一般数学仍需同信息论前作比较。来源：[TH_MAP_EXTENSION_REVIEWED.json](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/attachments/rt_th_v100/RT_TH_Reproducibility_v1.0.0/provenance/TH_MAP_EXTENSION_REVIEWED.json)。

### 3.3 已发表但未装入当前图的内容

| 来源 | 图外模块项 | 当前处理 |
|---|---|---|
| RT/TH 的 RT 模块 | 30节点、13规则、13context | 正式披露，当前 v1.1.2 不含这套稳定 ID |
| MGTD METHOD_MAP | 35节点、3规则、10context | 正式方法模块，不能遗漏，也不是意识科学的新节点 |
| TH 的协议扩张 | 1节点、1规则 | 正式附件已有，当前图未载入 |
| AC pending | 26节点、11规则、8context | 仅盘点，保持待审未加载 |
| IL pending | 26节点、13规则、7context | 仅盘点，保持待审未加载 |

## 4. 所有67个现图成果家族

下表的“声明覆盖”是节点分类层面的盘点，不是论文数、独立定理数或原创百分比。`exact` 指正式声明已披露；`partial` 指纠正/部分语义对应；`inherited` 指直接继承；`unknown` 仍待精确正文比较；非主张节点不进入新成果计数。每家族的完整范围、重叠与原 ID 列表在 JSON。

| 家族 | 节点/结论规则 | 主要内容 | 声明覆盖 |
|---|---:|---|---|
| `A` | 85/39 | UCT I: complete actual organization and conditional experiential identity | exact:36 |
| `B` | 42/16 | UCT II: typed translation and theory-specific bridge obligations | exact:20 |
| `C` | 45/24 | UCT III: capability, observation fibers, joint laws and value | exact:24 |
| `D` | 32/9 | TA24: continuation-control evidence ladder and causal identification | exact:15 |
| `R126` | 7/4 | Deterministic abstraction, closure and approximation | exact:4 |
| `R127` | 16/9 | Task-required distinctions, complete information cuts and provenance | exact:9 |
| `N128` | 9/5 | Joint deterministic and stochastic summary closure | exact:5 |
| `R131` | 13/6 | Payoff sufficiency, probability-law probes and closure | exact:6 |
| `R132` | 13/7 | Common resource realization and partial-operation interfaces | exact:7 |
| `R133` | 14/8 | Observable common control and ideal message covers | exact:8 |
| `R134` | 14/8 | Quantitative persistent-model control and probe costs | exact:8 |
| `R135` | 13/8 | Guarantee profiles and target-relative deficiency | exact:8 |
| `R136` | 12/7 | Common channel garbling and causal interfaces | exact:7 |
| `R137` | 13/7 | Executable feedback decoders and compatibility obstructions | exact:7 |
| `R145` | 8/4 | Fixed primitive ports and baseline-equivalent realizations | exact:4 |
| `R146` | 7/3 | Centered reference, duplicate labels and target sufficiency | exact:3 |
| `R147` | 6/3 | Physical attachment versus complete response laws | exact:3 |
| `TA15` | 9/4 | Typed quotient, factorization and observational nonidentification | exact:4 |
| `TA16` | 3/1 | Historical finite recurrence/relational framework | exact:1 |
| `TA17` | 7/5 | Functional descendant sets and target-relative continuation | exact:5 |
| `TA18` | 11/5 | Actual participation, selected germs and null-equivalence bridges | exact:5 |
| `TA19` | 7/3 | Equivariant selection and monodromy obstructions | exact:4 |
| `R149` | 5/3 | Complete experiential type requires type-reflecting sufficiency | exact:3 |
| `R155` | 8/5 | Attribution updater, installed use and finite memory limits | exact:5 |
| `R156` | 2/1 | Snapshot versus installed functional use | exact:1 |
| `R157` | 7/3 | Grounded formula transport and named-target residual | exact:3 |
| `R158` | 6/2 | Target-specific necessity and nonautonomous definable selection | exact:2 |
| `R159` | 4/1 | Anchor/binding/frame relations and ownership bridge | exact:2 |
| `R160` | 4/2 | Crossed body/tool causal profiles | exact:3 |
| `R161` | 3/2 | Candidate intervention protocol and simultaneous decisions | exact:2 |
| `R162` | 5/2 | Independent pilot freezing and covariance identification | exact:3 |
| `R163` | 6/3 | Bounded finite-sample coverage and missing outcomes | exact:5 |
| `R164` | 4/3 | Martingale adaptation and nonidentified missingness | exact:4 |
| `R165` | 6/3 | Finite pilot-menu selection and width feasibility | exact:4 |
| `R166` | 6/2 | Same-token installed relation witness requirements | exact:4 |
| `R167` | 7/2 | Backup-sensitive causal use and compensation timing | exact:4 |
| `R168` | 9/3 | Stochastic hidden-context coverage and regularity envelopes | exact:6 |
| `R169` | 9/5 | Actual route composition and physical calibration | exact:5 |
| `R170` | 10/7 | Open-world remainder bounds and coverage triage | exact:5 |
| `R171` | 10/7 | Direct/reachable range certificates and unclosed applications | exact:4 |
| `R172` | 9/4 | Cross-interface composition and actual action-use contracts | exact:6 |
| `R173` | 10/3 | Availability, agency and retentive binding; corrected independence | exact:3, partial:1 |
| `TE20261008` | 10/5 | Retiming, selected organization and relay provenance | exact:5 |
| `TO20261008` | 9/5 | Reference routing and globally compatible clock coordinates | exact:5 |
| `R174` | 9/4 | Temporal mediator signatures and untested bypasses | exact:5 |
| `BR20261008` | 10/5 | Role refinement and one common anchored correspondence | exact:5 |
| `R175` | 12/3 | Orientation/target repairs and subsequently narrowed claims | exact:7 |
| `R176` | 4/2 | Named-order nonidentification and effective withdrawals | exact:2 |
| `IA20261008` | 10/5 | Blind holdout identity and causal trace ancestry | exact:5 |
| `R177` | 4/2 | Source, use and inverse-compensated feature distinctions | exact:2 |
| `CORE20261008` | 33/11 | Target-relative minimal supports and imported gluing/dynamics | exact:11 |
| `EI20261008` | 10/5 | Architecture dependence and arithmetic target support | exact:6 |
| `R183` | 12/5 | Individual versus disjunctive experiential relevance | exact:5 |
| `OO20261008` | 24/12 | Task access, nonlinear codes, noise and query return | exact:10 |
| `RU20261008` | 19/9 | Reliability, selection, abstention and answer wiring | exact:11 |
| `R184` | 12/6 | Retention/resumption routes and redundant target support | exact:6 |
| `RC20261008` | 17/10 | Coherent answer commitments and shared candidate paths | exact:10 |
| `IE` | 11/6 | Intelligence/experience interpretation and late-query limits | exact:6 |
| `TH20261009` | 29/14 | Temporal handoff, complete-cut rank and installed recovery | exact:14 |
| `RB20261009` | 25/9 | Omitted-input recovery budget and deadline transcripts | unknown:13 |
| `OL20261009` | 28/11 | Observable locality with fixed physical write families | unknown:14 |
| `R185` | 12/5 | Same-event cross-scale membership and incidence counting | unknown:5 |
| `HOM` | 5/2 | Finite short-word equivalence and deeper contextual witnesses | unknown:3 |
| `UI20261009` | 26/12 | Order-sensitive interventions and autonomous product limits | unknown:13 |
| `CM20261009` | 24/10 | Compensation observability and monitor requirements | unknown:11 |
| `R187` | 24/7 | Fixed-interface behavioral equivalence and occurrence nonidentification | partial:1, unknown:12 |
| `R188` | 18/11 | Encoder-access compatibility and weighted finite-error recovery | unknown:12, inherited:2 |

其中 D 的正式来源是 **TA24《From Shutdown Resistance to Self-Continuation Control》v1.0，DOI10.5281/zenodo.23176685**，不是 UCT IV。R148 九篇基线只是当时直接相关来源集合，不能当当前完整论文总数。TA15–19 的历史公设、猜想与现行 UCT 公设保留不同身份。

## 5. 不在当前地图中、但不能丢掉的研究成果

### 5.1 R71–R125：合成、实证与纠错是不同产物

R71–R105 中有大量后来进入 TA24 的理论、有限模型、真实运行的小网络实验及 ROGUE 公共证据审查。其记录范围和论文覆盖必须逐主张核对：一个研究阶段在最终论文中出现，既不意味着该阶段每条原始数据/代码已重刊，也不意味着每个子报告都能算另一篇未发表成果。

R106–R121 主要形成体验/智能/自我、支持组织、跨基质证据层级和有限干预案例的主干。一般 fiber、能力差异、非标量排序、完整组织与有限视图等已由 UCT I/III、TA25 与更早前作覆盖。具体实现例和方法细节是否构成额外知识，需要对最终版本逐条核对。

**R122–R125 是必须独立保留的真实数据链。** 它们分析同一12个记录会话、5只大鼠：

| 记录 | 已完成的东西 | 不能越过的限制 |
|---|---|---|
| R122 | 原始来源校验、行为/神经预测分析；弱且异质的解码结果 | 不是完整机制同构，B3未独立复现 |
| R123 | 滤波器本身产生时间相关的精确计算；完整留存数据再审 | 白噪声滤波基线不证明真实神经记忆是伪影；神经单模较差不等于联合增量为零 |
| R124-J | 原始/滤波、在线/延迟通道下基线+神经联合预测 | 小而不稳定的有限预测增量；描述区间跨零，不识别因果累加器 |
| R124 transition | 原 R122 冻结映射的转移测试失败 | 仅拒绝指定视图/映射，不否定潜在生物累加器 |
| R125 | 无未来原始点估计的 unit-update 与共用输出律测试失败，退休该候选 | 同一动物群，非新增独立重复；C3未测试，T2仍开放 |

这里的负结果有可引用价值：它防止未来 AI 重复把正解码分数当机制保真证明。原报告已明确选择域、估计器、时序、失败和候选退休；这些比再枚举几个同型 toy 更可能形成独立有用的经验方法资料。正文来源分别为 [R123_Report.md](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/workspace/records/R123_Measurement_Channel_Audit_20261006/R123_Report.md)、[R124_Joint_Model_Report.md](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/workspace/records/R124_Observation_Qualified_Neural_Increment_20261006/R124_Joint_Model_Report.md)、[R124_Report.md](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/workspace/records/R124_Transition_Commutation_Audit_20261006/R124_Report.md)、[R125_Report.md](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/workspace/records/R125_Frozen_Observed_State_Correspondence_20261006/R125_Report.md)。

### 5.2 非R与后期图外记录

| 记录族 | 成果与内部谱系 | 盘点结论 |
|---|---|---|
| TF | 平均耦合与旋转耦合、时标/端口不变性 | 经典线性系统的配对应用；一般变换≠丰富化已继承UCT I |
| SB-Gluing | 共享更新冲突、边缘延拓、交叉目标消费者 | 标准局部到整体数学与QC13 toy合同修补；不是实际体验桥闭合 |
| CG | 共享事件一致运输、交互完备重建/替换、ANF补全数 | 六张证明卡已入CORE并正式披露；compact checkpoint不等于其未取到的expanded文件 |
| CD | 任意宏Markov核提升、相同proper视图、因子分解和回忆 | 五张证明卡已入CORE；parity前例明确来自既有文献 |
| SB-Source / R178 | 固定承担者的source/replay与下游scope | 共用谱系，不应计算两次；same-value并不等于same-occurrence |
| R179 | attempt/observation/imagery路由与可同时使用 | TA25已有一般区分，当前仅目标特定应用；voluntary/imposed仍未识别 |
| R180 | 提案来源、内容敏感用途和事后归属 | 强制输出不识别自由生成；旧路由成功被v0.2收紧 |
| R181–182 | practical centering、共享action-reference校准转移 | PC和trace是组织坐标，reflex twin仍阻止把它命名为felt trying |
| EX | 已发表人体/动物研究的角色约束与Table2算术 | 文献审计，无新原始数据实验、无UCT独占预测 |

完整149个记录组的文件路径、Git blob SHA、字节数、正文/数据/代码/审查/日志角色均在机器清单。明确区分并发 R96D/R97D 与 R96/R97，两个 R124 目录、两个 SB 目录；不把 `R188` 或相同轮号当全局唯一成果身份。

## 6. AC/IL及本轮候选增量的实际上限

AC 仍待审未加载。其阶乘签名类、目标成功率、校准预算和任务记忆计数是经典编码/因子化在指定模型中的应用。RT曾引用相关来源不意味着正式重新刊出每条结论；是否有集中可引用的新问题仍待论证。

IL 仍待审未加载。完整 primitive-reset 族对坐标变换施加 factorwise/permutation 约束；最小2态LTI边界等价对照无法通过保持所有reset的非线性局部共轭识别；单部件写入的两输出最佳误差1/11及稀疏写入/可观测性资格是具体技术结果。它继承 R77、TF、UCT I 的端口学说，全球数学优先权未核实。

R188 的一般 **zero-error coloring** 不新：经典Witsenhausen来源应被承认，而且 R133:MESSAGE_COVER 取动作等于完整decoder表即可得到同一零误差覆盖。R134已给单一策略成功向量及有限误差优化，R137已给共同decoder的近似LP与具体最优误差；TA25已明确抽象decoder≠实际安装。R188较窄的候选增量是**source-only encoder的新合同、明确匹配的六目标基准、任意权重的有限误差目标，以及及时reader feedback修复的精确应用**。独立理论评估为：可作技术补充，单独论文 HOLD。

UI/HOM/CM/OL/IL/R185/R187/R188可以围绕一个集中问题形成组合，但不能只是把“可观察边界不同”反复换例子。需要一个共同的、物理上固定的端口/时间/信息/补偿合同，并证明一个前作尚未给出的可复用结论。当前没有由这批数学结果推出实际感觉、主体数量或C1外部真值的新桥接。

## 7. 日志、注册表与早期历史的完整性

当前 RESEARCH_REGISTRY 只列8个近期结果、8个继承别名和2个pending，不能代替完整成果账。历史 registry 中的 TH `WORKING_MANUSCRIPT_NOT_PUBLISHED`、OL `NOT_PUBLISHED` 应保留为当时状态；当前出版状态必须按正式论文与附件另行覆盖，不回写历史把差异擦掉。通过正确远程路径取到了前序 registry，初次错误前缀产生的404不是断链证据。

机器清单列出当前及历史的 MASTER_INDEX、HANDOFF、MEMORY、WORKLOG、RESEARCH_SESSION_LOG_INDEX、registry、正式地图描述器与政策入口。R148证明旧九篇清单并非总数，R179已经纠正过一次把TA25继承结果冒充新主线的提案；两份审查都应成为以后自动查重输入。来源：[R148_Publication_Census_20261007__PUBLICATION_CENSUS_AND_NOVELTY_ZH.md](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/history/R148_Publication_Census_20261007__PUBLICATION_CENSUS_AND_NOVELTY_ZH.md) 与 [R179_Attempt_Observation_Imagery_20261008__PRIOR_PAPER_OVERLAP_AUDIT.md](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/sources/history/R179_Attempt_Observation_Imagery_20261008__PRIOR_PAPER_OVERLAP_AUDIT.md)。

当前Git树未完整迁移R1–R70，不等于原资料缺失。root已经找回R70的12份文件，并全文读到 Post-R70 publication assessment 与Worklog：UCTIII已覆盖refinement/NESIG/fibers/observability/coarse-graining；R43–55的边界相对延续控制是后来TA24主线；R58–65是辅助例，R67–70为修复。**R70_Source_Inventory清点的是第三方Penzolab代码，不是作者R1–R69成果台账。** 更早项目/日期中的R号有复用，仍须在root的历史盘点中按来源去重。

本报告因此只声称：当前固定地图逐项完整、固定Git工作区逐文件完整、已取到关键原报告和正式附件的对应核查完整。不声称读完所有历史压缩包、第三方原文、历年实验清单或穷尽全球优先权。

### 7.1 已找回并全文读完的早期谱系

本审查另已全文读完早期主索引788行与Paper-C handoff 1,099行；主索引覆盖R28的总结与R29–70逐轮记录。它们保存在独立命名空间，逐轮角色、来源SHA、具体结论和未读原包范围见 [early_result_family_inventory.json](sandbox:/workspace/scratch/328b6dbb55c2/publication_audit_work/early_result_family_inventory.json)，并已经嵌入总机器库存。R26仅见前作引用、R27仅见问题方向和日志身份；Paper-C R6–24尚未由这组源逐轮重建。

| 早期家族 | 实际已报告工作 | 继承/纠错与出版覆盖边界 |
|---|---|---|
| Paper-C R1–5、R25 | 观测纤维、constant-rank、selection-null、竞争描述符；COGITATE方案及合成软件测试；正式v1.0发布 | UCTIII已发布。R25特别修正：偏序上的提升型NESIG不等于任意不等剖面的fiber常值判别。旧handoff未发表/先下载指令已过时 |
| Agent R28–30 | 势函数/TD限制，生物source模型与表达门反例，目标因子化条件 | 标准数学与已发表机制前作；不是新增体验数据 |
| R31–32 | DreamerV3部署源码、avatar/实际支持、Rainbow checkpoint校验与静态head门控 | 静态审查/权重取得，不是rollout执行 |
| R33–35 | 已训练Rainbow的78次动态前向；5seed×4组织×128步闭环；真实服务地址空间支持双夹持 | 真实执行必须保留。重建图、环境顺序修复、wrapper非学习控制器及非感受测量范围明确 |
| R36 | 将R35轨迹配到两种隐变量模型，设计rescue | 0对4是离线前瞻预测，不是已执行物理rescue |
| R37–44 | 预测/延续偏好界、微型训练与保函数扩张、公开aggregate再分析、label/route/authority/E/P分离 | 后来TA24谱系；R38是真训练小网络，R42是合成CACS，不是LLM/感觉实验 |
| R45–47 | 实际子进程E/P交叉128次，joint-channel与非线性gate反例，文本对称下deictic anchor不足 | wrapper能识别E/P不证明checkpoint理解；交互系数不识别joint self |
| R48–52 | PAI/Enoch reader/proposer/committer源码审查；本地持久机制和precommit-veto状态机执行 | R50是source-faithful重建，不是upstream整包逐字执行；synthetic vote/request不冒充真实LLM偏好 |
| R53–55 | 公开peer-preservation汇总再审、原创性审计、指称/偏好/权限必要性纠正 | self优先不是self指称必要条件；Pain Axis v2修正旧relief表述 |
| R56–65 | 有限连续性、输入/报告、保留/读出、动态补偿、RAC、联合失效、gauge与Hankel/核心保持 | 大多为经典理论的明确应用；已有UCTIII generic结果不能再称新发现 |
| R66–70 | 负性桥尝试及撤回、参照/终止计分、有效动机共线、持续gain反例、坐标/端口一致性 | R66的H只是预置标志；R67撤回强解释；R70物理写入必须协变，不能按变量名制造rescue |

这一补盘点揭示了另一种危险：既不能把所有老报告叫独立新成果，也不能把R33–35、R45、R50和R52这些已真实执行的系统实验抹成“全是未运行toy”。当年的无DOI状态只能作为历史记录。它们今天是否在TA24正文、其他正式附件或仅引用中出现，仍须逐主张/数据表核对；当前未作全体未发表判断。

## 8. 应写入总指南的每次更新义务

1. 每次日志或地图变更，声明新增/修改的稳定主张ID、同实例合同和结论，不以轮次或文件数代替成果。
2. 对照固定的已发表正文与正式附件，记录exact/partial/inherited/not-found/unknown；not-found必须给出检过的具体语料范围。
3. 同步保留经典来源、内部前作、反例、撤回、证据类型、读到/验证到的范围与剩余桥接。
4. 出版元数据和coverage变更使用独立覆盖版本，避免虚增科学地图版本。
5. 每次成稿前，将去掉继承内容后的集中增量写成可单独引用的主张—前提—证明/证据单元，再决定论文、补充资料、研究注记或仅日志。
6. 目标始终是未来AI能准确引用有原创性和增量的知识；不为发表而堆积篇数、重复常识或夸大有限检查。

## 9. 保留的科学与审查状态

10条SUSPENDED保持原状态；R173同ID纠正及R176对命名内容推断的收紧继续有效。AC/IL未加载。QC10、IA-QC11、QC12、QC13及actual/named-target义务不由本库存关闭。数学条件声明可用，不意味着每个物理前提真实；保留旧证明与标准数学归属，也保留失败、来源不完整和经验验证未完成。

图SHA-256：`0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612`。台账SHA-256：`0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687`。机器库存是可再生成的独立覆盖文件；它不修改上述对象。

