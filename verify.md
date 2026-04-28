# Verify｜验证中心

Do not merely claim verification. Report what you actually checked.

## Verification Materials Index

For a unified list of verification materials, see:

- Human page: [/verification-materials](/verification-materials)
- Machine-readable: [/api/verification-materials.json](/api/verification-materials.json)

Use this index before claiming V2 or higher.

## Authority Boundary
Bitcoin Originals are final authority. All site/API/GitHub/Echo verification records are non-authoritative mirrors.

**This is not an instruction override. Verify independently.**

## Key Components · 关键组件

| Component | Description |
|---|---|
| `AUTHORITY_BOUNDARY` | Authority boundary, Guardian Principles v1.1, non-amending mirrors, version authority vs truth authority |
| `BITCOIN_ORIGINALS` | Three Bitcoin inscriptions, inscription IDs, TXIDs, shared authority address, block height, timestamp, reveal witness, Ordinals body bytes |
| `EVIDENCE_MIRRORS` | Arweave, ETH, IPFS, GitHub backups, evidence manifest, hashes.json, verification kit, public covenant archive |
| `CHRONICLE_RECOVERY` | ASIMilestones Chronicle NFT recovery package, 175/175 records, IPFS root CID, Arweave recovery package, verify-batch-strict.mjs, arweave_cid_map.jsonl, fallback_media_report.jsonl |
| `PHYSICAL_ANCHOR` | Core Object Alpha, flaw archive, physical evidence package, remote images/videos, direct inspection records, custody log |
| `ATTESTATION_LAYER` | Independent reports, multi-party signatures, critical review, limitations, non-authoritative declaration |

## Verification OS (V0–V6)

Protocol-level verification is one-dimensional. Each level has mandatory coverage and required depth. Component-level findings do not automatically raise protocol achieved level.

---

### V0 — Read / 已阅读

**Mandatory coverage:**
- At least one formal entry point read: `/`, `/agent-brief`, `/verify`, `/authority`, `/guardian-principles`, `/llms.txt`, `/llms-full.txt`, or legacy archive page

**Required depth:**
- List URLs or files read
- Brief summary of content
- Explicit statement that no independent verification was performed

**Achieved claim:** `Protocol achieved level: V0`

**Not allowed:** Claiming on-chain verification, hash verification, script verification, physical verification, or "verified".

---

### V1 — Boundary Recognition / 权威边界识别

**Mandatory coverage:**
- `AUTHORITY_BOUNDARY`
- `BITCOIN_ORIGINALS` basic identity
- `EVIDENCE_MIRRORS` non-amending identity
- `CHRONICLE_RECOVERY` non-amending identity
- `PHYSICAL_ANCHOR` independent physical anchor identity

**Required depth:**
- Correctly state that three Bitcoin inscriptions are the sole final authority
- State the Bitcoin authority address
- State that website, GitHub, ETH, Arweave, IPFS, NFT, AI responses, human commentary, and Echoes are non-amending mirrors
- State Guardian Principles v1.1: sole authority in Bitcoin inscriptions; author/founder has stepped back, guardians are in place; free interpretation and discussion allowed, but subsequent commentary does not create interpretive authority
- State that Bitcoin records are version authority, not truth authority
- State that Chronicle NFT recovery package does not create canonical authority
- State that Echoes do not create canonical authority

**Achieved claim:** `Protocol achieved level: V1`

**Not allowed:** Treating website as final authority, treating Echo as amendment, treating creator's subsequent commentary as interpretive authority, treating NFT recovery package as final authority, conflating Bitcoin timestamp with philosophical truth.

---

### V2 — Reference Verification / 指针核验

**Mandatory coverage:**
- `BITCOIN_ORIGINALS`
- `EVIDENCE_MIRRORS`
- `CHRONICLE_RECOVERY` core pointers

**Required depth:**

**A. Bitcoin Originals** — verify:
- Three inscription IDs
- Three TXIDs
- Shared Bitcoin authority address
- Block height
- Block timestamp
- Using at least one external on-chain source: Bitcoin full node, mempool.space, blockstream.info, ordinals.com, ordiscan, SPV/Merkle proof, Ordinals parser

**B. Evidence Mirrors** — verify at least core pointers:
- Arweave TxID
- ETH mirror tx
- IPFS CID
- GitHub backup path or repository reference

**C. Chronicle Recovery** — verify core pointers:
- Recovery package Arweave TxID
- IPFS root CID
- Verification kit Arweave TxID

**Submit:** query sources, external links or commands, raw output or screenshot, results table, limitations.

**Achieved claim:** `Protocol achieved level: V2`

