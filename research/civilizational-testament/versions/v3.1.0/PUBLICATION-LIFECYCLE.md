# CTP-2026-01 v3.1.0 — publication lifecycle

**Published Zenodo preprint, not peer reviewed.** Human author of record: Hongju Liu. The fixed three Trinity Accord Originals are unchanged.

## DOI: completed

- DOI: https://doi.org/10.5281/zenodo.23314212
- Record: https://zenodo.org/records/23314212
- State: `PUBLISHED_AND_PUBLIC_READBACK_PASS`.
- Publication receipt: `publication-record.json`; report `CTP-2026-01`; version `3.1.0`.
- Published English 27-page PDF: `Before_We_Know_What_We_Will_Become_v3.1.0.pdf`, **187669** bytes, SHA-256 `ee27e2e5e6b738481641917e080a00fc3a652a392cd26af1c3052416bf8f62da`.
- Complete English source: `manuscript.md`, **109364** bytes, SHA-256 `c6cc17c1b8068c08f88ac027232095365f52b62d30a51e1d8c20db67508b6635`.
- Reproducibility ZIP: `Open_Inheritance_DOI_Preparation_v3.1.0.zip`, **456515** bytes, SHA-256 `05c97b990347ee0e14199cff93dfcbcf3f63b42d73b93f7b13cdedbebec91e6e`.
- All three Zenodo files verified by anonymous public exact-byte SHA-256 readback in publication-only GitHub Actions run [38231907314](https://github.com/thechurchofagi/trinity-accord/actions/runs/38231907314). This does not certify peer review or independent acceptance.

## OTS: submitted, Bitcoin confirmation pending

- Batch `research/paper-timestamps/2026-10-12-ctp-v310` tracks **only the exact DOI-published PDF**.
- Detached proof `proofs/CTP-2026-01/Before_We_Know_What_We_Will_Become_v3.1.0.pdf.ots`, SHA-256 `f4c4a4ad827dd5f71be3763277e70a6f62a9e9aeefe917a7d32e1dfb24a7bf30`; initial submitted proof is separately retained.
- Last observed `status.json`: four pending calendar attestations, `bitcoin_heights: []`, `state: WAITING`, dated 12 October 2026.
- Calendar receipt is **not** Bitcoin verification. The scheduler may upgrade existing proof but MUST NOT mint new stamps when exact proof already exists.

## Arweave: NOT YET PAID OR ARCHIVED

- Only after verified Bitcoin proof under repository's agreeing remote-header verifier, an intact target/receipt/DOI identity, and the spending/readback gates.
- Independent strict per-version archive fee cap: cumulative **less than 0.1 AR**, minimum wallet reserve 0.25 AR, rolling 30-day spend max 0.5 AR, plus runtime size and rate safeguards.
- Existing uploader reuses any recorded transaction ID; never pay again to solve slow public readback.
- GitHub default-branch scheduler: `.github/workflows/research-ctp-v310-ots-arweave-scheduler.yml` (hourly minute 32 UTC), targets this branch. The workflow is a conditional preservation job, not a claim that Bitcoin/Arweave are already complete.
- Branch-only spending validator `scripts/research_paper_budget.mjs` was narrowly extended to recognize exact `CTP-2026-01` alongside existing TA-TR identifiers; no fee limit weakened.
- Final completion can only be reported after `status.json.state == ARWEAVE_READBACK_PASS` with transaction, exact payload hash and anonymous readback.

## Integrity and control

- No older publication or canonical inscription was amended.
- Prepublication v1/v2/v3 versions remain historically intact.
- No PR, research CI, or website deployment was part of this publication.
- Repository main-branch scheduler activation commit: `cb32918b98527e5f766c4414aabb469d1cee7977`.
- No future preservation completion should be inferred without consulting current batch status and proof.
