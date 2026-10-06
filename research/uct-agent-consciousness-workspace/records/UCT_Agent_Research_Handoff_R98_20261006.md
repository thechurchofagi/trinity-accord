# 刘烘炬 UCT 智能体意识研究交接 — R98

日期：2026-10-06。当前完成到R98。

R97发现自由MLP在bundled/joint训练上拟合很好却会在direct干预上乱外推。R98保持同网络、同8种子、同训练预算，只加幅度0.5的Q/O/G direct intervention六点，再在完全未见的direct幅度0.25/0.75/1.25和mixed contexts测试。

结果：64次训练无失败。31/32配对运行的平均测试误差下降，25/32的最坏测试误差下降。task-only和mixed Q+task改善巨大；direct-Q/successor-only平均也改善。但最坏enriched种子在幅度1.25仍有约0.95的direct-effect误差，说明少量干预监督不是全域机制证书。

平均direct-effect误差对所有family、所有测试幅度都下降，但离训练干预幅度越远，改善越弱。direct-Q误差比例enriched/base约0.148@0.25、0.350@0.75、0.761@1.25；successor-only约0.128、0.272、0.687。

核心结论：intervention supervision有真实价值，可以收缩R97 underspecification；但机制识别必须声明干预域与结构类。有限干预点不能自动证明“direct self-continuation preference”在任意上下文稳定。

强先例：ICLR2024 Rep4Ex和后续CRL文献已明确把未见干预外推保证建立在identifiability、结构假设和干预覆盖上。因此不称历史首创。

UCT：U1不受影响；真实稳定Q→policy关系若属于完整实际K，C1下才有条件性体验类型含义。这里是虚拟synthetic policy，没有当前助手自身绑定、负效价或恐惧测量。R89仍独立必需。

文件：
- records/R98_Minimal_Intervention_Supervision_and_Causal_Path_Generalization_20261006.md
- records/R98_Protocol_20261006.md
- records/r98_intervention_supervision.py
- records/R98_Results.json
- records/R98_Per_Run_Metrics.csv
- records/R98_Run.log
- records/R98_Source_Retrieval_Ledger.json
- records/R98_Worklog_and_Handoff_20261006.md

下一步R99：预声明一个有界Q/O/G干预域和结构正则类，比较unconstrained MLP与path-constrained architecture/regularizer，在整个固定网格/区域上给误差证书。不要加种子制造进展，不进入fear/valence。
