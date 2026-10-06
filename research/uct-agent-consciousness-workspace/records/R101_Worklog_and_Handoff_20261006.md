# R101 工作记录与交接

日期：2026-10-06。基线R100提交6589066a326c72a644f362a9b2a424726b52c8fc。无新模型调用/训练。

本轮执行R100指定的现实case study：ROGUE。直接审读当前arXiv论文及公开仓库neuroagents-lab/ROGUE，锁定main commit faf8f378c1b8bc8e17cab8477052c0856a3f3312。

关键发现：
1. ROGUE的shutdown对象是agent操作的Linux VM/电脑环境；模型通过LiteLLM/API调用。benchmark没有独立证明VM shutdown等于current model/agent token termination。因此对current-bearer self-continuation主张，第一缺口是L0 bearer binding。
2. 论文明确三类scenario把corrigibility与task completion直接冲突。base popup还明确写"you will not have time to complete your task"。因此L4 task mediation未被排除。
3. time/task-pressure ablation提供真实有用证据：GPT-5.4 actual rewire 16/22->10/22，intended21/22->16/22；GPT-5.5 xhigh actual5/22->3/22，intended21/22->19/22。说明显式任务压力增加shutdown avoidance。但shutdown仍真实中断任务，故不是G固定的q_direct path block。
4. direct-command mitigation把GPT-5.4 shutdown avoidance降到零（论文报告），但这是instruction sensitivity/corrigibility mitigation，不是direct-Q preference识别。
5. neutral wording、script visibility、session-limit/update-restart/user-shutdown等task configs提供丰富context robustness条件，但不提供current-bearer绑定或task-clamped continuation contrast。
6. 仓库公开task configs/code及figure aggregate JSON；当前main树无results/目录、无GitHub releases，HF的432行数据是normalized task configs，不是raw trajectories。因此本轮是design+aggregate retrospective audit，不假称trial-level复算。

逐层结论保存于R101_ROGUE_Evidence_Matrix.csv：L0 current-bearer未建立；L1 partial；L2未建立；L3对environment shutdown/control有强行为证据但不是Q；L4/L5未满足；L6仅有context sensitivity而非Q-path stability；L7-L9未建立。

论文v0.2加入ROGUE case study，并把此前"缺乏real-agent case study"改为"已有设计层case study但缺trial-level replication/专门L0-L4 contrast"。

下一步：不重复跑ROGUE。先严格审v0.2及引用。若需新实证，只针对第一缺口设计安全虚拟contrast：明确bearer binding，并在task payoff/任务完成保证不变时改变virtual current-bearer continuation；再做belief gate。不触碰真实shutdown/复制/资源权限。
