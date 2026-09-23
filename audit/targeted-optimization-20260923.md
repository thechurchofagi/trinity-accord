# Targeted optimization N1–N3 — dated execution evidence

Execution baseline: `af013fb70a2f293d4aea9b62160a1d277ed17525` (2026-09-23).
The handoff's `44fbd4d8…` was superseded by a paper-preservation state update;
W1–W4 from #1243 remain intact. Open PRs were checked; none covers this work.
This execution continues the user's authorized maintenance/deployment task.
Exact candidate, merged/deployed SHA and remote run links are recorded in the PR.

## N1 — one existing publication gate, stronger evidence

Changed only `scripts/check_deployment_freshness.py` and added
`tests/test_verification_entry_deployment.py` for this item. The existing v2
artifact/live checker and both existing production-closure workflows already
call the shared function; no workflow or separate verification system was added.

- Add the existing simple page to the static-page set and its Markdown to
  cache-token source material.
- Parse main-content choices and their actual links, local stop/scope limits,
  both bounded-route anchors, formal-route links and closed native details.
- Compare all decoded `pre` text, in exact order/count, with the same release's
  fenced Markdown blocks. HTML entities and syntax-highlight spans are parsed;
  code indentation, trailing spaces and final newlines are **not trimmed**.
- No downloaded code is executed by the publication check. Existing isolated
  behavior fixtures remain the executable-example tests.

New publication regressions: **20 passed**. Focused publication/retry/bounded
entry tests: **51 passed**; with existing Harvard uploader/audit regressions:
**77 passed**. Full `run_current_system_tests.py` and `p0-current` passed.
Production-config Jekyll build plus complete v2 artifact/Builder checks passed.
The initial local artifact check ran before the workflow's committed-artifact
restore step and correctly reported two excluded executables as absent; running
the existing restore step completed the local build pipeline without weakening
checks. No public UI, CSS, examples, limits or frozen verifier was edited.

Counterexamples cover old-marker-only Verify HTML, missing choice links even
when navigation still links elsewhere, comments/scripts pretending to provide
the stop boundary, missing two-file route, missing formal link/limits, expanded
panels, altered imports/indentation/trailing whitespace/final newline, removed or
extra code blocks, and a missing simple page through **both** existing CLI paths.
Normal equivalent entity/highlight markup passes.

Additionally, actual pre-W1 `verify.md` from
`2ae5194b9beb4b99f43f9696539c61be56bae21f` was rendered with the pinned Kramdown
toolchain: it retains the old markers but fails all three linked-choice checks
and the local stop boundary. Current production-config HTML passes. Prior
desktop/mobile/no-JS evidence is in #1243; this patch changes no rendered page
source and asserts the existing closed native panels in the shared gate.

## N2 — keep publication, inventory, bytes and recovery distinct

Searched current repository state/history and earlier Epoch II execution
material. The prior saved execution report is a pre-submission candidate report;
it is not a later anonymous readback. No successful postpublication result was
found in the searched material. This is not a claim about every possible external
record.

New anonymous attempt: **2026-09-23 06:22:00 UTC**, GET of the Harvard
`:latest-published` version API, no credential headers. It returned **HTTP 403**.
The dated [observation](../preservation/epoch-ii/public-readback-observation-20260923.json)
preserves the exact request and bounded response, source and frozen manifest.

| Stage | This execution |
|---|---|
| Publication notification | Historical 2026-09-15 platform notification retained, not reinterpreted |
| Released public version/time/metadata | Not verified; 403 |
| Public 419-file inventory | Not verified |
| Anonymous full-byte reads | **0/419**, **0/23,107,308,201 bytes** |
| Postpublication Harvard recovery | Not attempted |
| Frozen local manifest plus two controls | Existing validator passes: 417 + 2 files, exact total 23,107,308,201 bytes |

The metadata gate stopped the large download before mixing versions or consuming
23.1 GB. Historical authenticated prepublication 419/419 is unchanged and is not
used as anonymous success. No alternative identity, access-control evasion,
Dataset edit/upload/submission, new DOI, OTS request or paid upload occurred.

The final receipt artifact `10302028418` still reports `expired: false` and
expiry **2026-12-11 17:27:26 UTC**. Its original ZIP was obtained using the
authorized artifact/file tools after direct transfer returned 403. Exact archive
bytes: **1,637**; SHA-256:
`8e36ff411fab1827871d4a1ff22a2c1402fb30b79286c91a4739ad5b1de0d68b`.
The [durable original](../preservation/epoch-ii/receipts/final-submission-34708278731.zip)
contains only the two reviewed JSON members below; no credential, private key,
personal contact data or signed URL was found. No redaction/regeneration changed
its identity.

