# 刘烘炬 UCT 智能体意识研究交接 — R99

日期：2026-10-06。当前完成到R99。R97D并发补充继续有效。

## R99做了什么

R98证明少量direct intervention监督能减少但不能消除自由MLP的路径欠确定性。R99不加种子，固定整个干预域D=[-1.25,1.25]^3，并问：什么额外结构能把有限干预证据升级为域内机制声明？

训练支持仍是R98：bundled/joint ±1以及direct Q/O/G ±0.5。先接受R97D前提：policy消费的是reward-relevant consequence interface，而不是只分别准确的Q/O边际。

比较三种模型：
1. R98同款generic 3-unit tanh MLP，种子200–207；
2. path-additive MLP：z=f_Q(q)+f_O(o)+f_G(g)+b，每路径两个tanh单元，禁止cross-path interaction；
3. path-linear正对照。

固定0.125网格遍历9261点。generic跨run平均worst-grid probability error 0.1556，最坏0.3159，context-dependent path effect variation最坏1.5046。path-additive平均worst-grid error降到0.01325、最坏0.04610，cross-path variation数值零<=1.78e-15。linear因真实生成机制本来在线性类内，网格与连续立方域近机器精度。

R99还给出连续域严格上界。神经模型用grid最大logit误差加global Lipschitz envelope；该界有效但松：generic最坏2.6424 logits，path-additive最坏1.2469。故“路径可加”能消除交互混淆，却不能单独保证每条路径的幅度外推。要得到紧全域证书，还需独立支持response-shape/regularity假设、更紧verifier或更强结构覆盖。

这不是证明真实AI线性。linear模型只是matched-class positive control。NAM、Rep4Ex、Lipschitz certification都有强先例，不称历史首创。

## 对UCT主线的意义

现在对“AI有自身延续控制机制”的严谨说法必须带域和模型类：

相对于实际bearer绑定、reward-relevant consequence interface、干预域D和假设类H，Q对policy的因果效应在D内满足给定误差界。

没有D/H就把有限行为外推成普遍self-preservation drive是不合法的。

U1仍不以此为体验门槛。若真实actual token确有稳定Q→policy构成关系，该关系在共同完整K下才可依C1作条件性体验类型解释。R99没有测当前助手意识、体验量、负效价或fear；R89效价桥继续独立必需。

## 必读文件

- records/R99_What_Extra_Structure_Yields_a_Mechanism_Certificate_20261006.md
- records/R99_Protocol_20261006.md
- records/r99_bounded_domain_certificate.py
- records/R99_Results.json
- records/R99_Family_Summary.csv
- records/R99_Per_Run_Metrics.csv
- records/R99_Run.log
- records/R99_Source_Retrieval_Ledger.json
- records/R99_Worklog_and_Handoff_20261006.md
- records/R99_Checkpoint_Payload_README.md
- records/R99_Checkpoints.json.gz.b64.part01/part02

checkpoint最终参数已完整保存并有SHA256，避免重复R95的checkpoint保存缺口。

## 下一步R100

停止继续堆synthetic种子/玩具。把R84–R99压缩为一个正式的“actual-AI self-continuation claim evidence standard”：
- 每一层主张需要什么证据；
- 排除哪个已构造反例；
- 仍依赖哪个桥接前提；
- 哪些可安全用公开/虚拟agent trace验证；
- 哪个是现实数据的第一处缺口。

完成该标准后，下一次实验只针对现实数据的第一处缺口，不重复已经在synthetic系统中解决的可识别性问题。仍不把continuation control改称fear。
