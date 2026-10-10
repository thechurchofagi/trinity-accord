# CTD v1.0.0 发表后科学仓库同步：独立准备审阅

日期：2026-10-10 UTC。审阅者：`/root/theory_literature`。

## 结论

**PASS — 所列最终脚本通过本次限定范围的静态审阅，没有尚未处理、会阻塞真实 scratch overlay 准备的 must-fix。** 本结论适用于下表的精确文件版本，以及由真实发布收据、原样公开文件、独立覆盖审查和执行时干净研究 HEAD 构成的输入契约。它不是已应用仓库更新、已推送、已完成 DOI/OTS/Arweave 保存或已完成新的科学验证的收据。

本审阅只读源码、现有 JSON 和 Git 状态，并对两个脚本做无副作用 AST 解析。没有调用 `prepare_sync.main()`，没有运行 `apply_overlay.py`，没有制造发表成功收据，没有修改任何仓库或冻结科学文件，没有外部请求。本报告是本审阅者唯一新增的文件。

## 精确审阅对象

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `ctd_post_publication/prepare_sync.py` | 49,820 | `2de80f7457b082980622119b4e091cc7635b3fdbda51e07d5956b213c979665b` |
| `ctd_post_publication/apply_overlay.py` | 5,811 | `1fe39cc6834b36de241e7b0a90e07e34dec276531a6aecb313ac45e9f8ae5317` |
| CTD 正式发布器 `ctd_release_repo/research/noise-identifiability-bodily-judgments/publication.py` | 本次核对真实 receipt 构造与 FILES | `c55b188787dce0a3bd687d18ef1430e1dd3050b0629067157ef29064bae5e4ac` |
| `ctd_post_publication/PREPARATION_COMPONENT_CHECKS.json` | 修改者的 17 项组件检查收据；本审阅读回其结果 | `071deafdaa2f531a2dabf763bf24afbad797afe0d89112ce11e2eb0bc4bad3fb` |

最后只读核对时，研究仓库 HEAD 为 `5f0c7a4f1cb417500f5fadc822dbec3a6f06c4d2`，工作树干净，当前覆盖版本 `UCT-PUB-v1.0.30`，当前科学主线 `A3O20261010`。这些是审阅时事实；执行必须重新读取其实际 HEAD，不能把旧 `53d569b` / `.29` 准备快照当成固定执行基底。

## 逐项判定

### 1. 真实发表收据与解析证据：通过

发布器的 `publish()` 在提交和匿名逐文件回读成功后写出 `publication-record.json`。其字段包括 `submitted: true`、`public_file_readback_pass: true`、`public_readback_authenticated: false`、报告号、版本、记录 ID、DOI、精确文件字节数与 SHA-256。准备器要求这些状态及身份相容；预留或未提交记录在第一条发表门禁即被拒绝。

最终准备器的公开文件集合与发布器 `FILES` 完全一致，精确为九件：Markdown、PDF、复现 ZIP、许可说明、来源审查、SHA256SUMS 和三种引用文件。每件本地公开文件均需与真实回读收据中的字节数及 SHA-256 相同。兄弟位置的 `EXPECTED-PUBLICATION.json` 如存在，还须符合收据中的 manifest hash。准备器本身不进行新的匿名网络回读，因此此处依赖实际工作流收据的来源和完整性。

原 CI 收据的 DOI 解析状态可以仍为 pending。可选的独立 `DOI_RESOLUTION.json` 必须同时满足 DOI/record ID 匹配、匿名、`RESOLVER_PASS`、`matches_record: true`、HTTP 200 和最终 URL 精确匹配；该文件另存原字节。准备器据此报告后来的解析状态，保留原 CI 收据的历史快照，不将历史 false/pending 改写为当时已经成功。OTS、Arweave、Git 和文件保存仍分别依赖各自真实收据。

### 2. 正式内容与 25 + 28 项披露边界：通过

正式 ZIP 需通过 CRC、单根目录、成员唯一性、清单成员完全相等和逐成员哈希校验；不接受符号链接或路径越界。科学存档从 ZIP 原字节复制。公开 Markdown 相对已审稿只允许一次 DOI 替换及四个已实际存在的图路径调整，其余字节须一致。

独立覆盖审查的 `manuscript.sha256`、`release_attachment.sha256`、`source_ledger.sha256` 现在分别与实际正文模板、正式 ZIP、正式台账精确比较。25 个科学节点逐条核对 ID、完整 statement、statement hash 和 ZIP 内 evidence paths。最终增量恰为 53 个互异 ID：25 节点、9 条规则、19 条上下文。

节点的 `covered_exact` 明确指正式附件的完整披露，正文范围单独保留在逐条审阅中；28 项规则/上下文明确标为 ZIP 中禁用记录的披露，未声称正文逐条展开。特别是 CTD2-N016 的完整非 joint-Gaussian copula 反例、CTD2-N017 的完整治理限定，以及 CTD3 部分不等方差/连续校准细节，继续按正文与附件分层说明。

