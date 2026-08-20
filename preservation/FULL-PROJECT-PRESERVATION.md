# Full Project Preservation Bundle

This package is a **non-amending preservation mirror**. It is not Canon, an
interpretation, governance, succession, attestation, or a new Chronicle. The three
Bitcoin Originals remain the only canonical and interpretive authority. The
Ethereum Chronicle remains the same 175-entry corpus referenced by the third
Bitcoin Original. Polygon/Base material remains a separate noncanonical
Cross-chain Formation Record.

## Purpose

Build one independently portable set that can be transferred to a second
institutional repository without recollecting the project from live services.
The staging bundle contains:

1. a safe exact current repository preservation capsule, including source tree,
   tracked-file inventory, checksums and GitHub-zero restore program;
2. **every custom asset exposed by every GitHub Release**, enumerated through the
   paginated Release Assets API and downloaded byte-for-byte;
3. a fresh public readback of every file in the published Polygon/Base sidechain
   DOI `10.5281/zenodo.22012616`, checked against the repository's recorded
   SHA-256 map; and
4. a top-level SHA-256 content-addressed object store, manifest and offline
   verifier/restorer.

Release assets and DOI files with identical SHA-256 are stored only once in the
object store while every original logical provenance path remains in the manifest.
This reduces storage without weakening byte identity.

## Ethereum / NFT / media coverage

The current repository capsule includes the Git-tracked Ethereum witnesses,
proof-carrying evidence, 175-entry Chronicle indices, verifiers and recovery
catalog. The complete Release scan additionally captures the public source assets
used by the existing Evidence and Chronicle NFT media annexes, including video,
images, signed-data mirrors, OTS material and the content-complete NFT backup
Release. The existing immutable annex DOIs remain separately discoverable through
`preservation/recovery-catalog.json`; the new full-project staging bundle preserves
their underlying public Release source bytes rather than nesting another copy of
large `payload.tar` wrappers.

## Polygon / Base boundary

The sidechain source is not rebuilt. The workflow downloads the exact already
published DOI files and requires the recorded archive SHA-256:

`64152b7fc861dbf8aa9cec447ab7078a6a815136ccfc1b9bb0285aaca2ff1572`

The known historical boundary remains explicit: 217/217 L2 records pass, 250/257
IPFS roots have exact preserved CARs, and 7 historical payload roots remain
unresolved. Preservation does not convert those seven missing historical payloads
into recovered data.

## Security boundary

"All repository files" means all files in the safe current publication baseline.
It deliberately does **not** mean republishing unsafe parent-history/tag Git blobs.
A historical Git object briefly contained a leaked credential. The established
repository preservation capsule therefore uses a safe single-root recovery bundle
and does not immutably redistribute that compromised history. This is a security
boundary, not a missing current-source backup.

## External institutional copy

The GitHub workflow only builds and verifies a staging artifact. It performs no
Arweave write and no automatic external publication.

Harvard Dataverse does not use GitHub OAuth as its depositor login. A Dataverse
account/API token is required for API upload. The Dataverse Native API accepts the
API token in `X-Dataverse-key`; the token must be stored as a GitHub Actions secret
if an automated external upload is later enabled. No Dataverse credential is
stored in this repository.

Before any external publication, the receiving dataset should retain:

- the exact bundle identity SHA-256;
- the exact current source commit/tree;
- the complete Release enumeration counts;
- every content-addressed object and its SHA-256/size;
- the sidechain DOI source binding and seven-root historical limitation; and
- this non-amending authority boundary.

## Offline verification

After extracting the staged artifact:

```bash
python3 verify-and-restore-full-project.py --bundle-dir .
```

To reconstruct all logical source paths into a new directory:

```bash
python3 verify-and-restore-full-project.py \
  --bundle-dir . \
  --materialize-dir ./restored
```

The verifier fails closed on a missing object, size/hash mismatch, duplicate logical
path, invalid bundle identity, or any change to the canonical-authority boundary.
