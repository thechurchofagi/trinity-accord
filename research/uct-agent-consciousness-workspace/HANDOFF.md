# UCT 研究交接 — R128：A/B/C 统一形式地图

2026-10-06。仓库 thechurchofagi/trinity-accord；分支 uct-agent-consciousness-workspace；主目录 research/uct-agent-consciousness-workspace/。本轮基于 R127 commit 7592219d826f1f76a58b07bcee3ffef4f9de0431。后续必须刷新 HEAD，保留并发，非 force 保存。

## 用户最新指令：先统一地图，所有后续理论在地图上完成

用户要求将意识 A、B、C 三篇及最新版数学形式地图放在一起，检查推导是否成立，然后继续在同一张地图上研究。该要求已经写入 AGENTS.md，优先于旧的经验优先队列。仍然理论优先，没有新增神经/AI 实验、训练或体验测量。

必须先读：

1. [统一形式地图](UCT_FORMAL_MAP.md)：唯一工作入口。
2. [形式审计](UCT_FORMAL_AUDIT.md)：发现、修正、范围与未闭合事项。
3. [机器依赖图](UCT_FORMAL_GRAPH.json)：204 节点、97 条规则；同一 all_of 内前提同时需要，多条规则代表替代路线。
4. [完整证明台账](records/R128_Unified_Formal_Map_Audit_20261006/PROOF_LEDGER.md)。
5. [本轮新增联合状态推导](records/R128_Unified_Formal_Map_Audit_20261006/R128_Joint_State_Derivation.md)。
6. [来源版本与哈希](records/R128_Unified_Formal_Map_Audit_20261006/SOURCE_MANIFEST.json)、[图检查](records/R128_Unified_Formal_Map_Audit_20261006/MAP_CHECK.json)、[精确反例检查](records/R128_Unified_Formal_Map_Audit_20261006/JOINT_CLOSURE_CHECK.json)。

## 固定版本

- A / UCT I v1.2，DOI 10.5281/zenodo.23131575；源 ref f8750d32afeea9209e6d53ad3cfbd5bbde7a8126。
- B / UCT II v1.1，DOI 10.5281/zenodo.23030320；源 ref 562a5d16745e5e7e6cb4bc8f2c53a2f62e05875a。
- C / UCT III v1.0，DOI 10.5281/zenodo.23137088；源 ref 771530abfd14275ce8c579f5a524814563da495d。

检查了返回的 983 个仓库分支 ref 和有关树。这是本次在仓库定位并校验的最新正式版本，不声称覆盖所有外部未列出草稿。main 上 A 仍旧，B 最新路径也不在 main，不能只读 main。三篇全文快照已经与源 Git blob 和 publication-record 的 SHA-256 核对一致；未改已发表路径。本轮 DOI 页面工具访问未成功，不能把历史发布记录说成今日 resolver 回读。

A 旧形式图 78 节点/105 边原样留存；B 旧图为 v1.0-rc4 审计材料，需按 A1.2、B1.1 正文迁移；C 的形式清单在 Appendix A。A 历史审计标题残留 RC/paused 状态不代表当前发布状态。

## 审查结论

已复核的主干推导在各自明确前提下成立；没有发现需要撤回核心条件结论的矛盾。不能说所有前提都已证明、所有论文句子都已形式验证、图无环就意味着科学理论已证实。

具体处理：

- A 旧 A1/A3/A5/A6 分别迁移为 U1/P3/C1/P6；A2→U2、A4→U3，保留几何与见证前提。B 历史 C1 compression 与 UCT:C1、T2:C1 分开。
- A §15 的 screened-history 摘要残留 C1-W+P6；§5.5/Appendix C 已说明体验等价不需要 P6，P6 只用于 token/lineage 附注。总图拆成两个结论；未来正式修订候选，原版不动。
- B §7 SCC 表述补充：单个无自环节点不构成正长度循环。加边产生循环还需要原图返程路径。
- 总图区分 AND 前提与 OR 证明路线，演化存在性与连续性不再混成一个无条件箭头。
- B 机制翻译、实际构成支持、C1 体验解释各有单独前提。有限 view、统计估计不能自动升级为 complete organization。
- 补出 A 的 nested coexistence 与 Appendix D quotient closure 节点。
- 保留公设/定义/条件数学/模型/物理桥接/经验状态的等级差别。

