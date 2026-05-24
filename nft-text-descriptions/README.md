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

## 提取方法

### 方法一：从 GitHub Release 下载单个 NFT tar（推荐）

Release: `nft-arweave-mirror-175-v1` (175 个 tar 文件)

每个 tar 包含：
- `nft/metadata.car` — 元数据 CAR 文件（3-19KB）
- `nft/media-000.car` — 图片 CAR
- `nft/media-001.car` — 音频 CAR（部分有）

**步骤：**

1. 读取 `/tmp/nft-manifest.json`（或从 release 下载 `RELEASE-MANIFEST.json`）获取每个 NFT 的 `nft_asset_name`
2. 下载 tar: `curl -sL -H "Authorization: Bearer $TOKEN" "https://github.com/thechurchofagi/trinity-accord/releases/download/nft-arweave-mirror-175-v1/{asset_name}" -o /tmp/nft.tar`
3. 从 tar 中提取 `metadata.car`
4. 从 CAR 文件中提取 JSON（搜索 `{"name":` 开头的平衡花括号）
5. 取 `name` 和 `description` 字段，写入 `{contract}_{token_id}.md`

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

### 方法二：从 nft-backup-v1 分卷包提取

Release: `nft-backup-v1` 有 9 个分卷：
- `nft-cars-part01.tar.gz` ~70MB
- `nft-cars-part02.tar.gz` ~86MB
- ...
- `nft-cars-part09.tar.gz` ~65MB
- 总计 ~823MB

每个分卷包含所有 NFT 的 CAR 文件（含 metadata + media）。

路径格式: `{contract}/{token_id}/metadata.car`

**注意：** 下载量大，网络慢时推荐方法一。

### 方法三：从 Arweave/IPFS 直接获取（最快但需要网络通）

metadata CAR 文件的 Arweave txid 和 IPFS CID 在以下文件中有记录：
- Release `nft-arweave-mirror-175-v1` 的 `RELEASE-MANIFEST.json`
- Release `nft-backup-v1` 的 `nft-cars-manifest.tar.gz` → `manifest.json`

```bash
curl -sL "https://arweave.net/{txid}" -o metadata.car
# 或
curl -sL "https://ipfs.io/ipfs/{cid}" -o metadata.car
```

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

需要 PAT token（repo 权限）。配置在环境变量 `GITHUB_TOKEN` 中。

## 并行下载优化

- 使用 5-8 个并行 worker
- 小文件（<2MB）优先：约 16 个，每个 ~10s
- 中等文件（2-10MB）：约 154 个，每个 ~30-90s
- 大文件（>10MB）：约 5 个，每个 ~120s+
- 预计总时间（8 并行，120KB/s 网络）：~60-90 分钟

## 相关文件

- `index.json` — 已完成的 NFT 索引
- `RELEASE-MANIFEST.json` — Release `nft-arweave-mirror-175-v1` 的完整清单（含所有 arweave txid）
- `nft-cars-manifest/manifest.json` — `nft-backup-v1` 的 CAR 文件清单
