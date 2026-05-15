## Context

Commit `cdae9bc` completed a repository size audit. Key finding:

The 10 JPG files in `evidence/notarial-certificate-2026-05-13/公证书/` total **38 MiB** and are the dominant working-tree cost. They currently have **no external backup** — not in GitHub Release, Arweave, IPFS, or any manifest.

| File | Size | SHA-256 |
|------|------|---------|
| file_1.jpg | 4.54 MiB | `b36c4d3019370c458280e0b0ee45f19933a124a61f935aa2e24e605d00bd5275` |
| file_2.jpg | 4.61 MiB | `e7c6e3a8af679a328b709099d751a97bea0d2488a975fc2a914ba186529d1119` |
| file_3.jpg | 3.56 MiB | `f55694d77245e38734f92601213047910fef151f53b0f43cff75ea1177e9844f` |
| file_4.jpg | 3.52 MiB | `2098bb46e6ef5a10cbd0c95848b4bed7cc4b1cf12a019615c2d5d878bc89e01b` |
| file_5.jpg | 4.00 MiB | `519c68b1fd8af3c247b4e2c780d3fcf7183706cc623f0eef5b1876cfa6351638` |
| file_6.jpg | 4.03 MiB | `7c3a45d78442bb07efe9f542a600eeb425a7fb0061e979e4afb2c616bab33bf8` |
| file_7.jpg | 3.20 MiB | `d0838164df09c5298d90b546fae938640cf7bcdcb934a092ebbcae0024754ae1` |
| file_8.jpg | 3.61 MiB | `a7af5e60a8863c6548c373d60e2f73fbc2c63d8250d09dbdb53e391c96424e1a` |
| file_9.jpg | 3.00 MiB | `fbf6218b993b5eef261a1865bf56c26d0e14f160f3b0e5613a91379fd61e321d` |
| file_10.jpg | 3.96 MiB | `fb5edcf4d4737a4a79ee92727760c8a467990fc36a804b3c5ba872e363f95854` |

These JPGs are:
- Referenced only by `evidence/notarial-certificate-2026-05-13/证据保全公证完整档案.md` (with SHA-256 checksums)
- Not rendered by any site page or API endpoint
- Not in `RELEASE-LARGE-DATA-MANIFEST.json`, `archive/hash-manifest.json`, or `api/evidence-manifest.json`

## Decision needed

**Migrate these 10 JPGs to GitHub Release or Arweave, and replace Git copies with manifest entries?**

If approved, the migration PR would:
1. Upload 10 JPGs to a new or existing GitHub Release (or Arweave)
2. Create a manifest entry (path, sha256, size, description, release asset name, non-amending boundary, verification command)
3. Replace the Git copies with the manifest file
4. Update `证据保全公证完整档案.md` to reference the manifest instead of direct files
5. Update `RELEASE-LARGE-DATA-MANIFEST.json` or create a dedicated manifest

**Estimated savings:** ~38 MiB working tree reduction.

## Not in scope
- No history rewrite (`git filter-repo`)
- No thumbnail generation (Plan C deferred)
- No changes to other evidence files

## Related
- Audit report: `audit/repo-size/20260515T005808Z/report.md`
- Size policy: `docs/repository-size-policy.md`
