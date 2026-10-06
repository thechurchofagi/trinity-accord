# R105 — DOI release and preservation lifecycle status

Date: 2026-10-06.

User authorized archival publication with DOI, OTS and Arweave using the repository's mature paper process, after deciding whether a strict formal map was necessary.

## Formal audit

The release branch `research/self-continuation-control-v1-20261006` already contains a strict formal release map and audit for TA-TR-2026-24 v1.0.

Decision: `FORMAL_RELEASE_AUDIT_PASS`.

Independent recheck from the research workspace:
- release `source-main.md` and reviewed v0.3 manuscript are byte-identical from `## Abstract` onward;
- body length on both sides: 35,792 characters;
- virtual-Q -> actual-self, shutdown-resistance -> intrinsic-Q, control -> valence/fear inferential jumps are explicitly prohibited;
- exact DOI-bound PDF visual review is PASS across all 13 rendered pages.

## DOI

Published:
- report: TA-TR-2026-24
- version: 1.0
- DOI: 10.5281/zenodo.23176685
- Zenodo record: 23176685
- title: From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents
- PDF SHA-256: 368e80b07be1d25ec542971352b9067206aaba9cfff82945c7286c5a281ba104
- exact public file readback: PASS
- DOI resolver check: PASS
- peer reviewed: false

Zenodo package contains 11 manifest-bound files including PDF, Markdown, formal audit, claims, metadata, citations, hashes and reproducibility ZIP.

## OpenTimestamps

OTS is submitted for the exact DOI-bound PDF.

Current state at this record:
- state: PENDING_BITCOIN
- pending calendar attestations: 4
- Bitcoin heights: none yet
- OTS proof SHA-256: c137a6a378a31123b8c7ad5076c04c7515220703a914882030ad3bc0ed2c6fd4

Do not describe this as Bitcoin-verified until a Bitcoin block attestation is present and the repository verification lifecycle passes.

## Arweave

Current state:
`BLOCKED_PENDING_VERIFIED_BITCOIN_ATTESTATION`.

This is an intentional mature-flow guard, not a failure. The repository requires verified OTS Bitcoin evidence before the paid Arweave upload. The cumulative paper-edition fee must remain strictly below 0.1 AR and existing reserve/rolling-spend/duplicate-post/readback guards remain mandatory.

The existing Research Paper 24 v1.0 OTS and Arweave Scheduler was explicitly triggered on main by commit:
`9db7caf9447de9026e9ac23206c5e950e0169d3b`.

A condition watch is active to continue/check the existing lifecycle and only report preservation complete after verified Bitcoin evidence plus anonymous Arweave SHA-256 readback PASS.

## Truth-status boundary

DOI, OTS and Arweave establish identity, provenance, timestamping/preservation and discoverability. They do not establish scientific truth, significance, consciousness, valence, fear or peer review.
