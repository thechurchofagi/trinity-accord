# Independent CTD preservation readback: static review and execution notes

**Scope:** local preparation only. The script was read and AST parsed; it was not imported or executed. No HTTP request, wallet action, payment, upload, workflow trigger, or completed preservation receipt was produced by this review.

**Reviewed script:** `verify_public_preservation.py`, 11,385 bytes, SHA-256 `2e15bdbb194a590ad05640674d3a74894659d90303693de25a5529330bc25bf5`. Python standard library only; its three required path arguments make it independent of a repository checkout or current working directory.

**Static verdict: PASS; remaining must-fix items: 0.** The independent reviewer read back the final file and the added gates, verified this hash, and AST parsed the source without importing or executing it. This verdict is not an actual public readback result.

## Contract and checks

The implementation follows the actual uploader contract in `ctd_v10/release_review/sources/scripts/arweave_upload_payload.mjs` and the preservation/bundle contract in `ctd_v10/release_review/post_doi_main/scripts/research_paper_ots.py`.

- It accepts only the final `trinityaccord.paper-ots-status.v1` state `ARWEAVE_READBACK_PASS`, a real uploader result `uploaded` with `hash_match: true`, and matching transaction IDs and payload/readback hashes. Both final status and frozen bundle verification must name batch `2026-10-10-paper26-v100`, with one paper and one PDF. The frozen verification correctly retains `READY_FOR_ARWEAVE`; the script does not demand that this pre-upload snapshot have the later final state.
- Target identity is fixed to TA-TR-2026-26, DOI `10.5281/zenodo.23279189`, version 1.0.0. The original PDF must have 269,961 bytes and SHA-256 `479b4f2403ad7416f99f7676533fd4a8b9efed1bb289c7fcd52f64a09bf81c94`. The proof must match the exact batch-relative path and the hash recorded by `BITCOIN_VERIFIED_REMOTE_HEADERS`, with nonempty recorded Bitcoin heights.
- After all local gates pass, it performs an anonymous HTTPS GET of `https://arweave.net/<tx>`. Redirects remain restricted to public HTTPS Arweave gateway hosts. It uses no wallet, origin authentication, cookies, or transaction write operation.
- HTTP 200, exact payload length, SHA-256, and byte-for-byte equality are all required. A pending, error, HTML, truncated, extra-byte, or altered response cannot pass. Every embedded file is strictly base64 decoded and hash checked; duplicate or noncanonical member paths fail. The canonical embedded PDF and OTS proof must equal the verified local originals exactly. Other legitimate proof-log members are checked rather than discarded.
- It rereads local evidence before declaring success. A successful JSON report records the transaction, requested and downloaded endpoints, UTC times, HTTP status, exact bytes and hashes, member identities, and source-file snapshots. The report uses a new output path; prior receipts are never overwritten. Any incomplete or inconsistent result exits nonzero and cannot have `hash_match: true`.

An independent static reviewer identified one missing schema/batch/count gate for the two OTS status objects; that gate was added before the final hash above. No scientific files or existing preservation scripts were changed.

## Exact boundaries

This is **independent archive-byte and embedded-member readback**, with **inherited Bitcoin verification evidence** bound to the exact frozen receipt and proof. It does not independently rerun OTS or verify Bitcoin headers, confirmations, finality, or timestamp interpretation.

The nine Zenodo public assets are `README-LICENSE.txt`, `REVIEW-AND-SOURCES.md`, `SHA256SUMS.txt`, `citation.bib`, `citation.csl.json`, `citation.ris`, `noise-identifiability-bodily-judgments-v1.0.0.md`, `noise-identifiability-bodily-judgments-v1.0.0.pdf`, and `reproducibility-v1.0.0.zip`. Their publication readback belongs to separate DOI receipts. This single-PDF OTS batch does **not** claim that all nine assets were timestamped or archived in its Arweave payload. The decorated distribution PDF and the final delivery ZIP are also distinct from that payload and the exact public PDF above.

## Later execution by the authorized root task

Only after the actual workflow completes, obtain one consistent copy of its final `status.json`, `targets.json`, `arweave-receipt.json`, `arweave-bundle.json`, and `proofs/TA-TR-2026-26/noise-identifiability-bodily-judgments-v1.0.0.pdf.ots`. Keep the proof bytes frozen with the matching bundle; substituting a subsequently upgraded proof would correctly fail.

Example command below is a template, not an executed check. Replace each absolute placeholder with the real final files. The original PDF can come from the exact Zenodo download or the unchanged `public/` staging copy; do not supply a distribution-metadata PDF.

```bash
python3 /absolute/path/to/verify_public_preservation.py \
  --preservation /absolute/path/to/real-final-preservation-batch \
  --public-pdf /absolute/path/to/noise-identifiability-bodily-judgments-v1.0.0.pdf \
  --out /absolute/path/to/new/ROOT_ARWEAVE_READBACK.json
```

The later completion builder can consume the resulting `tx_id`, `hash_match`, and `readback_sha256` fields. A failed or pending report remains evidence of that attempt; use a new receipt filename for any subsequent attempt. No transaction ID or successful chain state is supplied or invented here.
