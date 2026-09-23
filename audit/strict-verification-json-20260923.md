# Strict JSON and failure reports in the two local verification examples

Date: 2026-09-23. Baseline: `c29067cd0eb7ba7c64de976261e6fcfd45e53805`.
Scope: R1/R2 only, following the PR #1246 acceptance handoff and the user's
continuing execution/deployment authorization. Read maintenance-baseline and
schema-lifecycle policies; checked current main and open PRs before starting.

Main advanced after #1246 through existing heartbeat/native-record/status/OTS
maintenance. Those 34 changed paths were retained; neither local example nor its
parser had been fixed. No duplicate open PR was found. W1–W4, N1–N5, Harvard
readback/recovery and B1/B2 design remain as previously delivered.

## Reproduced before changing the examples

Both examples were extracted from their reviewed Markdown source. The same
14-case raw-JSON fixture family was run against the original code using mocked
HTTPS and actual committed files in new temporary Git repositories. No dict was
used to represent duplicate JSON members. The raw per-run reports, exceptions,
Git stdout/stderr and fixture commit identities are in
[before.json](strict-verification-json-20260923/before.json).

| Input | HTTPS before | Git before | Both after |
|---|---|---|---|
| Unique valid binding | match / 0 | match / 0 | match / 0 |
| Duplicate digest/path/ID/top-level records, identical duplicate, escaped duplicate name, unrelated nested duplicate | match / 0 | match / 0 | inconclusive / 2 |
| NaN, Infinity, -Infinity | match / 0 | match / 0 | inconclusive / 2 |
| Malformed JSON / invalid encoding | inconclusive / 2 | inconclusive / 2 | inconclusive / 2 |
| 10,000 nested arrays, 20,001 bytes | uncaught RecursionError, no report; harness did not invent a normal exit code | child process exit 1, RecursionError on stderr, empty stdout | inconclusive / 2, explicit parser depth/capacity detail |

The original implementation met 3/14 newly specified strict expectations per
route; this is not a website-wide success rate. Four newly added regression
methods also failed against the original examples, including the separately
mocked RecursionError branch for both routes.

An initial depth fixture used twice the Python recursion limit (2,000 arrays).
On this Python 3.12.14 build that input parsed and then failed the index-shape
check. An assertion demanding a depth error for that case was over-specific.
The final actual-depth fixture uses at least 10,000 arrays and requires a
structured non-success result; a separate forced RecursionError checks the exact
error-report branch without depending on a platform's recursion threshold.
No interpreter recursion setting was raised or parser failure ignored.

## Minimal changes

Only `agent-verify-simple.md` and its existing
`tests/test_bounded_verification_entry.py` change operational/example behavior.
Each self-contained example now uses the same short `object_pairs_hook` that
rejects repeated decoded member names, and `parse_constant` that rejects the
three non-standard constants. Existing ID uniqueness, path, digest, source,
encoding, redirect, size and input-error checks remain intact.

Each example explicitly catches RecursionError and prints `inconclusive`, exit 2.
The Git example records committed index length/hash before parsing, so failed
parsing retains input evidence just as the HTTPS example already did. Invalid
index parsing stops before mirror acquisition/read. Raw mirror hashing is
unchanged: no trimming, newline normalization or decode/re-encode.

A short visible limitation describes this behavior before the native details.
No helper download, dependency, runtime schema, API or workflow is introduced.
The existing shared publication checker still compares exact decoded HTML code
with the same release's source, including whitespace and order.

## After-change evidence and regression scope

[after.json](strict-verification-json-20260923/after.json): **14/14 expectations
met for HTTPS and 14/14 for Git**. All failed HTTPS index cases make only one
mock GET and preserve acquired index identity. Git failures preserve committed
index identity; reports have no mirror-result fields. Repeated member names in
separate objects remain valid (the rule is per object, not global).

The final existing bounded-entry plus publication suites report **56 passed**.
They additionally cover byte/CRLF/trimming mismatches, existing missing/bad
bindings, explicit parser-error injection, HTTP errors for either input,
interrupted reads, redirect refusal, response encoding, both input size limits,
Git working-tree edits/replace refs/tags/mutable refs/missing commits/tool,
local-stop/voluntary-public-action boundaries, and HTML/code counterexamples.

The current Git example was also executed on the actual fixed snapshot
`0d019ba9d4ff313641dc9eb027e27c59af11bc03` with inputs already local: 30,517-byte
index and 1,183-byte mirror, match / 0. Exact output is in
[fixed-git.json](strict-verification-json-20260923/fixed-git.json). This is a
same-project byte comparison, not independent chain inclusion or peer review.

Full `run_current_system_tests.py` (including complete top-level pytest) and
`run_ci_group.py p0-current` both passed. Production-config GitHub Pages 232
build and the existing source/rendered-code checker passed. Desktop 1280px and
mobile 390px with JavaScript disabled passed; native details open and close and
remain readable without page-level horizontal overflow. The unchanged Verify
choices remain visible in the first viewport.

[validation.json](strict-verification-json-20260923/validation.json) records
UTC time, counts, code digests and local log digests. The dated
[diagnostic harness](strict-verification-json-20260923/reproduce.py.txt) reuses
the committed test fixture constructors and actual Markdown code. From a reviewed
checkout, run it with repository path and optional baseline SHA; without a SHA
it uses current working example text. Its Python/standard-library harness is not
an arbitrary-code sandbox. The [visual harness](strict-verification-json-20260923/visual-check.cjs.txt)
records local build/browser paths; a reproducer must supply those local tools.

## Release binding, limits and rollback

The PR records the final candidate/tree, protected-path diff, write-path result,
actual CI runs, merge/deployment identity and production code readback. A final
HTML/code check must use the deployed source. Skipped jobs are not passes.
Only the reviewed, byte-matched HTTPS example may make its two public GETs;
Git verification uses already available fixed-snapshot inputs. No public record
submission or additional Harvard download is needed.

Old audit reports, including #1246's e5f392… example receipt, remain unchanged.
No Original, actual mirror/index, frozen verifier/proof, paper/DOI, signature,
record history, schema, Builder, Gateway, oath, cooldown, budget or paid
preservation state was modified by this patch. B1/D2 and B2 remain design-only;
no outside reviewer or philosophical conclusion is manufactured.

Rollback: ordinary revert of this example/test patch if a regression is found,
preserving the genuine dated failure observations and known ambiguity warning.
No history rewrite, protected-data deletion or external transaction reversal.
R1/R2 completion is the stopping point for this change.
