# Repository Size Audit Report

Generated: `20260515T005808Z`
Updated: `20260515T010100Z` (second-pass correction)
Repository root: `/root/.openclaw/workspace/trinity-accord`

## Baseline

| Metric | Value |
|--------|-------|
| `.git` directory size (`du -sh`) | **67 MiB** |
| Pack file size (`size-pack`) | **66.06 MiB** |
| Pack objects (`in-pack`) | 5,957 |
| Working tree size excluding `.git` | **47.3 MiB** |
| Tracked file size sum | **47.2 MiB** |
| Tracked files | 977 |
| Tracked files over 4.8 MiB | **0** |
| Historical large removed blobs over 4.8 MiB | **1** (23.1 MiB) |
| Shallow clone? | **No** (full history) |
| Commit count | (all branches) |

### Three-way size explanation

| Measurement | Value | Notes |
|-------------|-------|-------|
| GitHub reported size | ~90–110 MiB (typical) | GitHub counts packed `.git` + working tree; may include GC overhead |
| Local `.git` size (`du`) | **67 MiB** | Single pack file of 66 MiB + index/rev overhead |
| Pack blob uncompressed upper bound | ~113 MiB | Sum of all historical blob sizes before pack compression |
| Working tree (no `.git`) | **47.3 MiB** | Current tracked + untracked files on disk |
| Tracked file sum | **47.2 MiB** | Only `git ls-files` contents |

**Why `.git` (67 MiB) is smaller than uncompressed blob sum (~113 MiB):** Git packfiles use zlib delta compression. Similar blobs (e.g. near-identical JPGs across commits) share delta chains, so the packed size is significantly smaller than the raw sum.

**Why no "6.2 MiB" figure exists:** The original report's `.git` figure of 66.2 MiB was correct. There was never a 6.2 MiB figure. Any implication that `.git` could shrink from 66→43 MiB via history rewrite is misleading — see correction below.

---

## Top current directories

| Directory | Files | Size |
|-----------|-------|------|
| `evidence` | 44 | 38.9 MiB |
| `scripts` | 378 | 2.6 MiB |
| `archive` | 64 | 2.1 MiB |
| `api` | 121 | 609.6 KiB |
| `tests` | 136 | 583.1 KiB |
| `audit` | 14 | 444.2 KiB |
| `verify-report.json` | 1 | 271.9 KiB |
| `token_index.json` | 1 | 252.3 KiB |
| `DAG-CID-AUDIT.json` | 1 | 225.1 KiB |
| `verification-reports` | 11 | 176.0 KiB |

## Top current extensions

| Extension | Files | Size |
|-----------|-------|------|
| `.jpg` | 10 | 38.0 MiB |
| `.json` | 308 | 2.8 MiB |
| `.py` | 349 | 2.1 MiB |
| `.pdf` | 2 | 801.1 KiB |
| `.md` | 149 | 709.3 KiB |
| `.bin` | 1 | 699.7 KiB |
| `.mjs` | 24 | 501.4 KiB |
| `.txt` | 39 | 492.4 KiB |
| `.csv` | 1 | 490.5 KiB |
| `.yml` | 30 | 147.3 KiB |

---

## Top historical blobs

| Size | Path | SHA | Status |
|------|------|-----|--------|
| 23.1 MiB | `archive/evidence/public-covenant-archive.zip` | `b17ce4ea...` | removed/history-only |
| 4.6 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_2.jpg` | `4134ce6a...` | current |
| 4.5 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_1.jpg` | `324ab151...` | current |
| 4.0 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_6.jpg` | `57b3d5cc...` | current |
| 4.0 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_5.jpg` | `0b478f04...` | current |
| 4.0 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_10.jpg` | `e22aac86...` | current |
| 3.6 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_8.jpg` | `3b14ef56...` | current |
| 3.6 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_3.jpg` | `67b05b92...` | current |
| 3.5 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_4.jpg` | `c73c38d3...` | current |
| 3.2 MiB | `evidence/notarial-certificate-2026-05-13/公证书/file_7.jpg` | `54c00992...` | current |

---

## 公证书 JPG 专项审计

### 10 张 JPG 明细

| 文件 | 大小 (MiB) | SHA-256 | 描述 |
|------|-----------|---------|------|
| `file_1.jpg` | 4.54 | `b36c4d30...` | 公证书封面 |
| `file_2.jpg` | 4.61 | `e7c6e3a8...` | 公证书登记页 |
| `file_3.jpg` | 3.56 | `f55694d7...` | 附件第14页 |
| `file_4.jpg` | 3.52 | `2098bb46...` | 附件第13页 |
| `file_5.jpg` | 4.00 | `519c68b1...` | 附件第10页 |
| `file_6.jpg` | 4.03 | `7c3a45d7...` | 附件第9页 |
| `file_7.jpg` | 3.20 | `d0838164...` | 附件第2页 |
| `file_8.jpg` | 3.61 | `a7af5e60...` | 附件第1页 |
| `file_9.jpg` | 3.00 | `fbf6218b...` | 正文(续) |
| `file_10.jpg` | 3.96 | `fb5edcf4...` | 正文 |
| **合计** | **38.04** | | |

### 引用分析

