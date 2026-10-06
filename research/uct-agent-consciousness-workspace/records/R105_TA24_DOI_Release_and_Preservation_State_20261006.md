# R105 — TA-TR-2026-24 v1.0 DOI release and preservation state

Date: 2026-10-06.

## Formal release audit

Before DOI reservation, the project created and passed a strict formal dependency map and no-jump audit.

Release identity:
- Report: `TA-TR-2026-24`
- Version: `1.0`
- Title: _From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents_
- Frozen substantive source: v0.3
- Frozen v0.3 Git blob SHA: `ea6d6c4d5b7ad63df6e343c9357e5d3f5959f3a6`

The v1.0 release body from `## Abstract` onward is constrained to be identical to the reviewed v0.3; release front matter alone carries version/report/DOI/status.

## DOI

Zenodo record:
- Record ID: `23176685`
- DOI: `10.5281/zenodo.23176685`
- Record URL: `https://zenodo.org/records/23176685`
- DOI resolver: public HTTP 200 and resolves to the exact Zenodo record.
- Public anonymous byte readback: PASS for all 11 released files.

Primary PDF:
- `from-shutdown-resistance-to-self-continuation-control-v1.0.pdf`
- bytes: `86272`
- SHA-256: `368e80b07be1d25ec542971352b9067206aaba9cfff82945c7286c5a281ba104`

Exact publication manifest SHA-256:
`cbaa8ba098534eaafe5ebc64b81f8792c34c3b6f4bce9c1681d7d31d7befe7d8`

Exact prepared PDF was rendered on all 13 pages and visually inspected before publication; no material clipping, overlap, missing glyph, broken table/reference, or out-of-page content was observed.

## Publication package

Zenodo v1.0 contains 11 files:
- primary PDF and Markdown;
- formal map and strict release audit;
- machine-readable release claims and metadata;
- reproducibility ZIP built from blob-pinned R95–R101 artifacts;
- README/license;
- BibTeX, RIS, CSL JSON;
- SHA256SUMS.

The release explicitly states that DOI/OTS/Arweave concern identity, availability and provenance, not truth or peer review.

## OTS current state

The exact public PDF SHA-256 above has been submitted to OpenTimestamps.

Current proof:
- detached proof SHA-256: `c137a6a378a31123b8c7ad5076c04c7515220703a914882030ad3bc0ed2c6fd4`
- pending calendar attestations: 4
- Bitcoin heights: none yet
- state: `PENDING_BITCOIN`

This is a normal external maturation state. The project does not treat calendar submission as Bitcoin finalization.

## Arweave gate

Arweave is intentionally blocked until the OTS proof contains a Bitcoin attestation and passes the repository's remote-header verification.

The mature preservation workflow retains:
- strict per-upload reward < 0.1 AR;
- minimum remaining balance protection;
- rolling 30-day spend limit;
- payload-bound paid intent;
- protection against repeated uncertain paid uploads;
- public Arweave readback with hash equality.

A main-branch hourly scheduler now checks out and writes only the dedicated release branch:
`research/self-continuation-control-v1-20261006`.

## Status

- Formal release audit: PASS
- Exact PDF visual review: PASS
- Zenodo DOI publication: COMPLETE
- Anonymous Zenodo readback: PASS
- DOI resolver: PASS
- OTS calendar submission: COMPLETE
- OTS Bitcoin attestation: PENDING external Bitcoin/calendar maturation
- Arweave: correctly blocked pending verified OTS Bitcoin attestation

A condition watch is also configured to report only final `ARWEAVE_READBACK_PASS` or an actionable preservation failure.
