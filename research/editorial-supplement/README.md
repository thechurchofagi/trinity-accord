# Dated editorial supplement: version and preservation decision

**Decision: 19 September 2026.** Editorial maintenance, not TA-TR-2026-07.

## Why update, and which object changes?

PR #1219 changed separate bilingual critical-use guidance and the research index, not the six deposited paper bodies. There is therefore no basis to label six identical manuscripts as new editions. There is, however, a genuine gap: the later commentary is not automatically discoverable from the old DOI records or covered by old timestamp and Arweave bundles.

The authorized intervention is to preserve the complete new commentary as one dated supplement, associate it with the six existing DOI records, and retain old editions and evidence unchanged. The record IDs are 21699878, 21900592, 22761411, 22804542, 22809019 and 22830239. Their titles, creators, dates, versions and files must remain unchanged; only a visible dated description link and `isSupplementedBy` relation may be added. Anonymous full-file SHA-256 checks compare their assets before and after each metadata edit.

## Papers are revisable; history need not be overwritten

The three Bitcoin Originals' non-amendment rule does not freeze research papers forever. When an argument, source, conclusion or materially important explanation changes, issue a specific erratum or a clearly linked new edition. Retain the earlier version and its proofs, identify changes, and obtain new proofs for new bytes. Existing AR or OTS preservation is not a reason to leave an actual scholarly error uncorrected.

[Zenodo versioning](https://help.zenodo.org/docs/deposit/manage-versions/) separates a new file edition from [metadata edits](https://help.zenodo.org/docs/deposit/manage-records/). Updating metadata need not change the DOI. A new file edition has its own linked version. This decision does not assert that every sentence of the six papers is error-free.

## DOI service and source preservation are independent

The complete eight-file package is frozen under `2026-09-19/published/`: English and Chinese Markdown and standalone HTML; a source manifest; rights/scope note; source-based citation; checksums. The actual guide sources are bound to commit `dd50a011345f6b879ac10fe09d03ee8588c6eb2e` and checked by blob hash. There is no guessed DOI in those files. A later deposit can identify exactly these bytes and its assigned DOI will appear in its real publication receipt.

This ordering was adopted after both Zenodo search and a direct known-deposition read returned HTTP 500/504. An unavailable DOI API does not prevent timestamping already prepared content. A later DOI or metadata update is not retroactively covered by a source-only proof. The actual publication outcome is separate from the OTS and Arweave outcome.

## Append-only OTS and Arweave lifecycle

`2026-09-19/published/SHA256SUMS.txt` binds the seven other supplemental assets. Its new OTS proof concerns this exact manifest. Upgrading an OTS proof matures evidence for the same hash; it does not make that proof cover changed text. The old nine PDF targets and proofs remain separate.

After the new proof is verified against the existing dual-provider Bitcoin-header proxy, a frozen JSON bundle includes the eight actual files, proof, initial calendar receipt and verification record. This is a source-and-proof archive, not a certificate for later DOI metadata. The existing guarded Arweave uploader retains a transaction checkpoint and requires anonymous exact-byte readback. A delayed gateway response must not cause a duplicate payment. New payload is capped at 1 MiB / 0.003 AR and remains subject to wallet-reserve and rolling-budget checks.

Remote-header verification is not local full-node consensus validation. `PENDING_BITCOIN` is not a verified timestamp; `READY_FOR_ARWEAVE` is not uploaded; a transaction ID without matching public bytes is not `ARWEAVE_READBACK_PASS`.

## Check the distinct receipts

- [Frozen inventory](2026-09-19/expected-files.json): actual prepared files and hashes.
- [OTS/AR status](2026-09-19/status.json): source preservation only.
- [Latest publication attempt](2026-09-19/publication-attempt.json): actual external attempt and blocker, if any.
- `publication-record.json`: exists only after supplemental publication and anonymous full-file readback.
- `metadata-links/`: pre-edit metadata and before/after hashes for each original DOI.
- `links-status.json`: exists only after all six public associations are verified.
- `arweave-receipt.json`: paid transaction checkpoint/readback, when an upload is attempted.

Absence of a completion receipt means completion is not asserted. A prepared workflow is not publication. `REQUEST.json` fixes the scope of the already authorized operations. The existing hourly workflow resumes incomplete operations and stops writing completed ones. It does not create a second scheduler. Read retries are bounded; an uncertain record-creation POST blocks another creation until its outcome is recovered. Failures are retained and surfaced rather than relabeled as success.

## Responsibility and scholarly boundaries

Hongju Liu requested evaluation and authorized justified DOI, OTS and Arweave updates. GPT-6 Astra Pro substantially performed critical analysis, editorial preparation and implementation under human direction. No separate final human line-by-line review or independent peer review is claimed. The new package preserves reading content, not only a summary of work performed. It neither changes the Originals nor supplies a seventh scholarly endorsement of the project.