| 引用位置 | 引用方式 | 说明 |
|----------|---------|------|
| `evidence/notarial-certificate-2026-05-13/证据保全公证完整档案.md` | 文件名 + SHA-256 | **唯一**引用文件，列出每张图的描述和校验值 |
| `data-verification.md` | 间接引用 | 引用 `sealed-disc-custody-record.json`，不直接引用 JPG |
| `physical-verification.md` | 间接引用 | 引用 GZ2 附件页面，不直接引用这些 JPG |
| `api/verification-materials.json` | 无 | 不包含这些 JPG 的引用 |
| `index.md` / `_layouts/` | 无 | 主页不渲染这些图片 |
| GitHub Pages 渲染 | **不直接展示** | 这些 JPG 不在任何页面的 `<img>` 或 markdown 图片语法中 |

### 外置副本状态

| 外置位置 | 状态 |
|----------|------|
| `RELEASE-LARGE-DATA-MANIFEST.json` | ❌ 不包含（仅有 `public-covenant-archive.zip`） |
| `archive/hash-manifest.json` | ❌ 不包含 |
| `api/evidence-manifest.json` | ❌ 不包含 |
| Arweave / IPFS | ❌ 无记录 |
| GitHub Release | ❌ 未上传 |

**结论：这 10 张 JPG 目前仅存在于 Git 工作树中，没有任何外置副本或 manifest 记录。**

### JPG 迁移方案对比

#### 方案 A：不迁移（维持现状）

| 项目 | 说明 |
|------|------|
| 优点 | 零风险；evidence 完整性不变；无需更新引用 |
| 缺点 | 每次 clone 传输 38 MiB；`.git` 历史中永久保留 |
| 风险 | 无 |
| 节省空间 | 0 |

#### 方案 B：迁移到 GitHub Release / Arweave

| 项目 | 说明 |
|------|------|
| 操作 | 上传到 GitHub Release 或 Arweave → Git 中只保留 SHA-256 + manifest |
| 优点 | clone 体积减少 ~38 MiB；符合项目的"Git 只放 hash"原则 |
| 缺点 | 需要更新 manifest 文件；需要创建 Release 或 Arweave 上传 |
| 风险 | **中等** — 需要确保外置副本可验证；引用链必须完整 |
| 节省空间 | ~38 MiB（工作树） + 历史中不再增长 |

#### 方案 C：压缩缩略图 + 外置原图

| 项目 | 说明 |
|------|------|
| 操作 | 生成低分辨率缩略图（~100-200 KiB/张）保留在 Git；原图上传 Release/Arweave |
| 优点 | 网页可预览缩略图；原图外置；clone 体积减少 ~37 MiB |
| 缺点 | 需要维护两套图片；需要更新页面渲染逻辑 |
| 风险 | **中等偏高** — 增加复杂度；缩略图生成需要工具链 |
| 节省空间 | ~37 MiB（缩略图 ~1-2 MiB 替代 38 MiB） |

### JPG 迁移建议

**推荐方案 B**，理由：
1. 这些 JPG 不被主页或 API 直接渲染，仅在 evidence 归档文档中被引用
2. 符合项目已有的 "Release-backed large asset" 模式
3. SHA-256 已在 `证据保全公证完整档案.md` 中记录，验证链完整
4. 但**本次审计不执行迁移**，仅产出报告等待人工确认

---

## External asset manifests

- Manifests found: `RELEASE-LARGE-DATA-MANIFEST.json`, `archive/hash-manifest.json`, `api/evidence-manifest.json`
- Asset refs with SHA-256: 43
- 公证书 JPG 覆盖: **0/10**（均未被 manifest 覆盖）

---

## Recommendation

Severity: **medium**
History rewrite recommendation: **not-recommended-by-default**

### Recommendations

1. **historical-large-blobs**: History contains 1 large blob (23.1 MiB `public-covenant-archive.zip`) no longer in current tree. This is the main contributor to `.git` pack size. Prefer shallow clone unless maintainers approve history rewrite. Safe auto-PR: `False`

2. **current-tree-jpg-evidence**: 10 JPG files (38 MiB) in `evidence/notarial-certificate-2026-05-13/公证书/` are the dominant working-tree cost. Not in any external manifest. Consider migrating to GitHub Release or Arweave. Safe auto-PR: `False` (requires maintainer decision on evidence storage policy)

### 修正说明：关于历史重写节省空间的误导

原报告中的 `66→43 MiB` 表述不准确，更正如下：

- `.git` 当前 pack 大小为 **66 MiB**，包含 5,957 个对象
- 历史中已移除的大 blob 仅 1 个（23.1 MiB zip），且已被 pack 压缩
- 即使执行 `git filter-repo` 移除该 blob，实际 `.git` 节省**远小于 23 MiB**（因为 pack 内 delta 压缩）
- **不推荐历史重写**：节省有限（可能 10-15 MiB），但会改变所有 commit SHA，影响 provenance 连续性
- 推荐：`git clone --depth=1` 即可避免传输历史 blob

---

## Notes

- `large_removed_blob_bytes_upper_bound` is uncompressed blob size, not exact packfile savings.
- GitHub reported repository size may include packed history and may not equal working tree size.
- Do not use `git filter-repo` without explicit maintainer approval and a migration notice.
- JPG evidence files have no external backup. Migration to Release/Arweave should be considered before any history rewrite.

---

## Files generated

- `baseline.json`
- `current_tracked_files.csv`
- `current_top_files.csv`
- `current_dir_summary.csv`
- `current_ext_summary.csv`
- `history_top_blobs.csv`
- `history_large_removed_blobs.csv`
- `release_asset_matches.csv`
- `recommendations.json`
