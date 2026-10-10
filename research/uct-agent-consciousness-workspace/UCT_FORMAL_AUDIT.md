# UCT 地图审查状态

[总览](UCT_FORMAL_MAP.md) · [全部候选](PENDING_RESEARCH.md) · [当前状态](CURRENT_STATE.json) · [统一登记](UNIFIED_RESEARCH_INDEX.json) · [审查](UCT_FORMAL_AUDIT.md)

| 范围 | 当前结论 |
|---|---|
| 正式科学图 v1.1.2 | 保留原 1,608 项合同兼容性审查与组装验证；原哈希不变 |
| 本轮导航整合 | 38 个检查点集合、源文件哈希、已有修正、引用解析、历史归档及入口同步 |
| 待整合科学内容 | 全部停用；不视为已成立的总图前提 |
| 全历史独立语义与证明审查 | AUDIT_INCOMPLETE；本轮未逐一重证 |
| 实际应用与指定体验桥接 | OPEN |

[本轮精确验证](integration/UCT-INTEGRATION-v1.0.0/VALIDATION.json) · [引用缺口](integration/UCT-INTEGRATION-v1.0.0/REFERENCE_RESOLUTION.json) · [原审计](integration/UCT-INTEGRATION-v1.0.0/history/UCT_FORMAL_AUDIT.md) · [监督账](REVIEW_SUPERVISION.md)

保留 QC-20261008-10、IA-QC11、QC-20261008-12、QC-20261008-13、SCU-OPEN-R191-NORMALIZATION 与 SCU-AUDIT-DEPTH，及各候选的其他 OPEN。结构遍历不等于语义证明，候选登记不等于实际前提成立。

TJR基础问题复核：[审查](records/TJR20261010_Temporal_Joint_Realization/AUDIT_REPORT.md)，1608项仅结构遍历、13节点有限兼容性核对；全历史深审AUDIT_INCOMPLETE，0新增正式节点/规则/关系。

A3X端点内容复核：[审查](records/A3X20261010_Action_Familiarity_Content_Admissibility/MAP_AUDIT.md) · [逐ID结构记录](records/A3X20261010_Action_Familiarity_Content_Admissibility/PER_ID_AUDIT.json.gz)。913/424/261逐项结构遍历通过；相关R157/R173 `all_of`、对象/时间/签名/实际性/证据层级人工复查。`S_H`不推出`C_H`或`O_H`；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A3Y测量对象身份复核：[审查](records/A3Y20261010_Measurand_Identity_Barrier/MAP_AUDIT.md) · [逐ID结构记录](records/A3Y20261010_Measurand_Identity_Barrier/PER_ID_AUDIT.json.gz) · [精确反例](records/A3Y20261010_Measurand_Identity_Barrier/EXACT_RESULTS.json)。913/424/261逐项结构遍历通过；所有`all_of`按AND处理。潜类`Z`与`H_way`之间的身份/方向不由观测律推出；C1/R157/R173条件结构结论与外部命名、测量、实际应用保持分离。全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A3Z现象锚点复核：[审查](records/A3Z20261010_Phenomenal_Anchor_Triage/MAP_AUDIT.md) · [逐ID结构记录](records/A3Z20261010_Phenomenal_Anchor_Triage/PER_ID_AUDIT.json.gz) · [精确结果](records/A3Z20261010_Phenomenal_Anchor_Triage/EXACT_RESULTS.json)。913/424/261逐项结构遍历通过；所有`all_of`按AND处理。候选桥接的预注册失败可在全部应用前提成立时否决它，但全部通过仍允许非现象代理模型；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A4A形成干预复核：[审查](records/A4A20261011_Formation_Intervention/MAP_AUDIT.md) · [逐ID结构记录](records/A4A20261011_Formation_Intervention/PER_ID_AUDIT.json.gz) · [精确结果](records/A4A20261011_Formation_Intervention/EXACT_RESULTS.json)。913/424/261逐项结构遍历通过；有效R175替代边界规则与R173合取路线按AND复核。形成后匹配可制造残差或阻断目标路径；五项受控直接效应未共同安装，全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

REV基础问题复核：[审查](records/REV20261010_Retained_Premise_Revision/AUDIT_REPORT.md)，1608项仅结构遍历、18节点有限兼容性核对；全历史深审 AUDIT_INCOMPLETE，0新增正式节点/规则/关系。

A4C同承载者痕迹换接复核：[审查](records/A4C20261011_Trace_Swap_Embodied_Loop/FORMAL_AUDIT.md) · [精确结果](records/A4C20261011_Trace_Swap_Embodied_Loop/EXACT_RESULTS.json)。历史根图584/284/178已读，统一图恢复为913/424/261并保持727个待定对象停用；相关C1/U1/R157/R172/R173节点、`all_of`方向、对象/时间/签名/实际性和证据层级复核。执行成功仅及声明的具身模拟，不能触发R173体验坐标路线；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A4D执行器写入器完备性复核：[审查](records/A4D20261011_Actuator_Writer_Completeness/FORMAL_AUDIT.md) · [逐ID结构记录](records/A4D20261011_Actuator_Writer_Completeness/PER_ID_AUDIT.json.gz) · [精确结果](records/A4D20261011_Actuator_Writer_Completeness/EXACT_RESULTS.json)。913/424/261逐项遍历，所有`all_of`按AND；保留81条本地AND注记缺失与22条非演绎语境端点格式差异为历史债。A4D证据不替代实际路线、完整K或现象语义，R173路线未触发；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A4E当前写入事件复核：[审查](records/A4E20261011_Actuation_Event_vs_Held_State/FORMAL_AUDIT.md) · [审计摘要](records/A4E20261011_Actuation_Event_vs_Held_State/AUDIT_SUMMARY.json) · [精确结果](records/A4E20261011_Actuation_Event_vs_Held_State/EXACT_RESULTS.json)。A4D全图验证器重跑并逐字节复现913/424/261结构结果；所有`all_of`按AND。最终电平、提交事件、选择写入者和实际路线使用保持分型，R173路线未触发；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A4F见证独立性复核：[审查](records/A4F20261011_Witness_Independence_and_Provenance/FORMAL_AUDIT.md) · [审计摘要](records/A4F20261011_Witness_Independence_and_Provenance/AUDIT_SUMMARY.json) · [精确结果](records/A4F20261011_Witness_Independence_and_Provenance/EXACT_RESULTS.json)。复用A4D/A4E字节稳定的913/424/261结构遍历并人工复核事件、来源标签、物理来源、见证控制根、实际路线与体验的分型；所有`all_of`按AND。五种重叠与一种条件分离均只及声明有限模型，R173路线未触发；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。

A4G共同控制切割复核：[审查](records/A4G20261011_Common_Control_Cuts/FORMAL_AUDIT.md) · [审计摘要](records/A4G20261011_Common_Control_Cuts/AUDIT_SUMMARY.json) · [精确结果](records/A4G20261011_Common_Control_Cuts/EXACT_RESULTS.json)。共同祖先、抑制/改时序/重放/伪造能力、同试次组合和完整向量重现保持分型；所有`all_of`按AND，R173路线未触发。A4F远端审查台账损坏已恢复并列入GAP；全历史深审仍AUDIT_INCOMPLETE，0正式图增量。