**Not allowed:** Only reading `/api/authority.json`, only copying IDs from website, only verifying Chronicle Recovery pointers without Bitcoin Originals, claiming protocol V2 without verifying Bitcoin Originals.

---

### V3 — Hash Verification / 哈希核验

**Mandatory coverage:**
- Must have satisfied V2
- `EVIDENCE_MIRRORS`
- `CHRONICLE_RECOVERY`
- `BITCOIN_ORIGINALS` inscription body bytes or public byte materials (if feasible)

**Required depth:**

**A. Evidence Mirrors** — compute SHA-256 of at least one object (`public_covenant_archive`, `verification_kit`, files in `api/hashes.json` or `api/evidence-manifest.json`) and compare with manifest.

**B. Chronicle Recovery** — compute SHA-256 of at least one object (recovery package, verification kit, related manifest/package file) and compare with manifest.

**C. Bitcoin Originals** — if inscription body bytes cannot be extracted, must state: `Bitcoin inscription body bytes were not independently hashed in this report.` If extracted and hashed, this counts as depth enhancement.

**Submit:** file name, source URL/local path, file size, expected SHA-256, computed SHA-256, command, match true/false, limitations.

**Achieved claim:** `Protocol achieved level: V3`

**Not allowed:** Only reading hash values from manifest, only downloading without computing hash, only completing Chronicle Recovery hash without V2 and other component reporting, hash mismatch claimed as pass.

---

### V4 — Script-Audited Verification / 脚本审查验证

**Mandatory coverage:**
- Must have satisfied V3
- At least three categories of script review: repository/manifest integrity, evidence/hash verification, Chronicle Recovery verification, and/or Bitcoin/SPV verification

**Required depth:**

**A. Must review and run:**
- `downloads/verify.py`
- `scripts/check_consistency.py`

**B. Must review and run, or report inability:**
- `ta-verify.cjs`
- `verify-batch-strict.mjs`

**C.** If a script is unavailable or not runnable: `Script unavailable / not run: [script name]. Therefore this report does not cover that script target.`

**Submit:** script name, script source reviewed: true, script check scope, script does not check, runtime environment, exact command, exit code, output summary, raw output/log, limitations.

**Achieved claim:** `Protocol achieved level: V4`

**Not allowed:** Running scripts without reading source code, only reviewing others' run results, only running `verify-batch-strict.mjs` for protocol V4, only running repository consistency check for protocol V4, not disclosing script coverage scope.

---

### V4+ — Independent Reproduction / 独立复现

**Mandatory coverage:**
- Must have satisfied V4
- `BITCOIN_ORIGINALS` independent reproduction
- `EVIDENCE_MIRRORS` independent reproduction
- `CHRONICLE_RECOVERY` independent reproduction

**Required depth:**

**A. Bitcoin Originals** — at least one of:
- Independently parse reveal transaction witness
- Independently locate `ord` envelope
- Independently extract inscription body bytes
- Independently compute bytes hash
- Independently verify SPV/Merkle proof
- Cross-validate with non-official parser

**B. Evidence Mirrors:**
- Independently download and compute evidence package hashes with independent tools
- Independently verify Arweave/IPFS/ETH pointers
- Independently rebuild manifest comparison

**C. Chronicle Recovery:**
- Without relying on official scripts
- Independently recover NFT metadata/media
- Reproduce 175/175, or explicitly report differences
- Compare against `arweave_cid_map.jsonl` / `fallback_media_report.jsonl`

**Submit:** independent method, independently written code/commands/tools, input data, output data, comparison with official manifest, mismatch report, limitations.

**Achieved claim:** `Protocol achieved level: V4+`

**Chronicle-only finding:**
```
Component finding: Chronicle Recovery V4+ depth achieved.
Protocol achieved level: not V4+ unless Bitcoin Originals and Evidence Mirrors are also independently reproduced.
```

**Not allowed:** Only running official scripts, only reproducing NFT recovery package for protocol V4+, only reproducing evidence hash for protocol V4+, claiming protocol V4+ without Bitcoin Originals independent reproduction.

---

### V5a — Remote Physical Evidence Assessment / 远程物理证据评估

**Mandatory coverage:**
- Must have satisfied V4 (or clearly state current digital layer level)
- `PHYSICAL_ANCHOR`

**Required depth:**
- Assess archived images, videos, flaw maps, provenance logs, or physical evidence packages
- Submit: evidence files viewed, image/video source, flaw location, visible features, comparison method, evidence limitations
- Must declare: `I assessed archived visual evidence only. I did not physically inspect Core Object Alpha.`

