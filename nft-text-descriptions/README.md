# NFT Text Descriptions — Mirror Task

## 目标

将 175 个 ASIMilestones NFT 的**纯文本描述**（name + description）从 Arweave CAR 文件中提取，一一对应镜像到本目录。

## 当前进度

- **已完成**: 175 / 175
- **剩余**: 0
- **最后更新**: 2026-05-24

## 边界说明

本目录镜像的是 175 个 NFT metadata 中的 name + description 文字，不包含音乐和图像正文。

这些文本适合作为 ASIMilestones / AGIMilestones historical chronicle context，但不等同于：
- canonical Bitcoin Original authority
- external factual verification
- Arweave/CAR integrity proof
- image or music content verification

## 数据来源

NFT 元数据存储在 Arweave 上的 CAR 文件中。每个 NFT 的 metadata.car 包含 JSON，格式如下：

```json
{
  "name": "ASIMilestones: ...",
  "description": "完整描述文本...",
  "image": "ipfs://...",
  "animation_url": "ipfs://...",
  "attributes": [...]
}
```

## 当前可用性说明

`nft-arweave-mirror-175-v1` 的历史说明曾描述 175 个单项 tar，但完整分页 API 观察显示该 Release 当前有 **0 个自定义资产**。它不是当前可用的字节恢复源，Release 文本也不能代替字节证据。

当前恢复路径是：

- 仓库内已经完成的 175 份 Markdown 文本镜像；
- `nft-backup-v1` 的 9 个 CAR 分卷和 1 个清单包；
- Zenodo NFT annex DOI `10.5281/zenodo.21754229`，其中逐字节保存上述 10 个包，并已完成公开冷恢复；
- Arweave 上由清单逐项指向的 CAR。

## 提取方法

### 方法一：直接使用已完成的文本镜像

一般阅读或分析无需再次下载约 823 MB 的 CAR 包。读取本目录的 `index.json`，再按 `{contract}_{token_id}.md` 打开对应的 175 份文本即可。

### 方法二：从 Zenodo annex 完整恢复（可复现恢复推荐）

从仓库根目录运行：

```bash
python3 scripts/restore_external_binary_annex.py \
  --zenodo-record-id 21754229 \
  --output-dir /tmp/trinity-nft-annex
```

恢复后，10 个原始 GitHub Release 包位于：

```text
/tmp/trinity-nft-annex/payload/releases/nft-backup-v1/
```

其中：

- `nft-cars-manifest.tar.gz` 包含 `manifest.json`；
- `nft-cars-part01.tar.gz` 至 `nft-cars-part09.tar.gz` 包含 434 个 CAR 文件；
- 分卷内的文件名是 `{arweave_txid}.car`，通过清单映射到 contract、token ID 和 metadata/media 角色。

该恢复会验证 annex 包、资产集合以及每个外层资产的大小和 SHA-256。清单记录 175 个 NFT、434 个 Arweave 文件、434 次成功下载和 0 次失败。

### 方法三：从 Arweave 获取单个 metadata CAR

若只需重新提取一个 NFT，先在 `nft-cars-manifest.json` 中按 contract 和 token ID 查到 role 为 `metadata` 的 txid、SHA-256 和 size，再下载并核对：

```bash
curl -fsSL "https://arweave.net/{txid}" -o /tmp/metadata.car
sha256sum /tmp/metadata.car
```

不要仅因网关返回了内容就视为验证通过；必须同时匹配清单中的大小与 SHA-256。

从 CAR 文件中提取 JSON 后，取 `name` 和 `description` 字段，写入 `{contract}_{token_id}.md`。

**CAR 文件解析方法：**
```python
def extract_json_from_car(car_bytes):
    text = car_bytes.decode('utf-8', errors='replace')
    start = text.find('{"name":')
    if start == -1:
        start = text.find('{"description":')
    if start == -1:
        start = text.find('{"')
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i+1])
    return None
```

### 方法四：直接从 `nft-backup-v1` 分卷包提取

Release: `nft-backup-v1` 有 9 个分卷：
- `nft-cars-part01.tar.gz` ~70MB
- `nft-cars-part02.tar.gz` ~86MB
- ...
- `nft-cars-part09.tar.gz` ~65MB
- 总计 ~823MB

九个分卷合计包含全部 434 个 CAR 文件（metadata + media）。

分卷内路径格式: `{arweave_txid}.car`；使用 `nft-cars-manifest.json` 或清单包中的 `manifest.json` 解析身份和角色。

**注意：** 公开 Release 资产可直接下载；GitHub token 只用于提高 API 额度，并不是读取公开资产所必需。完整下载量较大时，优先使用上面的 DOI 冷恢复入口。

## 文件命名规则

`{contract_address}_{token_id}.md`

示例: `0x019372bBee377109b8Eae66d7267f5C4EaAdBb79_85210329807936527805363210873332413577559846505703131855064182995898737885185.md`

## Markdown 格式

```markdown
# {name}

**Contract**: `{contract}`

**Token ID**: `{token_id}`

## Description

{description}
```

## 合约分布

| 合约 | 数量 |
|------|------|
| `0x019372bBee377109b8Eae66d7267f5C4EaAdBb79` | 156 |
| `0x2b0c3cc5CD9652BEf0caCFc9c7699455725B9cc1` | 16 |
| `0xF12815D22BAf904A21B498a5df8e5d8529d2079e` | 2 |
| `0x74f97bDEfa07C2F99c876C2Bd3b49628EdD1c603` | 1 |

## GitHub Token

读取公开 Release 或仓库不需要 PAT。若脚本通过 GitHub API 做大量枚举，可选地配置只读 `GITHUB_TOKEN` 以提高速率上限；不要为公开读取授予 `repo` 写权限。

## 并行下载优化

- 使用 5-8 个并行 worker
- 小文件（<2MB）优先：约 16 个，每个 ~10s
- 中等文件（2-10MB）：约 154 个，每个 ~30-90s
- 大文件（>10MB）：约 5 个，每个 ~120s+
- 预计总时间（8 并行，120KB/s 网络）：~60-90 分钟

## 相关文件

- `index.json` — 已完成的 NFT 索引
- `RELEASE-MANIFEST.json` — 历史 175 项映射快照；当前不应从空 Release 下载
- `nft-cars-manifest.json` — `nft-backup-v1` 的 434 项 CAR 文件清单
