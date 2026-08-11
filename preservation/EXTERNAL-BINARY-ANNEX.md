# Trinity Accord External Binary Annexes

<!-- BEGIN CORE DOI BASELINE RULE -->
The core concept DOI `10.5281/zenodo.21739343` resolves the latest published core
repository version. Each version restores the exact source commit named in its
manifest; no version is a live mirror of a later moving GitHub `main`. The embedded
`preservation/recovery-catalog.json` supplies both annex DOI identifiers without
requiring GitHub.
<!-- END CORE DOI BASELINE RULE -->

Core version DOI `10.5281/zenodo.21739344` restores the historical baseline at commit `484bdd7a85694ad53fe7e6e9dcea94d0dee5617e`; use concept DOI `10.5281/zenodo.21739343` to resolve the latest published core version.

The external-binary annex series preserves the separately hosted public payload bytes:

1. **External Evidence Binary Annex**
   - `signed-large-data-mirror-v1`
   - `notarial-certificate-images-v1`
   - `flaw-covenant-video-mirror-v1`
   - `ots-proof-bundle-mirror-v1`
   - `ots-and-flaw-mirror-v1`
   - `flaw-covenant-archive-accessibility-mirror-v1`

2. **Chronicle NFT Media Binary Annex**
   - `nft-arweave-mirror-175-v1` — historical Release metadata only; the complete paginated asset observation found zero custom assets, so its text is not treated as byte evidence
   - `nft-backup-v1` — ten embedded package assets whose manifest covers 175 NFTs, 434 Arweave transactions/files, four contracts, 434 successful downloads, and zero failed downloads

Every custom GitHub Release asset actually observed through the complete paginated API listing is embedded byte-for-byte in the relevant annex package. For the NFT annex, all ten payload assets come from `nft-backup-v1`; the empty historical Release contributes no payload bytes. GitHub-generated source archives are excluded because the core repository DOI already preserves the source tree. Deprecated failed NFT attempts (`nft-individual-v1`, `nft-individual-v2`) are not promoted into the annex.

Each annex contains:

- `payload.tar`
- `annex-manifest.json`
- `checksums.sha256`
- `README.txt`
- `restore-trinity-annex.py`
- `zenodo-metadata.json`

The workflow requires exact owner authorization, a versioned rights acknowledgement, the existing Zenodo secret, complete release-asset downloads, exact size and SHA-256 verification, authenticated Zenodo upload readback, unauthenticated public download verification, and a second DOI-only cold restore.

## Rights and authority boundary

All embedded bytes were already publicly released. The Zenodo records use open file visibility so that preservation recovery is possible, together with the `other-closed` rights identifier and an explicit statement that the deposit grants no new reuse rights. Components retain their existing rights and third-party rights are not transferred.

The annexes are non-amending mirrors. They are not canonical authority, attestation, governance, verification level, successor reception, or investment representation. The Bitcoin Originals remain final.
