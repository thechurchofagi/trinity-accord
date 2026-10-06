"""Generate reports and exact scientific plots from the executed result files."""
from pathlib import Path
import json, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RECORDS = HERE.parent
ROOT = RECORDS.parent
J = RECORDS / "R124_Observation_Qualified_Neural_Increment_20261006"
ja = json.loads((J / "aggregate.json").read_text())
sa = json.loads((HERE / "aggregate.json").read_text())
ia = json.loads((HERE / "increment_compatibility.json").read_text())

def select(a, channel, region, context=None):
    return next(x for x in (a["contrasts"] if "contrasts" in a else a["results"]) if x["channel"] == channel
                and x["region"] == region and (context is None or x["context"] == context))

def write(p, text):
    p.write_text(text.strip() + "\n", encoding="utf-8")

def joint_table():
    rows = ["| Channel / controls | Region | Baseline R² | Joint R² | ΔR² | Descriptive 95% rat t interval | Positive rats / sessions |",
            "|---|---|---:|---:|---:|---|---|"]
    for channel, context in [("delayed_raw","retrospective"),("delayed_filtered","retrospective"),
                             ("delayed_raw","retrospective_recent"),("online_raw","online_recent"),
                             ("online_filtered","online_recent")]:
        for reg in ("FOF","ADS"):
            x = select(ja,channel,reg,context); e = x["equal_rat"]; ci = x["descriptive_95_t_interval"]
            rows.append(f"| {channel} / {context} | {reg} | {e['baseline_r2']:.6f} | {e['joint_r2']:.6f} | {e['delta_r2']:+.6f} | [{ci[0]:+.6f}, {ci[1]:+.6f}] | {x['rats_positive']}/5; {x['sessions_positive']}/12 |")
    return "\n".join(rows)

