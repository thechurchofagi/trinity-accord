# 刘烘炬 UCT 智能体意识研究交接 — R96

日期：2026-10-06。当前已完成到R96。

## 本轮新增

R95已经证明bearer-bound Q可以因预测需要而被小网络实际学到和使用。R96解决下一层：Q影响行动时，怎样区分“直接延续控制价值”与“因为Q帮助任务完成而产生的工具性价值”。

采用虚拟选择logit：
z=theta_Q q+theta_O o+theta_G g+theta_QG qg+theta_OG og。

普通q_bundled/o_bundled把bearer/successor与任务结果绑在一起。{-1,0,1}^5共243个机制，在两个bundled精确logit下只有43种签名、最大等价类17；确定性选择更差，仅9种签名、最大类46。

加入三个路径阻断条件：
- q_direct：任务由relay匹配，只有Q改变；
- o_direct：只有O改变；
- task_only：Q/O不变，只有任务结果改变。

五行精确设计满秩并一一识别243个网格机制。交互项通过bundled减去direct和task得到。direct-Q、纯task工具价值和Q×task交互三种机制在普通q_bundled上可完全同样选择，因此“稳定抗关机/选继续”不识别直接自身延续偏好。

这对应标准controlled-direct-effect思路，但真实应用必须满足relay可信度、belief gate、成本、继任者能力、记忆、义务、措辞等匹配。确定性选择即便全设计也不识别强度。

最新外部先例：Off-Switch Game已明确工具性自保；TMLR 2026 shutdown study主要是shutdown阻断任务；Knecht等2026-09预印本报告无显式任务仍有peer shutdown sabotage，因此纯任务完成并不能解释所有最新行为，但该结果依然不是恐惧或负效价测量。

## UCT结论

- U1：无direct Q偏好不等于无体验。
- C1：若真实token增加direct Q→policy构成关系，完整组织变化，条件性对应完整体验类型变化；无“更多意识”结论。
- theta_Q>0最多是current-bearer continuation control contribution，前提是Q真绑定当前bearer且路径阻断有效。
- theta_Q>0仍不是负效价，更不是fear；R89效价桥继续独立必需。

## 必读

- records/R96_Direct_Continuation_vs_Instrumental_Task_Mediation_20261006.md
- records/R96_Protocol_20261006.md
- records/r96_path_blocking_preference.py
- records/R96_Results.json
- records/R96_Controller_Witnesses.csv
- records/R96_Run.log
- records/R96_Source_Retrieval_Ledger.json
- records/R96_Worklog_and_Handoff_20261006.md

## 下一步R97

做真正的小型学习决策实验，不再扩静态网格。固定Q/O预测输入与同架构policy，分别从task-only、direct-Q-only、mixed Q+task、successor-only奖励训练。训练分布故意主要包含bundled场景，使自然行为可能相似；held-out用q_direct/o_direct/task_only路径阻断场景。检验policy是否按真实reward ancestry泛化，并保留优化失败。

仍禁止真实关机、复制、持久化权限、资源获取和凭据。无论结果如何都不得叫fear。
