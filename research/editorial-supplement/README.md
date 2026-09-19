# Dated editorial supplement: version and preservation decision

Decision date: **19 September 2026**. This is editorial maintenance, not TA-TR-2026-07.

## What is being updated

The six papers' existing manuscripts have not changed in PR #1219. That change added separate bilingual critical-use notes and corrected a research-index citation ambiguity. It is therefore not evidence that six manuscript editions must be replaced. It does, however, leave a genuine access gap: people reaching an original Zenodo DOI do not necessarily find the later commentary, and a website-only note is not included in earlier frozen preservation bundles.

This workflow addresses that gap by publishing the actual complete English and Chinese notes as **one separate editorial supplement**, adding a visible dated link and `isSupplementedBy` relation to each of the six existing DOI records, and recording anonymous before-and-after SHA-256 checks of all original published assets. Each original title, creator, version, publication date and DOI is preserved; only description and related-identifier metadata change. The supplement links back with `isSupplementTo` relations. It is not independent scholarly validation.

The supplement is supplied in Markdown and self-contained HTML, plus publication scope, source identities, citation data and checksums. Its source checkpoint is `dd50a011345f6b879ac10fe09d03ee8588c6eb2e`. This deposit fixes real reading content rather than only a summary of implementation.

## Papers can legitimately be revised

The three Bitcoin Originals' non-amendment rule does not forbid new research editions. If a manuscript's argument, sources, conclusions or material explanation actually changes, publish a clearly linked new version or an appropriate erratum. Retain the old version and its proofs, identify the differences, and obtain a new proof for changed bytes. Do not call a metadata-only update a new body revision, and do not conceal substantive revisions inside an old version's file name.

Zenodo distinguishes [record metadata edits](https://help.zenodo.org/docs/deposit/manage-records/) from [new file versions](https://help.zenodo.org/docs/deposit/manage-versions/). Metadata can be changed while the DOI remains the same; a new file edition is a new linked version. The present choice does not establish that every sentence of all six papers is error-free, and it does not preclude a future justified correction.

## Separate, append-only preservation

`2026-09-19/published/SHA256SUMS.txt` binds the other seven supplemental assets. A new OTS proof is made for that manifest. OTS upgrade matures a receipt for the **same bytes**, not a revised paper. The old nine PDF proofs remain separate. No earlier timestamp is asserted to cover this supplement.

Once the new OTS proof is verified against the repository's existing dual-provider Bitcoin-header proxy, a frozen JSON bundle includes the actual eight assets, proof, initial receipt and verification report. The existing guarded Arweave uploader handles signing, a durable transaction checkpoint and exact anonymous readback. It may resume an existing transaction; it must not pay again merely because retrieval is delayed. This small batch is capped at 1 MiB and 0.003 AR, additionally subject to existing wallet-reserve and rolling-budget guards.

A pending OTS receipt is not a verified Bitcoin timestamp. An Arweave transaction identifier is not successful public readback. Inspect `2026-09-19/status.json` and `arweave-receipt.json`; only `ARWEAVE_READBACK_PASS` establishes the checked publication state. Remote-header verification is not a claim to local full-node consensus validation.

## Artifacts and responsibilities

- `publication-record.json`: supplemental DOI identity and anonymous full-byte readback.
- `metadata-links/`: pre-edit metadata and before/after file hashes for each original DOI.
- `links-status.json`: completion of all six public associations, distinct from body revisions.
- `status.json`: new OTS/Arweave lifecycle only, not the original paper batch.

Hongju Liu requested the evaluation and authorized justified updates. GPT-6 Astra Pro substantially performed the analysis, editorial preparation and implementation under human direction. Human publication responsibility is not transferred to the model. This is not independent peer review or an assertion that future AI will accept the papers' normative premises.
