# R122 工作日志与跨窗口交接 — 真实 rat B1/B2 已完成

日期：2026-10-06。固定仓库 `thechurchofagi/trinity-accord`，分支 `uct-agent-consciousness-workspace`，目录 `research/uct-agent-consciousness-workspace/`。

## 最新状态：先读这里

**Cells.zip 已完整取得并校验；12 个真实 recording session 的 B1/B2 已全部执行并通过独立复核。T2 仍未闭合。** 不要再把公开数据写成 unavailable，也不要重新执行 R117 AI 或增加 toy theorem 充当下一轮。

本轮开始与中途 fetch 的 HEAD 均为 `ab02cb6ea51442aa434bdfbe3ef69d52d2877996`，当时无 R122+。本次为 R122；未来窗口必须先 fetch 新 HEAD，若已有更新轮次，接最新结果。本交接不在自己的内容中硬编码包含自身的最终 commit SHA；以承载这些文件的 Git 提交为准。

先读：

1. [R122 主报告](R122_Real_Rat_B1_B2_and_Open_T2_Certificate_20261006.md)。
2. [完整可复算材料 README](R122_Biology_B1_B2_20261006/README.md)、[独立审计](R122_Biology_B1_B2_20261006/independent_review.md)。
3. [T2 七项证书](R122_Biology_B1_B2_20261006/R122_T2_Certificate.csv) 与 [机器可读结果摘要](R122_Biology_B1_B2_20261006/R122_Research_Status.json)。
4. 如需理论背景，再读 [R121 总交接](UCT_Experience_Intelligence_Cross_Substrate_Master_Handoff_R121_20261006.md)、R121 closure matrix、R119 certificate。R121 总交接原字节保留；其中“尚未取得 Cells.zip”的当时状态已被本轮更新。

## 取得的数据与来源

Figshare DOI `10.6084/m9.figshare.30369064.v1`；稳定下载 `https://ndownloader.figshare.com/files/58773835`。本轮 07:29:22 UTC 开始的首个普通流式下载成功，通过 Figshare→signed S3。完整 **1,929,137,550 bytes**，MD5 `3b0ab5c964fb492ec36ee0f55a5d53de` 与 Figshare 相符，SHA-256 `e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494`。

作者代码固定 `39d056fb12f688034b543d9ac8b7406a58ad0f77`。最终 Neuron 论文 PDF 与 supplement 共 38 页成功取得，实际阅读范围和 hash 已入 source ledgers。B1 是本项目独立新增分析；没有找到作者自己的 behavioral temporal-kernel estimator，不能写成复现作者 kernel。

原始 12 MAT、5 rats、5,230 trials、3,014 raw units；B1 3,344 trials（45 ties 保留）；B2 3,319 trials、32,656 held-out time bins。全部完成、没有拟合失败或收敛警告。

原始大文件临时路径是 `/workspace/scratch/42800b14a096/data/Cells.zip` 与 `data/rat_sessions/Cells_upload/`，跨窗口不保证仍存在。**Git 中保存了 downloader、校验值、schema、全部派生 trial/prediction/fold/结果，而不是把临时路径当唯一档案。** 文件失效时按 README 从相同版本重新下载，不要重复追查此前的 redirect blocker。

## 本轮最重要的结果

### B1：主比较不确定，预定 total control 方向一致

四模型共同 nuisance、训练内 scaling、5 个连续 whole-trial folds、相邻训练 trial purge，先 session 内计算，再同 rat 平均，最后 5 rat 等权。

| 模型 | held-out log loss ↓ | 对 observed rat choice 的预测准确率 |
|---|---:|---:|
| full10 | 0.587307 | 0.710356 |
| lastbin | 0.606539 | 0.678490 |
| total | 0.562148 | 0.725328 |
| nuisance | 0.691398 | 0.561456 |

预定主比较 full10−lastbin 的 loss 改善 **0.019232**，五 rat 描述性 t 区间 **[−0.031799, 0.070263]**；A294/A297 更差。不能宣布主比较成功。

预定 total−lastbin control 改善 **0.044391**，区间 **[0.005989, 0.082794]**，12/12 session、5/5 rat 同方向。full10 在 11/12 session 不如 total。结论是较完整历史摘要在该模型类中更有预测信息，不是每个 trial 都理想连续积分或平坦 kernel 的证明。902 条长时程 trial 的绝对时间敏感性已完成，早期权重不确定性保留。

### B2：可解码性较弱、异质，负结果全部保留

50 ms bins、明确 100 ms lag、因果 half-Gaussian σ75 ms、刺激期内观测、5×3 连续 whole-trial nested folds；训练内 FR>1Hz、两区域 neuron-count matching、scaler；Lasso 固定 alpha grid，seed122。

| 指标（rat 等权） | FOF | ADS |
|---|---:|---:|
| held-out Pearson r | 0.184790 | 0.136561 |
| held-out R² | 0.054277 | 0.036449 |
| 同时间/同选择中心化的描述性 r | 0.049238 | 0.042104 |

