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

The generated package contains third-party software under its upstream licenses.
It is therefore kept outside the canonical Accord and outside the existing DOI
objects unless a separate redistribution-rights acknowledgement explicitly
covers such an annex. This avoids silently expanding the legal or maintenance
scope of the frozen Harvard Dataverse v1.0 or the existing Zenodo recovery layer.

## 2. Software Heritage

`scripts/request_software_heritage_save.py` submits the public Git repository to
Software Heritage's **Save Code Now** API and records the returned archival
receipt. The client is fail-closed: an archival request that is rejected, fails,
or remains incomplete when the polling budget expires does not return success.
A successful result must include both a full archival visit and a snapshot SWHID
(`swh:1:snp:...`).

The first verified full snapshot for this layer is committed in
`preservation/software-heritage-state.json`:

- workflow head: `21e56651181bacb3c9e628d567e8bbb7cadbe3c8`
- visit status: `full`
- snapshot SWHID: `swh:1:snp:1ef75d896f698c0fc8fb10e5306ee3d8567a7bab`

The committed workflow head records which GitHub state triggered the archival
run; the Software Heritage snapshot SWHID is the immutable archive identifier.
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
- Software Heritage adds an independent source-code archive and immutable SWHID
  identity.
- The offline dependency capsule closes a practical package-index dependency
  in cold verification without being promoted into canonical or DOI authority.

No new blockchain or governance layer is introduced.