所有新增披露项均不启用为已成立的科学前提，实际应用仍为 OPEN。引用 UCT、SCU、R 系列、早期 CTD 或任何其他研究，不为那些工作自动增加发表覆盖。A3O 导航修复不进入这 53 项 CTD 正式披露。

### 3. 动态覆盖版本与完整发表计数：通过

版本分配同时读取执行时覆盖版本、本地 publication 目录及该 HEAD 的 Git 目录树；新记录目录和新覆盖目录在本地与 Git 树中均须不存在。稀疏检出不再被当作远端树中不存在的证据。准备器及应用器都检查精确 HEAD 与干净工作树；发生并发更新后需正常重新准备。

发表计数从当前入口指向的完整 works 清单重新计算，并与入口、完整清单及完整 ledger 三处计数相等后才追加 CTD。旧 work/version 对象需逐对象保持原样。代码保留“相同版本标签但不同版本 DOI”的区别，也保留研究作品与编辑补充的区别；不计入预留记录。此次仅增加一个研究工作、一个工作/版本标签对、一个研究 DOI 记录及总 DOI 记录各一。

审阅时继承计数为 29 个研究工作、39 个研究工作/版本标签对、40 个研究 DOI，以及一个独立编辑补充 DOI；总 DOI 41。若执行时完整清单仍相同，追加后应为 30 / 40 / 41，加一个编辑补充，总 DOI 42。这是条件性算术，最终值必须以执行时重算结果为准，不是本审阅新做的全账户普查。

### 4. A3M / A3N / A3O、OPEN 与导航前缀：通过

最终准备器从执行时 `CURRENT_STATE` 取得科学主线，不再把 CTD 发表行为写成替代 A3O 的最新科学研究。`latest_research`、`latest_activity`、`latest_pending_research`、`latest_scoped_review` 和 `next_priority` 在 CURRENT 中保持相等；CTD 进入独立 publication activity/result/candidate/scoped-review 字段。

SESSION 的原导航快照被保留，滞后的研究接续按 CURRENT 中当前 A3O 修复，而非切换为 CTD。registry 在确有缺项时，以该 HEAD 中 A3O 的真实禁用 MAP_EXTENSION 补入其原研究导航；这一步没有新增 A3O 科学候选、没有发表 A3O，也没有启用其任何前提。所有并发 pending 身份及覆盖更新链从执行时数据继承；不只硬编码 A3M/A3N。

旧 registry results、各 pending 数组和覆盖历史链均有原前缀相等检查。完成图 release/hash、审查 ledger hash、完成图计数、QC OPEN、优先级以及有效 module 的保护字段不改变。根目录五份 Markdown 保留全部旧字节，仅前置明确的发表导航；最高研究政策只插入独立导航说明。当前科学文件、历史证明和旧记录目录不属于覆盖写入范围。

修正后的组件收据记录了固定 HEAD 下非空 Git blob 身份清单：A3M 20 项、A3N 19 项、A3O 17 项、CTD v0.2 149 项。收据明确这些是 mode/type/blob/path 的 Git 身份范围；未检出文件没有因此被宣称重新逐字或语义审查。该说明替代了初版错误的“本地 0 文件”保护证据。

### 5. 默认不写仓库与应用边界：通过

prepare 的所有输出必须落在仓库之外的新目录；其 Git 命令限于读取。apply 默认在验证后输出 `DRY_RUN_VALIDATED_NO_WRITES` 并返回。只有显式 `--apply` 才写本地文件，且旧文件只允许 11 个根导航路径，新文件只允许固定 CTD 记录与新覆盖版本目录。

应用前检查源/目标哈希、目标树存在性、路径越界、符号链接逃逸、精确 HEAD 和干净工作树；每个目标写入前再次检查，随后用同目录临时文件替换并复核写入哈希。该工具没有 fetch、checkout、commit、push、发表或钱包调用。

应用并非整批事务：中途失败会明确报告部分已写路径并停止，不自动 reset 或覆盖其他进程的工作。实际操作应保持准备目录不再修改；发生失败或任何并发变动须按收据手动核对并重新准备，不能只改 manifest 的 HEAD 来绕过门禁。此限制已有显式行为，不属于本次必须新增的审批或流程。

## 已处理的问题与本审阅范围

初审的实质问题是稀疏目录的空清单被用作历史树证据，现已修正。新增的 A3O 主线保留要求已落实。精确九文件清单、精确覆盖审查字段绑定是本审阅提出的输入防误配加固，也已落实。

初审版本仅保留为历史身份：prepare `4fbb92960b2cf3613aa67d7c241ccddf190977ca4eb4fcba4de7e78cb5abebcf`；apply `6340ac1d12e7722f3ac6ad33e5262c85423fcd74725958edabbfc953e05e6040`。它们不是本报告通过的最终执行版本。

修改者的 17 项组件检查全部为 pass，本审阅读回了其收据并独立检查了相关源码逻辑；未重复运行该组件脚本，也未把组件检查等同于整批 overlay 执行成功。正式应用、提交、远端回读以及后续保存结果，仍需由真实执行者的独立收据记录。本报告不扩大原有全图语义审查范围，也不产生新的实证或体验结论。