24 个 session-region R² 有 8 个负值。FOF−ADS r 差 0.048229，描述性 cluster-bootstrap 区间 [−0.031930, 0.128388]，不能证明稳定区域优势，也不能证明等价。

本方法与作者 Figure 2C 同时在验证单位、预处理、平滑、lag、时间域及 population selection 等方面不同，是独立保守重分析。不能把低分唯一归因于作者某一实现，也不能据此说论文被推翻。eventual-choice nuisance control 不可当在线 accumulator；中心化相关不可冒称独立 nuisance-adjusted predictive R²。

### 关键 schema 与负结果

- stateTimes 是 absolute session clock；clicks 去共同 stereo onset；不能再加 cpoke_in。
- `recorded` 在7个session有、5个缺失；缺失不等于观测全有效。
- A294 54units有3,956 NaN spikes；按有限邻接括界保守排除B2原始rows203/204/205/208/210。括界不是已证实掉线区间。
- 另20trial不满足完整lagged window；A297有40eligible trial缺失cpoke_out，仍限制到stimulus结束并披露未验证的退出条件。
- 两个X087实际刺激超过1秒，保留真实时间。
- 12session的laser.isOn全部为0。**B3未独立复算；309 registry raw rows/222 retained sessions只是R118既有registry结果。**

## 独立复核、代码与失败

另一个执行者直接从 raw MAT 重建全部 B1 33,440 evidence features、3,344 histories 和 B2 32,656 targets；核验全部folds、purge与输出指标。B1首fold四模型独立重拟合误差≤1.12e−16；B2 378项神经rate手工复算误差≤2.14e−14Hz，训练scaler和读出核验通过。审计只支持计算正确性，不把它当生物机制证明。

执行代码SHA-256：

- `rat_cells.py`: `21a84a802ded32bb73d59316332c838ff84b4e5a14e6363d975b09db39009ca4`
- `b1_kernel.py`: `776e7e92a130bc9b29235f8382541d5b65398779d85f1c01e109f87027fdafd7`
- `b2_decode.py`: `7db8c365282f3560eee07c39d2cf460f854b5af4c70608b949d0e8dcf34b610a`

这些代码在接受的运行中一致，不能修改后仍冒称相同执行hash。协议为本地结果前冻结，不是external preregistration。whosmat/opaque字段失败、严格NaN拒绝、recorded假设错误、npx-utils 404等均保留在source/review ledgers。没有为了得到有利结果重调参数或重跑更多变体。

## T2证书与实际下一步

**C0仅外部task coordinate通过；C1/C2/C3/C4/C5/C6均未达到完整要求。T2_NOT_CLOSED，T3/G4_NOT_ESTABLISHED。**

新blocker是 biological state/transition identification 与 intervention transport。下一轮仍限定同一 accumulation domain：先明确候选因果状态、实际部件/端口、时间对应和接受误差；若必须分离作者/R122方法差异，只做预先声明的窄范围单因素敏感性，不按分数选获胜pipeline。干预证书还需可独立审查的trial-level perturbation behavior。不得把FOF→ADS持续抑制、整个FOF抑制、AI瞬时reset和+1外部pulse混作同一干预。

R117 的59,571 synthetic trials、accuracy、state-noise R²、pulse profile沿用既有结果，不与本轮choice-prediction accuracy/neural-CV R²直接比值或排名。直接代码回读确认：其R²为`r2_score(cum, cum + N(0,1))`，没有训练decoder/held-out验证；accuracy使用Gaussian decision noise σ3，pulse probabilities使用sigmoid temperature3，两套读出律不能在下一步C1/C3校准中默认同一个Y。没有新增AI运行。本轮在用户要求的B1/B2完成并更新证书后停止，不扩展领域。

保持R121理论澄清：UCT内complete K与complete E-type为C1身份对；A/I/S/B/R/V不同；realized I在U1/C1下experience-bearing。在固定完整比较条件、实际过程边界及共同完整K签名下，genuine capability difference可推出complete E-type difference；不能据此推出体验类型细化、标量增强或更接近人类体验。same I/B/R和more I不推出same/more E；self/access/report不是存在gate。AI实证E始终latent。T1/T2/T3、G1–G4与content/valence分别标注。decoder分数自身不构成跨底物G2 geometry对应；弱解码不证明无体验/无causal support，强解码不证明causal use。

深问题只保留四项：selected structural homology→ordinary phenomenal labels；valence/fear bridge；unified subject/bearer boundary/composition；C1/U1外部验证与可证伪性。

保存继续遵守：每轮更新HANDOFF/MASTER，固定分支commit带`[skip ci]`，fetch并合并并发提交、禁止force overwrite。已发表A/B/C与TA-TR-2026-24未动；不为研究checkpoint创建DOI/论文发行/CI/部署。
