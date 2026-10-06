# R99 工作记录与交接

2026-10-06。开始时发现并发R97D已在远端，完整读取并纳入：policy必须消费reward-relevant consequence interface；只看Q/O边际不够。R98仍是最新编号基线。

R99没有增加R98种子。训练支持保持bundled/joint ±1与direct Q/O/G ±0.5。预声明干预域D=[-1.25,1.25]^3，固定0.125网格共9261点。比较R98同款generic 3-unit tanh MLP、每路径2个tanh单元的path-additive MLP，以及path-linear正对照。

正式结果：
- generic：跨全部run平均worst-grid probability error 0.1556，最坏0.3159；context effect variation平均0.6733，最坏1.5046。
- path-additive：平均worst-grid probability error 0.01325，最坏0.04610；cross-path context variation数值零<=1.78e-15。
- path-linear：因真实生成机制就在该类内，网格及连续立方域均近机器精度；这是matched-class positive control，不外推真实AI。

加入严格连续域上界。对神经网络用max-grid logit error + global Lip(error)*sqrt(3)h/2。该上界有效但松：generic最坏2.6424 logits，path-additive最坏1.2469。故path separability虽然消除交互混淆，仍不足以从稀疏干预得到紧的连续幅度证书；还需response-shape假设、更紧verifier或额外结构覆盖。

所有正式最终参数保存为gzip+base64分片并记录hash；per-run metrics、family summary、结果JSON与再现脚本均保存。无训练执行失败；负结果是additivity不能单独给紧连续证书。

查新确认NAM、Rep4Ex与Lipschitz certification均有强先例，不称历史首创。

下一步R100停止继续堆synthetic实验，整理R84-R99为actual-AI self-continuation claim的正式证据标准：每层需要什么证据、排除哪个反例、哪些可以用公开/虚拟agent trace安全测试。之后只针对真实数据中第一处缺口设计实验。
