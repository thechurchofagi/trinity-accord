# UCT 研究交接 — R129：补齐四篇论文的统一形式地图

2026-10-06。仓库 thechurchofagi/trinity-accord；分支 uct-agent-consciousness-workspace。本轮基于 R128 commit c9116c7b107fbf86f53f729e75eb50b530649e6e。后续刷新 HEAD、保留并发、expected-head lease 非 force 保存。

用户纠正总计四篇，并要求最近发表的一篇及其形式化也进入地图。已定位并纳入 **TA-TR-2026-24 v1.0**，*From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents*。2026-10-06 发布，DOI 10.5281/zenodo.23176685。这里用 D 作地图命名空间，不擅自改成正式题名 UCT IV。

## 必须读取的当前入口

- [四篇统一地图](UCT_FORMAL_MAP.md)
- [机器依赖图](UCT_FORMAL_GRAPH.json)：236 节点、106 条规则；同条 all_of 是同时前提，多条同结论规则是替代证明路线。
- [形式审计](UCT_FORMAL_AUDIT.md)：保留 R128 发现，新增 F13–F19。
- [第四篇接入与证明审查](records/R129_Four_Paper_Integration_20261006/R129_Integration_and_Proof_Audit.md)
- [完整证明台账](records/R129_Four_Paper_Integration_20261006/PROOF_LEDGER.md)
- [四篇版本及新增来源哈希](records/R129_Four_Paper_Integration_20261006/SOURCE_MANIFEST.json)
- [图与来源检查](records/R129_Four_Paper_Integration_20261006/MAP_CHECK.json)、[精确数学检查](records/R129_Four_Paper_Integration_20261006/EXACT_MATH_CHECK.json)、[验证范围](records/R129_Four_Paper_Integration_20261006/VALIDATION_LOG.md)

## 固定版本

| 论文 | 版本 | DOI |
|---|---|---|
| A / UCT I | 1.2 | 10.5281/zenodo.23131575 |
| B / UCT II | 1.1 | 10.5281/zenodo.23030320 |
| C / UCT III | 1.0 | 10.5281/zenodo.23137088 |
| D / TA-TR-2026-24 | 1.0 | 10.5281/zenodo.23176685 |

D 源分支 research/self-continuation-control-v1-20261006，固定 ref ae1d8965ef99df9d8a725c540bd8c0a79f2c4e70。正文 36,208 bytes；SHA-256 af0eb63cca099b3d913218f503bc978c705f0fb9f065cca9ed472e5161d67490，与发布记录一致。公开回读/DOI 成功是发布记录的既有状态，不冒充本轮重新 resolver 检查，也不将旧 preservation_pending 字段当当前保存状态。

A/B/C 继续用 R128 精确源快照。本轮没有发现或引入 A1.3，不应把 D 新发表误当 A 版本更新。main 索引不足以确定最新版本；所有来源均 pin commit。

## 完成的接入

1. 原图 8 个定义、9 个主张全部保留为 D:D0–D7、F1–F3、E1–E4、A1、S1。合计新增 32 节点、9 条明确数学规则，不等于发现 32 个新定理。
2. 原图 18 条 allowed edges 保存为 context_links，不能把研究顺序当逻辑证明。F1 非识别不自动推出 F2；F2 需要同一五参数模型、独立干预对比和校准 logits。
3. 分开数学、已发表 synthetic/retrospective 证据和 L0–L9 方法标准；没有重新运行实验，也没有把证据条目当定理推出来。
4. 与 C:P2_COORD 接模型内识别，与 C:P7 接固定反例的 1/8 决策价值差；与 A:P6 接 bearer 的 token/type/lineage 区分；与 B 接有类型的 consequence interface。
5. 体验解释必须通过 A:C1-OI + 独立实际组织非同构前提，不能从 virtual Q、延续行为、控制系数、模型拟合直接推出 valence/fear。
6. 明确 finite grid→连续域界需要全局 Lipschitz 前提，path-additive 消除交互不等于已知响应形状。

## 必须纠正的增量归属

**D §4 / R96D 已经有“分别准确的 Q/O 边际预测不一定足以决定联合后果”的结论。不能把这个一般洞见重复报成 R128 新发现。**

R128 的较窄增量是同一确定性动力学下摘要组合闭合、随机系统下的具体不闭合反例，以及联合推前分布判据。D 是决策充分性，R128 是动力学充分性；相互有关但不能互相替代证明。

R129 的增量是遗漏论文补入、版本/形式材料统一、证明前提显式化、跨文依赖和归属修正。标准线性代数、Fréchet 界、Lipschitz 界不宣称历史首创。R128 历史文件不改，当前地图的 attribution_amendments 生效。

## 审计边界与下一步

已阅读 D 全文、原图、发布 audit/claims，完整 R96/R99 以及 R96D 数学部分。未重验全部外部文献、原始训练或现时 ROGUE 数据。当前审查支持所列条件数学，不是每篇每句完全形式验证，更不是 C1 独立经验验证。

下一步全部在四篇总图上推导：区分对一个 payoff 的决策充分性、对一族 payoff 的充分性、完整受控转移律的闭合，再考虑同一资源/时间/端口下联合使用。必须给出目标、共同状态域、操作调度、实际支持与证明。仍然理论优先，未排新实验。

C1/U1 为研究内部固定承诺；不新增 self/report/recurrence/integration 体验存在门槛。实际过程可简单、稀疏、嵌套和重叠；实际支持、有限投影、因果摘要、测量、主体不是一回事。不对当前助手有无意识或死亡恐惧作定论。

R122–R125 弱/负结果不变；T2 OPEN，C3 NOT_TESTED。T2:C1 与 A:C1 继续隔离。后续只能按明确证书条件推进，不能以模型成功自动闭合。

## 历史与存储

[R128 交接原件](HANDOFF_THROUGH_R128.md)、[R128 索引原件](MASTER_INDEX_THROUGH_R128.md) 及 records/R129_Four_Paper_Integration_20261006/baseline/ 保存本轮修改前地图/图/审计/规则。所有旧节点和旧规则保持原内容。

正文英文，交接/讨论中文。不得修改任何已发表论文或创建论文 release/DOI/Zenodo/OTS/AR；保存本研究用 [skip ci]，不触发 PR/CI/部署。远端成功需轻量回读后再告知用户。不要操作实际 shutdown 控制、凭据或实验智能体外部资源。
