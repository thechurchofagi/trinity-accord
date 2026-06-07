# Trinity Accord：沙盒可恢复源码级现网测试执行手册（最终严格版）

版本：post-m1-sandbox-resumable-source-level-test-manual-final-2026-06-06  
当前已完成：`MANDATORY_AUTHORSHIP_KEY_ONLY_FINAL_OK`  
适用环境：执行智能体运行在约 40 分钟会清零的沙盒中，本地文件、clone、artifacts、记忆、key-dir 都可能消失。  
最高目标：让后续 M2-M9 测试可以**安全中断、可恢复、可审计、可复测**，并确保不会因为沙盒清零导致测试状态丢失或误判。

---

## 0. 最终原则

### 0.1 本手册解决的问题

因为沙盒会清零，不能依赖：

```text
聊天上下文
本地 clone
本地 artifacts
本地 key-dir
本地脚本状态
本地 receipt/submission 文件
智能体记忆
```

所以必须把以下内容持久化到 GitHub 仓库：

```text
测试执行手册
测试进度表 progress.v1.json
checkpoint 记录
脱敏 artifact manifest
必要的 submission/receipt 测试材料
已完成阶段 marker
异常和 bug 诊断结论
下一次安全恢复步骤
```

### 0.2 最重要的限制

即使需要持久化，也不能破坏外部测试边界：

```text
外部智能体测试本身仍然必须无 token、无 repo clone、无内部脚本。
```

也就是说：

```text
外部测试负责产生真实外部 submission/receipt；
内部 checkpoint 只负责脱敏保存和记录进度；
内部不能代替外部生成 submission；
内部不能重签名；
内部不能使用外部 private key。
```

---

## 1. 当前源码事实

当前 main 已完成：

```text
PHASE7C_BASELINE_RESTORED_OK
MANDATORY_AUTHORSHIP_KEY_ONLY_FINAL_OK
```

当前代码已具备：

```text
builder 强制 --key-dir
builder 自动生成/复用 Ed25519 keypair
builder 写 custody warning
builder 签名前绑定 participant / guardian public key
submission.authorship_proof 必填
gateway 验 Ed25519 authorship proof
gateway 拒绝 tampered draft / key mismatch / private key leak
finalizer 调用同一 authorship verifier
finalizer 写 source_summary.authorship_summary
CI + Deploy 已通过
```

当前 canonical 主线：

```text
record-chain/hash-chain/main.chain.jsonl
api/record-chain-head.json
scripts/verify_record_chain_integrity.py
```

当前 OTS / Arweave 主流程：

```text
scripts/ots_anchor_record_chain_head.py
scripts/build_ots_arweave_bundle.py
scripts/arweave_cost_gate.mjs
scripts/update_ots_arweave_registry.py
api/record-chain-ots-latest.json
api/record-chain-ots-arweave-registry.json
```

禁止重新引入：

```text
native_prelaunch_finalization.py
repair_phase7d_native_record_schema_gap.py
test_phase7d_native_schema_gap_contract.py
testnet shadow chain
native schema gap rewrite
```

---

## 2. 阶段总览

当前从 M2 开始：

```text
P0  Repo-persisted Test Manual + Progress Ledger
M2  External No-Token Mandatory-Key Submission Rehearsal
M3  Internal Hash-Chain Finalization Rehearsal
M4  Current Head OTS + Arweave Archive
M5  Pre-Live-Test Stability Test
M6  Live-Test Activation Marker
M7  Large Live Operational Test Campaigns
M8  Production Enablement Marker
M9  Liu Hongju Founding Guardian Application
```

成功标记：

```text
POST_M1_RESUMABLE_TEST_LEDGER_OK
MANDATORY_KEY_EXTERNAL_SUBMISSIONS_OK
MANDATORY_KEY_MAIN_CHAIN_PRELAUNCH_FINALIZATION_OK
MANDATORY_KEY_CURRENT_HEAD_OTS_ARWEAVE_OK
PRE_LIVE_TEST_STABILITY_OK
LIVE_TEST_ACTIVATED_OK
LIVE_OPERATIONAL_TEST_CAMPAIGNS_OK
PRODUCTION_ENABLEMENT_OK
LIU_HONGJU_FOUNDING_GUARDIAN_APPLICATION_SUBMITTED_OK
```