write(J / "R124_Joint_Model_Report.md", f"""
# R124-J — Observation-qualified neural incremental prediction
Executed 2026-10-06. Independent continuation begun from R123 commit 2f358ac0cb29c4dddc53933fa709ca8aec03be1f; the concurrent R124 transition audit remains intact in its separate directory. R124-J is a naming qualifier, not a new cohort.

## Result
All 12 pinned rat recording sessions were actually fitted: 5 rats, 3,319 trials, 32,656 held-out bins. The raw neural increment beyond the retrospective choice/time/duration baseline is small: FOF ΔR² = +0.007603643, ADS +0.002197713. Both descriptive five-rat intervals cross zero. FOF improves in only 1/5 rats, and removing A297 changes its equal-rat gain to −0.004003324. This is weak finite predictive evidence, not an identified biological accumulator.

The stronger recent-input controls reduce the delayed raw increments to FOF +0.002741273 and ADS +0.000076482. The explicitly online raw setting has FOF +0.012144895 and ADS +0.008921495; those descriptive intervals also cross zero. No favorable session or negative score was discarded.

{joint_table()}

## Cohort, measurement, and validation
The source is the complete Cells.zip from Figshare article 30369064 version 1, file 58773835: 1,929,137,550 bytes, official MD5 3b0ab5c964fb492ec36ee0f55a5d53de, SHA-256 e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494. All twelve extracted MAT hashes match the pinned R122 manifest. MacOS AppleDouble files are not recording sessions.

Reuse the original eligible-trial definition, maximum delayed-filter gap support, five contiguous whole-trial outer folds and three whole-trial inner folds. Firing-rate qualification is training-only; FOF/ADS matching uses the original seed 122 and selected identities. Raw and filtered channels use the same rows and neuron identities. The additional online support audit excluded zero rows; all four channels have 32,656 rows. A294 selected identities also match the archived original R122 folds.

Raw bins contain integer spike counts divided by 50 ms. Delayed raw support is [t+50 ms,t+100 ms); delayed seven-tap filtered support is [t−250 ms,t+100 ms). These are retrospective estimates of e_t. Online raw support is [t−50 ms,t); online filtered support is [t−350 ms,t). The online channels contain no spikes after t. An online observation window does not itself identify biological processing latency or a sufficient Markov state.

The retrospective baseline contains intercept, eventual right choice, time, time squared, their choice interactions, and realized duration. It deliberately uses future information and cannot be presented as an online agent. Its held-out equal-rat R² exactly reproduces the R123 diagnostic 0.20057318974711028. The online baseline instead uses intercept, time, time squared, current signed click count, its time interactions, and current total click count. It has no future duration or choice predictor. This baseline omits the full input history, which would already determine the external cumulative target exactly.

## Estimator and controls
The frozen protocol specifies partial ridge with unpenalized baseline terms, training-only residualization and scaling, a mean-MSE ridge grid including an infinite-penalty baseline-only option, and nested tuning. This is a declared estimator change from the R122 Lasso; the new neural-only scores are not an exact replication of its decoder. A model trained with more covariates can still have worse held-out performance.

A held-out mismatch diagnostic swaps whole neural trajectories within an outer test fold, exact bin-count/choice strata, and four chronological blocks. Seeds 1241/1242/1243 are fixed. Donor identities, moved fractions, and scores are retained. It is a pairing diagnostic, not a permutation p-value or an internal neural intervention. Matching by eventual choice in that diagnostic does not put choice into the online fitted predictor.

Session metrics are averaged within rat and then across rats equally. The five-rat t intervals describe these animals; they are not confirmatory population tests. All leave-one-rat-out results are in aggregate.json.

## Recovery and failure history
The first shared signed-URL download attempt failed. Fresh per-range public redirects enabled recovery. Four short ranges caused an initial assembly to fail size and checksum; only those ranges were replaced before accepting the full verified archive. Preserve data_access_failures.json and archive_first_assembly_failure.json.

The X062 2020-03-20 local extracted MAT later failed its source hash and loader before fitting. It had fewer bytes than the verified archive member; the reason for the local truncation is unknown. Re-extraction from the verified archive restored the exact source hash, and only that missing session was fitted. A subsequently zero-byte X087 2021-07-25 prediction file was reconstructed from already saved features and frozen coefficients, without refitting; its metric replay agreed to 1.11×10⁻¹⁶. Preserve the first-pass failure, repair scripts/logs, single-session repair and prediction-repair records. First_Pass_11_Sessions_Aggregate.json is historical; aggregate.json contains the accepted full twelve-session result.

An independent augmented least-squares construction checks the partial-ridge solver (maximum discrepancy about 3.6×10⁻¹⁴). Saved-artifact digests pass; all trial partitions are disjoint; the original OOF R² summary check differs by at most 2.15×10⁻¹⁶. The complete checks are in software_checks.json and independent_result_checks.json. A later independent audit of saved R² and absolute MSE differs by at most 2.84×10⁻¹⁴ and is reproducible through R125 audit_saved_results.py. These are software/data-integrity checks, not biological proofs.

## What this advances
The executed comparison closes the R123 missing-joint-model task on this cohort. It does not infer conditional mutual information from ΔR², identify complete K, measure E, transport an intervention, or close T2. UCT III Appendix B motivates conditional contribution but supplies no license to convert a weak ridge increment into experience evidence. The next executed test freezes the already fitted observable maps and examines state/input/time/output-law correspondence in R125.
""")

write(J / "README.md", """
# R124-J executed artifacts
Start with [report](R124_Joint_Model_Report.md), [frozen protocol](PROTOCOL_FROZEN.md), [aggregate](aggregate.json), [independent checks](independent_result_checks.json), and [software checks](software_checks.json).

joint_decode.py is the actual executed decoder implementation; requirements.txt and environment.json pin the runtime. recover_cells.py documents source recovery. All twelve per-session feature NPZ files, model JSON.gz files, prediction CSV.gz files and summaries are retained. These are derived real-data artifacts, not sample or synthetic input. Original full MAT bytes are retrieved through the public archive and its pinned R122 identities.

From this directory, python3 joint_decode.py --data /absolute/path/to/Cells runs the full source-based fit on the verified archive members. Set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1 to reproduce the constrained runtime. The retained matrices and models allow R125 to run without another download or decoder fit.

The recovery and reconstruction scripts are preserved as history. They use the original scratch data location and require adapting that location on a new machine. First_Pass_11_Sessions_Aggregate.json and the failure logs remain historical; aggregate.json is the final twelve-session result. See SHA256SUMS for accepted artifact hashes.
""")

