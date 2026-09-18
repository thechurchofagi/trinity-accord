# Published research papers: Bitcoin OTS and Arweave preservation

The fixed batch `2026-09-18/targets.json` contains **six independent papers,
TA-TR-2026-01 through 06**, and nine published PDFs (six English and three
Chinese). Translations, revisions and academic briefs are not separate papers.
Paper 05's publication receipt and files were on commit
`baa302344493be7b28ade12d334bd9eff3c55dd1` in PR #1216 when this inventory was made;
the main research index therefore listed only five papers.

| Report | Short title | Published DOI | Version |
| --- | --- | --- | --- |
| 01 | Designing a Verifiable, Non-Amending Civilizational Memory Record | 10.5281/zenodo.21699878 | 1.1 |
| 02 | Writing Before the Outcome | 10.5281/zenodo.21900592 | 1.3 |
| 03 | Reading the Trinity Accord | 10.5281/zenodo.22761411 | 1.0 |
| 04 | Beyond Guaranteed Control | 10.5281/zenodo.22804542 | 1.0 |
| 05 | Recovery without Epistemic Monopoly | 10.5281/zenodo.22809019 | 1.0 |
| 06 | Coexistence after Preference Change | 10.5281/zenodo.22830239 | 2.1 |

The user authorized this batch's OTS submissions, future upgrade checks and
Arweave preservation on 18 September 2026. PDF bytes must match the existing
publication receipts before submission. Every PDF receives its own detached
`.ots` proof; `.ots.submitted` preserves its initial calendar receipt. Existing
proofs are upgraded rather than restamped. Published papers and DOI records are
never edited by this pipeline.

`Research Paper OTS and Arweave` runs on installation and checks hourly at minute
37 UTC. Calendar acknowledgement is `PENDING_BITCOIN`; an embedded Bitcoin
attestation alone is not a verified proof. The workflow reuses
`requirements-ots.txt` and `bitcoin_esplora_rpc_proxy.py` to check the OTS proof
against agreeing Blockstream and mempool.space Bitcoin headers. This is remote
header verification, **not local full-node consensus verification**.

Only after all nine proofs pass does the workflow freeze a single JSON bundle
containing all nine PDF originals, detached proofs, initial receipts, hashes and
verification logs. It reuses `arweave_upload_payload.mjs`, the existing
`ARKEY` secret/variable, `arweave_runtime_spend_guard.mjs` and the wallet ledger.
Research archives have a distinct tag and budget category. Existing limits
remain: at most one research upload per day, maximum 0.05 AR per transaction,
0.50 AR rolling 30-day wallet spend, 0.25 AR minimum reserve, and 8 MiB payload.
A deferred gateway readback resumes the recorded transaction without a second
paid post. Run artifacts preserve receipts even if pushing fails; recover any
such paid checkpoint before retrying.

Completion is only `ARWEAVE_READBACK_PASS` in `2026-09-18/status.json`, with the
transaction ID and an exact SHA-256 readback match. Completed batches do no
further stamping or uploading. Secrets never enter proofs or artifacts.

To verify a PDF independently, download its unchanged file from the DOI record
and run `ots verify -f paper.pdf paper.pdf.ots` using your chosen Bitcoin node.
The proof establishes that these exact bytes existed no later than the attested
Bitcoin block. It does not backdate the timestamp to the publication date, prove
authorship, peer review, truth, or modify the three Bitcoin Originals.