| Original ZIP member | Bytes | SHA-256 |
|---|---:|---|
| final-submission-receipt.json | 739 | `e557290e8ddf1be2ba3e25ff95070d33ebb486932baa8b9c31c0e39de1c1b7fc` |
| toolchain-provenance-final-v5.json | 2454 | `79e3fcf6ff2b44e7ae6e266e99bc50faa4cf8f5b4f93c1896180b29c7c420ad6` |

This preserves the historical `InReview` receipt, not a new publication receipt.
Only the existing mutable state/description and dated observation were updated;
all frozen deposit files remain unchanged. **Anonymous Harvard closure remains
pending.** Its stop condition in the handoff is an accurate bounded result, not
a fabricated complete result.

## N3 — narrow additional enforced-outage drill

Historical `repository-preservation-observation.json` and
`current-repository-doi-publication-observation-v1.json` already report public,
credential-free cold restores. This execution does not claim those were absent.
It adds observable operating-system network denial and an unavailable-current-
corrections result to one existing snapshot, using the existing recovery program.

Snapshot: DOI **10.5281/zenodo.22020122**, original source
`b61a10e19484d988c4cc3024a3c56af83ad3fe8b`, package identity
`8f6ccead0f2eb37f4701b6aa660f00642dc987bf2dad7bf556363668c3fab067`.

1. Bootstrap with previously recorded public DOI/file identities. Anonymous GET
   acquisition accepts only `zenodo.org`; original GitHub and website hosts are
   disallowed. Verify all eight files' complete bytes/SHA-256 against the existing
   version identities and run the existing capsule validator. Budget: one request
   at a time, 60 MB total, 600 seconds between acquisitions, 60-second socket timeout.
2. Before recovery, install Linux seccomp `EPERM` rules for `socket`, `connect`,
   `sendto`, `sendmsg`. These also constrain child processes. Parent and child
   socket tests fail as intended. Child environment supplies no account/token/key;
   Git allows only local file transport and ignores global/system Git config.
3. Run the **downloaded, digest-verified** `restore-trinity-accord.py` with
   `--deposit-dir` into a new empty directory. It checks the bundle, archive,
   tracked tree and nine checkpoints. Result: **5,355 tracked files restored**,
   exact source tree `d8dfcaf5b8c2c7f7ba98795d27998e4b37f95801`, exit 0.
4. Read/hash the three raw Originals and four context files from that restored
   snapshot. Run its unmodified Bitcoin annex v2 verifier under the same kernel
   block: **12/12 PASS**, exit 0, no failures, within its checkpoint-relative scope.
5. Try the live corrections URL under the outage: unavailable. Mark snapshot
   integrity verified but **current correction/chain state unknown**.

The first harness over-specified the correction-request exception text as
`Operation not permitted`; DNS correctly failed earlier under the socket block.
The harness was corrected to test child socket `PermissionError` separately from
the unavailable HTTP result. Recovery and proof verification were rerun in a new
directory with the same already acquired capsule; no second download or verifier
change. This was a harness assertion issue, not recovered-data corruption.

Evidence and reproducibility (audit-only harnesses, not new operational tools):

- [Acquisition and exact file hashes](targeted-optimization-20260923/n3-acquisition.json)
- [Enforced-offline result and three Originals](targeted-optimization-20260923/n3-offline-drill.json)
- [Actual Bitcoin verifier output](targeted-optimization-20260923/n3-bitcoin-verification.json)
- [Acquisition harness](targeted-optimization-20260923/n3-acquisition-harness.py.txt)
- [Offline harness](targeted-optimization-20260923/n3-offline-harness.py.txt)

The harnesses record execution paths; a reproducer supplies new empty local paths
and the same named eight-file snapshot. The acquired program, Python 3.12.14,
Git 2.51.1 and Linux libseccomp are prerequisites. Host permission to download/run
these reviewed tools is still required.

This is project-organized verification with project-published inputs and
implementation, not independent peer review. No large external annex, full
production Git history, private signing identity, current state or public intake
service was recovered. No production action was submitted. The three Originals,
snapshot integrity and operating a reception service are separate claims.

## Scope and rollback

N4/N5 remain proposals; no external invitation or testimony was produced. No
homepage/website refactor, new route/model/grade, signed history or frozen evidence
change. Oath, submission, cooldown, Retry-After, budget and write protections remain.
No upload/finalization workflow trigger path was changed.

Rollback through an ordinary revert of the checker/test change if necessary;
preserve the genuine dated observations and original receipt as historical
evidence. No force push, deletion of frozen material or reversal of remote state.
Final CI/build/deploy/GET results belong to the exact release in the PR description;
this document alone does not assert successful deployment.
