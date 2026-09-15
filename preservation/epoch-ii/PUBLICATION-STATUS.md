# Preservation Epoch II — publication status

Harvard Dataverse has published **Trinity Accord — Research Corpus and Preservation
Mirror · Preservation Epoch II**, DOI [10.7910/DVN/W9Y3IV](https://doi.org/10.7910/DVN/W9Y3IV).

The publication notification was sent by Harvard Dataverse Support at
**2026-09-15 10:40:06 UTC** (18:40:06 China Standard Time) and read from the
depositor mailbox. It names this exact Dataset and states that it “was published
in Harvard Dataverse.” This is the notification time; the exact release timestamp
and released version number still require a public API read.

Machine-readable observation: [preservation/harvard-epoch-ii-state.json](../harvard-epoch-ii-state.json).
Recovery discovery: [preservation/recovery-catalog.json](../recovery-catalog.json).

## Preserved scope and completed submission

| Item | Frozen scope / recorded result |
| --- | --- |
| Planned Dataset files | 419: 417 payload/support files plus 2 control files |
| Payload and support bytes | 23,107,006,729 |
| Total bytes including controls | 23,107,308,201 |
| Polygon/Base Finality | 26 files; 17,551,241,826 bytes |
| Computationally delayed witness archives | 48 ciphertext and support files; 2,798,199,225 bytes |
| Prepublication full-byte size/SHA-256 readback | 419/419 PASS; all files unrestricted |
| Project verifiers and clean candidate cold recovery | PASS in the completed submission evidence |
| Submission | One submitForReview request; final InReview at 2026-09-12 17:28:14 UTC |
| Publication | Confirmed by the 2026-09-15 Harvard notification |
| Postpublication anonymous full-byte readback | Pending; not inferred from prepublication verification |

The 48 delayed-access files include ciphertext and recovery/integrity/verification
materials. They are not 48 raw ciphertext files. The frozen scope and exclusions
remain as recorded in [the frozen manifest](frozen/DATASET-MANIFEST.json) and the
deposited limitations; publication does not turn a scoped inventory into a claim
that every historical original byte was recovered.

## Immutable identities

- Source commit: `3bdf9121fb9e98cd9ba9de62a2466367d0968e4e`
- Candidate SHA-256: `cd0bd263f548d23060422021408ab1705e8c48c1c1028f1a440eb89d1e88d7e8`
- Layout SHA-256: `938c6d9f3df75853e31821a1fc8b23f0f06ec235ff6408a104ebd91e6e4381e4`
- DATASET-MANIFEST.json SHA-256: `24212072367bdcdd5d550c379433b10bdefe0366f9bec3ddc10ea81e6fadbcad`
- Harvard SHA256SUMS SHA-256: `fbf5a3cc784683a595c6bb4d2869b209d786029dee184d19be56e0df7039f705`

## Submission evidence

- [Upload and full-byte readback run](https://github.com/thechurchofagi/trinity-accord/actions/runs/34706525207)
- [Final receipt validation and single submission run](https://github.com/thechurchofagi/trinity-accord/actions/runs/34708278731)
- [Final receipt artifact](https://github.com/thechurchofagi/trinity-accord/actions/runs/34708278731/artifacts/10302028418)

Final job log, reread on 2026-09-15:

```text
2026-09-12T17:28:09.0719272Z all gates PASS; issuing the sole submitForReview request
2026-09-12T17:28:14.1316083Z FINAL PASS files=419 state=InReview
```

The final receipt ZIP is 1,637 bytes, SHA-256
`8e36ff411fab1827871d4a1ff22a2c1402fb30b79286c91a4739ad5b1de0d68b`.
Its current Actions retention expires on **2026-12-11 17:27:26 UTC**.
This update preserves its identity and discovery link, not a new durable copy of
the ZIP. Preserve the receipt payload before expiry.

## Remaining read-only publication check

The local public Dataset API request on 2026-09-15 returned HTTP 403. No
postpublication public inventory or anonymous byte check completed in that
attempt. This is an access limitation of the observation, not evidence that
Harvard rejected the Dataset or that any file is corrupt.

The next verifier should retrieve the released version anonymously, compare the
exact logical paths, unrestricted flags, sizes and hashes for all 419 files
against the frozen manifest and two control files, then stream and hash each
public payload. Preserve a dated per-file report and update the separate
postpublication fields only after success. Reuse the existing source-build,
project-verifier, cold-recovery and prepublication results for their original
scope.

Publication is complete. No reminder or resubmission is needed. Do not edit,
reupload, version-upgrade or republish either Harvard Dataset as part of this
check.

## Authority and historical boundary

Harvard is a non-amending research and preservation mirror. Publication is not
peer review, institutional endorsement, philosophical validation or canonical
authority. The three Bitcoin Originals retain their existing authority.

Preservation Epoch I, DOI `10.7910/DVN/YUCG12`, and its state file remain
unchanged. Epoch II's deposited files and frozen candidate also remain unchanged.
This repository observation was added after publication; it is not retroactively
part of the frozen Harvard deposit.