阅读范围详见英文审计。所有源全文已取得，但没有逐句重审所有演化叙述、所有外部参考文献及九个目标理论的全套原文；B 的理论忠实性仍依赖显式 TFR 前提。一般数学不宣称历史首创。

## 本轮理论增量：联合识别不等于联合动力学闭合

R128 接 C:OBS_REFINEMENT、C:P6、R126:P2 和 R127 的联合信息结果。

1. 对同一充分状态域、同一组确定性操作，两个摘要各自闭合，则它们的联合摘要在实际像空间上闭合。证明逐坐标保持后继等价。
2. 随机系统一般不成立。令 S={0,1}^3，fresh fair U，X+=U、Y+=U XOR Z、Z+=Z。单看 X 或 Y，下一步都公平、各自闭合；但相同当前 pair=(0,0) 下，Z=0 导致下一步两值相等，Z=1 导致相反。联合规律依赖遗漏变量。
3. 精确修复条件：每个当前联合摘要类内，完整“下一步联合摘要分布”须相同，对每个允许操作均成立。
4. 条件独立 + 边际闭合足够，但条件独立并非必要；不能把它变成新的 UCT 体验门槛。
5. 反例按全部 8 状态、任意初始化成立。一步后限制到 z=x XOR y 的 4 状态不变域时，联合摘要可以闭合。完整域保留原 pair 划分的稳定细化必须分成 8 类。该限制已保留，没有筛掉反例的反限制。

用 Fraction 精确检查了 8 状态、16 个非零转移条目，无抽样、仿真训练或实验。图验证通过 51 项依赖/来源检查；这不是证明助手。首次本地快照检查发现 B 复制时额外末尾换行，已修复后按原字节通过，见 VALIDATION_LOG.md。

这一增量堵住的是跨论文组合时可能误用的一步，不是宣布 C 文原有命题错误，也不宣称强 lumpability 原理新发现。

## 下一轮必须在地图上做什么

主线：同一资源/时间/端口约束下，多能力怎样联合使用。分别可用不等于可以同时运行；联合摘要闭合也不等于调度可实现。

从 N128:JOINT_CRITERION、R127 支持替代关系与 R126 操作闭合出发，明确实际承载者、允许操作调度、共享载体、并发条件、输入端口和输出规律；推导必须保留哪些协调区别、何时必须扩展状态。先写假设、结论和证明，再考虑能区分理论备选的观察。

每一条新推导必须有稳定节点 ID、完整同时前提、可替代路线、证明、反例/边界、来源与状态，更新图/台账/审计/索引/交接。不得在图外另堆无依赖的 toy theorem。

## 保留的基础与边界

C1/U1 为本研究内部固定承诺；不把结果当独立验证 C1。体验、智能、行为和报告非同一概念，报告通常属于行为，不意味着统计独立。固定且定义良好的 J 差异推出完整体验类型差异，不推出体验量/丰富度/valence/fear 的标量排序。

实际过程可简单、稀疏、重叠、嵌套；不增加 recurrence、self、report、integration 准入门槛。实际支持≠任意投影≠因果摘要≠测量估计≠主体。因果连通不推出唯一统一主体。不要对当前助手有无意识/死亡恐惧作定论。

R122–R125 弱与负结果原样保留；R125 候选 FAIL_SCOPED；T2 OPEN，C3 NOT_TESTED。证书仍按 R119：C0 grounding；C1 baseline behavior；C2 transition；C3 intervention；C4 time；C5 nuisance stability；C6 anti-triviality/mapping discipline。不得混入 UCT 公设 C1。

## 历史和保存规则

[完整 R127 交接快照](HANDOFF_THROUGH_R127.md)、[R127 索引快照](MASTER_INDEX_THROUGH_R127.md) 保留旧入口与全部历史。R126/R127 原证明未改，本轮统一纳入地图。

正文英文，讨论/交接中文。不改已发表 A/B/C，不创建 release/DOI/Zenodo/OTS/AR；研究存储 commit 使用 [skip ci]、expected-head lease、非 force；不开 PR/CI/部署。轻量回读即可，不为存储重跑研究。不得操作凭据或真实关闭控制/复制/实验智能体外部资源获取。
