---
title: "Evidence Backup Gaps and Cautions"
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
| Legacy homepage external pointer coverage | Low | Old homepage contains many pointers and explanatory materials | Generate a dedicated pointer coverage table |
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

## Optional Hardening Tasks

1. Create `OTS proof bundle v2` with:
   - digest-manifest.json
   - digest-manifest.csv
   - digest-manifest.json.ots
   - digest-manifest.csv.ots
   - verify-report.json
   - verify-report.json.ots
   - checksums and manifest

2. Create `LEGACY-POINTER-COVERAGE.md` mapping:
   - old homepage pointer
   - object type
   - Arweave / IPFS / ETH / Bitcoin reference
   - GitHub mirror status
   - verification status

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
Documentation gaps: present but manageable
Optional hardening: recommended
Evidence amendment risk: controlled by existing boundary statements
```