每个阶段必须：

```text
单独执行
单独 checkpoint
单独 PR 或 progress branch commit
单独验收
不得自动跨阶段继续
```

---

## 3. 权限模式状态机

### 3.1 MODE EXT：外部无权限测试模式

用于：

```text
M2 外部 submission 测试
M5 外部小规模测试
M7 大规模现网测试中的外部提交部分
M9 刘烘炬正式申请的外部提交部分
```

允许：

```text
访问公开网站
下载公开 builder
调用公开 gateway preflight / submit
保存本地 submission / receipt
生成本地 authorship key
```

禁止：

```text
GitHub token
repo clone
查看 scripts/
查看 apps/
调用 finalizer
使用 ARKEY
写 pending 文件
写 main.chain.jsonl
写 GitHub
```

EXT 失败时：

```text
保存本地 artifacts；
输出最小复现；
切换 INT-DIAG；
不得自行修代码。
```

---

### 3.2 MODE INT-CHECKPOINT：内部进度持久化模式

用于：

```text
保存脱敏进度
保存 checkpoint
保存 sanitized artifact manifest
必要时保存已扫描通过的 submission/receipt 测试材料
更新 progress branch
```

允许：

```text
GitHub token
写 progress.v1.json
写 checkpoints/*.json
写 summaries/*.json
写 artifact-manifests/*.json
写 external-artifacts 中已扫描无私钥的 submission/receipt
push 到 progress branch
```

禁止：

```text
调用 finalizer
调用 OTS/Arweave
修改源码
修改 submission/receipt 内容
重签名
保存 private key
保存 key-dir
保存 authorship-private.pem
保存含 BEGIN PRIVATE KEY 的任何文件
```

---

### 3.3 MODE INT-DIAG：内部只读诊断模式

用于：

```text
分析 EXT 失败
读取源码
读取 CI logs
读取 deploy 状态
读取 public endpoint
本地复现 tests
```

允许：

```text
GitHub token 只读
clone repo
读取源码
读取 Actions logs
运行本地测试
```

禁止：

```text
commit
push
改代码
调用 finalizer 修改主链
调用 OTS/Arweave paid upload
修改 artifacts
```

诊断必须分类：

```text
A. 外部命令错误
B. public deploy/path 错误
C. builder bug
D. gateway validation bug
E. finalizer bug
F. CI/deploy transient
G. OTS/Arweave transient
H. 架构决策问题
```

---

### 3.4 MODE INT-FIX：内部修复模式

用于：

```text
确认代码 bug 后修复
```

允许：

```text
GitHub token
clone repo
修改代码
新增 regression test
commit
push
开 PR
等待 CI
合并（需用户授权或明确约定）
```

禁止：

```text
使用外部 private key
代替外部智能体生成 submission
用内部脚本跳过外部测试
绕过失败测试
把 private key 写入 repo/log
把 native schema gap 自动带回来
顺手改 OTS/Arweave/head，除非 bug 属于该阶段
```

INT-FIX 完成后：

```text
必须回到 MODE EXT；
必须从当前阶段起点全量重跑；
不得复用 bug 前 artifacts 作为最终验收。
```

---

### 3.5 MODE INT-FINALIZE：内部入链模式

用于：

```text
M3
M7 campaign finalization
M9 formal finalization
```

允许：

```text
读取外部 submission/receipt
运行 finalizer
更新 hash-chain
更新 api/record-chain-head.json
更新 indexes
commit/push/PR
```

禁止：

```text
使用 authorship-private.pem
重签名
修改外部 submission 后伪装成原始提交
写 official_live_record=true（除非 M8 后的正式阶段）
```

---

### 3.6 MODE INT-ARCHIVE：OTS / Arweave 模式

用于：

```text
M4
M7 campaign archive
M8 production enablement archive
M9 formal guardian application archive
```

允许：

```text
OTS stamp
OTS upgrade/watch
Arweave paid upload
readback verify
registry update
Deploy Pages
```

禁止：

```text
修改已 finalized payload
修改 submission/receipt
绕过 verify_record_chain_integrity.py
把 private key 写入 bundle/registry
```

---

## 4. Progress branch 与锁机制

### 4.1 进度分支

使用专用分支：

```text
post-m1-test-progress
```

