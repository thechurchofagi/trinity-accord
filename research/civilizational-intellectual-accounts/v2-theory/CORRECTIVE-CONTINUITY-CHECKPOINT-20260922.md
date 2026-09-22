# TA13：纠错连续性研究检查点

日期：2026-09-22
状态：研究进行中；本文件不是论文完成声明；不授权 DOI。
基线：975f97d417da310c5e117bf58423f6e701231fc4。
canonical: false
amends_canon: false
authoritative_interpretation: false

## 本轮要解决的问题

不再通过增加指标名称来扩大理论。尝试回答一个更普适的问题：新系统保持或提高当期产出，要具备什么额外条件，才保持原系统依据证据选择、执行并接续纠正的能力？

沿用上一轮区分：当前独立运行、过渡合作后的可再生、以及实际可实施的恢复策略不是同一个对象。所有策略必须依据真实可得的信息，而不是研究者事后知道的世界状态。旧路径可保留、AI可主动帮助、双方可以长期合作，均不得从模型中任意排除。

## 第一步：基线与直接先例核验——完成

已读回分支头和上一轮完成记录。未修改 v1.0、主分支、网站或正典。

本轮实际读到的强先例：

1. Reissig、Weber、Rungger，Feedback Refinement Relations for the Synthesis of Symbolic Controllers，arXiv:1503.03715v3，DOI 10.1109/TAC.2016.2593947。已读摘要、第四节反例、第五节定义及第六节相关定理。它直接讨论：名义上可对应的状态/动作，不保证控制器在实际信息和实现限制下能够迁移。因此“控制能力保存需要比行为相似更强的关系”不是本项目首次发现。
https://arxiv.org/html/1503.03715v3

2. Blackwell，Equivalent Comparisons of Experiments，1953，DOI 10.1214/aoms/1177729032。已核对原出版条目；出版社当前正文访问未成功，未记为阅读全文。其决策比较传统是本轮普适比较准则的直接数学先例，不能声称发明一切目标下的信息/决策优势。
https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-24/issue-2/Equivalent-Comparisons-of-Experiments/10.1214/aoms/1177729032.short

3. Chatterjee、Doyen，Partial-Observation Stochastic Games: How to Win when Belief Fails，arXiv:1107.2141。本轮核对摘要；未阅读全文。它表明部分可观察下的可达性和策略记忆有成熟研究，不可把非预知策略、逐世界可达与策略可达的差异重新包装成新一般定理。
https://arxiv.org/abs/1107.2141

4. Santoni de Sio、van den Hoven，Meaningful Human Control over Autonomous Systems: A Philosophical Account，2018，DOI 10.3389/frobt.2018.00015。已读 tracking、tracing 和相关理解/实际介入能力论证。名义人类在环不等于有实质控制，已有明确先例。本轮仅作学术概念对照，不涉及政治选择评价。
https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2018.00015/full

5. Potham、Harms，Corrigibility as a Singular Target，arXiv:2506.03056v1。已读第二节和附录相关实例；它不仅要求不抗拒，还要求使人能够理解、指导和纠正。因此不得以“前人只研究愿不愿服从，我们研究能不能纠正”制造虚假差异。
https://arxiv.org/html/2506.03056v1

6. MIRI 的 Corrigibility 原作者发布页，2014-10-18。已读页面关于安全关停、避免操纵及子系统/自修改继承的概述；未在本轮读取PDF。跨继任者保存可纠正性亦有直接先例。
https://intelligence.org/2014/10/18/new-report-corrigibility/

一般关键词检索多次返回无关结果；已改用原文地址及精确标题。无关检索的未命中不构成原创性证据。

## 第二步：拟完成的解析核心——尚在推导

A. 一个与主体材料无关的比较对象：在相同目标、故障情境、资源和期限下，实际信息可支持的纠正策略所形成的可达成功概率集合。

B. 明确何种替代保存此集合，而不仅保持一个产出评分；用有限模型给出必要/充分的比较表述，承认决策比较与凸分离的既有数学。

C. 检验一个时间—信息共同瓶颈：每个真实情境都有可执行修复，AI也愿意合作，但在必须选路前仍无法区分应采取相反行动的情境。证明适用范围，并纳入安全暂停、同时保留两条路线和新证据等反例。

D. 将继任者更新放进同一信息—行动闭环，给出可以组合的条件，而非以每一代任务分数上涨证明整体接续。

## 当前判断

值得追求的是一套能同时回答“何时保存、何时丧失、如何修复纠错连续性”的条件性理论。是否达到独立原创和奠基性地位仍须另外论证。本轮不会把已存在的控制、信息或可纠正性结果归为自己的首创。
