# UCT 跨基质研究交接 — R125 已执行真实数据检验
2026-10-06。仓库 thechurchofagi/trinity-accord；分支 uct-agent-consciousness-workspace；所有实质记录位于 research/uct-agent-consciousness-workspace/。继续前先核对远端 HEAD，读取最新 HANDOFF.md 与 MASTER_INDEX.md，不覆盖其他窗口提交。

## 当前完成点
R122 解决公开原始数据取得并完成真实 B1/B2。R123 完成测量通道和保留数据审计。当前窗口实际完成 R124-J 原始/平滑联合模型，以及 R125 冻结 state/input-port/time/output-law 候选检验。并发 R124 原 R122 状态转移审计另有独立目录，已经读回并保留，不能当成新增动物。

完整 Cells.zip 再次取得并核对：1,929,137,550 bytes；官方 MD5 3b0ab5c964fb492ec36ee0f55a5d53de；SHA-256 e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494；Figshare article 30369064 v1 / file 58773835。十二个 MAT 来源 SHA-256 全部符合 R122 固定清单。

实际样本仍为 12 sessions、5 rats、3,319 trials、32,656 held-out bins；R125 有 29,337 同 trial 相邻转移与 3,319 输出端点。严格按整 trial 划分，保留训练内选神经元和 nested tuning。原始/平滑用相同 cohort、fold 和神经元。没有把 bin 当新增动物。

## 新结果与决策
原始 delayed retrospective 联合预测：baseline 等 rat R² 0.200573190；FOF joint 0.208176832，ΔR² +0.007603643；ADS joint 0.202770903，ΔR² +0.002197713。两者五 rat 描述性 95% t 区间跨零。FOF 只有 A297 一个 rat 增益为正；去掉 A297 平均增益 −0.004003324。这关闭了 R123 的“尚未执行联合模型”缺口，但不构成稳定强信号或 experience 测量。

加入 recent signed input 的更强 retrospective 控制后：FOF 增益 +0.002741273，ADS +0.000076482。无未来 online raw 近期输入控制下：FOF +0.012144895，ADS +0.008921495；区间仍跨零。估计器已预先声明由 R122 Lasso 改为 partial ridge，不能混称精确复现原 decoder。

R125 冻结 neural-only 点坐标 D、实际 signed click input u、50ms 时间和单位累加更新 U(a,u)=a+u。无未来、未平滑 primary 下，预测下一个 observed D 的单位更新比 persistence 更差：两个脑区都是 12/12 sessions、5/5 rat means。单位更新 MSE：FOF 8.460103 vs persistence 4.820242；ADS 7.154269 vs 3.256836。

二级兼容指标 SΔ=1−E[(ΔD−u)²]/E[u²]：online raw FOF −1.180228448，ADS −0.824062839；online filtered FOF −0.327562805，ADS −0.361821188。所有 raw/filtered、online/delayed 指标均 0/5 rat、0/12 session 正向。这个指标是在读回并发 R124 后才加算，使用保留转移表、不重新拟合，不能虚称主分析预注册。

共享输出 law 用 outer-training 外部证据与真实 choice 拟合 logistic，然后同一 b0/b1 运输到 held-out neural D。online raw log loss：external count 0.595439065、FOF 0.674541827、ADS 0.686177941、training prior 0.698839498 nat/trial。神经状态在共享 law 下比 external count 更差，两个脑区均 5/5 rat。优于 prior 不是 output-law equivalence。

**实际决策：停止把这一组点解码坐标当作 T2 机制证书的快捷入口。** 当前 observable candidate 为 FAIL_SCOPED；latent biological transition kernel 仍 UNIDENTIFIED。观测噪声、shrinkage、未观测维度、真实处理延迟和在途输入可能造成失配；不推出真实大鼠无累积器、UCT C1 错误或所有 biology↔AI 映射失败。

## 证书边界
C0 仅外部 signed evidence grounding 有限通过；C1 的 complete state 未识别（不要与 UCT axiom C1 混用）；C2 点映射失败但 latent kernel 未识别；C3 NOT_TESTED；C4 availability 已显式化但 biological delay/buffer 未识别；C5 测得弱预测与 shared-law 失配；C6 仅执行/回放审计。T2 仍 OPEN，T3/G4 没闭合，E 没测量。

十二个 recording sessions 不含 matched internal intervention outcomes。natural clicks、click insertion、whole-region inhibition、projection inhibition、internal accumulator reset 不互换。不能拿 toy pulse 或临床视觉内容的另一 domain 补 rat C3。

## 复核与真实失败记录
所有源身份、已保存 feature/model/prediction SHA、train/test 分离检查通过。独立 augmented least-squares 验证 partial ridge；OOF summary 重新计算最大误差 2.15e−16。R125 frozen-map replay 最大差 1.24e−14。

