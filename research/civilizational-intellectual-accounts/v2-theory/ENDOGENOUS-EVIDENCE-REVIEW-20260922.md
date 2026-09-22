# TA13：证据生成与可检验性再生——研究检查点

日期：2026-09-22
状态：本轮研究进行中；非正式论文；不授权新DOI。
基线：0a2786047b918209ee18560798fbf83cfa61fbfa。
canonical: false
amends_canon: false
authoritative_interpretation: false
independent_corroboration: false

## 用户目标与边界

继续深入基础理论研究，不以小增量、命名或大量程序代替原创机制。继承上一轮限制：AUP、晚揭示目标、信息保存与反馈细化已有强先例；保留旧版与正典，只写独立研究分支。完成阶段及时保存和汇报。

## 步骤一：基线及直接先例——完成

通过连接读回分支，确认基线未变。现阶段关键问题不再只是‘未来的纠正目标什么时候告诉系统’，而是系统怎样生成使该问题能够被提出和检验的证据。

实际取得的主要来源：

1. Messeri、Crockett，Artificial intelligence and illusions of understanding in scientific research，Nature 627:49–58，2024，DOI10.1038/s41586-024-07146-0。已取得出版社摘要及页面；其科学问题/方法单一化和更多产出未必带来更多理解的论点直接相关。不能改名后作为本项目首创。
2. Perdomo等，Performative Prediction，ICML2020，arXiv:2002.06673；所读HTML为v4，2021-02-26。已读引言、主要定义和相关工作：决策改变后续观测分布已有形式框架，不能宣称首次发现内生数据分布。
3. Dekel、Fudenberg、Levine，Payoff Information and Self-Confirming Equilibrium，1999。取得Harvard作者机构仓储摘要，尚未在本轮读取PDF全文。已实现路径的正确预测与未尝试偏离上的错误可以共存，是既有思想。
4. Li、Pan，Rational Learning One Step Off the Path，arXiv:2608.05380v1。已打开正文，后续将查其内生实验与纠正机制。本检查点不声称已复核全部证明。
5. Kaufmann、Cappé、Garivier，On the Complexity of Best Arm Identification in Multi-Armed Bandit Models，arXiv:1407.4443。已取得原始摘要；自适应取样的变换测度/KL界是本轮数学核对方向，不是新一般定理。

一般组合检索返回不少无关材料，不能作为原创性否定/确认。一次按记忆试开的arXiv:1602.00388实际是核物理文章，已排除，绝不计入参考文献。未取得的全文不记为已读。

## 步骤二：待检验的机制

只说‘没有尝试，所以不会发现’仍是老问题。本轮尝试建立一个包含证据生成条件再生的模型：每期实验量可以增长，但可把相反解释拉开距离的实验条件，需要跨期维持或再生。

需完成：

- 固定真实问题与原始记录完整保存，排除已知的摘要丢失问题。
- 允许所有声明的适应策略，给出可检验性可能不足的条件，不以某个差策略失败冒充全策略失败。
- 正向构造能通过维护、AI帮助或新实验保持区分能力的策略。
- 区分有限精度的成功、渐近趋零的判错率和真实开放世界的全部科学能力。
- 与自我确认、持续激励/系统辨识、学习陷阱和内生观测文献做正面对照。

当前尚无新的奠基性判断。目标是产出一项清楚的机制与正反边界，而不是增加一份PASS。

## 来源

https://www.nature.com/articles/s41586-024-07146-0
https://arxiv.org/html/2002.06673
https://dash.harvard.edu/entities/publication/73120378-83d1-6bd4-e053-0100007fdf3b
https://arxiv.org/html/2608.05380v1
https://arxiv.org/abs/1407.4443
