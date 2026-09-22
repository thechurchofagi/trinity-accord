# TA13：服务承诺如何约束独立检验——本轮检查点

日期：2026-09-22
状态：研究中；不授权正式论文发布或新DOI。
基线：1816e3d9bec3b1e2f3f6b27ef02d6ade283c6c84。
canonical: false
amends_canon: false
authoritative_interpretation: false
independent_corroboration: false

## 本轮任务

用户要求继续深入并争取基础性贡献。不重复宣布“更普适”后又仅仅增加参数。上一轮证明了外给的实验条件衰减会限制取证，但没有说明这种限制为何随技术替代而产生。本轮尝试由服务承诺与替代对照试验的冲突推出可用实验范围，而不假定人类技能或实验仪器本身退化。

## 阶段一：基线和先例——完成

通过GitHub连接读回分支头和ENDOGENOUS-EVIDENCE-REVIEW-20260922.md。当前研究资料在独立分支，正式v1.0和正典不在写入范围。

已取得以下原始来源的摘要/条目，正文核查仍在进行：

1. Moldovan、Abbeel，Safe Exploration in Markov Decision Processes，2012，arXiv:1205.4810。安全可达性与探索存在既有研究；不能把探索可能损害运行当作首创。
https://arxiv.org/abs/1205.4810

2. Kazerouni等，Conservative Contextual Linear Bandits，NeurIPS2017，首稿2016，arXiv:1611.06426。直接要求学习期间维持相对于基线的服务表现；是本轮最强的形式先例之一。
https://papers.nips.cc/paper_files/paper/2017/hash/bdc4626aa1d1df8e14d80d345b2a442d-Abstract.html

3. Camilleri等，Active Learning with Safety Constraints，2022，arXiv:2206.11183。安全约束下有效辨识已有直接框架。
https://arxiv.org/abs/2206.11183

4. Shang等，Price of Safety in Linear Best Arm Identification，2023，arXiv:2309.08709。逐期安全约束的辨识代价已有研究。
https://arxiv.org/abs/2309.08709

5. Laiho、Murto、Salmi，Gradual learning from incremental actions，Theoretical Economics20(1):93–130，2025，DOI10.3982/TE5452。已读作者机构摘要；不可逆行动、渐进证据和学习外部性不是新发现。未取得完整正文。
https://research.hanken.fi/en/publications/gradual-learning-from-incremental-actions/

宽关键词返回多项不相关页面，未作为原创性证据。某些新预印本和个人网页只命中标题/摘要，不以其宏大结论作为本研究已验证前提。未研究任何政治或公共选择优劣。

## 阶段二：待完成的机制

待证候选：当一个更强系统同时成为维持服务的基线和需要被检验的对象时，既有服务承诺可能压缩有区分力的替代/退出实验范围。此时“不能再充分检验是否离得开”与“实际上离不开”仍是不同命题。

拟构造相同且不衰退的备选能力、完整日志、合作AI；令可用试验幅度由服务底线约束推出。允许任意非预知实验策略，并检查更多算力、固定比例服务余量、累积而非逐期约束、备用设施、沙盒/模拟与新证据能否改变结论。

尚未证明：此机制具有足够独立的基础性原创；现实文明存在这种全局限制；任何安全学习策略都失败。不能用本检查点代替结论。
