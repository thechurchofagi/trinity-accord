# SCU publisher implementation review

Review ID: SCU-PUBLISHER-REVIEW-20261010-v1.0.0  
Disposition: **READY FOR AUTHORIZED PREPARE. Publish implementation accepted subject to its existing final exact-package and visual-review gates.**  
This review performed no credential access, remote creation, file upload, or publication.

## Files examined and changed

Full SCU `publication.py` and `test_publication.py` were read. Both SCU workflow files were read in full. The TA23 predecessor and its eight tests were separately read and executed before adaptation.

Only the two files explicitly delegated by the parent were edited:

- `research/matched-behavior-source-use/publication.py`: SHA-256 `657d7662e7b4151f8939d750a398c15d536954e2abc3d5b6ccab7159aff62c2d`.
- `research/matched-behavior-source-use/test_publication.py`: SHA-256 `a401a473373803f81f49b011c016b2e9fea3640cc2d6d102841505df18ce4949`.

The workflow hashes are `47a910832a347dff77713c769986c56abbdd68636f06763a76d07dd71746a468` (prepare) and `5979d34fd32b6298e619cb9ccd8cb14e19d9d989400201f779207e7868117cc5` (publish). This reviewer did not edit them.

## Changes and why they matter

### 1. Bounded all-version duplicate detection

The previous publisher queried only an exact title and filtered to the exact target version. A pre-existing v1.0.0 could therefore be missed when preparing v1.0.1.

The revised publisher reads the authenticated account listing with `all_versions=true`, without a draft-only or published-only filter, using explicit pages of 100. It stops after a short page; it fails closed if the list reaches 20 full pages, contains malformed rows, or repeats record IDs across pages. It does not infer completeness from a failed or capped lookup.

Possible same-work candidates include Unicode/case/spacing/punctuation-normalized title matches, the title followed by a subtitle/version suffix, and the publisher's report marker. Any other edition or ambiguous multiple candidates blocks new creation. Normalization is used only to reject creation: adopting an existing reservation still requires the exact title and version plus the same locally saved reservation token and record/DOI checks.

This is a conservative duplicate guard, not a theorem that all possible paraphrased titles or independently created deposits can be recognized. It coordinates the declared workflow and fail-closed evidence; another external actor changing the account remains outside an atomic local guarantee.

### 2. Actual checkout provenance

A workflow can be triggered at one commit and check out the current branch tip at another. The revised `checked_out_commit()` reads and validates `git rev-parse --verify HEAD^{commit}`. Creation intent and package manifest use that actual value for `source_commit`; `GITHUB_SHA` is separately labeled `workflow_trigger_commit`.

Subsequent checkpoint commits need not equal the build commit. Frozen input hashes and package hashes still establish byte identity during publication; no requirement falsely assumes the later authorization commit is the earlier source commit.

### 3. Manifest stability through upload

Immediately before the publish intent, the complete local package is revalidated and its returned manifest hash is compared with the hash accepted at the start of publication. A changed manifest cannot pass by discarding the second validation's return value.

Local metadata construction is also evaluated before writing the creation intent, so an abstract-parsing error cannot unnecessarily create an unresolved creation intent before any POST is attempted.

## Inherited safeguards retained

The publisher retains protected historical IDs, its pinned credential client, HTTPS/host/redirect restrictions, no POST retry, durable create and publication intents before consequential POSTs, same-record recovery, exact file inventories, input/file SHA-256 checks, DOI substitution constraints, PDF/manifest-bound visual review and authorization, and scoped ordinary Git pushes.

Draft file uploads use the validated bucket and exact names. Unexpected files or checksum/size mismatches stop publication; nothing is deleted. Already submitted records take the readback path with no remote mutation. Public metadata and all file bytes are verified without authentication before a success receipt is written. DOI resolution, OTS and Arweave remain separately pending.

Both workflows use the designated repository and branch, explicit trigger markers, one shared non-cancelling concurrency group, pinned actions and credential exposure limited to the relevant operation. The publish workflow runs package verification before credential access and retains state/artifacts even after failure. No whole-workspace storage CI was added by this reviewer; these workflows are the authorized publication process.

## Verification

The final suite contains **17 offline tests; all 17 passed**. The eight inherited gates remain covered. Added tests check normalized/other-version/subtitle duplicates, later-page recovery with all versions included, foreign markers, malformed/capped/unstable pagination, actual checkout provenance, checkpoint failures before both POST types, manifest drift during upload, and failure of anonymous byte verification.

The command was:

```text
TMPDIR=<review directory>/tmp PYTHONDONTWRITEBYTECODE=1 python research/matched-behavior-source-use/test_publication.py
```

The observed exit code was 0. Temporary fixtures were confined to the review directory. Any synthetic record identifiers printed by the inherited test harness are test data, not real DOI reservations or publication evidence. No live network test or API mutation was performed.

The final gate outcome is not a replacement for an actual DOI-bearing PDF review. It means the authorized prepare workflow can safely attempt its bounded lookup/reservation procedure, and that the publisher's final gates remain necessary before a publication POST.

## Companion text and package check

The release `source-main.md` status now says preprint v1.0.1 and correctly retains internal AI-assisted review, absence of human/neural data and unchanged completed-map status.

The revised Data and code availability paragraph accurately calls the archive a selected supplement while retaining the pinned full-record repository. The ZIP contains 41 entries and no absolute or parent-traversal member names. This quick inventory check does not claim a new full scientific re-audit of the archive.

A direct text diff shows that `REVIEW-AND-SOURCES.md` adds a release-provenance introduction and removes chat-only web reference identifiers while preserving the earlier scientific review text and source URLs. These are acceptable editorial changes.

## Operational disposition

No remaining blocker to **prepare** was identified in the reviewed implementation. Once the actual deposit is reserved, the operator must retain the exact generated manifest and review all pages of that DOI-bearing PDF, then record the already-granted user authorization against those exact bytes. The initial preview does not satisfy that gate.

If lookup is incomplete, a suspected duplicate appears, a checkpoint fails, or a POST outcome is uncertain, stop the dependent action and reconcile the same identity through read-only evidence. Do not remove the intent or replay a POST merely to make the workflow succeed. No further broad code rewrite or scientific enumeration is needed for the current release.

