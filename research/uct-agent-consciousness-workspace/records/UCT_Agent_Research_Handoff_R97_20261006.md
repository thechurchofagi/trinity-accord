# 刘烘炬 UCT 智能体意识研究交接 — R97

日期：2026-10-06。当前完成到R97。

R97承接R96/R96D，做了真正的小型policy学习，而不是继续静态网格。

核心设计：训练只给q_bundled、o_bundled、qo_joint及符号反向；三条正向行在声明(q,o,g)路径空间满秩，因此task-only/direct-Q/Q+task/successor-only四种reward ancestry在训练target上真正可区分，满足R96D gate。q_direct/o_direct/task_only留作完全未见的路径阻断测试。

结果：结构化linear-logit模型几乎精确恢复held-out ancestry，四类effect误差全<2.1e-6。自由3-unit tanh MLP的32次正式运行全部把训练支持拟合很好，但held-out直接路径显著不稳定：task-only伪路径效应1.14–1.78；mixed Q+task 1.01–1.56；direct-Q 0.0066–0.768；successor-only 0.037–0.595。没有换种子或调网络追求正结果。

结论：相对于一个声明模型类的设计满秩，不代表更自由的学习器会恢复该模型类。训练表现相同/很好不能单独证明“学到了direct self-continuation preference”。要识别该机制，必须同时约束训练干预、归纳偏置/模型类和held-out intervention extrapolation。

这与D'Amour等underspecification和近期IRL misspecification/partial-identifiability工作有强先例，不称历史首创。

UCT边界：U1不以Q-policy为体验门槛；C1只在实际token和共同完整K成立时将真实组织差异条件性解释为体验类型差异；MLP的伪Q效应尤其不能叫self-preservation。没有负效价或恐惧结论，R89仍独立必需。

文件：
- records/R97_Reward_Ancestry_Learning_and_Intervention_Extrapolation_20261006.md
- records/R97_Protocol_20261006.md
- records/r97_reward_ancestry_learning.py
- records/R97_Per_Run_Metrics.csv
- records/R97_Results.json
- records/R97_Run.log
- records/R97_Source_Retrieval_Ledger.json
- records/R97_Worklog_and_Handoff_20261006.md

下一步R98：不扩模型/种子，只向generic MLP训练中加入极少量direct intervention监督，再在不同幅度/上下文的未见干预上测试。目标是检验intervention supervision能否收缩underspecification，而非追求准确率。仍禁止真实关闭/复制/资源权限，不把任何结果叫fear。