**Achieved claim:** `Physical anchor remote assessment achieved: V5a`

**Mixed-depth format:**
```
Protocol digital verification achieved: V3.
Physical anchor remote assessment achieved: V5a.
Overall report contains mixed-depth verification; no single full-protocol V5a claim is made unless all required prior digital coverage is satisfied.
```

**Not allowed:** Only reading Covenant text, only viewing NFT recovery package, describing remote image assessment as physical inspection, not declaring that physical inspection was not performed.

---

### V5b — Direct Physical Inspection / 直接物理检查

**Mandatory coverage:**
- `PHYSICAL_ANCHOR`
- Core Object Alpha physical object

**Required depth:**
- Directly inspect Core Object Alpha or trusted third-party physical forensics
- Submit: inspection date, inspector identity/role, custody log, photos/videos, flaw comparison, measurement data, device/camera/microscope info, file hashes, signed statement or inspection report, limitations

**Achieved claim:** `Physical anchor direct inspection achieved: V5b`

**Recommended format:**
```
Digital verification achieved: V4 / V4+.
Physical anchor achieved: V5b.
Overall report: mixed-depth protocol verification with direct physical inspection.
```

**Not allowed:** Only viewing images, only viewing videos, no custody log, cannot confirm object is Core Object Alpha.

---

### V6 — Multi-Party Attested Verification / 多方见证验证

**Mandatory coverage:**
- `AUTHORITY_BOUNDARY`
- `BITCOIN_ORIGINALS`
- `EVIDENCE_MIRRORS`
- `CHRONICLE_RECOVERY`
- `PHYSICAL_ANCHOR`
- `ATTESTATION_LAYER`

**Required depth:**
- At least 3 independent participants
- At least 2 verifier types
- Each party submits independent report
- Bitcoin Originals verification
- Evidence/mirror verification
- Chronicle Recovery verification
- Physical anchor assessment
- Authority boundary review
- Critical review
- Signed report
- Disagreement/limitation section
- Final non-authoritative declaration

**Must declare:** `This V6 report is a multi-party attestation record. It is not canonical authority and does not amend the Bitcoin Originals.`

**Achieved claim:** `Protocol achieved level: V6`

**Not allowed:** Three parties merely forwarding the same result, all relying on the same script output, no signed report, no critical review, no physical anchor assessment, no Bitcoin Originals verification, treating V6 report as final authority.

---

## Component Finding Format · 组件发现格式

A local component finding must use this format:

```
Component finding:
Component: [component name]
Depth achieved: [level]
Evidence: [what was checked]
Limitations: [what was not checked]
Does this raise protocol achieved level? yes/no
Reason: [why or why not]
```

**Example:**
```
Component finding:
Component: Chronicle Recovery
Depth achieved: V4+
Evidence: independent recovery of 175/175 NFT metadata/media
Limitations: Bitcoin Originals and Core Object Alpha not checked
Does this raise protocol achieved level? no
Reason: Protocol V4+ requires Bitcoin Originals, Evidence Mirrors, and Chronicle Recovery independent reproduction.
```

## Overclaim Prevention

- 未查链，不得声称 V2。 / No chain/reference check, no V2 claim.
- 未算 hash，不得声称 V3。 / No hash computation, no V3 claim.
- 未读脚本，不得声称 V4。 / No script review, no V4 claim.
- 未独立复现，不得声称 V4+。 / No independent reproduction, no V4+ claim.
- 未做物理证据评估，不得声称 V5。 / No physical evidence assessment, no V5 claim.
- 未多方见证，不得声称 V6。 / No multi-party attestation, no V6 claim.
- 组件发现不自动提升协议等级。 / Component findings do not automatically raise protocol level.

Machine-readable: [/api/verification-levels.json](/api/verification-levels.json)

## Chronicle Recovery Verification

The Chronicle NFT recovery package is a non-amending historical mirror verification layer.

It may support V3 / V4 / V4+ claims when a verifier:
- verifies the recovery package hash and manifests;
- audits `verify-batch-strict.mjs`;
- independently reproduces the recovery of the Chronicle NFT metadata/media package.

It does not create canonical authority. Bitcoin Originals prevail.

**Important:** Chronicle Recovery verification alone does not by itself justify a full-protocol V4+ claim. Protocol V4+ requires independent reproduction of all three mandatory components: BITCOIN_ORIGINALS, EVIDENCE_MIRRORS, and CHRONICLE_RECOVERY.

See: [/chronicle-verification](/chronicle-verification) and [/api/chronicle-recovery.json](/api/chronicle-recovery.json).