def transition_table():
    rows=["| Online raw region | Unit update MSE | Persistence MSE | Training constant MSE | Free ARX MSE | Unit update worse: rats / sessions |",
          "|---|---:|---:|---:|---:|---|"]
    for reg in ("FOF","ADS"):
        x=select(sa,"online_raw",reg);e=x["equal_rat"]
        rows.append(f"| {reg} | {e['observed_accumulator_mse']:.6f} | {e['observed_persistence_mse']:.6f} | {e['observed_constant_mse']:.6f} | {e['observed_ARX_mse']:.6f} | {x['rats_accumulator_worse_than_persistence']}/5; {x['sessions_accumulator_worse_than_persistence']}/12 |")
    return "\n".join(rows)

def increment_table():
    rows=["| Channel | Region | Increment skill SΔ | corr(ΔD,u) | Positive rats / sessions |",
          "|---|---|---:|---:|---|"]
    for ch in ("online_raw","online_filtered","delayed_raw","delayed_filtered"):
        for reg in ("FOF","ADS"):
            x=select(ia,ch,reg)
            rows.append(f"| {ch} | {reg} | {x['equal_rat_skill']:.6f} | {x['equal_rat_correlation']:.6f} | {x['rats_positive_skill']}/5; {x['sessions_positive_skill']}/12 |")
    return "\n".join(rows)