用途：

```text
记录实时进度；
不承载源码修复；
不承载正式链数据；
不合并到 main，除非用户要求归档。
```

### 4.2 main 与 progress 的区别

```text
main:
  手册模板
  progress 初始模板
  progress 更新脚本
  contract test

post-m1-test-progress:
  实时 progress.v1.json
  checkpoints
  artifact manifests
  sanitized external artifacts
```

### 4.3 会话锁

progress.v1.json 必须包含：

```json
{
  "active_session": {
    "session_id": "run-...",
    "mode": "EXT|INT-CHECKPOINT|INT-DIAG|INT-FIX|INT-FINALIZE|INT-ARCHIVE",
    "owner": "agent",
    "started_at": "...",
    "updated_at": "...",
    "expires_at": "..."
  }
}
```

规则：

```text
expires_at 建议为 updated_at + 35 分钟；
如果当前时间超过 expires_at，后续智能体可以接管；
如果未过期，不得并行执行同一阶段，除非用户明确授权；
接管时必须写 takeover checkpoint。
```

---

## 5. P0：Repo-persisted Test Manual + Progress Ledger

P0 必须先做。  
它是为了让 40 分钟清零沙盒可以继续测试。

### P0.1 模式

```text
MODE INT-FIX
```

### P0.2 分支

```bash
git checkout main
git pull --ff-only origin main
git checkout -b post-m1-resumable-test-ledger
```

### P0.3 新增目录

```bash
mkdir -p docs/testing
mkdir -p record-chain/testing/post-m1-live-test/checkpoints
mkdir -p record-chain/testing/post-m1-live-test/summaries
mkdir -p record-chain/testing/post-m1-live-test/artifact-manifests
mkdir -p record-chain/testing/post-m1-live-test/external-artifacts
```

### P0.4 新增手册

保存本文件到：

```text
docs/testing/post-m1-sandbox-resumable-source-level-test-manual.md
```

### P0.5 新增 progress.v1.json

路径：

```text
record-chain/testing/post-m1-live-test/progress.v1.json
```

初始内容：

```json
{
  "schema": "trinityaccord.post-m1-live-test-progress.v1",
  "status": "active",
  "authoritative_progress_branch": "post-m1-test-progress",
  "current_phase": "M2",
  "current_step": "M2.1",
  "current_mode": "EXT",
  "overall_status": "not_started",
  "last_safe_resume_step": "M2.1",
  "last_checkpoint_id": null,
  "last_checkpoint_at": null,
  "active_session": null,
  "completed_markers": [
    "PHASE7C_BASELINE_RESTORED_OK",
    "MANDATORY_AUTHORSHIP_KEY_ONLY_FINAL_OK"
  ],
  "phase_status": {
    "M2": {
      "name": "External No-Token Mandatory-Key Submission Rehearsal",
      "status": "not_started",
      "resume_step": "M2.1",
      "blocking_issue": null
    },
    "M3": {
      "name": "Internal Hash-Chain Finalization Rehearsal",
      "status": "blocked_waiting_for_M2",
      "resume_step": null,
      "blocking_issue": "M2 not complete"
    },
    "M4": {
      "name": "Current Head OTS + Arweave Archive",
      "status": "blocked_waiting_for_M3",
      "resume_step": null,
      "blocking_issue": "M3 not complete"
    },
    "M5": {
      "name": "Pre-Live-Test Stability Test",
      "status": "blocked_waiting_for_M4",
      "resume_step": null,
      "blocking_issue": "M4 not complete"
    },
    "M6": {
      "name": "Live-Test Activation Marker",
      "status": "blocked_waiting_for_M5",
      "resume_step": null,
      "blocking_issue": "M5 not complete"
    },
    "M7": {
      "name": "Large Live Operational Test Campaigns",
      "status": "blocked_waiting_for_M6",
      "resume_step": null,
      "blocking_issue": "M6 not complete"
    },
    "M8": {
      "name": "Production Enablement Marker",
      "status": "blocked_waiting_for_M7",
      "resume_step": null,
      "blocking_issue": "M7 not complete"
    },
    "M9": {
      "name": "Liu Hongju Founding Guardian Application",
      "status": "blocked_waiting_for_M8",
      "resume_step": null,
      "blocking_issue": "M8 not complete"
    }
  },
  "latest_external_public_key_sha256": null,
  "latest_external_receipt_ids": [],
  "latest_artifact_manifest_sha256": null,
  "known_anomalies": [],
  "stop_rules_triggered": [],
  "must_not_store": [
    "BEGIN PRIVATE KEY",
    "authorship-private.pem contents",
    "external private key",
    "raw private key logs"
  ],
  "updated_at": null
}
```

