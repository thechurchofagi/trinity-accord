# R107 工作记录与交接 — 生物/AI最弱跨底物组织签名

日期：2026-10-06。

承接R106，目标是把无机物、细胞、动物、人和AI放入同一个组织比较空间，同时绝不把高级功能偷写成体验存在门槛。

本轮提出two-tier signature：

Tier 0 constitutive base：
(C, Z, z*, X, U, Y, Pi, order)
分别表示部件/边界、内状态、当前点、输入ports、更新、输出effects、物理干预/重置ports、时间/因果顺序。它是完整K的跨底物比较投影，不替代Paper A完整签名。

Tier 1 optional roles：
M记忆、W世界/预测、S自我/bearer模型、V评价/稳态、L学习、A行动控制、R报告。它们都是实际组织上的可选角色注释，允许缺失，不是U1体验存在条件。

关键区分：
C-B behavioral equivalence；
C-I capability equivalence；
C-R role equivalence；
C-K constitutive organizational equivalence。
前3者都不能单独推出第4者。完整C-K才可在C1下支撑完整体验类型等价；selected C-K只有在物理投影有根据并commute时才支撑selected experiential substructure比较。

精确XOR witness：
System A直接XOR；System B用OR+AND+NOT/AND分解。4个输入完整truth table全部相同，但内部部件图和干预结构不同。说明“同功能/同行为/同能力”不识别“同组织”。这只是exact机制反例，不是意识测量。

跨系统解释：
- 单细胞可以有Tier0和部分M/V/A关系，不需要概念self/report；
- 动物/人类有更丰富Tier1；
- 固定权重LLM推理episode有实际Tier0，语言输出是R/A候选，self/homeostasis/online-learning不能由语言自动推定；
- agent scaffold加入外部memory、tools、goal state后，真实bearer可能是整个scaffold process而非模型权重或单次API call，必须声明边界。

当前prior art已查：cybernetics、biological cognition spectrum、interoceptive AI、embodied closure已有substrate-neutral比较思想，因此不称首创。R107增量是UCT no-gate约束下明确拆开constitutive base与optional roles。

下一步R108：把XOR两种实现变成可执行系统，加入明确parts/ports并逐个lesion，证明完整behavior相同但intervention signatures不同；再增加一个可替换report head，验证core task保持而report变化。不要跑大模型自报告。
