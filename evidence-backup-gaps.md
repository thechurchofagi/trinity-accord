---
title: "Evidence Backup Gaps and Cautions"
permalink: /evidence-backup-gaps/
---

# Evidence Backup Gaps and Cautions

## Summary

No critical backup gap is currently identified.

The major evidence families have Bitcoin / OTS / manifest coverage, Arweave availability, GitHub repository mirrors, GitHub Release mirrors, or a combination of these with SHA-256 based verification paths.

The remaining items are cautions and optional hardening tasks.

## Gaps / Cautions

| Item | Severity | Description | Recommended Action |
|---|---|---|---|
| OTS not local-node/fullnode independent | Medium | OTS proof is complete and Bitcoin-anchored, but not yet verified through local Bitcoin Core / pruned-node RPC | Run local-node OTS verification when available |
| OTS bundle v1 not fully self-contained | Low / Medium | OTS bundle contains proof artifacts and records, but client-level verification may still require original digest-manifest.json/csv from repository or another mirror | Optional OTS bundle v2 including original timestamped files |
| Release asset count ambiguity | Low | GitHub pages include source archives, causing asset count to differ from custom evidence asset count | Always report custom evidence assets separately |
| Guardian Attestation terminology | Low | It may be mistaken as part of the three canonical originals | Always describe it as Bitcoin-inscribed non-amending fortification |
| ETH witness count terminology | Low | authority.jcs.json records 7 items while verification-report confirms 8/8 including Guardianship Principles v1.1 | Use "ETH witness verification: 8/8 PASS" |
| Legacy homepage external pointer coverage | Low | Dedicated human- and machine-readable coverage registries now enumerate 35 Arweave records, 10 Ethereum non-NFT records, and IPFS pointers. Two small AR raw payloads remain unresolved. | Maintain `LEGACY-POINTER-COVERAGE.md` and `archive/legacy-pointers/index.json`; retrieve the two raw gaps when a functioning gateway or owner export is available |
| Authority v1.0.2 hash semantics | Medium | The signed `7d6a...` value is a covered JCS digest, not established as the Arweave transaction payload SHA-256; the current asset manifest therefore reports a semantic false-positive mismatch | Correct the manifest generator before changing any mirrored authority file |
| Arweave/GitHub authority confusion | Medium | Mirrors may be mistaken for canonical authority | Repeat boundary statement in all summary docs |
| Large payload repository risk | Low | Videos/tar/CAR files should not be committed to repository tree | Keep large payloads in Arweave and GitHub Releases only |
| Gateway availability for large ZIPs | ~~Medium~~ → Resolved | arweave.net returned 404 for large flaw archive ZIPs | ✅ Resolved: GitHub Release `flaw-covenant-archive-accessibility-mirror-v1` created as non-amending accessibility mirror |

## Not Considered Gaps

The following are not evidence-chain failures:

- GitHub not being canonical authority
- Arweave being a payload mirror rather than authority
- ETH being witness rather than authority
- OTS bundle mirror not being fullnode-independent OTS verification
- Deprecated NFT releases existing as historical artifacts
- GitHub release pages showing source archives in asset count
- Gateway availability for large Arweave payloads (mitigated by GitHub Release accessibility mirror)
- Reusing the exact Bitcoin inscription raw-text mirror when an Ethereum data transaction has the identical byte length and SHA-256
- Deliberately withholding sealed/non-public evidence from the public GitHub mirror

## Optional Hardening Tasks

1. Create `OTS proof bundle v2` with:
   - digest-manifest.json
   - digest-manifest.csv
   - digest-manifest.json.ots
   - digest-manifest.csv.ots
   - verify-report.json
   - verify-report.json.ots
   - checksums and manifest

2. Complete the remaining raw-payload retrievals listed by `archive/legacy-pointers/index.json`:
   - merged Guardian Index `mGW-QQyGyoNIybMghqZYo6PFhQIk44lbBy7_dNB4e2s`
   - Guardianship system docs v1 `I0xNBwbgaGsODjnK5ze25sOwV9V8i7FtKe-8upRoohw`
   - isolate currently metadata-only Ethereum readable payloads only after decoded bytes reproduce the chain-recorded length and SHA-256

3. Add Guardian Attestation to the top-level evidence relationship diagram as:
   - non-amending Bitcoin-inscribed fortification
   - not a fourth canonical original

4. Run fullnode-independent OTS verification using:
   - local Bitcoin Core
   - or pruned-node RPC
   - and record result separately

## Final Gap Determination

Current status:

```text
Critical gaps: none identified
Major payload backup gaps: none identified
Small raw-pointer payload gaps: 2 identified and explicitly registered
Documentation mapping: completed; maintain periodically
Optional hardening: recommended
Evidence amendment risk: controlled by existing boundary statements
```
