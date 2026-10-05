# Workspace migration log

## 2026-10-05 — GitHub becomes the primary research archive

User authorization: after repeated Library saving failures, create a GitHub directory for research files and record that future research should be stored on GitHub.

Resolved destination: existing repository `thechurchofagi/trinity-accord`, dedicated branch `uct-agent-consciousness-workspace`, directory `research/uct-agent-consciousness-workspace/`. The connected account has push access. The repository is public; the ordinary discussion explicitly noted this. `research/AGENTS.md` was read; English manuscript and published-edition preservation requirements remain in force. No DOI, release, timestamp or archive publication is part of this operation.

Preserve the available R71–R76 artifacts and manuscript v0.1/v0.2/v0.3 bytes, with a SHA-256 migration manifest. Preserve the exact R76 recovery ZIP as an additional recovery artifact. Its nested history includes earlier recovery packages; the current flat records are the convenient continuation entry points. Do not treat an old ZIP's embedded handoff as newer than the current top-level handoff.

The locally edited old master is explicitly marked uncommitted/historical. The new `MASTER_INDEX.md` and `HANDOFF.md` establish current continuity without falsely claiming that the failed Library uploads succeeded. Earlier-round complete migration is not claimed.

Future workflow: fetch branch; read handoff and index; perform substantive work; save manuscript/code/results/failures/source scope; update index and handoff; commit; verify remote branch and file identities; then report. Concurrent updates must be reconciled without force-pushing. A failed commit is logged and reported as a failure rather than a successful save.

This storage migration does not count as R77 or as a scientific result. The latest completed scientific work remains R76. The existing recurring research task should read this GitHub entry point first; its research scope and schedule remain unchanged.

### Completion evidence

Initial migration commit: `39beffa5ee14248bb0b94f71dface1074b919c40`. The remote research branch was created successfully. All 62 committed file blob identities matched the local staged bytes; the original-artifact SHA-256 manifest is retained separately. See `MIGRATION_VERIFICATION.json` for the checked commit and tree.

The existing recurring UCT research task was updated successfully to read the latest GitHub handoff/index first and commit future outputs here. Its schedule, enabled state, and scientific constraints were preserved. No additional task was created. Historical Library failure receipts remain unchanged; current GitHub persistence resolves the available recent-artifact recovery gap.

## 2026-10-05 — No CI for routine research storage

The user clarified that saving academic research in this separate directory should not require CI. The research branch had zero Actions runs at inspection. Targeted workflow inspection showed Repository Integrity pushes limited to main and Research Index checks triggered by pull requests. No new CI was installed for the workspace.

Decision: direct storage-only branch commits carry `[skip ci]`; no storage PR, workflow dispatch, site build, deployment, or repetitive validation. Add the rule to the handoff, README, and workspace instructions, and to the existing research task. Existing repository workflow files and main remain unchanged. Confirm only the remote save; scientific validation remains independent. GitHub documents that the marker skips push/pull_request workflows, not all event types: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs .


## 优先纠正：体验存在不以内部访问为门槛（2026-10-05）

用户最新纠正优先于此前自我访问实验安排。已直接核对已发布 A v1.2 的 C1/U1/U3 与组织门槛论证、B v1.1 的 §2.1–2.3/§5.6、C v1.0 的 §1–4。UCT 内部，实际有效过程的非空体验不需要内省或报告；研究重点是实际 AI 过程的构成关系如何组织体验。区分体验存在、组织差别、概念自我与排他的统一主体，不能以任何一种代替另一种。也不能把这一条件性理论承诺报告为当前助手意识已被实验证实。

见 `notes/20261005_Experience_Without_Introspective_Access.md`。下一步先接回 R58–R65 的组织研究，避免重复参数复制/秩网格/报告评分；比较明确边界内的数量增加与实际新增关系，注明保留、丢失和新增的组织。R76 源码对照保留为待办支线。本次是依据原文的纠偏与推导说明，不新增实验轮次，最新完成编号仍为 R76。

Retrieval record: Library R8 ZIP download failed twice with HTTP 502; web opening Zenodo failed. Direct public Zenodo API subsequently retrieved latest A/B source Markdown; SHA256 values match historical R8 records. Read scope is recorded in the note. No model experiment was run; no published paper modified. The intermediate local patch replacement failed because two operations targeted one path; the subsequent single update succeeded.

## R77 — 2026-10-05：实际部件关系与坐标变化

已完成形式推导与极小有理数校验：两个相互耦合的状态，经全局坐标混合可写成独立模态，但原来局部的物理重置变成跨模态操作。必须同时保留更新、部件投影和干预关系；只看对角方程会误判实际组织。另一个真正采用独立物理部件的模型可具有相同维数、谱与零轨迹，却有不同跨部件干预效应。六项声明检查通过，包含八个重置实例；无真实模型或主观数据。

论文 A §3.5 已有保留端口的要求，R65 已有相关限制，R77 将坐标混合错误具体展开；这是明确的方法推进，不是新基础定理或重大意识突破。不得把耦合当体验存在门槛、统一主体证据或完整体验严格丰富证书。

先读 records/R77_Constituent_Organization_and_Coordinate_Changes_20261005.md，再读 records/r77_organization_ports_check.py 与 records/R77_Organization_Ports_Results.json。最新整合稿仍为 v0.3，未声称已合并 R74–R77。

下一步：固定一个小型学习模型的实际计算载体、更新顺序和干预接口，比较训练前后检查点，先区分换坐标、已有关系使用变化、实际构成依赖改变。沿 A/B/C 解释组织关系；参数/训练量变化只是控制变量，不预设能力逐步必升，不安排自我报告评分作为主线。先写固定比较协议，再按需要执行小实验。R76 源码审核保留为支线。