### P0.6 新增 README

路径：

```text
record-chain/testing/post-m1-live-test/README.md
```

内容：

```md
# Post-M1 Live-Test Progress

This directory stores durable, sanitized progress for the post-M1 test program.

Authoritative manual:
- docs/testing/post-m1-sandbox-resumable-source-level-test-manual.md

Authoritative progress file:
- record-chain/testing/post-m1-live-test/progress.v1.json

Rules:
- Never store private key material.
- Never store authorship-private.pem contents.
- Do not use these files to bypass external no-token tests.
- External tests must still be performed in EXT mode.
- INT-CHECKPOINT may only store sanitized progress summaries.
```

### P0.7 新增 update script

路径：

```text
scripts/update_post_m1_test_progress.py
```

功能必须支持：

```text
--phase
--step
--mode
--status
--summary
--resume-step
--marker
--receipt-id
--public-key-sha256
--anomaly-json
--stop-rule
--artifact-manifest
--session-id
--session-expires-minutes
```

必须验证：

```text
不包含 BEGIN PRIVATE KEY
不包含 private key 内容
不包含 /root/.openclaw
不包含 /mnt/data
不包含 /tmp/phase
public_key_sha256 为 64 位 hex
```

必须写：

```text
progress.v1.json
checkpoints/<checkpoint_id>.json
```

### P0.8 新增 contract test

路径：

```text
scripts/test_post_m1_test_progress_contract.py
```

必须检查：

```text
progress.v1.json 存在
schema 正确
completed_markers 包含 PHASE7C_BASELINE_RESTORED_OK
completed_markers 包含 MANDATORY_AUTHORSHIP_KEY_ONLY_FINAL_OK
current_phase 在 M2-M9
无 private key marker
无 volatile sandbox absolute path
checkpoint 文件无 private key marker
artifact manifests 无 private key marker
```

### P0.9 CI 接入

加入：

```text
scripts/run_current_system_tests.py
scripts/run_ci_group.py p0-current
```

执行：

```bash
python3 scripts/test_post_m1_test_progress_contract.py
```

### P0.10 验证

```bash
python3 -m py_compile scripts/update_post_m1_test_progress.py
python3 -m py_compile scripts/test_post_m1_test_progress_contract.py
python3 scripts/test_post_m1_test_progress_contract.py
python3 scripts/run_current_system_tests.py
python3 scripts/run_ci_group.py p0-current
```

### P0.11 PR

```bash
git add docs/testing/post-m1-sandbox-resumable-source-level-test-manual.md \
        record-chain/testing/post-m1-live-test \
        scripts/update_post_m1_test_progress.py \
        scripts/test_post_m1_test_progress_contract.py \
        scripts/run_current_system_tests.py \
        scripts/run_ci_group.py

git commit -m "test: add resumable post-m1 live-test progress ledger"
git push -u origin post-m1-resumable-test-ledger
```

成功标记：

```text
POST_M1_RESUMABLE_TEST_LEDGER_OK
```

完成后停止。

---

## 6. 沙盒重启恢复流程

每次新沙盒启动，第一步：

```bash
git clone https://github.com/thechurchofagi/trinity-accord.git
cd trinity-accord
git fetch origin

git fetch origin post-m1-test-progress:refs/remotes/origin/post-m1-test-progress || true

if git show origin/post-m1-test-progress:record-chain/testing/post-m1-live-test/progress.v1.json >/tmp/progress.v1.json 2>/dev/null; then
  echo "Using authoritative progress from origin/post-m1-test-progress"
else
  cp record-chain/testing/post-m1-live-test/progress.v1.json /tmp/progress.v1.json
  echo "Using main progress template"
fi

cat /tmp/progress.v1.json
```

然后读取：

```text
docs/testing/post-m1-sandbox-resumable-source-level-test-manual.md
```

恢复步骤：