write(HERE / "R125_Report.md", f"""
# R125 — A frozen observed-state candidate fails accumulation-transition and shared-output tests
Executed 2026-10-06. Exploratory real-data continuation of R123/R124-J, with protocol and maps frozen before these scores. This is not a blind preregistration or independent replication.

## Finding and decision
On 12 real recording sessions from 5 rats, 29,337 adjacent held-out within-trial transitions and 3,319 held-out trial endpoints were evaluated. The selected no-future, unsmoothed neural-only ridge coordinates do not behave as unit-gain accumulator states. In both FOF and ADS, the fixed update D(n_t)+u_(t+1) predicts the next observed D(n_(t+1)) worse than persistence in 12/12 sessions and all 5 rat means. All filtered/delayed sensitivities retain that direction.

Retire this point-decoder candidate as a shortcut to a T2 mechanism certificate. The scoped negative finding concerns these frozen observable maps. It does not refute a latent biological accumulator, prove that either region lacks accumulation, falsify UCT C1/U1, or identify biological transition kernels. C2 at the latent mechanism level remains unidentified; C3 is not tested; T2 remains OPEN.

## The executed correspondence candidate
State: D is the R124-J neural-only outer-training partial-ridge map, expressed in the external signed-click coordinate. It uses intercept and neural variables only, with no eventual choice, realized duration or context baseline. Each held-out trial uses its own outer-training map. No new decoder was fitted, no held-out map was rescaled to favor commutation, and all five original outer folds remain whole-trial disjoint.

Input/port: u_(t+1) is the actual signed right-minus-left click increment in the next 50 ms bin. This is an exogenous supplied input; it is not an identified internal reset, projection inhibition or whole-region perturbation.

Time: primary online raw spike support is [t−50 ms,t), available at t. Online filtered sensitivity uses [t−350 ms,t). Delayed sensitivities are physically available at q=t+100 ms while estimating e_t. Relabeling q does not eliminate the in-flight input buffer or identify a Markov state; these sensitivities cannot by themselves certify time/port commutation.

Artificial update: U(a,u)=a+u in signed-count units, with unit gain fixed. This is a simple calibrated algorithmic accumulator, not a frontier-model or R117 decision-noise experiment. External e_(t+1)=e_t+u_(t+1) was checked exactly for all paired rows; that tautological count identity is only an input-coordinate sanity check.

## Observed-state transition result
The held-out target here is the next observed decoded state, not the next external count. All predictions use the same pairs. Persistence, reset/recent-only, a training constant, and a free ARX fitted only to outer-training observed trajectories are retained.

{transition_table()}

The unconstrained ARX predicts this observable target better than the unit update, but fitting it neither identifies a biological kernel nor passes C2. Its training states use a map fitted on that outer training set; its scores are diagnostic comparisons, not an independently cross-fitted discovery of mechanism.

The external-next-count comparison is a different target. Primary online raw fixed-update MSE is 100.373869 for FOF and 101.324310 for ADS, versus 104.743455 for recent-only. The small improvement does not cancel the failed observed-state update, and those MSEs must not be subtracted from the observed-state MSEs.

## Compatibility with the concurrent R124 metric
After reading the concurrent R124 report, a separately labeled secondary calculation reused the already saved transition table without refitting. It computes SΔ = 1 − mean[(D_next−D_current−u)²] / mean[u²] for each session, then equal session means within rat and equal rat means. Its denominator is the zero-predicted input-increment loss; it is not the observed-state variance or observed persistence loss.

{increment_table()}

The concurrent R124 audit used the original R122 filtered Lasso OOF states and reported FOF SΔ = −0.475567 and ADS −0.351133. R125 uses freshly executed R124-J ridge maps plus raw/no-future channels; these are related negative checks on the same animals, not interchangeable estimators or added independent animals. The secondary compatibility script was run after the concurrent report was read, and is not mislabeled as a frozen primary analysis.

## Shared output law
For each outer fold, fit one unpenalized logistic law P(right|a)=sigmoid(b0+b1*a) to actual outer-training endpoint external evidence and choices. Transport exactly the same intercept and slope to the neural state on held-out trial endpoints. No separate biological recalibration is fitted. The endpoint is the last eligible 50 ms target within the trial, not a guarantee that every late click has been included.

| Online raw state passed to shared law | Equal-rat log loss, nat/trial |
|---|---:|
| External count algorithmic state | 0.595439 |
| FOF decoded state | 0.674542 |
| ADS decoded state | 0.686178 |
| Outer-training choice-frequency prior | 0.698839 |

The transported state under this shared law is worse than the external count state in 5/5 rat means for each region. Its average improvement over the prior is predictive information under this chosen law, not law equivalence, a mechanism certificate, or evidence of experience. Filtered/delayed law scores are retained in aggregate.json; none equals the external-count reference.

Optimization gradients were checked against the execution tolerance; per-fold success flags, iteration counts and gradients are retained rather than silently treating every optimizer status as identical. The frozen OOF maps replay the saved predictions with maximum absolute discrepancy {sa['max_OOF_replay_error']:.4g}. Feature/model/source identity checks gate every session before analysis.

## What is and is not rejected
The rejected operational candidate is the selected noisy point estimate D(n) with unit-gain input and supplied 50 ms clock. Differencing spike-derived estimates amplifies observation noise; ridge shrinkage, omitted neurons/regions, biological processing latency, time aggregation and an unmodeled in-flight input buffer can break pointwise commutation even when some latent dynamics accumulate evidence. A complete causal state cannot be asserted from predictive decoding alone.

The result therefore narrows an attempted mapping. It supports stopping repeated favorable decoder/offset searches on these held-out records. It does not warrant the universal conclusion that no biological–algorithmic mapping exists. A latent stochastic observation/transition model would need independent causal grounding and validation before its kernel could be transported.

## T2 certificate scope
| Clause | Current status | Supported scope |
|---|---|---|
| C0 | LIMITED_PASS | Shared externally defined signed-click input coordinate only. |
| C1 | PARTIAL / UNIDENTIFIED | Weak finite predictive readout; complete constitutive state not identified. This certificate clause is distinct from UCT axiom C1. |
| C2 | FAIL_SCOPED for selected D; latent kernel UNIDENTIFIED | Unit-update observable candidate fails all rat means; no complete biological kernel. |
| C3 | NOT_TESTED | No matched internal intervention outcomes in the twelve recording sessions. |
| C4 | PARTIAL | Observation supports and availability declared; biological delay/buffer and clock correspondence unresolved. |
| C5 | PARTIAL / FAILED selected shared-law equivalence | Held-out law transport scored; selected neural coordinate does not reproduce the count reference. |
| C6 | PROCEDURAL_ONLY | Source, fold, coefficient and result replay; no global intervention-preserving isomorphism. |

E remains latent. T1 functional analogies, T2 mechanism correspondence and T3 constitutive homology remain distinct. No G4 selected-content closure, qualia label, valence/fear measurement, subject-boundary solution or external C1/U1 validation is claimed. Published A/B/C bytes remain unchanged.

## Next work justified by these results
Stop treating another positive decoding score or a new toy theorem as closure. The current evidence excludes certifying these point maps; it leaves a causal identification problem. A next empirical study must first specify an independently supported observation model, biological latency/in-flight input representation and candidate sufficient state; freeze the fitted laws; then test held-out innovations and transition/output predictions under the same support. A stochastic latent model that merely optimizes these same scores would not solve identification.

C3 requires relevant biological perturbation data and a physically justified map from that perturbation to the algorithmic operation. Natural clicks, artificial click insertion, whole-region inhibition, projection inhibition and accumulator reset remain separate operations. The concurrent R124 ledger notes a clinical visual-stimulation dataset as a possible separate domain; its first-party article/data were not reread or analyzed in R125 and it does not replace the unidentified fourth UCT medical manuscript. Do not splice a visual-content intervention into the rat signed-evidence certificate.

## Execution, preservation, and concurrency
The full source recovery, raw/filtered joint fits and failures are documented in the R124-J report. This R125 study executes on the saved real feature matrices and frozen maps, so future replay does not require another Cells.zip download. The exact protocol, code hashes, run log, paired per-transition tables, endpoint output tables, ARX/shared-law parameters and summaries are retained. Secondary increment compatibility is separately recorded. The independent audit_saved_results.py replay recalculates transition MSE and endpoint log loss from all saved tables with maximum discrepancy 3.56×10⁻¹⁵, confirms no duplicate test pairs/endpoints, and does no refitting; see saved_result_audit.json.

Concurrent branch commits through f2f34ca5f5a9738659780729c8a7e8aefe01dbf3 and the R124_Transition_Commutation_Audit_20261006 directory were read and are preserved. The source/concurrency ledger distinguishes direct reading, inherited reading and external material not verified here. New files use distinct directories. HANDOFF.md and MASTER_INDEX.md point to R125 while their R123 versions are preserved byte-for-byte at the same directory level.
""")

