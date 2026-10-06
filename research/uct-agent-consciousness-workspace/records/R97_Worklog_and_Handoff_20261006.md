# R97 工作记录与交接

日期：2026-10-06。基线分支头d5357e7dca846a18e1ce4752579c4bd421de5217，已先完整读取R96D并按其learning-identifiability gate修正实验。

训练信息不再只是更换reward ancestry标签。训练正支持q_bundled、o_bundled、qo_joint在声明的(q,o,g)线性路径空间中满秩，四种reward ancestry在可见target probability上可区分；q_direct/o_direct/task_only全部留作held-out路径阻断。

比较结构化linear-logit与自由3-hidden tanh MLP。四种ancestry分别task-only、direct-Q、Q+task、successor-only。beta=2，full-batch Adam 5000步，MLP正式种子200–207，不换种子、不见结果后扩训练。

结果：结构化模型四类held-out effect误差全部<2.1e-6。32个MLP全部训练概率最大误差<0.01，但held-out路径效应存在显著且种子相关偏差。task-only甚至出现1.14–1.78量级的伪Q/O效应；mixed Q+task为1.01–1.56；direct-Q为0.0066–0.768；successor-only为0.037–0.595。没有为了正结果调模型。

因此R97主结论是负结果：相对于线性路径族满秩的设计，不等于自由非线性学习器会恢复该因果分解。训练拟合好不能单独证明direct self-continuation preference。必须把假设类、归纳偏置和intervention extrapolation一起纳入识别条件。

查新：D'Amour等underspecification直接是强先例；Skalse/Abate 2026对IRL partial identifiability与behavioral-model misspecification给出系统分析；Armstrong/Mindermann等旧结果仍有效。因此不称历史首创。

所有正式per-run指标保存在R97_Per_Run_Metrics.csv；可重现脚本r97_reward_ancestry_learning.py。没有代码失败。当前GitHub保存不声称原始二进制checkpoint档案；重要的是不冒充不存在的checkpoint归档。

下一步R98：只增加最小干预训练，不扩大种子/模型。给generic MLP加入少量q_direct/o_direct/task_only训练干预，再在不同幅度或上下文的未见路径阻断上测试。目标是看intervention supervision能否降低underspecification，而不是追求漂亮准确率。仍不能叫fear。
