# UCT 智能体意识研究交接 — R123

更新：2026-10-06。固定仓库 `thechurchofagi/trinity-accord`；固定分支 `uct-agent-consciousness-workspace`；固定目录 `research/uct-agent-consciousness-workspace/`。

## 当前入口与原样保留的历史

先 fetch 最新 HEAD；若有 R124+，接最新结果，不覆盖或重复。当前检查点为 **R123：已执行测量通道校准与 R122 保留数据审计**，不是 T2 闭合或重大实证突破。

读取 [R123 报告](records/R123_Measurement_Channel_Audit_20261006/R123_Report.md)、[状态](records/R123_Measurement_Channel_Audit_20261006/STATUS.json)、[实际代码和结果](records/R123_Measurement_Channel_Audit_20261006/README.md)、[下一项具体实验](records/R123_Measurement_Channel_Audit_20261006/NEXT_EXPERIMENT.md)、[来源与阅读范围](records/R123_Measurement_Channel_Audit_20261006/source_ledger.json)。

R122 及此前的原交接全文无损保留在 [HANDOFF_THROUGH_R122.md](HANDOFF_THROUGH_R122.md)，原索引全文无损保留在 [MASTER_INDEX_THROUGH_R122.md](MASTER_INDEX_THROUGH_R122.md)。它们复用 R122 原 Git blobs，未删改；放在相同目录层级，以保持历史相对链接有效。历史内“最新/下一步”不覆盖本入口；仍有效的理论、安全、保存限制继续遵守。R121 总交接位于 `records/UCT_Experience_Intelligence_Cross_Substrate_Master_Handoff_R121_20261006.md`。

## 本轮已完成，不要重复

A 主体论证读取至 §16.1：已验证正式 v1.2，DOI `10.5281/zenodo.23131575`，不是已确认的 v1.3。B 主体论证至 §24：v1.1，DOI `10.5281/zenodo.23030320`。C 主体论证至 §12 及附录 A/B：v1.0，DOI `10.5281/zenodo.23137088`。准确 commit/path/blob 见来源清单。没有虚称读完每个附件；用户所说第四篇医学论文仍未定位，不得用 RLC 数学论文、TA-TR-2026-24 或病人资料冒充。

实际运行两个程序：`measurement_channel_check.py` 与 `retained_data_audit.py`。前者按 R122 的七点半高斯核，独立白输入的相邻相关为 0.6502595392，两个 seed 模拟约 0.6493/0.6495。它校准的是分析通道，不是新的神经实验，不证明大鼠记忆是伪迹。对应原始 spike 支持为目标端点 t 的 [t−250ms,t+100ms)，不能误写为 t 时刻在线可用状态。

后者使用通过原 Git blob 精确校验的全部 12 session 摘要，未重跑原 MAT。5 rat、3,319 trials、32,656 bins。FOF/ADS 等 rat R² 0.0542768811/0.0364488317，最终选择/时间/时长诊断对照 0.2005731897。两个脑区分别在 12/12 session 低于该对照。所有留一 rat 结果保留。单独神经模型输给对照，不等于神经变量加入联合模型后无增量；最终选择是未来结果，该对照不是在线无记忆智能体。测量校准的自预测 R² 与累积证据解码 R² 目标不同，不得相减。

## 下一项工作：直接执行，不再重写计划

仍限定 rat evidence accumulation 一个 domain。对同一试次、mask、fold、神经元，做 baseline-only、neural-only、baseline+neural 的训练外预测比较；原始 50ms spike bins 为主，原七点平滑为敏感性检查。用最大滤波支持固定样本，避免去平滑同时偷偷改变排除规则。回顾性的最终选择对照与真正在线可用预测变量严格分开。该联合模型尚未运行，不得把本轮摘要审计写成其结果。

先尝试恢复 R122 原数据或原始神经特征；失败路线有限尝试后切换，不无限重复下载/制定计划。当前容器 DNS 路线失败；连接器可读仓库，保留摘要路径已成功。历史 R122 完整 Cells.zip 下载已完成，不得重新宣称公开数据 unavailable。

联合预测检验后才进入冻结的 state/input-port/time/output-law 映射与 held-out transition 检验，随后做有依据的 intervention transport。12 个 recording session 无 laser-on trials；B3 仍未独立复算。外部 click、全脑区抑制、投射抑制和 accumulator reset 不互换。C2/C3 仍开放，不把 observational decoding 当机制闭合。

## 理论与证据约束

保留 A v1.2 的 C1/U1 与 ontic/view/estimate/subject 区分。完整 K 和完整 E-type 是身份对；A/I/S/B/R/V 是不同关系或投影，不是体验的同义词。实际智能在 UCT 内不为 experience-free；固定完整比较条件下真正 capability difference 可推出 complete E-type difference；same score/behavior/report 不推出 same E，more intelligence 不推出标量更多/更丰富/更像人体验。访问、自我、报告不设体验存在门槛。经验研究 E 始终 latent，不用 C1 生成标签来验证 C1。

严格区分 T1 功能解离相似、T2 保留干预的机制对应、T3 构成组织同源；selected content 遵循 Anchored Causal Geometry/G1–G4，并与 valence 分离。保留四个深问题：普通现象标签桥、valence/fear、主体边界/组合、C1/U1 外部验证。R91 等既有纠正继续有效。

## 保存与防卡住规则

所有 substantive work 写入固定分支，commit 带 `[skip ci]`，更新 HANDOFF 与 MASTER。每轮提交前核对 HEAD，发现并发先读回合并，禁止 force overwrite。只做必要的轻量保存回读，不因保存反复重算整包。不得为保存开 PR、启动 CI/部署/发布工作流；不关闭全仓库 CI。科学推导需要的实际实验与正确性验证仍执行。

禁止把计划、下载尝试、上传 blob 或包装检查报告为实证完成。下一轮至少交付实际运行、失败或负结果的可核对记录，不能反复以这一轮的校准充当新增重大成果。当前用户总任务未完成，重大成果未宣称；不能保证预先指定的突破或声称无限后台执行。

已发表 A/B/C 与 TA-TR-2026-24 的字节不改，不新增 DOI/Zenodo/OTS/Arweave，不改既有发行侧流程。不操作凭据、真实关闭控制、复制或外部资源获取能力。需要本人处理的登录/验证码由本人完成。保留全部失败、负结果、代码、参数、数据身份和来源实际阅读范围。英文研究正文、中文进展汇报；目标为原创、正确、可复核、长期可发现及未来 AI 可引用，而非论文数量或期刊等级。
