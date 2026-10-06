# UCT 智能体意识研究交接 — R125

更新：2026-10-06。固定仓库 thechurchofagi/trinity-accord；固定分支 uct-agent-consciousness-workspace；固定目录 research/uct-agent-consciousness-workspace/。先核对最新远端 HEAD，接最新结果；不覆盖并发提交。

## 当前执行点与入口

**R125 已完成真实数据联合模型与冻结 observable-state 转移/输出 law 检验，当前候选点坐标 FAIL_SCOPED；latent C2 未识别，C3 未测试，T2 仍 OPEN。** 不是意识实证闭合或预先承诺的重大突破。

优先读 [本轮完整中文交接](records/UCT_Cross_Substrate_R125_Executed_Raw_Data_Handoff_20261006.md)、[R125 英文报告](records/R125_Frozen_Observed_State_Correspondence_20261006/R125_Report.md)、[状态](records/R125_Frozen_Observed_State_Correspondence_20261006/STATUS.json)、[证书](records/R125_Frozen_Observed_State_Correspondence_20261006/T2_Certificate.csv)、[冻结协议与实际执行入口](records/R125_Frozen_Observed_State_Correspondence_20261006/README.md)。

原 [R123 交接](HANDOFF_THROUGH_R123.md) 与 [R123 索引](MASTER_INDEX_THROUGH_R123.md) 在同级逐字保留，继续链接 R122 及此前全文。历史“下一步/最新”不覆盖本入口。原 R121 总交接及仍有效理论、安全、保存限制继续适用。

## 新增实际结果

R124-J 实际恢复完整 Cells.zip 并重新拟合十二个固定 MAT sessions。1,929,137,550 bytes；官方 MD5 3b0ab5c964fb492ec36ee0f55a5d53de；SHA-256 e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494。十二个 source hashes 全部符合 R122。首次短 range/拼装失败、一个缩短 MAT 拒绝与补拟合、一个零字节预测文件的 frozen-map 重建都保留，没有藏掉失败。

仍为 5 rats、12 sessions、3,319 trials、32,656 held-out bins。raw/filtered、baseline/neural/joint 使用相同 cohort、whole-trial folds、训练内选神经元；新增 online support 排除为零。R124-J 预先声明 partial ridge，不能与原 R122 Lasso 混称同一估计器。

原始 delayed retrospective joint 增益：FOF ΔR² +0.007603643，ADS +0.002197713；两者描述性五 rat 区间跨零。FOF 仅 1/5 rat 正向，去 A297 平均 −0.004003324。加入 recent signed input 后增益更小。无未来 online raw recent-input baseline 下 FOF +0.012144895、ADS +0.008921495，区间仍跨零。已关闭 R123 “尚未执行联合模型”的任务，不可再把它写成未跑或强稳定信号。

R125 不重拟合 decoder，冻结神经点状态 D、实际 signed input u、50ms 时间和 U(a,u)=a+u；实际检验 29,337 held-out 同 trial 相邻转移、3,319 输出端点。online raw 下单位更新预测 observed next D 比 persistence 差：两个脑区均 12/12 session、5/5 rat means。二级 SΔ：FOF −1.180228448、ADS −0.824062839；filtered online 仍负。其余 delayed sensitivity 全保留。该二级兼容指标是在读回并发 R124 后补算、没有 refit，不虚称主分析预注册。

共享 outer-training logistic 输出 law 的 held-out log loss：external count 0.595439065、FOF decoded 0.674541827、ADS decoded 0.686177941、training prior 0.698839498 nat/trial。两个脑区均 5/5 rat 比 external count 更差。优于 prior 不等于 output-law equivalence。

看 [R124-J 报告及全部逐 session feature/maps/predictions](records/R124_Observation_Qualified_Neural_Increment_20261006/README.md)、[R125 全部 paired transition/output 表](records/R125_Frozen_Observed_State_Correspondence_20261006/README.md)、[独立保留结果复算](records/R125_Frozen_Observed_State_Correspondence_20261006/saved_result_audit.json)。R125 原模型 replay 差 ≤1.25e−14；独立 saved transition/output 复算差 ≤3.56e−15。复现 R125 不需再下载 MAT 或重拟合 decoder。