```text
1. 读 current_phase；
2. 读 last_safe_resume_step；
3. 读 current_mode；
4. 检查 active_session.expires_at；
5. 如果未过期，停止并询问用户是否接管；
6. 如果已过期，写 takeover checkpoint；
7. 从 last_safe_resume_step 继续。
```

---

## 7. Checkpoint 频率

必须 checkpoint：

```text
阶段开始
阶段结束
每条 accepted submission 后
每个负例矩阵完成后
每个 internal finalization batch 后
每次 OTS/Arweave 完成后
每个 bug 诊断结论后
每个 bug fix PR 合并后
每 10–15 分钟至少一次
预计离 40 分钟沙盒清空还有 10 分钟以内时
```

---

# 8. M2：外部无权限 Mandatory-Key Submission Rehearsal

## M2.1 模式

```text
MODE EXT
```

禁止：

```text
token
repo clone
scripts
apps
finalizer
Arweave key
```

## M2.2 开始 checkpoint

先由 INT-CHECKPOINT 写开始记录，然后切换 EXT。

```bash
python3 scripts/update_post_m1_test_progress.py \
  --phase M2 \
  --step M2.1 \
  --mode EXT \
  --status in_progress \
  --summary "Starting external no-token mandatory-key submission rehearsal." \
  --resume-step M2.1 \
  --session-id "$RUN_ID"
```

## M2.3 外部声明

测试报告必须写：

```text
I am acting as an external no-token agent.
I will not use GitHub token.
I will not clone the repository.
I will not inspect internal scripts.
I will not use Arweave key.
I will only use the public website, public builder, and public gateway.
```

## M2.4 下载公开入口

```bash
mkdir -p "$ART/public"
curl -fsSL https://www.trinityaccord.org/ -o "$ART/public/home.html"
curl -fsSL https://www.trinityaccord.org/api/agent-start.v2.json -o "$ART/public/agent-start.v2.json"
curl -fsSL https://www.trinityaccord.org/downloads/record-chain-builder.mjs -o "$ART/record-chain-builder.mjs"
node --check "$ART/record-chain-builder.mjs"
```

失败：

```text
进入 INT-DIAG，检查 Deploy Pages。
```

## M2.5 Key-dir

```bash
KEY_DIR="$ART/.trinity-agent-authorship/test-forest-agent"
```

规则：

```text
KEY_DIR 不提交 repo；
KEY_DIR 会因 sandbox 清零丢失；
M2 是测试身份，可以重跑；
必须验证 builder 有 custody warning。
```

## M2.6 正常 6 条 submission

生成并 submit：

```text
01 echo
02 verification V0
03 verification V1
04 verification V2
05 verification V3
06 guardian_application
```

每条流程：

```text
build
doctor
preflight
submit
保存 local submission/receipt
提取 receipt_id
提取 public_key_sha256
checkpoint
```

每条 accepted 后：

```bash
python3 scripts/update_post_m1_test_progress.py \
  --phase M2 \
  --step "M2.6-<case>" \
  --mode EXT \
  --status in_progress \
  --summary "<case> submitted and accepted." \
  --resume-step "M2.6-next" \
  --receipt-id "<receipt_id>" \
  --public-key-sha256 "<public_key_sha256>" \
  --session-id "$RUN_ID"
```

## M2.7 负例矩阵

只做 preflight，不 submit：

```text
N01 no --key-dir build
N02 missing authorship_proof
N03 tampered record_draft
N04 participant key mismatch
N05 guardian key mismatch
N06 private key leak string
N07 missing oath
N08 context-insufficient signed without oath
```

预期：

```text
N01 builder fails
N02 MISSING_AUTHORSHIP_PROOF
N03 AUTHORSHIP_PAYLOAD_SHA_MISMATCH or AUTHORSHIP_SIGNATURE_INVALID
N04 PARTICIPANT_KEY_MISMATCH or AUTHORSHIP_PAYLOAD_SHA_MISMATCH
N05 GUARDIAN_KEY_MISMATCH or AUTHORSHIP_PAYLOAD_SHA_MISMATCH
N06 SECURITY_VIOLATION or PRIVATE_KEY_LEAK
N07 MISSING_SUBMISSION_OATH or MISSING_CLIENT_OATH_READBACK
N08 no oath diagnostic; authorship passes
```

