# 《余晖》加密创作纪念存档 / Yu Hui encrypted capsule

This is the author's chosen record of a human–AI collaborative novel. It is a
literary work, not a research paper, priority certificate, or amendment to the
Trinity Accord. No particular AI model or independently verified first is claimed.

## 中文说明

公开材料只含密文、版本指纹、计算谜题、解码程序及证明。小说正文不公开上传。
作者选择让未来的人自行求解，不保留恢复密码或恢复密钥。原文仍可由作者私下保存；
不保留密钥并不意味着小说原稿被销毁，也不保证运行环境中的内存痕迹可被法证清除。

难度已经从先前讨论的 112 位方案降低为 **48 位均匀随机密码 + 120 万轮 PBKDF2**。
这是可并行穷举的计算谜题，**不是按日历到期自动解锁的时间锁**。
平均约需检查 2^47 个候选；最坏枚举 2^48 个候选。幸运的求解者可能很早命中。

按本包 cost-model.json 的公开基准和每小时 0.24 美元的抢占式 RTX 5090 报价推算，
平均费用约 101 万美元；该价格与基准不是本次现场租机实测。它不是最低费用保证，
也不是“全球一年算力”的认证。更便宜的自有硬件、ASIC、优化、量子计算或算法突破
均可能降低成本；未来价格与硬件变化也可能提高成本。作者已接受提前解锁风险。

允许保存、传播本完整加密包和证明材料，允许运行公开求解算法，并允许解密后个人
非商业阅览。小说的转载、再发行、改编、翻译、对公众传播等权利不因解密而自动授予；
法律规定的例外除外。小说不适用论文的 CC BY 4.0 许可。
目前没有上架链接；如果作者今后推出正版或付费阅读服务，欢迎通过其公布渠道支持。

## Exact format and independent recovery

1. Enumerate all 12-character lowercase ASCII hexadecimal passwords, including
   leading zeroes: `000000000000` through `ffffffffffff` (2^48 possibilities).
2. Decode the 16-byte salt from capsule.json. Compute PBKDF2-HMAC-SHA256 with
   exactly 1,200,000 iterations. Its first 32 output bytes are public only as a
   candidate verifier. A candidate matches when these equal verifier_base64.
3. For a matching candidate, derive 64 bytes with the SAME password, salt and
   iteration count. The AES-256 key is bytes 32..63 (PBKDF2 block 2), NOT the
   published first block. Publishing block 1 does not publish block 2.
4. Decode nonce, AAD and ciphertext from standard Base64. AES-256-GCM uses the
   12-byte nonce and the exact decoded AAD. The final 16 ciphertext bytes are
   the authentication tag. Authenticate before saving plaintext.
5. Verify plaintext byte count and SHA-256 against the capsule commitment.

The ciphertext is UTF-8 Markdown plus a Chinese rights/preservation page.
The story body is byte-for-byte preserved from the supplied manuscript. The
original uploaded-file digest and story-body digest are also committed.

Install Python and `cryptography`, then:

```sh
python3 unlock.py capsule.json hashcat --out verifier.hashcat
hashcat -m 10900 -a 3 -1 0123456789abcdef verifier.hashcat '?1?1?1?1?1?1?1?1?1?1?1?1'
# Save the recovered 12-character candidate in password.txt, then:
python3 unlock.py capsule.json decrypt --password-file password.txt --out yuhui.md
```

Hashcat is optional. The reference Python solver supports bounded resumable ranges:

```sh
python3 unlock.py capsule.json search --start 0 --count 100 --checkpoint range0.json --out yuhui.md
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Different machines can search disjoint ranges. The Python implementation is a
correctness reference, not an optimized GPU solver. The corpus's full secret was
sampled with the OS-backed cryptographic RNG, used only in process memory,
checked by authenticated full recovery, then omitted from all retained outputs.

## Evidence and completion

MANIFEST.json binds the exact public files. Its detached .ots proof establishes
existence of the manifest and transitively the listed hashes, not legal authorship,
literary merit, or an earlier private writing date. Initial calendar receipts are
pending, not Bitcoin-verified. The workflow reuses the repository's dual-provider
Bitcoin-header verification; this is not local full-node consensus verification.
Arweave completion is claimed only after a transaction and SHA-256 readback match.
Check status.json for actual progress. No DOI or paper license is implied.

## Reference code permission

The author permits copying, modifying and distributing the supplied unlock.py
and test_unlock.py for recovery and verification, without warranty. This narrow
code permission does not license the novel's prose. Public preservation metadata
and cryptographic evidence may be copied with the complete capsule.