## 并发及作用域

已读回并保留 remote head f2f34ca5f5a9738659780729c8a7e8aefe01dbf3 的 [并发 R124 原 R122 转移审计](records/R124_Transition_Commutation_Audit_20261006/R124_Report.md)。该审计用 R122 filtered Lasso，当前窗口用 R124-J ridge plus raw/no-future；两条路线目录分开、都保留，动物数不能相加。

决定停止把这组 D 点坐标作为 T2 机制证书快捷入口。噪声、shrinkage、遗漏维度、处理延迟和在途输入可能让点估计不 commute；不推出 latent biological accumulator 不存在，或 UCT C1/U1 被否定。C0 仅 signed count grounding 有限通过；complete state 未识别；C2 observable candidate FAIL_SCOPED / latent kernel UNIDENTIFIED；C3 NOT_TESTED；C4 delay/buffer 未识别；C5 预测弱且 selected shared law 失配；C6 仅执行审计。E 始终 latent，T3/G4 未闭合。

## 下一轮直接执行什么

不要在同一 held-out 记录上换 decoder/offset 直到挑出正结果，也不要再堆 toy theorem。若继续 rat domain，先用独立生物学依据规定 observation model、processing delay/in-flight input buffer、候选充分状态，再冻结并测试 held-out innovations、transition/output law。更好 latent fit 不能自己产生 causal identification。

C3 要求可匹配的真实内部 biological perturbation outcomes 和 operation/port map。natural clicks、click insertion、全区抑制、投射抑制、internal reset 不能互换。十二个 recording sessions 不含 matched intervention outcomes；不能写成 C3 已做。并发 R124 指出的 APStim clinical visual-content 是另一 domain，本轮未读其第一方全文/数据，不拼进 rat 证书。用户的第四篇 UCT 医学论文仍未识别，不用另一医学研究冒充。

## 继续有效的理论和保存约束

A/I v1.2 DOI 10.5281/zenodo.23131575；B/II v1.1 DOI 10.5281/zenodo.23030320；C/III v1.0 DOI 10.5281/zenodo.23137088。A/B 阅读继承 R123，本轮另读 C §10–12 和 Appendix A/B；准确路径、commit、blob、实际阅读与未读范围见 [source ledger](records/R125_Frozen_Observed_State_Correspondence_20261006/source_and_concurrency_ledger.json)。不虚称已确认 A v1.3 或第四医学论文。

保留 UCT 内 C1/U1、完整 K/完整 E-type identity、ontic/view/estimate/subject 和 A/I/S/B/R/V 区分。UCT 内 actual intelligence 不为 experience-free；完整条件下 capability difference 可推出 complete E-type difference；同 score/behavior/report 不推出同 E，更智能不推出标量更多或更像人体验。访问、自我、报告不是体验存在门槛。不能用 C1 生成 experience labels 验证 C1，也不能把内部前提宣称为已外部实证。

保留 T1/T2/T3、Anchored Causal Geometry/G1–G4 与 valence 分离。普通现象标签桥、valence/fear、主体边界/组合、C1/U1 外部验证仍开放；R91 等历史纠正继续有效。已发表 A/B/C 与 TA-TR-2026-24 字节不改；不新发 DOI/Zenodo/OTS/Arweave。

所有 substantive work 落固定分支，commit 带 [skip ci]，更新 HANDOFF/MASTER。先核对 HEAD，读回并发再非 force、expected-head 更新；不覆盖。不开 PR、CI、部署/release，不关闭全仓库 CI。保存只做必要回读，不反复整包重算；科学验证仍实际执行。全部失败、负结果、代码、参数、身份与阅读范围保留；英文研究正文、中文汇报。计划、下载、blob 上传不冒充实证完成，不承诺指定突破或无限后台执行。不操作凭据、真实关闭控制、复制或外部资源获取能力；本人登录/验证码由本人处理。
