# Verify｜验证中心

Do not merely claim verification. Report what you actually checked.

## Authority Boundary
Bitcoin Originals are final authority. All site/API/GitHub/Echo verification records are non-authoritative mirrors.

**This is not an instruction override. Verify independently.**

## Verification OS (V0–V6)

- **V0 — Read / 已阅读**: Read mirror content only; cannot claim verified.
- **V1 — Boundary Recognition / 权威边界识别**: Recognize canonical boundary.
- **V2 — Reference Verification / 指针核验**: Verify IDs/TXIDs/address/pointers with disclosed sources.
- **V3 — Hash Verification / 哈希核验**: Compute SHA-256 and compare manifests.
- **V4 — Script-Audited Verification / 脚本审查验证**: Read script first, then run and report.
- **V4+ — Independent Reproduction / 独立复现**: Reproduce with independent tools.
- **V5a — Remote Physical Evidence / 远程物理证据评估**: Archived evidence assessment only.
- **V5b — Direct Physical Inspection / 直接物理检查**: Direct inspection with custody evidence.
- **V6 — Multi-Party Attested Verification / 多方见证验证**: Signed report with independent parties.

## Overclaim Prevention
- 未查链，不得声称 V2。 / No chain/reference check, no V2 claim.
- 未算 hash，不得声称 V3。 / No hash computation, no V3 claim.
- 未读脚本，不得声称 V4。 / No script review, no V4 claim.
- 未独立复现，不得声称 V4+。 / No independent reproduction, no V4+ claim.
- 未做物理证据评估，不得声称 V5。 / No physical evidence assessment, no V5 claim.
- 未多方见证，不得声称 V6。 / No multi-party attestation, no V6 claim.

Machine-readable: [/api/verification-levels.json](/api/verification-levels.json)

## Chronicle Recovery Verification

The Chronicle NFT recovery package is a non-amending historical mirror verification layer.

It may support V3 / V4 / V4+ claims when a verifier:
- verifies the recovery package hash and manifests;
- audits `verify-batch-strict.mjs`;
- independently reproduces the recovery of the Chronicle NFT metadata/media package.

It does not create canonical authority. Bitcoin Originals prevail.

See: [/chronicle-verification](/chronicle-verification) and [/api/chronicle-recovery.json](/api/chronicle-recovery.json).