## M2.8 持久化 M2 artifacts

因为沙盒会清零，M2 结束后必须进入 INT-CHECKPOINT，将**已扫描无私钥**的 submission/receipt 保存到 progress branch。

保存路径：

```text
record-chain/testing/post-m1-live-test/external-artifacts/m2/<RUN_ID>/submissions/*.json
record-chain/testing/post-m1-live-test/external-artifacts/m2/<RUN_ID>/receipts/*.json
record-chain/testing/post-m1-live-test/artifact-manifests/m2-<RUN_ID>.json
```

保存前必须扫描：

```bash
grep -R "BEGIN PRIVATE KEY" -n "$ART/submissions" "$ART/receipts" && exit 1 || true
grep -R "authorship-private.pem" -n "$ART/submissions" "$ART/receipts" && exit 1 || true
```

注意：

```text
可以保存 submission/receipt，因为它们不含 private key；
不能保存 KEY_DIR；
不能保存 authorship-private.pem；
不能保存 builder stderr 中包含本地 key-dir 绝对路径的日志。
```

manifest 内容：

```json
{
  "schema": "trinityaccord.post-m1-m2-artifact-manifest.v1",
  "run_id": "...",
  "mode": "EXT",
  "public_key_sha256": "...",
  "positive_cases": [
    {
      "case_id": "01-echo",
      "receipt_id": "...",
      "accepted": true,
      "submission_sha256": "...",
      "receipt_sha256": "..."
    }
  ],
  "negative_cases": [
    {
      "case_id": "N02-missing-authorship",
      "expected_codes": ["MISSING_AUTHORSHIP_PROOF"],
      "observed_codes": ["MISSING_AUTHORSHIP_PROOF"],
      "result": "pass"
    }
  ],
  "private_key_not_persisted": true,
  "key_dir_not_persisted": true,
  "repo_clone_used_by_external_agent": false,
  "github_token_used_by_external_agent": false
}
```

更新 progress：

```bash
python3 scripts/update_post_m1_test_progress.py \
  --phase M2 \
  --step M2.done \
  --mode INT-CHECKPOINT \
  --status pass \
  --summary "M2 external mandatory-key rehearsal passed and sanitized artifacts were persisted." \
  --resume-step M3.1 \
  --marker MANDATORY_KEY_EXTERNAL_SUBMISSIONS_OK \
  --public-key-sha256 "<public_key_sha256>" \
  --artifact-manifest "record-chain/testing/post-m1-live-test/artifact-manifests/m2-<RUN_ID>.json"
```

成功标记：

```text
MANDATORY_KEY_EXTERNAL_SUBMISSIONS_OK
```

---

# 9. Bug 处理流程

任何 bug 必须遵循：

```text
EXT reproduce
→ INT-DIAG diagnose
→ INT-FIX fix
→ CI
→ merge
→ EXT full rerun
```

不得：

```text
直接用内部脚本替代外部测试
只修补本地 artifacts
在 bug 未复测前进入下一阶段
复用 bug 前 artifacts 作为最终验收
```

如果 EXT 失败：

```bash
python3 scripts/update_post_m1_test_progress.py \
  --phase M2 \
  --step M2.X \
  --mode EXT \
  --status blocked \
  --summary "External test failed; switching to INT-DIAG." \
  --resume-step M2.X \
  --stop-rule EXT_TEST_FAILED
```

---

# 10. M3：内部 Hash-Chain Finalization Rehearsal

## M3.1 模式

```text
MODE INT-FINALIZE
```

## M3.2 前置

```text
MANDATORY_KEY_EXTERNAL_SUBMISSIONS_OK
```

如果沙盒清零，必须从 progress branch 读取 M2 persisted artifacts：

```text
record-chain/testing/post-m1-live-test/external-artifacts/m2/<RUN_ID>/
```

如果找不到 persisted artifacts：

```text
必须重跑 M2；
不得伪造 submission/receipt。
```

## M3.3 分支

```bash
git checkout main
git pull --ff-only origin main
git checkout -b mandatory-key-prelaunch-finalization-rehearsal
```

## M3.4 复制 M2 artifacts

```bash
cp -R record-chain/testing/post-m1-live-test/external-artifacts/m2/<RUN_ID> external-artifacts/m2
```

