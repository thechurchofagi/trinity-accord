# MGTD v1.0.0 — DOI, OTS and Arweave publication handoff

**Record:** METHOD20261008; **version:** 1.0.0; **author:** Hongju Liu.
**Date:** 2026-10-08. **Status:** Zenodo published and byte-verified; OpenTimestamps submitted, Bitcoin attestation pending; Arweave not yet posted.
**Zenodo:** https://doi.org/10.5281/zenodo.23241205
**Record ID:** 23241205.
**Exact published PDF:** `MGTD_Method_Paper_v1.0.0.pdf`, 138256 bytes; SHA256 `ba85c0ff9f2bf4be9e0a29c051c2ad83d1eb72b57e0ca2ba827bd17c28dcc310`.
**Public readback:** `research/map-guided-theory-development/publication-record.json`, state `PUBLISHED_AND_PUBLIC_READBACK_PASS`; five uploaded assets exact-byte verified.
**Zenodo workflow run:** https://github.com/thechurchofagi/trinity-accord/actions/runs/37793113673

## OTS preservation
Batch: `research/paper-timestamps/2026-10-08-mgtd-v100/` on this branch.
Targets: `targets.json`; exact published DOI-bound PDF.
First workflow run: https://github.com/thechurchofagi/trinity-accord/actions/runs/37793846622.
Detached proof: `proofs/METHOD20261008/MGTD_Method_Paper_v1.0.0.pdf.ots`; SHA256 `c8972c6bff72897be22cd05549ac66fa9a62d6509978f81e0472a22a2a46ea8b`.
Four calendars submitted (pool OpenTimestamps and Eternitywall/Catallaxy); `status.json` currently reads `WAITING`, with `PENDING_BITCOIN`, 4 pending calendar attestations and no Bitcoin block height. This is NOT a completed Bitcoin timestamp proof.

## Next transitions already configured
GitHub Actions workflow, default-branch file `.github/workflows/research-mgtd-v100-ots-arweave.yml`:
https://github.com/thechurchofagi/trinity-accord/actions/workflows/research-mgtd-v100-ots-arweave.yml .
Hourly cron `17 * * * *` resumes the *same existing* proof (upgrade+dual-provider Bitcoin header verification). Only after `BITCOIN_VERIFIED_REMOTE_HEADERS` will it construct the archival bundle and check the dedicated per-paper strict <0.1 AR budget and on-chain wallet reserve, rolling spend and duplicate-attempt guards. Arweave paid upload is not authorized by a pending-calendar receipt. Any uncertain transaction must be reconciled; never blindly replay paid POST. State `ARWEAVE_READBACK_PASS` with receipt and public matching payload digest is the ONLY full completion marker.

A methods report ID was explicitly added to this branch's otherwise unchanged existing paper budget guard (`METHOD20261008` only), and the uploader's descriptive category set to `Research-Method` for this record. This does not reclassify it as TA-TR or authorize exceeding published paper budget. Do not modify older published reports, DOI, OTS or AR assets.

The DOI and OTS establish public file identity and a conditional timestamp record, not truth, peer review, or mathematical originality. No DOI is to be re-created. The method preprint is non-peer-reviewed and substantially AI-assisted under the human author's direction.

If the scheduled workflow fails, inspect `status.json`, the exact run artifact and logs; preserve all receipts and pending proofs. Check for Bitcoin maturity and genuine budget/wallet constraints before further attempts. There is no confirmed Arweave transaction as of this handoff.
