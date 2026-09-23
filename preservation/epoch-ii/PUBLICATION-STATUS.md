# Preservation Epoch II — publication status

Harvard Dataverse has published **Trinity Accord — Research Corpus and Preservation
Mirror · Preservation Epoch II**, DOI [10.7910/DVN/W9Y3IV](https://doi.org/10.7910/DVN/W9Y3IV).

The publication notification was sent by Harvard Dataverse Support at
**2026-09-15 10:40:06 UTC** (18:40:06 China Standard Time) and read from the
depositor mailbox. It names this exact Dataset and states that it “was published
in Harvard Dataverse.” This is the notification time. Anonymous public API reads on **2026-09-23**
confirmed released **v1.0**, Dataset version ID **748388**, with exact release time
**2026-09-15 10:40:01 UTC**.

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
| Publication | Notification plus anonymous v1.0 API confirmation |
| Postpublication anonymous full-byte readback | **419/419 PASS; 23,107,308,201 bytes** on 2026-09-23 |
| Postpublication source-capsule cold recovery | **6,423 tracked files / 9 checkpoints PASS**, offline; Bitcoin v2 **12/12 PASS** |

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
Actions metadata reread on **2026-09-23** still reports retention expiry at
**2026-12-11 17:27:26 UTC** and `expired: false`. The original ZIP has now been
[durably copied](receipts/final-submission-34708278731.zip), with its exact 1,637
bytes and SHA-256 independently checked. Both JSON members were reviewed for
credentials and personal contact data; none were found. The original is not a
redacted or regenerated archive. Its `InReview` and 419 readback receipts are
prepublication evidence, not a later anonymous verification result.

## Completed anonymous publication check

The [dated per-file receipt](public-readback-20260923.json) records anonymous
GETs pinned to released **v1.0 / version ID 748388**. All 419 logical paths,
sizes and SHA-256 identities matched the frozen manifest plus its two controls;
all files were unrestricted and their Dataverse IDs were pinned to this version.
Every file was read in full and hashed;
the version and inventory were checked again after completion. No management
credentials were sent. This result is separate from prepublication verification.

The earlier [403 observation](public-readback-observation-20260923.json) remains
unchanged as historical evidence. A follow-up comparison found a 403 response
from `awselb/2.0` for the default Python client identifier, while a transparent,
fixed project User-Agent obtained the same public API without authentication.
The web landing endpoint separately returned an explicit AWS WAF challenge.
These observations support an ingress/client-classification explanation; the
exact historical WAF rule cannot be proven without Harvard server logs. No
identity rotation, challenge solving, permission change or dataset mutation was
performed.

The run began with two simultaneous downloads and resumed from 84 verified
files with a maximum of four, a 28 GB total wire-byte ceiling (including a
conservative allowance for interrupted in-flight transfers),
three-hour execution ceiling and bounded transient retries respecting
Retry-After. Access denials stop the run. Large finality shards were fully
streamed and hashed without retaining a second local copy. Source and support
materials needed for the recovery exercise were retained.

The eight anonymously downloaded source-capsule files restored exact source
`3bdf9121fb9e98cd9ba9de62a2466367d0968e4e`, tree
`4474b90825253c41bf2e4159c76fde4b4f07b241`, into a fresh directory with network
syscalls blocked by Linux seccomp. The unchanged standalone recovery program
verified **6,423 tracked files and nine checkpoints**; the recovered Bitcoin
v2 verifier passed **12/12**. Current online corrections were deliberately
unavailable, so currentness is unknown. This does not restore production parent
history, signing authority or an operational public intake service. Full-file
hash verification of external archives is not a claim that all archives were
unpacked or every embedded proof independently rerun.

Detailed recovery evidence and the bounded acquisition harness are in the
[repository audit](https://github.com/thechurchofagi/trinity-accord/blob/main/audit/harvard-epoch-ii-public-readback-20260923.md).

The dated anonymous full-byte check is complete. Future downloads must still
be checked against the same frozen identities; this is not a promise of
perpetual availability. No edit, reupload, resubmission, new DOI or paid
transaction was part of this check.

## Authority and historical boundary

Harvard is a non-amending research and preservation mirror. Publication is not
peer review, institutional endorsement, philosophical validation or canonical
authority. The three Bitcoin Originals retain their existing authority.

Preservation Epoch I, DOI `10.7910/DVN/YUCG12`, and its state file remain
unchanged. Epoch II's deposited files and frozen candidate also remain unchanged.
This repository observation was added after publication; it is not retroactively
part of the frozen Harvard deposit.
