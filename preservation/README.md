# Repository Preservation Capsule

This directory records the public state of the independent Zenodo series for
full Git-tracked repository recovery.

The preservation capsule is distinct from:

- the research paper DOI `10.5281/zenodo.21699878`;
- the earlier GitHub-integration software snapshot DOI
  `10.5281/zenodo.21675727`;
- the Weekly Continuity Record-Chain dataset series.

Each capsule contains an exact source archive, a cloneable single-root Git
recovery bundle for the exact current tree, a SHA-256 inventory, a standalone
restore program, recovery checkpoints, and explicit rights/scope metadata. It
restores every current Git-tracked byte without GitHub.

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
