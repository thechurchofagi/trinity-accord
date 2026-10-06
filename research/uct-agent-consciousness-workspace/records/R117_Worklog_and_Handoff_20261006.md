# R117 工作记录与交接 — 第一套真实cross-substrate evidence-accumulation实验

日期：2026-10-06。

选定Gupta et al. Neuron 2026 rat evidence-accumulation系统，数据Figshare DOI 10.6084/m9.figshare.30369064.v1，公开1.8GB Cells.zip、12个MATLAB sessions；作者代码Brody-Lab/fof_ads_interactions main commit 39d056fb12f688034b543d9ac8b7406a58ad0f77。

生物公开事实：左右随机clicks需跨时间累积；FOF/ADS都编码/解码accumulator value并双向通信；FOF->ADS projection silencing影响积累期行为；nonselective FOF silencing较robust；作者RNN用multi-scale recurrence解释。代码明确分析whole-trial/first-half/second-half perturbations。

raw数据下载当前被执行环境阻塞：Figshare稳定文件ID58773835会重定向短时效S3，当前binary downloader未成功。因此绝不声称已复算raw neural trials。冻结最小B1-B3：psychophysical temporal kernel、FOF/ADS cumulative-evidence decoding、whole/first/second-half opto signature。

AI侧已经实际运行matched sequential evidence experiment：
seed117；60k trials，tie-filter后59571，10 bins。
full accumulator accuracy0.984858；
last-sample control0.717329；
midpoint reset0.930671。
full kernel 10 bins全部约2.0–2.17；
last-sample前9 bins约0、bin10=1.997；
midpoint reset前5约0、后5约2.17–2.22。
noisy state对cumulative evidence R²从0.917升到0.9985。
+1 grounded evidence pulse：full accumulator任何bin choice-prob effect均0.007923；midpoint reset前5精确0、后5均0.020651。

当前跨底物等级：
T1 functional support-pattern similarity STRONG；
T2 intervention-preserving correspondence PARTIAL/PROMISING；
T3 constitutive homology NOT ESTABLISHED。

关键grounded variable是cumulative click history H_t；后续如果raw数据拉取成功，直接在同一H_t空间做biology↔AI anchored causal geometry，不从qualia词开始。

下一步R118优先解决B1-B3原始数据复算；若二进制通道仍不行，用作者GitHub内optodata_FOFSTR.xlsx和公开derived aggregates做明确标记的derived-data reanalysis。
