# Publication author identity and contact policy

Policy: PUB-AUTHOR-IDENTITY-20261013 | Version: 1.0.0 | Effective: 2026-10-13

User instruction: future papers must contain the author's email in the paper itself, and publication instructions must preserve this requirement across sessions. This is a prospective publication rule, not an amendment to already published editions or to the Trinity Accord Canon.

## One author identity

Read [AUTHOR_IDENTITY.json](AUTHOR_IDENTITY.json) before preparing a new paper or a new edition. Use the following values for Hongju Liu unless the author explicitly updates them:

| Field | Required value |
| --- | --- |
| Name printed in manuscripts | Hongju Liu |
| Family name / given name | Liu / Hongju |
| Combined deposit/citation name | Liu, Hongju |
| Current affiliation | Independent researcher, Shenzhen, China |
| Author contact email | liuhongju3@163.com |
| Claimed OpenAlex author ID | https://openalex.org/A5150552024 |
| ORCID | Not verified; do not invent or infer one from a name match |

`trinityaccord@gmail.com` is a previously supplied project/research contact. It does not replace the author email above by default. A Zenodo login email, a Git commit email and a public manuscript contact are different fields; do not infer one from another. Do not overwrite co-authors' identities or assign them Hongju Liu's email. Preserve historically correct affiliations on old editions.

If a personally verified ORCID already exists, consistently reuse that same iD in future manuscripts and supported creator metadata. If none is verified, record `ORCID_PENDING_VERIFICATION`; do not fabricate an identifier or silently create duplicates. Absence of a verified ORCID is not, by itself, a new ban on publication.

## Required author block

Every new manuscript and every newly released revision must visibly print this block on the title/first page, before the abstract or in a clearly associated author footnote:

```text
Hongju Liu
Independent researcher, Shenzhen, China
Author contact: liuhongju3@163.com
```

The email must be selectable, searchable text in the final PDF, not only a picture, QR code, mailto link target, hidden PDF property, project website, README or deposit account setting. Use [the author block template](templates/PAPER_AUTHOR_BLOCK.md). Standalone supplementary manuscripts with their own author/title page should repeat the contact block.

## Before reserving a DOI and before publishing

1. Read the identity record and apply the author block to source and rendered PDF. Keep papers and publication materials in English by default.
2. Inspect the rendered first page. Extract the exact final PDF's first-page text and check that `Hongju Liu`, `Independent researcher, Shenzhen, China`, and `liuhongju3@163.com` are present and correctly associated. Whole-document hits in references do not satisfy the author-block check.
3. Keep the same author name and affiliation in source, PDF, deposit metadata and citation files (BibTeX/RIS/CSL-JSON). Where names have structured fields, family_name is `Liu` and given_name is `Hongju`.
4. Put the same author name and email in the public deposit description/contact area, using supported metadata fields. If the deposit API has no creator-email field, add a human-readable author-contact paragraph to its public description; do not invent an unsupported field or remove the abstract. ORCID goes only in the platform's supported identifier field after verification. Keep the OpenAlex ID in the identity/operational record; do not mislabel it as an ORCID.
5. Run [the publication identity checklist](templates/PUBLICATION_IDENTITY_CHECKLIST.md). Missing or mismatched author contact blocks the new release until corrected. Do not silently waive it because an earlier paper omitted the email.
6. Reserve one DOI, build the final DOI-bound package, repeat the first-page and metadata checks, and then freeze its exact bytes, hashes and manifest. Any subsequent edit, including contact information, requires rebuilding and checking the package before publication; do not reuse stale hashes.

These checks are release requirements for future publications. This policy update itself neither publishes a paper nor authorizes extra paid activity or an automatic research restart.

## Publication and preservation order

Retain the established sequence: publish the reviewed DOI-bound edition -> anonymous exact-byte public readback -> OTS submission -> actual Bitcoin attestation verification -> Arweave preservation and anonymous SHA-256 readback, subject to the existing budget and authorization rules. Record partial states truthfully. Do not equate a reserved DOI, OTS submission, an Arweave transaction, indexing or a profile claim with a completed later step.

Read back the publicly served PDF and landing page without relying on a signed-in session. Recheck the visible author contact and exact bytes. Keep the previous PDFs, source editions, DOI records, manifests and preservation receipts unchanged; apply this policy to a subsequent legitimate edition, never by silently replacing an already published file.

## After indexing

When an OpenAlex record becomes available, verify the work by DOI/title/version family and the relevant author position, then check its assignment against `A5150552024`. Keep logical works separate from versions and translations. Do not merge homonyms or unrelated co-authors just because their names resemble Hongju Liu's.

A visible email supports contact and identity verification; consistent names/affiliations and a verified ORCID can improve matching. None guarantees that every indexing platform will avoid author splits. Recheck the actual indexed assignment and correct it through the claimed profile when needed. Do not claim success from a submitted correction alone.

## Operational record and persistence

- On 2026-10-13, an OpenAlex screenshot confirmed that `A5150552024` was claimed successfully. A readable copy of the 2019 Cells paper (DOI `10.3390/cells8111405`) displayed the same email; the author explicitly confirmed co-authorship.
- The user subsequently reported selecting and adding publications via the CV workflow. The final selected work IDs/count and the refreshed public assignments have not been independently read back; this is not a verified claim that all former profiles have already merged.
- Store the identity check with each future publication receipt, including policy version, source/PDF hashes, first-page extraction result, rendered-page inspection result, public metadata result, verified ORCID or pending status, and post-indexing status.
- Future research/publication branches must inherit this policy and `research/AGENTS.md` before creating a new release. Keep routine documentation saves under `[skip ci]`, with no PR, CI dispatch or site deployment merely to save this change.
- This file and the workspace `MEMORY.md` are durable project instructions. They do not establish that a separate account-level ChatGPT memory system has been written.
