# Ninth-paper preservation batch

The user authorized completing OTS and Arweave preservation for TA-TR-2026-09
on 19 September 2026, after DOI publication. This is one paper with two PDF
assets: the English full text and a Chinese argument guide. The guide is not a
full translation and does not count as another paper.

`targets.json` freezes the exact v1.1 files from DOI 10.5281/zenodo.22844928.
The pipeline uses the existing OTS client, Bitcoin header proxy, Arweave uploader,
wallet ledger and runtime spend guard. It never edits the published PDFs, DOI
record, or earlier preservation batches.

The dedicated workflow runs initially and then hourly at minute 57 UTC. It
upgrades existing proofs without restamping them. Bitcoin verification requires
the OTS cryptographic proof and agreeing Blockstream/mempool.space headers; it
does not assert local full-node consensus verification.

Arweave upload follows successful verification of both PDFs. Existing limits
remain: at most one paid research archive per UTC day, 0.50 AR rolling 30-day
spend, and 0.25 AR minimum reserve. This batch caps a transaction at 0.05 AR and
the payload at 4 MiB. A used daily allowance defers a new upload; it does not
raise the limit or change its budget category. A recorded transaction can be
read back without a second paid post even when the daily allowance is used.

Before a new paid attempt, the workflow commits a payload-bound intent to its
branch. An intent with no transaction receipt blocks automatic further paid
attempts until the retained run artifacts are reconciled. This prevents a new
transaction after an ambiguous interrupted upload. The workflow retains proofs,
logs, and receipts as artifacts and commits them after each iteration.

`status.json` is the authoritative stage record. Calendar acceptance means
`PENDING_BITCOIN`, not Bitcoin verification. Completion requires
`ARWEAVE_READBACK_PASS`, a transaction ID and exact public bundle SHA-256
readback. `scheduling-status.json` records quota deferrals when applicable.
Completed batches do no further stamping or paid uploads.

The resulting archive contains the two unchanged PDFs and their detached OTS
proofs and verification records, following the previous paper batches. It does
not claim that every auxiliary Word/HTML/citation file is separately timestamped.
Timestamps establish existence by the attested Bitcoin block, not authorship,
truth, peer review, or the earlier publication date.
