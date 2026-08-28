# Preservation Portability Layer

This layer strengthens recovery without changing the Trinity Accord originals,
authority model, attestation model, governance boundary, or successor relation.

## 1. Offline dependency capsule

`scripts/build_offline_dependency_capsule.py` creates a preservation package
containing:

- a complete Python wheelhouse for the current CI platform, including transitive
  dependencies needed by `requirements-ci.txt`;
- source distributions for every distribution in pip's resolved Python dependency
  graph;
- the repository's Node `package.json` / `package-lock.json` pairs;
- every npm registry tarball referenced by those lock files;
- npm SRI verification results and an independent SHA-256 manifest for every
  preserved payload.

The `Preservation Portability` workflow then proves the important claim rather
than merely documenting it:

1. it creates a new Python virtual environment;
2. it installs with `pip --no-index` from the preserved wheelhouse;
3. it runs `scripts/audit_recovery_readiness.py`;
4. it seeds isolated npm caches from only the preserved `.tgz` files;
5. it runs `npm ci --offline` for both the root Arweave tooling and the Ethereum
   proof-verification tooling.

The source-distribution set is a future-portability aid. It does not claim that
an arbitrary future CPU/OS/ABI can rebuild every dependency without a suitable
compiler and language toolchain.

## 2. Software Heritage

`scripts/request_software_heritage_save.py` submits the public Git repository to
Software Heritage's **Save Code Now** API and records the returned archival
receipt. When the archival visit completes, the receipt contains the snapshot
SWHID (`swh:1:snp:...`).

The SWHID is a software-preservation identifier. It is not a Trinity Accord
original and does not create or modify canonical authority.

The workflow requests a new visit when this preservation layer changes and once
per quarter. Pull requests only test the offline dependency portion; they do
not create external archival requests.

## 3. Relationship to existing DOI preservation

This layer is additive:

- Harvard Dataverse v1.0 remains frozen and is not amended by this mechanism.
- Existing Zenodo repository/cold-recovery publication logic remains the DOI
  recovery layer.
- Software Heritage adds a source-code archive and SWHID identity.
- The offline dependency capsule closes a practical package-index dependency
  in cold verification.

No new blockchain or governance layer is introduced.
