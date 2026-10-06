# R112 工作记录与交接 — 第一版cross-substrate capability-support atlas

日期：2026-10-06。

从R111 support hypergraph选3个机制较清楚的能力：temporal working memory、evidence integration、self/bearer-state estimation。

Atlas A working memory：
跨底物最弱关系不是persistent firing，而是“过去输入造成的区别以某种实际状态保留，并在延迟后因果可用”。生物可能用persistent/recurrent activity、快速connectivity modulation、activity-silent状态；AI可用RNN hidden state、transformer context、显式/外部memory。exact toy reset memory使delayed accuracy 1.0->0.5。T1 strong，T2 partial/moderate，T3 absent。

Atlas B evidence integration：
最弱关系为history-dependent state update z_{t+1}=F(z_t,e_t)，最终决策依赖多时刻证据。2026 Neuron rat work支持distributed recurrent cortico-striatal accumulation；2026 RNN model出现transient与accumulated-evidence populations并有lesion effect。exact 3-sample majority toy：integrator 1.0，last-sample only 0.75。T1 strong，T2 moderate，T3 absent。

Atlas C bearer estimation：
最弱关系是own action channel与特定entity state-change的identity binding。生物bodily self-consciousness依赖multisensory ownership/agency/interoceptive relations；AI已有self-orienting和embodied self-model工作。exact two-entity toggle toy：保留entity-specific action/outcome可100%识别bearer；只保留“有一个entity改变”则0.5。T1 moderate-strong，T2 weak-moderate，T3 absent。

核心新结论：experience-intelligence coupling应该写成relation-specific：
capability T -> verified support relation R_T -> (C1条件下) selected experiential organization relation。
不能写成一个dExperience/dIntelligence全局系数。

另外，human和AI同能力可以依赖完全不同support：human WM可能依赖distributed recurrent/connectivity dynamics，AI可能依赖external buffer；因此same performance不推出same selected E organization。

下一步R113：形式化如何区分necessary support、alternative sufficient support、degenerate/redundant support、downstream readout和mere correlate；先在R112三个transparent AI systems上做causal support identification protocol，再考虑生物lesion数据。