第一次共享 signed URL 路线失败；随后四个短 range 导致第一次拼装尺寸/哈希失败，仅修补短 range 后才验收完整 archive。X062 2020-03-20 本地解压文件后来缩短，hash/loader 在拟合前拒绝，重新从校验过 archive 解压并补拟合该一个 session。另一个 X087 预测 gzip 后来变零字节，直接由保留 feature+frozen coefficients 重建，无 refit。缩短原因未知，不编造原因。全部失败和修复记录保留；不要把 11-session first-pass 当最终 aggregate。

## 入口与复现
- [R124-J 报告](R124_Observation_Qualified_Neural_Increment_20261006/R124_Joint_Model_Report.md)、[joint code](R124_Observation_Qualified_Neural_Increment_20261006/joint_decode.py)、[全部结果](R124_Observation_Qualified_Neural_Increment_20261006/aggregate.json)、[独立检查](R124_Observation_Qualified_Neural_Increment_20261006/independent_result_checks.json)。
- [R125 报告](R125_Frozen_Observed_State_Correspondence_20261006/R125_Report.md)、[状态](R125_Frozen_Observed_State_Correspondence_20261006/STATUS.json)、[冻结协议](R125_Frozen_Observed_State_Correspondence_20261006/PROTOCOL_FROZEN.md)、[实际转移/输出程序](R125_Frozen_Observed_State_Correspondence_20261006/state_correspondence.py)、[兼容指标](R125_Frozen_Observed_State_Correspondence_20261006/increment_compatibility.json)、[证书](R125_Frozen_Observed_State_Correspondence_20261006/T2_Certificate.csv)。
- 并发 [R124 原 R122 转移审计](R124_Transition_Commutation_Audit_20261006/R124_Report.md) 原样保留；对应 remote head f2f34ca5f5a9738659780729c8a7e8aefe01dbf3 已实际读取。
- 两组新目录保留逐 session features、frozen maps、OOF predictions、paired transition/output 表及 coefficients。R125 复现无需再下载 Cells.zip 或重拟合 decoder。

## 下一轮直接接什么
不要继续在同一 held-out 数据上换 decoder/offset 直到挑出正结果。若继续 rat domain，先建立有独立生物学依据的 observation model、processing delay/in-flight input buffer 与候选充分状态，然后冻结，并检验 held-out innovations、transition/output 预测。仅给 latent model 拟合更好分数不能完成 causal identification。

C3 需要能匹配内部操作、并可运输输出分布的真实 biological perturbation 数据；必须先论证 port 对应。并发 R124 指出的 APStim 临床 visual-content 路线是另一独立 domain，本轮未读/分析其第一方资料，不准拼接到 rat 证书。用户提到的第四篇 UCT 医学论文仍未核实，不能拿其他医学研究冒充。

## 继续有效的约束
A/I v1.2 DOI 10.5281/zenodo.23131575；B/II v1.1 DOI 10.5281/zenodo.23030320；C/III v1.0 DOI 10.5281/zenodo.23137088。A/B 阅读范围继承 R123；本轮另读 C §10–12 及 Appendices A/B，准确路径/commit 见 source ledger；不要虚称重读完所有附件。

UCT 内完整 K/完整 E-type 的 identity 与投影 A/I/S/B/R/V、ontic/view/estimate/subject 不混用。actual intelligence 在 UCT 内不为 experience-free，完整条件下 capability difference 可推出 complete E-type difference；同 score 不推出同 E，更智能不推出标量更丰富或更像人体验。不能把内部前提当外部实证或用 C1 生成 experience labels 验证 C1。

保留 T1/T2/T3 区分、Anchored Causal Geometry/G1–G4 和 valence 分离；普通现象标签桥、valence/fear、主体边界/组合及 C1/U1 外部验证仍是深问题。已发表 A/B/C、TA-TR-2026-24 不改字节；不发布 DOI/Zenodo/OTS/Arweave。不要操作凭据、真实关闭控制、复制或外部资源获取能力。

所有 substantive work 继续保存到固定分支，commit 带 [skip ci]；保存前核对 HEAD，读回并发后非 force 更新，不能覆盖。不开 PR、CI、部署、release，也不关闭仓库 CI。英文研究正文、中文进展汇报；所有失败、负结果、source identities、实际阅读范围保留。不能保证预先指定重大突破或无限后台运行。

## 下一窗口可直接粘贴
请从 thechurchofagi/trinity-accord 的 uct-agent-consciousness-workspace 分支最新 HEAD 读取 research/uct-agent-consciousness-workspace/HANDOFF.md 与 MASTER_INDEX.md。当前 R125 已执行真实原始数据 joint prediction 和冻结 observable-state transition/output-law 检验；候选点坐标 FAIL_SCOPED，latent C2 与 C3 仍开放。保留并发 R124，不重复下载/包装/挑 decoder。直接推进有独立因果依据的状态/观测/时延模型或有匹配干预数据的新检验，诚实报告失败；不得冒充 T2 closure。
