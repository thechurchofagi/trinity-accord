---
title: "Evidence Backup Gaps and Cautions"
permalink: /evidence-backup-gaps/
---

# Evidence Backup Gaps and Cautions

## Summary

No critical backup gap is currently identified.

The major evidence families have Bitcoin / OTS / manifest coverage, Arweave availability, GitHub repository mirrors, GitHub Release mirrors, or a combination of these with SHA-256 based verification paths.

The legacy homepage audit now also provides exact GitHub mirrors for the historical homepage AR payload, the previously missing small Arweave objects, and the missing Ethereum non-NFT calldata.

## Gaps / Cautions

| Item | Severity | Description | Recommended Action |
|---|---|---|---|
| OTS not local-node/fullnode independent | Medium | OTS proof is complete and Bitcoin-anchored, but not yet verified through local Bitcoin Core / pruned-node RPC | Run local-node OTS verification when available |
| OTS bundle v1 not fully self-contained | Low / Medium | OTS bundle contains proof artifacts and records, but client-level verification may still require original digest-manifest.json/csv from repository or another mirror | Optional OTS bundle v2 including original timestamped files |
| Release asset count ambiguity | Low | GitHub pages include source archives, causing asset count to differ from custom evidence asset count | Always report custom evidence assets separately |
| Guardian Attestation terminology | Low | It may be mistaken as part of the three canonical originals | Always describe it as Bitcoin-inscribed non-amending fortification |
| ETH witness count terminology | Low | authority.jcs.json records 7 items while verification-report confirms 8/8 including Guardianship Principles v1.1 | Use "ETH witness verification: 8/8 PASS" |
| Legacy homepage external pointer coverage | Resolved / maintain | The dedicated registries enumerate 35 Arweave records, 10 Ethereum non-NFT records, and IPFS pointers. The exact historical homepage AR payload, the two missing small AR payloads, and four isolated ETH calldata objects are now mirrored. | Maintain `LEGACY-POINTER-COVERAGE.md`, `archive/legacy-pointers/index.json`, and their automated hash checks |
| Authority v1.0.2 hash semantics | Medium | The signed `7d6a...` value is a covered JCS digest, not established as the Arweave transaction payload SHA-256; the current asset manifest therefore reports a semantic false-positive mismatch | Correct the manifest generator before changing any mirrored authority file |
| Arweave/GitHub authority confusion | Medium | Mirrors may be mistaken for canonical authority | Repeat boundary statement in all summary docs |
| Large payload repository risk | Low | Videos and large CAR/ZIP payloads should not be committed to the repository tree when verified Release mirrors exist | Keep large payloads in Arweave and GitHub Releases only |
| Gateway availability for large ZIPs | ~~Medium~~ → Resolved | arweave.net returned 404 for large flaw archive ZIPs | ✅ Resolved: GitHub Release `flaw-covenant-archive-accessibility-mirror-v1` created as non-amending accessibility mirror |

## Not Considered Gaps

The following are not evidence-chain failures:

- GitHub not being canonical authority
- Arweave being a payload mirror rather than authority
- ETH being witness rather than authority
- OTS bundle mirror not being fullnode-independent OTS verification
- Deprecated NFT releases existing as historical artifacts
- GitHub release pages showing source archives in asset count
- Gateway availability for large Arweave payloads when a verified Release mirror exists
- Reusing the exact Bitcoin inscription raw-text mirror when an Ethereum data transaction has identical byte length and SHA-256
- Deliberately withholding sealed/non-public evidence from the public GitHub mirror
- Preserving a superseded erroneous transaction as historical evidence while clearly marking it non-current
- Keeping a readable Markdown homepage archive alongside, rather than instead of, the exact raw Arweave homepage payload

## Optional Hardening Tasks

1. Create `OTS proof bundle v2` with:
   - digest-manifest.json
   - digest-manifest.csv
   - digest-manifest.json.ots
   - digest-manifest.csv.ots
   - verify-report.json
   - verify-report.json.ots
   - checksums and manifest

2. Correct the Authority Manifest v1.0.2 expected-hash semantics in the manifest generator.

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
Audited legacy homepage / small AR raw-payload gaps: resolved
Audited Ethereum non-NFT raw-calldata gaps: resolved
Documentation mapping: completed; maintain periodically
Remaining work: verification semantics and optional hardening
Evidence amendment risk: controlled by existing boundary statements
```