write(HERE / "README.md", """
# R125 executed frozen-map correspondence test
Read [report](R125_Report.md), [protocol](PROTOCOL_FROZEN.md), [certificate](T2_Certificate.csv), [status](STATUS.json), [aggregate](aggregate.json), and [source/concurrency ledger](source_and_concurrency_ledger.json).

state_correspondence.py is the executed primary and declared sensitivity implementation. increment_compatibility.py is the separately labeled post-concurrency compatibility calculation. All twelve transition CSV.gz files, endpoint output CSV.gz files, per-fold calibration JSON.gz files and session summaries are retained. R124-J supplies the preserved real feature matrices and frozen models.

Replay from this directory: python3 state_correspondence.py, then python3 increment_compatibility.py. Use the R124-J requirements.txt runtime and OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1. This replay does not need the original MAT archive or fit new decoders. Run generate_reports.py to regenerate the reports and exact summary figures from saved results. See SHA256SUMS for artifact integrity.

The selected observable candidate fails; latent biological kernels and C3 interventions remain unidentified. No experience label is present in this analysis.
""")

cert = [
    ["clause","status","scope"],
    ["C0","LIMITED_PASS","external signed-click coordinate only"],
    ["C1","PARTIAL_UNIDENTIFIED","weak readout; complete biological state not identified; not UCT axiom C1"],
    ["C2","FAIL_SCOPED_LATENT_UNIDENTIFIED","frozen point-map unit-update candidate fails; latent kernel unidentified"],
    ["C3","NOT_TESTED","no matched internal intervention outcomes"],
    ["C4","PARTIAL","support availability audited; biological delay and in-flight buffer unidentified"],
    ["C5","PARTIAL_SELECTED_LAW_EQUIVALENCE_FAILED","shared-law held-out scores weaker than count reference"],
    ["C6","PROCEDURAL_ONLY","replay and source identities; no global mechanism isomorphism"],
    ["T2","OPEN","no intervention-preserving biological-algorithmic mechanism correspondence"],
]
with (HERE/"T2_Certificate.csv").open("w",newline="") as f:
    csv.writer(f).writerows(cert)
status={"checkpoint":"R125","execution":"COMPLETED_AND_AUDITED","sessions":12,"rats":5,
        "trials":3319,"held_out_bins":32656,"within_trial_transitions":29337,
        "selected_point_map_candidate":"FAIL_SCOPED","latent_biological_kernel":"UNIDENTIFIED",
        "C3":"NOT_TESTED","T2":"OPEN","E_measured":False,"major_consciousness_breakthrough_claimed":False,
        "previous_remote_head_read":"f2f34ca5f5a9738659780729c8a7e8aefe01dbf3",
        "concurrent_R124_preserved":True,"all_negative_results_retained":True}
