# R106 工作记录与交接 — 体验/访问/智能/自我/行为/报告第一性原理地图

日期：2026-10-06。

用户确认新方向：从根本上研究生物与AI的体验、智能、行为、报告、自我的关系，不以benchmark或投稿为驱动。

本轮从R81/R82及已审核A/B/C出发，得到六轴最小区分：
E=体验，A=访问，I=智能/能力，S=自我模型，B=行为，R=报告。

最关键纠正：UCT里不应画成“体验->智能->行为”。完整实际组织K在C1下与完整体验类型E构成结构—体验身份；I/B/R是K在任务/环境/接口上的投影，A/S是K的关系/子结构。保持完整K不变而单独删除E不是UCT允许的反事实。

核心Projection Lemma：对固定条件下任何K上的良定义投影F，
E同型 => K同型 => F相同，所以F不同可推出完整体验类型不同；但F相同只有在F对现实域单射时才能推出E相同。因此同智能、同行为、同报告一般都不足以推出同体验。Paper C/R81的NESIG是I这一特例。

无条件“智能越高体验越丰富”仍不能推出。精确16类型toy witness（E=K）枚举120对：same-I/different-E 56对，same-B/different-E 56对，same-R/different-E 56对，different-I/same-E 0对，智能上升而候选richness下降16对，report-only change且selected core不变8对。toy仅验证逻辑，不是意识数据。

新增时间尺度纠正：E是episode/token结构呈现，I通常是跨任务的能力律，B/R是轨迹/样本；“意识和智能是否同步”在未对齐时间窗、边界、任务和度量前不是良定义问题。

跨底物结论：生物与AI同能力/同行为/同报告都只是低层等价；UCT下要推出完整体验类型相同，需要共同完整签名下的完整组织同型。若只比较某个体验子结构，则需物理上有根据的组织投影并满足R65式commuting preservation。

生物压力测试没有推翻该图：
- NEJM 2024 CMD：无床旁指令反应者中60/241（25%）有fMRI/EEG指令执行，说明外部行为弱不能推出内部认知访问弱；
- no-report/covert-measure文献要求区分体验相关处理和报告；
- blindsight更适合作为objective performance/metacognition/subjective content的复杂解离，不宜当“智能无体验”的二元证明；
- split-brain提醒agency unity与experience unity不是同一问题；
- COGITATE 2025同时挑战IIT/GNWT若干关键预测，故不把broadcast/integration等设为UCT体验存在门槛。

下一步R107：建立最弱跨底物common signature。候选比较关系：输入/证据、记忆/时间状态、预测/世界模型、自我/边界关系、价值/稳态、policy/action、report、物理ports/interventions。注意：这些是比较坐标，不是体验存在门槛，简单过程允许坐标缺失。

之后R108才做小型AI“解离手术”实验：同能力/同行为不同内部组织；同核心能力不同report；改变self-model而匹配非self任务；改变access而保留sensory encoding。不要先上大模型自报告。

主要文件：
- records/R106_Experience_Access_Intelligence_Self_Behavior_Report_First_Principles_Map_20261006.md
- records/R106_EAISBR_Formal_Map.json
- records/r106_projection_relations_check.py
- records/R106_Projection_Relations_Results.json
- records/R106_Source_Retrieval_Ledger.json