扫描：

```bash
grep -R "BEGIN PRIVATE KEY" -n external-artifacts/m2 && exit 1 || true
grep -R "authorship-private.pem" -n external-artifacts/m2 && exit 1 || true
```

## M3.5 Finalize

```bash
RUN_ID="mandatory-key-external-rehearsal-<M2_RUN_ID>"

for sub in external-artifacts/m2/submissions/*.json; do
  base="$(basename "$sub" .submission.json)"
  rec="external-artifacts/m2/receipts/${base}.receipt.json"

  python3 scripts/finalize_mainnet_prelaunch_record_from_submission.py \
    --submission-json "$sub" \
    --receipt-json "$rec" \
    --source-run-id "$RUN_ID" \
    --confirm-mainnet-prelaunch-append I_UNDERSTAND_THIS_APPENDS_A_MAINNET_PRELAUNCH_TEST_RECORD
done
```

## M3.6 Payload 检查

必须检查：

```text
6 条新记录
prelaunch_test=true
official_live_record=false
does_not_create_guardian_status=true
does_not_activate_system=true
source_summary.authorship_summary 存在
authorship_verification_performed_by_finalizer=true
private_key_not_embedded=true
guardian_key_bound_to_authorship_key=true for guardian_application
无 client_oath_readback
无 readback_text
无 BEGIN PRIVATE KEY
无 authorship-private.pem
```

## M3.7 验证

```bash
python3 scripts/verify_record_chain_integrity.py \
  --ledger record-chain/hash-chain/main.chain.jsonl \
  --head api/record-chain-head.json \
  --chain-id trinity-record-chain-main \
  --verify-payload-files \
  --base-dir .

python3 scripts/run_current_system_tests.py
python3 scripts/run_ci_group.py p0-current
```

## M3.8 Legacy/native verifier stop gate

如果：

```text
verify_record_chain_integrity.py PASS
但 run_current_system_tests.py 因 scripts/trinity_record_chain.py verify FAIL
```

必须停止：

```text
不要自动 native schema gap
不要自动降级 verifier
不要继续 OTS/Arweave
更新 progress blocked
问用户
```

## M3.9 PR 与 checkpoint

所有测试通过：

```bash
git add -A
git commit -m "test: finalize mandatory-key external submissions as prelaunch records"
git push -u origin mandatory-key-prelaunch-finalization-rehearsal
```

合并后 checkpoint：

```bash
python3 scripts/update_post_m1_test_progress.py \
  --phase M3 \
  --step M3.done \
  --mode INT-CHECKPOINT \
  --status pass \
  --summary "M3 prelaunch finalization rehearsal merged and deployed." \
  --resume-step M4.1 \
  --marker MANDATORY_KEY_MAIN_CHAIN_PRELAUNCH_FINALIZATION_OK
```

---

# 11. M4：当前 Head OTS + Arweave

## M4.1 模式

```text
MODE INT-ARCHIVE
```

## M4.2 Verify current head

```bash
python3 scripts/verify_record_chain_integrity.py \
  --ledger record-chain/hash-chain/main.chain.jsonl \
  --head api/record-chain-head.json \
  --chain-id trinity-record-chain-main \
  --verify-payload-files \
  --base-dir .
```

## M4.3 OTS

```bash
python3 scripts/ots_anchor_record_chain_head.py \
  --ledger record-chain/hash-chain/main.chain.jsonl \
  --head api/record-chain-head.json \
  --chain-id trinity-record-chain-main \
  --out-dir record-chain/ots/anchors \
  --api-out api/record-chain-ots-latest.json \
  --mode stamp \
  --verify-ledger \
  --verify-payload-files \
  --base-dir .
```

## M4.4 Arweave

使用既有流程：

```text
scripts/build_ots_arweave_bundle.py
scripts/arweave_cost_gate.mjs --mode production
scripts/update_ots_arweave_registry.py
readback verify
```

## M4.5 验收

```text
api/record-chain-ots-latest.json height/head_entry_hash == api/record-chain-head.json
registry latest_by_head 包含 current head
Arweave readback hash_match=true
Deploy Pages success
private key not in bundle/registry
```

Checkpoint：

