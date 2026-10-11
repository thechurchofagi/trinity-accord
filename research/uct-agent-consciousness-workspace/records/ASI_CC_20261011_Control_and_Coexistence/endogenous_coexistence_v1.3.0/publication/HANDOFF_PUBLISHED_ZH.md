# ASI-CC-v1.3.0 DOI发表与长期存证交接

论文：《When Revocation Does Not Restore Safety: Exact Admission Across Asynchronous Policy Changes in Multi-Agent Systems》，Hongju Liu，12页英文预印本，版本1.3.0，CC-BY-4.0，非同行评审。**DOI已经发表：10.5281/zenodo.23299153**。官方页面 https://zenodo.org/records/23299153。

## 具体核验

GitHub发表工作流38144868048运行成功。Zenodo六个公开资产逐份SHA-256字节回读，与冻结PDF、LaTeX源码及完整复现ZIP一致。DOI解析HTTP200，指向正确的Zenodo记录。PDF SHA-256：16357a609238a789b2babdd426e73536489f9a3dfe30070a1a891b5ba6aa6a4b。ZIP SHA-256：c7edff33ca746d47ebf77e7648ed4f3b8160ecea1e1e7c00c5196912b809b6fc。发表和校验程序保存在研究专用分支 research/revocation-admission-v130-20261011。

OpenTimestamps 初始日历提交工作流38145179179已成功；原始.ots证明SHA-256：10adc5907e57f347a2f81fcbd804213b31c686ccc5cb586f063d14b687a2ef54。四个日历待确认，无比特币区块高度：PENDING_BITCOIN，尚非最终链上存证。

主分支已部署 `research-rac13-v130-ots-arweave-scheduler.yml`，每小时第17分做一次受控升级验证。首次运行38145220011成功执行检查，但因OTS区块证明未成熟，Arweave付费步骤被跳过，无txid，无Arweave公开回读；严格保留0.5 AR/30天、单笔<0.1 AR、最低余额0.25 AR等仓库原预算约束。最终成功与否不保证具体时间，定时作业只会依严格条件尝试。

发表不是科学正确性或全球原创性证明。当前正式UCT地图UCT-MAP-v1.1.2未新增节点规则；已公开的旧PR-v6 DOI 10.5281/zenodo.23295776是不同作品，未被覆盖；ASI-CC-v1.1/v1.2稿源保留。科研完整台账仍需与已公开语料进一步核对。

正式回执见 `publication/PUBLICATION-RECEIPT.json` 与本目录 `PUBLICATION_COMPLETION.json`。初始OTS证据见 `research/paper-timestamps/2026-10-11-rac13-v130/`。
