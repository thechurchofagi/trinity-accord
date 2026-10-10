<!-- CTD_FINAL_PRESERVATION_COMPLETE:2026-10-10 -->
## CTD DOI → OTS → Arweave 最终完成｜2026-10-10

本篇固定公开版本已经完成全链路存证。DOI 为 `10.5281/zenodo.23279189`。269,961字节正式 PDF 的 SHA-256 为 `479b4f2403ad7416f99f7676533fd4a8b9efed1bb289c7fcd52f64a09bf81c94`；升级后的 OTS 证明为3,843字节，SHA-256 `640be99b62a1c2689b836496199d26097c7deabc92e5b12b2b9fda583787291d`，已在 Bitcoin 高度970752、970753、970754通过远程区块头验证。

Arweave 交易为 `6pOSf4PK21Ot3lti8wYDvyL2KUXVC3zCaz1X72zjfBA`，记录费用0.006818438011 AR；370,493字节载荷 SHA-256 为 `5104443441dde47e6185b24735e5596b292d433d8a4a48b6e535e6480b938e4c`。上传后的初始公开网关回读尚未传播，工作流随后只恢复同一交易，没有再次付款；最终工作流和独立匿名 HTTP GET 均逐字节通过。独立核验还解码并检查了全部6个 base64 成员，确认包内正式 PDF 与 OTS 证明等于冻结原件。前三次空体回读失败作为历史保存在 `operations/ROOT_ARWEAVE_READBACK_ATTEMPT_*.json`，最终成功收据为 `operations/ROOT_ARWEAVE_READBACK.json`。

最终固定批次原字节位于 `operations/final_preservation_batch/`；全链路收据为 `FINAL_CHAIN_RECEIPT.json`；中文成果与操作交接为 `PUBLICATION_COMPLETION_ZH.md`；完整交付包的构建回执为 `operations/PUBLICATION_AND_PRESERVATION_BUNDLE_RECEIPT.json`。早期 `PERSISTENCE_RECEIPT.json`、pending 检查点和失败记录保持原样。

此次仅完成既有固定论文版本的发表存证，不新增科学主张。当前 A3V20261010 科研主线、`CURRENT_STATE.json` 的 next_priority、UCT-MAP-v1.1.2、C1/U1、体验桥接 OPEN 状态及所有禁用证据节点均未改变。预印本和链上存证不等于外部同行评议、人体内部机制识别、UCT 验证或 AI 意识证明。

---

<!-- CTD_CONTINUATION_CHECKPOINT:2026-10-10_WAITING_SIX_CONFIRMATIONS -->
## CTD 存证续办检查点｜2026-10-10

本篇 DOI `10.5281/zenodo.23279189` 已公开。10:57 UTC 新检查确认：批次顶层 `WAITING`，PDF 为 `PENDING_BITCOIN`；没有 AR paid-intent、交易回执或上传包。第二轮20分钟以内的既有日历查询已停止，Alice/Bob 报告等待六次确认，`.ots` 中仍无 Bitcoin heights。独立交易状态查询只作为链上背景保存，不代替证明。main scheduler 为 active。

本篇专用存证收尾任务已实际启用；后续读取 `records/CTD20261010_Noise_Identifiability_v10/operations/CONTINUATION.md`、当前 release 批次及实际回执接续。独立 AR 回读脚本已完成静态审阅，但尚无真实 AR 交易可执行；完成版 ZIP 构建器也保持未执行。科学定稿、原始 pending 历史、当前 A3Q 主线与 next_priority 均保持原样。

<!-- CTD_OPS_CHECKPOINT:2026-10-10_INITIAL_OTS -->
# CTD v1.0.0 发表与首次 OTS 检查点

截至 2026-10-10T10:36:47.092945+00:00，DOI [10.5281/zenodo.23279189](https://doi.org/10.5281/zenodo.23279189) 及九件公开文件已核验；完整科学提交 `fda7a0ae491c4bf3a7c9bc80ccab38acb3984299` 的248件文件已远端逐件回读。PDF阅读副本与原件21页文字及像素一致；时间戳仍绑定269961字节的公开原件。

**OTS 已取得4份日历回执，当前 PENDING_BITCOIN；Arweave 尚未付款。** 首次证明已保存于 release commit `df37353d5153e981caae4017cae1fc12677e085d`；main PR1261已合并，既有小时流程会在验证Bitcoin后依原预算与去重门进入AR。工作流success仅表示本轮检查/保存成功。完整链路收据尚未产生，准备中的报告和构建器不能当完成证据。

此次是操作保存，不改变 A3O 科学主线、next_priority、UCT-PUB-v1.0.31、全部禁用候选或OPEN。当前状态详见 CTD记录的 `PERSISTENCE_RECEIPT.json` 和 `operations/`。下方历史状态完整保留。

---

<!-- CTD_V10_PUBLICATION:10.5281/zenodo.23279189 -->
# 最新发表：CTD v1.0.0；科学主线保留 A3O20261010

[正式论文](release/noise-identifiability-bodily-judgments-v1.0.0.pdf) · [DOI](https://doi.org/10.5281/zenodo.23279189) · [真实公开回读收据](publication-record.json) · [中文交接](HANDOFF_ZH.md) · [逐项发表覆盖](../../publication/UCT-PUB-v1.0.31/CLAIM_COVERAGE_DELTA.json)。

本稿为公开数据二次分析与条件识别方法预印本：含响应概率等价反例、30人既有数据审计、配对读数识别边界及480个合成二项场景的有限样本计算。没有新增配对人体数据、已识别神经中介、体验测量或外部同行评议通过。CTD2的40项与CTD3的13项均停用；完成图913/424/261、10暂停、1608审查项、C1/U1与全部OPEN不变。发表覆盖UCT-PUB-v1.0.31，研究作品30、研究版本标签对40、研究DOI记录41，含独立编辑补充共42个DOI记录。

执行时当前科学接续 A3O20261010 及全部并发/旧记录完整保留；既定下一科学问题仍以 CURRENT_STATE.json 的 next_priority 为准。此次只新增发表导航，不把CTD设为替代当前科学主线。DOI公开、OTS、Arweave、Git及文件保存分别按真实收据记录，不互相代替。以下科学接续标签及历史记录均原样保留。

---