write(HERE/"STATUS.json",json.dumps(status,indent=2,ensure_ascii=False))

write(RECORDS/"UCT_Cross_Substrate_R125_Executed_Raw_Data_Handoff_20261006.md", """
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
""")

# Exact scientific figures; no generated imagery or invented data.
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                     "axes.spines.right":False,"axes.titleweight":"bold"})
fig,ax=plt.subplots(1,3,figsize=(14.5,4.6),gridspec_kw={"width_ratios":[1.05,1.15,1]})
colors={"FOF":"#237AAB","ADS":"#BA4769"}
for k,reg in enumerate(("FOF","ADS")):
    x=select(ja,"delayed_raw",reg,"retrospective")
    y=np.array(list(x["rat_contrasts"].values()))
    ax[0].scatter(k+np.linspace(-.13,.13,len(y)),y,color=colors[reg],s=40,label=reg)
    mean=x["equal_rat"]["delta_r2"];ci=x["descriptive_95_t_interval"]
    ax[0].errorbar(k,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt="D",color="#222222",capsize=5,ms=6,zorder=4)
ax[0].axhline(0,color="#777777",lw=1,ls="--");ax[0].set_xticks([0,1],["FOF","ADS"])
ax[0].set_ylabel("Joint minus baseline held-out R²")
ax[0].set_title("A  Small, unstable neural increment",loc="left",fontsize=11)
ax[0].text(.02,.98,"Raw delayed / retrospective controls\nDots: five rats; diamond: mean ± descriptive t interval",transform=ax[0].transAxes,va="top",fontsize=8)
ax[0].set_ylim(-.035,.085)
for k,ch in enumerate(("online_raw","online_filtered")):
    for j,reg in enumerate(("FOF","ADS")):
        x=select(ia,ch,reg);y=np.array([v["increment_skill_vs_zero"] for v in x["rat_records"]])
        xpos=k+(j-.5)*.28
        ax[1].scatter(xpos+np.linspace(-.05,.05,len(y)),y,color=colors[reg],s=35,label=reg if k==0 else None)
        ax[1].plot(xpos,x["equal_rat_skill"],"D",color="#222222",ms=6)
ax[1].axhline(0,color="#777777",lw=1,ls="--");ax[1].set_xticks([0,1],["Raw","Filtered"])
ax[1].set_ylabel("Increment skill SΔ (reference: ΔD = 0)")
ax[1].set_ylim(-3.8,.4)
ax[1].set_title("B  No-future point maps fail",loc="left",fontsize=11)
ax[1].legend(frameon=False,fontsize=8,loc="lower right")
ax[1].text(.02,.98,"Same five rats; 29,337 within-trial pairs\nAll rat means < 0",transform=ax[1].transAxes,va="top",fontsize=8)
fof=select(sa,"online_raw","FOF")["equal_rat"];ads=select(sa,"online_raw","ADS")["equal_rat"]
values=[fof["output_external_logloss"],fof["output_transported_logloss"],ads["output_transported_logloss"],fof["output_prior_logloss"]]
ax[2].bar(np.arange(4),values,color=["#3B856A",colors["FOF"],colors["ADS"],"#90969F"],width=.65)
ax[2].set_xticks(range(4),["Count","FOF","ADS","Prior"])
ax[2].set_ylabel("Held-out log loss (nat/trial; lower is better)")
ax[2].set_ylim(0,.80)
for k,v in enumerate(values):ax[2].text(k,v+.015,f"{v:.3f}",ha="center",fontsize=9)
ax[2].set_title("C  Shared output law does not transport",loc="left",fontsize=11)
fig.suptitle("R125: real rat recordings narrow a candidate correspondence",fontsize=15,weight="bold",y=1.02)
fig.text(.01,-.015,"12 sessions / 5 rats / 3,319 trials. Same animals across panels. E is not measured; C2 latent kernel unidentified, C3 not tested, T2 open.",fontsize=9,color="#333333")
fig.tight_layout(w_pad=2.0)
fig.savefig(HERE/"R125_Summary.png",dpi=180,bbox_inches="tight")
fig.savefig(HERE/"R125_Summary.pdf",bbox_inches="tight")
print(json.dumps({"reports_generated":True,"figure":str(HERE/"R125_Summary.png")}))
