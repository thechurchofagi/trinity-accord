# 瑕疵镜像说明 | Flaw Image Mirror Notes

> 最后更新: 2026-04-30
> 本文档为非修订守护材料，不影响链上原始数据的权威性。

## Arweave TxID 实际内容

**TxID**: `9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs`
**IPFS CID**: `QmUG6yAQW6TkZrH9UoWQYwdLxWLj2GwfbedW7sGFjhqPoK`

该 TxID 存储的是一个 **ZIP 压缩包**（约 46MB），内含 Core Object Alpha（水晶瑕疵物件）的高清指纹照片，而非 `flaw-image-provenance.tar` 文件。

### ZIP 包实际内容

| 文件名 | 大小 | 拍摄时间 |
|--------|------|----------|
| 指纹/微信图片_20250629170752.jpg | 3,969,541 | 2025-06-29 17:07 |
| 指纹/微信图片_20250629170840.jpg | 4,200,357 | 2025-06-29 17:08 |
| 指纹/微信图片_20250629170849.jpg | 2,643,258 | 2025-06-29 17:08 |
| 指纹/微信图片_20250629170856.jpg | 2,707,845 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629170903.jpg | 4,644,415 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629170918.jpg | 5,015,791 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629170932.jpg | 5,878,349 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629170940.jpg | 5,885,424 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629170946.jpg | 2,165,700 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629170952.jpg | 4,124,290 | 2025-06-29 17:09 |
| 指纹/微信图片_20250629171001.jpg | 4,928,268 | 2025-06-29 17:10 |

**共 11 张照片，总计约 46MB。**

## 与 hash-manifest.json 的差异

`archive/hash-manifest.json` 中记录：

```json
{
  "path": "archive/evidence/flaw-image-provenance.tar",
  "sha256": "9a1f320758ba0882135171bb99ce0cd1312d85dd6d6ce6aa57d930665ca576bf",
  "size_bytes": 94556,
  "arweave_tx": "9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs"
}
```

但该 TxID 实际返回的是 46MB 的 ZIP 文件（内含 11 张 JPG），不是 94KB 的 tar 文件。

**可能原因**：
1. `flaw-image-provenance.tar` 曾经作为单独文件存在于 Arweave，后被替换为照片 ZIP 包
2. 或者 TxID 对应的是包含 tar 的上层 bundle，公共网关返回了 bundle 中的其他数据项
3. 哈希记录可能来自早期版本，后续 Arweave 数据发生了变化

**结论**：以 Arweave 链上实际返回的数据为准。本镜像保存的是链上实际数据。

## 下载遇到的问题与解决方案

### 问题 1：arweave.net 网关超时

从中国大陆或部分服务器访问 `arweave.net` 经常超时（>120秒无响应）。

**解决方案**：使用备用网关 `ar-io.dev`，速度更快且更稳定。

```bash
# 推荐
curl -L "https://ar-io.dev/<TxID>" -o output.bin

# 备选
curl -L "https://g8way.io/<TxID>" -o output.bin
```

### 问题 2：文件类型不是预期的 tar

下载后发现文件是 ZIP 格式（PK 头），而非预期的 tar 格式。

**解决方案**：先用 `file` 命令检测实际格式，再决定处理方式：

```bash
file downloaded.bin
# 如果是 Zip archive data:
unzip -l downloaded.bin
unzip downloaded.bin -d extracted/
```

### 问题 3：GitHub Actions 中 arbundles 提取失败

尝试使用 `arbundles` npm 包提取 ANS-104 bundle 中的数据项，但该 TxID 返回的并非标准 ANS-104 bundle 格式，而是普通 ZIP。

**解决方案**：直接用 `unzip` 解压即可，无需 arbundles。

### 问题 4：Git clone 大仓库失败

仓库包含 24MB 的 `public-covenant-archive.zip`，完整 clone 容易超时。

**解决方案**：使用 shallow clone 或 GitHub API 直接操作文件：

```bash
# Shallow clone
git clone --depth 1 <repo_url>

# 或使用 GitHub Contents API 直接上传文件（无需 clone）
curl -X PUT -H "Authorization: token <PAT>" \
  "https://api.github.com/repos/<owner>/<repo>/contents/<path>" \
  -d '{"message":"...", "content":"<base64>", "sha":"<existing_sha>"}'
```

## 镜像文件位置

- **原始数据（ZIP 包）**: `archive/evidence/flaw-archive-bundle.zip`
- **解压后的照片**: `archive/evidence/flaw-images/指纹/`
- **本说明文档**: `archive/evidence/FLAW-MIRROR-NOTES.md`

## 权威边界

本镜像为非修订守护材料。Arweave 原始数据和比特币铭文为最终权威。
如本镜像与链上数据冲突，以链上数据为准。
