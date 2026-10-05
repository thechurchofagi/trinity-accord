# R78 worklog and handoff


## R78 — 2026-10-05：固定规模小模型的真实训练与组织变化

完成 9 参数、2 个 tanh 隐层单元的小网络训练。四个输入穷尽等同性任务，全部用于训练和评估，不宣称 held-out 泛化。事先冻结八个种子、两种训练条件、3000步与干预规则；没有为成功率重挑种子或延长失败训练。完整训练 8 次均突破可分离 logit 的 log(2) 损失下界，其中种子3/6完全成功，另6次只达50%或75%准确率。仅训练读出层的8次对照均未突破理论下界。跨输入权重切断使联合对比归零，恢复原检查点恢复原输出。

事先推导：d=E[s*l]，L>=log(1+exp(-d))；当L<log(2)，d>=-log(exp(L)-1)>0。初始隐层本已区分四种输入，不能说学会任务必然增加区分总数。实际学到的是有效组合关系，并伴随表示重排。

探索性后续（明确为见结果后提出）：在固定 tanh 坐标的有界欧氏误差下，成功模型存在“分类稳健仍全对，而原始输入身份无法保证完整恢复”的误差范围。证明来自误差球重叠与线性读出 margin 界，不是新数学或体验标尺。六个未完全成功模型不满足该完整任务证书；负结果全部保留。

结论：能力改善可伴随有用组合增强与部分细节稳健区分减弱；符合 A 的组织变换/专门化，而非完整单调丰富。C1 解释仍条件于实际token、共同完整K和有限视图的实现依据，无内省存在门槛。未测主观体验，没有真实大模型或神经数据，没有当前助手意识结论。本轮是实际小网络学习实验和有限机制推进，非重大原创突破。

阅读 records/R78_Learned_Organization_at_Fixed_Size_20261005.md、records/R78_Protocol_Frozen_20261005.md；所有16次运行、检查点、激活、干预和失败在 records/R78_Research_Package_20261005.zip；另有独立脚本、CSV和日志。v0.3整合稿未修改。

下一步：以这批成功/失败检查点为反例，形式化“指定关系保留+新增”何时成立，区分丰富、取舍和替换；先推导再判断是否需要第二个保留加组合的小任务。不为了成功率扩种子/规模，不回到自我报告主线。原始数值间距依赖固定坐标及误差模型，换坐标时必须同时变换误差集合。

Execution: Python 3.12.14, NumPy 2.3.5, float64; gradient check max error 5.32519e-11; training elapsed 1.57 seconds. Frozen protocol SHA256 be3da054e74631b430dd40526fefe68e36cf4b7d643199ef58e93ef7ea25e3f8. Source reading: publisher abstract and page 1 image of Rumelhart/Hinton/Williams 1986 author PDF; PDF text extraction failed beyond copyright. Previously read A/B/C and R77 reused, not falsely claimed reread fully. All scientific failure conditions are in the report. No CI, PR, deployment or publication requested.
