# CTD publisher adaptation: local safety review

Date: 10 October 2026. This is an AI-assisted internal technical review of the isolated CTD release code. It is not an external review, a live publication receipt, or an authorization to bypass a release gate.

## Decision

**PASS for the local adaptation.** The 17 inherited consequence-oriented gate tests pass with Python socket connections forcibly blocked. All 22 selected guard functions/classes have identical Python ASTs to the SCU publisher after only the literal `SCU`/`scu` release-label substitution. No existing publisher, spend guard, shared workflow, or older publication record was modified by this adaptation.

The current machine-readable receipt is `PUBLISHER_REVIEW_RECEIPT.json`; the exact test transcript is `CTD_PUBLISHER_OFFLINE_TESTS.log`. The receipt's history retains the earlier check before a metadata-only rights clarification. The final publisher SHA256 is `c55b188787dce0a3bd687d18ef1430e1dd3050b0629067157ef29064bae5e4ac`.

## Files created in the isolated worktree

| Path, relative to the repository | Purpose |
| --- | --- |
| `research/noise-identifiability-bodily-judgments/publication.py` | Independent CTD create-once, frozen-package publisher |
| `research/noise-identifiability-bodily-judgments/test_publication.py` | Adapted 17-test safety suite |
| `research/noise-identifiability-bodily-judgments/build_pdf.py` | Pandoc plus two-pass XeLaTeX build using the paper's supplied style and figures |
| `.github/workflows/prepare-ctd-noise-identifiability-v100.yml` | Branch/path/commit-marker restricted prepare workflow |
| `.github/workflows/publish-ctd-noise-identifiability-v100.yml` | Branch/path/commit-marker restricted verify-and-publish workflow |

The worktree is based on main commit `6cfb89f0b88605da9a44da9c97203729a6742894`. The SCU source baseline is commit `2d7fc42d859fada3a316478ac6c0b4b33f1c542d` and publisher SHA256 `657d7662e7b4151f8939d750a398c15d536954e2abc3d5b6ccab7159aff62c2d`.

## Intentional changes

The release identity is `TA-TR-2026-26`, version `1.0.0`, title *Identifiability of Noise Sources in Bodily Judgments*. The branch is `research/ctd-noise-identifiability-v100-20261010`; the push markers are `[ctd-prepare]` and `[ctd-publish]`. The fixed registry snapshot records TA01–TA25, but a local numbering decision does not reserve an online deposition. The inherited account-wide scan must still exclude concurrent same-work/report occupation.

The ten frozen inputs are `source-main.md`, `build_pdf.py`, `reproducibility-v1.0.0.zip`, `REVIEW-AND-SOURCES.md`, `publication.py`, `pdf_style.tex`, and the four specified figure PDFs. The protected-record set retains the entire SCU baseline and adds SCU record `23272690`, giving 44 protected identifiers. The related records are the original Nature Communications study, SCU, and UCT I/II/III.

Metadata describes methods, retrospective analysis of existing human observations, conditional identification, and finite-sample model calculations. It does not report a new participant experiment, empirical validation of C1, external peer review, or final human line-by-line checking. The substantial ChatGPT assistance is disclosed. Both landing-page description and bundled license notice now state that CC BY 4.0 applies only to newly authored material to the extent rights are held. Third-party workbooks retain their separate rights and provenance; the unlicensed OSF data-node metadata is not relabeled CC BY.

## Safety properties retained

The unchanged guard bodies cover source and byte hashes; actual checked-out commit identity; normalized-title/report detection across a complete all-version account scan; strict HTTPS Zenodo URLs without redirect; protected-record checks; and a pinned legacy transport client. Creation and publication remain separate, durable, single-attempt operations. Their intents must be persisted before a remote POST. An uncertain creation or publication cannot be replayed as a fresh attempt.

Publishing still requires the exact local manifest, original source hashes, record/version/DOI binding, PDF-bound visual review, and authorization. Remote file count, names, sizes and digests must match. Unexpected files are not deleted or silently overwritten. Anonymous record and all-file byte readback remain required for the success state; DOI-resolver readiness is recorded separately. Persistence remains scoped to the intended branch and publication files, with no force push or automatic replay in the publisher.

The workflows retain the source actions' pinned SHAs, narrow paths, release-branch check, exact commit marker, shared CTD concurrency group, tests before credentials, verification before publication, and durable state/artifact collection. No scheduler or paid preservation gate is silently attached to the DOI publisher.

## Verification limits and remaining concrete gates

The isolated worktree inherited sparse checkout. The legacy client is absent from its filesystem, but the exact fixed-main Git object is present and has the required Git blob `a0cbc84cc5fd826c06d16456c4adbaa40dabc788` (SHA256 `92e94028b8e05c9502c2266223856e1a706cd270e61e6c51739476d9d618b0d3`). The new Actions workflows request ordinary full checkout, so this dependency is obtained there. Its pin was not relaxed and the old file was not locally recreated or altered.

The tests use synthetic IDs and mocked network/Git side effects. They do not establish credential availability, remote service health, successful pushes, a live DOI, or final PDF appearance. The authoring agent supplies the final ten inputs; the prepare phase must generate and verify the exact DOI-bound PDF and manifest before the distinct visual/authorization gate. The new PDF wrapper was structurally reviewed but not executed against an incomplete final figure set by this reviewer.

OTS and Arweave are a separate lifecycle. Their template must be bound to the eventual public-readback receipt and exact PDF bytes. A real main-branch scheduler, Bitcoin proof verification, the existing wallet and cumulative publication budget, payload-bound paid intent, and anonymous archive readback remain necessary. Nothing in this local review marks those steps complete.

