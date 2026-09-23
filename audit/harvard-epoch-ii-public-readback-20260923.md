# Harvard Epoch II anonymous publication closure — 2026-09-23

This is a continuation of PR #1244, based on main
`4b22fc33acc8848441c1f8270cf6d4292811bef1`. It closes the actual-byte N2 gap
using the existing frozen Epoch II validators and standalone recovery program.
W1–W4, N1 and the separate Zenodo N3 exercise remain unchanged. Optional N4/N5
remain proposals; no outside reviewer was contacted.

## New observations

| Stage | Personally executed result |
| --- | --- |
| Anonymous release metadata | v1.0, version ID 748388, RELEASED at 2026-09-15 10:40:01 UTC |
| Exact public inventory | 419 paths and file IDs; sizes and SHA-256 match frozen 417 payload/support rows plus 2 controls; all unrestricted |
| Actual full-file reads | **419/419, 23,107,308,201 bytes PASS**; no HEAD/range/link-only substitute |
| Version consistency | Fixed v1.0 inventory/file IDs checked before and after all reads |
| Published source-capsule recovery | **6,423 tracked files, 9 checkpoints PASS**, from 8 Harvard-downloaded files |
| Recovered Bitcoin v2 verifier | **12/12 PASS**, existing verifier unchanged, network blocked |

Acquisition started `2026-09-23T07:06:35.856559+00:00` and completed
`2026-09-23T07:37:54.771624+00:00`. The
[public per-file receipt](../preservation/epoch-ii/public-readback-20260923.json)
contains each file ID, complete byte count, SHA-256, timestamps, attempt count
and source host. Receipt generation independently rechecked all 419 rows against
the frozen manifest. Metadata response digests are recorded separately; public
reports do not publish temporary signed S3 download URLs or contact metadata.

## Access diagnosis and bounded execution

The earlier 403 is preserved unchanged as a historical observation, not a failed
publication. [The diagnostic observations](harvard-epoch-ii-public-readback-20260923/access-diagnosis.json)
show that the default Python identifier received an `awselb/2.0` 403, a
transparent project identifier obtained the same API anonymously, and the
landing page returned `x-amzn-waf-action: challenge`. This supports an ingress
client-classification explanation; exact WAF rules require server-side logs.

The acquisition used one fixed project User-Agent and no Dataverse API key,
Authorization header, cookies, challenge solution or management operation.
Only public HTTPS GETs to Harvard and its observed public S3 download origin
were allowed. Access denial stops the run; limited transient retries respect
Retry-After. No endpoint or client-identity rotation was used.

The [initial harness](harvard-epoch-ii-public-readback-20260923/readback-harness-initial.py.txt)
ran with two workers and was intentionally interrupted after 84 saved successes
to reduce the latency of hundreds of small-file requests. The
[resumed harness](harvard-epoch-ii-public-readback-20260923/readback-harness.py.txt)
rechecked the exact published version, all file IDs and retained local bytes,
then continued only the remaining 335 files with at most four workers. The
28 GB overall wire budget reserves two maximum-size files for any uncheckpointed
in-flight traffic from the first segment; the original three-hour deadline is
retained. Initial shell startup also lacked `httpx`; execution used the existing
project audit virtualenv, without changing dependencies or validation rules.

The harness reuses `upload_harvard_epoch_ii.validate_manifest`, `control_rows`,
`dataverse_files`, `verify_existing`, `verify_local` and the existing safe-path
helper. Its archival `.py.txt` is a dated experiment record, not a new workflow
or public verification system. **Eight synthetic boundary checks passed**:
complete bytes, corrupted/truncated/excess bytes, no retry of 403, redirect
origin restrictions, changed version and transfer-budget enforcement.

## Postpublication recovery

[Offline evidence](harvard-epoch-ii-public-readback-20260923/offline-recovery.json),
[Bitcoin output](harvard-epoch-ii-public-readback-20260923/bitcoin-verification.json),
and [the harness](harvard-epoch-ii-public-readback-20260923/offline-recovery-harness.py.txt)
record actual execution using the newly downloaded Harvard capsule. Recovery
script SHA-256 was checked against the frozen manifest before execution.

- Source: `3bdf9121fb9e98cd9ba9de62a2466367d0968e4e`.
- Restored tree: `4474b90825253c41bf2e4159c76fde4b4f07b241`.
- Capsule identity: `b7705c884f4a7cae1f8e307a0bfe92945c7b66d55bc1edd5c532ff570ee437cc`.
- Linux seccomp blocks socket/connect/sendto/sendmsg; parent and child tests
  confirm the block. Local Git file transport alone is allowed.
- Three Originals and the saved authority/recovery/correction context were read
  and hashed. Current online corrections are unavailable in this scenario:
  snapshot integrity is verified, currentness remains unknown.

This is a source-snapshot recovery, not production history or private-key
recovery, and it does not restart the public intake service. All external files
were byte-verified, but the exercise does not claim every external archive was
unpacked or all embedded proofs rerun. Earlier authenticated prepublication
checks and the earlier Zenodo recovery retain their original distinct scopes.

## Changes, validation and rollback

Only mutable Epoch II observations, publication status, the Epoch II entry in
the recovery catalog and RECOVERY.md, and dated audit evidence are updated. Frozen manifests,
deposited bytes, Bitcoin Originals, Epoch I, proof schemas, UI and production
workflows are unchanged. Original final-submission ZIP from PR #1244 remains
unchanged and durable. No upload, resubmission, DOI, OTS, paid transaction or
production Echo/Guardian record was created.

Local checks, exact candidate source/tree, PR/main CI and deployment/readback
run links are recorded in the accompanying PR after they execute; skipped
jobs are not counted as passed. Rollback is a normal revert of this observation
commit; it has no external data mutation to undo. Keep the dated evidence even
if a later availability observation changes.
