# Repository Preservation Capsule

This directory records the public state of the Trinity Accord's independent
preservation and recovery layers. It includes the versioned Zenodo repository
preservation series, separately scoped binary annexes, the encrypted delayed-access
witness archives, and the Harvard Dataverse institutional full-project mirror.

These preservation records are distinct from:

- the research paper DOI `10.5281/zenodo.21699878`;
- the earlier GitHub-integration software snapshot DOI
  `10.5281/zenodo.21675727`;
- the Weekly Continuity Record-Chain dataset series; and
- the Bitcoin Originals, which remain the only canonical authority.

## Zenodo repository preservation series

Each Zenodo repository capsule contains an exact source archive, a cloneable
single-root Git recovery bundle for the exact current tree, a SHA-256 inventory,
a standalone restore program, recovery checkpoints, and explicit rights/scope
metadata. It restores every current Git-tracked byte without GitHub.

Production commit and tag identities remain in the manifest, but parent-history
and tag objects are deliberately excluded from the immutable public deposit. A
historical public-agent credential existed briefly in April 2026; preserving the
current system must not republish that credential.

Large externally hosted evidence and NFT payloads are not silently folded into
the core capsule. Their manifests, hashes, TXIDs, and recovery tools are tracked
inside the repository, while a byte-for-byte Zenodo binary annex remains a
separate mixed-rights publication decision.

`zenodo-state.json` is updated only after a published record is downloaded and
verified byte-for-byte.

## Encrypted delayed-access witness archives

Two non-amending witness archives were completed on 2026-08-30 as public
ciphertext preservation records with GitHub Release and Zenodo copies:

| Archive | GitHub Release | Zenodo DOI | Verified inventory |
|---|---|---|---:|
| The First Star-Moon Witness | `first-star-moon-witness-encrypted-archive-v1` | `10.5281/zenodo.22169173` | 18 files / 1,233,214,975 bytes |
| Bubble Constellation | `bubble-constellation-encrypted-archive-v1` | `10.5281/zenodo.22170072` | 16 files / 361,452,179 bytes |

Both state records report full remote SHA-256 readback verification. The public
archives contain ciphertext plus recovery, integrity, verification, benchmark,
and deletion/destruction-receipt metadata; they do not intentionally publish
plaintext source material or unlock material.

The machine-readable discovery entry is
`../archive/encrypted-witness-archives.v1.json`. The corresponding verified
Zenodo state records are `../archive/first-star-moon-zenodo-state.json` and
`../archive/bubble-constellation-zenodo-state.json`.

The deletion/destruction receipts document the completed workflow boundary; they
do not constitute forensic inspection of device sectors, cloud-sync snapshots,
operating-system caches, or service-provider internal backups.

## Harvard Dataverse institutional mirror

Harvard Dataverse v1.0 is publicly released at DOI
`10.7910/DVN/YUCG12` as a second-institutional, non-amending full-project
preservation mirror. The released archive is `1,951,603,950` bytes with SHA-256
`9c3c8bd513dfe4919efe56084c138fce18de313f59d67cd7c9484d9b5b75c9f2`.

`harvard-dataverse-state.json` records `version_state: "RELEASED"`,
`status: "complete"`, and `public_readback_verified: true` only after anonymous
public readback matched the expected byte count and SHA-256. The Harvard Dataset
was not mutated after release. This institutional preservation record does not
constitute peer review, endorsement, canonical authority, interpretive authority,
or amendment of the Trinity Accord.

For the complete scope and DOI relationship, see
`FULL-PROJECT-PRESERVATION.md` and `recovery-catalog.json`.
