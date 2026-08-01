# Trinity Accord External Binary Annexes

The core repository preservation DOI (`10.5281/zenodo.21739344`) remains unchanged and continues to restore the complete Git-tracked repository.

The external-binary annex series preserves the separately hosted public payload bytes:

1. **External Evidence Binary Annex**
   - `signed-large-data-mirror-v1`
   - `notarial-certificate-images-v1`
   - `flaw-covenant-video-mirror-v1`
   - `ots-proof-bundle-mirror-v1`
   - `ots-and-flaw-mirror-v1`
   - `flaw-covenant-archive-accessibility-mirror-v1`

2. **Chronicle NFT Media Binary Annex**
   - `nft-arweave-mirror-175-v1`
   - `nft-backup-v1`

Every custom GitHub Release asset from the named releases is embedded byte-for-byte in the relevant annex package. GitHub-generated source archives are excluded because the core repository DOI already preserves the source tree. Deprecated failed NFT attempts (`nft-individual-v1`, `nft-individual-v2`) are not promoted into the annex.

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