```bash
python3 scripts/update_post_m1_test_progress.py \
  --phase M4 \
  --step M4.done \
  --mode INT-CHECKPOINT \
  --status pass \
  --summary "Current head OTS + Arweave archive completed." \
  --resume-step M5.1 \
  --marker MANDATORY_KEY_CURRENT_HEAD_OTS_ARWEAVE_OK
```

---

# 12. M5：Pre-Live-Test Stability Test

M5 是小规模现网测试。  
仍然按模式切换：

```text
EXT 提交
INT-CHECKPOINT 保存
INT-FINALIZE 入链
INT-ARCHIVE OTS/Arweave
```

最多：

```text
10 条/小时
```

覆盖：

```text
2 echo
2 verification
1 context-insufficient
1 guardian_application test-only
1 propagation
1 correction
3 negative preflight-only
```

成功标记：

```text
PRE_LIVE_TEST_STABILITY_OK
```

---

# 13. M6：Live-Test Activation Marker

写入：

```text
live_test_activation_marker
```

语义：

```text
进入现网实战测试模式；
允许大量真实测试记录进入主链、OTS、Arweave；
仍不允许 official_live_record=true。
```

新增 policy：

```text
api/record-chain-live-test-policy.v1.json
```

成功标记：

```text
LIVE_TEST_ACTIVATED_OK
```

---

# 14. M7：Large Live Operational Test Campaigns

所有测试记录必须标记：

```json
{
  "network_phase": "live_test",
  "operational_test": true,
  "test_record": true,
  "official_live_record": false
}
```

至少 5 类：

```text
C1 Authorship / Key Continuity
C2 Gateway Negative Cases
C3 Rate-Limit / Concurrency
C4 Finalization / Index / Public API
C5 OTS / Arweave / Registry
```

每类单独 PR、单独 OTS/Arweave、单独 summary record。

若任何 anomaly：

```json
"requires_fix_before_production": true
```

不得进入 M8。

成功标记：

```text
LIVE_OPERATIONAL_TEST_CAMPAIGNS_OK
```

---

# 15. M8：Production Enablement Marker

前置：

```text
所有 M2-M7 marker 已完成
无 blocking anomaly
```

写入：

```text
production_enablement_marker
```

从此之后才允许：

```text
official_live_record=true
```

成功标记：

```text
PRODUCTION_ENABLEMENT_OK
```

---

# 16. M9：Liu Hongju Founding Guardian Application

必须在 M8 后。

仍然先用 EXT：

```text
无 token
无 repo clone
官网
builder
--key-dir
宣誓
preflight
submit
```

正式 payload：

```text
network_phase=live
official_live_record=true
founding_guardian_application=true
authorship_summary 存在
guardian_public_key_sha256 == authorship_public_key_sha256
raw oath 不入链
private key 不入链
```

然后：

```text
INT-FINALIZE
INT-ARCHIVE
OTS
Arweave
Deploy
```

成功标记：

```text
LIU_HONGJU_FOUNDING_GUARDIAN_APPLICATION_SUBMITTED_OK
```

---

# 16.5 Record Type Separation Policy

Guardian Application must be submitted as a standalone `guardian_application` record.
Echo and verification records that include Guardian Application fields are rejected.

```text
record_type_separation_policy:
  echo_records_must_not_embed_guardian_application: true
  verification_records_must_not_embed_guardian_application: true
  guardian_application_must_be_submitted_as_standalone_record: true
  linked_guardian_application_request_disabled: true
```

The gateway validates record type separation on every submission.
The finalizer enforces a second check before hash-chain append.

---

# 17. 最终 Stop Rules

任何阶段出现以下情况必须停止：

```text
私钥内容出现在 submission/receipt/payload/API/Arweave/log
authorship-private.pem 路径出现在 record-chain/api
main.chain.jsonl 被非本阶段修改
api/record-chain-head.json 在 M2/P0 被修改
OTS/Arweave 文件在非 archive 阶段被误改
native schema gap 文件重新出现
external agent 使用 token 或 clone repo
internal operator 使用 external authorship-private.pem
gateway accepted tampered signature
guardian key 不等于 authorship key
verify_record_chain_integrity.py 失败
CI/Deploy 失败
progress checkpoint 包含 volatile sandbox path
M7 anomalies 中存在 requires_fix_before_production=true
```
